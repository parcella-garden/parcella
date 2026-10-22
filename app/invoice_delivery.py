"""
Delivery for finalized invoices (issue #58): email with the invoice
PDF attached, upload to the parcel's cloud-storage folder, and a
merged print bundle for members who aren't reachable by email.

Recipient resolution is re-derived at send time (not from the
Invoice's recipient_names/-address snapshot) since delivery can happen
well after a run is finalized, and membership may have changed since.
"""
from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional, Tuple

from fastapi import Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import current_tenant_filter
from app.models import Invoice, InvoiceRun, InvoiceReminder, MemberParcel, Member
from app.email_service import send_email
from app.parcel_cloud_folders import get_active_folder
from app.cloud_storage import CloudStorageError, CloudStorageProvider
from app.i18n import t_for
from app.invoice_pdf import (
    InvoicePdfData, render_invoice_pdf, render_invoice_bundle_pdf, invoice_pdf_data_from_invoice,
    invoice_pdf_filename, reminder_pdf_data_from_reminder, render_reminder_pdf, reminder_pdf_filename,
)


async def _invoice_recipient(db: AsyncSession, invoice: Invoice) -> Optional[Tuple[Member, str]]:
    """The (member, email) to send `invoice` to. For a parcel invoice:
    any current invoice-address resident of its parcel with
    email_notifications=True and a stored email address. For a member
    invoice (no parcel, invoice.member_id set instead -- see
    app/invoice_generation.py's _compute_member_invoices): that member
    directly, same email_notifications/stored-address check, no
    household grouping needed since it's always exactly that one
    member."""
    if invoice.member_id is not None:
        result = await db.execute(
            select(Member)
            .options(selectinload(Member.email_addresses))
            .where(Member.id == invoice.member_id)
        )
        member = result.scalar_one_or_none()
        if member is None or not member.email_notifications or not member.email_addresses:
            return None
        primary = next((e for e in member.email_addresses if e.is_primary), member.email_addresses[0])
        return member, primary.address

    result = await db.execute(
        select(MemberParcel)
        .options(selectinload(MemberParcel.member).selectinload(Member.email_addresses))
        .where(
            MemberParcel.parcel_id == invoice.parcel_id,
            current_tenant_filter(),
            MemberParcel.is_invoice_address.is_(True),
        )
    )
    for assignment in result.scalars().all():
        member = assignment.member
        if not member.email_notifications or not member.email_addresses:
            continue
        primary = next((e for e in member.email_addresses if e.is_primary), member.email_addresses[0])
        return member, primary.address
    return None


async def invoice_has_email_recipient(db: AsyncSession, invoice: Invoice) -> bool:
    """Whether `invoice` has a reachable invoice-address resident with
    email_notifications=True (see _invoice_recipient) -- i.e. it will
    be delivered by email rather than print, independent of whether
    that email has actually been sent yet."""
    return await _invoice_recipient(db, invoice) is not None


async def send_invoice_email(
    request: Request, db: AsyncSession, invoice: Invoice, run: InvoiceRun, pdf_context: dict,
) -> bool:
    """Emails `invoice`'s PDF to its parcel's invoice-address member,
    if reachable. Returns whether an email was actually sent; sets
    invoice.emailed_at on success. Caller commits."""
    recipient = await _invoice_recipient(db, invoice)
    if recipient is None:
        return False
    member, email_address = recipient

    data = invoice_pdf_data_from_invoice(invoice, run)
    pdf_bytes = render_invoice_pdf(data, **pdf_context)

    subject = t_for(request, "email.invoice_delivery.subject", invoice_number=invoice.invoice_number, club_name=pdf_context["footer_context"].club_name)
    body = (
        t_for(request, "email.invoice_delivery.body", club_name=pdf_context["footer_context"].club_name, parcel_number=invoice.parcel.plot_number, due_date=run.due_date.strftime("%d.%m.%Y"))
        if invoice.parcel else
        t_for(request, "email.invoice_delivery.body_member", club_name=pdf_context["footer_context"].club_name, due_date=run.due_date.strftime("%d.%m.%Y"))
    )
    html = f"""
    <html><body style="font-family: sans-serif;">
    <p>{t_for(request, "email.invoice_delivery.greeting", name=member.full_name)}</p>
    <p>{body}</p>
    </body></html>
    """
    filename = invoice_pdf_filename(invoice, run)
    sent = await send_email(
        email_address, subject, html, db=db,
        attachments=[(filename, pdf_bytes, "application/pdf")],
    )
    if sent:
        invoice.emailed_at = datetime.now(timezone.utc)
    return sent


