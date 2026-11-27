"""
Issue #77: only invoice-address members who also opted into email
notifications should be emailed; the print bundle must contain only
those with is_invoice_address=True and email_notifications=False --
regardless of whether /deliver has run yet (see app/invoice_delivery.py
and the print-bundle filter in app/routers/finances/runs.py).
"""
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import AsyncSessionLocal
from app.models import Member, MemberEmail, MemberParcel, Parcel, Invoice, ClubSetting


async def _enable_finances_module():
    """Finances defaults to off (see app/module_flags.py); enable it
    directly via ClubSetting, same pattern test_smoke_templates.py uses."""
    async with AsyncSessionLocal() as session:
        session.add(ClubSetting(key="modul_finances", value="true", description="test"))
        await session.commit()


async def _make_run(client, year="2026"):
    r_create = await client.post("/finances/runs", data={
        "year": year, "subject": "Delivery test", "issued_date": f"{year}-08-01",
        "due_date": f"{year}-09-01", "footer_text": "",
    })
    assert r_create.status_code in (302, 303)
    return r_create.headers["location"].rstrip("/").split("/")[-1]


async def test_print_bundle_excludes_email_eligible_members_even_before_deliver(client, admin_user, monkeypatch):
    """The core bug in #77: calling print-bundle before deliver used to
    include every invoice (emailed_at was still None for everyone), so
    an email-opted-in member's invoice would end up printed AND later
    emailed. The filter must be based on recipient eligibility, not on
    the emailed_at side effect."""
    async def fake_send_email(recipient, subject, html_body, text_body=None, db=None, attachments=None):
        return True

    monkeypatch.setattr("app.invoice_delivery.send_email", fake_send_email)

    await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})
    await _enable_finances_module()

    async with AsyncSessionLocal() as session:
        email_member = Member(
            first_name="Email", last_name="Reachable",
            street="Test-Str 1", postal_code="12345", city="Testort",
            email_notifications=True,
        )
        print_member = Member(
            first_name="Print", last_name="Only",
            street="Test-Str 2", postal_code="12345", city="Testort",
            email_notifications=False,
        )
        email_parcel = Parcel(plot_number="ISSUE77-EMAIL", area_sqm=100)
        print_parcel = Parcel(plot_number="ISSUE77-PRINT", area_sqm=100)
        session.add_all([email_member, print_member, email_parcel, print_parcel])
        await session.flush()
        session.add(MemberEmail(member_id=email_member.id, address="reachable@example.com", is_primary=True))
        session.add(MemberParcel(member_id=email_member.id, parcel_id=email_parcel.id, is_invoice_address=True))
        session.add(MemberParcel(member_id=print_member.id, parcel_id=print_parcel.id, is_invoice_address=True))
        await session.commit()

    run_id = await _make_run(client)
    r_item = await client.post(f"/finances/runs/{run_id}/items", data={
        "order_number": "10", "name": "Membership fee", "description": "",
        "pricing_mode": "fixed_per_parcel", "unit_price": "12.50", "applies_to_all_parcels": "on",
    })
    assert r_item.status_code in (302, 303)

    r_finalize = await client.post(f"/finances/runs/{run_id}/finalize")
    assert r_finalize.status_code in (302, 303), r_finalize.headers.get("location")

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Invoice)
            .options(selectinload(Invoice.parcel))
            .where(Invoice.invoice_run_id == run_id)
        )
        invoices_by_parcel = {i.parcel.plot_number: i for i in result.scalars().unique().all()}
    email_invoice_id = invoices_by_parcel["ISSUE77-EMAIL"].id
    print_invoice_id = invoices_by_parcel["ISSUE77-PRINT"].id

    # Print bundle requested BEFORE /deliver ever ran.
    r_bundle = await client.get(f"/finances/runs/{run_id}/print-bundle")
    assert r_bundle.status_code == 200
    assert r_bundle.headers["content-type"] == "application/pdf"

    async with AsyncSessionLocal() as session:
        email_invoice = await session.get(Invoice, email_invoice_id)
        print_invoice = await session.get(Invoice, print_invoice_id)
        assert email_invoice.printed_at is None, "email-eligible member must never be printed"
        assert print_invoice.printed_at is not None, "print-only member must be in the bundle"
        assert email_invoice.emailed_at is None, "deliver hasn't run yet"

    # Now deliver: the email-eligible member gets emailed; the
    # print-only member is untouched (no stored email at all).
    r_deliver = await client.post(f"/finances/runs/{run_id}/deliver")
    assert r_deliver.status_code in (302, 303)
    assert "emailed=1" in r_deliver.headers["location"]

    async with AsyncSessionLocal() as session:
        email_invoice = await session.get(Invoice, email_invoice_id)
        print_invoice = await session.get(Invoice, print_invoice_id)
        assert email_invoice.emailed_at is not None
        assert email_invoice.printed_at is None, "must still never be printed, even after deliver"
        assert print_invoice.emailed_at is None


