"""
Issue #172: a tenant who gave notice for a FUTURE date (assigned_until
in the future, not yet moved out -- MemberParcel.is_current/ADR 0052
already treats this as still current everywhere else) was silently
un-billed the moment that date was recorded, because is_invoice_address
was being cleared for ANY assigned_until, not just an already-ended
one. Confirmed live in production: two occupied, still-current tenants
(TERMINATED-status parcels with a future move-out date) stopped
appearing in invoice runs and stopped being findable as an email
recipient for their invoices.

Fixed across every write path (app/routers/parcels.py's
member_assignment_update, app/routers/api_parcels.py's assignment
create) and every read path (app/invoice_generation.py's
_parcel_is_billable / invoice_address_members,
app/invoice_delivery.py's recipient lookup) to use
MemberParcel.is_current / current_tenant_filter() instead of
"assigned_until is None". The DB-level CHECK constraint that used to
block this (ck_invoice_address_only_for_current_tenants) was dropped
in migration 0069 -- see ADR 0058.
"""
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import AsyncSessionLocal
from app.invoice_generation import _parcel_is_billable
from app.invoice_delivery import copy_email_recipients
from app.invoice_pdf import invoice_copies
from app.models import (
    Member, MemberEmail, MemberParcel, Parcel, ParcelStatus, Invoice, ClubSetting,
)


async def _enable_finances_module():
    async with AsyncSessionLocal() as session:
        session.add(ClubSetting(key="modul_finances", value="true", description="test"))
        await session.commit()


async def _make_run(client, year="2026"):
    r_create = await client.post("/finances/runs", data={
        "year": year, "subject": "Future termination test", "issued_date": f"{year}-08-01",
        "due_date": f"{year}-09-01", "footer_text": "",
    })
    assert r_create.status_code in (302, 303)
    return r_create.headers["location"].rstrip("/").split("/")[-1]


async def test_editing_assignment_with_future_assigned_until_keeps_invoice_address(client, admin_user):
    """The actual reported bug: saving a future termination date via
    the assignment edit form must not clear is_invoice_address."""
    await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})

    async with AsyncSessionLocal() as session:
        parcel = Parcel(plot_number="FUTURE-TERM-1", status=ParcelStatus.TERMINATED)
        tenant = Member(first_name="Notice", last_name="Given", street="Gartenweg 1", postal_code="12345", city="Testort")
        session.add_all([parcel, tenant])
        await session.flush()
        assignment = MemberParcel(member_id=tenant.id, parcel_id=parcel.id, is_invoice_address=True)
        session.add(assignment)
        await session.commit()
        parcel_id, assignment_id = parcel.id, assignment.id

    future_date = (date.today() + timedelta(days=90)).isoformat()
    response = await client.post(
        f"/parcels/{parcel_id}/member/{assignment_id}/edit",
        data={"is_invoice_address": "true", "assigned_from": "", "assigned_until": future_date},
    )
    assert response.status_code in (302, 303)

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(MemberParcel).where(MemberParcel.id == assignment_id))
        updated = result.scalar_one()

    assert updated.is_current is True
    assert updated.is_invoice_address is True, "a future-dated termination must not clear invoice-address status"


async def test_editing_assignment_with_past_assigned_until_clears_invoice_address(client, admin_user):
    """Unchanged, correct behavior: an ALREADY-ended tenancy still
    clears is_invoice_address -- only the future-dated case changed."""
    await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})

    async with AsyncSessionLocal() as session:
        parcel = Parcel(plot_number="PAST-TERM-1")
        tenant = Member(first_name="Already", last_name="Left", street="Gartenweg 1", postal_code="12345", city="Testort")
        session.add_all([parcel, tenant])
        await session.flush()
        assignment = MemberParcel(member_id=tenant.id, parcel_id=parcel.id, is_invoice_address=True)
        session.add(assignment)
        await session.commit()
        parcel_id, assignment_id = parcel.id, assignment.id

    past_date = (date.today() - timedelta(days=10)).isoformat()
    response = await client.post(
        f"/parcels/{parcel_id}/member/{assignment_id}/edit",
        data={"is_invoice_address": "true", "assigned_from": "", "assigned_until": past_date},
    )
    assert response.status_code in (302, 303)

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(MemberParcel).where(MemberParcel.id == assignment_id))
        updated = result.scalar_one()

    assert updated.is_current is False
    assert updated.is_invoice_address is False, "an already-ended tenancy must still clear invoice-address status"


