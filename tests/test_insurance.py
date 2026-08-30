"""Tests for the insurance module."""
import re

from tests.conftest import login, auth_header


async def web_login(client, email: str, password: str = "testpasswort123") -> None:
    response = await client.post("/auth/login", data={"email": email, "password": password})
    assert response.status_code in (302, 303)


async def test_new_parcel_insurance_seeds_household_members_by_default(client, admin_user):
    """Issue #204: a freshly created ParcelInsurance (first visit to a
    parcel's insurance detail page for a year) must default to the
    whole currently-detected household checked/covered -- otherwise
    saving without touching anything would silently drop the household
    base fee for every parcel that never had this page opened before."""
    from app.database import AsyncSessionLocal
    from app.models import Member, MemberParcel, Parcel

    async with AsyncSessionLocal() as session:
        parcel = Parcel(plot_number="204-2")
        tenant = Member(
            first_name="Tenant", last_name="204b", street="Only St 1", postal_code="11111", city="Testort",
        )
        session.add_all([parcel, tenant])
        await session.flush()
        session.add(MemberParcel(member_id=tenant.id, parcel_id=parcel.id, is_invoice_address=True))
        await session.commit()
        parcel_id, tenant_id = parcel.id, tenant.id

    await web_login(client, "admin@example.com")

    response = await client.get(f"/insurance/parcels/{parcel_id}?year=2026")
    assert response.status_code == 200
    body = response.text

    checkbox_start = body.index(f'id="hm-{tenant_id}"')
    checkbox_end = body.index(">", checkbox_start)
    assert "checked" in body[checkbox_start:checkbox_end]


