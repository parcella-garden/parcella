"""
Finances module router: annual invoices (issues #55/#56/#57/#58),
bookkeeping categories (issue #67).

Phase 1 (#56): creating an InvoiceRun and configuring its
InvoiceItemDefinitions. Phase 2 (#57): preview (renders a PDF from
app.invoice_generation's in-memory computation, no DB writes) and
finalize (persists real Invoice/InvoiceLineItem rows with permanent
numbers -- see app/invoice_generation.py's module docstring for why
this is a one-way action). Phase 3 (#58): delivery (email with the PDF
attached, upload to the parcel's cloud folder, a merged print bundle
for anyone not reachable by email -- see app/invoice_delivery.py) and
payment tracking across every finalized run. Categories (#67): optional
bookkeeping codes an item definition can be tagged with, manageable by
hand or via CSV import -- see FinanceCategory's docstring in
app/models.py for why this app doesn't ship real SKR42 codes itself.
Accounts (#156): a club's real bank/cash accounts, a reporting tag on
InvoicePayment with the same "no effect on invoice generation" role as
categories -- see FinanceAccount's docstring.
"""
import base64
import csv
import io
import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Optional
from itertools import zip_longest
from urllib.parse import quote as urlquote

from fastapi import APIRouter, Request, Form, Depends, HTTPException, UploadFile, File, Query
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, union_all, literal, or_, and_, cast, String
from sqlalchemy.orm import selectinload

from app.database import get_db, active_member_filter
from app.csv_utils import (
    csv_safe,
    decode_csv_upload,
    sniff_csv_delimiter,
    guess_column_mapping,
    parse_column_mapping,
    parse_mapped_csv_rows,
)
from app.i18n import t_for, load_current_language
from app.models import (
    InvoiceRun, InvoiceRunStatus, InvoiceItemDefinition, InvoiceItemDefinitionParcel, InvoiceItemDefinitionMember,
    InvoiceItemTemplate, InvoiceItemTemplateParcel, InvoiceItemTemplateMember,
    InvoicePricingMode, Invoice, InvoicePayment, InvoiceReminder, Parcel, ParcelStatus, Member,
    FinanceCategory, FinanceCategoryGroup, FinanceAccount, FinanceAccountType, AccountTransaction,
    IncomingInvoice, IncomingInvoiceLineItem, IncomingInvoicePayment, ClubSetting,
)
from app.auth import require_admin
from app.permissions import require_permission
from app.module_flags import require_module
from app.branding import load_branding
from app.pdf_chrome import load_org_footer_context
from app.l10n import load_current_region, load_current_currency
from app.cloud_storage import get_nextcloud_provider, CloudStorageError
from app.invoice_generation import compute_invoices_for_run, finalize_run, SequenceCollisionError
from app.invoice_pdf import (
    InvoicePdfData, InvoicePdfLineItem, render_invoice_pdf, invoice_pdf_data_from_invoice, invoice_pdf_filename,
    reminder_pdf_data_from_reminder, render_reminder_pdf, reminder_pdf_filename,
)
from app.invoice_delivery import (
    send_invoice_email, upload_invoice_to_cloud, build_print_bundle, deliver_reminder, invoice_has_email_recipient,
)
from app.accounting_statement import compute_cash_accounting_statement, available_statement_years
from app.accounting_statement_pdf import render_accounting_statement_pdf
from app.bookings import list_bookings
from app.invoice_matching import find_matching_invoices, best_match_option

router = APIRouter(
    prefix="/finances",
    tags=["finances"],
    dependencies=[Depends(require_module("finances"))],
)
from app.templating import templates


def _parse_decimal(value: str) -> Optional[Decimal]:
    value = (value or "").strip().replace(",", ".")
    if not value:
        return None
    try:
        return Decimal(value)
    except InvalidOperation:
        return None


# Pricing modes computed entirely from another module -- unit_price is
# never stored for these (INSURANCE_COST/WORK_HOURS_SHORTFALL pull
# their amount from the insurance/work-hours modules;
# WATER_USAGE/ELECTRICITY_USAGE pull their price from
# MeteringPriceConfiguration, per medium/year -- see
# app/invoice_generation.py's item_quantity_and_price).
_AUTOMATIC_PRICING_MODES = (
    InvoicePricingMode.INSURANCE_COST, InvoicePricingMode.WORK_HOURS_SHORTFALL,
    InvoicePricingMode.WATER_USAGE, InvoicePricingMode.ELECTRICITY_USAGE,
)


def _dedupe_ids(ids: list[str]) -> list[str]:
    """De-duplicates a submitted scope-picker id list while preserving
    order. A resubmitted/retried form (e.g. after a network hiccup, or
    a double form-resubmission on browser back/forward) can otherwise
    include the same parcel/member id twice, which crashes the
    subsequent INSERT with a UniqueViolationError on the
    (definition_id, parcel_id)/(definition_id, member_id) constraint --
    found via a real 500 on /finances/item-templates."""
    return list(dict.fromkeys(ids))


async def _get_run_or_404(db: AsyncSession, run_id: str) -> InvoiceRun:
    result = await db.execute(
        select(InvoiceRun)
        .options(
            selectinload(InvoiceRun.item_definitions).selectinload(InvoiceItemDefinition.parcel_scopes),
            selectinload(InvoiceRun.item_definitions).selectinload(InvoiceItemDefinition.member_scopes),
            selectinload(InvoiceRun.item_definitions).selectinload(InvoiceItemDefinition.category),
        )
        .where(InvoiceRun.id == run_id)
    )
    run = result.scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=404)
    return run


async def _item_templates(db: AsyncSession) -> list:
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


async def _active_parcels(db: AsyncSession) -> list:
    result = await db.execute(
        select(Parcel).where(Parcel.status == ParcelStatus.ACTIVE).order_by(Parcel.plot_number)
    )
    return list(result.scalars().all())


async def _active_members(db: AsyncSession) -> list:
    result = await db.execute(
        select(Member).where(active_member_filter()).order_by(Member.last_name, Member.first_name)
    )
    return list(result.scalars().all())


async def _pdf_context(db: AsyncSession) -> dict:
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

    return templates.TemplateResponse("finances/dashboard.html", {
        "request": request, "user": user,
        "run_count": run_count, "open_invoice_count": open_count,
        "overdue_count": overdue_count, "outstanding_total": outstanding_total,
        "category_count": category_count, "item_template_count": item_template_count,
        "account_count": account_count, "incoming_invoice_count": incoming_invoice_count,
    })


# ---------------------------------------------------------------------------
# Invoice runs: list, create
# ---------------------------------------------------------------------------

