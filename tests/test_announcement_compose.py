"""
Issue #345 (ADR 0139): the compose popup. Writing and sending a message
in one step from wherever it starts (/members/, a member's page,
/applicants/, /announcements/), using the same channel code as the send
page, so ADR 0087's rules still hold.
"""
import base64
import re

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.auth import hash_password
from app.database import AsyncSessionLocal
from app.member_filters import MemberListFilter
from app.models import (
    Announcement, AnnouncementChannel, AnnouncementDeliveryStatus, Member, MemberEmail, User, UserRole,
)
from tests.conftest import auth_header, login
from tests.test_announcement_audience import _setup
from tests.test_announcements import _enable_module, web_login


def _fake_mail(monkeypatch):
    sent_to = []

    async def fake_send_email(to, subject, html_body, text_body=None, db=None):
        sent_to.append((to, subject))
        return True

    monkeypatch.setattr("app.announcement_mailer.send_email", fake_send_email)
    return sent_to


async def _announcements():
    async with AsyncSessionLocal() as db:
        return (await db.scalars(
            select(Announcement).options(selectinload(Announcement.deliveries)).order_by(Announcement.created_at)
        )).all()


def _channel_input(html: str, channel: str) -> str:
    match = re.search(r'<input[^>]*id="compose-channel-%s"[^>]*>' % channel, html)
    return match.group(0) if match else ""


def _picked(*member_ids) -> dict:
    return {"audience": "1", "audience_query": MemberListFilter(ids=tuple(member_ids)).query_string()}


async def test_popup_is_on_every_page_for_the_board_and_the_triggers_open_it(client, admin_user):
    _, ids = await _setup(client)
    members = (await client.get("/members/")).text
    assert 'id="compose-modal"' in members and "data-compose" in members  # "Write to selected"
    assert "data-compose" in (await client.get(f"/members/{ids['Unbeteiligt']}")).text
    assert "data-compose" in (await client.get("/announcements/")).text

    form = await client.get("/announcements/compose", params=_picked(ids["Unbeteiligt"]))
    assert form.status_code == 200 and form.json()["state"] == "form"
    html = form.json()["html"]
    assert 'id="compose-form"' in html and "1 picked by hand" in html
    # Email is ticked by default when the member has an address.
    assert "checked" in _channel_input(html, "EMAIL") and "checked" not in _channel_input(html, "LETTER")


async def test_no_popup_for_users_without_full_access_or_without_the_module(client, admin_user):
    await web_login(client, "admin@example.com")
    assert 'id="compose-modal"' not in (await client.get("/members/")).text  # module off by default
    assert (await client.get("/announcements/compose")).status_code == 404

    await _enable_module(client, auth_header(await login(client, "admin@example.com")))
    async with AsyncSessionLocal() as db:
        db.add(User(email="reader@example.com", name="Reader", password_hash=hash_password("testpasswort123"),
                    role=UserRole.READONLY))
        await db.commit()
    await web_login(client, "reader@example.com")
    assert 'id="compose-modal"' not in (await client.get("/members/")).text
    assert (await client.get("/announcements/compose")).status_code in (302, 303, 403)
    assert (await client.post("/announcements/compose", data={"action": "draft", "title": "x", "body_markdown": "y"})).status_code in (302, 303, 403)
    assert await _announcements() == []


async def test_save_and_send_email_in_one_step(client, admin_user, monkeypatch):
    _, ids = await _setup(client)
    sent_to = _fake_mail(monkeypatch)

    response = await client.post("/announcements/compose", data={
        **_picked(ids["Unbeteiligt"], ids["Optout"]), "action": "send", "channels": ["EMAIL"],
        "title": "Wasser", "body_markdown": "Am **Samstag**.",
    })
    assert response.status_code == 200
    result = response.json()
    assert result["state"] == "done" and result["downloads"] == []
    assert "Being sent to 1 recipient(s)." in result["html"]
    assert [to for to, _ in sent_to] == ["udo@example.org"]  # Olga opted out of email (#403)

    [announcement] = await _announcements()
    assert announcement.title == "Wasser" and sorted(announcement.audience_filter["ids"]) == sorted([ids["Unbeteiligt"], ids["Optout"]])
    assert announcement.delivery_for(AnnouncementChannel.EMAIL).status == AnnouncementDeliveryStatus.SENT
    assert result["edit_url"] == f"/announcements/{announcement.id}/edit"