async def test_leaser_can_opt_out_while_additional_person_stays_insured(client, admin_user):
    """Issue #204: the leaser's own household checkbox can be
    individually unchecked while a named additional person (e.g. an
    outside relative) stays insured -- previously impossible since the
    household's flat fee was all-or-nothing (first as an implicit part
    of has_accident_insurance, then briefly as an atomic covers_household
    toggle that was itself the wrong shape)."""
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
        # household_members deliberately omitted -- the leaser is the
        # only household member here, so leaving it out means he's
        # unchecked/opted out, same as an unchecked checkbox not
        # submitting at all.
        "additional_persons": [mate_id],
    })
    assert response.status_code in (302, 303)

    response = await client.get(f"/insurance/parcels/{parcel_id}?year=2026")
    assert response.status_code == 200
    body = response.text

    checkbox_start = body.index(f'id="hm-{leaser.id}"')
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
    tenant = (await client.post(
        "/api/v1/members", json={"first_name": "Haupt", "last_name": "Paechter"}, headers=headers
    )).json()

    status_response = await client.put(
        f"/api/v1/insurance/parcels/{parcel['id']}/2026",
        json={
            "has_property_insurance": True, "property_package_id": package["id"],
            "has_accident_insurance": True, "household_member_ids": [tenant["id"]],
            "additional_person_member_ids": [],
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
    tenant = (await client.post(
        "/api/v1/members", json={"first_name": "Haupt", "last_name": "Paechter"}, headers=headers
    )).json()
    additional_person = (await client.post(
        "/api/v1/members", json={"first_name": "Weiterer", "last_name": "Paechter"}, headers=headers
    )).json()

    daten = (await client.put(
        f"/api/v1/insurance/parcels/{parcel['id']}/2026",
        json={
            "has_property_insurance": False, "has_accident_insurance": True,
            "household_member_ids": [tenant["id"]],
            "additional_person_member_ids": [additional_person["id"]],
        },
        headers=headers,
    )).json()

    assert float(daten["accident_cost_eur"]) == 6.0  # 3 Grund + 3 Zusatzperson


async def test_terminated_parcel_with_active_insurance_still_shown_in_list(client, admin_user):
    """Issue #207: a lease termination doesn't automatically cancel the
    actual (external) insurance contract, so a TERMINATED parcel that
    still has an active insurance entry for the year must keep showing
    up in /insurance/parcels as a reminder to cancel it by hand."""
    from app.database import AsyncSessionLocal
    from app.models import Parcel, ParcelStatus, PropertyInsurancePackage, ParcelInsurance

    async with AsyncSessionLocal() as session:
        package = PropertyInsurancePackage(year=2026, name="Paket 207", amount_eur=40)
        insured_parcel = Parcel(plot_number="207-insured", status=ParcelStatus.TERMINATED)
        session.add_all([package, insured_parcel])
        await session.flush()
        session.add(ParcelInsurance(
            parcel_id=insured_parcel.id, year=2026,
            has_property_insurance=True, property_package_id=package.id,
        ))
        await session.commit()

    await web_login(client, "admin@example.com")

    response = await client.get("/insurance/parcels?year=2026")
    assert response.status_code == 200
    assert "207-insured" in response.text


async def test_terminated_parcel_with_no_insurance_row_still_shown_for_review(client, admin_user):
    """Follow-up correction to issue #207 (2026-08-30): a parcel that was
    terminated before anyone entered this year's insurance data has *no*
    ParcelInsurance row at all yet -- the original fix gated visibility
    on an existing True-flagged row, which hid exactly the parcels that
    most need reviewing (confirmed against real prod data: terminated
    parcels with zero insurance history were invisible in the list).
    A TERMINATED parcel with no row for the year must stay visible by
    default, same as an ACTIVE parcel with no insurance yet."""
    from app.database import AsyncSessionLocal
    from app.models import Parcel, ParcelStatus

    async with AsyncSessionLocal() as session:
        bare_parcel = Parcel(plot_number="207-bare", status=ParcelStatus.TERMINATED)
        session.add(bare_parcel)
        await session.commit()

    await web_login(client, "admin@example.com")

    response = await client.get("/insurance/parcels?year=2026")
    assert response.status_code == 200
    assert "207-bare" in response.text


async def test_terminated_parcel_with_confirmed_no_insurance_excluded(client, admin_user):
    """Follow-up correction to issue #207 (2026-08-30): once someone has
    actually reviewed a terminated parcel and recorded that there's no
    insurance left to track (both flags explicitly False for the year),
    it should drop off the list -- that's the one case that should stay
    excluded, not "no row exists yet"."""
    from app.database import AsyncSessionLocal
    from app.models import Parcel, ParcelStatus, ParcelInsurance

    async with AsyncSessionLocal() as session:
        cancelled_parcel = Parcel(plot_number="207-cancelled", status=ParcelStatus.TERMINATED)
        session.add(cancelled_parcel)
        await session.flush()
        session.add(ParcelInsurance(
            parcel_id=cancelled_parcel.id, year=2026,
            has_property_insurance=False, has_accident_insurance=False,
        ))
        await session.commit()

    await web_login(client, "admin@example.com")

    response = await client.get("/insurance/parcels?year=2026")
    assert response.status_code == 200
    assert "207-cancelled" not in response.text


async def test_accident_overview_stat_excludes_non_leaser_only_coverage(client, admin_user):
    """Issue #208: has_accident_insurance can be true purely because a
    non-leaser 'additional person' opted in while the actual leaser
    (household member) opted out -- calculate_insurance_cost() already
    charges no base fee for that case, so the /insurance/ 'insured
    parcels' stat must not count it as an insured parcel either."""
    from app.database import AsyncSessionLocal
    from app.models import (
        Member, MemberParcel, Parcel, InsuranceConfiguration, ParcelInsurance,
        AccidentInsuranceAdditionalPerson,
    )

    async with AsyncSessionLocal() as session:
        session.add(InsuranceConfiguration(
            year=2026, accident_base_amount_eur=20, accident_additional_amount_eur=10,
        ))
        parcel = Parcel(plot_number="208-1")
        leaser = Member(first_name="Leaser", last_name="208", street="Main St 1", postal_code="12345", city="Testort")
        relative = Member(first_name="Relative", last_name="208", street="Elsewhere 1", postal_code="54321", city="Otherville")
        session.add_all([parcel, leaser, relative])
        await session.flush()
        session.add(MemberParcel(member_id=leaser.id, parcel_id=parcel.id, is_invoice_address=True))
        await session.flush()
        pi = ParcelInsurance(parcel_id=parcel.id, year=2026, has_accident_insurance=True)
        session.add(pi)
        await session.flush()
        # Leaser (household) deliberately left unchecked -- only the
        # non-leaser additional person is covered.
        session.add(AccidentInsuranceAdditionalPerson(parcel_insurance_id=pi.id, member_id=relative.id))
        await session.commit()

    await web_login(client, "admin@example.com")

    response = await client.get("/insurance/?year=2026")
    assert response.status_code == 200
    body = response.text

    label = "Accident insurance"
    label_index = body.index(label)
    window = body[label_index:label_index + 400]
    match = re.search(r">(\d+)<", window)
    assert match is not None
    assert match.group(1) == "0"


async def test_insurance_parcels_list_filters_and_sums(client, admin_user):
    """Issue #209: /insurance/parcels can be filtered by property
    package/accident status and shows a footer row summing the
    displayed rows' costs."""
    from app.database import AsyncSessionLocal
    from app.models import Parcel, PropertyInsurancePackage, InsuranceConfiguration, ParcelInsurance

    async with AsyncSessionLocal() as session:
        package = PropertyInsurancePackage(year=2026, name="Paket 209", amount_eur=50)
        session.add(package)
        session.add(InsuranceConfiguration(year=2026, accident_base_amount_eur=0, accident_additional_amount_eur=0))
        insured_parcel = Parcel(plot_number="209-insured")
        bare_parcel = Parcel(plot_number="209-bare")
        session.add_all([insured_parcel, bare_parcel])
        await session.flush()
        session.add(ParcelInsurance(
            parcel_id=insured_parcel.id, year=2026,
            has_property_insurance=True, property_package_id=package.id,
        ))
        await session.commit()
        package_id = package.id

    await web_login(client, "admin@example.com")

    response = await client.get(f"/insurance/parcels?year=2026&property_filter={package_id}")
    assert response.status_code == 200
    body = response.text
    assert "209-insured" in body
    assert "209-bare" not in body
    assert "50,00" in body or "50.00" in body  # footer sum

    response = await client.get("/insurance/parcels?year=2026&property_filter=none")
    assert response.status_code == 200
    body = response.text
    assert "209-bare" in body
    assert "209-insured" not in body


async def test_insurance_parcels_list_links_to_parcel_detail_page(client, admin_user):
    """Issue #210: "In the list view /insurance/parcels/, link directly
    to their detail page /insurance/parcels/{UUID}" -- the plot number
    links straight to that parcel's insurance detail page. Corrected
    2026-08-30: the first cut of this fix linked the plot number to the
    general parcel record (/parcels/{id}) instead, which kermie flagged
    as not what the issue asked for."""
    from app.database import AsyncSessionLocal
    from app.models import Parcel

    async with AsyncSessionLocal() as session:
        parcel = Parcel(plot_number="210-1")
        session.add(parcel)
        await session.commit()
        parcel_id = parcel.id

    await web_login(client, "admin@example.com")

    response = await client.get("/insurance/parcels?year=2026")
    assert response.status_code == 200
    assert f'href="/insurance/parcels/{parcel_id}?year=2026"' in response.text
