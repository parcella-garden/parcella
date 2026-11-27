"""Incoming invoices, their payments and documents."""
from fastapi import APIRouter
from datetime import date, datetime
from typing import Optional
from itertools import zip_longest
from urllib.parse import quote as urlquote
from fastapi import Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.i18n import t_for
from app.security_headers import content_disposition
from app.models import (
    FinanceAccount,
    FinanceCategory,
    IncomingInvoice,
    IncomingInvoiceLineItem,
    IncomingInvoicePayment,
)
from app.auth import require_admin
from app.permissions import require_permission
from app.module_flags import require_module
from app.l10n import parse_decimal
from app.cloud_storage import CloudStorageError, get_cloud_storage_provider
from app.routers.external_contacts import picker_contacts, resolve_picked_contact
from app.templating import templates
from app.services.finances import get_incoming_invoices_folder, parse_date_flexible

router = APIRouter()


def _cloud_storage_enabled(request: Request) -> bool:
    module_flags = getattr(request.state, "module_flags", {})
    return bool(module_flags.get("cloud_storage")) and getattr(request.state, "is_full_access", False)


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

    parsed_amount_min = parse_decimal(amount_min) if amount_min.strip() else None
    if parsed_amount_min is not None:
        invoices = [i for i in invoices if i.total_amount >= float(parsed_amount_min)]
    parsed_amount_max = parse_decimal(amount_max) if amount_max.strip() else None
    if parsed_amount_max is not None:
        invoices = [i for i in invoices if i.total_amount <= float(parsed_amount_max)]
    if status in ("open", "partially_paid", "paid"):
        invoices = [i for i in invoices if i.payment_status == status]

    categories_result = await db.execute(select(FinanceCategory).order_by(FinanceCategory.code))
    categories = list(categories_result.scalars().all())

    cloud_storage_enabled = _cloud_storage_enabled(request)
    folder_path = await get_incoming_invoices_folder(db) if cloud_storage_enabled else None

    return templates.TemplateResponse(request, "finances/incoming_invoices_list.html", {
        "request": request, "user": user, "invoices": invoices, "categories": categories,
        "cloud_storage_enabled": cloud_storage_enabled, "folder_path": folder_path,
        "today": date.today().isoformat(), "contacts": await picker_contacts(request, db),
        "filter_invoice_number": invoice_number, "filter_sender": sender,
        "filter_amount_min": amount_min, "filter_amount_max": amount_max, "filter_status": status,
    })


@router.post("/incoming-invoices")
async def incoming_invoice_create(
    request: Request,
    sender: str = Form(...), invoice_number: str = Form(""), invoice_date: str = Form(...), note: str = Form(""),
    external_contact_id: str = Form(""),
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

    parsed_date = parse_date_flexible(invoice_date)
    if parsed_date is None or not sender.strip():
        raise HTTPException(status_code=400)

    invoice = IncomingInvoice(
        sender=sender.strip(), invoice_number=invoice_number.strip() or None,
        invoice_date=parsed_date, note=note.strip() or None, created_by_id=user.id,
        external_contact_id=await resolve_picked_contact(request, db, external_contact_id),
    )
    db.add(invoice)
    await db.flush()

    for cat_id, desc, amt in zip_longest(category_id, description, amount, fillvalue=""):
        parsed_amount = parse_decimal(amt)
        if parsed_amount is None:
            continue
        db.add(IncomingInvoiceLineItem(
            incoming_invoice_id=invoice.id, category_id=cat_id.strip() or None,
            description=desc.strip() or None, amount=parsed_amount,
        ))

    if file is not None and file.filename and _cloud_storage_enabled(request):
        folder_path = await get_incoming_invoices_folder(db)
        if folder_path:
            provider = await get_cloud_storage_provider(db)
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
            selectinload(IncomingInvoice.external_contact),
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

    return templates.TemplateResponse(request, "finances/incoming_invoice_detail.html", {
        "request": request, "user": user, "invoice": invoice, "accounts": accounts,
        "cloud_storage_enabled": _cloud_storage_enabled(request),
        "today": date.today().isoformat(), "contacts": await picker_contacts(request, db),
    })


@router.post("/incoming-invoices/{invoice_id}/contact")
async def incoming_invoice_set_contact(
    invoice_id: str, request: Request, external_contact_id: str = Form(""), db: AsyncSession = Depends(get_db),
):
    """Links (or unlinks, with "") the external contact who sent the
    invoice (ADR 0096). Leaves `sender` alone -- that's what search,
    the accounting statement and bank matching read."""
    await require_permission(request, db, "finances", "write")
    invoice = await db.get(IncomingInvoice, invoice_id)
    if invoice is None:
        raise HTTPException(status_code=404)
    invoice.external_contact_id = await resolve_picked_contact(request, db, external_contact_id)
    await db.commit()
    return RedirectResponse(f"/finances/incoming-invoices/{invoice_id}", status_code=303)


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

    parsed_amount = parse_decimal(amount)
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

    folder_path = await get_incoming_invoices_folder(db)
    if not folder_path:
        raise HTTPException(status_code=400, detail=t_for(request, "finances.incoming_invoices.cloud_not_configured"))

    provider = await get_cloud_storage_provider(db)
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
        headers={"Content-Disposition": content_disposition(invoice.cloud_filename)},
    )
