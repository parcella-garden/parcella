"""
Renders a single annual invoice as a PDF (issue #57) -- shares its page
chrome (header/footer/@page, "Page X of Y") with every other PDF in
this app via app/pdf_chrome.py, so it looks consistent with the rest
of the app's printed output. Invoices originated this look; see
app/pdf_chrome.py's module docstring for why it was later extracted
into a shared module rather than left duplicated per generator.

render_invoice_pdf() takes plain values rather than an Invoice ORM
object so it works identically for a real, numbered, persisted invoice
and for a not-yet-persisted preview (see app/invoice_generation.py's
compute_invoices_for_run) -- the router builds an InvoicePdfData from
whichever source it has.
"""
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import List, Optional

from weasyprint import HTML

from app.pdf_chrome import ADDRESS_WINDOW_CSS, wrap_document, org_footer_html, sender_line, OrgFooterContext
from app.l10n import format_money
from app.i18n import translate

# Invoice/reminder-specific CSS, appended after app/pdf_chrome.py's
# shared page chrome (@page, body, #header, #footer base rules -- the
# three-column footer layout itself is shared now, not invoice-only).
EXTRA_CSS = ADDRESS_WINDOW_CSS + """
.meta-block { display: flex; justify-content: space-between; margin-bottom: 0.8cm; }
.invoice-meta td { padding: 1px 6px; }
.invoice-meta td:first-child { color: #6b7280; }
.invoice-meta td:last-child { font-weight: bold; text-align: right; }
h1 { font-size: 14pt; margin-bottom: 0.1cm; color: #1f2937; }
.parcel-line { color: #6b7280; margin-bottom: 0.5cm; font-size: 9.5pt; }
table.items { width: 100%; border-collapse: collapse; margin-top: 0.3cm; }
table.items th { text-align: left; font-size: 9pt; text-transform: uppercase; color: #4b5563; border-bottom: 2px solid #2f6f3e; padding: 6px 8px; }
table.items td { padding: 7px 8px; border-bottom: 1px solid #e5e7eb; vertical-align: top; }
table.items td.num { text-align: right; white-space: nowrap; }
table.items small { color: #6b7280; }
table.items tfoot td { border-bottom: none; border-top: 2px solid #2f6f3e; font-weight: bold; padding-top: 8px; }
.footer-text { margin-top: 0.8cm; font-size: 9.5pt; color: #374151; white-space: pre-line; }
.preview-banner {
    background: #fef3c7; color: #92400e; padding: 6px 10px; border-radius: 4px;
    font-size: 9pt; margin-bottom: 0.4cm; text-align: center;
}
.invoice-block + .invoice-block { page-break-before: always; }
"""


@dataclass
class InvoicePdfLineItem:
    order_number: int
    name: str
    description: Optional[str]
    quantity: Decimal
    unit_price: Decimal
    line_total: Decimal


@dataclass
class InvoicePdfData:
    invoice_number: str  # placeholder like "Preview" if not yet finalized
    issued_date: date
    due_date: date
    subject: str
    recipient_names: str
    recipient_address: str
    parcel_plot_number: Optional[str]
    parcel_area_sqm: Optional[float]
    line_items: List[InvoicePdfLineItem]
    subtotal: Decimal
    footer_text: Optional[str]
    is_preview: bool = False


@dataclass
class ReminderPdfData:
    invoice_number: str
    level: int
    issued_date: date  # original invoice's issued date
    due_date: date  # original invoice's due date
    sent_date: date
    recipient_names: str
    recipient_address: str
    original_subtotal: Decimal
    paid_total: Decimal
    previous_fees_total: Decimal
    fee_amount: Decimal
    amount_due: Decimal
    message: Optional[str]


