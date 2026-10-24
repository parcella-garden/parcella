"""
Issues #246/#247: tick applicants on /applicants/ (all, none or some)
and write to exactly those by email, reusing the announcements module
(ADR 0112). The selection is a stored list of applicant ids; an address
shared by several picked applications gets the message once.
"""
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import AsyncSessionLocal
from app.models import Announcement, AnnouncementChannel, Applicant
from tests.conftest import auth_header, login
from tests.test_announcements import _enable_module, web_login


async def _applicant(email, first_name, last_name):
    async with AsyncSessionLocal() as db:
        applicant = Applicant(email=email, first_name=first_name, last_name=last_name)
        db.add(applicant)
        await db.commit()
        return applicant.id


async def _setup(client):
    await _enable_module(client, auth_header(await login(client, "admin@example.com")))
    await web_login(client, "admin@example.com")
    return {
        "anna": await _applicant("anna@example.org", "Anna", "Acker"),
        "anna_again": await _applicant(" ANNA@example.org ", "Anna", "Acker"),
        "bert": await _applicant("bert@example.org", "Bert", "Beet"),
        "carla": await _applicant("carla@example.org", "Carla", "Kompost"),
    }


async def _announcement(announcement_id):
    async with AsyncSessionLocal() as db:
        return (await db.execute(
            select(Announcement).where(Announcement.id == announcement_id).options(selectinload(Announcement.deliveries))
        )).scalar_one()


async def test_list_offers_picker_only_with_announcements(client, admin_user):
    await web_login(client, "admin@example.com")
    await _applicant("solo@example.org", "Solo", "Bewerber")
    without = await client.get("/applicants/?filter=all")
    assert without.status_code == 200
    assert 'class="form-check-input pick-applicant"' not in without.text

    await _enable_module(client, auth_header(await login(client, "admin@example.com")))
    with_module = await client.get("/applicants/?filter=all")
    assert 'class="form-check-input pick-applicant"' in with_module.text
    assert 'action="/announcements/new"' in with_module.text


async def test_write_to_picked_applicants_once_per_address(client, admin_user, monkeypatch):
    ids = await _setup(client)
    picked = [ids["anna"], ids["anna_again"], ids["bert"]]
    query = "audience_kind=applicants&" + "&".join(f"applicant_ids={i}" for i in picked)

    preview = await client.get(f"/announcements/new?{query}")
    assert preview.status_code == 200
    assert "Bert Beet" in preview.text and "Carla Kompost" not in preview.text
    assert "1 selected application(s) share an address" in preview.text

    response = await client.post("/announcements/new", data={
        "title": "Besichtigung", "body_markdown": "Am Samstag zeigen wir freie Gärten.",
        "audience_kind": "applicants", "applicant_ids": picked,
    })
    assert response.status_code == 303, response.text
    announcement_id = response.headers["location"].split("/")[2]
    stored = await _announcement(announcement_id)
    assert stored.is_applicant_message and stored.is_targeted
    assert stored.audience_applicant_ids == picked and stored.audience_filter is None

    edit = await client.get(f"/announcements/{announcement_id}/edit")
    assert f"/announcements/{announcement_id}/letters" not in edit.text
    assert f"/announcements/{announcement_id}/send/blog" not in edit.text

    sent_to = []

    async def fake_send_email(to, subject, html_body, text_body=None, db=None):
        sent_to.append(to)
        return True

    monkeypatch.setattr("app.announcement_mailer.send_email", fake_send_email)
    assert (await client.post(f"/announcements/{announcement_id}/send/email")).status_code == 303
    # Anna once (her two applications differ only in case/blanks), Bert, not Carla.
    assert sorted(sent_to) == ["anna@example.org", "bert@example.org"]
    assert (await _announcement(announcement_id)).delivery_for(AnnouncementChannel.EMAIL).status.value == "SENT"

    # Email only: no blog post, notice-board page or letters.
    assert (await client.post(f"/announcements/{announcement_id}/send/blog")).status_code == 409
    assert (await client.post(f"/announcements/{announcement_id}/print")).status_code == 409
    assert (await client.post(f"/announcements/{announcement_id}/letters")).status_code == 409


async def test_empty_or_unknown_selection_is_refused(client, admin_user):
    await _setup(client)
    assert (await client.get("/announcements/new?audience_kind=applicants")).status_code == 400
    assert (await client.get(
        "/announcements/new?audience_kind=applicants&applicant_ids=00000000-0000-0000-0000-000000000000"
    )).status_code == 400
    response = await client.post("/announcements/new", data={
        "title": "x", "body_markdown": "y", "audience_kind": "applicants",
    })
    assert response.status_code == 400
    async with AsyncSessionLocal() as db:
        assert (await db.scalars(select(Announcement))).all() == []
