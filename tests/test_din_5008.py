"""
Issue #398: letters, invoices and reminders put the address where a
DIN 5008 Form B window envelope shows it -- return address in the zone
from 45 mm, recipient from 62.7 mm (to 90 mm), 20 mm from the left --
and carry fold marks at 105/210 mm and a punch mark at 148.5 mm.
Measured from the rendered PDF, so the layout can't drift unnoticed.
"""
import io
from datetime import date
from decimal import Decimal
from types import SimpleNamespace

from pypdf import PdfReader

from app.announcement_letters import render_announcement_letters_pdf
from app.announcement_utils import render_markdown_to_html
from app.invoice_pdf import InvoicePdfData, InvoicePdfLineItem, render_invoice_pdf
from app.pdf_chrome import DIN_MARKS_HTML, OrgFooterContext, wrap_document

MM = 72 / 25.4  # PDF points per millimetre
PAGE_HEIGHT_MM = 297

FOOTER = OrgFooterContext(
    club_name="KGV Beispiel e.V.", address_lines=["Gartenweg 1", "04103 Leipzig"], register_court="",
    register_number="", bank_name="", bank_iban="", bank_bic="", bank_account_owner="", board_members=[],
)


def _text_positions(pdf_bytes: bytes) -> dict:
    """First page: text fragment -> (x mm from the left, y mm from the top)."""
    positions = {}

    def visit(text, cm, tm, font_dict, font_size):
        if text.strip():
            x, y = tm[4] * cm[0] + cm[4], tm[5] * cm[3] + cm[5]
            positions.setdefault(text.strip(), (x / MM, PAGE_HEIGHT_MM - y / MM))

    PdfReader(io.BytesIO(pdf_bytes)).pages[0].extract_text(visitor_text=visit)
    return positions


def _find(positions: dict, fragment: str):
    return next(pos for text, pos in positions.items() if fragment in text)


def _assert_form_b(pdf_bytes: bytes):
    positions = _text_positions(pdf_bytes)
    sender_x, sender_y = _find(positions, "Gartenweg 1 · 04103 Leipzig")
    name_x, name_y = _find(positions, "Anna Haus")
    _, city_y = _find(positions, "Lindenweg 1")
    assert 45 < sender_y < 62.7, sender_y          # return-address zone
    assert 62.7 < name_y < 90 and 62.7 < city_y < 90, (name_y, city_y)  # recipient zone
    assert 19.9 < name_x < 26 and 19.9 < sender_x < 26, (name_x, sender_x)  # 20 mm, float rounding


def test_letter_address_is_in_the_form_b_window():
    body = "Am Samstag ist Arbeitseinsatz."
    announcement = SimpleNamespace(title="Arbeitseinsatz", body_markdown=body, body_html=render_markdown_to_html(body))
    member = SimpleNamespace(full_name="Anna Haus", street="Lindenweg 1", postal_code="04103", city="Leipzig")
    _assert_form_b(render_announcement_letters_pdf(announcement, [[member]] if _takes_groups() else [member], FOOTER, None, "DE", "de"))


def test_invoice_address_is_in_the_form_b_window():
    data = InvoicePdfData(
        invoice_number="2026/1", issued_date=date(2026, 1, 1), due_date=date(2026, 2, 1), subject="Jahresrechnung",
        recipient_names="Anna Haus", recipient_address="Lindenweg 1\n04103 Leipzig",
        parcel_plot_number="12", parcel_area_sqm=300,
        line_items=[InvoicePdfLineItem(order_number=1, name="Pacht", description=None,
                                       quantity=Decimal(1), unit_price=Decimal(50), line_total=Decimal(50))],
        subtotal=Decimal(50), footer_text="",
    )
    _assert_form_b(render_invoice_pdf(data, FOOTER, None, "DE", "EUR", "de"))


def test_fold_and_punch_marks_only_where_asked():
    marks = ('top: 8.3cm', 'top: 12.65cm', 'top: 18.8cm')  # 105, 148.5, 210 mm minus the 22 mm top margin
    assert all(m in DIN_MARKS_HTML for m in marks)
    assert DIN_MARKS_HTML in wrap_document("<p>x</p>", "Club", None, "", "de", din_marks=True)
    assert DIN_MARKS_HTML not in wrap_document("<p>x</p>", "Club", None, "", "de")


def _takes_groups() -> bool:
    """Letters take one list of members per letter once #397 is in."""
    import inspect
    return "letters" in inspect.signature(render_announcement_letters_pdf).parameters
