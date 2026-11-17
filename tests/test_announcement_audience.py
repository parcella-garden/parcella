"""
Issue #242: from the filtered /members/ list, write to exactly those
members -- by email, and by letter for those without an email address
(ADR 0095). Reuses the announcements module: a "targeted" announcement
stores the member-list filter (MemberListFilter) and offers EMAIL and
LETTER instead of EMAIL/BLOG/PRINT.
"""
import urllib.parse

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import AsyncSessionLocal
from app.models import Announcement, AnnouncementChannel, Member, MemberEmail
from app.services.members import tag_member
from tests.conftest import auth_header, login
from tests.test_announcements import _enable_module, web_login


async def _setup(client):
    await _enable_module(client, auth_header(await login(client, "admin@example.com")))
    await web_login(client, "admin@example.com")
    async with AsyncSessionLocal() as db:
        def member(first, last, email=None, street=None, opted_in=True):
            m = Member(first_name=first, last_name=last, email_notifications=opted_in,
                       street=street, postal_code="04109" if street else None, city="Leipzig" if street else None)
            if email:
                m.email_addresses.append(MemberEmail(address=email, is_primary=True))
            db.add(m)
            return m

        opted_out = member("Olga", "Optout", email="olga@example.org", street="Weg 1", opted_in=False)
        paper = member("Paul", "Papier", street="Gartenweg 2")
        nowhere = member("Nina", "Nirgends")
        outsider = member("Udo", "Unbeteiligt", email="udo@example.org")
        await db.commit()
        for m in (opted_out, paper, nowhere):
            tag = await tag_member(db, m.id, name="Wasser")
        await db.commit()
        return tag.id, {m.last_name: m.id for m in (opted_out, paper, nowhere, outsider)}


async def _create_targeted(client, tag_id, title="Wasser abstellen", **extra):
    response = await client.post("/announcements/new", data={
        "title": title, "body_markdown": "Am **Samstag** wird das Wasser abgestellt.",
        "audience": "1", "audience_query": f"tag={tag_id}", **extra,
    })
    assert response.status_code == 303, response.text
    return response.headers["location"].split("/")[2]


async def _announcement(announcement_id):
    async with AsyncSessionLocal() as db:
        return (await db.execute(
            select(Announcement).where(Announcement.id == announcement_id).options(selectinload(Announcement.deliveries))
        )).scalar_one()


async def test_write_to_filtered_members_by_email_and_letter(client, admin_user, monkeypatch):
    tag_id, ids = await _setup(client)

    members_page = await client.get(f"/members/?tag={tag_id}")
    link = f"/announcements/new?audience=1&amp;audience_query={urllib.parse.quote('tag=' + tag_id, safe='')}"
    assert link in members_page.text

    preview = await client.get(f"/announcements/new?audience=1&audience_query=tag%3D{tag_id}")
    assert preview.status_code == 200
    assert "Nina Nirgends" in preview.text  # unreachable, named so the board can fix the record

    announcement_id = await _create_targeted(client, tag_id)
    stored = await _announcement(announcement_id)
    assert stored.is_targeted and stored.audience_filter["tag"] == tag_id

    edit = await client.get(f"/announcements/{announcement_id}/edit")
    assert edit.status_code == 200
    assert f"/announcements/{announcement_id}/letters" in edit.text
    assert f"/announcements/{announcement_id}/send/blog" not in edit.text

    sent_to = []

    async def fake_send_email(to, subject, html_body, text_body=None, db=None):
        sent_to.append(to)
        return True

    monkeypatch.setattr("app.announcement_mailer.send_email", fake_send_email)
    assert (await client.post(f"/announcements/{announcement_id}/send/email")).status_code == 303
    # Only the tagged member with an address -- although she opted out of
    # the email info: a targeted message isn't a newsletter.
    assert sent_to == ["olga@example.org"]

    # Not a blog post, not a notice-board page.
    assert (await client.post(f"/announcements/{announcement_id}/send/blog")).status_code == 409
    assert (await client.post(f"/announcements/{announcement_id}/print")).status_code == 409

    letters = await client.post(f"/announcements/{announcement_id}/letters")
    assert letters.status_code == 200
    assert letters.headers["content-type"] == "application/pdf" and letters.content.startswith(b"%PDF")
    delivery = (await _announcement(announcement_id)).delivery_for(AnnouncementChannel.LETTER)
    assert delivery.status.value == "SENT"
    # Paul only (no email, has an address); no names are stored.
    assert delivery.error_message == "1 letter(s) generated."


