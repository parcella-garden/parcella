"""Finances dashboard."""
from fastapi import APIRouter
from datetime import date
from decimal import Decimal
from fastapi import Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models import (
    FinanceAccount,
    FinanceCategory,
    IncomingInvoice,
    Invoice,
    InvoiceItemTemplate,
    InvoiceRun,
)
from app.permissions import require_permission
from app.templating import templates

router = APIRouter()


# ---------------------------------------------------------------------------
# Dashboard (nav landing page) -- outstanding-balance summary and quick
# links into the module's sections, including Accounts (issue #156) as
# a card linking out, rather than getting its own nav entry.
# ---------------------------------------------------------------------------

@router.get("/", response_class=HTMLResponse)
async def finances_dashboard(request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_permission(request, db, "finances", "read")

    result = await db.execute(
        select(Invoice, InvoiceRun.due_date)
        .join(InvoiceRun, Invoice.invoice_run_id == InvoiceRun.id)
        .options(selectinload(Invoice.payments), selectinload(Invoice.reminders))
    )
    today = date.today()
    outstanding_total = Decimal("0")
    open_count = 0
    overdue_count = 0
    for invoice, due_date in result.all():
        if invoice.payment_status == "paid":
            continue
        open_count += 1
        outstanding_total += Decimal(str(invoice.subtotal)) - Decimal(str(invoice.paid_total))
        if due_date and due_date < today:
            overdue_count += 1

    run_count_result = await db.execute(select(InvoiceRun))
    run_count = len(run_count_result.scalars().all())

    category_count_result = await db.execute(select(FinanceCategory))
    category_count = len(category_count_result.scalars().all())

    item_template_count_result = await db.execute(select(InvoiceItemTemplate))
    item_template_count = len(item_template_count_result.scalars().all())

    account_count_result = await db.execute(select(FinanceAccount))
    account_count = len(account_count_result.scalars().all())

    incoming_invoice_count_result = await db.execute(select(IncomingInvoice))
    incoming_invoice_count = len(incoming_invoice_count_result.scalars().all())

    return templates.TemplateResponse(request, "finances/dashboard.html", {
        "request": request, "user": user,
        "run_count": run_count, "open_invoice_count": open_count,
        "overdue_count": overdue_count, "outstanding_total": outstanding_total,
        "category_count": category_count, "item_template_count": item_template_count,
        "account_count": account_count, "incoming_invoice_count": incoming_invoice_count,
    })
