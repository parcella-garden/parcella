"""
Birthday list features: declining presents (issue #269) and member tags
(issue #271). The present flag is set on
the member form, shown on the detail page and the birthday list, and
available through the REST API.
"""
from datetime import date, timedelta

from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models import Member
from tests.conftest import auth_header, login


def _birth_date_in(days: int, age: int) -> date:
    soon = date.today() + timedelta(days=days)
    return soon.replace(year=soon.year - age)


async def test_declined_presents_flag_on_form_detail_and_birthday_list(client, admin_user):
    await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})

    create = await client.post("/members/new", data={
        "first_name": "Greta", "last_name": "Giftless",
        "date_of_birth": _birth_date_in(10, 61).isoformat(),
        "member_since": "2020-01-01", "birthday_present_declined": "on",
    })
    assert create.status_code in (302, 303)
    await client.post("/members/new", data={
        "first_name": "Paul", "last_name": "Presents",
        "date_of_birth": _birth_date_in(12, 50).isoformat(), "member_since": "2020-01-01",
    })

    async with AsyncSessionLocal() as session:
        greta = (await session.scalars(select(Member).where(Member.last_name == "Giftless"))).one()
        paul = (await session.scalars(select(Member).where(Member.last_name == "Presents"))).one()
        assert greta.birthday_present_declined is True
        assert paul.birthday_present_declined is False

    edit_form = await client.get(f"/members/{greta.id}/edit")
    assert 'name="birthday_present_declined"' in edit_form.text

    page = (await client.get("/calendar/birthdays")).text
    assert "Present" in page  # column header
    def row_of(name: str) -> str:
        return page[page.index(name):].split("</tr>")[0]

    assert "No present" in row_of("Greta Giftless")
    assert "No present" not in row_of("Paul Presents")

    # Unchecking it on edit clears it again.
    await client.post(f"/members/{greta.id}/edit", data={
        "first_name": "Greta", "last_name": "Giftless", "member_since": "2020-01-01",
    })
    async with AsyncSessionLocal() as session:
        assert (await session.get(Member, greta.id)).birthday_present_declined is False


async def test_declined_presents_flag_in_api(client, admin_user):
    token = await login(client, "admin@example.com")
    created = await client.post(
        "/api/v1/members", headers=auth_header(token),
        json={"first_name": "Api", "last_name": "Opt-Out", "birthday_present_declined": True},
    )
    assert created.status_code in (200, 201), created.text
    assert created.json()["birthday_present_declined"] is True

    member_id = created.json()["id"]
    updated = await client.put(
        f"/api/v1/members/{member_id}", headers=auth_header(token),
        json={"birthday_present_declined": False},
    )
    assert updated.status_code == 200, updated.text
    assert updated.json()["birthday_present_declined"] is False


async def test_birthday_list_shows_member_tags(client, admin_user):
    """Issue #271: the birthday list has a Tags column with the member's
    tags, translated (ADR 0098) and linking to the filtered member list."""
    from app.models import MemberTag

    await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})
    async with AsyncSessionLocal() as session:
        board = MemberTag(name="Erweiterter Vorstand", translations={"en": "Extended board"})
        tagged = Member(first_name="Tina", last_name="Tagged", member_since=date(2020, 1, 1),
                        date_of_birth=_birth_date_in(5, 44))
        tagged.tags = [board]
        session.add_all([board, tagged, Member(
            first_name="Ulla", last_name="Untagged", member_since=date(2020, 1, 1),
            date_of_birth=_birth_date_in(6, 45),
        )])
        await session.commit()
        tag_id = board.id

    page = (await client.get("/calendar/birthdays")).text
    assert "Tags" in page

    def row_of(name: str) -> str:
        return page[page.index(name):].split("</tr>")[0]

    assert "Extended board" in row_of("Tina Tagged")  # English UI -> translated name
    assert f"/members/?tag={tag_id}" in row_of("Tina Tagged")
    assert "Extended board" not in row_of("Ulla Untagged")
