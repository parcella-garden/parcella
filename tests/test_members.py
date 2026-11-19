"""Tests for the members CSV import column-mapping wizard (issue #227).

Members CSV import previously had zero test coverage despite existing
since before this file was created -- these are its first tests.
"""
import base64

from tests.conftest import login, auth_header


def _b64_csv(text: str) -> str:
    return base64.b64encode(text.encode("utf-8")).decode("ascii")


async def _web_login(client, email: str, password: str = "testpasswort123") -> None:
    response = await client.post("/auth/login", data={"email": email, "password": password})
    assert response.status_code in (302, 303)


async def test_members_import_wizard_creates_member_with_emails_and_phones(client, admin_user):
    await _web_login(client, "admin@example.com")

    csv_text = (
        "Vorname;Nachname;Strasse;PLZ;Ort;Geburtsdatum;E-Mail-Adressen;Telefonnummern\n"
        "Erika;Musterfrau;Gartenweg 1;12345;Musterstadt;1980-05-15;"
        "erika@example.com;0123-456789\n"
    )
    import_response = await client.post(
        "/members/import/finalize",
        data={
            "csv_content_b64": _b64_csv(csv_text), "delimiter": ";",
            "map_0": "first_name", "map_1": "last_name", "map_2": "street", "map_3": "postal_code",
            "map_4": "city", "map_5": "date_of_birth", "map_6": "email_addresses", "map_7": "phone_numbers",
        },
        follow_redirects=False,
    )
    assert import_response.status_code in (302, 303)
    assert "imported" in import_response.headers["location"]

    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    from app.database import AsyncSessionLocal
    from app.models import Member

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Member)
            .options(selectinload(Member.email_addresses), selectinload(Member.phone_numbers))
            .where(Member.first_name == "Erika", Member.last_name == "Musterfrau")
        )
        member = result.scalar_one()
        assert member.street == "Gartenweg 1"
        assert member.postal_code == "12345"
        assert [e.address for e in member.email_addresses] == ["erika@example.com"]
        assert [p.number for p in member.phone_numbers] == ["0123-456789"]


async def test_member_create_form_saves_email_and_phone(client, admin_user):
    """The "New member" form's email/phone fields (added after issue #236:
    members created via /members/new had no way to enter an email address
    or phone number at all, only the email_notifications checkbox -- which
    defaults to checked regardless of whether an address was ever
    captured, letting a member silently end up eligible for announcement
    emails with zero stored addresses) must create the member's first
    MemberEmail/MemberPhone rows."""
    await _web_login(client, "admin@example.com")

    create_response = await client.post(
        "/members/new",
        data={
            "first_name": "Frieda", "last_name": "Neumitglied",
            "email": "frieda@example.com", "phone": "0123-456789",
            "email_notifications": "true",
        },
        follow_redirects=False,
    )
    assert create_response.status_code in (302, 303)

    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    from app.database import AsyncSessionLocal
    from app.models import Member

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Member)
            .options(selectinload(Member.email_addresses), selectinload(Member.phone_numbers))
            .where(Member.first_name == "Frieda", Member.last_name == "Neumitglied")
        )
        member = result.scalar_one()
        assert [e.address for e in member.email_addresses] == ["frieda@example.com"]
        assert member.email_addresses[0].is_primary is True
        assert [p.number for p in member.phone_numbers] == ["0123-456789"]
        assert member.phone_numbers[0].is_primary is True


async def test_member_create_form_allows_blank_email_and_phone(client, admin_user):
    """Leaving the new email/phone fields blank must not error or create
    MemberEmail/MemberPhone rows -- both fields are optional, addresses
    can still be added later on the member's detail page."""
    await _web_login(client, "admin@example.com")

    create_response = await client.post(
        "/members/new",
        data={"first_name": "Klaus", "last_name": "Ohnekontakt"},
        follow_redirects=False,
    )
    assert create_response.status_code in (302, 303)

    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    from app.database import AsyncSessionLocal
    from app.models import Member

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Member)
            .options(selectinload(Member.email_addresses), selectinload(Member.phone_numbers))
            .where(Member.first_name == "Klaus", Member.last_name == "Ohnekontakt")
        )
        member = result.scalar_one()
        assert member.email_addresses == []
        assert member.phone_numbers == []


