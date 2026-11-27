"""
Issue #174: a unified, filterable, CSV-exportable/importable list of
everything booked against a FinanceAccount -- InvoicePayment rows
(always tied to an invoice) UNION ALL'd with the new AccountTransaction
rows (anything else: refunds, purchases, bank fees, CSV-imported).
Confirmed with the reporter this deliberately reopens FinanceAccount's
original "not a ledger" stance from issue #156 -- see ADR 0059.
"""
import base64
import io
from datetime import date
from decimal import Decimal

from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models import (
    ClubSetting, Parcel, Member, MemberParcel, Invoice, InvoicePayment,
    FinanceAccount, FinanceAccountType, AccountTransaction,
    IncomingInvoice, IncomingInvoicePayment,
)


async def web_login(client, email: str = "admin@example.com", password: str = "testpasswort123") -> None:
    response = await client.post("/auth/login", data={"email": email, "password": password})
    assert response.status_code in (302, 303)


async def _enable_finances_module():
    async with AsyncSessionLocal() as session:
        session.add(ClubSetting(key="modul_finances", value="true", description="test"))
        await session.commit()


async def _make_account(name="Vereinskonto") -> str:
    async with AsyncSessionLocal() as session:
        account = FinanceAccount(name=name, account_type=FinanceAccountType.BANK, is_active=True)
        session.add(account)
        await session.commit()
        return account.id


async def _make_open_invoice(client, amount: str, plot_number: str, year: str = "2026"):
    """Creates a finalized, still-unpaid Invoice -- returns (invoice_id, recipient_names)."""
    async with AsyncSessionLocal() as session:
        member = Member(
            first_name="Booking", last_name=plot_number,
            street="Gartenweg 1", postal_code="12345", city="Testort",
        )
        parcel = Parcel(plot_number=plot_number, area_sqm=100)
        session.add_all([member, parcel])
        await session.flush()
        session.add(MemberParcel(member_id=member.id, parcel_id=parcel.id, is_invoice_address=True))
        await session.commit()

    r_create = await client.post("/finances/runs", data={
        "year": year, "subject": "Booking test", "issued_date": f"{year}-08-01",
        "due_date": f"{year}-09-01", "footer_text": "",
    })
    assert r_create.status_code in (302, 303)
    run_id = r_create.headers["location"].rstrip("/").split("/")[-1]

    r_item = await client.post(f"/finances/runs/{run_id}/items", data={
        "order_number": "10", "name": "Fee", "description": "",
        "pricing_mode": "fixed_per_parcel", "unit_price": amount,
        "applies_to_all_parcels": "on",
    })
    assert r_item.status_code in (302, 303)

    r_finalize = await client.post(f"/finances/runs/{run_id}/finalize")
    assert r_finalize.status_code in (302, 303), r_finalize.headers.get("location")

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Invoice).where(Invoice.invoice_run_id == run_id))
        invoice = result.scalar_one()
        return invoice.id, invoice.recipient_names


async def _make_invoice_payment(client, account_id: str, amount: str, paid_on: str, plot_number: str) -> None:
    """Creates a finalized invoice and records a payment against it,
    tagged to account_id."""
    invoice_id, _ = await _make_open_invoice(client, amount, plot_number)

    r_pay = await client.post(f"/finances/invoices/{invoice_id}/payments", data={
        "amount": amount, "paid_on": paid_on, "note": "", "account_id": account_id,
    })
    assert r_pay.status_code in (302, 303)


async def _make_incoming_invoice_payment(client, account_id: str, amount: str, paid_on: str, sender: str) -> str:
    """Creates an incoming invoice and records a payment against it,
    tagged to account_id -- returns the incoming invoice id."""
    r_invoice = await client.post("/finances/incoming-invoices", data={
        "sender": sender, "invoice_number": "", "invoice_date": paid_on, "note": "",
        "category_id": [""], "amount": [amount],
    })
    assert r_invoice.status_code in (302, 303)

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(IncomingInvoice).where(IncomingInvoice.sender == sender))
        incoming_invoice_id = result.scalar_one().id

    r_pay = await client.post(f"/finances/incoming-invoices/{incoming_invoice_id}/payments", data={
        "amount": amount, "paid_on": paid_on, "note": "", "account_id": account_id,
    })
    assert r_pay.status_code in (302, 303)
    return incoming_invoice_id


