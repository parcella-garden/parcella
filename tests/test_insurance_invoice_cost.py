"""
Issues #87/#89/#93: the "insurance cost" invoice pricing mode bills
whichever parcels have a nonzero cost per
app/insurance_utils.py's calculate_insurance_cost()/insurance_cost_line_items()
-- property + accident, including the "+1" per-additional-person
accident surcharge -- with no manual parcel scoping, exactly mirroring
how WORK_HOURS_SHORTFALL (issue #83) is fully automatic. A
parcel_scopes/applies_to_all_parcels selection is still stored on the
item (the form doesn't special-case what it submits) but must be
ignored for eligibility: an insured parcel left OUT of the scope must
still be billed, and an uninsured parcel must never be billed
regardless of being IN scope.

Issue #93 additionally splits the cost into one labeled line item per
component (property / accident household / accident +N additional)
instead of one combined lump sum, so the invoice recipient sees the
insurance type and fee for each part.
"""
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import AsyncSessionLocal
from app.models import (
    Member, MemberParcel, Parcel, Invoice, ClubSetting,
    PropertyInsurancePackage, InsuranceConfiguration, ParcelInsurance,
    AccidentInsuranceAdditionalPerson,
)


async def _enable_modules():
    async with AsyncSessionLocal() as session:
        session.add(ClubSetting(key="modul_finances", value="true", description="test"))
        session.add(ClubSetting(key="modul_insurance", value="true", description="test"))
        await session.commit()


async def _make_run(client, year="2026"):
    r_create = await client.post("/finances/runs", data={
        "year": year, "subject": "Insurance cost test", "issued_date": f"{year}-08-01",
        "due_date": f"{year}-09-01", "footer_text": "",
    })
    assert r_create.status_code in (302, 303)
    return r_create.headers["location"].rstrip("/").split("/")[-1]


async def _occupied_parcel(session, plot_number: str) -> tuple:
    parcel = Parcel(plot_number=plot_number, area_sqm=200)
    tenant = Member(
        first_name="Tenant", last_name=plot_number,
        street=f"{plot_number} Street", postal_code="12345", city="Testort",
    )
    extra = Member(
        first_name="Extra", last_name=plot_number,
        street="Elsewhere 1", postal_code="54321", city="Otherville",
    )
    session.add_all([parcel, tenant, extra])
    await session.flush()
    session.add(MemberParcel(member_id=tenant.id, parcel_id=parcel.id, is_invoice_address=True))
    return parcel, tenant, extra


async def test_insurance_cost_ignores_parcel_scope_and_skips_uninsured_parcels(client, admin_user):
    await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})
    await _enable_modules()

    year = 2026
    async with AsyncSessionLocal() as session:
        package = PropertyInsurancePackage(year=year, name="Package 1", amount_eur=60)
        config = InsuranceConfiguration(year=year, accident_base_amount_eur=20, accident_additional_amount_eur=10)
        session.add_all([package, config])
        await session.flush()

        insured_parcel, insured_tenant, additional_person = await _occupied_parcel(session, "INSCOST-INSURED")
        uninsured_parcel, _, _ = await _occupied_parcel(session, "INSCOST-BARE")
        await session.flush()

        pi = ParcelInsurance(
            parcel_id=insured_parcel.id, year=year,
            has_property_insurance=True, property_package_id=package.id,
            has_accident_insurance=True,
        )
        session.add(pi)
        await session.flush()
        session.add(AccidentInsuranceAdditionalPerson(parcel_insurance_id=pi.id, member_id=additional_person.id))
        await session.commit()

        insured_id, bare_id = insured_parcel.id, uninsured_parcel.id

    run_id = await _make_run(client, str(year))
    # Deliberately scope the item to ONLY the uninsured parcel -- if
    # scoping were honored, the insured parcel would never be billed;
    # if it's correctly ignored, the insured parcel is billed anyway
    # and the (scoped-in) uninsured parcel still isn't, since it has
    # no insurance cost to charge.
    r_item = await client.post(f"/finances/runs/{run_id}/items", data={
        "order_number": "10", "name": "Insurance cost", "description": "",
        "pricing_mode": "insurance_cost", "parcel_ids": [bare_id],
    })
    assert r_item.status_code in (302, 303)

    r_finalize = await client.post(f"/finances/runs/{run_id}/finalize")
    assert r_finalize.status_code in (302, 303), r_finalize.headers.get("location")

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Invoice)
            .options(selectinload(Invoice.parcel), selectinload(Invoice.line_items))
            .where(Invoice.invoice_run_id == run_id)
        )
        invoices = list(result.scalars().unique().all())

    billed_plot_numbers = {inv.parcel.plot_number for inv in invoices}
    assert billed_plot_numbers == {"INSCOST-INSURED"}, (
        "the insured parcel must be billed even though it was left OUT of parcel_scopes, "
        "and the uninsured parcel must not be billed even though it was left IN parcel_scopes"
    )
    # property (60) + accident base (20) + one additional person (10) = 90,
    # split across 3 separate line items (issue #93), not one lump sum.
    assert float(invoices[0].subtotal) == 90.0
    totals_by_name = {li.name: float(li.line_total) for li in invoices[0].line_items}
    assert totals_by_name == {
        "Property insurance (Package 1)": 60.0,
        "Accident insurance (household)": 20.0,
        "Accident insurance (+1 additional person(s))": 10.0,
    }


