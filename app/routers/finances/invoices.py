"""Invoices across all runs: list, detail, PDF, payments."""
from fastapi import APIRouter
from datetime import date, datetime
from fastapi import Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.i18n import t_for
from app.security_headers import content_disposition
from app.models import FinanceAccount, Invoice, InvoicePayment, InvoiceRun, Parcel
from app.permissions import require_permission
from app.l10n import parse_decimal
from app.invoice_pdf import invoice_pdf_filename
from app.invoice_delivery import render_all_copies_pdf, send_invoice_email
from app.templating import templates
from app.routers.finances._common import _get_invoice_or_404
from app.services.finances import pdf_context

router = APIRouter()


@router.get("/invoices/{invoice_id}/pdf")
async def invoice_pdf(invoice_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    await require_permission(request, db, "finances", "read")

    result = await db.execute(
        select(Invoice)
        .options(selectinload(Invoice.line_items), selectinload(Invoice.parcel), selectinload(Invoice.member))
        .where(Invoice.id == invoice_id)
    )
    invoice = result.scalar_one_or_none()
    if not invoice:
        raise HTTPException(status_code=404)

    run_result = await db.execute(select(InvoiceRun).where(InvoiceRun.id == invoice.invoice_run_id))
    run = run_result.scalar_one_or_none()

    ctx = await pdf_context(db)
    pdf_bytes = render_all_copies_pdf(invoice, run, ctx)
    return Response(
        content=pdf_bytes, media_type="application/pdf",
        headers={"Content-Disposition": content_disposition(invoice_pdf_filename(invoice, run), "inline")},
    )


@router.get("/invoices", response_class=HTMLResponse)
async def invoice_list(
    request: Request,
    parcel: str = "",
    invoice_number: str = "",
    recipient: str = "",
    amount_min: str = "",
    amount_max: str = "",
    status: str = "",
    db: AsyncSession = Depends(get_db),
):
    """Issue #190: search/filter outgoing invoices by invoice number,
    recipient, amount, and payment status. amount and status are still
    applied in Python after loading (payment_status is a computed
    property, not a column) -- same precedent status already used
    here before recipient/amount were added."""
    user = await require_permission(request, db, "finances", "read")

    query = (
        select(Invoice)
        .options(selectinload(Invoice.parcel), selectinload(Invoice.member), selectinload(Invoice.payments), selectinload(Invoice.reminders))
        .outerjoin(Parcel, Invoice.parcel_id == Parcel.id)
        .order_by(Invoice.invoice_number.desc())
    )
    if parcel.strip():
        query = query.where(Parcel.plot_number.ilike(f"%{parcel.strip()}%"))
    if invoice_number.strip():
        query = query.where(Invoice.invoice_number.ilike(f"%{invoice_number.strip()}%"))
    if recipient.strip():
        query = query.where(Invoice.recipient_names.ilike(f"%{recipient.strip()}%"))
    parsed_amount_min = parse_decimal(amount_min) if amount_min.strip() else None
    if parsed_amount_min is not None:
        query = query.where(Invoice.subtotal >= parsed_amount_min)
    parsed_amount_max = parse_decimal(amount_max) if amount_max.strip() else None
    if parsed_amount_max is not None:
        query = query.where(Invoice.subtotal <= parsed_amount_max)

    result = await db.execute(query)
    invoices = list(result.scalars().all())
    if status in ("open", "partially_paid", "paid"):
        invoices = [i for i in invoices if i.payment_status == status]

    return templates.TemplateResponse(request, "finances/invoice_list.html", {
        "request": request, "user": user, "invoices": invoices,
        "filter_parcel": parcel, "filter_invoice_number": invoice_number, "filter_recipient": recipient,
        "filter_amount_min": amount_min, "filter_amount_max": amount_max, "filter_status": status,
    })


@router.get("/invoices/{invoice_id}", response_class=HTMLResponse)
async def invoice_detail(invoice_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_permission(request, db, "finances", "read")
    invoice = await _get_invoice_or_404(db, invoice_id)

    run_result = await db.execute(select(InvoiceRun).where(InvoiceRun.id == invoice.invoice_run_id))
    run = run_result.scalar_one_or_none()

    accounts_result = await db.execute(
        select(FinanceAccount).where(FinanceAccount.is_active == True).order_by(FinanceAccount.name)  # noqa: E712
    )
    accounts = list(accounts_result.scalars().all())

    return templates.TemplateResponse(request, "finances/invoice_detail.html", {
        "request": request, "user": user, "invoice": invoice, "run": run,
        "today": date.today().isoformat(), "accounts": accounts,
    })


@router.post("/invoices/{invoice_id}/resend-email")
async def invoice_resend_email(invoice_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    await require_permission(request, db, "finances", "write")
    invoice = await _get_invoice_or_404(db, invoice_id)

    run_result = await db.execute(select(InvoiceRun).where(InvoiceRun.id == invoice.invoice_run_id))
    run = run_result.scalar_one_or_none()

    ctx = await pdf_context(db)
    sent = await send_invoice_email(request, db, invoice, run, ctx)
    await db.commit()

    if sent:
        return RedirectResponse(f"/finances/invoices/{invoice_id}?success=1", status_code=302)
    return RedirectResponse(
        f"/finances/invoices/{invoice_id}?error={t_for(request, 'finances.errors.no_email_recipient')}",
        status_code=302,
    )


@router.post("/invoices/{invoice_id}/payments")
async def payment_create(
    invoice_id: str, request: Request,
    amount: str = Form(...), paid_on: str = Form(...), note: str = Form(""),
    account_id: str = Form(""),
    from_run: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    """Issue #173: also reachable from a run's own invoice list
    (/finances/runs/{run_id}), not just an invoice's own detail page --
    from_run, when present, sends the admin back there instead, so they
    can record payments for several invoices in one run without
    re-navigating each time. Built from a plain id (never an arbitrary
    URL) to avoid an open-redirect; a bogus id just 404s on the next
    request, same as visiting a wrong URL directly."""
    user = await require_permission(request, db, "finances", "write")
    await _get_invoice_or_404(db, invoice_id)

    parsed_amount = parse_decimal(amount)
    if parsed_amount is None:
        raise HTTPException(status_code=400)

    db.add(InvoicePayment(
        invoice_id=invoice_id, amount=parsed_amount,
        paid_on=datetime.strptime(paid_on, "%Y-%m-%d").date(),
        note=note.strip() or None, recorded_by_id=user.id,
        account_id=account_id.strip() or None,
    ))
    await db.commit()
    if from_run.strip():
        return RedirectResponse(f"/finances/runs/{from_run.strip()}", status_code=302)
    return RedirectResponse(f"/finances/invoices/{invoice_id}", status_code=302)


@router.post("/invoices/{invoice_id}/payments/{payment_id}/delete")
async def payment_delete(
    invoice_id: str, payment_id: str, request: Request,
    from_run: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    await require_permission(request, db, "finances", "delete")

    result = await db.execute(
        select(InvoicePayment).where(InvoicePayment.id == payment_id, InvoicePayment.invoice_id == invoice_id)
    )
    payment = result.scalar_one_or_none()
    if payment:
        await db.delete(payment)
        await db.commit()
    if from_run.strip():
        return RedirectResponse(f"/finances/runs/{from_run.strip()}", status_code=302)
    return RedirectResponse(f"/finances/invoices/{invoice_id}", status_code=302)