def invoice_pdf_data_from_invoice(invoice, run) -> InvoicePdfData:
    """Builds an InvoicePdfData from a real, persisted Invoice (with
    .line_items and .parcel eagerly loaded) and its InvoiceRun --
    shared by the single-invoice PDF route, the email-attachment path,
    and the print-bundle builder (see app/invoice_delivery.py), so
    there's exactly one place that knows how to turn an Invoice row
    into rendered PDF data. A member invoice (no parcel) simply omits
    the parcel line -- see _invoice_body_html."""
    return InvoicePdfData(
        invoice_number=invoice.invoice_number,
        issued_date=run.issued_date, due_date=run.due_date, subject=run.subject,
        recipient_names=invoice.recipient_names, recipient_address=invoice.recipient_address,
        parcel_plot_number=invoice.parcel.plot_number if invoice.parcel else None,
        parcel_area_sqm=invoice.parcel.area_sqm if invoice.parcel else None,
        line_items=[
            InvoicePdfLineItem(
                order_number=li.order_number, name=li.name, description=li.description,
                quantity=li.quantity, unit_price=li.unit_price, line_total=li.line_total,
            ) for li in sorted(invoice.line_items, key=lambda li: li.order_number)
        ],
        subtotal=invoice.subtotal, footer_text=run.footer_text, is_preview=False,
    )


def reminder_pdf_data_from_reminder(reminder, invoice, run) -> ReminderPdfData:
    """Builds a ReminderPdfData from a real, persisted InvoiceReminder
    (with `invoice.reminders`/`invoice.payments` eagerly loaded) and
    its Invoice/InvoiceRun. All amounts are computed from *current*
    live state (payments/other reminders' fees), not snapshotted at
    send time -- re-downloading an old reminder shows today's true
    balance rather than a frozen historical one, which is fine for a
    dunning notice (unlike Invoice's own recipient/address snapshot,
    there's no legal requirement here for the numbers to stay fixed)."""
    previous_fees_total = sum(
        (Decimal(str(r.fee_amount)) for r in invoice.reminders if r.level < reminder.level and r.fee_amount),
        Decimal("0"),
    )
    fee_amount = Decimal(str(reminder.fee_amount)) if reminder.fee_amount else Decimal("0")
    paid_total = Decimal(str(invoice.paid_total))
    original_subtotal = Decimal(str(invoice.subtotal))
    amount_due = max(Decimal("0"), original_subtotal + previous_fees_total + fee_amount - paid_total)
    return ReminderPdfData(
        invoice_number=invoice.invoice_number, level=reminder.level,
        issued_date=run.issued_date, due_date=run.due_date, sent_date=reminder.sent_at.date(),
        recipient_names=invoice.recipient_names, recipient_address=invoice.recipient_address,
        original_subtotal=original_subtotal, paid_total=paid_total,
        previous_fees_total=previous_fees_total, fee_amount=fee_amount, amount_due=amount_due,
        message=reminder.message,
    )


def _invoice_subject_slug(invoice) -> str:
    """The parcel's plot number, or -- for a member invoice with no
    parcel -- the member's last name, used as the filename segment
    identifying who/what an invoice PDF is for."""
    return invoice.parcel.plot_number if invoice.parcel else invoice.member.last_name


def invoice_pdf_filename(invoice, run) -> str:
    """Filename for `invoice`'s PDF -- {issued date YYYYMMDD}_{parcel
    plot number, or the member's last name for a member invoice}
    _invoice-{invoice number}.pdf, e.g. "20260724_G093_invoice-2026-500.pdf".
    Shared by the download route, email attachment, and cloud-storage
    upload (see app/invoice_delivery.py) so the naming stays consistent
    everywhere a PDF gets a filename. The invoice number's own "/" is
    swapped for "-" since it isn't valid in a filename -- the
    (club-configurable) invoice number format is otherwise left
    untouched."""
    date_part = run.issued_date.strftime("%Y%m%d")
    number_part = invoice.invoice_number.replace("/", "-")
    return f"{date_part}_{_invoice_subject_slug(invoice)}_invoice-{number_part}.pdf"


def reminder_pdf_filename(reminder, invoice, run) -> str:
    """Filename for a reminder's PDF -- {sent date YYYYMMDD}_{parcel
    plot number, or the member's last name}_reminder{level}-{invoice
    number}.pdf, mirroring invoice_pdf_filename's convention."""
    date_part = reminder.sent_at.strftime("%Y%m%d")
    number_part = invoice.invoice_number.replace("/", "-")
    return f"{date_part}_{_invoice_subject_slug(invoice)}_reminder{reminder.level}-{number_part}.pdf"


