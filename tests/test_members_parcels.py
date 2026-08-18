"""Tests for members, parcels, and their m:n assignment."""
from tests.conftest import login, auth_header


async def test_treasurer_without_group_grant_is_blocked_from_member_write_via_api(client):
    """ADR 0070: api_members.py used require_write_access (role-only) --
    ANY TREASURER could write members via the API regardless of Group
    configuration, even one a Group deliberately did not grant
    members_parcels:write to (correctly blocked in the HTML UI). Now
    the API checks the same Group-derived permission as HTML."""
    from app.database import AsyncSessionLocal
    from app.models import User, UserRole
    from app.auth import hash_password

    async with AsyncSessionLocal() as db:
        user = User(
            email="treasurer-no-group-members@example.com", name="Treasurer No Group",
            password_hash=hash_password("testpasswort123"), role=UserRole.TREASURER,
        )
        db.add(user)
        await db.commit()

    token = await login(client, "treasurer-no-group-members@example.com")
    response = await client.post(
        "/api/v1/members", json={"first_name": "Erika", "last_name": "Musterfrau"},
        headers=auth_header(token),
    )
    assert response.status_code == 403


async def test_treasurer_without_group_grant_is_blocked_from_parcel_write_via_api(client):
    """ADR 0070: api_parcels.py used require_write_access (role-only) --
    ANY TREASURER could write parcels via the API regardless of Group
    configuration. Now the API checks the same Group-derived permission
    as HTML (members_parcels governs both members and parcels)."""
    from app.database import AsyncSessionLocal
    from app.models import User, UserRole
    from app.auth import hash_password

    async with AsyncSessionLocal() as db:
        user = User(
            email="treasurer-no-group-parcels@example.com", name="Treasurer No Group",
            password_hash=hash_password("testpasswort123"), role=UserRole.TREASURER,
        )
        db.add(user)
        await db.commit()

    token = await login(client, "treasurer-no-group-parcels@example.com")
    response = await client.post(
        "/api/v1/parcels", json={"plot_number": "G900"}, headers=auth_header(token),
    )
    assert response.status_code == 403


async def test_readonly_with_group_grant_can_write_parcels_via_api(client):
    """Flip side: a READONLY user granted members_parcels:write via a
    Group could already write parcels through the HTML UI, but the
    role-only API check blocked them regardless of Group membership."""
    from app.database import AsyncSessionLocal
    from app.models import User, UserRole, Group, GroupModulePermission, GroupMembership
    from app.auth import hash_password

    async with AsyncSessionLocal() as db:
        user = User(
            email="readonly-with-group-parcels@example.com", name="Readonly With Group",
            password_hash=hash_password("testpasswort123"), role=UserRole.READONLY,
        )
        db.add(user)
        await db.flush()

        group = Group(name="Parcel Handlers")
        db.add(group)
        await db.flush()
        db.add(GroupModulePermission(group_id=group.id, module="members_parcels", can_read=True, can_write=True))
        db.add(GroupMembership(user_id=user.id, group_id=group.id))
        await db.commit()

    token = await login(client, "readonly-with-group-parcels@example.com")
    response = await client.post(
        "/api/v1/parcels", json={"plot_number": "G901"}, headers=auth_header(token),
    )
    assert response.status_code == 201, response.text


async def test_readonly_with_group_grant_can_write_members_via_api(client):
    """Flip side of the bug above: a READONLY user granted
    members_parcels:write via a Group could already write members
    through the HTML UI, but the role-only API check blocked them
    regardless of Group membership. Pure bug fix: both surfaces now
    agree."""
    from app.database import AsyncSessionLocal
    from app.models import User, UserRole, Group, GroupModulePermission, GroupMembership
    from app.auth import hash_password

    async with AsyncSessionLocal() as db:
        user = User(
            email="readonly-with-group-members@example.com", name="Readonly With Group",
            password_hash=hash_password("testpasswort123"), role=UserRole.READONLY,
        )
        db.add(user)
        await db.flush()

        group = Group(name="Member Handlers")
        db.add(group)
        await db.flush()
        db.add(GroupModulePermission(group_id=group.id, module="members_parcels", can_read=True, can_write=True))
        db.add(GroupMembership(user_id=user.id, group_id=group.id))
        await db.commit()

    token = await login(client, "readonly-with-group-members@example.com")
    response = await client.post(
        "/api/v1/members", json={"first_name": "Erika", "last_name": "Musterfrau"},
        headers=auth_header(token),
    )
    assert response.status_code == 201, response.text


