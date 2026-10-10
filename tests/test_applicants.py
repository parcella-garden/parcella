"""
Tests for the applicants module (docs/module-applicants.md): people who
applied for a free garden plot.

Covers the public side (the website's form and the token JSON endpoint,
same form contract as the contact form -- ADR 0090), the board's web UI
and REST API, the status history, and the GDPR hard delete (ADR 0091),
including that deleting needs the "delete" permission.
"""
import pytest
from sqlalchemy import select

from app.auth import hash_password
from app.database import AsyncSessionLocal
from app.models import (
    Applicant, ApplicantSource, ApplicantStatus, ChangeHistory, ClubSetting,
    Group, GroupMembership, GroupModulePermission, User, UserRole,
)
from app.rate_limit import reset_all
from tests.conftest import login, auth_header
from tests.test_admin_integrations_incoming_folder import web_login
from tests.test_public_api import _set_api_token
from tests.test_public_forms import (  # noqa: F401
    ERROR_URL, FROM_SITE, SUCCESS_URL, _allow_origins, _cheap_altcha, _require_altcha, _solved,
)

TOKEN = {"X-Parcella-API-Token": "test-public-api-token"}


@pytest.fixture(autouse=True)
def _fresh_rate_limits():
    reset_all()
    yield
    reset_all()


async def _enable_public_form(client, headers):
    response = await client.put(
        "/api/v1/club-settings/modul_public_applicant_api", json={"value": "true"}, headers=headers,
    )
    assert response.status_code == 200, response.text
    await _allow_origins(client, headers)


def _form(**overrides):
    form = {
        "email": "erika@example.org", "first_name": "Erika", "last_name": "Musterfrau",
        "phone": "0341 123456", "message": "Gern mit Laube, wir sind zu dritt.",
        "consent": "on", "website": "", "success_url": SUCCESS_URL, "error_url": ERROR_URL,
    }
    form.update(overrides)
    return {k: v for k, v in form.items() if v is not None}


async def _post_form(client, form):
    return await client.post("/api/v1/public/forms/applicant", data=form, headers=FROM_SITE)


async def _applicants():
    async with AsyncSessionLocal() as db:
        return (await db.execute(select(Applicant).order_by(Applicant.applied_at))).scalars().all()


async def _create_applicant(**fields) -> str:
    async with AsyncSessionLocal() as db:
        applicant = Applicant(email=fields.pop("email", "erika@example.org"), **fields)
        db.add(applicant)
        await db.commit()
        return applicant.id


# ---------------------------------------------------------------------------
# Public form
# ---------------------------------------------------------------------------

async def test_website_form_creates_an_applicant(client, admin_user):
    await _enable_public_form(client, auth_header(await login(client, "admin@example.com")))

    response = await _post_form(client, _form())
    assert response.status_code == 303
    assert response.headers["location"] == f"{SUCCESS_URL}#ok"

    [applicant] = await _applicants()
    assert applicant.email == "erika@example.org"
    assert (applicant.first_name, applicant.last_name) == ("Erika", "Musterfrau")
    assert applicant.phone == "0341 123456"
    assert applicant.message == "Gern mit Laube, wir sind zu dritt."
    assert applicant.status == ApplicantStatus.NEW
    assert applicant.source == ApplicantSource.WEBSITE
    assert applicant.consent_at is not None and applicant.applied_at is not None


async def test_only_the_email_address_is_required(client, admin_user):
    await _enable_public_form(client, auth_header(await login(client, "admin@example.com")))

    response = await _post_form(client, _form(first_name="", last_name="", phone="", message=""))
    assert response.headers["location"] == f"{SUCCESS_URL}#ok"
    [applicant] = await _applicants()
    assert (applicant.first_name, applicant.last_name, applicant.phone, applicant.message) == (None, None, None, None)

    missing = await _post_form(client, _form(email=""))
    assert missing.headers["location"] == f"{ERROR_URL}#invalid"
    bad = await _post_form(client, _form(email="not-an-address"))
    assert bad.headers["location"] == f"{ERROR_URL}#invalid"
    assert len(await _applicants()) == 1