def _substitute_placeholders(text: Optional[str], data: InvoicePdfData) -> str:
    if not text:
        return ""
    try:
        return text.format(
            invoice_number=data.invoice_number,
            parcel_number=data.parcel_plot_number,
            invoice_address=f"{data.recipient_names}\n{data.recipient_address}",
            due_date=data.due_date.strftime("%d.%m.%Y"),
        )
    except (KeyError, IndexError):
        return text


_sender_line = sender_line  # moved to app/pdf_chrome.py, shared with announcement letters


def _invoice_body_html(data: InvoicePdfData, region: str, currency: str, language: str, sender_line: str) -> str:
    """The part of an invoice that's specific to it (recipient, meta,
    line items, footer text) -- everything except the page chrome
    (header/footer/@page CSS), which is shared across a whole document
    whether that document holds one invoice or a print bundle of many
    (see render_invoice_pdf / render_invoice_bundle_pdf)."""
    rows_html = []
    for li in data.line_items:
        desc_html = f"<br><small>{li.description}</small>" if li.description else ""
        # .normalize() strips trailing zeros (e.g. a DB-round-tripped
        # Numeric(10,2) 1.00 -> 1) so preview and finalized PDFs render
        # quantities identically regardless of Postgres's fixed scale.
        quantity_display = li.quantity.normalize()
        rows_html.append(f"""
        <tr>
            <td>{li.order_number}</td>
            <td>{li.name}{desc_html}</td>
            <td class="num">{quantity_display}</td>
            <td class="num">{format_money(li.unit_price, region, currency)}</td>
            <td class="num">{format_money(li.line_total, region, currency)}</td>
        </tr>
        """)

    preview_banner = (
        f'<div class="preview-banner">{translate("finances.pdf.preview_banner", language)}</div>'
        if data.is_preview else ""
    )
    footer_text_html = _substitute_placeholders(data.footer_text, data)

    return f"""
    <div class="invoice-block">
        {preview_banner}

        <div class="meta-block">
            <div class="address-window">
                <div class="sender-line">{sender_line}</div>
                <div class="recipient">{data.recipient_names}<br>{data.recipient_address.replace(chr(10), '<br>')}</div>
            </div>
            <table class="invoice-meta">
                <tr><td>{translate("finances.pdf.invoice_no", language)}</td><td>{data.invoice_number}</td></tr>
                <tr><td>{translate("finances.pdf.date", language)}</td><td>{data.issued_date.strftime('%d.%m.%Y')}</td></tr>
                <tr><td>{translate("finances.pdf.due_date", language)}</td><td>{data.due_date.strftime('%d.%m.%Y')}</td></tr>
            </table>
        </div>

        <h1>{data.subject}</h1>
        {f'''<div class="parcel-line">
            {translate("finances.pdf.parcel", language)} {data.parcel_plot_number}{f" · {data.parcel_area_sqm} m&sup2;" if data.parcel_area_sqm else ""}
        </div>''' if data.parcel_plot_number else ''}

        <table class="items">
            <thead>
                <tr>
                    <th>#</th>
                    <th>{translate("finances.pdf.col_description", language)}</th>
                    <th>{translate("finances.pdf.col_qty", language)}</th>
                    <th>{translate("finances.pdf.col_unit_price", language)}</th>
                    <th>{translate("finances.pdf.col_total", language)}</th>
                </tr>
            </thead>
            <tbody>
                {''.join(rows_html)}
            </tbody>
            <tfoot>
                <tr><td colspan="4">{translate("finances.pdf.subtotal", language)}</td><td class="num">{format_money(data.subtotal, region, currency)}</td></tr>
            </tfoot>
        </table>

        {f'<div class="footer-text">{footer_text_html}</div>' if footer_text_html else ''}
    </div>
    """