async def test_member_create_and_retrieve(client, admin_user):
    token = await login(client, "admin@example.com")

    response = await client.post(
        "/api/v1/members",
        json={"first_name": "Erika", "last_name": "Musterfrau"},
        headers=auth_header(token),
    )
    assert response.status_code == 201
    mitglied = response.json()
    assert mitglied["first_name"] == "Erika"

    response = await client.get(f"/api/v1/members/{mitglied['id']}", headers=auth_header(token))
    assert response.status_code == 200
    assert response.json()["last_name"] == "Musterfrau"


async def test_members_csv_export_respects_active_search_filter(client, admin_user):
    """Issue #198: the export must match whatever the list page is
    currently filtered to, not always every active member -- e.g.
    searching for one member and exporting must not also include an
    unrelated member who'd appear in the unfiltered list."""
    await web_login(client, "admin@example.com")

    from app.database import AsyncSessionLocal
    from app.models import Member

    async with AsyncSessionLocal() as session:
        session.add(Member(first_name="Erika", last_name="Filterfrau"))
        session.add(Member(first_name="Otto", last_name="Anderer"))
        await session.commit()

    unfiltered = await client.get("/members/export/csv")
    assert "Filterfrau" in unfiltered.text
    assert "Anderer" in unfiltered.text

    filtered = await client.get("/members/export/csv?search=Filterfrau")
    assert filtered.status_code == 200
    assert "Filterfrau" in filtered.text
    assert "Anderer" not in filtered.text


async def test_parcel_create_duplicate_plot_number_rejected(client, admin_user):
    token = await login(client, "admin@example.com")

    response = await client.post(
        "/api/v1/parcels", json={"plot_number": "G001"}, headers=auth_header(token)
    )
    assert response.status_code == 201

    response = await client.post(
        "/api/v1/parcels", json={"plot_number": "g001"}, headers=auth_header(token)
    )
    assert response.status_code == 409  # case is normalized (G001 == g001)


async def test_parcel_update_rejects_duplicate_plot_number_via_api(client, admin_user):
    """ADR 0070: the duplicate-plot-number check used to only run on
    CREATE on the HTML side (its edit form had no check at all) -- now
    shared and enforced on UPDATE too, both surfaces."""
    token = await login(client, "admin@example.com")
    headers = auth_header(token)

    p1 = (await client.post("/api/v1/parcels", json={"plot_number": "G100"}, headers=headers)).json()
    await client.post("/api/v1/parcels", json={"plot_number": "G101"}, headers=headers)

    response = await client.put(
        f"/api/v1/parcels/{p1['id']}", json={"plot_number": "G101"}, headers=headers,
    )
    assert response.status_code == 409


async def test_parcel_update_writes_audit_trail_via_api(client, admin_user):
    """ADR 0070: API-driven parcel edits used to leave no ChangeHistory
    row at all (ChangeTracker was only wired into the HTML router) --
    the most serious finding for this module, same shape as tickets'
    worst finding."""
    from app.database import AsyncSessionLocal
    from app.models import ChangeHistory
    from sqlalchemy import select

    token = await login(client, "admin@example.com")
    headers = auth_header(token)

    p1 = (await client.post("/api/v1/parcels", json={"plot_number": "G110"}, headers=headers)).json()
    response = await client.put(
        f"/api/v1/parcels/{p1['id']}", json={"area_sqm": 321.5}, headers=headers,
    )
    assert response.status_code == 200

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(ChangeHistory).where(
                ChangeHistory.entity_type == "Parcel", ChangeHistory.entity_id == p1["id"],
            )
        )
        entries = result.scalars().all()

    assert any(e.field_name == "area_sqm" for e in entries)
    assert all(e.changed_by_id == admin_user.id for e in entries)


