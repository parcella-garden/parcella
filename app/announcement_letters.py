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

from app.pdf_utils import data_uri_only_fetcher
from app.l10n import format_address_lines
from app.models import Announcement, Member
from app.pdf_chrome import ADDRESS_WINDOW_CSS, OrgFooterContext, org_footer_html, sender_line, wrap_document

LETTER_CSS = ADDRESS_WINDOW_CSS + """
@page { @bottom-right { content: none; } }
.letter + .letter { page-break-before: always; }
.letter-head { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1.2cm; }
.letter-date { color: #4b5563; white-space: nowrap; }
.letter h1 { font-size: 13pt; margin: 0 0 0.5cm 0; color: #1f2937; }
.letter .body { line-height: 1.45; }
.letter .body img { max-width: 100%; }
"""


def _letter_html(announcement: Announcement, members: List[Member], sender: str, region: str, today: date) -> str:
    """One letter to `members` -- usually one person; several who share
    a postal address for a message to picked parcels (issue #397), all
    named in the address window."""
    first = members[0]
    address_lines = format_address_lines(first.street, first.postal_code, first.city, region)
    recipient = "<br>".join(escape(line) for line in [*(m.full_name for m in members), *address_lines])
    return f"""
    <div class="letter">
        <div class="letter-head">
            <div class="address-window">
                <div class="sender-line">{escape(sender)}</div>
                <div class="recipient">{recipient}</div>
            </div>
            <div class="letter-date din-info">{today.strftime('%d.%m.%Y')}</div>
        </div>
        <h1>{escape(announcement.title)}</h1>
        <div class="body">{announcement.body_html}</div>
    </div>
    """


def render_announcement_letters_pdf(
    announcement: Announcement, letters: List[List[Member]], footer_context: OrgFooterContext,
    logo_path: Optional[Path], region: str, language: str, today: Optional[date] = None,
) -> bytes:
    """One PDF, one letter per entry of `letters` (Audience.letter_groups,
    in the given order), each addressed to the members in it. Caller
    passes only members with a postal address (resolve_audience)."""
    today = today or date.today()
    sender = sender_line(footer_context.club_name, footer_context.address_lines)
    body = "".join(_letter_html(announcement, group, sender, region, today) for group in letters)
    html_doc = wrap_document(
        body, footer_context.club_name, logo_path, org_footer_html(footer_context, language),
        language, extra_css=LETTER_CSS, din_marks=True,
    )
    return HTML(string=html_doc, url_fetcher=data_uri_only_fetcher()).write_pdf()