async def test_print_bundle_excludes_invoice_address_member_with_email_notifications_off_but_no_email(client, admin_user):
    """A member with is_invoice_address=True and email_notifications=False
    but with a stored email address is still print-only -- opting out of
    email notifications takes precedence, matching issue #77's explicit
    address=true AND email_info=false rule for the print bundle."""
    await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})
    await _enable_finances_module()

    async with AsyncSessionLocal() as session:
        member = Member(
            first_name="OptedOut", last_name="ButHasEmail",
            street="Test-Str 3", postal_code="12345", city="Testort",
            email_notifications=False,
        )
        parcel = Parcel(plot_number="ISSUE77-OPTOUT", area_sqm=100)
        session.add_all([member, parcel])
        await session.flush()
        session.add(MemberEmail(member_id=member.id, address="optedout@example.com", is_primary=True))
        session.add(MemberParcel(member_id=member.id, parcel_id=parcel.id, is_invoice_address=True))
        await session.commit()

    run_id = await _make_run(client, year="2027")
    await client.post(f"/finances/runs/{run_id}/items", data={
        "order_number": "10", "name": "Membership fee", "description": "",
        "pricing_mode": "fixed_per_parcel", "unit_price": "12.50", "applies_to_all_parcels": "on",
    })
    r_finalize = await client.post(f"/finances/runs/{run_id}/finalize")
    assert r_finalize.status_code in (302, 303)

    r_deliver = await client.post(f"/finances/runs/{run_id}/deliver")
    assert "emailed=0" in r_deliver.headers["location"]

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Invoice).where(Invoice.invoice_run_id == run_id))
        invoice = result.scalars().first()
    assert invoice.emailed_at is None

    r_bundle = await client.get(f"/finances/runs/{run_id}/print-bundle")
    assert r_bundle.status_code == 200

    async with AsyncSessionLocal() as session:
        invoice = await session.get(Invoice, invoice.id)
        assert invoice.printed_at is not None