async def test_bookings_list_unifies_invoice_payments_and_transactions(client, admin_user):
    await web_login(client)
    await _enable_finances_module()
    account_id = await _make_account()

    await _make_invoice_payment(client, account_id, "50.00", "2026-08-10", "BOOK-1")
    async with AsyncSessionLocal() as session:
        session.add(AccountTransaction(
            account_id=account_id, booking_date=date.fromisoformat("2026-08-15"), amount="-12.50",
            description="Bank fee", source="manual",
        ))
        await session.commit()

    response = await client.get(f"/finances/accounts/{account_id}/bookings")
    assert response.status_code == 200
    assert "Bank fee" in response.text
    assert "50,00" in response.text
    # Most recent first: the bank fee (Aug 15) must appear before the invoice payment (Aug 10).
    assert response.text.index("Bank fee") < response.text.index("50,00")


async def test_incoming_invoice_payment_appears_in_account_bookings(client, admin_user):
    """Issue #189: IncomingInvoicePayment was entirely missing from
    this UNION -- any expense payment tagged to an account (issue #181
    payment form, or issue #188's invoice matching) was silently
    invisible on that account's own bookings page."""
    await web_login(client)
    await _enable_finances_module()
    account_id = await _make_account()

    incoming_invoice_id = await _make_incoming_invoice_payment(
        client, account_id, "30.00", "2026-08-05", "Repair Shop",
    )

    response = await client.get(f"/finances/accounts/{account_id}/bookings")
    assert response.status_code == 200
    assert "Repair Shop" in response.text
    assert f"/finances/incoming-invoices/{incoming_invoice_id}" in response.text


async def test_incoming_invoice_payment_shows_as_negative_amount(client, admin_user):
    await web_login(client)
    await _enable_finances_module()
    account_id = await _make_account()

    await _make_incoming_invoice_payment(client, account_id, "30.00", "2026-08-06", "Negative Amount Test")

    response = await client.get(f"/finances/accounts/{account_id}/bookings")
    assert response.status_code == 200
    assert "-30,00" in response.text


async def test_incoming_invoice_payment_has_no_delete_button(client, admin_user):
    """Same reasoning as an outgoing InvoicePayment: it must be removed
    via the incoming invoice's own payment-delete route, not from here."""
    await web_login(client)
    await _enable_finances_module()
    account_id = await _make_account()
    incoming_invoice_id = await _make_incoming_invoice_payment(
        client, account_id, "20.00", "2026-08-07", "No Delete Button Test",
    )

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(IncomingInvoicePayment).where(IncomingInvoicePayment.incoming_invoice_id == incoming_invoice_id)
        )
        payment_id = result.scalar_one().id

    response = await client.get(f"/finances/accounts/{account_id}/bookings")
    assert f'/bookings/{payment_id}/delete' not in response.text


async def test_assigned_filter_yes_shows_only_invoice_linked_bookings(client, admin_user):
    await web_login(client)
    await _enable_finances_module()
    account_id = await _make_account()

    await _make_invoice_payment(client, account_id, "40.00", "2026-08-08", "ASSIGNFILTER1")
    await _make_incoming_invoice_payment(client, account_id, "25.00", "2026-08-08", "Assigned Expense")
    async with AsyncSessionLocal() as session:
        session.add(AccountTransaction(
            account_id=account_id, booking_date=date.fromisoformat("2026-08-08"), amount="-5.00",
            description="Unassigned Entry", source="manual",
        ))
        await session.commit()

    response = await client.get(f"/finances/accounts/{account_id}/bookings?assigned=yes")
    assert response.status_code == 200
    assert "40,00" in response.text
    assert "Assigned Expense" in response.text
    assert "Unassigned Entry" not in response.text


