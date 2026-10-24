"""
Budget plan (issue #248): per bookkeeping category, what the club plans
to take in and spend in a year, next to what actually moved in the
three years before it.

Only the plan is stored (FinanceBudgetLine). The actuals are the cash
accounting statement (app/accounting_statement.py) of each earlier
year, computed on every call -- so they always match
/finances/accounting-statement, and the year that is still running
shows its takings and spending so far. See docs/ADR/0113.

Rows are the club's FinanceCategory entries: INCOME categories form
the income section, every other group (EXPENSE, FIXED_ASSETS, ...) the
expense section. A category's actual is the statement's income amount
for an income category and its expense amount otherwise. Whatever the
statement counts but no row of the section shows -- uncategorized
payments, or money on the "other" side of a category -- goes into one
"other" row per section, so section totals equal the statement's.
"""
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from typing import Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.accounting_statement import compute_cash_accounting_statement
from app.models import FinanceBudgetLine, FinanceCategory, FinanceCategoryGroup

# How many years of actuals stand before the planned year.
ACTUAL_YEARS = 3
# Numeric(12, 2): ten digits before the decimal point.
MAX_BUDGET_AMOUNT = Decimal("9999999999.99")


@dataclass
class BudgetRow:
    category: FinanceCategory
    actuals: List[float]
    planned: Optional[float]


@dataclass
class BudgetSection:
    rows: List[BudgetRow] = field(default_factory=list)
    other_actuals: List[float] = field(default_factory=list)
    actual_totals: List[float] = field(default_factory=list)

    @property
    def planned_total(self) -> float:
        return sum((r.planned or 0.0) for r in self.rows)

    @property
    def has_other(self) -> bool:
        return any(abs(a) >= 0.005 for a in self.other_actuals)


@dataclass
class BudgetPlan:
    year: int
    actual_years: List[int]
    income: BudgetSection
    expense: BudgetSection

    @property
    def actual_results(self) -> List[float]:
        return [i - e for i, e in zip(self.income.actual_totals, self.expense.actual_totals)]

    @property
    def planned_result(self) -> float:
        return self.income.planned_total - self.expense.planned_total


async def compute_budget_plan(db: AsyncSession, year: int) -> BudgetPlan:
    actual_years = list(range(year - ACTUAL_YEARS, year))
    categories = (await db.scalars(select(FinanceCategory).order_by(FinanceCategory.code))).all()
    planned: Dict[str, float] = {
        line.category_id: float(line.amount)
        for line in (await db.scalars(select(FinanceBudgetLine).where(FinanceBudgetLine.year == year))).all()
    }

    income, expense = BudgetSection(), BudgetSection()
    income_by_year, expense_by_year = [], []
    for actual_year in actual_years:
        statement = await compute_cash_accounting_statement(db, actual_year)
        income_by_year.append({r.category.id: r.amount for r in statement.income_by_category if r.category})
        expense_by_year.append({r.category.id: r.amount for r in statement.expense_by_category if r.category})
        income.actual_totals.append(statement.income_total)
        expense.actual_totals.append(statement.expense_total)

    for category in categories:
        is_income = category.group == FinanceCategoryGroup.INCOME
        by_year = income_by_year if is_income else expense_by_year
        (income if is_income else expense).rows.append(BudgetRow(
            category=category,
            actuals=[amounts.get(category.id, 0.0) for amounts in by_year],
            planned=planned.get(category.id),
        ))

    for section in (income, expense):
        section.other_actuals = [
            total - sum(r.actuals[i] for r in section.rows) for i, total in enumerate(section.actual_totals)
        ]
    return BudgetPlan(year=year, actual_years=actual_years, income=income, expense=expense)


def parse_budget_amount(raw: Optional[str]) -> Optional[Decimal]:
    """A planned amount as typed: blank means "nothing planned" (None).
    Raises ValueError for anything that isn't a finite amount within the
    column's range. Accepts a decimal comma, since browsers in some
    locales submit one."""
    text = (raw or "").strip().replace(" ", "")
    if not text:
        return None
    if "," in text and "." not in text:
        text = text.replace(",", ".")
    try:
        amount = Decimal(text)
    except InvalidOperation:
        raise ValueError(raw)
    if not amount.is_finite() or abs(amount) > MAX_BUDGET_AMOUNT:
        raise ValueError(raw)
    return amount.quantize(Decimal("0.01"))


async def save_budget(db: AsyncSession, year: int, amounts: Dict[str, Optional[Decimal]]) -> None:
    """Upserts the planned amounts of `year` (category id -> amount, None
    deletes the line). Ids that aren't categories are ignored. Caller
    commits."""
    valid_ids = set((await db.scalars(select(FinanceCategory.id))).all())
    existing = {
        line.category_id: line
        for line in (await db.scalars(select(FinanceBudgetLine).where(FinanceBudgetLine.year == year))).all()
    }
    for category_id, amount in amounts.items():
        if category_id not in valid_ids:
            continue
        line = existing.get(category_id)
        if amount is None:
            if line is not None:
                await db.delete(line)
        elif line is None:
            db.add(FinanceBudgetLine(year=year, category_id=category_id, amount=amount))
        else:
            line.amount = amount
    await db.flush()