async def test_consent_is_required(client, admin_user):
    await _enable_public_form(client, auth_header(await login(client, "admin@example.com")))
    response = await _post_form(client, _form(consent=None))
    assert response.headers["location"] == f"{ERROR_URL}#consent_missing"
    assert await _applicants() == []


async def test_honeypot_looks_successful_but_stores_nothing(client, admin_user):
    await _enable_public_form(client, auth_header(await login(client, "admin@example.com")))
    response = await _post_form(client, _form(website="http://spam.example"))
    assert response.headers["location"] == f"{SUCCESS_URL}#ok"
    assert await _applicants() == []


async def test_form_closed_without_module_flag_or_from_other_sites(client, admin_user):
    headers = auth_header(await login(client, "admin@example.com"))
    await _allow_origins(client, headers)
    assert (await _post_form(client, _form())).status_code == 404  # public_applicant_api is off by default

    await _enable_public_form(client, headers)
    other = await client.post(
        "/api/v1/public/forms/applicant", data=_form(), headers={"Origin": "https://evil.example"},
    )
    assert other.status_code == 403
    assert await _applicants() == []


async def test_form_requires_altcha_while_switched_on(client, admin_user, _cheap_altcha):
    headers = auth_header(await login(client, "admin@example.com"))
    await _enable_public_form(client, headers)
    await _require_altcha(client, headers)

    assert (await _post_form(client, _form())).headers["location"] == f"{ERROR_URL}#captcha"
    accepted = await _post_form(client, _form(altcha=await _solved(client)))
    assert accepted.headers["location"] == f"{SUCCESS_URL}#ok"
    assert len(await _applicants()) == 1


async def test_json_endpoint_for_connectors(client, admin_user):
    headers = auth_header(await login(client, "admin@example.com"))
    await _enable_public_form(client, headers)
    await _set_api_token(client, headers)

    payload = {"email": "max@example.org", "consent": True}
    assert (await client.post("/api/v1/public/applicants", json=payload)).status_code == 401

    response = await client.post("/api/v1/public/applicants", json=payload, headers=TOKEN)
    assert response.json() == {"accepted": True, "reason": None, "code": None}

    refused = await client.post("/api/v1/public/applicants", json={**payload, "consent": False}, headers=TOKEN)
    assert refused.json()["code"] == "consent_missing"
    assert [a.email for a in await _applicants()] == ["max@example.org"]


# ---------------------------------------------------------------------------
# Board side: web UI
# ---------------------------------------------------------------------------

async def test_board_lists_applicants_and_changes_status(client, admin_user):
    applicant_id = await _create_applicant(first_name="Erika", last_name="Musterfrau")
    await _create_applicant(email="old@example.org", status=ApplicantStatus.WITHDRAWN)
    await web_login(client)

    page = await client.get("/applicants/")
    assert page.status_code == 200
    assert "Erika Musterfrau" in page.text
    assert "old@example.org" not in page.text  # the default "open" filter hides closed ones
    assert "old@example.org" in (await client.get("/applicants/?filter=all")).text

    response = await client.post(f"/applicants/{applicant_id}/edit", data={
        "email": "erika@example.org", "first_name": "Erika", "last_name": "Musterfrau",
        "phone": "", "message": "", "board_note": "Rückruf am Montag", "status": "CONTACTED",
    })
    assert response.status_code == 303

    async with AsyncSessionLocal() as db:
        applicant = await db.get(Applicant, applicant_id)
        assert applicant.status == ApplicantStatus.CONTACTED
        assert applicant.status_changed_at is not None
        assert applicant.board_note == "Rückruf am Montag"
        history = (await db.execute(
            select(ChangeHistory).where(ChangeHistory.entity_id == applicant_id)
        )).scalars().all()
    assert [(h.field_name, h.old_value, h.new_value) for h in history] == [("status", "NEW", "CONTACTED")]

    detail = await client.get(f"/applicants/{applicant_id}")
    assert detail.status_code == 200 and "Rückruf am Montag" in detail.text


