"""Tests for the insurance module."""
from tests.conftest import login, auth_header


async def web_login(client, email: str, password: str = "testpasswort123") -> None:
    response = await client.post("/auth/login", data={"email": email, "password": password})
    assert response.status_code in (302, 303)


async def test_covers_household_toggle_round_trips_and_leaves_additional_person_billable(client, admin_user):
    """Issue #204: a household can decline accident-insurance coverage
    for themselves while a named additional person (e.g. an outside
    relative) stays insured -- previously impossible since the
    household's flat fee and the additional-person slot were both
    gated behind the single has_accident_insurance switch."""
    from app.database import AsyncSessionLocal
    from app.models import Member, MemberParcel, Parcel, InsuranceConfiguration

    async with AsyncSessionLocal() as session:
        session.add(InsuranceConfiguration(
            year=2026, accident_base_amount_eur=20, accident_additional_amount_eur=10,
        ))
        parcel = Parcel(plot_number="204-1")
        leaser = Member(
            first_name="Leaser", last_name="204", street="Main St 1", postal_code="12345", city="Testort",
        )
        mate = Member(
            first_name="Mate", last_name="204", street="Elsewhere 1", postal_code="54321", city="Otherville",
        )
        session.add_all([parcel, leaser, mate])
        await session.flush()
        session.add(MemberParcel(member_id=leaser.id, parcel_id=parcel.id, is_invoice_address=True))
        session.add(MemberParcel(member_id=mate.id, parcel_id=parcel.id, is_invoice_address=False))
        await session.commit()
        parcel_id, mate_id = parcel.id, mate.id

    await web_login(client, "admin@example.com")

    response = await client.post(f"/insurance/parcels/{parcel_id}/save", data={
        "year": "2026",
        "has_accident_insurance": "true",
        # covers_household deliberately omitted -- unchecked checkboxes
        # don't submit at all, same as the household opting out.
        "additional_persons": [mate_id],
    })
    assert response.status_code in (302, 303)

    response = await client.get(f"/insurance/parcels/{parcel_id}?year=2026")
    assert response.status_code == 200
    body = response.text

    checkbox_start = body.index('id="covers-household"')
    checkbox_end = body.index(">", checkbox_start)
    assert "checked" not in body[checkbox_start:checkbox_end]

    # accident_cost = additional (10) only, household base (20) excluded.
    assert "10,00" in body or "10.00" in body



async def test_insurance_detail_page_shows_previous_and_next_navigation(client, admin_user):
    """Issue #203: Previous/Next buttons on /insurance/parcels/{UUID},
    analogous to the ones on /parcels/{id} (issue #202)."""
    from app.database import AsyncSessionLocal
    from app.models import Parcel, ParcelStatus

    async with AsyncSessionLocal() as session:
        parcels = [
            Parcel(plot_number=f"203-{i}", status=ParcelStatus.ACTIVE)
            for i in range(1, 4)
        ]
        session.add_all(parcels)
        await session.commit()
        for p in parcels:
            await session.refresh(p)
        first_id, middle_id, last_id = [p.id for p in parcels]

    await web_login(client, "admin@example.com")

    response = await client.get(f"/insurance/parcels/{middle_id}?year=2026")
    assert response.status_code == 200
    body = response.text
    assert f"/insurance/parcels/{first_id}?year=2026" in body
    assert f"/insurance/parcels/{last_id}?year=2026" in body

    response = await client.get(f"/insurance/parcels/{first_id}?year=2026")
    assert response.status_code == 200
    body = response.text
    assert f"/insurance/parcels/{middle_id}?year=2026" in body
    assert 'id="nav-prev-link"' in body
    prev_link_start = body.index('id="nav-prev-link"')
    prev_link_end = body.index("</a>", prev_link_start)
    assert 'aria-disabled="true"' in body[prev_link_start:prev_link_end]


