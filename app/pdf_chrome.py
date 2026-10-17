"""
Shared PDF page chrome for every "formal document" PDF in this app --
invoices/reminders, the birthday calendar, the work-session attendee
sheet, the meeting sign-in sheet, and the announcement flyer all use
this SAME visual template: a DIN-style fixed header (club logo at the
true physical page edge, club name centered across the full sheet),
the same color/font palette, a running footer, and localized
"Page X of Y" page numbering. The flyer still always renders as exactly
one page (see app/print_publisher.py's shortening loop) -- it just also
shows "Page 1 of 1" now rather than no page number at all.

Deliberately the one shared source now, not independently duplicated
per generator: this app's invoice PDF originated the look, and each
later document was asked to match it "from now on" -- see docs/ADR/0043
for the decision to extract this rather than keep copy-pasting the same
CSS block into every new generator, and docs/ADR/0045 for later folding
the flyer in too and making the footer content itself (not just its
styling) universal.

Every document supplies its own BODY content (table columns, address
blocks, whatever's specific to it), but the FOOTER content is now
shared as well via `OrgFooterContext`/`org_footer_html()` below: club
identity, register-court/number, and bank details on every document,
not just invoices -- an explicit choice (issue: "streamline the footer
across all PDFs, bank details included") over showing bank details on
invoices only. `load_org_footer_context()` reads straight from
`ClubSetting` rather than going through the finances module: this data
is club-identity/legal info, not finances-owned, and every PDF-
producing router needs it regardless of which optional modules a club
has enabled.
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import active_member_filter
from app.i18n import translate
from app.models import ClubSetting, ClubBoardMember, Member
from app.pdf_utils import file_to_data_uri


@dataclass
class OrgFooterContext:
    """Everything the shared footer shows: club identity/address,
    register-court disclosure, and bank details. Any field left blank
    (e.g. a club that hasn't entered bank details yet) simply omits
    that line -- see org_footer_html()."""
    club_name: str
    address_lines: List[str] = field(default_factory=list)
    register_court: str = ""
    register_number: str = ""
    bank_name: str = ""
    bank_iban: str = ""
    bank_bic: str = ""
    bank_account_owner: str = ""
    board_members: List[str] = field(default_factory=list)


async def load_org_footer_context(db: AsyncSession, club_name: str) -> OrgFooterContext:
    """Loads the address/register/bank ClubSettings every PDF footer
    needs. `club_name` is passed in rather than reloaded here since
    every caller already has it from load_branding() for the header."""
    result = await db.execute(
        select(ClubSetting).where(ClubSetting.key.in_([
            "verein_strasse", "verein_plz", "verein_ort",
            "bank_name", "bank_iban", "bank_bic", "bank_account_owner",
            "registergericht", "vereinsnummer",
        ]))
    )
    settings_map = {e.key: e.value for e in result.scalars().all()}
    address_lines = [
        line for line in [settings_map.get("verein_strasse"), " ".join(
            filter(None, [settings_map.get("verein_plz"), settings_map.get("verein_ort")])
        )] if line
    ]

    # Board members (issue #121): same active-member scoping and
    # last_name/first_name ordering as their admin -> settings picker
    # (app/routers/admin.py), so a member removed/deactivated after
    # being listed doesn't keep showing up on printed documents.
    board_result = await db.execute(
        select(Member)
        .join(ClubBoardMember, ClubBoardMember.member_id == Member.id)
        .where(active_member_filter())
        .order_by(Member.last_name, Member.first_name)
    )
    board_members = [m.full_name for m in board_result.scalars().all()]

    return OrgFooterContext(
        club_name=club_name,
        address_lines=address_lines,
        register_court=settings_map.get("registergericht") or "",
        register_number=settings_map.get("vereinsnummer") or "",
        bank_name=settings_map.get("bank_name") or "",
        bank_iban=settings_map.get("bank_iban") or "",
        bank_bic=settings_map.get("bank_bic") or "",
        bank_account_owner=settings_map.get("bank_account_owner") or "",
        board_members=board_members,
    )


def org_footer_html(context: OrgFooterContext, language: str) -> str:
    """Three-column footer content (issue #74, later made universal):
    organization identity, register-court info, and bank details, laid
    out side by side via the shared flex #footer rule in page_css().
    "Page X of Y" is the visual fourth column, but lives in its own
    @bottom-right margin box (see page_css() below) rather than here,
    since WeasyPrint only resolves page counters directly inside a
    margin box's own `content`, not inside the DOM of an element placed
    there via `content: element(...)`."""
    org_lines = [context.club_name, *context.address_lines]

    register_line = " ".join(filter(None, [context.register_court, context.register_number]))
    register_lines = [register_line] if register_line else []
    if context.board_members:
        register_lines.append(translate("pdf.board_members", language, names=", ".join(context.board_members)))

    bank_line = " · ".join(filter(None, [context.bank_name, f"BIC {context.bank_bic}" if context.bank_bic else ""]))
    bank_lines = [b for b in [
        bank_line,
        f"IBAN {context.bank_iban}" if context.bank_iban else "",
        translate("pdf.account_holder", language, name=context.bank_account_owner) if context.bank_account_owner else "",
    ] if b]

    def column(lines: List[str]) -> str:
        return f'<div class="footer-col">{"".join(f"<div>{line}</div>" for line in lines)}</div>'

    return column(org_lines) + column(register_lines) + column(bank_lines)


def page_css(language: str, bottom_margin: str = "2.6cm", extra_css: str = "") -> str:
    """@page CSS with localized "Page X of Y" page numbering (baked
    into the CSS itself, not translated in the HTML body, since
    WeasyPrint only resolves page counters directly inside a margin
    box's own `content` property -- see app/invoice_pdf.py's original
    _page_css docstring for the full explanation, still accurate here).
    `bottom_margin` defaults to the height every document's three-column
    org/register/bank footer needs now that it's universal."""
    page_word = translate("pdf.page_label", language)
    of_word = translate("pdf.of_label", language)
    return f"""
@page {{
    size: A4;
    margin: 2.2cm 1.5cm {bottom_margin} 1.5cm;
    @bottom-left {{ content: element(footer); width: 15.7cm; }}
    @bottom-right {{
        content: "{page_word} " counter(page) " {of_word} " counter(pages);
        font-size: 8pt; color: #6b7280;
    }}
}}
body {{ margin: 0; font-family: 'DejaVu Sans', sans-serif; color: #1f2937; font-size: 10.5pt; }}
/* True-page-edge header: the negative top/left offsets exactly cancel
   the @page margin above, so the logo sits at the physical page
   corner and the club name is centered across the full 21cm sheet,
   not just the printable area -- WeasyPrint's containing block for
   position:fixed here is the page's own content box (inset by the
   @page margin), not the raw sheet, so this cancels that inset back
   out to the true page corner. */
#header {{ position: fixed; top: -2.2cm; left: -1.5cm; width: 21cm; height: 1.8cm; border-bottom: 2px solid #2f6f3e; }}
#header .header-logo {{ position: absolute; left: 0.5cm; top: 0.3cm; }}
#header .header-logo img {{ max-height: 50px; }}
#header .club-name {{
    position: absolute; left: 0; top: 0.65cm; width: 21cm; text-align: center;
    font-size: 13pt; font-weight: bold; color: #2f6f3e; white-space: nowrap;
}}
#footer {{
    position: running(footer); font-size: 7.5pt; color: #6b7280;
    border-top: 1px solid #d1d5db; padding-top: 6px;
    display: flex; gap: 0.6cm; line-height: 1.4;
}}
#footer .footer-col {{ flex: 1; min-width: 0; }}
#footer .footer-col:nth-child(1) {{ flex: 0.85; }}
#footer .footer-col:nth-child(3) {{ flex: 1.3; }}
{extra_css}
"""


# DIN 5008 Form A address window, shared by every document that goes out
# in a windowed envelope (invoices, reminders, announcement letters --
# issue #242). Append to a document's extra_css. Page margin-top is
# 2.2cm, so the 0.5cm padding-top here lands the sender line at 2.7cm
# from the page edge and the 1.8cm sender-line box ends exactly at
# 4.5cm, where the Anschriftzone (recipient address) must start;
# padding-left 0.5cm plus the 1.5cm page margin lands the whole
# window's left edge at the standard 2.0cm.
ADDRESS_WINDOW_CSS = """
.address-window { width: 8.5cm; padding-top: 0.5cm; padding-left: 0.5cm; box-sizing: content-box; }
.sender-line {
    height: 1.8cm; display: flex; align-items: flex-end;
    font-size: 7.5pt; color: #4b5563; border-bottom: 0.5pt solid #9ca3af;
    margin-bottom: 2pt;
}
.recipient { white-space: pre-line; line-height: 1.5; }
"""


def sender_line(club_name: str, club_address_lines: List[str]) -> str:
    """The DIN 5008 Form A "Einzeilige Rücksendeangabe" -- the club's
    own name/address compressed onto one small line, printed directly
    above the recipient's address so it stays visible through a
    windowed envelope (and tells the recipient/post office who to
    return the letter to)."""
    return " · ".join(filter(None, [club_name, *club_address_lines]))


def header_html(club_name: str, logo_path: Optional[Path]) -> str:
    logo_data_uri = file_to_data_uri(logo_path)
    logo_block = f'<img src="{logo_data_uri}">' if logo_data_uri else ""
    return f"""<div id="header">
        <div class="header-logo">{logo_block}</div>
        <div class="club-name">{club_name}</div>
    </div>"""


def wrap_document(
    body_html: str, club_name: str, logo_path: Optional[Path], footer_html: str,
    language: str, extra_css: str = "", bottom_margin: str = "2.6cm",
) -> str:
    """Wraps `body_html` in the shared page chrome (header/footer/@page
    rules); `extra_css` is appended after the shared CSS so a document
    can add its own rules (table columns, address blocks, ...) without
    a second <style> tag."""
    return f"""
    <html>
    <head><meta charset="utf-8"><style>{page_css(language, bottom_margin, extra_css)}</style></head>
    <body>
        {header_html(club_name, logo_path)}
        <div id="footer">{footer_html}</div>
        {body_html}
    </body>
    </html>
    """