@router.get("/runs", response_class=HTMLResponse)
async def run_list(request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_permission(request, db, "finances", "read")

    result = await db.execute(
        select(InvoiceRun)
        .options(selectinload(InvoiceRun.item_definitions))
        .order_by(InvoiceRun.year.desc())
    )
    runs = list(result.scalars().all())

    return templates.TemplateResponse("finances/run_list.html", {
        "request": request, "user": user, "runs": runs,
        "today": date.today().isoformat(),
        "current_year": date.today().year,
    })


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

    return templates.TemplateResponse("finances/reminders_list.html", {
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

    parsed_fee = _parse_decimal(fee_amount) if fee_amount.strip() else None

    ctx = await _pdf_context(db)
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

    ctx = await _pdf_context(db)
    data = reminder_pdf_data_from_reminder(reminder, invoice, run)
    pdf_bytes = render_reminder_pdf(data, **ctx)
    return Response(
        content=pdf_bytes, media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{reminder_pdf_filename(reminder, invoice, run)}"'},
    )


INCOMING_INVOICES_FOLDER_SETTING = "incoming_invoices_cloud_folder"


def _cloud_storage_enabled(request: Request) -> bool:
    module_flags = getattr(request.state, "module_flags", {})
    return bool(module_flags.get("cloud_storage")) and getattr(request.state, "is_full_access", False)


async def _get_incoming_invoices_folder(db: AsyncSession) -> Optional[str]:
    result = await db.execute(select(ClubSetting).where(ClubSetting.key == INCOMING_INVOICES_FOLDER_SETTING))
    entry = result.scalar_one_or_none()
    return entry.value if entry and entry.value else None


@router.get("/incoming-invoices", response_class=HTMLResponse)
async def incoming_invoices_list(
    request: Request,
    invoice_number: str = "", sender: str = "", amount_min: str = "", amount_max: str = "", status: str = "",
    db: AsyncSession = Depends(get_db),
):
    """Issue #190: search/filter incoming invoices by invoice number,
    sender, amount, and payment status. amount and status are applied
    in Python after loading, same as the outgoing invoice list --
    total_amount/payment_status are computed properties, not columns."""
    user = await require_permission(request, db, "finances", "read")

    query = (
        select(IncomingInvoice)
        .options(
            selectinload(IncomingInvoice.line_items).selectinload(IncomingInvoiceLineItem.category),
            selectinload(IncomingInvoice.payments),
        )
        .order_by(IncomingInvoice.invoice_date.desc(), IncomingInvoice.created_at.desc())
    )
    if invoice_number.strip():
        query = query.where(IncomingInvoice.invoice_number.ilike(f"%{invoice_number.strip()}%"))
    if sender.strip():
        query = query.where(IncomingInvoice.sender.ilike(f"%{sender.strip()}%"))

    result = await db.execute(query)
    invoices = list(result.scalars().all())

    parsed_amount_min = _parse_decimal(amount_min) if amount_min.strip() else None
    if parsed_amount_min is not None:
        invoices = [i for i in invoices if i.total_amount >= float(parsed_amount_min)]
    parsed_amount_max = _parse_decimal(amount_max) if amount_max.strip() else None
    if parsed_amount_max is not None:
        invoices = [i for i in invoices if i.total_amount <= float(parsed_amount_max)]
    if status in ("open", "partially_paid", "paid"):
        invoices = [i for i in invoices if i.payment_status == status]

    categories_result = await db.execute(select(FinanceCategory).order_by(FinanceCategory.code))
    categories = list(categories_result.scalars().all())

    cloud_storage_enabled = _cloud_storage_enabled(request)
    folder_path = await _get_incoming_invoices_folder(db) if cloud_storage_enabled else None

    return templates.TemplateResponse("finances/incoming_invoices_list.html", {
        "request": request, "user": user, "invoices": invoices, "categories": categories,
        "cloud_storage_enabled": cloud_storage_enabled, "folder_path": folder_path,
        "today": date.today().isoformat(),
        "filter_invoice_number": invoice_number, "filter_sender": sender,
        "filter_amount_min": amount_min, "filter_amount_max": amount_max, "filter_status": status,
    })


@router.post("/incoming-invoices")
async def incoming_invoice_create(
    request: Request,
    sender: str = Form(...), invoice_number: str = Form(""), invoice_date: str = Form(...), note: str = Form(""),
    category_id: list[str] = Form([]), description: list[str] = Form([]), amount: list[str] = Form([]),
    file: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
):
    """One or more (category_id, description, amount) positions,
    submitted as same-named repeated fields (issue #178: "there might
    be more than one position with different categories/amounts") --
    paired up by index, same convention as the scope-picker lists
    elsewhere in this router."""
    user = await require_permission(request, db, "finances", "write")

    parsed_date = _parse_date_flexible(invoice_date)
    if parsed_date is None or not sender.strip():
        raise HTTPException(status_code=400)

    invoice = IncomingInvoice(
        sender=sender.strip(), invoice_number=invoice_number.strip() or None,
        invoice_date=parsed_date, note=note.strip() or None, created_by_id=user.id,
    )
    db.add(invoice)
    await db.flush()

    for cat_id, desc, amt in zip_longest(category_id, description, amount, fillvalue=""):
        parsed_amount = _parse_decimal(amt)
        if parsed_amount is None:
            continue
        db.add(IncomingInvoiceLineItem(
            incoming_invoice_id=invoice.id, category_id=cat_id.strip() or None,
            description=desc.strip() or None, amount=parsed_amount,
        ))

    if file is not None and file.filename and _cloud_storage_enabled(request):
        folder_path = await _get_incoming_invoices_folder(db)
        if folder_path:
            provider = await get_nextcloud_provider(db)
            if provider is not None:
                try:
                    content = await file.read()
                    stored_filename = f"{invoice.id}_{file.filename}"
                    await provider.upload_file(folder_path, stored_filename, content)
                    invoice.cloud_filename = stored_filename
                except CloudStorageError as e:
                    await db.commit()
                    message = urlquote(str(e))
                    return RedirectResponse(f"/finances/incoming-invoices?cloud_error={message}", status_code=303)
                finally:
                    await provider.aclose()

    await db.commit()
    return RedirectResponse("/finances/incoming-invoices?success=1", status_code=302)


@router.get("/incoming-invoices/{invoice_id}", response_class=HTMLResponse)
async def incoming_invoice_detail(invoice_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_permission(request, db, "finances", "read")

    result = await db.execute(
        select(IncomingInvoice)
        .options(
            selectinload(IncomingInvoice.line_items).selectinload(IncomingInvoiceLineItem.category),
            selectinload(IncomingInvoice.payments).selectinload(IncomingInvoicePayment.account),
        )
        .where(IncomingInvoice.id == invoice_id)
    )
    invoice = result.scalar_one_or_none()
    if not invoice:
        raise HTTPException(status_code=404)

    accounts_result = await db.execute(
        select(FinanceAccount).where(FinanceAccount.is_active == True).order_by(FinanceAccount.name)  # noqa: E712
    )
    accounts = list(accounts_result.scalars().all())

    return templates.TemplateResponse("finances/incoming_invoice_detail.html", {
        "request": request, "user": user, "invoice": invoice, "accounts": accounts,
        "cloud_storage_enabled": _cloud_storage_enabled(request),
        "today": date.today().isoformat(),
    })


@router.post("/incoming-invoices/{invoice_id}/delete")
async def incoming_invoice_delete(invoice_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    """Deletes the DB record only -- an attachment already uploaded to
    the shared cloud folder is left in place, same principle as
    deleting a FinanceAccount never reaching into Nextcloud to remove
    files (this app's own data is not the source of truth for media)."""
    await require_permission(request, db, "finances", "delete")

    result = await db.execute(select(IncomingInvoice).where(IncomingInvoice.id == invoice_id))
    invoice = result.scalar_one_or_none()
    if invoice:
        await db.delete(invoice)
        await db.commit()
    return RedirectResponse("/finances/incoming-invoices?deleted=1", status_code=302)


@router.post("/incoming-invoices/{invoice_id}/payments")
async def incoming_invoice_payment_create(
    invoice_id: str, request: Request,
    amount: str = Form(...), paid_on: str = Form(...), note: str = Form(""),
    account_id: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    """Issue #181: "could be the same method as in outgoing invoices" --
    same fields/route shape as POST /invoices/{id}/payments, just
    without a from_run redirect target since incoming invoices have no
    run grouping to return to."""
    user = await require_permission(request, db, "finances", "write")

    result = await db.execute(select(IncomingInvoice).where(IncomingInvoice.id == invoice_id))
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404)

    parsed_amount = _parse_decimal(amount)
    if parsed_amount is None:
        raise HTTPException(status_code=400)

    db.add(IncomingInvoicePayment(
        incoming_invoice_id=invoice_id, amount=parsed_amount,
        paid_on=datetime.strptime(paid_on, "%Y-%m-%d").date(),
        note=note.strip() or None, recorded_by_id=user.id,
        account_id=account_id.strip() or None,
    ))
    await db.commit()
    return RedirectResponse(f"/finances/incoming-invoices/{invoice_id}", status_code=302)


@router.post("/incoming-invoices/{invoice_id}/payments/{payment_id}/delete")
async def incoming_invoice_payment_delete(
    invoice_id: str, payment_id: str, request: Request, db: AsyncSession = Depends(get_db),
):
    await require_permission(request, db, "finances", "delete")

    result = await db.execute(
        select(IncomingInvoicePayment).where(
            IncomingInvoicePayment.id == payment_id, IncomingInvoicePayment.incoming_invoice_id == invoice_id,
        )
    )
    payment = result.scalar_one_or_none()
    if payment:
        await db.delete(payment)
        await db.commit()
    return RedirectResponse(f"/finances/incoming-invoices/{invoice_id}", status_code=302)


@router.get(
    "/incoming-invoices/{invoice_id}/download",
    dependencies=[Depends(require_module("cloud_storage"))],
)
async def incoming_invoice_download(invoice_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    await require_admin(request, db)

    result = await db.execute(select(IncomingInvoice).where(IncomingInvoice.id == invoice_id))
    invoice = result.scalar_one_or_none()
    if not invoice or not invoice.cloud_filename:
        raise HTTPException(status_code=404)

    folder_path = await _get_incoming_invoices_folder(db)
    if not folder_path:
        raise HTTPException(status_code=400, detail=t_for(request, "finances.incoming_invoices.cloud_not_configured"))

    provider = await get_nextcloud_provider(db)
    if provider is None:
        raise HTTPException(status_code=400, detail=t_for(request, "finances.incoming_invoices.cloud_not_configured"))

    try:
        content = await provider.download_file(folder_path, invoice.cloud_filename)
    except CloudStorageError as e:
        raise HTTPException(status_code=502, detail=str(e))
    finally:
        await provider.aclose()

    return Response(
        content=content, media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{invoice.cloud_filename}"'},
    )


@router.get("/accounting-statement", response_class=HTMLResponse)
async def accounting_statement_page(
    request: Request, year: Optional[int] = Query(None), db: AsyncSession = Depends(get_db),
):
    user = await require_permission(request, db, "finances", "read")

    available_years = await available_statement_years(db)
    target_year = year if year in available_years else (available_years[0] if available_years else date.today().year)

    statement = await compute_cash_accounting_statement(db, target_year)

    return templates.TemplateResponse("finances/accounting_statement.html", {
        "request": request, "user": user, "statement": statement,
        "available_years": available_years, "year": target_year,
    })


@router.get("/accounting-statement/pdf")
async def accounting_statement_pdf(
    request: Request, year: int = Query(...), db: AsyncSession = Depends(get_db),
):
    await require_permission(request, db, "finances", "read")

    statement = await compute_cash_accounting_statement(db, year)
    ctx = await _pdf_context(db)
    pdf_bytes = render_accounting_statement_pdf(statement, **ctx)

    return Response(
        content=pdf_bytes, media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="accounting_statement_{year}.pdf"'},
    )


@router.get("/bookings", response_class=HTMLResponse)
async def bookings_list(request: Request, db: AsyncSession = Depends(get_db)):
    """Issue #180: every invoice payment across the club (incoming and
    outgoing), sorted by date descending, filterable by time frame,
    counterparty, category, description/amount -- see app/bookings.py
    for why this is club-wide rather than the per-account bookings
    list from issue #174."""
    user = await require_permission(request, db, "finances", "read")

    q = request.query_params
    search = q.get("search", "")
    date_from_str = q.get("date_from", "")
    date_to_str = q.get("date_to", "")
    amount_min_str = q.get("amount_min", "")
    amount_max_str = q.get("amount_max", "")
    direction = q.get("direction", "")
    category_id = q.get("category_id", "")

    rows = await list_bookings(
        db,
        date_from=_parse_date_flexible(date_from_str) if date_from_str.strip() else None,
        date_to=_parse_date_flexible(date_to_str) if date_to_str.strip() else None,
        category_id=category_id.strip() or None,
        search=search,
        amount_min=float(_parse_decimal(amount_min_str)) if amount_min_str.strip() and _parse_decimal(amount_min_str) is not None else None,
        amount_max=float(_parse_decimal(amount_max_str)) if amount_max_str.strip() and _parse_decimal(amount_max_str) is not None else None,
        direction=direction.strip() or None,
    )

    categories_result = await db.execute(select(FinanceCategory).order_by(FinanceCategory.code))
    categories = list(categories_result.scalars().all())

    return templates.TemplateResponse("finances/bookings_list.html", {
        "request": request, "user": user, "rows": rows, "categories": categories,
        "search": search, "date_from": date_from_str, "date_to": date_to_str,
        "amount_min": amount_min_str, "amount_max": amount_max_str,
        "direction": direction, "category_id": category_id,
    })


@router.post("/runs")
async def run_create(
    request: Request,
    year: int = Form(...),
    subject: str = Form(...),
    issued_date: str = Form(...),
    due_date: str = Form(...),
    footer_text: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    user = await require_permission(request, db, "finances", "write")

    run = InvoiceRun(
        year=year,
        subject=subject.strip(),
        issued_date=datetime.strptime(issued_date, "%Y-%m-%d").date(),
        due_date=datetime.strptime(due_date, "%Y-%m-%d").date(),
        footer_text=footer_text.strip() or None,
        created_by_id=user.id,
    )
    db.add(run)
    await db.commit()
    return RedirectResponse(f"/finances/runs/{run.id}", status_code=302)


@router.post("/runs/{run_id}/delete")
async def run_delete(run_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    await require_permission(request, db, "finances", "delete")

    run = await _get_run_or_404(db, run_id)
    if run.status != InvoiceRunStatus.DRAFT:
        return RedirectResponse(
            f"/finances/runs?error={t_for(request, 'finances.errors.cannot_delete_finalized_run')}",
            status_code=302,
        )
    await db.delete(run)
    await db.commit()
    return RedirectResponse("/finances/runs?success=1", status_code=302)


# ---------------------------------------------------------------------------
# Invoice run detail: item definitions
# ---------------------------------------------------------------------------

@router.get("/runs/{run_id}", response_class=HTMLResponse)
async def run_detail(
    run_id: str, request: Request,
    invoice_number: str = "", recipient: str = "", parcel: str = "",
    amount_min: str = "", amount_max: str = "", status: str = "",
    db: AsyncSession = Depends(get_db),
):
    """Issue #190 follow-up: the flat /finances/invoices list got
    search/filter, but a single run's own invoice table (which can
    still run to one row per parcel) had none at all -- same fields,
    scoped to this run."""
    user = await require_permission(request, db, "finances", "read")

    run = await _get_run_or_404(db, run_id)
    parcels = await _active_parcels(db)
    members = await _active_members(db)

    next_order = (max((i.order_number for i in run.item_definitions), default=0) + 10)

    invoices = []
    accounts = []
    if run.status == InvoiceRunStatus.FINALIZED:
        query = (
            select(Invoice)
            .options(
                selectinload(Invoice.parcel), selectinload(Invoice.member),
                selectinload(Invoice.payments).selectinload(InvoicePayment.account),
                selectinload(Invoice.reminders),
            )
            .outerjoin(Parcel, Invoice.parcel_id == Parcel.id)
            .where(Invoice.invoice_run_id == run.id)
            .order_by(Invoice.invoice_number)
        )
        if invoice_number.strip():
            query = query.where(Invoice.invoice_number.ilike(f"%{invoice_number.strip()}%"))
        if recipient.strip():
            query = query.where(Invoice.recipient_names.ilike(f"%{recipient.strip()}%"))
        if parcel.strip():
            query = query.where(Parcel.plot_number.ilike(f"%{parcel.strip()}%"))
        parsed_amount_min = _parse_decimal(amount_min) if amount_min.strip() else None
        if parsed_amount_min is not None:
            query = query.where(Invoice.subtotal >= parsed_amount_min)
        parsed_amount_max = _parse_decimal(amount_max) if amount_max.strip() else None
        if parsed_amount_max is not None:
            query = query.where(Invoice.subtotal <= parsed_amount_max)

        result = await db.execute(query)
        invoices = list(result.scalars().all())
        if status in ("open", "partially_paid", "paid"):
            invoices = [i for i in invoices if i.payment_status == status]

        accounts_result = await db.execute(
            select(FinanceAccount).where(FinanceAccount.is_active == True).order_by(FinanceAccount.name)  # noqa: E712
        )
        accounts = list(accounts_result.scalars().all())

    item_templates = []
    catalog_all_used = False
    if run.status == InvoiceRunStatus.DRAFT:
        all_item_templates = await _item_templates(db)
        # Issue #94: don't offer a catalog item the run already has --
        # matched by name, since applying a template copies its fields
        # onto a brand new InvoiceItemDefinition with no stored link
        # back to the template it came from (see items_add_from_catalog).
        # Recomputed fresh on every load, so renaming/deleting an item
        # directly on the run makes its template reappear here again.
        used_names = {d.name for d in run.item_definitions}
        item_templates = [t for t in all_item_templates if t.name not in used_names]
        catalog_all_used = bool(all_item_templates) and not item_templates

    categories_result = await db.execute(select(FinanceCategory).order_by(FinanceCategory.code))
    categories = list(categories_result.scalars().all())

    return templates.TemplateResponse("finances/run_detail.html", {
        "request": request, "user": user, "run": run, "parcels": parcels, "members": members,
        "pricing_modes": list(InvoicePricingMode),
        "next_order": next_order,
        "invoices": invoices,
        "accounts": accounts,
        "today": date.today().isoformat(),
        "item_templates": item_templates,
        "catalog_all_used": catalog_all_used,
        "categories": categories,
        "filter_invoice_number": invoice_number, "filter_recipient": recipient, "filter_parcel": parcel,
        "filter_amount_min": amount_min, "filter_amount_max": amount_max, "filter_status": status,
    })


@router.post("/runs/{run_id}/items")
async def item_create(
    run_id: str,
    request: Request,
    order_number: int = Form(0),
    name: str = Form(...),
    description: str = Form(""),
    pricing_mode: str = Form(...),
    unit_price: str = Form(""),
    applies_to_all_parcels: str = Form(""),
    applies_to_all_members: str = Form(""),
    parcel_ids: list[str] = Form([]),
    member_ids: list[str] = Form([]),
    category_id: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    await require_permission(request, db, "finances", "write")

    run = await _get_run_or_404(db, run_id)
    if run.status != InvoiceRunStatus.DRAFT:
        raise HTTPException(status_code=400, detail=t_for(request, "finances.errors.run_not_draft"))

    try:
        mode = InvoicePricingMode(pricing_mode)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid pricing_mode")

    applies_all_parcels = applies_to_all_parcels == "on"
    applies_all_members = applies_to_all_members == "on"
    item = InvoiceItemDefinition(
        invoice_run_id=run.id,
        order_number=order_number,
        name=name.strip(),
        description=description.strip() or None,
        pricing_mode=mode,
        unit_price=_parse_decimal(unit_price) if mode not in _AUTOMATIC_PRICING_MODES else None,
        applies_to_all_parcels=applies_all_parcels,
        applies_to_all_members=applies_all_members,
        category_id=category_id.strip() or None,
    )
    db.add(item)
    await db.flush()

    if not applies_all_parcels:
        for parcel_id in _dedupe_ids(parcel_ids):
            db.add(InvoiceItemDefinitionParcel(invoice_item_definition_id=item.id, parcel_id=parcel_id))
    if not applies_all_members:
        for member_id in _dedupe_ids(member_ids):
            db.add(InvoiceItemDefinitionMember(invoice_item_definition_id=item.id, member_id=member_id))

    await db.commit()
    return RedirectResponse(f"/finances/runs/{run_id}", status_code=302)


@router.post("/runs/{run_id}/items/add-from-catalog")
async def items_add_from_catalog(
    run_id: str,
    request: Request,
    template_ids: list[str] = Form([]),
    db: AsyncSession = Depends(get_db),
):
    """Adds one InvoiceItemDefinition per selected InvoiceItemTemplate
    to `run_id` -- the visible, curated replacement for the old "copy
    items from another run" mechanism (issue #66), so a board member
    picks known-good recurring items by name/price instead of blindly
    duplicating everything from a specific past run (which may have
    included one-off items). Inherits the template's own scope
    verbatim, including specific parcel_scopes/member_scopes -- itself
    still freely editable afterward on the new item, same as the
    template. Adds to whatever's already on the target run rather than
    replacing it."""
    await require_permission(request, db, "finances", "write")

    run = await _get_run_or_404(db, run_id)
    if run.status != InvoiceRunStatus.DRAFT:
        raise HTTPException(status_code=400, detail=t_for(request, "finances.errors.run_not_draft"))

    if template_ids:
        result = await db.execute(
            select(InvoiceItemTemplate)
            .options(
                selectinload(InvoiceItemTemplate.parcel_scopes), selectinload(InvoiceItemTemplate.member_scopes),
            )
            .where(InvoiceItemTemplate.id.in_(template_ids))
        )
        for template in result.scalars().all():
            item = InvoiceItemDefinition(
                invoice_run_id=run.id,
                order_number=template.order_number,
                name=template.name,
                description=template.description,
                pricing_mode=template.pricing_mode,
                unit_price=template.unit_price,
                applies_to_all_parcels=template.applies_to_all_parcels,
                applies_to_all_members=template.applies_to_all_members,
                category_id=template.category_id,
            )
            db.add(item)
            await db.flush()

            if not template.applies_to_all_parcels:
                for scope in template.parcel_scopes:
                    db.add(InvoiceItemDefinitionParcel(invoice_item_definition_id=item.id, parcel_id=scope.parcel_id))
            if not template.applies_to_all_members:
                for scope in template.member_scopes:
                    db.add(InvoiceItemDefinitionMember(invoice_item_definition_id=item.id, member_id=scope.member_id))

    await db.commit()
    return RedirectResponse(f"/finances/runs/{run_id}", status_code=302)


@router.post("/runs/{run_id}/items/{item_id}/edit")
async def item_update(
    run_id: str,
    item_id: str,
    request: Request,
    order_number: int = Form(0),
    name: str = Form(...),
    description: str = Form(""),
    pricing_mode: str = Form(...),
    unit_price: str = Form(""),
    applies_to_all_parcels: str = Form(""),
    applies_to_all_members: str = Form(""),
    parcel_ids: list[str] = Form([]),
    member_ids: list[str] = Form([]),
    category_id: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    """
    Edits an item definition, including its scope (specific parcels for
    plot-scoped modes, specific members for fixed_per_person) --
    editable freely any time before the run is finalized (a member
    asked for this explicitly: the picker should stay open to change up
    until the next invoice run actually happens, not be locked in at
    creation). Once finalized, item definitions can't be changed at all
    (see the run.status check below), matching how every other field
    here already works.
    """
    await require_permission(request, db, "finances", "write")

    result = await db.execute(
        select(InvoiceItemDefinition)
        .options(
            selectinload(InvoiceItemDefinition.parcel_scopes), selectinload(InvoiceItemDefinition.member_scopes),
        )
        .where(InvoiceItemDefinition.id == item_id, InvoiceItemDefinition.invoice_run_id == run_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404)

    run = await _get_run_or_404(db, run_id)
    if run.status != InvoiceRunStatus.DRAFT:
        raise HTTPException(status_code=400, detail=t_for(request, "finances.errors.run_not_draft"))

    try:
        mode = InvoicePricingMode(pricing_mode)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid pricing_mode")

    applies_all_parcels = applies_to_all_parcels == "on"
    applies_all_members = applies_to_all_members == "on"
    item.order_number = order_number
    item.name = name.strip()
    item.description = description.strip() or None
    item.pricing_mode = mode
    item.unit_price = _parse_decimal(unit_price) if mode not in _AUTOMATIC_PRICING_MODES else None
    item.applies_to_all_parcels = applies_all_parcels
    item.applies_to_all_members = applies_all_members
    item.category_id = category_id.strip() or None

    # Always resync scopes to what was actually submitted -- cleared
    # when applies_all, replaced with the new selection otherwise, so
    # stale choices never linger if scope changes back and forth
    # before finalize.
    #
    # The flush() right after each delete loop is required, not
    # cosmetic: SQLAlchemy's unit of work flushes INSERTs before
    # DELETEs for a given table within a single flush, so re-adding a
    # scope row that's unchanged from before (same parcel/member kept
    # selected) would otherwise try to INSERT the new row while the
    # identical old row is still physically present, tripping the
    # (definition_id, parcel_id)/(definition_id, member_id) unique
    # constraint -- found via a real 500 on re-saving an item whose
    # scope didn't change.
    for scope in list(item.parcel_scopes):
        await db.delete(scope)
    await db.flush()
    if not applies_all_parcels:
        for parcel_id in _dedupe_ids(parcel_ids):
            db.add(InvoiceItemDefinitionParcel(invoice_item_definition_id=item.id, parcel_id=parcel_id))
    for scope in list(item.member_scopes):
        await db.delete(scope)
    await db.flush()
    if not applies_all_members:
        for member_id in _dedupe_ids(member_ids):
            db.add(InvoiceItemDefinitionMember(invoice_item_definition_id=item.id, member_id=member_id))

    await db.commit()
    return RedirectResponse(f"/finances/runs/{run_id}", status_code=302)


@router.post("/runs/{run_id}/items/{item_id}/delete")
async def item_delete(run_id: str, item_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    await require_permission(request, db, "finances", "delete")

    result = await db.execute(
        select(InvoiceItemDefinition).where(
            InvoiceItemDefinition.id == item_id, InvoiceItemDefinition.invoice_run_id == run_id,
        )
    )
    item = result.scalar_one_or_none()
    if item:
        await db.delete(item)
        await db.commit()
    return RedirectResponse(f"/finances/runs/{run_id}", status_code=302)


# ---------------------------------------------------------------------------
# Preview and finalization
# ---------------------------------------------------------------------------

@router.get("/runs/{run_id}/preview", response_class=HTMLResponse)
async def run_preview(run_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_permission(request, db, "finances", "read")

    run = await _get_run_or_404(db, run_id)
    computed = await compute_invoices_for_run(db, run)

    return templates.TemplateResponse("finances/run_preview.html", {
        "request": request, "user": user, "run": run, "computed": computed,
    })


@router.get("/runs/{run_id}/preview/{parcel_id}/pdf")
async def run_preview_pdf(run_id: str, parcel_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    await require_permission(request, db, "finances", "read")

    run = await _get_run_or_404(db, run_id)
    computed = await compute_invoices_for_run(db, run)
    match = next((c for c in computed if c.parcel and c.parcel.id == parcel_id), None)
    if not match:
        raise HTTPException(status_code=404)

    ctx = await _pdf_context(db)
    data = InvoicePdfData(
        invoice_number=t_for(request, "finances.run_preview.pdf_placeholder_number"),
        issued_date=run.issued_date, due_date=run.due_date, subject=run.subject,
        recipient_names=match.recipient_names, recipient_address=match.recipient_address,
        parcel_plot_number=match.parcel.plot_number, parcel_area_sqm=match.parcel.area_sqm,
        line_items=[
            InvoicePdfLineItem(
                order_number=li.order_number, name=li.name, description=li.description,
                quantity=li.quantity, unit_price=li.unit_price, line_total=li.line_total,
            ) for li in match.line_items
        ],
        subtotal=match.subtotal, footer_text=run.footer_text, is_preview=True,
    )
    pdf_bytes = render_invoice_pdf(data, **ctx)
    return Response(content=pdf_bytes, media_type="application/pdf")


@router.get("/runs/{run_id}/preview/member/{member_id}/pdf")
async def run_preview_member_pdf(run_id: str, member_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    """Same as run_preview_pdf, but for a computed member invoice --
    a club member billed directly by a fixed_per_person item's own
    applies_to_all_members/member_scopes, regardless of parcel status
    (see app/invoice_generation.py)."""
    await require_permission(request, db, "finances", "read")

    run = await _get_run_or_404(db, run_id)
    computed = await compute_invoices_for_run(db, run)
    match = next((c for c in computed if c.member and c.member.id == member_id), None)
    if not match:
        raise HTTPException(status_code=404)

    ctx = await _pdf_context(db)
    data = InvoicePdfData(
        invoice_number=t_for(request, "finances.run_preview.pdf_placeholder_number"),
        issued_date=run.issued_date, due_date=run.due_date, subject=run.subject,
        recipient_names=match.recipient_names, recipient_address=match.recipient_address,
        parcel_plot_number=None, parcel_area_sqm=None,
        line_items=[
            InvoicePdfLineItem(
                order_number=li.order_number, name=li.name, description=li.description,
                quantity=li.quantity, unit_price=li.unit_price, line_total=li.line_total,
            ) for li in match.line_items
        ],
        subtotal=match.subtotal, footer_text=run.footer_text, is_preview=True,
    )
    pdf_bytes = render_invoice_pdf(data, **ctx)
    return Response(content=pdf_bytes, media_type="application/pdf")


@router.post("/runs/{run_id}/finalize")
async def run_finalize(run_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    await require_permission(request, db, "finances", "write")

    run = await _get_run_or_404(db, run_id)
    if run.status != InvoiceRunStatus.DRAFT:
        return RedirectResponse(f"/finances/runs/{run_id}", status_code=302)
    if not run.item_definitions:
        return RedirectResponse(
            f"/finances/runs/{run_id}?error={t_for(request, 'finances.errors.no_item_definitions')}",
            status_code=302,
        )

    try:
        await finalize_run(db, run)
    except SequenceCollisionError as e:
        await db.rollback()
        return RedirectResponse(f"/finances/runs/{run_id}?error={e}", status_code=302)
    await db.commit()
    return RedirectResponse(f"/finances/runs/{run_id}?success=1", status_code=302)


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

    ctx = await _pdf_context(db)
    data = invoice_pdf_data_from_invoice(invoice, run)
    pdf_bytes = render_invoice_pdf(data, **ctx)
    return Response(
        content=pdf_bytes, media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{invoice_pdf_filename(invoice, run)}"'},
    )


# ---------------------------------------------------------------------------
# Delivery: email, cloud upload, print bundle (issue #58)
# ---------------------------------------------------------------------------

async def _run_invoices(db: AsyncSession, run_id: str):
    result = await db.execute(
        select(Invoice)
        .options(selectinload(Invoice.line_items), selectinload(Invoice.parcel), selectinload(Invoice.member))
        .where(Invoice.invoice_run_id == run_id)
        .order_by(Invoice.invoice_number)
    )
    return list(result.scalars().all())


@router.post("/runs/{run_id}/deliver")
async def run_deliver(run_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    """Emails every not-yet-emailed invoice in the run (to whichever
    invoice-address resident has email_notifications=True and a
    stored email -- see app/invoice_delivery.py), and uploads every
    not-yet-uploaded one to its parcel's cloud folder if configured.
    Members without email stay for the print bundle (see
    run_print_bundle below) -- this action never marks anything
    printed."""
    await require_permission(request, db, "finances", "write")

    run = await _get_run_or_404(db, run_id)
    if run.status != InvoiceRunStatus.FINALIZED:
        raise HTTPException(status_code=400)

    invoices = await _run_invoices(db, run_id)
    ctx = await _pdf_context(db)
    provider = await get_nextcloud_provider(db)

    emailed_count = 0
    uploaded_count = 0
    for invoice in invoices:
        if invoice.emailed_at is None and await send_invoice_email(request, db, invoice, run, ctx):
            emailed_count += 1
        if invoice.uploaded_to_cloud_at is None and await upload_invoice_to_cloud(db, invoice, run, ctx, provider):
            uploaded_count += 1

    await db.commit()
    return RedirectResponse(
        f"/finances/runs/{run_id}?success=1&emailed={emailed_count}&uploaded={uploaded_count}",
        status_code=302,
    )


@router.get("/runs/{run_id}/print-bundle")
async def run_print_bundle(run_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    """Merges every invoice without a reachable invoice-address member
    (is_invoice_address=True and email_notifications=True -- see
    app/invoice_delivery.py) into one print-ready PDF and marks them
    printed. Filtered by recipient eligibility rather than emailed_at
    so the bundle is correct regardless of whether /deliver has run
    yet -- members eligible for email must never end up printed."""
    await require_permission(request, db, "finances", "write")

    run = await _get_run_or_404(db, run_id)
    invoices = [
        invoice for invoice in await _run_invoices(db, run_id)
        if not await invoice_has_email_recipient(db, invoice)
    ]
    if not invoices:
        raise HTTPException(status_code=404, detail=t_for(request, "finances.errors.no_print_invoices"))

    ctx = await _pdf_context(db)
    pdf_bytes = await build_print_bundle(db, invoices, run, ctx)
    await db.commit()

    return Response(
        content=pdf_bytes, media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="invoices_{run.year}_print_bundle.pdf"'},
    )


# ---------------------------------------------------------------------------
# Cross-run invoice list, detail, payments (issue #58)
# ---------------------------------------------------------------------------

async def _get_invoice_or_404(db: AsyncSession, invoice_id: str) -> Invoice:
    result = await db.execute(
        select(Invoice)
        .options(
            selectinload(Invoice.line_items), selectinload(Invoice.parcel), selectinload(Invoice.member),
            selectinload(Invoice.payments).selectinload(InvoicePayment.account),
            selectinload(Invoice.reminders),
        )
        .where(Invoice.id == invoice_id)
    )
    invoice = result.scalar_one_or_none()
    if not invoice:
        raise HTTPException(status_code=404)
    return invoice


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
    parsed_amount_min = _parse_decimal(amount_min) if amount_min.strip() else None
    if parsed_amount_min is not None:
        query = query.where(Invoice.subtotal >= parsed_amount_min)
    parsed_amount_max = _parse_decimal(amount_max) if amount_max.strip() else None
    if parsed_amount_max is not None:
        query = query.where(Invoice.subtotal <= parsed_amount_max)

    result = await db.execute(query)
    invoices = list(result.scalars().all())
    if status in ("open", "partially_paid", "paid"):
        invoices = [i for i in invoices if i.payment_status == status]

    return templates.TemplateResponse("finances/invoice_list.html", {
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

    return templates.TemplateResponse("finances/invoice_detail.html", {
        "request": request, "user": user, "invoice": invoice, "run": run,
        "today": date.today().isoformat(), "accounts": accounts,
    })


@router.post("/invoices/{invoice_id}/resend-email")
async def invoice_resend_email(invoice_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    await require_permission(request, db, "finances", "write")
    invoice = await _get_invoice_or_404(db, invoice_id)

    run_result = await db.execute(select(InvoiceRun).where(InvoiceRun.id == invoice.invoice_run_id))
    run = run_result.scalar_one_or_none()

    ctx = await _pdf_context(db)
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

    parsed_amount = _parse_decimal(amount)
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


# ---------------------------------------------------------------------------
# Bookkeeping categories (issue #67)
# ---------------------------------------------------------------------------

_CATEGORY_CODE_RE = re.compile(r"^\d{5}$")


def _valid_category_group(value: str) -> Optional[FinanceCategoryGroup]:
    try:
        return FinanceCategoryGroup(value.strip().upper())
    except ValueError:
        return None


@router.get("/categories", response_class=HTMLResponse)
async def category_list(request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_permission(request, db, "finances", "read")

    result = await db.execute(select(FinanceCategory).order_by(FinanceCategory.code))
    categories = list(result.scalars().all())

    return templates.TemplateResponse("finances/category_list.html", {
        "request": request, "user": user, "categories": categories,
        "groups": list(FinanceCategoryGroup),
    })


@router.post("/categories")
async def category_create(
    request: Request,
    code: str = Form(...),
    title: str = Form(...),
    group: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    await require_permission(request, db, "finances", "write")

    code = code.strip()
    parsed_group = _valid_category_group(group)
    if not _CATEGORY_CODE_RE.match(code) or not parsed_group or not title.strip():
        return RedirectResponse(
            f"/finances/categories?error={t_for(request, 'finances.errors.invalid_category')}", status_code=302,
        )

    existing = await db.execute(select(FinanceCategory).where(FinanceCategory.code == code))
    if existing.scalar_one_or_none():
        return RedirectResponse(
            f"/finances/categories?error={t_for(request, 'finances.errors.duplicate_category_code')}", status_code=302,
        )

    db.add(FinanceCategory(code=code, title=title.strip(), group=parsed_group))
    await db.commit()
    return RedirectResponse("/finances/categories?success=1", status_code=302)


@router.post("/categories/{category_id}/edit")
async def category_update(
    category_id: str,
    request: Request,
    code: str = Form(...),
    title: str = Form(...),
    group: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    await require_permission(request, db, "finances", "write")

    result = await db.execute(select(FinanceCategory).where(FinanceCategory.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404)

    code = code.strip()
    parsed_group = _valid_category_group(group)
    if not _CATEGORY_CODE_RE.match(code) or not parsed_group or not title.strip():
        return RedirectResponse(
            f"/finances/categories?error={t_for(request, 'finances.errors.invalid_category')}", status_code=302,
        )

    duplicate = await db.execute(
        select(FinanceCategory).where(FinanceCategory.code == code, FinanceCategory.id != category_id)
    )
    if duplicate.scalar_one_or_none():
        return RedirectResponse(
            f"/finances/categories?error={t_for(request, 'finances.errors.duplicate_category_code')}", status_code=302,
        )

    category.code = code
    category.title = title.strip()
    category.group = parsed_group
    await db.commit()
    return RedirectResponse("/finances/categories?success=1", status_code=302)


@router.post("/categories/{category_id}/delete")
async def category_delete(category_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    await require_permission(request, db, "finances", "delete")

    result = await db.execute(select(FinanceCategory).where(FinanceCategory.id == category_id))
    category = result.scalar_one_or_none()
    if category:
        await db.delete(category)
        await db.commit()
    return RedirectResponse("/finances/categories?success=1", status_code=302)


@router.post("/categories/import")
async def category_import(request: Request, file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    """Bulk-imports categories from a CSV file with a header row
    "code,title,group" -- e.g. a club's own real SKR42-derived chart
    exported from their accounting software. This app never ships
    SKR42 codes itself, see FinanceCategory's docstring."""
    await require_permission(request, db, "finances", "write")

    raw = (await file.read()).decode("utf-8-sig", errors="replace")
    reader = csv.DictReader(io.StringIO(raw))

    existing_result = await db.execute(select(FinanceCategory.code))
    existing_codes = {row[0] for row in existing_result.all()}

    imported = 0
    skipped = 0
    for row in reader:
        code = (row.get("code") or "").strip()
        title = (row.get("title") or "").strip()
        group_value = row.get("group") or ""
        parsed_group = _valid_category_group(group_value)

        if not _CATEGORY_CODE_RE.match(code) or not parsed_group or not title or code in existing_codes:
            skipped += 1
            continue

        db.add(FinanceCategory(code=code, title=title, group=parsed_group))
        existing_codes.add(code)
        imported += 1

    await db.commit()
    return RedirectResponse(
        f"/finances/categories?success=1&imported={imported}&skipped={skipped}", status_code=302,
    )


# ---------------------------------------------------------------------------
# Accounts (issue #156): a club's real bank/cash accounts. Purely a tag
# on InvoicePayment (see FinanceAccount's docstring) -- not a ledger.
# ---------------------------------------------------------------------------

@router.get("/accounts", response_class=HTMLResponse)
async def account_list(request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_permission(request, db, "finances", "read")

    result = await db.execute(select(FinanceAccount).order_by(FinanceAccount.name))
    accounts = list(result.scalars().all())

    payment_sums_result = await db.execute(
        select(InvoicePayment.account_id, func.sum(InvoicePayment.amount))
        .where(InvoicePayment.account_id.is_not(None))
        .group_by(InvoicePayment.account_id)
    )
    payment_sums = {account_id: total for account_id, total in payment_sums_result.all()}

    return templates.TemplateResponse("finances/account_list.html", {
        "request": request, "user": user, "accounts": accounts,
        "account_types": list(FinanceAccountType), "payment_sums": payment_sums,
    })


@router.post("/accounts")
async def account_create(
    request: Request,
    name: str = Form(...),
    account_type: str = Form(...),
    account_number: str = Form(""),
    note: str = Form(""),
    is_active: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    await require_permission(request, db, "finances", "write")

    if not name.strip():
        return RedirectResponse(
            f"/finances/accounts?error={t_for(request, 'errors.name_required')}", status_code=302,
        )
    try:
        parsed_type = FinanceAccountType(account_type)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid account_type")

    db.add(FinanceAccount(
        name=name.strip(), account_type=parsed_type,
        account_number=account_number.strip() or None, note=note.strip() or None,
        is_active=is_active == "on",
    ))
    await db.commit()
    return RedirectResponse("/finances/accounts?success=1", status_code=302)


@router.post("/accounts/{account_id}/edit")
async def account_update(
    account_id: str,
    request: Request,
    name: str = Form(...),
    account_type: str = Form(...),
    account_number: str = Form(""),
    note: str = Form(""),
    is_active: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    await require_permission(request, db, "finances", "write")

    result = await db.execute(select(FinanceAccount).where(FinanceAccount.id == account_id))
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404)

    if not name.strip():
        return RedirectResponse(
            f"/finances/accounts?error={t_for(request, 'errors.name_required')}", status_code=302,
        )
    try:
        parsed_type = FinanceAccountType(account_type)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid account_type")

    account.name = name.strip()
    account.account_type = parsed_type
    account.account_number = account_number.strip() or None
    account.note = note.strip() or None
    account.is_active = is_active == "on"
    await db.commit()
    return RedirectResponse("/finances/accounts?success=1", status_code=302)


@router.post("/accounts/{account_id}/delete")
async def account_delete(account_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    await require_permission(request, db, "finances", "delete")

    result = await db.execute(select(FinanceAccount).where(FinanceAccount.id == account_id))
    account = result.scalar_one_or_none()
    if account:
        await db.delete(account)
        await db.commit()
    return RedirectResponse("/finances/accounts?success=1", status_code=302)


# ---------------------------------------------------------------------------
# Account bookings (issue #174): a unified, filterable list of
# everything ever booked against one account -- InvoicePayment and
# IncomingInvoicePayment rows (always tied to an invoice) UNION ALL'd
# with AccountTransaction rows (anything else: refunds, purchases,
# bank fees, CSV-imported), see ADR 0059. issue #189: IncomingInvoicePayment
# was missing from this union entirely -- since issue #181 gave it an
# account_id, and issue #188 started actively creating tagged rows via
# invoice matching, any expense payment tagged to an account had been
# silently invisible on that account's own bookings page. All three are
# normalized to the same (id, booking_date, amount, reference,
# description, source, counterparty, invoice_id, incoming_invoice_id)
# shape so search/filtering/pagination only has to be written once,
# against the combined result. counterparty (issue #185) is
# Invoice.recipient_names / IncomingInvoice.sender for invoice rows,
# AccountTransaction.counterparty (manual/CSV, optional) otherwise.
# source is kept internally (it decides whether a row is deletable
# here, and now also drives the "assigned" filter, issue #189) but is
# no longer shown directly in the UI (issue #184).
# ---------------------------------------------------------------------------

BOOKINGS_PAGE_SIZE = 50
ASSIGNED_SOURCES = ("invoice_payment", "incoming_invoice_payment")
UNASSIGNED_SOURCES = ("manual", "csv_import")


def _account_bookings_base(account_id: str):
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


def _account_bookings_filtered(
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
    bookings = _account_bookings_base(account_id)
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
        parsed = _parse_date_flexible(date_from)
        if parsed:
            query = query.where(bookings.c.booking_date >= parsed)
    if date_to.strip():
        parsed = _parse_date_flexible(date_to)
        if parsed:
            query = query.where(bookings.c.booking_date <= parsed)
    if amount_min.strip():
        parsed = _parse_decimal(amount_min)
        if parsed is not None:
            query = query.where(bookings.c.amount >= parsed)
    if amount_max.strip():
        parsed = _parse_decimal(amount_max)
        if parsed is not None:
            query = query.where(bookings.c.amount <= parsed)

    return bookings, query


def _parse_date_flexible(s: str):
    s = s.strip()
    for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d.%m.%y"):
        try:
            return date.fromisoformat(s) if fmt == "%Y-%m-%d" else datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def _bookings_filter_params(request: Request) -> dict:
    q = request.query_params
    return {
        "search": q.get("search", ""), "date_from": q.get("date_from", ""), "date_to": q.get("date_to", ""),
        "amount_min": q.get("amount_min", ""), "amount_max": q.get("amount_max", ""),
        "assigned": q.get("assigned", ""),
    }


@router.get("/accounts/{account_id}/bookings", response_class=HTMLResponse)
async def account_bookings(account_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_permission(request, db, "finances", "read")

    result = await db.execute(select(FinanceAccount).where(FinanceAccount.id == account_id))
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404)

    filters = _bookings_filter_params(request)
    bookings, query = _account_bookings_filtered(account_id, **filters)
    query = query.order_by(bookings.c.booking_date.desc(), bookings.c.id.desc()).limit(BOOKINGS_PAGE_SIZE)
    rows = (await db.execute(query)).all()

    return templates.TemplateResponse("finances/account_bookings.html", {
        "request": request, "user": user, "account": account, "rows": rows,
        "filters": filters, "page_size": BOOKINGS_PAGE_SIZE,
        "has_more": len(rows) == BOOKINGS_PAGE_SIZE,
        "today": date.today().isoformat(),
    })


@router.get("/accounts/{account_id}/bookings.json")
async def account_bookings_json(
    account_id: str, request: Request, offset: int = 0, db: AsyncSession = Depends(get_db),
):
    """Fetched by the bookings page's infinite scroll for every page
    after the first (which the HTML route above already renders)."""
    await require_permission(request, db, "finances", "read")

    filters = _bookings_filter_params(request)
    bookings, query = _account_bookings_filtered(account_id, **filters)
    query = (
        query.order_by(bookings.c.booking_date.desc(), bookings.c.id.desc())
        .limit(BOOKINGS_PAGE_SIZE).offset(offset)
    )
    rows = (await db.execute(query)).all()

    return {
        "rows": [
            {
                "id": r.id,
                "booking_date": r.booking_date.strftime("%d.%m.%Y"),
                "amount": float(r.amount),
                "reference": r.reference,
                "description": r.description,
                "counterparty": r.counterparty,
                "invoice_url": (
                    f"/finances/invoices/{r.invoice_id}" if r.invoice_id
                    else f"/finances/incoming-invoices/{r.incoming_invoice_id}" if r.incoming_invoice_id
                    else None
                ),
            }
            for r in rows
        ],
        "has_more": len(rows) == BOOKINGS_PAGE_SIZE,
    }


@router.get("/accounts/{account_id}/bookings/export.csv")
async def account_bookings_export_csv(account_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    await require_permission(request, db, "finances", "read")

    result = await db.execute(select(FinanceAccount).where(FinanceAccount.id == account_id))
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404)

    filters = _bookings_filter_params(request)
    bookings, query = _account_bookings_filtered(account_id, **filters)
    query = query.order_by(bookings.c.booking_date.desc(), bookings.c.id.desc())
    rows = (await db.execute(query)).all()

    output = io.StringIO()
    writer = csv.writer(output, delimiter=";")
    writer.writerow(["Date", "Amount", "Reference", "Description", "Counterparty"])
    for r in rows:
        writer.writerow([
            r.booking_date.strftime("%Y-%m-%d"), f"{float(r.amount):.2f}",
            csv_safe(r.reference or ""), csv_safe(r.description or ""), csv_safe(r.counterparty or ""),
        ])

    filename = f"{account.name.replace(' ', '_')}_bookings.csv"
    return Response(
        content=output.getvalue(), media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


CSV_IMPORT_TARGET_FIELDS = ["date", "amount", "description", "counterparty", "iban"]
CSV_IMPORT_PREVIEW_ROWS = 5


FINANCES_IMPORT_FIELD_ALIASES = {
    "date": {"date", "datum", "buchungsdatum"},
    "amount": {"amount", "betrag"},
    "description": {"description", "beschreibung", "verwendungszweck", "note"},
    "counterparty": {"counterparty", "sender", "recipient", "empfänger", "auftraggeber", "name"},
    "iban": {"iban"},
}


@router.post(
    "/accounts/{account_id}/bookings/import/preview",
    response_class=HTMLResponse,
)
async def account_bookings_import_preview(
    account_id: str, request: Request,
    datei: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """Issue #186: "import any CSV of any structure" -- step 1 just
    detects the header row and lets the user map each column to a
    Parcella field (or ignore it) before anything is written. The raw
    CSV is round-tripped to step 2 as a hidden base64 field rather than
    kept in server-side session state, matching this app's stateless-
    request style elsewhere."""
    user = await require_permission(request, db, "finances", "write")

    result = await db.execute(select(FinanceAccount).where(FinanceAccount.id == account_id))
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404)

    content = await datei.read()
    text = decode_csv_upload(content)
    delimiter = sniff_csv_delimiter(text)

    reader = csv.reader(io.StringIO(text), delimiter=delimiter)
    rows = list(reader)
    if not rows:
        return RedirectResponse(
            f"/finances/accounts/{account_id}/bookings?error={urlquote(t_for(request, 'finances.account_bookings.csv_empty_error'))}",
            status_code=303,
        )
    headers = [h.strip() for h in rows[0]]
    preview_rows = rows[1:1 + CSV_IMPORT_PREVIEW_ROWS]
    default_mapping = guess_column_mapping(headers, FINANCES_IMPORT_FIELD_ALIASES)

    return templates.TemplateResponse("finances/account_bookings_import_preview.html", {
        "request": request, "user": user, "account": account,
        "headers": headers, "preview_rows": preview_rows,
        "default_mapping": default_mapping, "target_fields": CSV_IMPORT_TARGET_FIELDS,
        "csv_content_b64": base64.b64encode(content).decode("ascii"), "delimiter": delimiter,
    })


def _parse_finances_mapped_rows(csv_content_b64: str, delimiter: str, column_mapping: dict) -> list:
    """finances-specific finishing pass over app.csv_utils.parse_mapped_csv_rows'
    raw string values: parses date/amount and marks row validity."""
    raw_rows = parse_mapped_csv_rows(csv_content_b64, delimiter, column_mapping)
    parsed_rows = []
    for values in raw_rows:
        parsed_date = _parse_date_flexible(values.get("date", ""))
        parsed_amount = _parse_decimal(values.get("amount", ""))
        parsed_rows.append({
            "date": parsed_date, "amount": parsed_amount,
            "description": values.get("description", ""), "counterparty": values.get("counterparty", ""),
            "iban": values.get("iban", ""), "valid": parsed_date is not None and parsed_amount is not None,
        })
    return parsed_rows


@router.post(
    "/accounts/{account_id}/bookings/import/match",
    response_class=HTMLResponse,
)
async def account_bookings_import_match(
    account_id: str, request: Request,
    csv_content_b64: str = Form(...), delimiter: str = Form(";"),
    db: AsyncSession = Depends(get_db),
):
    """Step 2 (issue #188): before creating anything, show each row's
    possible open-invoice matches (by amount, then counterparty name)
    so the user can turn a row into a real payment instead of a
    generic booking."""
    user = await require_permission(request, db, "finances", "write")

    result = await db.execute(select(FinanceAccount).where(FinanceAccount.id == account_id))
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404)

    form = await request.form()
    column_mapping = parse_column_mapping(form, CSV_IMPORT_TARGET_FIELDS)
    if "date" not in column_mapping.values() or "amount" not in column_mapping.values():
        return RedirectResponse(
            f"/finances/accounts/{account_id}/bookings?error={urlquote(t_for(request, 'finances.account_bookings.csv_mapping_required_error'))}",
            status_code=303,
        )

    parsed_rows = _parse_finances_mapped_rows(csv_content_b64, delimiter, column_mapping)

    row_matches = []
    for row in parsed_rows:
        matches = await find_matching_invoices(db, row["amount"], row["counterparty"]) if row["valid"] else []
        row_matches.append({"row": row, "matches": matches, "best": best_match_option(matches)})

    return templates.TemplateResponse("finances/account_bookings_import_match.html", {
        "request": request, "user": user, "account": account, "row_matches": row_matches,
        "csv_content_b64": csv_content_b64, "delimiter": delimiter, "column_mapping": column_mapping,
    })


@router.post("/accounts/{account_id}/bookings/import/finalize")
async def account_bookings_import_finalize(
    account_id: str, request: Request,
    csv_content_b64: str = Form(...), delimiter: str = Form(";"),
    db: AsyncSession = Depends(get_db),
):
    """Step 3: applies each row's chosen match (a real InvoicePayment/
    IncomingInvoicePayment) or creates a generic AccountTransaction
    otherwise -- never auto-matches, only what the user picked in step
    2 (issue #174/ADR 0059's reconciliation-is-out-of-scope stance
    still holds for anything not explicitly confirmed). Also backfills
    a matched member's IBAN (issue #187) when "counterparty" and
    "iban" columns were both mapped."""
    user = await require_permission(request, db, "finances", "write")

    result = await db.execute(select(FinanceAccount).where(FinanceAccount.id == account_id))
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404)

    form = await request.form()
    column_mapping = parse_column_mapping(form, CSV_IMPORT_TARGET_FIELDS)
    if "date" not in column_mapping.values() or "amount" not in column_mapping.values():
        return RedirectResponse(
            f"/finances/accounts/{account_id}/bookings?error={urlquote(t_for(request, 'finances.account_bookings.csv_mapping_required_error'))}",
            status_code=303,
        )
    parsed_rows = _parse_finances_mapped_rows(csv_content_b64, delimiter, column_mapping)

    members_by_name: dict = {}
    if "iban" in column_mapping.values() and "counterparty" in column_mapping.values():
        members_result = await db.execute(select(Member))
        for member in members_result.scalars().all():
            forward = f"{member.first_name} {member.last_name}".strip().lower()
            reverse = f"{member.last_name} {member.first_name}".strip().lower()
            members_by_name[forward] = member
            members_by_name[reverse] = member

    imported = 0
    skipped = 0
    iban_updated = 0
    matched = 0
    for i, row in enumerate(parsed_rows):
        if not row["valid"]:
            skipped += 1
            continue

        match_choice = form.get(f"match_{i}", "none")
        did_match = await _create_matched_or_generic_transaction(
            db, account_id, user.id, row["date"], row["amount"], row["description"], row["counterparty"], match_choice,
            source="csv_import",
        )
        imported += 1
        if did_match:
            matched += 1

        if row["iban"] and row["counterparty"]:
            member = members_by_name.get(row["counterparty"].lower())
            if member and not member.iban:
                member.iban = row["iban"]
                iban_updated += 1

    await db.commit()
    return RedirectResponse(
        f"/finances/accounts/{account_id}/bookings?imported={imported}&skipped={skipped}"
        f"&iban_updated={iban_updated}&matched={matched}",
        status_code=302,
    )


async def _create_matched_or_generic_transaction(
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


@router.post("/accounts/{account_id}/bookings/manual/preview", response_class=HTMLResponse)
async def account_bookings_manual_preview(
    account_id: str, request: Request,
    booking_date: str = Form(...), amount: str = Form(...), description: str = Form(""),
    counterparty: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    """Issue #188: before creating a generic booking, show any open
    invoices whose amount (and ideally counterparty name) matches, so
    the user can record this as a real payment instead."""
    user = await require_permission(request, db, "finances", "write")

    result = await db.execute(select(FinanceAccount).where(FinanceAccount.id == account_id))
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404)

    parsed_date = _parse_date_flexible(booking_date)
    parsed_amount = _parse_decimal(amount)
    if parsed_date is None or parsed_amount is None:
        raise HTTPException(status_code=400)

    matches = await find_matching_invoices(db, parsed_amount, counterparty)

    return templates.TemplateResponse("finances/account_bookings_manual_match.html", {
        "request": request, "user": user, "account": account, "matches": matches,
        "best_match": best_match_option(matches),
        "booking_date": booking_date, "amount": amount, "description": description, "counterparty": counterparty,
    })


@router.post("/accounts/{account_id}/bookings/manual/confirm")
async def account_bookings_manual_confirm(
    account_id: str, request: Request,
    booking_date: str = Form(...), amount: str = Form(...), description: str = Form(""),
    counterparty: str = Form(""), match_choice: str = Form("none"),
    db: AsyncSession = Depends(get_db),
):
    user = await require_permission(request, db, "finances", "write")

    result = await db.execute(select(FinanceAccount).where(FinanceAccount.id == account_id))
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404)

    parsed_date = _parse_date_flexible(booking_date)
    parsed_amount = _parse_decimal(amount)
    if parsed_date is None or parsed_amount is None:
        raise HTTPException(status_code=400)

    did_match = await _create_matched_or_generic_transaction(
        db, account_id, user.id, parsed_date, parsed_amount,
        description.strip(), counterparty.strip(), match_choice,
    )
    await db.commit()
    suffix = "?matched=1" if did_match else ""
    return RedirectResponse(f"/finances/accounts/{account_id}/bookings{suffix}", status_code=302)


@router.post("/accounts/{account_id}/bookings/{transaction_id}/delete")
async def account_bookings_delete_manual(
    account_id: str, transaction_id: str, request: Request, db: AsyncSession = Depends(get_db),
):
    """Only AccountTransaction rows can be deleted here -- an
    InvoicePayment must be removed via its own invoice's payment-delete
    route, since that's the only place that still makes sense as the
    single source of truth for a real invoice payment."""
    await require_permission(request, db, "finances", "delete")

    result = await db.execute(
        select(AccountTransaction).where(
            AccountTransaction.id == transaction_id, AccountTransaction.account_id == account_id,
        )
    )
    transaction = result.scalar_one_or_none()
    if transaction:
        await db.delete(transaction)
        await db.commit()
    return RedirectResponse(f"/finances/accounts/{account_id}/bookings", status_code=302)


# ---------------------------------------------------------------------------
# Item catalog: reusable line-item templates a board member curates
# directly, replacing the old "copy items from another run" mechanism
# (issue #66) -- see InvoiceItemTemplate's docstring in app/models.py.
# ---------------------------------------------------------------------------

@router.get("/item-templates", response_class=HTMLResponse)
async def item_template_list(request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_permission(request, db, "finances", "read")

    item_templates = await _item_templates(db)
    next_order = max((t.order_number for t in item_templates), default=0) + 10
    categories_result = await db.execute(select(FinanceCategory).order_by(FinanceCategory.code))
    categories = list(categories_result.scalars().all())
    parcels = await _active_parcels(db)
    members = await _active_members(db)

    return templates.TemplateResponse("finances/item_template_list.html", {
        "request": request, "user": user, "item_templates": item_templates, "next_order": next_order,
        "pricing_modes": list(InvoicePricingMode), "categories": categories, "parcels": parcels, "members": members,
    })


@router.post("/item-templates")
async def item_template_create(
    request: Request,
    order_number: int = Form(0),
    name: str = Form(...),
    description: str = Form(""),
    pricing_mode: str = Form(...),
    unit_price: str = Form(""),
    applies_to_all_parcels: str = Form(""),
    applies_to_all_members: str = Form(""),
    parcel_ids: list[str] = Form([]),
    member_ids: list[str] = Form([]),
    category_id: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    await require_permission(request, db, "finances", "write")

    try:
        mode = InvoicePricingMode(pricing_mode)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid pricing_mode")

    applies_all_parcels = applies_to_all_parcels == "on"
    applies_all_members = applies_to_all_members == "on"
    template = InvoiceItemTemplate(
        order_number=order_number,
        name=name.strip(),
        description=description.strip() or None,
        pricing_mode=mode,
        unit_price=_parse_decimal(unit_price) if mode not in _AUTOMATIC_PRICING_MODES else None,
        applies_to_all_parcels=applies_all_parcels,
        applies_to_all_members=applies_all_members,
        category_id=category_id.strip() or None,
    )
    db.add(template)
    await db.flush()

    if not applies_all_parcels:
        for parcel_id in _dedupe_ids(parcel_ids):
            db.add(InvoiceItemTemplateParcel(invoice_item_template_id=template.id, parcel_id=parcel_id))
    if not applies_all_members:
        for member_id in _dedupe_ids(member_ids):
            db.add(InvoiceItemTemplateMember(invoice_item_template_id=template.id, member_id=member_id))

    await db.commit()
    return RedirectResponse("/finances/item-templates?success=1", status_code=302)


@router.post("/item-templates/{template_id}/edit")
async def item_template_update(
    template_id: str,
    request: Request,
    order_number: int = Form(0),
    name: str = Form(...),
    description: str = Form(""),
    pricing_mode: str = Form(...),
    unit_price: str = Form(""),
    applies_to_all_parcels: str = Form(""),
    applies_to_all_members: str = Form(""),
    parcel_ids: list[str] = Form([]),
    member_ids: list[str] = Form([]),
    category_id: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    """Edits a template, including its scope (specific parcels or
    specific members, depending on pricing mode) -- freely editable at
    any time, same as a run's own item (see item_update)."""
    await require_permission(request, db, "finances", "write")

    result = await db.execute(
        select(InvoiceItemTemplate)
        .options(
            selectinload(InvoiceItemTemplate.parcel_scopes), selectinload(InvoiceItemTemplate.member_scopes),
        )
        .where(InvoiceItemTemplate.id == template_id)
    )
    template = result.scalar_one_or_none()
    if not template:
        raise HTTPException(status_code=404)

    try:
        mode = InvoicePricingMode(pricing_mode)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid pricing_mode")

    applies_all_parcels = applies_to_all_parcels == "on"
    applies_all_members = applies_to_all_members == "on"
    template.order_number = order_number
    template.name = name.strip()
    template.description = description.strip() or None
    template.pricing_mode = mode
    template.unit_price = _parse_decimal(unit_price) if mode not in _AUTOMATIC_PRICING_MODES else None
    template.applies_to_all_parcels = applies_all_parcels
    template.applies_to_all_members = applies_all_members
    template.category_id = category_id.strip() or None

    # See item_update's identical comment above -- the flush() between
    # delete and re-add is required to avoid a transient unique-
    # constraint violation when a scope is unchanged from before.
    for scope in list(template.parcel_scopes):
        await db.delete(scope)
    await db.flush()
    if not applies_all_parcels:
        for parcel_id in _dedupe_ids(parcel_ids):
            db.add(InvoiceItemTemplateParcel(invoice_item_template_id=template.id, parcel_id=parcel_id))
    for scope in list(template.member_scopes):
        await db.delete(scope)
    await db.flush()
    if not applies_all_members:
        for member_id in _dedupe_ids(member_ids):
            db.add(InvoiceItemTemplateMember(invoice_item_template_id=template.id, member_id=member_id))

    await db.commit()
    return RedirectResponse("/finances/item-templates?success=1", status_code=302)


@router.post("/item-templates/{template_id}/delete")
async def item_template_delete(template_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    await require_permission(request, db, "finances", "delete")

    result = await db.execute(select(InvoiceItemTemplate).where(InvoiceItemTemplate.id == template_id))
    template = result.scalar_one_or_none()
    if template:
        await db.delete(template)
        await db.commit()
    return RedirectResponse("/finances/item-templates?success=1", status_code=302)