async def test_assigned_filter_no_shows_only_generic_bookings(client, admin_user):
    await web_login(client)
    await _enable_finances_module()
    account_id = await _make_account()

    await _make_invoice_payment(client, account_id, "40.00", "2026-08-09", "ASSIGNFILTER2")
    async with AsyncSessionLocal() as session:
        session.add(AccountTransaction(
            account_id=account_id, booking_date=date.fromisoformat("2026-08-09"), amount="-5.00",
            description="Unassigned Entry Two", source="manual",
        ))
        await session.commit()

    response = await client.get(f"/finances/accounts/{account_id}/bookings?assigned=no")
    assert response.status_code == 200
    assert "Unassigned Entry Two" in response.text
    assert "40,00" not in response.text


async def test_bookings_search_filters_by_description(client, admin_user):
    await web_login(client)
    await _enable_finances_module()
    account_id = await _make_account()

    async with AsyncSessionLocal() as session:
        session.add(AccountTransaction(
            account_id=account_id, booking_date=date.fromisoformat("2026-08-01"), amount="-5.00",
            description="Office supplies", source="manual",
        ))
        session.add(AccountTransaction(
            account_id=account_id, booking_date=date.fromisoformat("2026-08-02"), amount="-8.00",
            description="Postage stamps", source="manual",
        ))
        await session.commit()

    response = await client.get(f"/finances/accounts/{account_id}/bookings?search=Office")
    assert response.status_code == 200
    assert "Office supplies" in response.text
    assert "Postage stamps" not in response.text


async def test_bookings_date_range_filter(client, admin_user):
    await web_login(client)
    await _enable_finances_module()
    account_id = await _make_account()

    async with AsyncSessionLocal() as session:
        session.add(AccountTransaction(
            account_id=account_id, booking_date=date.fromisoformat("2026-01-01"), amount="-1.00",
            description="January entry", source="manual",
        ))
        session.add(AccountTransaction(
            account_id=account_id, booking_date=date.fromisoformat("2026-08-01"), amount="-2.00",
            description="August entry", source="manual",
        ))
        await session.commit()

    response = await client.get(f"/finances/accounts/{account_id}/bookings?date_from=2026-07-01")
    assert response.status_code == 200
    assert "August entry" in response.text
    assert "January entry" not in response.text


async def test_bookings_search_matches_counterparty(client, admin_user):
    """Issue #185: "I want to know who send me the money or who
    received this money from me. I want to filter for this sender or
    recipient" -- counterparty is searchable via the same free-text box
    as reference/description."""
    await web_login(client)
    await _enable_finances_module()
    account_id = await _make_account()

    async with AsyncSessionLocal() as session:
        session.add(AccountTransaction(
            account_id=account_id, booking_date=date.fromisoformat("2026-08-01"), amount="-1.00",
            description="Bank fee", counterparty="Sparkasse Musterstadt", source="manual",
        ))
        session.add(AccountTransaction(
            account_id=account_id, booking_date=date.fromisoformat("2026-08-02"), amount="-2.00",
            description="Refund", counterparty="Gartenbau Müller", source="manual",
        ))
        await session.commit()

    response = await client.get(f"/finances/accounts/{account_id}/bookings?search=Sparkasse")
    assert response.status_code == 200
    assert "Sparkasse Musterstadt" in response.text
    assert "Gartenbau Müller" not in response.text


async def _manual_confirm(client, account_id, booking_date, amount, description="", counterparty="", match_choice="none"):
    """Bypasses the intermediate match-preview page (issue #188) --
    mirrors what confirming "no match" on that page would submit."""
    return await client.post(f"/finances/accounts/{account_id}/bookings/manual/confirm", data={
        "booking_date": booking_date, "amount": amount, "description": description,
        "counterparty": counterparty, "match_choice": match_choice,
    })


async def test_bookings_manual_add_with_counterparty(client, admin_user):
    await web_login(client)
    await _enable_finances_module()
    account_id = await _make_account()

    response = await _manual_confirm(
        client, account_id, "2026-08-03", "-15.00", description="Repair", counterparty="Repair Shop GmbH",
    )
    assert response.status_code in (302, 303)

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(AccountTransaction).where(AccountTransaction.account_id == account_id)
        )
        transaction = result.scalar_one()
        assert transaction.counterparty == "Repair Shop GmbH"


