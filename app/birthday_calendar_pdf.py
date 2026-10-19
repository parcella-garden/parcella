"""
Renders a printable birthday calendar covering an entire year (issue
#99): every active member with a birth date on file, grouped by month
(Jan-Dec) in a single document -- unlike /calendar/birthdays' web view,
which only lists the next 90 days for the dashboard-style "upcoming"
use case (see app.birthdays.upcoming_birthdays vs birthdays_for_year).

Shares its page chrome (header/footer/@page, "Page X of Y") with every
other PDF in this app via app/pdf_chrome.py -- see that module's
docstring and docs/ADR/0043 for why.
"""
from pathlib import Path
from typing import List, Optional

from babel.dates import get_month_names
from weasyprint import HTML

from app.pdf_utils import data_uri_only_fetcher
from app.birthdays import YearBirthdayEntry
from app.i18n import translate
from app.pdf_chrome import wrap_document, org_footer_html, OrgFooterContext

EXTRA_CSS = """
h1 { font-size: 14pt; margin-top: 0.4cm; margin-bottom: 0.6cm; color: #1f2937; }
table { width: 100%; border-collapse: collapse; }
thead { display: table-header-group; } /* repeats on every page */
th { text-align: left; font-size: 9pt; text-transform: uppercase; color: #4b5563; border-bottom: 2px solid #2f6f3e; padding: 6px 8px; }
td { padding: 6px 8px; border-bottom: 1px solid #e5e7eb; vertical-align: top; }
td.day-col { font-weight: bold; white-space: nowrap; width: 2.2cm; }
td.age-col { white-space: nowrap; width: 3cm; }
tr.month-row td { background: #eef6f0; font-weight: bold; color: #2f6f3e; border-top: 1px solid #2f6f3e; border-bottom: 1px solid #2f6f3e; padding-top: 8px; padding-bottom: 8px; }
tr.round-birthday td { background: #fef3c7; }
"""


def _body_html(
    heading: str, entries: List[YearBirthdayEntry], language: str, empty_text: str,
) -> str:
    month_names = get_month_names("wide", context="stand-alone", locale=language)

    rows_html = []
    current_month: Optional[int] = None
    for entry in entries:
        if entry.month != current_month:
            current_month = entry.month
            rows_html.append(
                f'<tr class="month-row"><td colspan="3">{month_names[current_month]}</td></tr>'
            )
        row_class = "round-birthday" if entry.is_round else ""
        age_text = translate("calendar.birthdays.turning_label", language, age=entry.turning_age)
        if entry.is_round:
            age_text += f" ({translate('calendar.birthdays.round_badge', language)})"
        rows_html.append(
            f'<tr class="{row_class}">'
            f'<td class="day-col">{entry.day:02d}.</td>'
            f'<td>{entry.member.full_name}</td>'
            f'<td class="age-col">{age_text}</td>'
            f'</tr>'
        )

    if not rows_html:
        rows_html.append(f'<tr><td colspan="3" style="text-align: center; color: #6b7280;">{empty_text}</td></tr>')

    col_day = translate("calendar.birthdays.pdf_col_day", language)
    col_name = translate("calendar.birthdays.col_name", language)
    col_turning = translate("calendar.birthdays.col_turning", language)

    return f"""
    <h1>{heading}</h1>
    <table>
        <thead>
            <tr>
                <th>{col_day}</th>
                <th>{col_name}</th>
                <th>{col_turning}</th>
            </tr>
        </thead>
        <tbody>
            {''.join(rows_html)}
        </tbody>
    </table>
    """


def render_birthday_calendar_pdf(
    year: int, footer_context: OrgFooterContext, logo_path: Optional[Path],
    entries: List[YearBirthdayEntry], language: str,
) -> bytes:
    """entries should already be sorted by (month, day) -- see
    app.birthdays.birthdays_for_year(); this function doesn't re-sort."""
    heading = translate("calendar.birthdays.pdf_heading", language, year=year)
    empty_text = translate("calendar.birthdays.pdf_empty", language)
    html_doc = wrap_document(
        _body_html(heading, entries, language, empty_text),
        footer_context.club_name, logo_path, org_footer_html(footer_context, language), language,
        extra_css=EXTRA_CSS,
    )
    return HTML(string=html_doc, url_fetcher=data_uri_only_fetcher()).write_pdf()
