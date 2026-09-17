"""
Issue: give water_usage/electricity_usage invoice pricing modes full
parity with work_hours_shortfall/insurance_cost (see docs/ADR/0056) --
price pulled from MeteringPriceConfiguration (per medium/year) instead
of a manually-entered unit_price, and billing automatically limited to
parcels with an active meter of that medium regardless of the manual
scope picker. Mirrors tests/test_work_hours_shortfall.py's shape.
"""
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import AsyncSessionLocal
from app.models import (
    Member, MemberParcel, Parcel, Invoice, ClubSetting,
    MeteringPoint, MeteringPointType, MeteringMedium, Meter, MeterReading,
    MeteringPriceConfiguration,
)


async def _enable_finances_module():
    async with AsyncSessionLocal() as session:
        session.add(ClubSetting(key="modul_finances", value="true", description="test"))
        await session.commit()


async def _make_run(client, year):
    r_create = await client.post("/finances/runs", data={
        "year": str(year), "subject": "Metering pricing test", "issued_date": f"{year}-08-01",
        "due_date": f"{year}-09-01", "footer_text": "",
    })
    assert r_create.status_code in (302, 303)
    return r_create.headers["location"].rstrip("/").split("/")[-1]


async def _add_meter_with_reading(
    session, parcel_id: str, medium: MeteringMedium, meter_number: str,
    year: int, initial_reading: float, current_reading: float,
):
    point = MeteringPoint(medium=medium, type=MeteringPointType.PARCEL, parcel_id=parcel_id)
    session.add(point)
    await session.flush()
    meter = Meter(metering_point_id=point.id, number=meter_number, initial_reading=initial_reading)
    session.add(meter)
    await session.flush()
    session.add(MeterReading(meter_id=meter.id, year=year, date=date(year, 10, 1), reading=current_reading))


