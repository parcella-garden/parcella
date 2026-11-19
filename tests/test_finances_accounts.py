"""
Issue #156: "add possibility to add accounts in /finances/accounts/"
(bank accounts + cash accounts). Confirmed scope: not just a named
list -- payments should be attributable to an account, with each
account showing the payments recorded against it and their sum. Still
not a ledger: no manual transactions, no opening balance, just a tag
on InvoicePayment plus a sum of what the app already tracks (same role
FinanceCategory already has for item definitions).
"""
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import AsyncSessionLocal
from app.models import (
    ClubSetting, Parcel, Member, MemberParcel, Invoice, InvoicePayment,
    FinanceAccount, FinanceAccountType,
)


async def _enable_finances_module():
    async with AsyncSessionLocal() as session:
        session.add(ClubSetting(key="modul_finances", value="true", description="test"))
        await session.commit()


async def web_login(client, email: str = "admin@example.com", password: str = "testpasswort123") -> None:
    response = await client.post("/auth/login", data={"email": email, "password": password})
    assert response.status_code in (302, 303)


async def _make_invoice(client, year=2026, plot_number="ACCT-TEST") -> str:
    """Creates a run with one FIXED_PER_PARCEL item on one parcel,
    finalizes it, and returns the resulting Invoice id."""
    async with AsyncSessionLocal() as session:
        member = Member(
            first_name="Account", last_name="Tester",
            street="Gartenweg 1", postal_code="12345", city="Testort",
        )
        parcel = Parcel(plot_number=plot_number, area_sqm=100)
        session.add_all([member, parcel])
        await session.flush()
        session.add(MemberParcel(member_id=member.id, parcel_id=parcel.id, is_invoice_address=True))
        await session.commit()

    r_create = await client.post("/finances/runs", data={
        "year": str(year), "subject": "Account test", "issued_date": f"{year}-08-01",
        "due_date": f"{year}-09-01", "footer_text": "",
    })
    assert r_create.status_code in (302, 303)
    run_id = r_create.headers["location"].rstrip("/").split("/")[-1]

    r_item = await client.post(f"/finances/runs/{run_id}/items", data={
        "order_number": "10", "name": "Fee", "description": "",
        "pricing_mode": "fixed_per_parcel", "unit_price": "50.00",
        "applies_to_all_parcels": "on",
    })
    assert r_item.status_code in (302, 303)

    r_finalize = await client.post(f"/finances/runs/{run_id}/finalize")
    assert r_finalize.status_code in (302, 303), r_finalize.headers.get("location")

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Invoice).where(Invoice.invoice_run_id == run_id))
        invoice = result.scalar_one()
        return invoice.id


async def test_account_create_list_and_edit(client, admin_user):
    await web_login(client)
    await _enable_finances_module()

    r_create = await client.post("/finances/accounts", data={
        "name": "Sparkasse Giro (neu)", "account_type": "BANK",
        "account_number": "DE00 1234 5678 9012 3456 00", "note": "", "is_active": "on",
    })
    assert r_create.status_code in (302, 303)

    page = await client.get("/finances/accounts")
    assert page.status_code == 200
    assert "Sparkasse Giro (neu)" in page.text

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(FinanceAccount).where(FinanceAccount.name == "Sparkasse Giro (neu)"))
        account = result.scalar_one()
        assert account.account_type == FinanceAccountType.BANK
        assert account.is_active is True

    r_edit = await client.post(f"/finances/accounts/{account.id}/edit", data={
        "name": "Sparkasse Giro (alt)", "account_type": "BANK",
        "account_number": "", "note": "closed 2026", "is_active": "",
    })
    assert r_edit.status_code in (302, 303)

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(FinanceAccount).where(FinanceAccount.id == account.id))
        updated = result.scalar_one()
        assert updated.name == "Sparkasse Giro (alt)"
        assert updated.is_active is False
        assert updated.note == "closed 2026"


async def test_cash_account_create(client, admin_user):
    await web_login(client)
    await _enable_finances_module()

    r_create = await client.post("/finances/accounts", data={
        "name": "Cash box", "account_type": "CASH", "account_number": "", "note": "", "is_active": "on",
    })
    assert r_create.status_code in (302, 303)

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(FinanceAccount).where(FinanceAccount.name == "Cash box"))
        account = result.scalar_one()
        assert account.account_type == FinanceAccountType.CASH


