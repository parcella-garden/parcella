"""
Renders a general-meeting sign-in sheet: current members, grouped by
parcel number, each with a blank signature line -- for printing and
bringing to a physical meeting.

Shares its page chrome (header/footer/@page, "Page X of Y") with every
other PDF in this app via app/pdf_chrome.py -- see that module's
docstring for why. Unlike the announcement flyer (app.print_publisher),
this is deliberately NOT constrained to one page: a real member roster
can run to several pages, and unlike a flyer there's no "shorten it"
option for a list of people who need to sign in. Instead it's a normal
multi-page document with a repeating header/footer and "Page X of Y"
numbering.
"""
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

from weasyprint import HTML

from app.pdf_utils import data_uri_only_fetcher
from app.i18n import translate
from app.pdf_chrome import wrap_document, org_footer_html, OrgFooterContext

EXTRA_CSS = """
h1 { font-size: 15pt; margin-top: 0.4cm; margin-bottom: 0.6cm; color: #1f2937; }
table { width: 100%; border-collapse: collapse; }
thead { display: table-header-group; } /* repeats on every page */
th { text-align: left; font-size: 9pt; text-transform: uppercase; color: #4b5563; border-bottom: 2px solid #2f6f3e; padding: 6px 8px; }
td { padding: 7px 8px; border-bottom: 1px solid #e5e7eb; vertical-align: top; }
td.parcel-col { font-weight: bold; white-space: nowrap; width: 3.2cm; border-right: 1px solid #e5e7eb; }
td.name-col { width: 6.5cm; }
td.signature-col { border-bottom: 1px solid #9ca3af; }
tr.parcel-group-start td { border-top: 1px solid #d1d5db; }
"""


@dataclass
class ParcelGroup:
    plot_number: str
    member_names: List[str]


def _body_html(headline: str, groups: List[ParcelGroup], language: str) -> str:
    rows_html = []
    for group in groups:
        for row_index, name in enumerate(group.member_names):
            is_first_row_in_group = row_index == 0
            row_class = "parcel-group-start" if is_first_row_in_group else ""
            parcel_cell = (
                f'<td class="parcel-col" rowspan="{len(group.member_names)}">{group.plot_number}</td>'
                if is_first_row_in_group else ""
            )
            rows_html.append(
                f'<tr class="{row_class}">{parcel_cell}'
                f'<td class="name-col">{name}</td>'
                f'<td class="signature-col"></td></tr>'
            )

    return f"""
    <h1>{headline}</h1>
    <table>
        <thead>
            <tr>
                <th>{translate("members.signin_sheet.col_parcel", language)}</th>
                <th>{translate("members.signin_sheet.col_name", language)}</th>
                <th>{translate("members.signin_sheet.col_signature", language)}</th>
            </tr>
        </thead>
        <tbody>
            {''.join(rows_html)}
        </tbody>
    </table>
    """


def render_meeting_signin_sheet_pdf(
    headline: str, footer_context: OrgFooterContext, logo_path: Optional[Path],
    parcel_members: List[Tuple[str, List[str]]], language: str = "en",
) -> bytes:
    """parcel_members: list of (plot_number, [member full names]),
    already sorted the way the caller wants them to appear -- this
    function doesn't re-sort, so grouping order is entirely the
    caller's responsibility."""
    groups = [ParcelGroup(plot_number=p, member_names=names) for p, names in parcel_members]
    html_doc = wrap_document(
        _body_html(headline, groups, language),
        footer_context.club_name, logo_path, org_footer_html(footer_context, language), language,
        extra_css=EXTRA_CSS,
    )
    return HTML(string=html_doc, url_fetcher=data_uri_only_fetcher()).write_pdf()