async def test_manual_booking_preview_shows_matching_invoice(client, admin_user):
    await web_login(client)
    await _enable_finances_module()
    account_id = await _make_account()
    invoice_id, recipient_names = await _make_open_invoice(client, "77.00", "MATCHPREVIEW")

    response = await client.post(f"/finances/accounts/{account_id}/bookings/manual/preview", data={
        "booking_date": "2026-08-10", "amount": "77.00", "description": "", "counterparty": recipient_names,
    })
    assert response.status_code == 200
    assert f"value=\"invoice:{invoice_id}\"" in response.text


async def test_manual_booking_confirm_with_match_creates_invoice_payment(client, admin_user):
    """Issue #188: picking a suggested match creates a real
    InvoicePayment against that invoice, not a generic AccountTransaction."""
    await web_login(client)
    await _enable_finances_module()
    account_id = await _make_account()
    invoice_id, recipient_names = await _make_open_invoice(client, "88.00", "MATCHCONFIRM")

    response = await _manual_confirm(
        client, account_id, "2026-08-11", "88.00", counterparty=recipient_names,
        match_choice=f"invoice:{invoice_id}",
    )
    assert response.status_code in (302, 303)
    assert "matched=1" in response.headers["location"]

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(InvoicePayment).where(InvoicePayment.invoice_id == invoice_id))
        payment = result.scalar_one()
        assert float(payment.amount) == 88.00
        assert payment.account_id == account_id

        no_transaction = await session.execute(
            select(AccountTransaction).where(AccountTransaction.account_id == account_id)
        )
        assert no_transaction.scalar_one_or_none() is None


async def test_bookings_page_no_longer_shows_source_filter(client, admin_user):
    """Issue #184: "I do not need the field sources ... It does not
    matter if it is a paid invoice / manually added or added by CSV
    import." -- the source filter/column is gone from this page."""
    await web_login(client)
    await _enable_finances_module()
    account_id = await _make_account()

    response = await client.get(f"/finances/accounts/{account_id}/bookings")
    assert response.status_code == 200
    assert 'name="source"' not in response.text


async def test_bookings_pagination_json_endpoint(client, admin_user):
    await web_login(client)
    await _enable_finances_module()
    account_id = await _make_account()

    async with AsyncSessionLocal() as session:
        for i in range(60):
            session.add(AccountTransaction(
                account_id=account_id, booking_date=date.fromisoformat(f"2026-01-{(i % 28) + 1:02d}"), amount="-1.00",
                description=f"Entry {i}", source="manual",
            ))
        await session.commit()

    page1 = await client.get(f"/finances/accounts/{account_id}/bookings")
    assert page1.status_code == 200

    page2 = await client.get(f"/finances/accounts/{account_id}/bookings.json?offset=50")
    assert page2.status_code == 200
    data = page2.json()
    assert len(data["rows"]) == 10
    assert data["has_more"] is False


async def test_bookings_csv_export(client, admin_user):
    await web_login(client)
    await _enable_finances_module()
    account_id = await _make_account()

    async with AsyncSessionLocal() as session:
        session.add(AccountTransaction(
            account_id=account_id, booking_date=date.fromisoformat("2026-08-01"), amount="-9.99",
            description="Export me", counterparty="Export Counterparty Ltd", source="manual",
        ))
        await session.commit()

    response = await client.get(f"/finances/accounts/{account_id}/bookings/export.csv")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "Export me" in response.text
    assert "-9.99" in response.text
    assert "Export Counterparty Ltd" in response.text
    assert "Counterparty" in response.text.splitlines()[0]