async def deliver_reminder(
    request: Request, db: AsyncSession, invoice: Invoice, run: InvoiceRun,
    fee_amount: Optional[Decimal], message: Optional[str], created_by_id: Optional[str], pdf_context: dict,
) -> InvoiceReminder:
    """Creates and delivers the next reminder for `invoice` (issue #59):
    level is one past however many already exist. Delivery follows the
    exact same recipient resolution as the original invoice (see
    _invoice_recipient) -- email if the member opted in and has a
    stored address, otherwise the PDF is generated and left available
    for manual/postal sending, matching "the way the member already
    chose" for invoice delivery rather than asking again per reminder.
    Caller commits."""
    next_level = max((r.level for r in invoice.reminders), default=0) + 1
    reminder = InvoiceReminder(
        level=next_level, fee_amount=fee_amount, message=message or None,
        delivery_method="print", created_by_id=created_by_id,
    )
    invoice.reminders.append(reminder)
    await db.flush()

    data = reminder_pdf_data_from_reminder(reminder, invoice, run)
    pdf_bytes = render_reminder_pdf(data, **pdf_context)

    recipient = await _invoice_recipient(db, invoice)
    if recipient is not None:
        member, email_address = recipient
        subject = t_for(
            request, "email.reminder_delivery.subject",
            invoice_number=invoice.invoice_number, level=next_level, club_name=pdf_context["footer_context"].club_name,
        )
        html = f"""
        <html><body style="font-family: sans-serif;">
        <p>{t_for(request, "email.reminder_delivery.greeting", name=member.full_name)}</p>
        <p>{t_for(request, "email.reminder_delivery.body", club_name=pdf_context["footer_context"].club_name, invoice_number=invoice.invoice_number)}</p>
        </body></html>
        """
        filename = reminder_pdf_filename(reminder, invoice, run)
        sent = await send_email(
            email_address, subject, html, db=db,
            attachments=[(filename, pdf_bytes, "application/pdf")],
        )
        if sent:
            reminder.delivery_method = "email"

    return reminder


async def upload_invoice_to_cloud(
    db: AsyncSession, invoice: Invoice, run: InvoiceRun, pdf_context: dict, provider: Optional[CloudStorageProvider],
) -> bool:
    """Uploads `invoice`'s PDF to its parcel's active cloud-storage
    folder, if one is configured. `provider` is resolved once by the
    caller (app.cloud_storage.get_cloud_storage_provider) and reused across
    every invoice in a run, rather than reconnecting per invoice.
    Returns whether it was actually uploaded (silently skipped -- not
    an error -- if cloud storage isn't configured, the parcel has no
    folder assigned, or `invoice` is a member invoice with no parcel at
    all -- there's no member-level cloud folder concept, same as the
    rest of the app treats this as opt-in). Sets
    invoice.uploaded_to_cloud_at on success. Caller commits."""
    if provider is None or invoice.parcel_id is None:
        return False
    folder = await get_active_folder(db, invoice.parcel_id)
    if folder is None:
        return False

    data = invoice_pdf_data_from_invoice(invoice, run)
    pdf_bytes = render_invoice_pdf(data, **pdf_context)
    filename = invoice_pdf_filename(invoice, run)

    try:
        await provider.upload_file(folder.relative_path, filename, pdf_bytes)
    except CloudStorageError:
        return False

    invoice.uploaded_to_cloud_at = datetime.now(timezone.utc)
    return True


async def build_print_bundle(db: AsyncSession, invoices: List[Invoice], run: InvoiceRun, pdf_context: dict) -> bytes:
    """Merges `invoices` into one print-ready PDF (issue #58's "merge
    PDFs to one big one so we can print it") and marks each as printed.
    Caller decides which invoices to include (see the router: members
    without email notifications) and commits."""
    items = [invoice_pdf_data_from_invoice(invoice, run) for invoice in invoices]
    now = datetime.now(timezone.utc)
    for invoice in invoices:
        invoice.printed_at = now
    return render_invoice_bundle_pdf(items, **pdf_context)