async def test_letters_for_everyone_and_header_safe_file_name(client, admin_user):
    tag_id, _ = await _setup(client)
    announcement_id = await _create_targeted(
        client, tag_id, title='Wasser — Ablesung "2026"', letters_for_all="true",
    )
    letters = await client.post(f"/announcements/{announcement_id}/letters")
    assert letters.status_code == 200
    disposition = letters.headers["content-disposition"]
    assert disposition.isascii() and disposition.count('"') == 2
    delivery = (await _announcement(announcement_id)).delivery_for(AnnouncementChannel.LETTER)
    assert delivery.error_message == "2 letter(s) generated."  # Olga (has email) and Paul


async def test_club_news_has_no_letter_channel(client, admin_user):
    await _setup(client)
    create = await client.post("/announcements/new", data={"title": "News", "body_markdown": "Hallo"})
    announcement_id = create.headers["location"].split("/")[2]
    assert not (await _announcement(announcement_id)).is_targeted
    assert (await client.post(f"/announcements/{announcement_id}/letters")).status_code == 409
    assert f"/announcements/{announcement_id}/send/blog" in (await client.get(f"/announcements/{announcement_id}/edit")).text


async def test_unfiltered_list_is_club_news_not_a_targeted_message(client, admin_user):
    """Review finding: an empty filter would reach everyone while
    ignoring the email-info opt-out -- it must become club news."""
    await _setup(client)
    assert "audience_query=" not in (await client.get("/members/")).text
    response = await client.post("/announcements/new", data={
        "title": "Alle", "body_markdown": "Hallo", "audience": "1", "audience_query": "",
    })
    assert not (await _announcement(response.headers["location"].split("/")[2])).is_targeted


async def test_hand_picked_members_for_export_and_message(client, admin_user, monkeypatch):
    """Issue #337: filter the list (here: all with email), tick some rows
    by hand, then export or write to exactly those. The picked ids
    intersect with the filter and are stored with it."""
    from app.member_filters import MemberListFilter

    tag_id, ids = await _setup(client)
    picked = [ids["Optout"], ids["Unbeteiligt"]]

    page = await client.get(f"/members/?tag={tag_id}")
    assert 'id="member-pick"' in page.text and 'name="ids"' in page.text

    # The pick form's export: filter fields + ticked ids. Udo isn't tagged,
    # so he drops out although he was "picked".
    export = await client.get("/members/export/csv", params=[("tag", tag_id), *[("ids", i) for i in picked]])
    assert export.status_code == 200
    assert "Optout" in export.text and "Papier" not in export.text and "Unbeteiligt" not in export.text

    # Without a tag filter both picked members are in, nobody else.
    export = await client.get("/members/export/csv", params=[("ids", i) for i in picked])
    assert "Optout" in export.text and "Unbeteiligt" in export.text and "Papier" not in export.text

    # The list shows only the picked ones, with a way back.
    page = await client.get("/members/", params=[("ids", i) for i in picked])
    assert "Unbeteiligt" in page.text and "Papier" not in page.text and "Show the whole list" in page.text

    # "Write to selected": the pick form sends audience_query + ids.
    preview = await client.get("/announcements/new", params=[
        ("audience", "1"), ("audience_query", ""), *[("ids", i) for i in picked],
    ])
    assert preview.status_code == 200 and "2 picked by hand" in preview.text

    response = await client.post("/announcements/new", data={
        "title": "Picked", "body_markdown": "Nur an euch.", "audience": "1",
        "audience_query": MemberListFilter(ids=tuple(picked)).query_string(),
    })
    assert response.status_code == 303
    stored = await _announcement(response.headers["location"].split("/")[2])
    assert sorted(stored.audience_filter["ids"]) == sorted(picked)

    sent_to = []

    async def fake_send_email(to, subject, html_body, text_body=None, db=None):
        sent_to.append(to)
        return True

    monkeypatch.setattr("app.announcement_mailer.send_email", fake_send_email)
    assert (await client.post(f"/announcements/{stored.id}/send/email")).status_code == 303
    assert sorted(sent_to) == ["olga@example.org", "udo@example.org"]


def test_member_filter_ids_round_trip_and_cleaning():
    import pytest
    from fastapi import HTTPException
    from app.member_filters import MAX_PICKED_MEMBERS, MemberListFilter

    f = MemberListFilter(email_info_only=True, ids=("a", "a", " ", "x" * 37, "b"))
    assert f.ids == ("a", "b")
    assert MemberListFilter.from_dict(f.to_dict()) == f  # stored JSON list comes back as the same filter
    assert f.query_string() == "email_info_only=true&ids=a&ids=b"
    assert f.without_ids() == MemberListFilter(email_info_only=True)
    assert not MemberListFilter(ids=("a",)).is_empty() and MemberListFilter.from_dict({"ids": []}).is_empty()
    with pytest.raises(HTTPException):
        MemberListFilter(ids=tuple(str(i) for i in range(MAX_PICKED_MEMBERS + 1)))