async def test_reassigning_a_former_tenant_to_the_same_parcel_via_api_reactivates(client, admin_user):
    """ADR 0070: the API used to 409 if ANY assignment row already
    existed for a member/parcel pair, even an already-ended one -- a
    former tenant could never be reassigned to the same parcel via the
    API at all, unlike the HTML side, which always reactivated."""
    token = await login(client, "admin@example.com")
    headers = auth_header(token)

    member = (await client.post(
        "/api/v1/members", json={"first_name": "Rosa", "last_name": "Wiederkehr"}, headers=headers,
    )).json()
    parcel = (await client.post("/api/v1/parcels", json={"plot_number": "G120"}, headers=headers)).json()

    first = await client.post(
        f"/api/v1/parcels/{parcel['id']}/assignments",
        json={"member_id": member["id"], "parcel_id": parcel["id"]},
        headers=headers,
    )
    assert first.status_code == 201
    assignment_id = first.json()["id"]

    ended = await client.delete(
        f"/api/v1/parcels/{parcel['id']}/assignments/{assignment_id}", headers=headers,
    )
    assert ended.status_code == 204

    reassigned = await client.post(
        f"/api/v1/parcels/{parcel['id']}/assignments",
        json={"member_id": member["id"], "parcel_id": parcel["id"]},
        headers=headers,
    )
    assert reassigned.status_code == 201, reassigned.text
    assert reassigned.json()["id"] == assignment_id  # reactivated, not a new row


async def test_api_assignment_delete_ends_active_assignment_instead_of_hard_deleting(client, admin_user):
    """ADR 0070: the API's single DELETE endpoint used to hard-delete
    unconditionally, including an ACTIVE assignment -- silently
    discarding tenancy history the HTML side deliberately protects (it
    only ever soft-ends an active assignment; hard-delete is reserved
    for already-ended ones). The API now makes the same distinction."""
    from app.database import AsyncSessionLocal
    from app.models import MemberParcel
    from sqlalchemy import select

    token = await login(client, "admin@example.com")
    headers = auth_header(token)

    member = (await client.post(
        "/api/v1/members", json={"first_name": "Theo", "last_name": "Aktiv"}, headers=headers,
    )).json()
    parcel = (await client.post("/api/v1/parcels", json={"plot_number": "G121"}, headers=headers)).json()

    created = (await client.post(
        f"/api/v1/parcels/{parcel['id']}/assignments",
        json={"member_id": member["id"], "parcel_id": parcel["id"]},
        headers=headers,
    )).json()

    response = await client.delete(
        f"/api/v1/parcels/{parcel['id']}/assignments/{created['id']}", headers=headers,
    )
    assert response.status_code == 204

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(MemberParcel).where(MemberParcel.id == created["id"]))
        assignment = result.scalar_one_or_none()

    assert assignment is not None  # still exists -- soft-ended, not hard-deleted
    assert assignment.assigned_until is not None