async def _import_preview(client, account_id, csv_content):
    files = {"file": ("import.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    return await client.post(f"/finances/accounts/{account_id}/bookings/import/preview", files=files)


async def _import_match(client, account_id, csv_content, mapping, delimiter=";"):
    """mapping: dict of {column_index: target_field} -- mirrors what the
    preview step's mapping form would submit, without needing to parse
    the rendered HTML in every test. Hits the step-2 "match" route,
    which renders per-row invoice-match suggestions."""
    data = {"csv_content_b64": base64.b64encode(csv_content.encode("utf-8")).decode("ascii"), "delimiter": delimiter}
    for index, field in mapping.items():
        data[f"map_{index}"] = field
    return await client.post(f"/finances/accounts/{account_id}/bookings/import/match", data=data)


async def _import_finalize(client, account_id, csv_content, mapping, match_choices=None, delimiter=";"):
    """match_choices: dict of {row_index: "invoice:<id>"/"incoming_invoice:<id>"},
    defaults to "none" (generic booking) for every row -- mirrors what
    the step-3 "finalize" form would submit."""
    data = {"csv_content_b64": base64.b64encode(csv_content.encode("utf-8")).decode("ascii"), "delimiter": delimiter}
    for index, field in mapping.items():
        data[f"map_{index}"] = field
    for row_index, choice in (match_choices or {}).items():
        data[f"match_{row_index}"] = choice
    return await client.post(f"/finances/accounts/{account_id}/bookings/import/finalize", data=data)


async def test_bookings_csv_import_preview_guesses_mapping(client, admin_user):
    await web_login(client)
    await _enable_finances_module()
    account_id = await _make_account()

    csv_content = "Date;Amount;Description\n2026-08-01;-15.50;Supplies\n"
    response = await _import_preview(client, account_id, csv_content)
    assert response.status_code == 200
    assert "UndefinedError" not in response.text
    assert "Supplies" in response.text
    assert 'name="map_0"' in response.text


async def test_bookings_csv_import_confirm_creates_transactions(client, admin_user):
    await web_login(client)
    await _enable_finances_module()
    account_id = await _make_account()

    csv_content = "Date;Amount;Description\n2026-08-01;-15.50;Supplies\n2026-08-02;100.00;Membership refund\ninvalid;abc;Broken row\n"
    response = await _import_finalize(
        client, account_id, csv_content, {0: "date", 1: "amount", 2: "description"},
    )
    assert response.status_code in (302, 303)
    assert "imported=2" in response.headers["location"]
    assert "skipped=1" in response.headers["location"]

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(AccountTransaction).where(AccountTransaction.account_id == account_id)
        )
        transactions = list(result.scalars().all())

    assert len(transactions) == 2
    assert all(t.source == "csv_import" for t in transactions)
    descriptions = {t.description for t in transactions}
    assert descriptions == {"Supplies", "Membership refund"}


async def test_bookings_csv_import_keeps_amounts_of_1000_and_more(client, admin_user):
    """Issue #350: "1.234,56" (German) and "1,234.56" (English) were
    invalid, so these rows were silently skipped."""
    await web_login(client)
    await _enable_finances_module()
    account_id = await _make_account()

    csv_content = (
        "Datum;Betrag;Verwendungszweck\n"
        "2026-08-01;1.234,56;Pacht Parzelle 7\n"
        "2026-08-02;-2.500,00;Wasserrechnung\n"
        "2026-08-03;1,234.56;English export\n"
        "2026-08-04;15,50;Kleinbetrag\n"
    )
    response = await _import_finalize(client, account_id, csv_content, {0: "date", 1: "amount", 2: "description"})
    assert "imported=4" in response.headers["location"] and "skipped=0" in response.headers["location"]

    async with AsyncSessionLocal() as session:
        amounts = {
            t.description: t.amount for t in (await session.execute(
                select(AccountTransaction).where(AccountTransaction.account_id == account_id)
            )).scalars()
        }
    assert amounts == {
        "Pacht Parzelle 7": Decimal("1234.56"), "Wasserrechnung": Decimal("-2500.00"),
        "English export": Decimal("1234.56"), "Kleinbetrag": Decimal("15.50"),
    }


async def test_bookings_csv_import_requires_date_and_amount_mapping(client, admin_user):
    await web_login(client)
    await _enable_finances_module()
    account_id = await _make_account()

    csv_content = "Date;Amount;Description\n2026-08-01;-15.50;Supplies\n"
    response = await _import_finalize(client, account_id, csv_content, {2: "description"})
    assert response.status_code in (302, 303)
    assert "error=" in response.headers["location"]

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(AccountTransaction).where(AccountTransaction.account_id == account_id)
        )
        assert result.scalar_one_or_none() is None


