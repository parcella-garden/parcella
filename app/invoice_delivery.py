"""
Delivery for finalized invoices (issue #58): email with the invoice
PDF attached, upload to the parcel's cloud-storage folder, and a
merged print bundle for whoever isn't reachable by email.

Since issue #396 a parcel invoice has one copy per address its
invoice-address tenants live at (Invoice.recipient_copies, see
app/invoice_pdf.py's invoice_copies). Each copy is delivered on its
own: every person on it with email notifications and a stored address
gets it by email, and a copy nobody on it can be emailed at goes into
the print bundle. So a co-tenant at another address without email gets
a letter even when the others are emailed.

Who is on a copy is the snapshot taken when the run was finalized --
they are the people the invoice is addressed to. Only their email
addresses and consent are read live. Invoices from before #396 have no
snapshot; for them every current invoice-address tenant of the parcel
is resolved at send time, as before.
"""
from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional, Tuple

from fastapi import Request
from markupsafe import escape
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
    InvoiceCopy, invoice_copies, render_invoice_pdf, render_invoice_bundle_pdf, invoice_pdf_data_from_invoice,
    invoice_pdf_filename, reminder_pdf_data_from_reminder, render_reminder_pdf, render_reminder_bundle_pdf,
    reminder_pdf_filename,
)


def _primary_address(member: Member) -> str:
    return next((e for e in member.email_addresses if e.is_primary), member.email_addresses[0]).address


async def _copy_members(db: AsyncSession, invoice: Invoice, copy: InvoiceCopy) -> List[Member]:
    """The people `copy` is for, with their email addresses loaded."""
    if copy.member_ids is not None:
        if not copy.member_ids:
            return []
        result = await db.execute(
            select(Member)
            .options(selectinload(Member.email_addresses))
            .where(Member.id.in_(copy.member_ids), Member.deleted_at.is_(None))
        )
        by_id = {m.id: m for m in result.scalars().all()}
        return [by_id[i] for i in copy.member_ids if i in by_id]
    # Invoice from before #396: its parcel's current invoice-address tenants.
    if invoice.parcel_id is None:
        return []
    result = await db.execute(
        select(MemberParcel)
        .options(selectinload(MemberParcel.member).selectinload(Member.email_addresses))
        .where(
            MemberParcel.parcel_id == invoice.parcel_id,
            current_tenant_filter(),
            MemberParcel.is_invoice_address.is_(True),
        )
    )
    return [a.member for a in result.scalars().all()]


async def copy_email_recipients(db: AsyncSession, invoice: Invoice, copy: InvoiceCopy) -> List[Tuple[Member, str]]:
    """(member, email) for everyone on `copy` who gets invoices by
    email: email notifications on and an address on file."""
    return [
        (m, _primary_address(m)) for m in await _copy_members(db, invoice, copy)
        if m.email_notifications and m.email_addresses
    ]


async def copies_to_print(db: AsyncSession, invoice: Invoice) -> List[InvoiceCopy]:
    """The copies of `invoice` that nobody on them can be emailed at."""
    return [c for c in invoice_copies(invoice) if not await copy_email_recipients(db, invoice, c)]


async def _send_to_copies(db: AsyncSession, invoice: Invoice, render_pdf, build_mail) -> Tuple[int, int]:
    """Emails each copy of `invoice` to the people on it. `render_pdf(copy)`
    returns (filename, bytes); `build_mail(member)` returns (subject, html).
    One email per address, even if it turns up on two copies. Returns
    (emails sent, copies nobody could be emailed at)."""
    sent_count, unreached = 0, 0
    seen: set = set()
    for copy in invoice_copies(invoice):
        recipients = [(m, a) for m, a in await copy_email_recipients(db, invoice, copy) if a.lower() not in seen]
        if not recipients:
            unreached += 1
            continue
        filename, pdf_bytes = render_pdf(copy)
        for member, address in recipients:
            seen.add(address.lower())
            subject, html = build_mail(member)
            if await send_email(address, subject, html, db=db, attachments=[(filename, pdf_bytes, "application/pdf")]):
                sent_count += 1
    return sent_count, unreached


