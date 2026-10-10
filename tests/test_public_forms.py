"""
Tests for the plain-HTML-form endpoints of the public API
(POST /api/v1/public/forms/*, see app/routers/api_public.py and ADR 0088).

They run the same signup/contact logic as the JSON endpoints (covered in
tests/test_public_api.py), so these tests focus on what is different
here: no API token, an allowlist of website origins instead, form-encoded
input, and a 303 redirect back to the website -- only ever to an allowed
origin -- carrying the outcome as the URL fragment.
"""
import pytest
from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models import ClubSetting
from app.rate_limit import reset_all
from tests.conftest import login, auth_header
from tests.test_public_api import (
    _FakeFreeScoutClient, _assign_member_to_parcel, _create_member, _create_parcel,
    _create_session, _enable_contact_module, _enable_module, _get_session_participations,
    _patch_freescout_client,
)
from tests.test_admin_integrations_incoming_folder import web_login

SITE = "https://garden.example"
FROM_SITE = {"Origin": SITE, "Referer": f"{SITE}/arbeitseinsatz/"}
SUCCESS_URL = f"{SITE}/danke/"
ERROR_URL = f"{SITE}/fehler/"


@pytest.fixture(autouse=True)
def _fresh_rate_limits():
    # The limiter is module-level state; without this the contact
    # endpoint's 10/hour budget leaks across tests.
    reset_all()
    yield
    reset_all()


async def _allow_origins(client, headers, value=SITE):
    response = await client.put(
        "/api/v1/club-settings/public_form_allowed_origins", json={"value": value}, headers=headers,
    )
    assert response.status_code == 200, response.text


async def _signup_setup(client, max_participants=None):
    """Admin headers, an allowed site, and parcel G042 with one resident."""
    headers = auth_header(await login(client, "admin@example.com"))
    await _enable_module(client, headers)
    await _allow_origins(client, headers)
    member = await _create_member(client, headers)
    parcel = await _create_parcel(client, headers)
    await _assign_member_to_parcel(client, headers, member["id"], parcel["id"])
    session = await _create_session(client, headers, max_participants=max_participants)
    return headers, session


def _signup_form(*session_ids, **overrides):
    form = {
        "parcel_number": "G042", "name": "", "phone": "", "email": "", "remarks": "", "website": "",
        "session_ids": list(session_ids), "success_url": SUCCESS_URL, "error_url": ERROR_URL,
    }
    form.update(overrides)
    return form


async def _post_signup(client, form, headers=FROM_SITE):
    return await client.post("/api/v1/public/forms/work-session-signup", data=form, headers=headers)


async def test_signup_form_requires_module_flag(client, admin_user):
    response = await _post_signup(client, _signup_form("x"))
    assert response.status_code == 404


async def test_signup_form_closed_while_no_origin_is_configured(client, admin_user):
    headers = auth_header(await login(client, "admin@example.com"))
    await _enable_module(client, headers)

    response = await _post_signup(client, _signup_form("x"))
    assert response.status_code == 403


async def test_signup_form_rejects_other_or_missing_origins(client, admin_user):
    _headers, session = await _signup_setup(client)
    form = _signup_form(session["id"])

    foreign = await _post_signup(client, form, headers={"Origin": "https://evil.example"})
    assert foreign.status_code == 403
    # A look-alike that merely starts with the allowed origin.
    lookalike = await _post_signup(client, form, headers={"Origin": f"{SITE}.evil.example"})
    assert lookalike.status_code == 403
    missing = await _post_signup(client, form, headers={})
    assert missing.status_code == 403


async def test_signup_form_registers_and_redirects_to_success(client, admin_user):
    headers, session = await _signup_setup(client)

    response = await _post_signup(client, _signup_form(session["id"]))
    assert response.status_code == 303
    assert response.headers["location"] == f"{SUCCESS_URL}#ok"

    participations = await _get_session_participations(client, headers, session["id"])
    assert len(participations) == 1