async def test_recording_payment_with_account_persists_and_displays(client, admin_user):
    await web_login(client)
    await _enable_finances_module()

    await client.post("/finances/accounts", data={
        "name": "Main Giro", "account_type": "BANK", "account_number": "", "note": "", "is_active": "on",
    })
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(FinanceAccount).where(FinanceAccount.name == "Main Giro"))
        account = result.scalar_one()

    invoice_id = await _make_invoice(client, year=2026, plot_number="ACCT-PAYMENT")

    r_payment = await client.post(f"/finances/invoices/{invoice_id}/payments", data={
        "amount": "50.00", "paid_on": "2026-08-15", "note": "", "account_id": account.id,
    })
    assert r_payment.status_code in (302, 303)

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(InvoicePayment)
            .options(selectinload(InvoicePayment.account))
            .where(InvoicePayment.invoice_id == invoice_id)
        )
        payment = result.scalar_one()
        assert payment.account_id == account.id
        assert payment.account.name == "Main Giro"

    # Issue #175/#176/#177: the invoice detail page no longer shows a
    # Payments card (payments are recorded from the run page, #173) --
    # the account-tagged booking now displays on the account's own
    # bookings list instead (#174).
    page = await client.get(f"/finances/accounts/{account.id}/bookings")
    assert page.status_code == 200
    assert "Main Giro" in page.text


async def test_deleting_account_sets_payment_account_null_not_cascade(client, admin_user):
    await web_login(client)
    await _enable_finances_module()

    await client.post("/finances/accounts", data={
        "name": "To Be Deleted", "account_type": "BANK", "account_number": "", "note": "", "is_active": "on",
    })
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(FinanceAccount).where(FinanceAccount.name == "To Be Deleted"))
        account = result.scalar_one()

    invoice_id = await _make_invoice(client, year=2027, plot_number="ACCT-DELETE")

    await client.post(f"/finances/invoices/{invoice_id}/payments", data={
        "amount": "50.00", "paid_on": "2027-08-15", "note": "", "account_id": account.id,
    })

    # Issue #353: the web UI now refuses (the account has a booking) ...
    r_delete = await client.post(f"/finances/accounts/{account.id}/delete")
    assert r_delete.status_code == 303 and "error=" in r_delete.headers["location"]
    # ... so the schema rule (SET NULL, the payment survives) is pinned by deleting directly.
    async with AsyncSessionLocal() as session:
        await session.delete(await session.get(FinanceAccount, account.id))
        await session.commit()

    async with AsyncSessionLocal() as session:
        deleted = await session.execute(select(FinanceAccount).where(FinanceAccount.id == account.id))
        assert deleted.scalar_one_or_none() is None

        payment_result = await session.execute(select(InvoicePayment).where(InvoicePayment.invoice_id == invoice_id))
        payment = payment_result.scalar_one()
        assert payment.account_id is None, "the payment record itself must survive, only its account link is cleared"


async def test_inactive_account_excluded_from_payment_dropdown(client, admin_user):
    await web_login(client)
    await _enable_finances_module()

    await client.post("/finances/accounts", data={
        "name": "Active Account", "account_type": "BANK", "account_number": "", "note": "", "is_active": "on",
    })
    await client.post("/finances/accounts", data={
        "name": "Closed Account", "account_type": "BANK", "account_number": "", "note": "", "is_active": "",
    })

    invoice_id = await _make_invoice(client, year=2028, plot_number="ACCT-INACTIVE")

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Invoice).where(Invoice.id == invoice_id))
        run_id = result.scalar_one().invoice_run_id

    # Issue #175/#176/#177: the payment form (and its account dropdown)
    # moved from the invoice detail page to the run detail page (#173).
    page = await client.get(f"/finances/runs/{run_id}")
    assert page.status_code == 200
    assert "Active Account" in page.text
    assert "Closed Account" not in page.text


async def test_dashboard_shows_account_count(client, admin_user):
    await web_login(client)
    await _enable_finances_module()

    await client.post("/finances/accounts", data={
        "name": "Account One", "account_type": "BANK", "account_number": "", "note": "", "is_active": "on",
    })
    await client.post("/finances/accounts", data={
        "name": "Account Two", "account_type": "CASH", "account_number": "", "note": "", "is_active": "on",
    })

    page = await client.get("/finances/")
    assert page.status_code == 200
    assert "2 account(s) defined" in page.text