async def test_water_usage_bills_metered_parcel_and_ignores_manual_scoping(client, admin_user):
    await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})
    await _enable_finances_module()
    year = 2026

    async with AsyncSessionLocal() as session:
        session.add(MeteringPriceConfiguration(medium=MeteringMedium.WATER, year=year, price_per_unit=2.50))

        metered_member = Member(
            first_name="Metered", last_name="Tenant",
            street="Gartenweg 1", postal_code="12345", city="Testort",
        )
        unmetered_member = Member(
            first_name="Unmetered", last_name="Tenant",
            street="Gartenweg 2", postal_code="12345", city="Testort",
        )
        metered_parcel = Parcel(plot_number="WATERPRICE-METERED", area_sqm=100)
        unmetered_parcel = Parcel(plot_number="WATERPRICE-UNMETERED", area_sqm=100)
        session.add_all([metered_member, unmetered_member, metered_parcel, unmetered_parcel])
        await session.flush()

        session.add(MemberParcel(member_id=metered_member.id, parcel_id=metered_parcel.id, is_invoice_address=True))
        session.add(MemberParcel(member_id=unmetered_member.id, parcel_id=unmetered_parcel.id, is_invoice_address=True))

        await _add_meter_with_reading(
            session, metered_parcel.id, MeteringMedium.WATER, "W-PRICE-1",
            year, initial_reading=100.0, current_reading=150.0,
        )
        # unmetered_parcel deliberately gets no MeteringPoint at all.

        await session.commit()

    run_id = await _make_run(client, year)
    # applies_to_all_parcels deliberately NOT sent ("off") and unit_price
    # deliberately wrong -- if manual scoping/pricing had any effect here,
    # this would exclude every parcel and/or bill the typed price.
    r_item = await client.post(f"/finances/runs/{run_id}/items", data={
        "order_number": "10", "name": "Water usage", "description": "",
        "pricing_mode": "water_usage", "unit_price": "999.00",
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
    assert billed_plot_numbers == {"WATERPRICE-METERED"}, (
        "only the parcel with an active water meter gets billed, regardless of applies_to_all_parcels"
    )
    line = invoices[0].line_items[0]
    assert float(line.quantity) == 50.0  # 150 - 100 initial reading
    assert float(line.unit_price) == 2.50, "price from MeteringPriceConfiguration, not the typed 999.00"
    assert float(line.line_total) == 125.00


async def test_electricity_usage_uses_its_own_price_independent_of_water(client, admin_user):
    await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})
    await _enable_finances_module()
    year = 2027

    async with AsyncSessionLocal() as session:
        session.add(MeteringPriceConfiguration(medium=MeteringMedium.WATER, year=year, price_per_unit=2.50))
        session.add(MeteringPriceConfiguration(medium=MeteringMedium.ELECTRICITY, year=year, price_per_unit=0.35))

        member = Member(
            first_name="Electric", last_name="Tenant",
            street="Vereinsstr 1", postal_code="12345", city="Testort",
        )
        parcel = Parcel(plot_number="ELECPRICE-METERED", area_sqm=100)
        session.add_all([member, parcel])
        await session.flush()
        session.add(MemberParcel(member_id=member.id, parcel_id=parcel.id, is_invoice_address=True))

        await _add_meter_with_reading(
            session, parcel.id, MeteringMedium.ELECTRICITY, "E-PRICE-1",
            year, initial_reading=1000.0, current_reading=1200.0,
        )

        await session.commit()

    run_id = await _make_run(client, year)
    r_item = await client.post(f"/finances/runs/{run_id}/items", data={
        "order_number": "10", "name": "Electricity usage", "description": "",
        "pricing_mode": "electricity_usage", "unit_price": "999.00",
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

    assert len(invoices) == 1
    line = invoices[0].line_items[0]
    assert float(line.quantity) == 200.0  # 1200 - 1000 initial reading
    assert float(line.unit_price) == 0.35, "electricity's own price, not water's 2.50 or the typed 999.00"
    assert float(line.line_total) == 70.00


async def test_water_usage_bills_nothing_when_no_price_configured_for_year(client, admin_user):
    await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})
    await _enable_finances_module()
    year = 2028

    async with AsyncSessionLocal() as session:
        # Deliberately NO MeteringPriceConfiguration for this year.
        member = Member(
            first_name="NoPrice", last_name="Tenant",
            street="Gartenweg 9", postal_code="12345", city="Testort",
        )
        parcel = Parcel(plot_number="WATERPRICE-NOCONFIG", area_sqm=100)
        session.add_all([member, parcel])
        await session.flush()
        session.add(MemberParcel(member_id=member.id, parcel_id=parcel.id, is_invoice_address=True))

        await _add_meter_with_reading(
            session, parcel.id, MeteringMedium.WATER, "W-PRICE-NOCONFIG",
            year, initial_reading=0.0, current_reading=42.0,
        )
        await session.commit()

    run_id = await _make_run(client, year)
    r_item = await client.post(f"/finances/runs/{run_id}/items", data={
        "order_number": "10", "name": "Water usage", "description": "",
        "pricing_mode": "water_usage", "unit_price": "",
    })
    assert r_item.status_code in (302, 303)

    r_finalize = await client.post(f"/finances/runs/{run_id}/finalize")
    assert r_finalize.status_code in (302, 303), r_finalize.headers.get("location")

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Invoice).where(Invoice.invoice_run_id == run_id))
        invoices = list(result.scalars().all())

    assert invoices == [], "no price configured for this year -> nothing billed, no crash"


async def test_item_template_water_usage_ignores_submitted_unit_price(client, admin_user):
    await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})
    await _enable_finances_module()

    resp = await client.post(
        "/finances/item-templates",
        data={
            "order_number": "10", "name": "Water usage template", "description": "",
            "pricing_mode": "water_usage", "unit_price": "15.00",
        },
    )
    assert resp.status_code in (302, 303)

    from app.models import InvoiceItemTemplate

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(InvoiceItemTemplate).where(InvoiceItemTemplate.name == "Water usage template")
        )
        template = result.scalar_one()

    assert template.unit_price is None, "unit_price must be ignored for water_usage, same as insurance_cost/work_hours_shortfall"