async def test_board_adds_an_applicant_by_hand(client, admin_user):
    await web_login(client)
    assert (await client.get("/applicants/new")).status_code == 200

    invalid = await client.post("/applicants/new", data={"email": "nope"})
    assert invalid.status_code == 400
    assert await _applicants() == []

    response = await client.post("/applicants/new", data={"email": "Tel@Example.org ", "first_name": "Telefon"})
    assert response.status_code == 303
    [applicant] = await _applicants()
    assert applicant.source == ApplicantSource.MANUAL
    assert applicant.email == "Tel@example.org"  # domain part normalized, local part kept
    assert applicant.consent_at is None


async def test_dashboard_counts_new_applications(client, admin_user):
    await _create_applicant()
    await _create_applicant(email="b@example.org")
    await _create_applicant(email="c@example.org", status=ApplicantStatus.CONTACTED)
    await web_login(client)
    page = await client.get("/")
    assert "/applicants/?filter=new" in page.text
    new_only = await client.get("/applicants/?filter=new")
    assert "c@example.org" not in new_only.text and "b@example.org" in new_only.text


async def test_delete_removes_applicant_and_its_history(client, admin_user):
    applicant_id = await _create_applicant()
    await web_login(client)
    await client.post(f"/applicants/{applicant_id}/edit", data={"email": "erika@example.org", "status": "REJECTED"})

    response = await client.post(f"/applicants/{applicant_id}/delete")
    assert response.status_code == 303
    assert await _applicants() == []
    async with AsyncSessionLocal() as db:
        leftovers = (await db.execute(select(ChangeHistory).where(ChangeHistory.entity_id == applicant_id))).scalars().all()
    assert leftovers == []


async def test_delete_needs_the_delete_permission(client, admin_user):
    async with AsyncSessionLocal() as db:
        user = User(
            email="allocation@example.com", name="Plot Allocation",
            password_hash=hash_password("testpasswort123"), role=UserRole.READONLY,
        )
        db.add(user)
        await db.flush()
        group = Group(name="Plot allocation")
        db.add(group)
        await db.flush()
        db.add(GroupModulePermission(group_id=group.id, module="applicants", can_read=True, can_write=True))
        db.add(GroupMembership(user_id=user.id, group_id=group.id))
        await db.commit()
    applicant_id = await _create_applicant()

    await web_login(client, "allocation@example.com")
    assert (await client.get("/applicants/")).status_code == 200
    assert (await client.post(f"/applicants/{applicant_id}/delete")).status_code == 403
    assert len(await _applicants()) == 1


async def test_module_flag_hides_the_board_ui(client, admin_user):
    async with AsyncSessionLocal() as db:
        db.add(ClubSetting(key="modul_applicants", value="false", description="test"))
        await db.commit()
    await web_login(client)
    assert (await client.get("/applicants/")).status_code == 404


# ---------------------------------------------------------------------------
# Board side: REST API
# ---------------------------------------------------------------------------

async def test_rest_api_crud(client, admin_user):
    headers = auth_header(await login(client, "admin@example.com"))

    created = await client.post("/api/v1/applicants", json={"email": "api@example.org", "last_name": "Api"}, headers=headers)
    assert created.status_code == 201, created.text
    body = created.json()
    assert body["status"] == "NEW" and body["source"] == "MANUAL"
    applicant_id = body["id"]

    listed = await client.get("/api/v1/applicants?status=NEW", headers=headers)
    assert [a["id"] for a in listed.json()] == [applicant_id]

    updated = await client.patch(f"/api/v1/applicants/{applicant_id}", json={"status": "OFFERED", "board_note": "Garten 62"}, headers=headers)
    assert updated.status_code == 200, updated.text
    assert updated.json()["status"] == "OFFERED" and updated.json()["last_name"] == "Api"

    assert (await client.get(f"/api/v1/applicants/{applicant_id}", headers=headers)).json()["board_note"] == "Garten 62"
    assert (await client.delete(f"/api/v1/applicants/{applicant_id}", headers=headers)).status_code == 204
    assert (await client.get(f"/api/v1/applicants/{applicant_id}", headers=headers)).status_code == 404