async def send_invoice_email(
    request: Request, db: AsyncSession, invoice: Invoice, run: InvoiceRun, pdf_context: dict,
) -> bool:
    """Emails `invoice` to everyone on its copies who can be reached by
    email, each with the PDF of their own copy (issue #396). Returns
    whether at least one email was sent; sets invoice.emailed_at then.
    Copies nobody could be emailed at are left for the print bundle.
    Caller commits."""
    club_name = pdf_context["footer_context"].club_name
    body = (
        t_for(request, "email.invoice_delivery.body", club_name=club_name, parcel_number=invoice.parcel.plot_number, due_date=run.due_date.strftime("%d.%m.%Y"))
        if invoice.parcel else
        t_for(request, "email.invoice_delivery.body_member", club_name=club_name, due_date=run.due_date.strftime("%d.%m.%Y"))
    )
    subject = t_for(request, "email.invoice_delivery.subject", invoice_number=invoice.invoice_number, club_name=club_name)
    filename = invoice_pdf_filename(invoice, run)

    def render_pdf(copy):
        return filename, render_invoice_pdf(invoice_pdf_data_from_invoice(invoice, run, copy), **pdf_context)

    def build_mail(member):
        return subject, f"""
    <html><body style="font-family: sans-serif;">
    <p>{t_for(request, "email.invoice_delivery.greeting", name=escape(member.full_name))}</p>
    <p>{body}</p>
    </body></html>
    """

    sent_count, _ = await _send_to_copies(db, invoice, render_pdf, build_mail)
    if sent_count:
        invoice.emailed_at = datetime.now(timezone.utc)
    return sent_count > 0


async def deliver_reminder(
    request: Request, db: AsyncSession, invoice: Invoice, run: InvoiceRun,
    fee_amount: Optional[Decimal], message: Optional[str], created_by_id: Optional[str], pdf_context: dict,
) -> InvoiceReminder:
    """Creates and delivers the next reminder for `invoice` (issue #59):
    level is one past however many already exist. Delivered like the
    invoice itself, copy by copy (issue #396): emailed to whoever on a
    copy can be reached, the other copies are left as a PDF for postal
    sending (see the reminder PDF route). delivery_method records the
    outcome: "email", "print", or "both" when some copies went by email
    and others need printing. Caller commits."""
    next_level = max((r.level for r in invoice.reminders), default=0) + 1
    reminder = InvoiceReminder(
        level=next_level, fee_amount=fee_amount, message=message or None,
        delivery_method="print", created_by_id=created_by_id,
    )
    invoice.reminders.append(reminder)
    await db.flush()

    club_name = pdf_context["footer_context"].club_name
    subject = t_for(
        request, "email.reminder_delivery.subject",
        invoice_number=invoice.invoice_number, level=next_level, club_name=club_name,
    )
    filename = reminder_pdf_filename(reminder, invoice, run)

    def render_pdf(copy):
        return filename, render_reminder_pdf(reminder_pdf_data_from_reminder(reminder, invoice, run, copy), **pdf_context)

    def build_mail(member):
        return subject, f"""
        <html><body style="font-family: sans-serif;">
        <p>{t_for(request, "email.reminder_delivery.greeting", name=escape(member.full_name))}</p>
        <p>{t_for(request, "email.reminder_delivery.body", club_name=club_name, invoice_number=invoice.invoice_number)}</p>
        </body></html>
        """

    sent_count, unreached = await _send_to_copies(db, invoice, render_pdf, build_mail)
    if sent_count:
        reminder.delivery_method = "both" if unreached else "email"
    return reminder


def render_all_copies_pdf(invoice: Invoice, run: InvoiceRun, pdf_context: dict, copies: Optional[List[InvoiceCopy]] = None) -> bytes:
    """`invoice` as one PDF with every copy (or the given ones), one
    after the other -- for the download and the cloud folder."""
    copies = copies or invoice_copies(invoice)
    if len(copies) == 1:
        return render_invoice_pdf(invoice_pdf_data_from_invoice(invoice, run, copies[0]), **pdf_context)
    return render_invoice_bundle_pdf([invoice_pdf_data_from_invoice(invoice, run, c) for c in copies], **pdf_context)


def render_reminder_copies_pdf(
    reminder: InvoiceReminder, invoice: Invoice, run: InvoiceRun, pdf_context: dict, copies: List[InvoiceCopy],
) -> bytes:
    if len(copies) == 1:
        return render_reminder_pdf(reminder_pdf_data_from_reminder(reminder, invoice, run, copies[0]), **pdf_context)
    return render_reminder_bundle_pdf(
        [reminder_pdf_data_from_reminder(reminder, invoice, run, c) for c in copies], **pdf_context,
    )


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

    pdf_bytes = render_all_copies_pdf(invoice, run, pdf_context)
    filename = invoice_pdf_filename(invoice, run)

    try:
        await provider.upload_file(folder.relative_path, filename, pdf_bytes)
    except CloudStorageError:
        return False

    invoice.uploaded_to_cloud_at = datetime.now(timezone.utc)
    return True


async def build_print_bundle(
    db: AsyncSession, items: List[Tuple[Invoice, InvoiceCopy]], run: InvoiceRun, pdf_context: dict,
) -> bytes:
    """Merges the given invoice copies into one print-ready PDF (issue
    #58's "merge PDFs to one big one so we can print it") and marks
    their invoices as printed. The caller picks the copies (see the
    router: copies_to_print) and commits."""
    data = [invoice_pdf_data_from_invoice(invoice, run, copy) for invoice, copy in items]
    now = datetime.now(timezone.utc)
    for invoice, _ in items:
        invoice.printed_at = now
    return render_invoice_bundle_pdf(data, **pdf_context)