async def test_members_import_wizard_updates_existing_member_without_touching_emails(client, admin_user):
    """Re-importing a row matching an existing member by name+DOB updates
    their fields but never touches existing emails/phones -- those are
    only seeded on create (see members_import_finalize)."""
    token = await login(client, "admin@example.com")
    headers = auth_header(token)

    member = (await client.post(
        "/api/v1/members",
        json={"first_name": "Theo", "last_name": "Aktiv", "date_of_birth": "1975-01-01", "street": "Old street"},
        headers=headers,
    )).json()

    await _web_login(client, "admin@example.com")
    add_email_response = await client.post(
        f"/members/{member['id']}/email/add",
        data={"address": "theo@example.com", "is_primary": "true"},
        follow_redirects=False,
    )
    assert add_email_response.status_code in (302, 303)

    csv_text = (
        "Vorname;Nachname;Geburtsdatum;Strasse;E-Mail-Adressen\n"
        "Theo;Aktiv;1975-01-01;New street;someone-else@example.com\n"
    )
    import_response = await client.post(
        "/members/import/finalize",
        data={
            "csv_content_b64": _b64_csv(csv_text), "delimiter": ";",
            "map_0": "first_name", "map_1": "last_name", "map_2": "date_of_birth",
            "map_3": "street", "map_4": "email_addresses",
        },
        follow_redirects=False,
    )
    assert import_response.status_code in (302, 303)

    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    from app.database import AsyncSessionLocal
    from app.models import Member

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Member)
            .options(selectinload(Member.email_addresses))
            .where(Member.id == member["id"])
        )
        updated = result.scalar_one()
        assert updated.street == "New street"
        # The CSV row's email column is ignored on update -- still just
        # the one email added via the web form, not duplicated or replaced.
        assert [e.address for e in updated.email_addresses] == ["theo@example.com"]


async def test_members_import_wizard_maps_reordered_headers(client, admin_user):
    """The mapping wizard (generalized from ADR 0062 in docs/ADR/0083)
    lets a CSV with different/reordered headers than Parcella's own
    export still be imported, by guessing a mapping the user confirms."""
    await _web_login(client, "admin@example.com")

    csv_text = (
        "Last name;First name;City\n"
        "Wiederkehr;Rosa;Beispielstadt\n"
    )
    preview = await client.post(
        "/members/import/preview",
        files={"file": ("import.csv", csv_text.encode("utf-8"), "text/csv")},
    )
    assert preview.status_code == 200
    assert 'value="last_name" selected' in preview.text
    assert 'value="first_name" selected' in preview.text
    assert 'value="city" selected' in preview.text

    import_response = await client.post(
        "/members/import/finalize",
        data={
            "csv_content_b64": _b64_csv(csv_text), "delimiter": ";",
            "map_0": "last_name", "map_1": "first_name", "map_2": "city",
        },
        follow_redirects=False,
    )
    assert import_response.status_code in (302, 303)

    from sqlalchemy import select
    from app.database import AsyncSessionLocal
    from app.models import Member

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Member).where(Member.first_name == "Rosa", Member.last_name == "Wiederkehr")
        )
        member = result.scalar_one()
        assert member.city == "Beispielstadt"


async def test_members_import_wizard_requires_name_columns_mapped(client, admin_user):
    await _web_login(client, "admin@example.com")

    csv_text = "City\nBeispielstadt\n"
    import_response = await client.post(
        "/members/import/finalize",
        data={"csv_content_b64": _b64_csv(csv_text), "delimiter": ";", "map_0": "city"},
        follow_redirects=False,
    )
    assert import_response.status_code in (302, 303)
    assert "error" in import_response.headers["location"]


# --- Issue #352: a re-import only changes what the file actually says ---

async def _member_import(client, csv_text: str, mapping: dict):
    data = {"csv_content_b64": _b64_csv(csv_text), "delimiter": ";"}
    data.update({f"map_{i}": field for i, field in mapping.items()})
    response = await client.post("/members/import/finalize", data=data, follow_redirects=False)
    assert response.status_code in (302, 303)
    return response.headers["location"]


