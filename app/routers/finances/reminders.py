"""Payment reminders."""
from fastapi import APIRouter
from datetime import date
from fastapi import Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.security_headers import content_disposition
from app.models import Invoice, InvoiceReminder, InvoiceRun
from app.permissions import require_permission
from app.l10n import parse_decimal
from app.invoice_pdf import invoice_copies, reminder_pdf_filename
from app.invoice_delivery import copies_to_print, deliver_reminder, render_reminder_copies_pdf
from app.templating import templates
from app.routers.finances._common import _get_invoice_or_404
from app.services.finances import pdf_context

router = APIRouter()


# ---------------------------------------------------------------------------
# Reminders (issue #59): a "don't let an unpaid invoice get forgotten"
# overview of overdue invoices, plus sending/tracking dunning
# reminders against them. Incoming invoices remains a placeholder
# (issue TBD).
# ---------------------------------------------------------------------------

@router.get("/reminders", response_class=HTMLResponse)
async def reminders_list(request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_permission(request, db, "finances", "read")

    result = await db.execute(
        select(Invoice, InvoiceRun.due_date)
        .join(InvoiceRun, Invoice.invoice_run_id == InvoiceRun.id)
        .options(
            selectinload(Invoice.parcel), selectinload(Invoice.member), selectinload(Invoice.payments), selectinload(Invoice.reminders),
        )
    )
    today = date.today()
    overdue = []
    for invoice, due_date in result.all():
        if invoice.payment_status == "paid" or not due_date or due_date >= today:
            continue
        overdue.append((invoice, due_date, (today - due_date).days))
    overdue.sort(key=lambda row: row[2], reverse=True)

    return templates.TemplateResponse(request, "finances/reminders_list.html", {
        "request": request, "user": user, "overdue": overdue,
    })


@router.post("/invoices/{invoice_id}/reminders")
async def reminder_create(
    invoice_id: str, request: Request,
    fee_amount: str = Form(""), message: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    user = await require_permission(request, db, "finances", "write")
    invoice = await _get_invoice_or_404(db, invoice_id)

    run_result = await db.execute(select(InvoiceRun).where(InvoiceRun.id == invoice.invoice_run_id))
    run = run_result.scalar_one_or_none()

    parsed_fee = parse_decimal(fee_amount) if fee_amount.strip() else None

    ctx = await pdf_context(db)
    await deliver_reminder(request, db, invoice, run, parsed_fee, message.strip(), user.id, ctx)
    await db.commit()
    return RedirectResponse(f"/finances/invoices/{invoice_id}?success=1", status_code=302)


@router.get("/reminders/{reminder_id}/pdf")
async def reminder_pdf(reminder_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    await require_permission(request, db, "finances", "read")

    result = await db.execute(select(InvoiceReminder).where(InvoiceReminder.id == reminder_id))
    reminder = result.scalar_one_or_none()
    if not reminder:
        raise HTTPException(status_code=404)

    invoice = await _get_invoice_or_404(db, reminder.invoice_id)
    run_result = await db.execute(select(InvoiceRun).where(InvoiceRun.id == invoice.invoice_run_id))
    run = run_result.scalar_one_or_none()

    ctx = await pdf_context(db)
    # Issue #396: the copies that need posting; if every copy reaches
    # someone by email, all of them (to look at or print anyway).
    copies = await copies_to_print(db, invoice) or invoice_copies(invoice)
    pdf_bytes = render_reminder_copies_pdf(reminder, invoice, run, ctx, copies)
    return Response(
        content=pdf_bytes, media_type="application/pdf",
        headers={"Content-Disposition": content_disposition(reminder_pdf_filename(reminder, invoice, run), "inline")},
    )