async def test_bookings_csv_import_with_counterparty_column(client, admin_user):
    await web_login(client)
    await _enable_finances_module()
    account_id = await _make_account()

    csv_content = "Date;Amount;Description;Counterparty\n2026-08-01;-15.50;Supplies;Hardware Store\n"
    response = await _import_finalize(
        client, account_id, csv_content, {0: "date", 1: "amount", 2: "description", 3: "counterparty"},
    )
    assert response.status_code in (302, 303)

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(AccountTransaction).where(AccountTransaction.account_id == account_id)
        )
        transaction = result.scalar_one()
        assert transaction.counterparty == "Hardware Store"


async def test_bookings_csv_import_backfills_empty_member_iban(client, admin_user):
    """Issue #187: match by name against the mapped counterparty
    column, backfill IBAN only when the member's own IBAN is empty."""
    await web_login(client)
    await _enable_finances_module()
    account_id = await _make_account()

    async with AsyncSessionLocal() as session:
        member = Member(first_name="Erika", last_name="Musterfrau")
        session.add(member)
        await session.commit()
        member_id = member.id

    csv_content = (
        "Date;Amount;Description;Counterparty;IBAN\n"
        "2026-08-01;50.00;Dues;Erika Musterfrau;DE89370400440532013000\n"
    )
    response = await _import_finalize(
        client, account_id, csv_content,
        {0: "date", 1: "amount", 2: "description", 3: "counterparty", 4: "iban"},
    )
    assert response.status_code in (302, 303)
    assert "iban_updated=1" in response.headers["location"]

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Member).where(Member.id == member_id))
        refreshed = result.scalar_one()
        assert refreshed.iban == "DE89370400440532013000"


async def test_bookings_csv_import_does_not_overwrite_existing_member_iban(client, admin_user):
    await web_login(client)
    await _enable_finances_module()
    account_id = await _make_account()

    async with AsyncSessionLocal() as session:
        member = Member(first_name="Hans", last_name="Beispiel", iban="DE00000000000000000000")
        session.add(member)
        await session.commit()
        member_id = member.id

    csv_content = (
        "Date;Amount;Description;Counterparty;IBAN\n"
        "2026-08-01;50.00;Dues;Hans Beispiel;DE89370400440532013000\n"
    )
    response = await _import_finalize(
        client, account_id, csv_content,
        {0: "date", 1: "amount", 2: "description", 3: "counterparty", 4: "iban"},
    )
    assert response.status_code in (302, 303)
    assert "iban_updated=0" in response.headers["location"]

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Member).where(Member.id == member_id))
        refreshed = result.scalar_one()
        assert refreshed.iban == "DE00000000000000000000"


async def test_csv_import_match_step_shows_candidate_invoices(client, admin_user):
    await web_login(client)
    await _enable_finances_module()
    account_id = await _make_account()
    invoice_id, recipient_names = await _make_open_invoice(client, "66.00", "CSVMATCH")

    csv_content = f"Date;Amount;Counterparty\n2026-08-01;66.00;{recipient_names}\n"
    response = await _import_match(
        client, account_id, csv_content, {0: "date", 1: "amount", 2: "counterparty"},
    )
    assert response.status_code == 200
    assert f"invoice:{invoice_id}" in response.text


async def test_csv_import_finalize_with_match_creates_invoice_payment(client, admin_user):
    await web_login(client)
    await _enable_finances_module()
    account_id = await _make_account()
    invoice_id, recipient_names = await _make_open_invoice(client, "55.00", "CSVFINALIZE")

    csv_content = f"Date;Amount;Counterparty\n2026-08-01;55.00;{recipient_names}\n"
    response = await _import_finalize(
        client, account_id, csv_content, {0: "date", 1: "amount", 2: "counterparty"},
        match_choices={0: f"invoice:{invoice_id}"},
    )
    assert response.status_code in (302, 303)
    assert "matched=1" in response.headers["location"]

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(InvoicePayment).where(InvoicePayment.invoice_id == invoice_id))
        payment = result.scalar_one()
        assert float(payment.amount) == 55.00

        no_transaction = await session.execute(
            select(AccountTransaction).where(AccountTransaction.account_id == account_id)
        )
        assert no_transaction.scalar_one_or_none() is None