async def test_parcel_is_billable_with_future_terminated_resident():
    async with AsyncSessionLocal() as session:
        parcel = Parcel(plot_number="FUTURE-TERM-BILL", status=ParcelStatus.TERMINATED)
        tenant = Member(first_name="Notice", last_name="Given2")
        session.add_all([parcel, tenant])
        await session.flush()
        session.add(MemberParcel(
            member_id=tenant.id, parcel_id=parcel.id, is_invoice_address=True,
            assigned_until=date.today() + timedelta(days=90),
        ))
        await session.commit()

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Parcel).options(selectinload(Parcel.member_assignments)).where(Parcel.id == parcel.id)
        )
        loaded = result.scalar_one()

    assert _parcel_is_billable(loaded) is True


async def test_invoice_generation_bills_future_terminated_occupied_parcel(client, admin_user):
    await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})
    await _enable_finances_module()

    async with AsyncSessionLocal() as session:
        parcel = Parcel(plot_number="FUTURE-TERM-RUN", area_sqm=200, status=ParcelStatus.TERMINATED)
        tenant = Member(first_name="Notice", last_name="Given3", street="Gartenweg 1", postal_code="12345", city="Testort")
        session.add_all([parcel, tenant])
        await session.flush()
        session.add(MemberParcel(
            member_id=tenant.id, parcel_id=parcel.id, is_invoice_address=True,
            assigned_until=date.today() + timedelta(days=90),
        ))
        await session.commit()
        parcel_id = parcel.id

    run_id = await _make_run(client)
    r_item = await client.post(f"/finances/runs/{run_id}/items", data={
        "order_number": "10", "name": "Membership fee", "description": "",
        "pricing_mode": "fixed_per_parcel", "unit_price": "50.00", "applies_to_all_parcels": "on",
    })
    assert r_item.status_code in (302, 303)

    r_finalize = await client.post(f"/finances/runs/{run_id}/finalize")
    assert r_finalize.status_code in (302, 303), r_finalize.headers.get("location")

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Invoice).where(Invoice.invoice_run_id == run_id))
        invoices = result.scalars().all()

    assert len(invoices) == 1
    assert invoices[0].parcel_id == parcel_id


async def test_invoice_email_recipient_found_for_future_terminated_resident(client, admin_user):
    """app/invoice_delivery.py's recipient lookup must also find them --
    a fixed billing computation with no findable email recipient would
    still silently fail to deliver."""
    await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})
    await _enable_finances_module()

    async with AsyncSessionLocal() as session:
        parcel = Parcel(plot_number="FUTURE-TERM-EMAIL", area_sqm=200, status=ParcelStatus.TERMINATED)
        tenant = Member(
            first_name="Notice", last_name="Given4", email_notifications=True,
            street="Gartenweg 1", postal_code="12345", city="Testort",
        )
        session.add_all([parcel, tenant])
        await session.flush()
        session.add(MemberEmail(member_id=tenant.id, address="notice@example.com", is_primary=True))
        session.add(MemberParcel(
            member_id=tenant.id, parcel_id=parcel.id, is_invoice_address=True,
            assigned_until=date.today() + timedelta(days=90),
        ))
        await session.commit()

    run_id = await _make_run(client)
    r_item = await client.post(f"/finances/runs/{run_id}/items", data={
        "order_number": "10", "name": "Membership fee", "description": "",
        "pricing_mode": "fixed_per_parcel", "unit_price": "50.00", "applies_to_all_parcels": "on",
    })
    assert r_item.status_code in (302, 303)

    r_finalize = await client.post(f"/finances/runs/{run_id}/finalize")
    assert r_finalize.status_code in (302, 303), r_finalize.headers.get("location")

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Invoice).where(Invoice.invoice_run_id == run_id))
        invoice = result.scalar_one()
        recipients = await copy_email_recipients(session, invoice, invoice_copies(invoice)[0])

    assert recipients
    member, email = recipients[0]
    assert email == "notice@example.com"


async def test_rest_api_assignment_create_with_future_assigned_until_keeps_invoice_address(client, admin_user):
    token_resp = await client.post("/api/v1/auth/login", json={"email": "admin@example.com", "password": "testpasswort123"})
    assert token_resp.status_code == 200
    headers = {"Authorization": f"Bearer {token_resp.json()['access_token']}"}

    async with AsyncSessionLocal() as session:
        parcel = Parcel(plot_number="API-FUTURE-TERM")
        member = Member(first_name="Api", last_name="Notice")
        session.add_all([parcel, member])
        await session.commit()
        parcel_id, member_id = parcel.id, member.id

    future_date = (date.today() + timedelta(days=90)).isoformat()
    resp = await client.post(
        f"/api/v1/parcels/{parcel_id}/assignments",
        json={
            "member_id": member_id, "parcel_id": parcel_id,
            "is_invoice_address": True, "assigned_until": future_date,
        },
        headers=headers,
    )
    assert resp.status_code in (200, 201), resp.text
    assert resp.json()["is_invoice_address"] is True
