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