async def test_insurance_cost_household_declined_bills_only_additional_person(client, admin_user):
    """Issue #204: the household can decline accident-insurance coverage
    for themselves (covers_household=False) while a named additional
    person stays insured -- only the additional-person line should be
    billed, the household base fee must be entirely absent."""
    await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})
    await _enable_modules()

    year = 2026
    async with AsyncSessionLocal() as session:
        config = InsuranceConfiguration(year=year, accident_base_amount_eur=20, accident_additional_amount_eur=10)
        session.add(config)
        await session.flush()

        parcel, tenant, additional_person = await _occupied_parcel(session, "INSCOST-HHDECLINED")
        await session.flush()

        pi = ParcelInsurance(
            parcel_id=parcel.id, year=year,
            has_accident_insurance=True, covers_household=False,
        )
        session.add(pi)
        await session.flush()
        session.add(AccidentInsuranceAdditionalPerson(parcel_insurance_id=pi.id, member_id=additional_person.id))
        await session.commit()

    run_id = await _make_run(client, str(year))
    r_item = await client.post(f"/finances/runs/{run_id}/items", data={
        "order_number": "10", "name": "Insurance cost", "description": "",
        "pricing_mode": "insurance_cost",
    })
    assert r_item.status_code in (302, 303)

    r_finalize = await client.post(f"/finances/runs/{run_id}/finalize")
    assert r_finalize.status_code in (302, 303), r_finalize.headers.get("location")

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Invoice)
            .options(selectinload(Invoice.line_items))
            .where(Invoice.invoice_run_id == run_id)
        )
        invoice = result.scalars().unique().one()

    assert len(invoice.line_items) == 1, "household declined -> only the additional-person line, no household line"
    line = invoice.line_items[0]
    assert line.name == "Accident insurance (+1 additional person(s))"
    assert float(line.line_total) == 10.0
    assert float(invoice.subtotal) == 10.0


async def test_insurance_cost_splits_into_labeled_line_items_per_component(client, admin_user):
    """Issue #93: the invoice recipient sees the insurance type and fee
    for each component (property, accident household, accident +N
    additional persons) as its own line, not one opaque combined total.
    Also covers a parcel with only accident insurance and NO additional
    persons -- exactly two lines (property must be entirely absent, and
    the "+N additional" line must not appear when there are none)."""
    await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})
    await _enable_modules()

    year = 2026
    async with AsyncSessionLocal() as session:
        config = InsuranceConfiguration(year=year, accident_base_amount_eur=25, accident_additional_amount_eur=5)
        session.add(config)
        await session.flush()

        parcel, tenant, _ = await _occupied_parcel(session, "INSCOST-ACCIDENTONLY")
        await session.flush()

        pi = ParcelInsurance(
            parcel_id=parcel.id, year=year,
            has_property_insurance=False, has_accident_insurance=True,
        )
        session.add(pi)
        await session.commit()

    run_id = await _make_run(client, str(year))
    r_item = await client.post(f"/finances/runs/{run_id}/items", data={
        "order_number": "10", "name": "Insurance cost", "description": "",
        "pricing_mode": "insurance_cost",
    })
    assert r_item.status_code in (302, 303)

    r_finalize = await client.post(f"/finances/runs/{run_id}/finalize")
    assert r_finalize.status_code in (302, 303), r_finalize.headers.get("location")

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Invoice)
            .options(selectinload(Invoice.line_items))
            .where(Invoice.invoice_run_id == run_id)
        )
        invoice = result.scalars().unique().one()

    assert len(invoice.line_items) == 1, "no property insurance and no additional persons -> exactly one line item"
    line = invoice.line_items[0]
    assert line.name == "Accident insurance (household)"
    assert float(line.line_total) == 25.0
    assert float(invoice.subtotal) == 25.0
