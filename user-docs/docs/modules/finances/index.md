# Finances

The Finances module is where the treasurer works. It builds the club's
annual invoices for every parcel and member, tracks who has paid, sends
payment reminders, and records the bills the club itself receives. It
also keeps a simple cash book per bank account. From all of that it
produces a cash-based accounting statement for the tax office and a
budget plan for the next year.

!!! info "Who can use this"
    - The module is **off by default**. An administrator turns it on
      under **Club settings** (the switch is called **Finances**), see
      [Turning modules on and off](../../administration/modules.md).
      Before you send the first invoices, fill in the **Finance
      settings** (bank details, invoice number format) in
      [Club settings](../../administration/settings.md) -- they are
      printed in the footer of every invoice.
    - Board members and administrators (and anyone in a group with full
      access) can do everything.
    - Everybody else needs a [group](../../administration/groups.md)
      that grants **Finances** permissions:
        - **read** -- see every screen, open PDFs, export CSV files;
        - **write** -- create and change runs, items, payments,
          reminders, accounts, bookings, incoming invoices, categories
          and the budget;
        - **delete** -- delete those things again.
    - A few actions around cloud-storage attachments of incoming
      invoices are for board members and administrators only, see
      [Incoming invoices](incoming-invoices.md).

    See [Roles, groups and permissions](../../getting-started/roles-and-permissions.md).

## Where to find it

When the module is on and you may read it, the sidebar shows a
**Finances** group with four entries:

| Menu entry | Opens |
|---|---|
| **Overview** | The finances dashboard described below. |
| **Outgoing Invoices** | The list of invoice runs, see [Invoice runs](invoice-runs.md). |
| **Reminders** | The list of overdue invoices, see [Invoices, payments and reminders](invoices.md#reminders). |
| **Incoming Invoices** | Bills the club received, see [Incoming invoices](incoming-invoices.md). |

Everything else (accounts, categories, item catalog, bookings,
statement, budget) is reached from the dashboard's cards.

## Finances dashboard

![Finances dashboard](../../assets/screenshots/finances/dashboard.png)

The landing page of the module. Three figures at the top give you the
state of your outgoing invoices at a glance. Below them, one card per
area of the module takes you there.

| Figure | What it shows |
|---|---|
| **Open invoices** | How many outgoing invoices are not fully paid yet. Partially paid invoices count as open here. |
| **Outstanding amount** | The sum still unpaid across those invoices (invoice amount minus payments recorded). Reminder fees are not included in this figure. |
| **Overdue** | How many of the open invoices are past the due date of their invoice run. Shown in red when it's more than zero. |

| Card | Hint below the title | Opens |
|---|---|---|
| **Outgoing Invoices** | *n* invoice run(s) | [Invoice runs](invoice-runs.md) |
| **Categories** | *n* categor(y/ies) defined | [Bookkeeping categories](bookkeeping.md#bookkeeping-categories) |
| **Item catalog** | *n* item template(s) defined | [Item catalog](invoice-runs.md#item-catalog) |
| **Accounts** | *n* account(s) defined | [Accounts](bank-accounts.md#accounts) |
| **Reminders** | *n* invoice(s) overdue | [Reminders](invoices.md#reminders) |
| **Incoming Invoices** | *n* incoming invoice(s) | [Incoming invoices](incoming-invoices.md) |
| **All bookings** | Every payment across incoming and outgoing invoices | [All bookings](bookkeeping.md#all-bookings) |
| **Accounting statement** | Cash-based statement for the tax office | [Accounting statement](bookkeeping.md#accounting-statement) |
| **Budget plan** | Planned income and expenses per category for the coming year, next to past actuals | [Budget plan](bookkeeping.md#budget-plan) |

Most sub-pages have a **Back to Finances** button in the top bar that
brings you back here.

<!-- TODO(verify): finances/coming_soon.html ("This feature is coming soon.") exists, but no route renders it any more, so it is not documented as a screen. -->

## How the money flows through a year

A typical club year in Parcella looks like this:

1. **Set up once.** Create your [bookkeeping categories](bookkeeping.md#bookkeeping-categories)
   (or import your chart of accounts), your [bank and cash accounts](bank-accounts.md#accounts),
   and the recurring invoice lines in the [item catalog](invoice-runs.md#item-catalog)
   (lease per m², membership fee, water, electricity, insurance ...).
2. **Prepare the annual invoices.** Create an [invoice run](invoice-runs.md)
   for the year, add the items from the catalog, adjust prices, and
   check the [preview](invoice-runs.md#preview-invoices). Meter readings,
   insurance and work hours for that year should be complete at this
   point -- the usage-based items read them live.
3. **Finalize and send.** Finalizing assigns the permanent invoice
   numbers. Then send the invoices by email, upload them to the
   parcels' cloud folders, and download the print bundle for everyone
   who gets paper.
4. **Record payments.** Enter payments by hand on the run's invoice
   list, or import your bank statement on the [account's bookings page](bank-accounts.md#bookings-of-an-account)
   and match each line to the invoice it pays.
5. **Chase late payers.** The [Reminders](invoices.md#reminders) page
   lists every overdue invoice; send the first, second, third reminder
   from the invoice, with or without a fee.
6. **Record the club's own bills** as [incoming invoices](incoming-invoices.md)
   and mark them paid when the money goes out.
7. **Close the year.** The [accounting statement](bookkeeping.md#accounting-statement)
   shows income and expenses per category, counted on the day money
   actually moved. Use it for the tax office and the annual general
   meeting, and plan next year in the [budget plan](bookkeeping.md#budget-plan).

The task guide [Running the annual invoices](../../guides/annual-invoicing.md)
walks through steps 2 to 5 in order.

## Chapters

- [Invoice runs](invoice-runs.md) -- the annual invoice batch, its line
  items and how each amount is calculated, the item catalog, preview
  and finalizing.
- [Invoices, payments and reminders](invoices.md) -- every invoice
  across all runs, delivery, payments, and the dunning process.
- [Bank accounts and bookings](bank-accounts.md) -- your accounts, their
  bookings, and importing a bank statement with invoice matching.
- [Incoming invoices](incoming-invoices.md) -- bills the club received
  and their payments.
- [Categories, budget and statement](bookkeeping.md) -- bookkeeping
  categories, the club-wide bookings list, the accounting statement and
  the budget plan.
