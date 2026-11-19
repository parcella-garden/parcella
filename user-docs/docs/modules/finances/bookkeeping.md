# Categories, budget and statement

Bookkeeping categories are short codes like "40000 Membership fees"
that you attach to invoice lines and to the positions of incoming
invoices. With them, Parcella can tell you where the club's money came
from and where it went: in the list of all bookings, in the cash-based
accounting statement for the tax office, and in the budget plan for
next year.

!!! info "Who can use this"
    Part of the **Finances** module (off by default). All four screens
    can be viewed with **Finances** read permission, including the PDF
    export of the statement. Adding, changing and importing categories
    and saving the budget need write permission; deleting a category
    needs delete permission. Board members and administrators can do
    everything. See [Finances](index.md).

## Bookkeeping categories

![Bookkeeping categories](../../assets/screenshots/finances/category-list.png)

Open it with the **Categories** card on the finances dashboard.
**Back to Finances** in the top bar takes you back.

Parcella doesn't ship an official chart of accounts. The sample data
contains three example categories; replace them with your club's own
chart, typed in or imported from your accounting software.

### New category

Shown with write permission.

| Field | What it does |
|---|---|
| **Code** | Required. Exactly five digits, e.g. `40000`. Must not be used by another category. |
| **Title** | Required, e.g. "Membership fees". |
| **Group** | **Income**, **Expense**, **Fixed assets**, **Equity & liabilities** or **Other**. The budget plan puts **Income** categories in its income section and all others in its expense section. |
| **Add category** | Saves the category. |

Errors: "Invalid category -- the code must be exactly 5 digits, and a
title and group are required." or "A category with this code already
exists."

### Import from CSV

Shown with write permission. Pick a **CSV file** and click **Import**.

The file needs a header row `code,title,group`, separated by commas.
**group** is one of `income`, `expense`, `fixed_assets`,
`equity_liabilities`, `other` (upper or lower case). For example:

```
code,title,group
40000,Membership fees,income
40100,Lease income,income
60020,Volunteer allowance,expense
```

Rows with an invalid code, an unknown group, a missing title, or a code
that already exists are skipped. The result is shown as "Imported *n*,
skipped *m*." Existing categories are never changed by an import.

### Categories list

| Column / button | What it shows |
|---|---|
| **Code**, **Title**, **Group** | The category. With write permission they are editable in the row; click the tick icon to save. The same rules as for a new category apply. |
| Bin icon | Deletes the category after a confirmation. Needs delete permission. |

If there are none: "No categories yet -- add one above, or import a CSV."

!!! warning "Deleting a category"
    "Delete this category? Items using it keep working, just without a
    category." Invoice lines, item templates and incoming invoice
    positions lose the category; past payments for them then show as
    "Uncategorized" in the statement. **Planned amounts for this
    category in the budget plan are deleted.** Rename a category rather
    than deleting and recreating it.

## All bookings

![All bookings](../../assets/screenshots/finances/bookings.png)

Open it with the **All bookings** card on the dashboard. It lists every
payment the club received for its invoices and every payment it made
for incoming invoices, across all accounts, newest first. Bookings that
aren't tied to an invoice (bank fees, refunds) are not included -- see
the account's [bookings](bank-accounts.md#bookings-of-an-account) for
those.

**Filter**

| Filter | What it does |
|---|---|
| **Search** | Finds payments whose sender/recipient or description contains this text. |
| **From** / **To** | Payment date on or between these dates. |
| **Category** | **All categories**, or only payments whose invoice has a line in this category. |
| **Type** | **Income & expenses**, **Income** or **Expense**. |
| **Min. amount** / **Max. amount** | Payment amount in this range. Expenses count as positive amounts here. |
| **Filter** / **Reset** | Applies the filter / clears it. |

**Table** (the header shows the number, e.g. "42 booking(s)")

| Column | What it shows |
|---|---|
| **Date** | The payment date. |
| **Type** | **Income** (green) or **Expense** (red). |
| **Sender / recipient** | The invoice's recipient, or the incoming invoice's sender. Click it to open that invoice. |
| **Categories** | All categories on the invoice's lines, or "Uncategorized". |
| **Description** | The invoice's line names and descriptions. |
| **Amount** | The amount paid, green for income, red for expenses. |