async def test_bookings_manual_add_and_delete(client, admin_user):
    await web_login(client)
    await _enable_finances_module()
    account_id = await _make_account()

    r_add = await _manual_confirm(client, account_id, "2026-08-01", "-3.33", description="Coffee for the meeting")
    assert r_add.status_code in (302, 303)

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(AccountTransaction).where(AccountTransaction.account_id == account_id)
        )
        transaction = result.scalar_one()
        assert transaction.source == "manual"
        assert float(transaction.amount) == -3.33

    r_delete = await client.post(f"/finances/accounts/{account_id}/bookings/{transaction.id}/delete")
    assert r_delete.status_code in (302, 303)

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(AccountTransaction).where(AccountTransaction.account_id == account_id)
        )
        assert result.scalar_one_or_none() is None


async def test_account_deletion_cascades_transactions(client, admin_user):
    """Unlike InvoicePayment.account_id (ON DELETE SET NULL, keeping the
    payment), an AccountTransaction only exists for its account -- it
    must be CASCADE-deleted with it. Since issue #353 the web UI refuses
    to delete an account that has bookings, so this pins the schema rule
    by deleting directly."""
    await web_login(client)
    await _enable_finances_module()
    account_id = await _make_account()

    async with AsyncSessionLocal() as session:
        session.add(AccountTransaction(
            account_id=account_id, booking_date=date.fromisoformat("2026-08-01"), amount="-1.00",
            description="Should vanish with the account", source="manual",
        ))
        await session.commit()

    async with AsyncSessionLocal() as session:
        await session.delete(await session.get(FinanceAccount, account_id))
        await session.commit()

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(AccountTransaction).where(AccountTransaction.account_id == account_id)
        )
        assert result.scalar_one_or_none() is None


# --- Issue #353: deleting an account took its whole ledger with it ---

async def test_account_with_bookings_cannot_be_deleted(client, admin_user):
    import urllib.parse
    await web_login(client)
    await _enable_finances_module()
    account_id = await _make_account("Girokonto")
    await _import_finalize(client, account_id, "Date;Amount;Description\n2026-08-01;-15.50;Supplies\n2026-08-02;100.00;Refund\n",
                           {0: "date", 1: "amount", 2: "description"})

    page = (await client.get("/finances/accounts")).text
    assert f"/finances/accounts/{account_id}/delete" not in page  # only a greyed-out button
    assert "Has bookings: untick" in page

    response = await client.post(f"/finances/accounts/{account_id}/delete")
    assert response.status_code == 303
    message = urllib.parse.unquote(response.headers["location"])
    assert "“Girokonto” has 2 booking(s) and can't be deleted." in message
    async with AsyncSessionLocal() as session:
        assert await session.get(FinanceAccount, account_id) is not None
        transactions = (await session.execute(
            select(AccountTransaction).where(AccountTransaction.account_id == account_id)
        )).scalars().all()
    assert len(transactions) == 2


async def test_account_with_only_an_invoice_payment_cannot_be_deleted_either(client, admin_user):
    await web_login(client)
    await _enable_finances_module()
    account_id = await _make_account()
    invoice_id, recipient_names = await _make_open_invoice(client, "40.00", "DELPAY")
    await _import_finalize(client, account_id, f"Date;Amount;Counterparty\n2026-08-01;40.00;{recipient_names}\n",
                           {0: "date", 1: "amount", 2: "counterparty"}, match_choices={0: f"invoice:{invoice_id}"})
    response = await client.post(f"/finances/accounts/{account_id}/delete")
    assert "error=" in response.headers["location"]
    async with AsyncSessionLocal() as session:
        assert await session.get(FinanceAccount, account_id) is not None


async def test_empty_account_can_still_be_deleted(client, admin_user):
    await web_login(client)
    await _enable_finances_module()
    account_id = await _make_account("Leer")
    assert f"/finances/accounts/{account_id}/delete" in (await client.get("/finances/accounts")).text
    response = await client.post(f"/finances/accounts/{account_id}/delete")
    assert "success=1" in response.headers["location"]
    async with AsyncSessionLocal() as session:
        assert await session.get(FinanceAccount, account_id) is None


# --- Issue #356: importing the same statement twice ---

