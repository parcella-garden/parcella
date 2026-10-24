"""
Issue #248: a budget plan -- per bookkeeping category the planned amount
for the coming year, next to the actuals of the three years before it.
Only the plan is stored; the actuals are the cash accounting statement
of each year (ADR 0113).
"""
from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import select

from app.budget_plan import compute_budget_plan, parse_budget_amount
from app.database import AsyncSessionLocal
from app.models import FinanceBudgetLine, FinanceCategoryGroup
from tests.test_accounting_statement import (
    _enable_finances_module, _make_category, _make_run_with_invoice, _record_payment, web_login,
)


async def test_plan_shows_actuals_and_saves_next_year(client, admin_user):
    await _enable_finances_module()
    await web_login(client)
    this_year = date.today().year
    fees = await _make_category("40000", "Mitgliedsbeiträge")
    office = await _make_category("60000", "Bürobedarf", FinanceCategoryGroup.EXPENSE)
    _, invoice_id = await _make_run_with_invoice(client, "B1", this_year, [("Beitrag", "120.00", fees)])
    await _record_payment(client, invoice_id, "120.00", f"{this_year}-03-01")

    page = await client.get("/finances/budget")
    assert page.status_code == 200
    assert f"Budget plan {this_year + 1}" in page.text
    assert f"{this_year} so far" in page.text and f"{this_year - 2} actual" in page.text
    assert f'name="amount_{fees}"' in page.text and f'name="amount_{office}"' in page.text

    async with AsyncSessionLocal() as db:
        plan = await compute_budget_plan(db, this_year + 1)
    assert plan.actual_years == [this_year - 2, this_year - 1, this_year]
    fee_row = next(r for r in plan.income.rows if r.category.id == fees)
    assert fee_row.actuals == [0.0, 0.0, 120.0]
    assert [r.category.id for r in plan.expense.rows] == [office]
    assert not plan.income.has_other

    saved = await client.post("/finances/budget", data={
        "year": str(this_year + 1), f"amount_{fees}": "10050", f"amount_{office}": "520,00",
    })
    assert saved.status_code == 303
    async with AsyncSessionLocal() as db:
        plan = await compute_budget_plan(db, this_year + 1)
    assert plan.income.planned_total == 10050.0 and plan.expense.planned_total == 520.0
    assert plan.planned_result == 9530.0
    reloaded = await client.get(f"/finances/budget?year={this_year + 1}")
    assert 'value="10050.00"' in reloaded.text and "Budget plan saved." not in reloaded.text

    # Blank removes the line; a bogus amount is refused and nothing changes.
    assert (await client.post("/finances/budget", data={
        "year": str(this_year + 1), f"amount_{fees}": "10050", f"amount_{office}": "",
    })).status_code == 303
    refused = await client.post("/finances/budget", data={"year": str(this_year + 1), f"amount_{fees}": "viel"})
    assert refused.status_code == 400
    async with AsyncSessionLocal() as db:
        lines = (await db.scalars(select(FinanceBudgetLine))).all()
    assert [(line.category_id, line.amount) for line in lines] == [(fees, Decimal("10050.00"))]


@pytest.mark.parametrize("raw, expected", [
    ("", None), ("  ", None), ("1050", Decimal("1050.00")), ("1050,5", Decimal("1050.50")),
    ("-20.125", Decimal("-20.12")),
])
def test_parse_budget_amount(raw, expected):
    assert parse_budget_amount(raw) == expected


@pytest.mark.parametrize("raw", ["abc", "NaN", "Infinity", "1e20", "1.000,50"])
def test_parse_budget_amount_refuses(raw):
    with pytest.raises(ValueError):
        parse_budget_amount(raw)