async def _add_member(**fields):
    from app.database import AsyncSessionLocal
    from app.models import Member
    async with AsyncSessionLocal() as db:
        member = Member(**fields)
        db.add(member)
        await db.commit()
        return member.id


async def _get_member(member_id):
    from app.database import AsyncSessionLocal
    from app.models import Member
    async with AsyncSessionLocal() as db:
        return await db.get(Member, member_id)


async def test_member_reimport_keeps_unmapped_and_empty_fields_and_the_opt_out(client, admin_user):
    from datetime import date
    member_id = await _add_member(
        first_name="Olga", last_name="Optout", date_of_birth=date(1970, 1, 1), street="Alter Weg 1",
        postal_code="12345", city="Altstadt", iban="DE02120300000000202051", notes="Schlüssel 7",
        member_since=date(2001, 4, 1), email_notifications=False,
    )
    await _web_login(client, "admin@example.com")
    # Only the city changes; street is mapped but empty; IBAN, notes, consent aren't in the file.
    location = await _member_import(client, "Vorname;Nachname;Geburtsdatum;Strasse;Ort\nOlga;Optout;1970-01-01;;Neustadt\n",
                                    {0: "first_name", 1: "last_name", 2: "date_of_birth", 3: "street", 4: "city"})
    import urllib.parse
    assert "0 newly imported, 1 updated" in urllib.parse.unquote(location)

    member = await _get_member(member_id)
    assert member.city == "Neustadt"
    assert (member.street, member.postal_code, member.iban, member.notes) == ("Alter Weg 1", "12345", "DE02120300000000202051", "Schlüssel 7")
    assert member.member_since == date(2001, 4, 1)
    assert member.email_notifications is False  # was turned back on before


async def test_member_import_consent_column_changes_consent_only_when_filled_in(client, admin_user):
    from datetime import date
    member_id = await _add_member(first_name="Ida", last_name="Ja", date_of_birth=date(1980, 2, 2), email_notifications=True)
    await _web_login(client, "admin@example.com")
    mapping = {0: "first_name", 1: "last_name", 2: "date_of_birth", 3: "email_notifications"}
    await _member_import(client, "Vorname;Nachname;Geburtsdatum;E-Mail-Benachrichtigungen\nIda;Ja;1980-02-02;Nein\n", mapping)
    assert (await _get_member(member_id)).email_notifications is False
    await _member_import(client, "Vorname;Nachname;Geburtsdatum;E-Mail-Benachrichtigungen\nIda;Ja;1980-02-02;\n", mapping)
    assert (await _get_member(member_id)).email_notifications is False  # empty cell: unchanged
    await _member_import(client, "Vorname;Nachname;Geburtsdatum;E-Mail-Benachrichtigungen\nIda;Ja;1980-02-02;Ja\n", mapping)
    assert (await _get_member(member_id)).email_notifications is True


async def test_member_import_without_birth_date_never_picks_one_of_several_namesakes(client, admin_user):
    from datetime import date
    first = await _add_member(first_name="Hans", last_name="Meier", date_of_birth=date(1950, 1, 1), city="Nord")
    second = await _add_member(first_name="Hans", last_name="Meier", date_of_birth=date(1990, 1, 1), city="Süd")
    unique = await _add_member(first_name="Uta", last_name="Einzig", city="West")
    await _web_login(client, "admin@example.com")

    location = await _member_import(client, "Vorname;Nachname;Ort\nHans;Meier;Ost\nUta;Einzig;Ostwest\n",
                                     {0: "first_name", 1: "last_name", 2: "city"})
    import urllib.parse
    message = urllib.parse.unquote(location)
    assert "0 newly imported, 1 updated" in message
    assert "Row 2: several members are called Hans Meier, skipped." in message
    assert ((await _get_member(first)).city, (await _get_member(second)).city) == ("Nord", "Süd")
    assert (await _get_member(unique)).city == "Ostwest"