_STATEMENT = (
    "Date;Amount;Description\n"
    "2026-08-01;-15.50;Supplies\n"
    "2026-08-02;100.00;Membership refund\n"
)
_MAPPING = {0: "date", 1: "amount", 2: "description"}


async def _account_transactions(account_id):
    async with AsyncSessionLocal() as session:
        return list((await session.execute(
            select(AccountTransaction).where(AccountTransaction.account_id == account_id)
        )).scalars())


async def test_reimporting_the_same_statement_adds_nothing(client, admin_user):
    await web_login(client)
    await _enable_finances_module()
    account_id = await _make_account()

    first = await _import_finalize(client, account_id, _STATEMENT, _MAPPING)
    assert "imported=2" in first.headers["location"]
    # The same file again -- e.g. the back button, a double click, or next month's export overlapping this one.
    again = await _import_finalize(client, account_id, _STATEMENT, _MAPPING)
    assert "imported=0" in again.headers["location"] and "duplicates=2" in again.headers["location"]
    assert len(await _account_transactions(account_id)) == 2


async def test_duplicates_are_counted_not_just_compared(client, admin_user):
    """Two identical bookings on one day are real: the file has two, the account one -> one is new."""
    await web_login(client)
    await _enable_finances_module()
    account_id = await _make_account()
    await _import_finalize(client, account_id, "Date;Amount;Description\n2026-08-01;-2.00;Coffee\n", _MAPPING)

    two = "Date;Amount;Description\n2026-08-01;-2.00;Coffee\n2026-08-01;-2.00;Coffee\n"
    response = await _import_finalize(client, account_id, two, _MAPPING)
    assert "imported=1" in response.headers["location"] and "duplicates=1" in response.headers["location"]
    assert len(await _account_transactions(account_id)) == 2


async def test_match_page_marks_duplicates_and_they_can_still_be_imported(client, admin_user):
    await web_login(client)
    await _enable_finances_module()
    account_id = await _make_account()
    await _import_finalize(client, account_id, "Date;Amount;Description\n2026-08-01;-15.50;Supplies\n", _MAPPING)

    data = {"csv_content_b64": base64.b64encode(_STATEMENT.encode()).decode("ascii"), "delimiter": ";",
            **{f"map_{i}": f for i, f in _MAPPING.items()}}
    page = (await client.post(f"/finances/accounts/{account_id}/bookings/import/match", data=data)).text
    assert page.count("Already imported") == 1
    assert 'name="duplicate_0" value="1"' in page and 'name="duplicate_1"' not in page
    assert '<option value="skip" selected>' in page  # the duplicate row is preset to "Don't import"

    # The user decides the "duplicate" is a second real booking and imports it anyway.
    forced = await client.post(f"/finances/accounts/{account_id}/bookings/import/finalize",
                               data={**data, "match_0": "none", "duplicate_0": "1", "match_1": "none"})
    assert "imported=2" in forced.headers["location"]
    assert len(await _account_transactions(account_id)) == 3


async def test_stale_form_does_not_pay_an_invoice_twice(client, admin_user):
    await web_login(client)
    await _enable_finances_module()
    account_id = await _make_account()
    invoice_id, recipient_names = await _make_open_invoice(client, "55.00", "CSVTWICE")

    paid = await _import_finalize(client, account_id, f"Date;Amount;Counterparty\n2026-08-01;55.00;{recipient_names}\n",
                                  {0: "date", 1: "amount", 2: "counterparty"}, match_choices={0: f"invoice:{invoice_id}"})
    assert "matched=1" in paid.headers["location"]
    # Another row (other date, so not a duplicate) still pointing at that invoice, e.g. an old open tab.
    stale = await _import_finalize(client, account_id, f"Date;Amount;Counterparty\n2026-08-05;55.00;{recipient_names}\n",
                                   {0: "date", 1: "amount", 2: "counterparty"}, match_choices={0: f"invoice:{invoice_id}"})
    assert "already_paid=1" in stale.headers["location"] and "imported=0" in stale.headers["location"]
    async with AsyncSessionLocal() as session:
        payments = (await session.execute(select(InvoicePayment).where(InvoicePayment.invoice_id == invoice_id))).scalars().all()
    assert len(payments) == 1
