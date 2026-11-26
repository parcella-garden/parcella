"""A number format without {year} ("R-{number}") must keep counting
across years: restarting at 1 in the second year repeated "R-1" and the
finalize failed on the unique invoice number (audit 2026-11-26)."""
from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models import ClubSetting, Invoice, Member, MemberParcel, Parcel


async def _finalize_run_for(client, year: str) -> str:
    r_create = await client.post("/finances/runs", data={
        "year": year, "subject": f"Annual invoice {year}", "issued_date": f"{year}-08-01",
        "due_date": f"{year}-09-01", "footer_text": "",
    })
    run_id = r_create.headers["location"].rstrip("/").split("/")[-1]
    await client.post(f"/finances/runs/{run_id}/items", data={
        "order_number": "10", "name": "Lease", "description": "",
        "pricing_mode": "fixed_per_parcel", "unit_price": "50.00", "applies_to_all_parcels": "on",
    })
    r_finalize = await client.post(f"/finances/runs/{run_id}/finalize")
    assert r_finalize.status_code in (302, 303)
    assert "error" not in r_finalize.headers["location"], r_finalize.headers["location"]
    return run_id


async def test_numbers_without_year_continue_across_years(client, admin_user):
    await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})
    async with AsyncSessionLocal() as session:
        session.add(ClubSetting(key="modul_finances", value="true", description="test"))
        session.add(ClubSetting(key="invoice_number_format", value="R-{number}", description="test"))
        parcel = Parcel(plot_number="1", area_sqm=200)
        tenant = Member(first_name="Erna", last_name="Example", street="Weg 1", postal_code="12345", city="Ort")
        session.add_all([parcel, tenant])
        await session.flush()
        session.add(MemberParcel(member_id=tenant.id, parcel_id=parcel.id, is_invoice_address=True))
        await session.commit()

    first_run = await _finalize_run_for(client, "2026")
    second_run = await _finalize_run_for(client, "2027")

    async with AsyncSessionLocal() as session:
        numbers = {
            run_id: (await session.execute(
                select(Invoice.invoice_number).where(Invoice.invoice_run_id == run_id)
            )).scalar_one()
            for run_id in (first_run, second_run)
        }
    assert numbers == {first_run: "R-1", second_run: "R-2"}
