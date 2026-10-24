"""
Red flag on applicants (ADR 0098): an applicant whose name, email or
phone matches an external contact carrying the chosen tag gets a badge
on the list and a warning on the detail page. Checked live, nothing
stored on the applicant.
"""
from datetime import datetime, timezone

from sqlalchemy import select

from app.auth import hash_password
from app.database import AsyncSessionLocal
from app.models import (
    Applicant, ExternalContact, ExternalContactEmail, ExternalContactKind, ExternalContactPhone, ExternalContactTag,
    Group, GroupMembership, GroupModulePermission, User, UserRole,
)
from app.services.applicants import find_red_flags, save_red_flag_tag
from tests.test_detail_page_navigation import web_login


async def _flagged_contact(choose_tag=True, **fields):
    """A contact tagged "Rote Liste"; that tag is the red-flag tag unless
    choose_tag is False."""
    async with AsyncSessionLocal() as db:
        tag = ExternalContactTag(name="Rote Liste")
        contact = ExternalContact(
            kind=ExternalContactKind.PERSON, first_name=fields.get("first_name", "Max"), last_name=fields.get("last_name", "Ärger"), tags=[tag],
            deleted_at=fields.get("deleted_at"),
        )
        db.add(contact)
        await db.flush()
        db.add(ExternalContactEmail(contact_id=contact.id, address="aerger@example.org", is_primary=True))
        db.add(ExternalContactPhone(contact_id=contact.id, number="0170 999 111"))
        if choose_tag:
            await save_red_flag_tag(db, tag.id)
        await db.commit()
        return contact.id


async def _applicant(**fields):
    async with AsyncSessionLocal() as db:
        applicant = Applicant(email=fields.pop("email", "someone@example.org"), **fields)
        db.add(applicant)
        await db.commit()
        return applicant.id


async def _flags_for(applicant_id):
    async with AsyncSessionLocal() as db:
        applicant = await db.get(Applicant, applicant_id)
        return [m.fields for m in (await find_red_flags(db, [applicant])).get(applicant_id, [])]


async def test_matches_by_name_email_or_phone(client, admin_user):
    await _flagged_contact()
    by_name = await _applicant(first_name=" max ", last_name="ärger")
    by_email = await _applicant(email="AERGER@example.org")
    by_phone = await _applicant(phone="0170-999111")
    unrelated = await _applicant(first_name="Max", last_name="Freude", phone="0170 123")

    assert await _flags_for(by_name) == [["name"]]
    assert await _flags_for(by_email) == [["email"]]
    assert await _flags_for(by_phone) == [["phone"]]
    assert await _flags_for(unrelated) == []


async def test_no_flag_without_a_chosen_tag(client, admin_user):
    await _flagged_contact(choose_tag=False)
    assert await _flags_for(await _applicant(first_name="Max", last_name="Ärger")) == []


async def test_no_flag_for_a_deleted_contact(client, admin_user):
    await _flagged_contact(deleted_at=datetime.now(timezone.utc))
    assert await _flags_for(await _applicant(first_name="Max", last_name="Ärger")) == []


async def test_list_badge_and_detail_warning(client, admin_user):
    contact_id = await _flagged_contact()
    applicant_id = await _applicant(first_name="Max", last_name="Ärger")
    await _applicant(first_name="Clean", last_name="Person", email="clean@example.org")
    await web_login(client, "admin@example.com")

    page = (await client.get("/applicants/?filter=all")).text
    assert page.count("bi-flag-fill") == 1

    detail = (await client.get(f"/applicants/{applicant_id}")).text
    assert "bi-flag-fill" in detail and f'href="/contacts/{contact_id}"' in detail


async def test_warning_hides_contact_link_without_contacts_permission(client, admin_user):
    contact_id = await _flagged_contact()
    applicant_id = await _applicant(first_name="Max", last_name="Ärger")
    async with AsyncSessionLocal() as db:
        user = User(email="alloc@example.com", name="Alloc", password_hash=hash_password("testpasswort123"), role=UserRole.READONLY)
        group = Group(name="Allocation")
        db.add_all([user, group])
        await db.flush()
        db.add(GroupModulePermission(group_id=group.id, module="applicants", can_read=True))
        db.add(GroupMembership(user_id=user.id, group_id=group.id))
        await db.commit()
    await web_login(client, "alloc@example.com")

    detail = (await client.get(f"/applicants/{applicant_id}")).text
    assert "bi-flag-fill" in detail and f'href="/contacts/{contact_id}"' not in detail


async def test_choosing_the_red_flag_tag_on_the_tags_page(client, admin_user):
    await _flagged_contact(choose_tag=False)
    async with AsyncSessionLocal() as db:
        tag_id = await db.scalar(select(ExternalContactTag.id))
    await web_login(client, "admin@example.com")

    assert 'action="/contacts/tags/red-flag"' in (await client.get("/contacts/tags")).text
    assert (await client.post("/contacts/tags/red-flag", data={"tag_id": tag_id})).status_code == 303
    assert await _flags_for(await _applicant(first_name="Max", last_name="Ärger")) == [["name"]]

    assert (await client.post("/contacts/tags/red-flag", data={"tag_id": ""})).status_code == 303
    assert await _flags_for(await _applicant(first_name="Max", last_name="Ärger", email="x@example.org")) == []


async def test_a_flagged_company_flags_its_people(client, admin_user):
    async with AsyncSessionLocal() as db:
        tag = ExternalContactTag(name="Rote Liste")
        company = ExternalContact(kind=ExternalContactKind.COMPANY, company_name="Ärger GmbH", tags=[tag])
        person = ExternalContact(kind=ExternalContactKind.PERSON, first_name="Paul", last_name="Plage", company=company)
        db.add_all([company, person])
        await db.flush()
        await save_red_flag_tag(db, tag.id)
        await db.commit()
    assert await _flags_for(await _applicant(first_name="Paul", last_name="Plage")) == [["name"]]