async def test_signup_form_accepts_referer_when_origin_is_absent(client, admin_user):
    _headers, session = await _signup_setup(client)

    response = await _post_signup(
        client, _signup_form(session["id"]), headers={"Referer": f"{SITE}/arbeitseinsatz/"},
    )
    assert response.status_code == 303
    assert response.headers["location"] == f"{SUCCESS_URL}#ok"


async def test_signup_form_partial_success(client, admin_user):
    headers, open_session = await _signup_setup(client)
    full_session = await _create_session(client, headers, title="Full", max_participants=0)

    response = await _post_signup(client, _signup_form(open_session["id"], full_session["id"]))
    assert response.headers["location"] == f"{SUCCESS_URL}#partial"


async def test_signup_form_full_session_redirects_to_error_with_reason(client, admin_user):
    headers, session = await _signup_setup(client, max_participants=0)

    response = await _post_signup(client, _signup_form(session["id"]))
    assert response.status_code == 303
    assert response.headers["location"] == f"{ERROR_URL}#session_full"
    assert await _get_session_participations(client, headers, session["id"]) == []


async def test_signup_form_unknown_parcel_and_missing_session(client, admin_user):
    _headers, session = await _signup_setup(client)

    unknown = await _post_signup(client, _signup_form(session["id"], parcel_number="X999"))
    assert unknown.headers["location"] == f"{ERROR_URL}#unknown_parcel"

    none_ticked = await _post_signup(client, _signup_form())
    assert none_ticked.headers["location"] == f"{ERROR_URL}#no_session_selected"


async def test_signup_form_honeypot_looks_successful_but_registers_nobody(client, admin_user):
    headers, session = await _signup_setup(client)

    response = await _post_signup(client, _signup_form(session["id"], website="http://spam.example"))
    assert response.headers["location"] == f"{SUCCESS_URL}#ok"
    assert await _get_session_participations(client, headers, session["id"]) == []


async def test_signup_form_never_redirects_off_the_allowed_site(client, admin_user):
    """An injected success_url on another host must not be followed --
    otherwise this endpoint is an open redirect. Falls back to the page
    the form was submitted from."""
    _headers, session = await _signup_setup(client)

    response = await _post_signup(client, _signup_form(session["id"], success_url="https://evil.example/"))
    assert response.headers["location"] == f"{SITE}/arbeitseinsatz/#ok"

    response = await _post_signup(
        client, _signup_form(session["id"], success_url="https://evil.example/"), headers={"Origin": SITE},
    )
    assert response.headers["location"] == f"{SITE}/#ok"


async def _contact_setup(client, monkeypatch):
    headers = auth_header(await login(client, "admin@example.com"))
    await _enable_contact_module(client, headers)
    await _allow_origins(client, headers)
    fake_client = _FakeFreeScoutClient()
    _patch_freescout_client(monkeypatch, fake_client)
    return fake_client


def _contact_form(**overrides):
    form = {
        "name": "Gerd Mustergärtner", "email": "gerd@example.com",
        "message": "Could you please check the water tap near G042?", "consent": "on", "website": "",
        "success_url": SUCCESS_URL, "error_url": ERROR_URL,
    }
    form.update(overrides)
    return {k: v for k, v in form.items() if v is not None}


async def _post_contact(client, form, headers=FROM_SITE):
    return await client.post("/api/v1/public/forms/contact", data=form, headers=headers)


async def test_contact_form_creates_conversation_and_redirects(client, admin_user, monkeypatch):
    fake_client = await _contact_setup(client, monkeypatch)

    response = await _post_contact(client, _contact_form())
    assert response.status_code == 303
    assert response.headers["location"] == f"{SUCCESS_URL}#ok"
    assert len(fake_client.calls) == 1
    assert fake_client.calls[0]["customer_email"] == "gerd@example.com"


