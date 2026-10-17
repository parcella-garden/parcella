"""
Letter channel for announcements to filtered members (issue #242): one
PDF with one addressed letter per recipient, ready to print, fold and
put into windowed envelopes -- for the members a message can't reach by
email (see resolve_audience() in app/announcement_mailer.py).

Shares the page chrome with every other PDF in the app
(app/pdf_chrome.py: header, three-column org/bank footer) and the
DIN 5008 Form A address window with invoices (ADDRESS_WINDOW_CSS,
sender_line). Each letter starts on a new page. The running "Page X of
Y" counter is switched off: it would count across the whole bundle
("Page 7 of 40") and mean nothing on an individual letter.

The body is the announcement's body_html -- already sanitized at save
time (app/announcement_utils.render_markdown_to_html) -- so it's
embedded as is -- the same text the email carries, with no added
salutation (the author writes their own greeting, once, for both).
Names and addresses come from member records and are escaped. The
announcement's image isn't printed: letters are meant to be plain and
cheap to print.
"""
from datetime import date
from pathlib import Path
from typing import List, Optional

from markupsafe import escape
from weasyprint import HTML

from app.l10n import format_address_lines
from app.models import Announcement, Member
from app.pdf_chrome import ADDRESS_WINDOW_CSS, OrgFooterContext, org_footer_html, sender_line, wrap_document

LETTER_CSS = ADDRESS_WINDOW_CSS + """
@page { @bottom-right { content: none; } }
.letter + .letter { page-break-before: always; }
.letter-head { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1.2cm; }
.letter-date { color: #4b5563; padding-top: 2.3cm; white-space: nowrap; }
.letter h1 { font-size: 13pt; margin: 0 0 0.5cm 0; color: #1f2937; }
.letter .body { line-height: 1.45; }
.letter .body img { max-width: 100%; }
"""


def _letter_html(announcement: Announcement, member: Member, sender: str, region: str, today: date) -> str:
    address_lines = format_address_lines(member.street, member.postal_code, member.city, region)
    recipient = "<br>".join(escape(line) for line in [member.full_name, *address_lines])
    return f"""
    <div class="letter">
        <div class="letter-head">
            <div class="address-window">
                <div class="sender-line">{escape(sender)}</div>
                <div class="recipient">{recipient}</div>
            </div>
            <div class="letter-date">{today.strftime('%d.%m.%Y')}</div>
        </div>
        <h1>{escape(announcement.title)}</h1>
        <div class="body">{announcement.body_html}</div>
    </div>
    """


def render_announcement_letters_pdf(
    announcement: Announcement, members: List[Member], footer_context: OrgFooterContext,
    logo_path: Optional[Path], region: str, language: str, today: Optional[date] = None,
) -> bytes:
    """One PDF, one letter per member (in the given order). Caller
    passes only members with a postal address (resolve_audience)."""
    today = today or date.today()
    sender = sender_line(footer_context.club_name, footer_context.address_lines)
    body = "".join(_letter_html(announcement, m, sender, region, today) for m in members)
    html_doc = wrap_document(
        body, footer_context.club_name, logo_path, org_footer_html(footer_context, language),
        language, extra_css=LETTER_CSS,
    )
    return HTML(string=html_doc).write_pdf()
