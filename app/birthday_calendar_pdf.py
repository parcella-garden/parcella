"""
Printable birthday list (issue #272, replacing the whole-year calendar
from issue #99): the same upcoming window as /calendar/birthdays,
arranged by plot for whoever visits members with presents -- plot
number first and sorted by it, the members of that plot under it, then
the birthday, the age being turned (milestones highlighted), tags,
whether the member declines presents (#269), and postal address, email
and phone.

A4 landscape, since nine columns don't fit upright. Shares its page
chrome (header/footer, "Page X of Y") with every other PDF in this app
via app/pdf_chrome.py -- see that module's docstring and docs/ADR/0043.

Every value from the database goes through html.escape(): member names,
addresses and tag names are user-entered and this is HTML for
WeasyPrint.
"""
from datetime import date
from html import escape
from pathlib import Path
from typing import List, Optional

from weasyprint import HTML

from app.announcement_mailer import primary_email
from app.birthdays import ParcelBirthdayRow
from app.i18n import translate
from app.l10n import format_address_lines
from app.pdf_chrome import wrap_document, org_footer_html, OrgFooterContext
from app.pdf_utils import data_uri_only_fetcher
from app.tag_translations import tag_label

EXTRA_CSS = """
@page { size: A4 landscape; }
body { font-size: 8.5pt; }
h1 { font-size: 14pt; margin-top: 0.4cm; margin-bottom: 0.5cm; color: #1f2937; }
table { width: 100%; border-collapse: collapse; }
thead { display: table-header-group; } /* repeats on every page */
th { text-align: left; font-size: 7.5pt; text-transform: uppercase; color: #4b5563; border-bottom: 2px solid #2f6f3e; padding: 5px 6px; }
td { padding: 5px 6px; border-bottom: 1px solid #e5e7eb; vertical-align: top; }
tr { page-break-inside: avoid; }
tr.plot-start td { border-top: 1.5px solid #2f6f3e; }
td.plot-col { font-weight: bold; white-space: nowrap; color: #2f6f3e; }
td.nowrap { white-space: nowrap; }
tr.round-birthday td.age-col, tr.round-birthday td.name-col { background: #fef3c7; }
span.tag { display: inline-block; background: #f3f4f6; color: #374151; border-radius: 3px; padding: 0 4px; margin: 0 2px 2px 0; font-size: 7.5pt; }
span.no-present { color: #991b1b; font-weight: bold; }
"""


def _primary_phone(member) -> Optional[str]:
    phones = member.phone_numbers
    if not phones:
        return None
    return next((p for p in phones if p.is_primary), phones[0]).number


def _body_html(heading: str, rows: List[ParcelBirthdayRow], language: str, region: str) -> str:
    def t(key: str, **kwargs) -> str:
        return escape(translate(key, language, **kwargs))

    no_plot = t("calendar.birthdays.pdf_no_plot")
    rows_html = []
    previous_plot: object = object()  # never equal to a real plot or None
    for row in rows:
        b = row.birthday
        m = b.member
        first_of_plot = row.plot_number != previous_plot
        previous_plot = row.plot_number
        plot_text = (escape(row.plot_number) if row.plot_number is not None else no_plot) if first_of_plot else ""

        age_text = t("calendar.birthdays.turning_label", age=b.turning_age)
        if b.is_round:
            age_text += f" ({t('calendar.birthdays.round_badge')})"
        tags = "".join(f'<span class="tag">{escape(tag_label(tag, language))}</span>' for tag in m.tags)
        present = (
            f'<span class="no-present">{t("calendar.birthdays.no_present")}</span>'
            if m.birthday_present_declined else ""
        )
        address = "<br>".join(escape(line) for line in format_address_lines(m.street, m.postal_code, m.city, region))
        email = escape(primary_email(m) or "")
        phone = escape(_primary_phone(m) or "")

        classes = " ".join(filter(None, ["plot-start" if first_of_plot else "", "round-birthday" if b.is_round else ""]))
        rows_html.append(
            f'<tr class="{classes}">'
            f'<td class="plot-col">{plot_text}</td>'
            f'<td class="name-col">{escape(m.full_name)}</td>'
            f'<td class="nowrap">{b.next_occurrence.strftime("%d.%m.%Y")}</td>'
            f'<td class="age-col nowrap">{age_text}</td>'
            f'<td>{tags}</td>'
            f'<td>{present}</td>'
            f'<td>{address}</td>'
            f'<td>{email}</td>'
            f'<td class="nowrap">{phone}</td>'
            f'</tr>'
        )

    if not rows_html:
        rows_html.append(
            f'<tr><td colspan="9" style="text-align: center; color: #6b7280;">{t("calendar.birthdays.empty")}</td></tr>'
        )

    headers = [
        t("members.detail.col_plot_number"), t("calendar.birthdays.col_name"), t("calendar.birthdays.col_date"),
        t("calendar.birthdays.col_turning"), t("calendar.birthdays.col_tags"), t("calendar.birthdays.col_present"),
        t("members.form.address_header"), t("members.form.label_email_address"), t("members.form.label_phone_number"),
    ]
    return f"""
    <h1>{escape(heading)}</h1>
    <table>
        <thead><tr>{''.join(f'<th>{h}</th>' for h in headers)}</tr></thead>
        <tbody>{''.join(rows_html)}</tbody>
    </table>
    """


def render_birthday_calendar_pdf(
    start: date, end: date, footer_context: OrgFooterContext, logo_path: Optional[Path],
    rows: List[ParcelBirthdayRow], language: str, region: str,
) -> bytes:
    """rows should already be sorted by plot -- see
    app.birthdays.birthdays_by_parcel(); this function doesn't re-sort."""
    heading = translate(
        "calendar.birthdays.pdf_heading", language,
        start=start.strftime("%d.%m.%Y"), end=end.strftime("%d.%m.%Y"),
    )
    html_doc = wrap_document(
        _body_html(heading, rows, language, region),
        footer_context.club_name, logo_path, org_footer_html(footer_context, language), language,
        extra_css=EXTRA_CSS,
    )
    return HTML(string=html_doc, url_fetcher=data_uri_only_fetcher()).write_pdf()