def _reminder_body_html(data: ReminderPdfData, region: str, currency: str, language: str, sender_line: str) -> str:
    """The part of a reminder that's specific to it -- same page chrome
    as an invoice (see render_reminder_pdf), but a much simpler body:
    a reference back to the original invoice, an itemized amount-due
    breakdown (only showing rows that actually apply), and an optional
    free-text message (issue #59's "let me decide whether to add a
    fee" -- fee/previous-fee rows just don't render when there's
    nothing to show)."""
    rows = [(translate("finances.reminder_pdf.row_original_amount", language), data.original_subtotal)]
    if data.paid_total:
        rows.append((translate("finances.reminder_pdf.row_paid", language), -data.paid_total))
    if data.previous_fees_total:
        rows.append((translate("finances.reminder_pdf.row_previous_fees", language), data.previous_fees_total))
    if data.fee_amount:
        rows.append((translate("finances.reminder_pdf.row_this_fee", language), data.fee_amount))

    rows_html = "".join(
        f'<tr><td>{label}</td><td class="num">{format_money(amount, region, currency)}</td></tr>'
        for label, amount in rows
    )
    message_html = f'<div class="footer-text">{data.message}</div>' if data.message else ""

    return f"""
    <div class="invoice-block">
        <div class="meta-block">
            <div class="address-window">
                <div class="sender-line">{sender_line}</div>
                <div class="recipient">{data.recipient_names}<br>{data.recipient_address.replace(chr(10), '<br>')}</div>
            </div>
            <table class="invoice-meta">
                <tr><td>{translate("finances.pdf.invoice_no", language)}</td><td>{data.invoice_number}</td></tr>
                <tr><td>{translate("finances.pdf.date", language)}</td><td>{data.sent_date.strftime('%d.%m.%Y')}</td></tr>
                <tr><td>{translate("finances.pdf.due_date", language)}</td><td>{data.due_date.strftime('%d.%m.%Y')}</td></tr>
            </table>
        </div>

        <h1>{translate("finances.reminder_pdf.heading", language, level=data.level)}</h1>
        <div class="parcel-line">
            {translate("finances.reminder_pdf.reference_line", language, invoice_number=data.invoice_number, date=data.issued_date.strftime('%d.%m.%Y'))}
        </div>

        <p>{translate("finances.reminder_pdf.intro", language)}</p>

        <table class="items">
            <tbody>
                {rows_html}
            </tbody>
            <tfoot>
                <tr><td>{translate("finances.pdf.subtotal", language)}</td><td class="num">{format_money(data.amount_due, region, currency)}</td></tr>
            </tfoot>
        </table>

        <p class="footer-text">{translate("finances.reminder_pdf.closing", language)}</p>
        {message_html}
    </div>
    """


def render_invoice_pdf(
    data: InvoicePdfData, footer_context: OrgFooterContext, logo_path: Optional[Path],
    region: str, currency: str, language: str = "en",
) -> bytes:
    footer_html = org_footer_html(footer_context, language)
    sender_line = _sender_line(footer_context.club_name, footer_context.address_lines)
    html_doc = wrap_document(
        _invoice_body_html(data, region, currency, language, sender_line),
        footer_context.club_name, logo_path, footer_html, language, extra_css=EXTRA_CSS,
    )
    return HTML(string=html_doc).write_pdf()


def render_invoice_bundle_pdf(
    items: List[InvoicePdfData], footer_context: OrgFooterContext, logo_path: Optional[Path],
    region: str, currency: str, language: str = "en",
) -> bytes:
    """Same rendering as render_invoice_pdf, but for many invoices in
    one PDF (issue #58's "merge PDFs to one big one so we can print
    it") -- a page-break-before between each invoice's block, sharing
    one @page header/footer/page-numbering across the whole bundle
    rather than resetting per invoice, since it's meant to be printed
    and handled as a single stack."""
    footer_html = org_footer_html(footer_context, language)
    sender_line = _sender_line(footer_context.club_name, footer_context.address_lines)
    body_html = "".join(_invoice_body_html(data, region, currency, language, sender_line) for data in items)
    html_doc = wrap_document(
        body_html, footer_context.club_name, logo_path, footer_html, language, extra_css=EXTRA_CSS,
    )
    return HTML(string=html_doc).write_pdf()


def render_reminder_pdf(
    data: ReminderPdfData, footer_context: OrgFooterContext, logo_path: Optional[Path],
    region: str, currency: str, language: str = "en",
) -> bytes:
    """Same page chrome as render_invoice_pdf (issue #59) -- header,
    three-column footer, page numbering -- with a reminder-specific body."""
    footer_html = org_footer_html(footer_context, language)
    sender_line = _sender_line(footer_context.club_name, footer_context.address_lines)
    html_doc = wrap_document(
        _reminder_body_html(data, region, currency, language, sender_line),
        footer_context.club_name, logo_path, footer_html, language, extra_css=EXTRA_CSS,
    )
    return HTML(string=html_doc).write_pdf()