If nothing matches: "No bookings match these filters."

!!! note
    The amount shown is the whole payment, even if the invoice has lines
    in several categories. The [accounting statement](#accounting-statement)
    splits it between the categories; this list doesn't.

## Accounting statement

![Accounting statement](../../assets/screenshots/finances/accounting-statement.png)

Open it with the **Accounting statement** card on the dashboard. The
title is "Accounting statement *year*". It is a simple cash-based
income and expense statement per category, the kind a non-profit
association hands to the tax office or presents at the annual general
meeting.

**Top bar**

| Control | What it does |
|---|---|
| Year | Drop-down with every year in which a payment was recorded, plus the current year. Shows the newest one first; changing it reloads the page. |
| **Export as PDF** | Downloads the statement for the selected year as a PDF with your club's letterhead ("Cash-based accounting statement *year*"). |
| **Back to Finances** | Back to the dashboard. |

The page has two cards, **Income** and **Expenses**, each listing
**Category** ("code · title", or "Uncategorized") and **Amount**, with
a **Total** row. Below them, the **Net result** (income minus
expenses) is shown in green, or red if negative. A card without entries
says "No entries for this year."

How the figures are counted:

- **Only money that actually moved counts.** Income is the payments
  recorded for outgoing invoices, expenses the payments recorded for
  incoming invoices. Unpaid invoices don't appear.
- **The payment date decides the year**, not the invoice date.
- **Each payment is split by category** in proportion to the invoice's
  lines. If a 100.00 invoice has 80.00 lease and 20.00 water, a 50.00
  partial payment counts 40.00 to lease and 10.00 to water. A
  reminder fee included in a payment is split the same way.
- Lines without a category, and invoices from before categories were
  used, show as "Uncategorized".
- Account bookings not tied to an invoice (bank fees, interest, cash
  purchases entered on an account) are **not** included. Record such
  costs as an [incoming invoice](incoming-invoices.md) with a payment if
  they should appear here.

!!! tip
    For a clean statement, give every catalog item and every incoming
    invoice position a category *before* you finalize the run or record
    the bill. Categories are copied onto the invoices when the run is
    finalized and can't be added to them afterwards.

## Budget plan

![Budget plan](../../assets/screenshots/finances/budget.png)

Open it with the **Budget plan** card on the dashboard. The title is
"Budget plan *year*". It opens on **next year**. Use the arrow buttons
**Previous year** / **Next year** in the top bar to plan another year;
**Back to Finances** returns to the dashboard.

The table has one row per bookkeeping category and these columns:

| Column | What it shows |
|---|---|
| **Category** | Code and title. |
| "*year* actual" (three columns) | What was actually received or paid in each of the three years before the planned year, exactly as in the [accounting statement](#accounting-statement). For the current year the heading reads "*year* so far", because the year isn't over. |
| "*year* plan" | The amount you plan for this category. Editable with write permission. |

The rows are grouped:

- **Income** -- all categories of the group **Income**, with a
  **Total** row.
- **Expenses** -- all other categories (expense, fixed assets, equity &
  liabilities, other), with a **Total** row.
- **Other (uncategorized or booked on the other side)** -- appears in a
  section only when needed. It holds what the statement counted but no
  row of the section shows: uncategorized payments, or for example a
  payment of an incoming invoice whose position carries an income
  category. With it, the section totals always match the statement.
- **Result (income − expenses)** at the bottom, red when negative.

Enter the planned amounts as numbers, e.g. `1050.00`, and click **Save
plan**. You see "Budget plan saved.". "Past years show what was
actually paid (as in the accounting statement). Leave a field empty for
"nothing planned"." Emptying a field removes the plan for that
category. Something that isn't a number is refused with "Please enter
amounts as numbers, e.g. 1050.00." and nothing is saved.

Only the plan is stored. The actual columns are recalculated every time
from the recorded payments, so they always agree with the accounting
statement.

If you have no categories yet: "No bookkeeping categories yet. The
budget plan has one row per category." with a link **Manage categories**.

## Related

- [Invoice runs](invoice-runs.md) -- where invoice lines get their
  category.
- [Incoming invoices](incoming-invoices.md) -- where expense positions
  get their category.
- [Bank accounts and bookings](bank-accounts.md)
