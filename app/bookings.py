"""
A unified, filterable list of every invoice payment across the club
(issue #180) -- money actually received against an outgoing Invoice,
and money actually paid against an IncomingInvoice, combined into one
chronological list. Complements the per-account "bookings" view
(issue #174, app/services/finances.py's account_bookings_base) which
is scoped to one FinanceAccount and includes AccountTransaction rows;
this one is club-wide and scoped to invoice payments only.

AccountTransaction is deliberately excluded here too, same reasoning
as the cash-based accounting statement's ADR 0060: it has neither a
sender/recipient nor a category, so it doesn't fit this list's
sender/recipient/category/description shape any better than it fit
the statement's category breakdown.

Built entirely in Python rather than a SQL UNION ALL (contrast with
account_bookings_base in app/services/finances.py) because each payment can touch several
categories via its invoice's line items -- a one-to-many relationship
that doesn't collapse cleanly into one UNION'd row. Fine at the scale
a garden club actually operates at; revisit with a real pagination/
SQL-level approach if that assumption ever stops holding.
"""
from dataclasses import dataclass
from datetime import date
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import (
    FinanceCategory, IncomingInvoice, IncomingInvoiceLineItem, IncomingInvoicePayment,
    Invoice, InvoiceLineItem, InvoicePayment,
)


@dataclass
class BookingRow:
    id: str
    booking_date: date
    direction: str  # "income" | "expense"
    counterparty: str  # sender (expense) or recipient (income)
    categories: List[FinanceCategory]
    description: str
    amount: float
    detail_url: str


def _categories_and_description(line_items) -> tuple:
    categories = []
    seen_category_ids = set()
    description_parts = []
    for li in line_items:
        if li.category and li.category.id not in seen_category_ids:
            seen_category_ids.add(li.category.id)
            categories.append(li.category)
        text = getattr(li, "description", None) or getattr(li, "name", None)
        if text:
            description_parts.append(text)
    categories.sort(key=lambda c: c.code)
    return categories, ", ".join(description_parts)


async def list_bookings(
    db: AsyncSession, *,
    date_from: Optional[date] = None, date_to: Optional[date] = None,
    category_id: Optional[str] = None, search: str = "",
    amount_min: Optional[float] = None, amount_max: Optional[float] = None,
    direction: Optional[str] = None,
) -> List[BookingRow]:
    rows: List[BookingRow] = []

    if direction != "expense":
        income_query = select(InvoicePayment).options(
            selectinload(InvoicePayment.invoice).selectinload(Invoice.line_items).selectinload(InvoiceLineItem.category)
        )
        if date_from:
            income_query = income_query.where(InvoicePayment.paid_on >= date_from)
        if date_to:
            income_query = income_query.where(InvoicePayment.paid_on <= date_to)
        income_payments = (await db.execute(income_query)).scalars().all()
        for payment in income_payments:
            categories, description = _categories_and_description(payment.invoice.line_items)
            rows.append(BookingRow(
                id=f"income-{payment.id}", booking_date=payment.paid_on, direction="income",
                counterparty=payment.invoice.recipient_names, categories=categories,
                description=description, amount=float(payment.amount),
                detail_url=f"/finances/invoices/{payment.invoice_id}",
            ))

    if direction != "income":
        expense_query = select(IncomingInvoicePayment).options(
            selectinload(IncomingInvoicePayment.incoming_invoice)
            .selectinload(IncomingInvoice.line_items).selectinload(IncomingInvoiceLineItem.category)
        )
        if date_from:
            expense_query = expense_query.where(IncomingInvoicePayment.paid_on >= date_from)
        if date_to:
            expense_query = expense_query.where(IncomingInvoicePayment.paid_on <= date_to)
        expense_payments = (await db.execute(expense_query)).scalars().all()
        for payment in expense_payments:
            categories, description = _categories_and_description(payment.incoming_invoice.line_items)
            rows.append(BookingRow(
                id=f"expense-{payment.id}", booking_date=payment.paid_on, direction="expense",
                counterparty=payment.incoming_invoice.sender, categories=categories,
                description=description, amount=float(payment.amount),
                detail_url=f"/finances/incoming-invoices/{payment.incoming_invoice_id}",
            ))

    if category_id:
        rows = [r for r in rows if any(c.id == category_id for c in r.categories)]
    if search.strip():
        needle = search.strip().lower()
        rows = [r for r in rows if needle in r.counterparty.lower() or needle in r.description.lower()]
    if amount_min is not None:
        rows = [r for r in rows if r.amount >= amount_min]
    if amount_max is not None:
        rows = [r for r in rows if r.amount <= amount_max]

    rows.sort(key=lambda r: r.booking_date, reverse=True)
    return rows
