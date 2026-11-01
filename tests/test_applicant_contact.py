"""
Issue #267: contacting a NEW applicant by email from the detail page --
a boilerplate (Admin settings -> Applicants, or the built-in text),
edited per send, goes out over SMTP and the status moves to CONTACTED.
See "Contacting a new applicant" in docs/module-applicants.md.
"""
import pytest
from sqlalchemy import select

from app.auth import hash_password
from app.database import AsyncSessionLocal
from app.models import Applicant, ApplicantStatus, ChangeHistory, ClubSetting, User, UserRole
from tests.conftest import auth_header, login
from tests.test_admin_integrations_incoming_folder import web_login

SUBJECT = "Thank you for registering to our waiting list!"


async def _create_applicant(**fields) -> str:
    async with AsyncSessionLocal() as db:
        applicant = Applicant(email=fields.pop("email", "erika@example.org"), **fields)
        db.add(applicant)
        await db.commit()
        return applicant.id


async def _get(applicant_id: str) -> Applicant:
    async with AsyncSessionLocal() as db:
        return await db.get(Applicant, applicant_id)


async def _set(key: str, value: str) -> None:
    async with AsyncSessionLocal() as db:
        db.add(ClubSetting(key=key, value=value))
        await db.commit()


@pytest.fixture
def outbox(monkeypatch):
    sent = []

    async def fake_send_email(recipient, subject, html_body, text_body=None, db=None, attachments=None):
        sent.append({"to": recipient, "subject": subject, "html": html_body, "text": text_body})
        return True

    monkeypatch.setattr("app.services.applicants.send_email", fake_send_email)
    return sent


async def test_contacting_a_new_applicant_sends_the_email_and_sets_contacted(client, admin_user, outbox):
    applicant_id = await _create_applicant(first_name="Erika", last_name="Musterfrau")
    await web_login(client)

    page = await client.get(f"/applicants/{applicant_id}")
    assert f'action="/applicants/{applicant_id}/contact"' in page.text
    assert "Hello Erika Musterfrau," in page.text  # built-in text, name filled in
    assert SUBJECT in page.text

    response = await client.post(f"/applicants/{applicant_id}/contact", data={"body": "Hallo Erika,\nwillkommen!"})
    assert response.status_code == 303
    assert response.headers["location"] == f"/applicants/{applicant_id}?contacted=1"

    assert outbox == [{
        "to": "erika@example.org", "subject": SUBJECT,
        "html": '<html><body style="font-family: sans-serif;">Hallo Erika,<br>willkommen!</body></html>',
        "text": "Hallo Erika,\nwillkommen!",
    }]
    applicant = await _get(applicant_id)
    assert applicant.status == ApplicantStatus.CONTACTED
    async with AsyncSessionLocal() as db:
        history = (await db.execute(select(ChangeHistory).where(ChangeHistory.entity_id == applicant_id))).scalars().all()
    assert [(h.field_name, h.old_value, h.new_value) for h in history] == [("status", "NEW", "CONTACTED")]

    # Once contacted, the box is gone -- it's the first step only.
    page = await client.get(f"/applicants/{applicant_id}?contacted=1")
    assert "/contact\"" not in page.text
    assert "The email was sent" in page.text


async def test_user_entered_text_is_escaped_in_the_html_mail(client, admin_user, outbox):
    applicant_id = await _create_applicant()
    await web_login(client)
    await client.post(f"/applicants/{applicant_id}/contact", data={"body": "<script>alert(1)</script>"})
    assert "<script>" not in outbox[0]["html"]
    assert "&lt;script&gt;" in outbox[0]["html"]


async def test_club_boilerplate_and_placeholders(client, admin_user, outbox):
    await _set("applicant_contact_template", "Hello {name}, greetings from {club}. {unknown}")
    await _set("verein_name", "KGV Goldene Höhe")
    named = await _create_applicant(first_name="Erika")
    nameless = await _create_applicant(email="anon@example.org")
    await web_login(client)

    assert "Hello Erika, greetings from KGV Goldene Höhe. {unknown}" in (await client.get(f"/applicants/{named}")).text
    # No name: the placeholder goes away with the space before it.
    assert "Hello, greetings from KGV Goldene Höhe." in (await client.get(f"/applicants/{nameless}")).text

    admin_page = await client.get("/admin/settings")
    assert 'name="applicant_contact_template"' in admin_page.text


async def test_failed_send_keeps_the_status_and_the_text(client, admin_user, monkeypatch):
    async def failing_send_email(*args, **kwargs):
        return False

    monkeypatch.setattr("app.services.applicants.send_email", failing_send_email)
    applicant_id = await _create_applicant()
    await web_login(client)

    response = await client.post(f"/applicants/{applicant_id}/contact", data={"body": "Mein eigener Text"})
    assert response.status_code == 502
    assert "could not be sent" in response.text
    assert "Mein eigener Text" in response.text  # the board's edits aren't lost
    assert (await _get(applicant_id)).status == ApplicantStatus.NEW


async def test_only_new_applications_and_only_with_write_permission(client, admin_user, outbox):
    contacted = await _create_applicant(status=ApplicantStatus.CONTACTED)
    new = await _create_applicant(email="new@example.org")
    await web_login(client)
    assert "/contact\"" not in (await client.get(f"/applicants/{contacted}")).text
    assert (await client.post(f"/applicants/{contacted}/contact", data={"body": "Hi"})).status_code == 409
    assert (await client.post(f"/applicants/{new}/contact", data={"body": "   "})).status_code == 400
    assert outbox == []

    async with AsyncSessionLocal() as db:
        db.add(User(
            email="viewer@example.com", name="Viewer",
            password_hash=hash_password("testpasswort123"), role=UserRole.READONLY,
        ))
        await db.commit()
    await client.get("/auth/logout")
    await web_login(client, "viewer@example.com")
    assert (await client.post(f"/applicants/{new}/contact", data={"body": "Hi"})).status_code == 403
    assert outbox == []
    assert (await _get(new)).status == ApplicantStatus.NEW


async def test_rest_api_contact_uses_the_boilerplate_without_a_body(client, admin_user, outbox):
    applicant_id = await _create_applicant(first_name="Api")
    headers = auth_header(await login(client, "admin@example.com"))

    response = await client.post(f"/api/v1/applicants/{applicant_id}/contact", json={}, headers=headers)
    assert response.status_code == 200, response.text
    assert response.json()["status"] == "CONTACTED"
    assert outbox[0]["text"].startswith("Hello Api,")

    again = await client.post(f"/api/v1/applicants/{applicant_id}/contact", json={"body": "x"}, headers=headers)
    assert again.status_code == 409
    assert len(outbox) == 1
