"""
A note as a formal PDF (issue #343): the note's Markdown body inside
the club's shared page chrome -- the same header (logo, club name),
three-column footer and "Page X of Y" as invoices, the sign-in sheet
and every other "formal document" PDF (app/pdf_chrome.py, ADR 0043).

Meant for things like the minutes of a general meeting that get
printed, signed or sent around. The note's own H1 is the document
title (kermie's call on #343: no extra title on top). A note without
an H1 gets its title as one, so the PDF never starts headless.

The body goes through the same nh3 sanitizer as the note page
(render_markdown_to_html), and WeasyPrint gets the data:-URI-only
fetcher: an image or stylesheet URL in a note is never fetched (no
server-side requests to wherever a note points), so remote images
simply don't appear in the PDF.
"""
from pathlib import Path
from typing import Optional

from markupsafe import escape
from weasyprint import HTML

from app.announcement_utils import render_markdown_to_html
from app.pdf_chrome import OrgFooterContext, org_footer_html, wrap_document
from app.pdf_utils import data_uri_only_fetcher

EXTRA_CSS = """
h1 { font-size: 16pt; margin: 0.4cm 0 0.5cm; color: #1f2937; }
h2 { font-size: 13pt; margin-top: 0.6cm; }
h3 { font-size: 11.5pt; }
h1, h2, h3, h4 { page-break-after: avoid; }
table { width: 100%; border-collapse: collapse; margin: 0.3cm 0; }
thead { display: table-header-group; }
tr { page-break-inside: avoid; }
th, td { border: 1px solid #d1d5db; padding: 4px 6px; text-align: left; vertical-align: top; }
th { background: #f3f4f6; }
img { max-width: 100%; }
blockquote { border-left: 3px solid #d1d5db; margin-left: 0; padding-left: 0.4cm; color: #4b5563; }
pre, code { font-family: 'DejaVu Sans Mono', monospace; font-size: 9pt; }
pre { white-space: pre-wrap; background: #f9fafb; padding: 6px; }
a { color: #2f6f3e; }
"""


def note_body_html(title: str, body_markdown: str) -> str:
    body = render_markdown_to_html(body_markdown, allow_tables=True)
    if "<h1" not in body:
        body = f"<h1>{escape(title)}</h1>{body}"
    return body


def render_note_pdf(
    title: str, body_markdown: str, footer_context: OrgFooterContext,
    logo_path: Optional[Path], language: str = "en",
) -> bytes:
    html_doc = wrap_document(
        note_body_html(title, body_markdown),
        footer_context.club_name, logo_path, org_footer_html(footer_context, language), language,
        extra_css=EXTRA_CSS,
    )
    return HTML(string=html_doc, url_fetcher=data_uri_only_fetcher()).write_pdf()
