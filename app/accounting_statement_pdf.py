"""
Renders the cash-based accounting statement (issue #179) as a PDF for
handing to the tax office. Shares its page chrome (header/footer/
@page, "Page X of Y") with every other PDF in this app via
app/pdf_chrome.py.
"""
from pathlib import Path
from typing import List, Optional

from weasyprint import HTML

from app.pdf_utils import data_uri_only_fetcher
from app.accounting_statement import CashAccountingStatement, CategoryAmount
from app.i18n import translate
from app.l10n import format_money
from app.pdf_chrome import wrap_document, org_footer_html, OrgFooterContext

EXTRA_CSS = """
h1 { font-size: 14pt; margin-top: 0.4cm; margin-bottom: 0.6cm; color: #1f2937; }
h2 { font-size: 11pt; margin-top: 0.8cm; margin-bottom: 0.3cm; color: #2f6f3e; }
table { width: 100%; border-collapse: collapse; }
th { text-align: left; font-size: 9pt; text-transform: uppercase; color: #4b5563; border-bottom: 2px solid #2f6f3e; padding: 6px 8px; }
td { padding: 6px 8px; border-bottom: 1px solid #e5e7eb; vertical-align: top; }
td.num { text-align: right; white-space: nowrap; }
tr.total-row td { border-top: 2px solid #2f6f3e; border-bottom: none; font-weight: bold; padding-top: 8px; }
.net-result { margin-top: 0.8cm; font-size: 12pt; font-weight: bold; text-align: right; }
.net-result.negative { color: #b91c1c; }
.note { margin-top: 0.4cm; font-size: 8pt; color: #6b7280; }
"""


def _category_rows_html(rows: List[CategoryAmount], region: str, currency: str, uncategorized_label: str) -> str:
    if not rows:
        return ""
    return "".join(
        f'<tr><td>{row.category.code + " · " + row.category.title if row.category else uncategorized_label}</td>'
        f'<td class="num">{format_money(row.amount, region, currency)}</td></tr>'
        for row in rows
    )


def render_accounting_statement_pdf(
    statement: CashAccountingStatement, footer_context: OrgFooterContext, logo_path: Optional[Path],
    region: str, currency: str, language: str = "en",
) -> bytes:
    heading = translate("finances.accounting_statement.pdf_heading", language, year=statement.year)
    col_category = translate("finances.accounting_statement.col_category", language)
    col_amount = translate("finances.accounting_statement.col_amount", language)
    section_income = translate("finances.accounting_statement.section_income", language)
    section_expenses = translate("finances.accounting_statement.section_expenses", language)
    row_total = translate("finances.accounting_statement.row_total", language)
    row_net_result = translate("finances.accounting_statement.row_net_result", language)
    uncategorized_label = translate("finances.incoming_invoices.no_category", language)
    note = translate("finances.accounting_statement.pdf_note", language)

    income_rows_html = _category_rows_html(statement.income_by_category, region, currency, uncategorized_label)
    expense_rows_html = _category_rows_html(statement.expense_by_category, region, currency, uncategorized_label)

    net_class = "net-result negative" if statement.net_result < 0 else "net-result"

    body_html = f"""
    <h1>{heading}</h1>

    <h2>{section_income}</h2>
    <table>
        <thead><tr><th>{col_category}</th><th class="num">{col_amount}</th></tr></thead>
        <tbody>
            {income_rows_html}
            <tr class="total-row"><td>{row_total}</td><td class="num">{format_money(statement.income_total, region, currency)}</td></tr>
        </tbody>
    </table>

    <h2>{section_expenses}</h2>
    <table>
        <thead><tr><th>{col_category}</th><th class="num">{col_amount}</th></tr></thead>
        <tbody>
            {expense_rows_html}
            <tr class="total-row"><td>{row_total}</td><td class="num">{format_money(statement.expense_total, region, currency)}</td></tr>
        </tbody>
    </table>

    <div class="{net_class}">{row_net_result}: {format_money(statement.net_result, region, currency)}</div>
    <div class="note">{note}</div>
    """

    html_doc = wrap_document(
        body_html, footer_context.club_name, logo_path, org_footer_html(footer_context, language), language,
        extra_css=EXTRA_CSS,
    )
    return HTML(string=html_doc, url_fetcher=data_uri_only_fetcher()).write_pdf()