async def test_new_member_from_import_gets_email_consent_by_default(client, admin_user):
    await _web_login(client, "admin@example.com")
    location = await _member_import(client, "Vorname;Nachname\nNina;Neu\n;Ohnevorname\n", {0: "first_name", 1: "last_name"})
    import urllib.parse
    assert "Row 3: first or last name missing, skipped." in urllib.parse.unquote(location)

    from sqlalchemy import select
    from app.database import AsyncSessionLocal
    from app.models import Member
    async with AsyncSessionLocal() as db:
        member = (await db.execute(select(Member).where(Member.last_name == "Neu"))).scalar_one()
    assert member.email_notifications is True


async def test_member_import_tells_namesakes_apart_by_email_or_phone(client, admin_user):
    """kermie on #352: several members with the same name -> use the row's
    email address or phone number to find the right one."""
    from app.database import AsyncSessionLocal
    from app.models import Member, MemberEmail, MemberPhone
    async with AsyncSessionLocal() as db:
        senior = Member(first_name="Hans", last_name="Meier", city="Nord")
        senior.email_addresses.append(MemberEmail(address="hans.senior@example.org", is_primary=True))
        junior = Member(first_name="Hans", last_name="Meier", city="Süd")
        junior.phone_numbers.append(MemberPhone(number="0171 234-5678", is_primary=True))
        db.add_all([senior, junior])
        await db.commit()
        senior_id, junior_id = senior.id, junior.id
    await _web_login(client, "admin@example.com")

    mapping = {0: "first_name", 1: "last_name", 2: "city", 3: "email_addresses", 4: "phone_numbers"}
    location = await _member_import(client, (
        "Vorname;Nachname;Ort;E-Mail-Adressen;Telefonnummern\n"
        "Hans;Meier;Nordost;HANS.SENIOR@example.org;\n"   # email, any case
        "Hans;Meier;Südwest;;01712345678\n"               # same phone, other formatting
        "Hans;Meier;Irgendwo;fremd@example.org;\n"        # fits neither: skipped
    ), mapping)
    import urllib.parse
    message = urllib.parse.unquote(location)
    assert "0 newly imported, 2 updated" in message and "Row 4: several members are called Hans Meier" in message
    assert ((await _get_member(senior_id)).city, (await _get_member(junior_id)).city) == ("Nordost", "Südwest")


async def test_member_import_never_matches_a_different_name_by_shared_email(client, admin_user):
    from app.database import AsyncSessionLocal
    from app.models import Member, MemberEmail
    async with AsyncSessionLocal() as db:
        anna = Member(first_name="Anna", last_name="Paar", city="Hier")
        anna.email_addresses.append(MemberEmail(address="familie@example.org", is_primary=True))
        db.add(anna)
        await db.commit()
        anna_id = anna.id
    await _web_login(client, "admin@example.com")
    location = await _member_import(client, "Vorname;Nachname;Ort;E-Mail-Adressen\nBernd;Paar;Dort;familie@example.org\n",
                                    {0: "first_name", 1: "last_name", 2: "city", 3: "email_addresses"})
    import urllib.parse
    assert "1 newly imported, 0 updated" in urllib.parse.unquote(location)
    assert (await _get_member(anna_id)).city == "Hier"


async def test_member_import_of_an_excel_ansi_file(client, admin_user):
    """Issue #351: a Latin-1 file passed the preview, then crashed the final step (500)."""
    await _web_login(client, "admin@example.com")
    raw = "Vorname;Nachname;Ort\nJürgen;Größer;Köln\n".encode("latin-1")
    preview = await client.post("/members/import/preview", files={"file": ("mitglieder.csv", raw, "text/csv")})
    assert preview.status_code == 200 and "Größer" in preview.text
    response = await client.post("/members/import/finalize", data={
        "csv_content_b64": base64.b64encode(raw).decode("ascii"), "delimiter": ";",
        "map_0": "first_name", "map_1": "last_name", "map_2": "city",
    }, follow_redirects=False)
    assert response.status_code in (302, 303)

    from sqlalchemy import select
    from app.database import AsyncSessionLocal
    from app.models import Member
    async with AsyncSessionLocal() as db:
        member = (await db.execute(select(Member).where(Member.last_name == "Größer"))).scalar_one()
    assert (member.first_name, member.city) == ("Jürgen", "Köln")
