"""Finances: database helpers shared by the finances routes (issue #416).

No HTTP here -- no Request, no templates, no HTTPException. The routes in
app/routers/finances/ call these.
"""
from collections import Counter
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import String, cast, func, literal, or_, select, union_all
from sqlalchemy.orm import selectinload
from app.database import active_member_filter
from app.csv_utils import parse_mapped_csv_rows
from app.i18n import load_current_language
from app.models import (
    AccountTransaction,
    ClubSetting,
    IncomingInvoice,
    IncomingInvoicePayment,
    Invoice,
    InvoiceItemTemplate,
    InvoicePayment,
    Member,
    Parcel,
    ParcelStatus,
)
from app.branding import load_branding
from app.pdf_chrome import load_org_footer_context
from app.l10n import load_current_currency, load_current_region, parse_decimal


async def list_item_templates(db: AsyncSession) -> list:
    result = await db.execute(
        select(InvoiceItemTemplate)
        .options(
            selectinload(InvoiceItemTemplate.category),
            selectinload(InvoiceItemTemplate.parcel_scopes),
            selectinload(InvoiceItemTemplate.member_scopes),
        )
        .order_by(InvoiceItemTemplate.order_number)
    )
    return list(result.scalars().all())


async def list_active_parcels(db: AsyncSession) -> list:
    result = await db.execute(
        select(Parcel).where(Parcel.status == ParcelStatus.ACTIVE).order_by(Parcel.plot_number)
    )
    return list(result.scalars().all())


async def list_active_members(db: AsyncSession) -> list:
    result = await db.execute(
        select(Member).where(active_member_filter()).order_by(Member.last_name, Member.first_name)
    )
    return list(result.scalars().all())


async def pdf_context(db: AsyncSession) -> dict:
    """Everything render_invoice_pdf() needs beyond the invoice itself
    -- club branding, footer context (address/register/bank, now shared
    with every other PDF generator via app/pdf_chrome.py, not finances-
    specific), and formatting locale. Shared by the preview and the
    real/finalized PDF routes."""
    branding = await load_branding(db)
    logo_path = Path("app" + branding["logo_url"]) if branding["logo_url"] else None
    footer_context = await load_org_footer_context(db, branding["club_name"])

    return {
        "logo_path": logo_path,
        "footer_context": footer_context,
        "region": await load_current_region(db),
        "currency": await load_current_currency(db),
        "language": await load_current_language(db),
    }


INCOMING_INVOICES_FOLDER_SETTING = "incoming_invoices_cloud_folder"


async def get_incoming_invoices_folder(db: AsyncSession) -> Optional[str]:
    result = await db.execute(select(ClubSetting).where(ClubSetting.key == INCOMING_INVOICES_FOLDER_SETTING))
    entry = result.scalar_one_or_none()
    return entry.value if entry and entry.value else None


# ---------------------------------------------------------------------------
# Budget plan (issue #248, ADR 0113)
# ---------------------------------------------------------------------------

def budget_year(year: Optional[int]) -> int:
    """The planned year: next year unless another is asked for (kept to
    a sane range, it's only ever a calendar year)."""
    if year is None or not 2000 <= year <= 2100:
        return date.today().year + 1
    return year


# ---------------------------------------------------------------------------
# Delivery: email, cloud upload, print bundle (issue #58)
# ---------------------------------------------------------------------------

async def run_invoices(db: AsyncSession, run_id: str):
    result = await db.execute(
        select(Invoice)
        .options(selectinload(Invoice.line_items), selectinload(Invoice.parcel), selectinload(Invoice.member))
        .where(Invoice.invoice_run_id == run_id)
        .order_by(Invoice.invoice_number)
    )
    return list(result.scalars().all())


async def account_booking_counts(db: AsyncSession, account_id: Optional[str] = None) -> dict:
    """Bookings per account: generic/imported ones plus payments recorded
    against an invoice. Issue #353: an account with any of them can't be
    deleted -- AccountTransaction cascades with the account, so the whole
    ledger used to vanish."""
    counts: dict = {}
    for model, column in (
        (AccountTransaction, AccountTransaction.account_id),
        (InvoicePayment, InvoicePayment.account_id),
        (IncomingInvoicePayment, IncomingInvoicePayment.account_id),
    ):
        query = select(column, func.count()).where(column.is_not(None)).group_by(column)
        if account_id is not None:
            query = query.where(column == account_id)
        for key, count in (await db.execute(query)).all():
            counts[key] = counts.get(key, 0) + count
    return counts
ASSIGNED_SOURCES = ("invoice_payment", "incoming_invoice_payment")
UNASSIGNED_SOURCES = ("manual", "csv_import")


