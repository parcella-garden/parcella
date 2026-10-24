# Budget plan: store only the plan, derive the actuals

**Context:** Issue #248 asked for a budget plan: an editable table of
income and expense categories with the present year's figures and an
editable column for next year, ideally with at least two past years
before it. The finances module already has bookkeeping categories
(`FinanceCategory`, issue #67) and a cash accounting statement per year
(`app/accounting_statement.py`, ADRs 0060/0061) that splits every
payment across its invoice's categories.

**Decision:**

- **Rows are the club's finance categories**, not a separate list of
  budget items. An INCOME category belongs to the income section; every
  other group (EXPENSE, FIXED_ASSETS, EQUITY_LIABILITIES, OTHER) to the
  expense section. A new category shows up in the plan without further
  setup.
- **Only the plan is stored**: `finance_budget_lines` (year, category,
  amount), unique per year and category. A blank field deletes the
  line, so "nothing planned" and "planned 0" stay distinct.
- **The actuals are derived** from the cash accounting statement of each
  of the three years before the planned year, every time the page
  loads. The year that is still running shows "so far". The numbers
  always match `/finances/accounting-statement`, and correcting a
  payment corrects the plan's history too. Freezing a copy would have
  let the two drift apart.
- A category's actual is the statement's income amount for an income
  category and its expense amount otherwise. Whatever the statement
  counts that no row of a section shows (uncategorized payments, or
  money on the "wrong" side of a category) goes into one "other" row
  per section, so section totals equal the statement's.
- The planned year defaults to next year; any calendar year can be
  opened (previous/next buttons), so a plan for the running year can be
  entered too.

**Consequences:**

- Viewing needs finances read access, saving needs write access.
- No REST API: the finances module has none yet. When it gets one, the
  budget should be part of it.
- No per-category planned values for past years in the table (only the
  plan of the opened year next to past actuals). Plan-vs-actual for the
  same year can be read by opening that year's plan.