async def test_treasurer_without_group_grant_is_blocked_from_insurance_write_via_api(client):
    """ADR 0070: api_insurance.py used require_write_access (role-only)
    -- ANY TREASURER could write insurance data via the API regardless
    of Group configuration. Now the API checks the same Group-derived
    permission as HTML."""
    from app.database import AsyncSessionLocal
    from app.models import User, UserRole
    from app.auth import hash_password

    async with AsyncSessionLocal() as db:
        user = User(
            email="treasurer-no-group-insurance@example.com", name="Treasurer No Group",
            password_hash=hash_password("testpasswort123"), role=UserRole.TREASURER,
        )
        db.add(user)
        await db.commit()

    token = await login(client, "treasurer-no-group-insurance@example.com")
    response = await client.post(
        "/api/v1/insurance/packages",
        json={"year": 2026, "name": "Paket 1", "amount_eur": "40.00"},
        headers=auth_header(token),
    )
    assert response.status_code == 403


async def test_readonly_with_group_grant_can_write_insurance_via_api(client):
    """Flip side: a READONLY user granted insurance:write via a Group
    could already write insurance data through the HTML UI, but the
    role-only API check blocked them regardless of Group membership."""
    from app.database import AsyncSessionLocal
    from app.models import User, UserRole, Group, GroupModulePermission, GroupMembership
    from app.auth import hash_password

    async with AsyncSessionLocal() as db:
        user = User(
            email="readonly-with-group-insurance@example.com", name="Readonly With Group",
            password_hash=hash_password("testpasswort123"), role=UserRole.READONLY,
        )
        db.add(user)
        await db.flush()

        group = Group(name="Insurance Handlers")
        db.add(group)
        await db.flush()
        db.add(GroupModulePermission(group_id=group.id, module="insurance", can_read=True, can_write=True))
        db.add(GroupMembership(user_id=user.id, group_id=group.id))
        await db.commit()

    token = await login(client, "readonly-with-group-insurance@example.com")
    response = await client.post(
        "/api/v1/insurance/packages",
        json={"year": 2026, "name": "Paket 1", "amount_eur": "40.00"},
        headers=auth_header(token),
    )
    assert response.status_code == 201, response.text


async def test_package_create_and_cost_calculation(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)

    package = (await client.post(
        "/api/v1/insurance/packages",
        json={"year": 2026, "name": "Paket 1", "amount_eur": "40.00"},
        headers=headers,
    )).json()

    await client.put(
        "/api/v1/insurance/configuration/2026",
        json={"year": 2026, "accident_base_amount_eur": "3.00", "accident_additional_amount_eur": "3.00"},
        headers=headers,
    )

    parcel = (await client.post(
        "/api/v1/parcels", json={"plot_number": "G300"}, headers=headers
    )).json()

    status_response = await client.put(
        f"/api/v1/insurance/parcels/{parcel['id']}/2026",
        json={
            "has_property_insurance": True, "property_package_id": package["id"],
            "has_accident_insurance": True, "additional_person_member_ids": [],
        },
        headers=headers,
    )
    assert status_response.status_code == 200
    daten = status_response.json()
    assert float(daten["property_cost_eur"]) == 40.0
    assert float(daten["accident_cost_eur"]) == 3.0
    assert float(daten["total_cost_eur"]) == 43.0


async def test_additional_person_increases_accident_cost(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)

    await client.put(
        "/api/v1/insurance/configuration/2026",
        json={"year": 2026, "accident_base_amount_eur": "3.00", "accident_additional_amount_eur": "3.00"},
        headers=headers,
    )

    parcel = (await client.post("/api/v1/parcels", json={"plot_number": "G301"}, headers=headers)).json()
    additional_person = (await client.post(
        "/api/v1/members", json={"first_name": "Weiterer", "last_name": "Paechter"}, headers=headers
    )).json()

    daten = (await client.put(
        f"/api/v1/insurance/parcels/{parcel['id']}/2026",
        json={
            "has_property_insurance": False, "has_accident_insurance": True,
            "additional_person_member_ids": [additional_person["id"]],
        },
        headers=headers,
    )).json()

    assert float(daten["accident_cost_eur"]) == 6.0  # 3 Grund + 3 Zusatzperson