async def test_letters_come_back_as_a_download_and_are_ticked_without_email(client, admin_user):
    _, ids = await _setup(client)
    form = (await client.get("/announcements/compose", params=_picked(ids["Papier"]))).json()["html"]
    assert "checked" in _channel_input(form, "LETTER")
    email = _channel_input(form, "EMAIL")
    assert "disabled" in email and "checked" not in email  # Paul has no email address

    response = await client.post("/announcements/compose", data={
        **_picked(ids["Papier"]), "action": "send", "channels": ["LETTER"],
        "title": "Brief", "body_markdown": "Hallo Paul.",
    })
    result = response.json()
    assert result["state"] == "done" and "1 letter(s) generated and downloaded." in result["html"]
    [download] = result["downloads"]
    assert download["filename"] == "Brief_letters.pdf"
    assert base64.b64decode(download["data"]).startswith(b"%PDF")
    [announcement] = await _announcements()
    assert announcement.delivery_for(AnnouncementChannel.LETTER).status == AnnouncementDeliveryStatus.SENT


async def test_club_news_print_pdf_without_website(client, admin_user):
    await _enable_module(client, auth_header(await login(client, "admin@example.com")))
    await web_login(client, "admin@example.com")
    form = (await client.get("/announcements/compose")).json()["html"]
    assert "compose-channel-PRINT" in form and "compose-channel-BLOG" not in form  # no website set up

    response = await client.post("/announcements/compose", data={
        "action": "send", "channels": ["PRINT", "BLOG"], "title": "Aushang", "body_markdown": "Kurz.",
    })
    result = response.json()
    assert "PDF generated and downloaded." in result["html"]
    assert [d["filename"] for d in result["downloads"]] == ["Aushang.pdf"]
    [announcement] = await _announcements()
    # Channels the popup didn't offer are ignored, not run.
    assert [d.channel for d in announcement.deliveries] == [AnnouncementChannel.PRINT]
    assert f'/announcements/{announcement.id}/print/download' in result["html"]


async def test_test_email_saves_a_draft_the_popup_keeps_editing_until_sent(client, admin_user, monkeypatch):
    _, ids = await _setup(client)
    sent_to = _fake_mail(monkeypatch)

    test = await client.post("/announcements/compose", data={
        **_picked(ids["Unbeteiligt"]), "action": "test", "test_email": "board@example.org",
        "title": "Entwurf", "body_markdown": "Erste Fassung.",
    })
    assert test.status_code == 200 and test.json()["state"] == "form"
    html = test.json()["html"]
    assert "Test email sent to board@example.org" in html
    assert sent_to == [("board@example.org", "[Test] Entwurf")]
    [draft] = await _announcements()
    assert f'name="announcement_id" value="{draft.id}"' in html and draft.deliveries == []

    sent = await client.post("/announcements/compose", data={
        "announcement_id": draft.id, "action": "send", "channels": ["EMAIL"],
        "title": "Endfassung", "body_markdown": "Zweite Fassung.",
    })
    assert sent.json()["state"] == "done"
    [announcement] = await _announcements()
    assert announcement.title == "Endfassung" and announcement.body_markdown == "Zweite Fassung."
    assert sent_to[-1] == ("udo@example.org", "Endfassung")

    # Once something went out, the popup can't touch it any more.
    again = await client.post("/announcements/compose", data={
        "announcement_id": draft.id, "action": "send", "channels": ["EMAIL"], "title": "Nochmal", "body_markdown": "x",
    })
    assert again.status_code == 409
    assert len(sent_to) == 2
    [announcement] = await _announcements()
    assert announcement.title == "Endfassung"