async def test_contact_form_rejections_carry_a_reason(client, admin_user, monkeypatch):
    fake_client = await _contact_setup(client, monkeypatch)

    # An unticked checkbox isn't sent at all by the browser.
    no_consent = await _post_contact(client, _contact_form(consent=None))
    assert no_consent.headers["location"] == f"{ERROR_URL}#consent_missing"

    bad_email = await _post_contact(client, _contact_form(email="not-an-address"))
    assert bad_email.headers["location"] == f"{ERROR_URL}#invalid"

    assert fake_client.calls == []


async def test_contact_form_without_freescout_reports_unavailable(client, admin_user):
    headers = auth_header(await login(client, "admin@example.com"))
    await _enable_contact_module(client, headers)
    await _allow_origins(client, headers)

    response = await _post_contact(client, _contact_form())
    assert response.headers["location"] == f"{ERROR_URL}#unavailable"


async def test_contact_form_rate_limit_redirects_instead_of_erroring(client, admin_user, monkeypatch):
    await _contact_setup(client, monkeypatch)

    for _ in range(10):
        await _post_contact(client, _contact_form())
    response = await _post_contact(client, _contact_form())
    assert response.status_code == 303
    assert response.headers["location"] == f"{ERROR_URL}#rate_limited"


async def test_admin_saves_normalized_origins_and_reports_invalid_ones(client, admin_user):
    await web_login(client)

    response = await client.post(
        "/admin/integrations/public-forms",
        data={"public_form_origins": "https://Garden.example/some/page\nftp://nope.example\nnot-a-url"},
    )
    assert response.status_code == 303
    assert "public_forms_saved=1" in response.headers["location"]
    assert "public_forms_ignored=" in response.headers["location"]

    async with AsyncSessionLocal() as session:
        entry = (await session.execute(
            select(ClubSetting).where(ClubSetting.key == "public_form_allowed_origins")
        )).scalar_one()
        assert entry.value == SITE

    page = await client.get("/admin/integrations")
    assert page.status_code == 200
    assert "/api/v1/public/forms/contact" in page.text
    assert SITE in page.text


# ---------------------------------------------------------------------------
# ALTCHA (ADR 0089)
# ---------------------------------------------------------------------------

from altcha import Challenge, Payload, solve_challenge  # noqa: E402

from app import form_altcha  # noqa: E402


@pytest.fixture
def _cheap_altcha(monkeypatch):
    # Solving at the production cost takes a second or so per challenge in
    # pure Python; the check itself doesn't depend on the cost.
    monkeypatch.setattr(form_altcha, "COST", 1)
    form_altcha.reset_used()
    yield
    form_altcha.reset_used()


async def _require_altcha(client, headers):
    response = await client.put(
        "/api/v1/club-settings/public_form_require_altcha", json={"value": "1"}, headers=headers,
    )
    assert response.status_code == 200, response.text


async def _solved(client):
    """What the widget would submit: a fetched challenge, solved."""
    response = await client.get("/api/v1/public/forms/challenge", headers=FROM_SITE)
    assert response.status_code == 200, response.text
    challenge = Challenge.from_dict(response.json())
    return Payload(challenge, solve_challenge(challenge)).to_base64()


async def test_challenge_only_for_allowed_origins_with_cors(client, admin_user, _cheap_altcha):
    headers = auth_header(await login(client, "admin@example.com"))
    closed = await client.get("/api/v1/public/forms/challenge", headers=FROM_SITE)
    assert closed.status_code == 403  # no origins configured yet

    await _allow_origins(client, headers)
    other = await client.get("/api/v1/public/forms/challenge", headers={"Origin": "https://evil.example"})
    assert other.status_code == 403

    response = await client.get("/api/v1/public/forms/challenge", headers=FROM_SITE)
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == SITE
    assert response.headers["cache-control"] == "no-store"
    body = response.json()
    assert body["signature"] and body["parameters"]["algorithm"] == "PBKDF2/SHA-256"

    preflight = await client.options("/api/v1/public/forms/challenge", headers={
        **FROM_SITE, "Access-Control-Request-Method": "GET", "Access-Control-Request-Headers": "content-type"})
    assert preflight.status_code == 204
    assert preflight.headers["access-control-allow-origin"] == SITE


