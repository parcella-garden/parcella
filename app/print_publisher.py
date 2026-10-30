"""
Print channel for the announcements module: renders a one-page,
branded PDF notice from an Announcement, meant for physical posting
on the allotment grounds.

Shares its page chrome (header/footer/@page, "Page X of Y") with every
other PDF in this app via app/pdf_chrome.py -- see that module's
docstring and docs/ADR/0045 for why (it was originally left out as a
differently-shaped single-page document, then brought in line on
request). Still always exactly one page -- the shortening loop below is
unaffected, it just now also shows "Page 1 of 1" like every other
document instead of no page number at all.

Renders once with the full text (the manual print_text_override if the
admin set one, otherwise the full body). If that fits on one page,
done. If not, shortens paragraph-by-paragraph and re-renders each
attempt, stopping at the first one that fits -- adding a "read the
rest online" note with a QR code, but only once shortening actually
happened (untouched text never gets a QR code slapped on it) and only
if the website draft has genuinely been published (see
WebsiteConnector.get_public_url_if_published in app/website_connectors --
there's nothing public to point a QR code at until then, so the note
is simply omitted, not shown with a broken link).

If even a single paragraph still doesn't fit alongside the header,
footer, and image, generation stops and raises PrintTooLongError
rather than silently producing a multi-page "one-pager" or truncating
mid-sentence -- per the original design decision to ask a human in
that case.

The shortened text, once found, is written back onto
announcement.print_text_override so it's visible and freely editable
afterward, and so regenerating the PDF later doesn't have to redo the
same search.
"""
import base64
import io
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import qrcode
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from markupsafe import escape
from weasyprint import HTML

from app.models import Announcement, ClubSetting
from app.announcement_utils import render_markdown_to_html
from app.pdf_chrome import wrap_document, org_footer_html, OrgFooterContext
from app.pdf_utils import data_uri_only_fetcher, file_to_data_uri

# Issue #262: cloud folder every generated print PDF is also saved to,
# chosen on the admin integrations page. Unset = download only.
PRINT_CLOUD_FOLDER_SETTING = "announcements_print_cloud_folder"


async def load_print_cloud_folder(db: AsyncSession) -> Optional[str]:
    value = await db.scalar(select(ClubSetting.value).where(ClubSetting.key == PRINT_CLOUD_FOLDER_SETTING))
    return value or None


# Flyer-specific rules only -- @page/body/#header/#footer chrome now
# comes from app/pdf_chrome.py's page_css(). font-size/line-height stay
# a deliberate override: a physical notice meant to be read from a
# pinboard wants larger, airier text than the denser 10.5pt used by the
# tabular administrative documents sharing this chrome.
EXTRA_CSS = """
body { font-size: 11pt; line-height: 1.45; }
h1 { font-size: 18pt; margin-top: 0.6cm; margin-bottom: 0.4cm; color: #1f2937; }
.announcement-image { max-width: 100%; max-height: 7cm; display: block; margin: 0.3cm auto; }
.byline { font-size: 9.5pt; font-style: italic; color: #4b5563; margin: 0.2cm 0 0.4cm; }
.online-note { margin-top: 0.6cm; padding-top: 0.3cm; border-top: 1px dashed #9ca3af; font-size: 9pt; color: #4b5563; display: flex; align-items: center; gap: 0.4cm; }
.online-note img { width: 2.2cm; height: 2.2cm; }
"""


class PrintTooLongError(Exception):
    """Raised when even the shortest attempt (a single paragraph)
    still doesn't fit on one printed page. The router turns this into
    a FAILED AnnouncementDelivery asking a human to shorten the text
    manually, rather than silently producing a multi-page flyer."""


@dataclass
class PrintRenderResult:
    pdf_bytes: bytes
    was_shortened: bool
    qr_included: bool


def _qr_data_uri(url: str) -> str:
    img = qrcode.make(url)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def _split_paragraphs(markdown_text: str) -> List[str]:
    # Blank-line-separated paragraphs, the same convention Markdown
    # itself uses to tell paragraphs apart.
    return [p.strip() for p in markdown_text.split("\n\n") if p.strip()]


def _build_html(
    title: str, body_html: str, image_data_uri: Optional[str],
    logo_path: Optional[Path], footer_context: OrgFooterContext, language: str, online_note_html: str,
    byline: Optional[str] = None,
) -> str:
    image_block = f'<img class="announcement-image" src="{image_data_uri}">' if image_data_uri else ""
    # Title and byline are user-entered plain text: escaped, so a "<" in
    # a title can't turn into markup in the PDF.
    byline_block = f'<p class="byline">{escape(byline)}</p>' if byline else ""
    body = f"""
        <h1>{escape(title)}</h1>
        {image_block}
        {byline_block}
        <div>{body_html}</div>
        {online_note_html}
    """
    return wrap_document(
        body, footer_context.club_name, logo_path, org_footer_html(footer_context, language), language,
        extra_css=EXTRA_CSS,
    )


def render_announcement_print_pdf(
    announcement: Announcement, footer_context: OrgFooterContext,
    logo_path: Optional[Path], image_path: Optional[Path],
    public_blog_url: Optional[str], language: str = "en", byline: Optional[str] = None,
) -> PrintRenderResult:
    """Renders the announcement as a one-page PDF, shortening the text
    if needed. Mutates announcement.print_text_override if shortening
    happens (caller is responsible for persisting/committing that).
    Raises PrintTooLongError if it still doesn't fit even at the
    shortest attempt -- callers should not catch this to try again
    with different parameters; it means a human needs to shorten the
    source text."""
    image_data_uri = None
    if image_path is not None and image_path.exists():
        image_data_uri = file_to_data_uri(image_path)

    def render(body_markdown: str, include_online_note: bool):
        online_note_html = ""
        if include_online_note and public_blog_url:
            qr_uri = _qr_data_uri(public_blog_url)
            online_note_html = (
                f'<div class="online-note"><img src="{qr_uri}">'
                f'<div>Read the full announcement online:<br>{escape(public_blog_url)}</div></div>'
            )
        html_doc = _build_html(
            announcement.title, render_markdown_to_html(body_markdown),
            image_data_uri, logo_path, footer_context, language, online_note_html, byline,
        )
        return HTML(string=html_doc, url_fetcher=data_uri_only_fetcher()).render()

    source_markdown = announcement.print_text_override or announcement.body_markdown

    doc = render(source_markdown, include_online_note=False)
    if len(doc.pages) == 1:
        return PrintRenderResult(pdf_bytes=doc.write_pdf(), was_shortened=False, qr_included=False)

    # Doesn't fit as-is -- shorten paragraph by paragraph, most content
    # kept first, until it fits or we run out of paragraphs to drop.
    paragraphs = _split_paragraphs(source_markdown)
    for keep_count in range(len(paragraphs) - 1, 0, -1):
        shortened_markdown = "\n\n".join(paragraphs[:keep_count])
        doc = render(shortened_markdown, include_online_note=True)
        if len(doc.pages) == 1:
            # Persisted so it's visible and editable afterward, and so
            # the next generation doesn't repeat this search -- see
            # Announcement.print_text_override's docstring in models.py.
            announcement.print_text_override = shortened_markdown
            return PrintRenderResult(
                pdf_bytes=doc.write_pdf(), was_shortened=True, qr_included=bool(public_blog_url),
            )

    raise PrintTooLongError(
        "Even a single paragraph doesn't fit on one printed page alongside the header, footer, and image. "
        "Please shorten the text manually in the print override field and try again."
    )