async def test_missing_text_keeps_the_typed_values_and_saves_nothing(client, admin_user):
    _, ids = await _setup(client)
    response = await client.post("/announcements/compose", data={
        **_picked(ids["Unbeteiligt"]), "action": "send", "channels": ["EMAIL"], "title": "Nur Titel", "body_markdown": " ",
    })
    assert response.status_code == 400 and response.json()["state"] == "form"
    html = response.json()["html"]
    assert "Please provide both a title and a body text." in html and 'value="Nur Titel"' in html
    assert 'name="audience_query"' in html  # still the same audience
    assert await _announcements() == []


async def test_draft_only_and_unknown_action(client, admin_user):
    _, ids = await _setup(client)
    draft = await client.post("/announcements/compose", data={
        **_picked(ids["Unbeteiligt"]), "action": "draft", "channels": ["EMAIL"], "title": "Später", "body_markdown": "Text.",
    })
    assert "Saved as a draft. Nothing was sent." in draft.json()["html"]
    [announcement] = await _announcements()
    assert announcement.deliveries == []
    assert (await client.post("/announcements/compose", data={"action": "publish", "title": "x", "body_markdown": "y"})).status_code == 400


async def test_rendered_values_are_escaped(client, admin_user):
    _, ids = await _setup(client)
    async with AsyncSessionLocal() as db:
        member = Member(first_name='<img src=x onerror=alert(1)>', last_name="Evil")
        member.email_addresses.append(MemberEmail(address="evil@example.org", is_primary=True))
        db.add(member)
        await db.commit()
    html = (await client.get("/announcements/compose", params=_picked(member.id))).json()["html"]
    assert "<img src=x" not in html and "&lt;img src=x onerror=alert(1)&gt;" in html
    response = await client.post("/announcements/compose", data={
        **_picked(member.id), "action": "draft", "title": '"><script>alert(2)</script>', "body_markdown": "x",
    })
    assert "<script>alert(2)" not in response.json()["html"]


async def test_every_kind_of_message_offers_all_four_channels(client, admin_user):
    """Issue #399: email, website draft (with a website), notice and
    letters for every kind of message -- except letters to applicants,
    who have no postal address on file."""
    _, ids = await _setup(client)

    form = (await client.get("/announcements/compose", params=_picked(ids["Papier"]))).json()["html"]
    assert _channel_input(form, "PRINT") and _channel_input(form, "LETTER")

    club = (await client.get("/announcements/compose")).json()["html"]
    assert _channel_input(club, "PRINT") and _channel_input(club, "LETTER")

    # Club news as letters: the active members without email consent who
    # have a postal address -- Olga (opted out) and Paul (no email).
    # Nina has neither, Udo gets the email.
    create = await client.post("/announcements/new", data={"title": "News", "body_markdown": "Hallo"})
    club_id = create.headers["location"].split("/")[2]
    letters = await client.post(f"/announcements/{club_id}/letters")
    assert letters.status_code == 200 and letters.headers["content-type"] == "application/pdf"
    [announcement] = [a for a in await _announcements() if a.id == club_id]
    assert announcement.delivery_for(AnnouncementChannel.LETTER).error_message == "2 letter(s) generated."

    # A message to members can be printed as a notice too.
    picked = await client.post("/announcements/new", data={
        "title": "Wasser", "body_markdown": "Am Samstag.", **_picked(ids["Papier"]),
    })
    picked_id = picked.headers["location"].split("/")[2]
    edit = await client.get(f"/announcements/{picked_id}/edit")
    assert f"/announcements/{picked_id}/print" in edit.text and 'name="print_qr_code"' in edit.text
    assert (await client.post(f"/announcements/{picked_id}/print")).status_code != 409