def account_bookings_base(account_id: str):
    payments_q = (
        select(
            InvoicePayment.id.label("id"),
            InvoicePayment.paid_on.label("booking_date"),
            InvoicePayment.amount.label("amount"),
            Invoice.invoice_number.label("reference"),
            InvoicePayment.note.label("description"),
            cast(literal("invoice_payment"), String(30)).label("source"),
            Invoice.recipient_names.label("counterparty"),
            Invoice.id.label("invoice_id"),
            cast(literal(None), String(36)).label("incoming_invoice_id"),
        )
        .join(Invoice, Invoice.id == InvoicePayment.invoice_id)
        .where(InvoicePayment.account_id == account_id)
    )
    incoming_payments_q = (
        select(
            IncomingInvoicePayment.id.label("id"),
            IncomingInvoicePayment.paid_on.label("booking_date"),
            (-IncomingInvoicePayment.amount).label("amount"),
            IncomingInvoice.invoice_number.label("reference"),
            IncomingInvoicePayment.note.label("description"),
            cast(literal("incoming_invoice_payment"), String(30)).label("source"),
            IncomingInvoice.sender.label("counterparty"),
            cast(literal(None), String(36)).label("invoice_id"),
            IncomingInvoice.id.label("incoming_invoice_id"),
        )
        .join(IncomingInvoice, IncomingInvoice.id == IncomingInvoicePayment.incoming_invoice_id)
        .where(IncomingInvoicePayment.account_id == account_id)
    )
    transactions_q = (
        select(
            AccountTransaction.id.label("id"),
            AccountTransaction.booking_date.label("booking_date"),
            AccountTransaction.amount.label("amount"),
            cast(literal(None), String(50)).label("reference"),
            AccountTransaction.description.label("description"),
            AccountTransaction.source.label("source"),
            AccountTransaction.counterparty.label("counterparty"),
            cast(literal(None), String(36)).label("invoice_id"),
            cast(literal(None), String(36)).label("incoming_invoice_id"),
        )
        .where(AccountTransaction.account_id == account_id)
    )
    return union_all(payments_q, incoming_payments_q, transactions_q).subquery("bookings")


def account_bookings_filtered(
    account_id: str, search: str, date_from: str, date_to: str,
    amount_min: str, amount_max: str, assigned: str = "",
):
    """Returns the filtered/searched (but not yet ordered, limited, or
    offset) bookings query -- shared by the HTML page, the JSON
    pagination endpoint, and the CSV export, so all three always agree
    on exactly which rows match the current filters. search also
    matches counterparty (issue #185: "I want to filter for this
    sender or recipient") -- there's no separate filter control for it,
    same free-text box already used for reference/description.
    assigned (issue #189) filters on whether a row is tied to an
    outgoing/incoming invoice at all, independent of how it got
    entered (which issue #184 already decided doesn't matter)."""
    bookings = account_bookings_base(account_id)
    query = select(bookings)

    if assigned == "yes":
        query = query.where(bookings.c.source.in_(ASSIGNED_SOURCES))
    elif assigned == "no":
        query = query.where(bookings.c.source.in_(UNASSIGNED_SOURCES))

    if search.strip():
        like = f"%{search.strip()}%"
        query = query.where(or_(
            bookings.c.reference.ilike(like), bookings.c.description.ilike(like),
            bookings.c.counterparty.ilike(like),
        ))
    if date_from.strip():
        parsed = parse_date_flexible(date_from)
        if parsed:
            query = query.where(bookings.c.booking_date >= parsed)
    if date_to.strip():
        parsed = parse_date_flexible(date_to)
        if parsed:
            query = query.where(bookings.c.booking_date <= parsed)
    if amount_min.strip():
        parsed = parse_decimal(amount_min)
        if parsed is not None:
            query = query.where(bookings.c.amount >= parsed)
    if amount_max.strip():
        parsed = parse_decimal(amount_max)
        if parsed is not None:
            query = query.where(bookings.c.amount <= parsed)

    return bookings, query


def parse_date_flexible(s: str):
    s = s.strip()
    for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d.%m.%y"):
        try:
            return date.fromisoformat(s) if fmt == "%Y-%m-%d" else datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def parse_finances_mapped_rows(csv_content_b64: str, delimiter: str, column_mapping: dict) -> list:
    """finances-specific finishing pass over app.csv_utils.parse_mapped_csv_rows'
    raw string values: parses date/amount and marks row validity."""
    raw_rows = parse_mapped_csv_rows(csv_content_b64, delimiter, column_mapping)
    parsed_rows = []
    for values in raw_rows:
        parsed_date = parse_date_flexible(values.get("date", ""))
        parsed_amount = parse_decimal(values.get("amount", ""))
        parsed_rows.append({
            "date": parsed_date, "amount": parsed_amount,
            "description": values.get("description", ""), "counterparty": values.get("counterparty", ""),
            "iban": values.get("iban", ""), "valid": parsed_date is not None and parsed_amount is not None,
        })
    return parsed_rows


