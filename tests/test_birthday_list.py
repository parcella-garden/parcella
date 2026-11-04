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


async def test_birthday_pdf_by_plot_with_contact_details(client, admin_user):
    """Issue #272: the print PDF covers the web list's 90 days (not the
    whole year), one row per member and current plot, sorted by plot
    number in natural order, with tags, the present opt-out, address,
    email and phone. Members past the window don't appear; one without
    a plot comes last."""
    import io

    from pypdf import PdfReader

    from app.birthdays import birthdays_by_parcel, upcoming_birthdays
    from app.models import MemberEmail, MemberParcel, MemberPhone, MemberTag, Parcel

    await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})
    async with AsyncSessionLocal() as session:
        p2, p10 = Parcel(plot_number="2"), Parcel(plot_number="10")
        hedge = MemberTag(name="Heckenteam")
        ten = Member(first_name="Tom", last_name="Ten", member_since=date(2020, 1, 1),
                     date_of_birth=_birth_date_in(3, 70), street="Gartenweg 10", postal_code="12345", city="Kleinstadt",
                     birthday_present_declined=True)
        ten.tags = [hedge]
        ten.email_addresses = [MemberEmail(address="tom@example.org", is_primary=True)]
        ten.phone_numbers = [MemberPhone(number="0170 1234567", is_primary=True)]
        two = Member(first_name="Tara", last_name="Two", member_since=date(2020, 1, 1),
                     date_of_birth=_birth_date_in(40, 33))
        loose = Member(first_name="Lou", last_name="Plotless", member_since=date(2020, 1, 1),
                       date_of_birth=_birth_date_in(1, 25))
        later = Member(first_name="Lena", last_name="Later", member_since=date(2020, 1, 1),
                       date_of_birth=_birth_date_in(120, 40))
        session.add_all([p2, p10, hedge, ten, two, loose, later])
        await session.flush()
        session.add_all([
            MemberParcel(member_id=ten.id, parcel_id=p10.id, assigned_from=date(2020, 1, 1)),
            MemberParcel(member_id=two.id, parcel_id=p2.id, assigned_from=date(2020, 1, 1)),
            MemberParcel(member_id=later.id, parcel_id=p2.id, assigned_from=date(2020, 1, 1)),
        ])
        await session.commit()

        rows = birthdays_by_parcel(await upcoming_birthdays(session, within_days=90, with_contact_details=True))
        assert [(r.plot_number, r.birthday.member.last_name) for r in rows] == [
            ("2", "Two"), ("10", "Ten"), (None, "Plotless"),
        ]
        assert rows[1].birthday.is_round  # turning 70

    response = await client.get("/calendar/birthdays/pdf")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.headers["content-disposition"] == f'attachment; filename="birthdays-{date.today().isoformat()}.pdf"'

    reader = PdfReader(io.BytesIO(response.content))
    # pypdf splits kerned glyphs ("T om"), so compare without whitespace.
    text = "".join("".join(page.extract_text() for page in reader.pages).split())
    for expected in ("TomTen", "TaraTwo", "LouPlotless", "Heckenteam", "Gartenweg10",
                     "tom@example.org", "01701234567", "Milestone", "Nopresent"):
        assert expected in text, (expected, text)
    assert "LenaLater" not in text  # outside the 90 days
    assert text.index("TaraTwo") < text.index("TomTen") < text.index("LouPlotless")
    width, height = reader.pages[0].mediabox.width, reader.pages[0].mediabox.height
    assert width > height  # landscape


async def test_birthday_pdf_escapes_member_data():
    """Names, addresses and tags are user-entered; the PDF's HTML must
    escape them (the #99 version put member names in raw)."""
    from types import SimpleNamespace

    from app.birthday_calendar_pdf import _body_html
    from app.birthdays import ParcelBirthdayRow, UpcomingBirthday

    member = SimpleNamespace(
        full_name="<b>Bold</b> & Co", street="<i>Street</i>", postal_code="1", city="X",
        tags=[SimpleNamespace(name="<script>", translations=None)], birthday_present_declined=False,
        email_addresses=[], phone_numbers=[],
    )
    row = ParcelBirthdayRow(plot_number="<7>", birthday=UpcomingBirthday(
        member=member, next_occurrence=date.today(), turning_age=41, is_round=False,
    ))
    html = _body_html("Heading", [row], "en", "de_DE")
    assert "<b>Bold</b>" not in html and "&lt;b&gt;Bold&lt;/b&gt; &amp; Co" in html
    assert "<script>" not in html and "<i>Street</i>" not in html
    assert "&lt;7&gt;" in html