async def test_invoice_reaches_every_address_of_a_parcels_tenants(client, admin_user, monkeypatch):
    """Issue #396: one invoice per parcel, one copy per address. Anna
    and Bernd share an address; only Anna consented to email. Clara
    lives elsewhere without email -- before #396 she was left off the
    invoice and got nothing at all. Now: Anna gets an email, Bernd a
    letter of his own anyway (one member's email doesn't cover the
    household, kermie), Clara a letter; the reminder likewise."""
    import io
    from pypdf import PdfReader
    from app.models import InvoiceReminder

    sent = []

    async def fake_send_email(recipient, subject, html_body, text_body=None, db=None, attachments=None):
        sent.append((recipient, attachments[0][1]))
        return True

    monkeypatch.setattr("app.invoice_delivery.send_email", fake_send_email)
    await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})
    await _enable_finances_module()

    async with AsyncSessionLocal() as session:
        anna = Member(first_name="Anna", last_name="Haus", street="Lindenweg 1", postal_code="04103", city="Leipzig", email_notifications=True)
        bernd = Member(first_name="Bernd", last_name="Haus", street=" lindenweg 1", postal_code="04103", city="LEIPZIG", email_notifications=False)
        clara = Member(first_name="Clara", last_name="Fern", street="Am Hang 7", postal_code="01067", city="Dresden", email_notifications=False)
        parcel = Parcel(plot_number="ISSUE396", area_sqm=100)
        session.add_all([anna, bernd, clara, parcel])
        await session.flush()
        session.add(MemberEmail(member_id=anna.id, address="anna@example.com", is_primary=True))
        for m in (clara, anna, bernd):
            session.add(MemberParcel(member_id=m.id, parcel_id=parcel.id, is_invoice_address=True))
        await session.commit()

    run_id = await _make_run(client, year="2028")
    await client.post(f"/finances/runs/{run_id}/items", data={
        "order_number": "10", "name": "Membership fee", "description": "",
        "pricing_mode": "fixed_per_parcel", "unit_price": "40.00", "applies_to_all_parcels": "on",
    })
    assert (await client.post(f"/finances/runs/{run_id}/finalize")).status_code in (302, 303)

    async with AsyncSessionLocal() as session:
        invoices = (await session.execute(select(Invoice).where(Invoice.invoice_run_id == run_id))).scalars().all()
    assert len(invoices) == 1, "still one invoice per parcel"
    invoice = invoices[0]
    copies = invoice.recipient_copies
    assert [c["names"] for c in copies] == ["Anna Haus\nBernd Haus", "Clara Fern"], "largest address group first"
    assert "Dresden" in copies[1]["address"]
    assert all(n in invoice.recipient_names for n in ("Anna Haus", "Bernd Haus", "Clara Fern"))

    def pdf_text(data: bytes) -> str:
        return " ".join(" ".join(p.extract_text() for p in PdfReader(io.BytesIO(data)).pages).split())

    # Email: Anna gets the copy for Lindenweg; Clara has no email.
    r_deliver = await client.post(f"/finances/runs/{run_id}/deliver")
    assert "emailed=1" in r_deliver.headers["location"]
    assert [r for r, _ in sent] == ["anna@example.com"]
    assert "Bernd Haus" in pdf_text(sent[0][1]) and "Clara Fern" not in pdf_text(sent[0][1])

    # Print bundle: a letter to Bernd (just him, at Lindenweg) and one to
    # Clara, even though the invoice was emailed to Anna.
    bundle = await client.get(f"/finances/runs/{run_id}/print-bundle")
    assert bundle.status_code == 200
    pages = [" ".join(p.extract_text().split()) for p in PdfReader(io.BytesIO(bundle.content)).pages]
    assert len(pages) == 2
    assert any("Bernd Haus" in p and "Lindenweg 1" in p and "Anna Haus" not in p for p in pages)
    assert any("Clara Fern" in p and "Am Hang 7" in p for p in pages)

    # The invoice's own PDF holds both copies.
    full = pdf_text((await client.get(f"/finances/invoices/{invoice.id}/pdf")).content)
    assert "Clara Fern" in full and "Anna Haus" in full
    detail = await client.get(f"/finances/invoices/{invoice.id}")
    assert "2 copies, one per address" in detail.text

    # Reminder: emailed to Anna, Bernd's and Clara's letters to print.
    sent.clear()
    assert (await client.post(f"/finances/invoices/{invoice.id}/reminders", data={"fee_amount": "", "message": ""})).status_code in (302, 303)
    assert [r for r, _ in sent] == ["anna@example.com"]
    async with AsyncSessionLocal() as session:
        reminder = (await session.execute(select(InvoiceReminder).where(InvoiceReminder.invoice_id == invoice.id))).scalar_one()
    assert reminder.delivery_method == "both"
    reminder_text = pdf_text((await client.get(f"/finances/reminders/{reminder.id}/pdf")).content)
    assert "Clara Fern" in reminder_text and "Bernd Haus" in reminder_text and "Anna Haus" not in reminder_text


async def test_invoice_pdf_escapes_the_recipients_names(client, admin_user):
    """A name is shown as typed in the address window, not read as HTML."""
    from app.invoice_pdf import invoice_copies

    await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})
    await _enable_finances_module()
    async with AsyncSessionLocal() as session:
        member = Member(first_name="<b>Fett", last_name="Name</b>", street="Weg 1", postal_code="1", city="X")
        parcel = Parcel(plot_number="ISSUE396-ESC", area_sqm=100)
        session.add_all([member, parcel])
        await session.flush()
        session.add(MemberParcel(member_id=member.id, parcel_id=parcel.id, is_invoice_address=True))
        await session.commit()
    run_id = await _make_run(client, year="2029")
    await client.post(f"/finances/runs/{run_id}/items", data={
        "order_number": "10", "name": "Fee", "description": "",
        "pricing_mode": "fixed_per_parcel", "unit_price": "1.00", "applies_to_all_parcels": "on",
    })
    await client.post(f"/finances/runs/{run_id}/finalize")
    async with AsyncSessionLocal() as session:
        invoice = (await session.execute(select(Invoice).where(Invoice.invoice_run_id == run_id))).scalar_one()
    assert invoice_copies(invoice)[0].names == "<b>Fett Name</b>"
    import io
    from pypdf import PdfReader
    pdf = (await client.get(f"/finances/invoices/{invoice.id}/pdf")).content
    assert "<b>Fett" in "".join(p.extract_text() for p in PdfReader(io.BytesIO(pdf)).pages)