# Issue #356: importing the same bank statement twice doubled every
# booking. A CSV row counts as already imported when the account already
# has a booking with the same date, signed amount and text -- generic
# bookings and payments recorded against an invoice alike (an incoming
# payment is +, a paid incoming invoice is -). Counted as a multiset: two
# identical rows in the file with one in the account means one is new.
BOOKING_TEXT_MAX = 255  # InvoicePayment.note / IncomingInvoicePayment.note


def booking_key(booking_date, amount, text) -> tuple:
    return (booking_date, Decimal(str(amount)).quantize(Decimal("0.01")), (text or "").strip()[:BOOKING_TEXT_MAX])


async def existing_booking_keys(db: AsyncSession, account_id: str) -> Counter:
    keys = Counter()
    for t in (await db.execute(select(AccountTransaction).where(AccountTransaction.account_id == account_id))).scalars():
        keys[booking_key(t.booking_date, t.amount, t.description)] += 1
    for p in (await db.execute(select(InvoicePayment).where(InvoicePayment.account_id == account_id))).scalars():
        keys[booking_key(p.paid_on, p.amount, p.note)] += 1
    for p in (await db.execute(select(IncomingInvoicePayment).where(IncomingInvoicePayment.account_id == account_id))).scalars():
        keys[booking_key(p.paid_on, -Decimal(str(p.amount)), p.note)] += 1
    return keys


def duplicate_flags(parsed_rows: list, existing: Counter) -> list:
    """One bool per row: True when that row is (as far as the account's
    bookings tell) already imported."""
    remaining = Counter(existing)
    flags = []
    for row in parsed_rows:
        key = booking_key(row["date"], row["amount"], row["description"]) if row["valid"] else None
        if key is not None and remaining[key] > 0:
            remaining[key] -= 1
            flags.append(True)
        else:
            flags.append(False)
    return flags


async def invoice_choice_settled(db: AsyncSession, match_choice: str) -> bool:
    """True when the row should become a payment for an invoice that has
    been fully paid in the meantime (issue #356: a stale import form
    recorded a second payment)."""
    if match_choice.startswith("invoice:"):
        invoice = (await db.execute(
            select(Invoice).options(selectinload(Invoice.payments), selectinload(Invoice.reminders))
            .where(Invoice.id == match_choice.removeprefix("invoice:"))
        )).scalar_one_or_none()
    elif match_choice.startswith("incoming_invoice:"):
        invoice = (await db.execute(
            select(IncomingInvoice).options(selectinload(IncomingInvoice.payments), selectinload(IncomingInvoice.line_items))
            .where(IncomingInvoice.id == match_choice.removeprefix("incoming_invoice:"))
        )).scalar_one_or_none()
    else:
        return False
    return invoice is not None and invoice.payment_status == "paid"


async def create_matched_or_generic_transaction(
    db: AsyncSession, account_id: str, user_id: str,
    parsed_date, parsed_amount: Decimal, description: str, counterparty: str, match_choice: str,
    source: str = "manual",
) -> bool:
    """Creates either a real InvoicePayment/IncomingInvoicePayment
    against the invoice named in match_choice ("invoice:<id>" /
    "incoming_invoice:<id>"), or a generic AccountTransaction when
    match_choice is "none"/unrecognized (issue #188). Returns True if
    a match was applied."""
    if match_choice.startswith("invoice:"):
        invoice_id = match_choice.removeprefix("invoice:")
        result = await db.execute(select(Invoice).where(Invoice.id == invoice_id))
        if result.scalar_one_or_none() is not None:
            db.add(InvoicePayment(
                invoice_id=invoice_id, amount=abs(parsed_amount), paid_on=parsed_date,
                note=description or None, account_id=account_id, recorded_by_id=user_id,
            ))
            return True
    elif match_choice.startswith("incoming_invoice:"):
        incoming_invoice_id = match_choice.removeprefix("incoming_invoice:")
        result = await db.execute(select(IncomingInvoice).where(IncomingInvoice.id == incoming_invoice_id))
        if result.scalar_one_or_none() is not None:
            db.add(IncomingInvoicePayment(
                incoming_invoice_id=incoming_invoice_id, amount=abs(parsed_amount), paid_on=parsed_date,
                note=description or None, account_id=account_id, recorded_by_id=user_id,
            ))
            return True

    db.add(AccountTransaction(
        account_id=account_id, booking_date=parsed_date, amount=parsed_amount,
        description=description or None, counterparty=counterparty or None,
        source=source, recorded_by_id=user_id,
    ))
    return False