async def test_altcha_not_checked_while_switched_off(client, admin_user, monkeypatch, _cheap_altcha):
    await _contact_setup(client, monkeypatch)
    response = await _post_contact(client, _contact_form())
    assert response.headers["location"] == f"{SUCCESS_URL}#ok"


async def test_contact_form_requires_a_valid_unused_altcha_solution(client, admin_user, monkeypatch, _cheap_altcha):
    fake_client = await _contact_setup(client, monkeypatch)
    await _require_altcha(client, auth_header(await login(client, "admin@example.com")))

    missing = await _post_contact(client, _contact_form())
    assert missing.headers["location"] == f"{ERROR_URL}#captcha"
    garbage = await _post_contact(client, _contact_form(altcha="bm90IGpzb24="))
    assert garbage.headers["location"] == f"{ERROR_URL}#captcha"

    solution = await _solved(client)
    accepted = await _post_contact(client, _contact_form(altcha=solution))
    assert accepted.headers["location"] == f"{SUCCESS_URL}#ok"
    assert len(fake_client.calls) == 1

    # The same solution a second time: a bot can't solve once and post many times.
    replayed = await _post_contact(client, _contact_form(altcha=solution))
    assert replayed.headers["location"] == f"{ERROR_URL}#captcha"
    assert len(fake_client.calls) == 1


async def test_altcha_rejects_tampered_and_expired_challenges(client, admin_user, monkeypatch, _cheap_altcha):
    await _contact_setup(client, monkeypatch)
    await _require_altcha(client, auth_header(await login(client, "admin@example.com")))

    # Lowering the stated cost after the fact breaks the server's signature.
    response = await client.get("/api/v1/public/forms/challenge", headers=FROM_SITE)
    data = response.json()
    data["parameters"]["cost"] = 0
    tampered = Challenge.from_dict(data)
    forged = Payload(tampered, solve_challenge(Challenge.from_dict(response.json()))).to_base64()
    assert (await _post_contact(client, _contact_form(altcha=forged))).headers["location"] == f"{ERROR_URL}#captcha"

    solution = await _solved(client)
    monkeypatch.setattr(form_altcha.time, "time", lambda: 10**10)  # far beyond the expiry
    assert (await _post_contact(client, _contact_form(altcha=solution))).headers["location"] == f"{ERROR_URL}#captcha"


async def test_signup_form_requires_altcha_too(client, admin_user, _cheap_altcha):
    headers, session = await _signup_setup(client)
    await _require_altcha(client, headers)

    rejected = await _post_signup(client, _signup_form(session["id"]))
    assert rejected.headers["location"] == f"{ERROR_URL}#captcha"
    assert await _get_session_participations(client, headers, session["id"]) == []

    accepted = await _post_signup(client, _signup_form(session["id"], altcha=await _solved(client)))
    assert accepted.headers["location"] == f"{SUCCESS_URL}#ok"


async def test_admin_switches_altcha_on_and_off(client, admin_user):
    await web_login(client)

    async def saved_value():
        async with AsyncSessionLocal() as session:
            return (await session.execute(
                select(ClubSetting.value).where(ClubSetting.key == "public_form_require_altcha")
            )).scalar_one()

    await client.post("/admin/integrations/public-forms", data={"public_form_origins": SITE, "require_altcha": "1"})
    assert await saved_value() == "1"
    page = await client.get("/admin/integrations")
    assert 'id="require_altcha"' in page.text and "checked" in page.text.split('id="require_altcha"')[1][:80]
    assert "/api/v1/public/forms/challenge" in page.text

    await client.post("/admin/integrations/public-forms", data={"public_form_origins": SITE})
    assert await saved_value() == "0"
