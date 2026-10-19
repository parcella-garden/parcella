"""
Per-language tag names (ADR 0098): a tag typed as "Rote Liste" shows as
"red flag" while the club runs in English, and typing the translated
name reuses the tag instead of creating a second one. Same helpers for
member tags and external-contact tags (app/tag_translations.py).
"""
from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models import ClubSetting, ExternalContact, ExternalContactTag, Member, MemberTag
from tests.test_detail_page_navigation import web_login


async def _set_language(code):
    async with AsyncSessionLocal() as db:
        entry = await db.scalar(select(ClubSetting).where(ClubSetting.key == "language"))
        if entry is None:
            db.add(ClubSetting(key="language", value=code, description="test"))
        else:
            entry.value = code
        await db.commit()


async def test_contact_tag_shows_translation_in_club_language(client, admin_user):
    async with AsyncSessionLocal() as db:
        tag = ExternalContactTag(name="Rote Liste")
        contact = ExternalContact(company_name="Zwielicht GmbH", tags=[tag])
        db.add(contact)
        await db.commit()
        tag_id = tag.id
    await web_login(client, "admin@example.com")

    response = await client.post(f"/contacts/tags/{tag_id}/translations", data={"name_en": "  red   flag ", "name_pl": ""})
    assert response.status_code == 303
    async with AsyncSessionLocal() as db:
        assert (await db.get(ExternalContactTag, tag_id)).translations == {"en": "red flag"}

    await _set_language("en")
    page = (await client.get("/contacts/")).text
    assert "red flag" in page and "Rote Liste" not in page

    await _set_language("de")
    page = (await client.get("/contacts/")).text
    assert "Rote Liste" in page and "red flag" not in page


async def test_typing_a_translated_name_reuses_the_member_tag(client, admin_user):
    async with AsyncSessionLocal() as db:
        db.add(MemberTag(name="Wasserteam", translations={"en": "water team"}))
        member = Member(first_name="Anna", last_name="Aal")
        db.add(member)
        await db.commit()
        member_id = member.id
    await web_login(client, "admin@example.com")

    assert (await client.post(f"/members/{member_id}/tags/add", data={"name": "Water Team"})).status_code == 303
    async with AsyncSessionLocal() as db:
        assert [t.name for t in (await db.scalars(select(MemberTag))).all()] == ["Wasserteam"]


async def test_translation_may_not_reuse_another_tags_name(client, admin_user):
    async with AsyncSessionLocal() as db:
        first, second = MemberTag(name="Vorstand"), MemberTag(name="Board")
        db.add_all([first, second])
        await db.commit()
        first_id = first.id
    await web_login(client, "admin@example.com")

    response = await client.post(f"/members/tags/{first_id}/translations", data={"name_en": "board"})
    assert response.status_code == 303 and "error=" in response.headers["location"]
    async with AsyncSessionLocal() as db:
        assert (await db.get(MemberTag, first_id)).translations is None


async def test_tags_page_offers_a_field_per_language(client, admin_user):
    async with AsyncSessionLocal() as db:
        db.add(MemberTag(name="Heckenteam"))
        await db.commit()
    await web_login(client, "admin@example.com")

    page = (await client.get("/members/tags")).text
    for code in ("de", "en", "pl", "cs", "sk", "fr", "nl"):
        assert f'name="name_{code}"' in page