async def test_member_parcel_assignment_and_double_garden(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)

    m1 = (await client.post("/api/v1/members", json={"first_name": "Anna", "last_name": "Eins"}, headers=headers)).json()
    m2 = (await client.post("/api/v1/members", json={"first_name": "Bruno", "last_name": "Zwei"}, headers=headers)).json()
    p1 = (await client.post("/api/v1/parcels", json={"plot_number": "G010"}, headers=headers)).json()
    p2 = (await client.post("/api/v1/parcels", json={"plot_number": "G011"}, headers=headers)).json()

    # Doppelgarten: ein Member bekommt zwei Parzellen
    r1 = await client.post(
        f"/api/v1/parcels/{p1['id']}/assignments",
        json={"member_id": m1["id"], "parcel_id": p1["id"]},
        headers=headers,
    )
    assert r1.status_code == 201

    r2 = await client.post(
        f"/api/v1/parcels/{p2['id']}/assignments",
        json={"member_id": m1["id"], "parcel_id": p2["id"]},
        headers=headers,
    )
    assert r2.status_code == 201

    # Gemeinschaftsgarten: zweites Member auf derselben Parcel
    r3 = await client.post(
        f"/api/v1/parcels/{p1['id']}/assignments",
        json={"member_id": m2["id"], "parcel_id": p1["id"]},
        headers=headers,
    )
    assert r3.status_code == 201

    detail = (await client.get(f"/api/v1/parcels/{p1['id']}", headers=headers)).json()
    assert len(detail["members"]) == 2


# ---------------------------------------------------------------------------
# GPS coordinates (latitude/longitude)
# ---------------------------------------------------------------------------

async def web_login(client, email: str, password: str = "testpasswort123") -> None:
    response = await client.post("/auth/login", data={"email": email, "password": password})
    assert response.status_code in (302, 303)


async def test_parcel_create_and_update_with_coordinates_round_trip(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)

    response = await client.post(
        "/api/v1/parcels",
        json={"plot_number": "G200", "latitude": 51.339695, "longitude": 12.373075},
        headers=headers,
    )
    assert response.status_code == 201, response.text
    parcel = response.json()
    assert float(parcel["latitude"]) == 51.339695
    assert float(parcel["longitude"]) == 12.373075

    response = await client.put(
        f"/api/v1/parcels/{parcel['id']}",
        json={"latitude": 51.34, "longitude": 12.38},
        headers=headers,
    )
    assert response.status_code == 200, response.text
    updated = response.json()
    assert float(updated["latitude"]) == 51.34
    assert float(updated["longitude"]) == 12.38


async def test_parcel_invalid_coordinates_rejected_via_api(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)

    response = await client.post(
        "/api/v1/parcels",
        json={"plot_number": "G201", "latitude": 200, "longitude": 12.0},
        headers=headers,
    )
    # Same blanket 409 convention this router already uses for every
    # ServiceError, independent of ServiceError.http_status (see
    # _service_error_to_http in app/routers/api_parcels.py).
    assert response.status_code == 409, response.text

    response = await client.post(
        "/api/v1/parcels",
        json={"plot_number": "G202", "latitude": 51.0, "longitude": -200},
        headers=headers,
    )
    assert response.status_code == 409, response.text


async def test_parcel_csv_export_import_round_trips_coordinates(client, admin_user):
    await web_login(client, "admin@example.com")

    create = await client.post(
        "/parcels/new",
        data={"plot_number": "G203", "area_sqm": "312,5", "latitude": "51,339695", "longitude": "12,373075", "notes": ""},
        follow_redirects=False,
    )
    assert create.status_code in (302, 303)

    export = await client.get("/parcels/export/csv")
    assert export.status_code == 200
    assert "Breitengrad" in export.text
    assert "Längengrad" in export.text
    assert "G203" in export.text

    import_response = await client.post(
        "/parcels/import/csv",
        files={"file": ("parcels.csv", export.text.encode("utf-8"), "text/csv")},
        follow_redirects=False,
    )
    assert import_response.status_code in (302, 303)

    from app.database import AsyncSessionLocal
    from sqlalchemy import select
    from app.models import Parcel

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Parcel).where(Parcel.plot_number == "G203"))
        parcels = result.scalars().all()
        # Re-importing the just-exported CSV skips existing plot numbers
        # (see parcels_import_csv), so still exactly one G203 -- but that
        # confirms the round-trip parsed the new columns without error.
        assert len(parcels) == 1
        assert float(parcels[0].latitude) == 51.339695
        assert float(parcels[0].longitude) == 12.373075
