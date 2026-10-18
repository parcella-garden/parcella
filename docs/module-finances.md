# Finances module (annual invoicing, payments, reminders, bookkeeping categories)

Builds and delivers a club's annual invoice run: define billable line
items once, preview exactly what every parcel/member would be charged,
finalize to assign permanent invoice numbers, then deliver by email,
print bundle, or upload to a parcel's cloud folder. Also tracks partial
payments and dunning reminders against finalized invoices, and an
optional bookkeeping-category tag for reporting. Off by default
(`finances` module flag).

## Data model

```
finance_categories        -- optional bookkeeping tag (code + title + group)
finance_accounts           -- a club's real bank/cash accounts (issue #156)
  account_transactions      -- other bookings against the account (issue #174)

incoming_invoices          -- a bill the club received (issue #178)
  incoming_invoice_line_items

invoice_runs               -- one "annual invoices" batch (e.g. "2026")
  invoice_item_templates    -- reusable catalog, independent of any run
    invoice_item_template_parcels   -- explicit parcel scope (non-FIXED_PER_PERSON)
    invoice_item_template_members   -- explicit member scope (FIXED_PER_PERSON only)
  invoice_item_definitions  -- this run's actual line-item types
    invoice_item_definition_parcels -- explicit parcel scope (non-FIXED_PER_PERSON)
    invoice_item_definition_members -- explicit member scope (FIXED_PER_PERSON only)
  invoices                  -- one per parcel OR one per directly-targeted member
    invoice_line_items
    invoice_payments         -- optionally tagged with a finance_accounts row
    invoice_reminders
```

`InvoiceItemTemplate` and `InvoiceItemDefinition` are structurally
identical (template is just "not yet attached to a run"); applying a
catalog template to a run (`items_add_from_catalog` in
`app/routers/finances.py`) copies every field, including scope rows,
onto a new `InvoiceItemDefinition` -- there is no `template_id` FK
recorded on the resulting definition, so nothing links it back to the
template it came from.

That absence of a link is why the "add from catalog" picker on a
draft run (issue #94) filters out already-added templates **by name**
(`run_detail`'s GET handler diffs the catalog against
`{d.name for d in run.item_definitions}`) rather than by any stored
relationship -- there wasn't one to check. This is recomputed on every
page load, so renaming or deleting an item directly on the run makes
its template reappear as available again; conversely, renaming the
*template* after it was already added breaks the match and it
reappears too, even though conceptually it's "already used" under its
old name. Accepted as a known limitation rather than adding a
template_id column for this alone.

### Two independent targeting mechanisms, routed by `pricing_mode`

This is the module's central design decision -- see
[ADR 0042](./ADR/0042-invoice-item-targeting-plot-scoped-vs-person-scoped.md)
for the full history of why it ended up this shape:

- **Plot-scoped** (`FIXED_PER_PARCEL`, `PER_SQM`, `COMMUNAL_AREA_SHARE`,
  `PUBLIC_BURDENS`): `applies_to_all_parcels` (default `True`) with
  `parcel_scopes` listing specific parcels when `False`. Billed one
  `Invoice` per occupied parcel with an invoice-address resident,
  regardless of the parcel's status (issue #166: a TERMINATED plot with
  a current invoice-address resident -- typically a new tenant who's
  taken over before the status gets flipped back to ACTIVE -- must
  still be billed; only DELETED parcels are excluded). This does *not*
  reopen [ADR 0035](./ADR/0035-invoice-address-flag-on-member-parcel-assignments.md)'s
  constraint that a former tenant can never hold `is_invoice_address` --
  a terminated *lease* still means the departed tenant is never billed,
  only that a terminated *parcel* isn't excluded outright.
- **Person-scoped** (`FIXED_PER_PERSON` only): `applies_to_all_members`
  (default `True`) with `member_scopes` listing specific members when
  `False`. Billed one `Invoice` per targeted member, **regardless of
  whether that member currently has a parcel** -- this is what makes
  honorary/supporting memberships and dues for plot-less members
  possible at all.
- **Automatically scoped** (`WORK_HOURS_SHORTFALL`, `INSURANCE_COST`,
  `WATER_USAGE`, `ELECTRICITY_USAGE` -- see
  [ADR 0056](./ADR/0056-metering-price-drives-automatic-usage-billing.md)
  for why the latter two joined this group): neither field is honored
  for eligibility -- both `applies_to_all_parcels` and `parcel_scopes`
  are still stored on the row (the form doesn't special-case what it
  submits) but `compute_invoices_for_run`'s parcel loop bypasses
  `_parcel_in_scope()` entirely for these four modes, billing exactly
  whichever parcels the underlying module computes a nonzero amount
  for. There is deliberately no manual narrowing here: for insurance
  cost, the `ParcelInsurance` record already *is* the scope (a parcel
  with no insurance, or a zero total, is skipped by
  `item_quantity_and_price` regardless); for water/electricity usage,
  having (or not having) an active metering point of that medium
  already is the scope. A separate parcel picker could only be used to
  under-bill a metered/insured parcel by mistake, never to usefully
  restrict it. The item forms (`run_detail.html`,
  `item_template_list.html`) hide the scope picker for all four and
  show a mode-specific "Automatic (... evaluation)" note instead.

These scope fields/relationships are meaningless/ignored for the "wrong"
pricing mode -- a `PER_SQM` item's `member_scopes` is simply never
read, and vice versa. The UI shows exactly one of the two pickers (or
the automatic note) per item row, switched by the pricing-mode
`<select>`, never more than one at a time.

### `Invoice`'s dual subject

`Invoice.parcel_id` and `Invoice.member_id` are both nullable;
`ck_invoice_exactly_one_subject` (a DB CHECK constraint) enforces
exactly one is set. `recipient_names`/`recipient_address` are
snapshotted at generation time so a later member move, parcel change,
or member deletion (`member_id` is `ON DELETE SET NULL`, not
`CASCADE`, precisely so the invoice survives that) never rewrites
history.

## Generation: `app/invoice_generation.py`

Deliberately two-phase and one-way:

- **`compute_invoices_for_run(db, run)`** -- pure computation, no DB
  writes, safe to call as many times as needed for a preview. Loops
  occupied parcels, applying every non-`FIXED_PER_PERSON` item
  definition in scope; then calls `_compute_member_invoices()` for the
  `FIXED_PER_PERSON` items, which resolves each definition's target
  members and aggregates every definition targeting the same member
  onto **one** `ComputedInvoice` with multiple lines (mirrors how a
  parcel's several applicable items already merge onto its one
  invoice).
- **`finalize_run(db, run)`** -- runs the same computation once, in
  order, assigns permanent invoice numbers via
  `_first_invoice_sequence()`, persists `Invoice`/`InvoiceLineItem`
  rows, and flips the run to `FINALIZED`. There is no "regenerate a
  draft run" -- item definitions stay fully editable up to this point
  instead.

Per-parcel quantity/price resolution (`item_quantity_and_price`) pulls
from other modules rather than storing its own numbers:
`WATER_USAGE`/`ELECTRICITY_USAGE` read consumption via
`app/meter_utils.py`'s `calculate_consumption()` and price per unit via
`MeteringPriceConfiguration` (per medium/year -- see
[module-metering.md](./module-metering.md)), ignoring `unit_price`
entirely, same as the two modes below. `INSURANCE_COST` ignores
`unit_price` entirely and is handled outside
`item_quantity_and_price` altogether: instead of one combined amount,
`app/insurance_utils.py`'s `insurance_cost_line_items()` (issue #93)
returns one `(label, amount)` pair per component actually owed --
property insurance, accident insurance for the household, and a
separate "+N additional persons" line when applicable -- and
`compute_invoices_for_run` turns each pair into its own
`ComputedLineItem`, all sharing the definition's `order_number`. This
is deliberately not routed through the single-line-per-definition path
every other pricing mode uses, since the invoice recipient is meant to
see the insurance type and fee for each part, not one opaque total
(a member with only property insurance gets one line, one with both
gets two, +N additional persons adds a third). The labels come from
`translate()` using the club's configured language (`ClubSetting
"language"`), not the item definition's own name/description, since
they're generated per parcel rather than typed once by an admin.

`COMMUNAL_AREA_SHARE` (issue #82) bills Area B (communal, see
`app/area_utils.py`) split evenly across however many parcels actually
get billed for that specific item definition -- the denominator is
per-definition, not global, since two communal-share items could be
scoped to different parcel subsets. `PUBLIC_BURDENS` (issue #163)
reuses that exact same per-definition denominator/split, but adds it
**on top of** the parcel's own leased area (`PER_SQM`'s quantity) at
one combined rate, rather than billing the communal share alone. The
two modes deliberately diverge on missing-data behavior: if Area B
isn't configured (or has no eligible parcels), `COMMUNAL_AREA_SHARE`
bills nothing at all (its only component is the missing one), while
`PUBLIC_BURDENS` still bills the parcel's own area with the communal
share simply treated as 0 -- the own-area component is always
well-defined and shouldn't silently vanish over an unrelated club
setting.

`GENERAL_LEVY` (issue #171, "Umlage") reuses the exact same billable-
parcel denominator as a third consumer, but for an unrelated purpose:
`unit_price` here holds a single TOTAL amount the club needs to cover
(e.g. a one-off legal fee or an insurance premium hike), split evenly
across every billable parcel rather than multiplied by a per-unit
rate. Quantized to cents (`0.01`), not the tenth-of-a-sqm precision the
area-based modes use, since this is money, not an area share. Like
`COMMUNAL_AREA_SHARE`, a zero denominator means the item bills nothing
at all rather than dividing by zero.

Invoice numbering (`invoice_number_format` / `invoice_number_start`
`ClubSetting`s, issue #65) is club-configurable
(`{year}/{number}` by default) and supports a one-shot starting-sequence
override that's checked for collisions against every number already
used that year before being accepted, then cleared back to blank so it
doesn't keep forcing every future run to the same start.

## Delivery: `app/invoice_delivery.py`

Recipient resolution is re-derived at send time, not read from the
snapshot, since delivery can happen well after finalization and
membership may have changed. For a parcel invoice: current
invoice-address residents grouped by shared address (same pattern as
`app/insurance_utils.py`'s `household_grouping`). For a member invoice:
that one member directly, no grouping needed. Three delivery paths:
email (PDF attached, requires `email_notifications=True` and a stored
address), a merged print bundle PDF for everyone not reachable by
email, and upload to the parcel's cloud folder (member invoices have no
cloud-folder concept, since that concept is inherently parcel-scoped --
see `docs/module-cloud-storage.md`). Reminders (`InvoiceReminder`,
issue #59) are delivered the same way, resolved per-invoice at send
time.

## PDF layout: `app/invoice_pdf.py`

WeasyPrint-rendered. The address block is positioned per **DIN 5008
Form A** (the standard German business-letter window-envelope layout),
and the header places the club logo at the page's true left edge with
the club name centered across the page in one row -- both deliberately
matching German business-correspondence convention rather than an
arbitrary layout choice, since these invoices are expected to be
printed and mailed in window envelopes.

## Payments and reminders

`InvoicePayment` supports multiple partial payments per invoice (issue
#58). `Invoice.payment_status` (`open`/`partially_paid`/`paid`) is
**derived** from `payments` vs. `total_owed`, never stored, so it can't
go stale. `InvoiceReminder.level` is a simple incrementing counter (no
fixed/named dunning stages, so a club can run whatever collection
process it wants); an optional per-reminder `fee_amount` is added to
what the invoice owes (`Invoice.reminder_fees_total`) when present, but
nothing charges one automatically -- a board member decides per
reminder.

Both invoice lists are searchable/filterable (issue #190):
`/finances/invoices` (outgoing, across every run) by invoice number,
recipient, amount range, and payment status; `/finances/incoming-invoices`
by invoice number, sender, amount range, and payment status.
`/finances/runs/{id}` (a single run's own invoice table) got the same
invoice-number/recipient/parcel/amount/status filters as a same-session
follow-up -- the flat cross-run list doesn't replace the run-scoped
view, which can still run to one row per parcel. Invoice number/
recipient/sender/parcel filter at the SQL level; amount and status
filter in Python after loading, since `payment_status` (and, for
incoming invoices, `total_amount`) are computed properties, not
columns -- same approach the outgoing list's status filter already
used before this issue.

## Bookkeeping categories

`FinanceCategory` (issue #67) is a short code + title + one of
`INCOME`/`EXPENSE`/`FIXED_ASSETS`/`EQUITY_LIABILITIES`/`OTHER`, loosely
inspired by German chart-of-accounts conventions (the originating issue
referenced SKR42) without shipping any of DATEV's actual copyrighted
codes -- a club imports its own chart via CSV or types categories in by
hand. Purely a reporting tag on item definitions/templates; has no
effect on invoice generation.

## Accounts

`FinanceAccount` (issue #156) is a club's real bank/cash account (e.g.
an old and a new giro account, plus a cash box) -- `name`, `account_type`
(`BANK`/`CASH`), an optional `account_number`/IBAN and note, and
`is_active` so a closed/retired account can stay around for its
already-recorded payments' sake without still being offered when
recording a new one (`/finances/accounts`).

Started as purely a reporting tag on `InvoicePayment.account_id`
(nullable, `ON DELETE SET NULL` -- deleting an account never deletes
the payment record itself, only its account attribution), same role as
`FinanceCategory`. Issue #174 deliberately reopened the original "not a
ledger" stance: `/finances/accounts/{id}/bookings` shows a unified,
searchable, paginated (infinite scroll) list of everything ever booked
against the account -- `InvoicePayment` rows `UNION ALL`'d with the new
`AccountTransaction` rows (any other money movement: a refund, a
purchase, a bank fee, manually entered or CSV-imported, `ON DELETE
CASCADE` since a transaction only exists *for* its account). Supports
CSV export (honoring the current search/filter), always creates
`AccountTransaction` rows -- never auto-matches or creates an
`InvoicePayment`; reconciling an import against outstanding invoices
is a different, harder problem, explicitly out of scope. See
[ADR 0059](./ADR/0059-account-transactions-reopen-not-a-ledger-stance.md)
for the full reasoning.

CSV import (issue #186) is a two-step upload-then-map flow, not a
fixed expected header: step 1 (`/import/preview`) detects the file's
actual columns and lets the user assign each one to a Parcella field
(Date/Amount required, Description/Counterparty/IBAN optional,
pre-guessed from common header names but always overridable); step 2
(`/import/confirm`) applies that mapping to create the rows. If both
Counterparty and IBAN are mapped, a row whose counterparty exactly
matches an existing member's full name (either name order) backfills
that member's `iban` field when it's currently empty (issue #187). See
[ADR 0062](./ADR/0062-csv-import-column-mapping.md) for the full
reasoning, including why matching is exact-name rather than fuzzy.

Issue #185 added `AccountTransaction.counterparty` (free text -- who
sent or received the money) so the bookings list can show and search
by it; for `InvoicePayment` rows the counterparty is simply
`Invoice.recipient_names`, no new field needed. Issue #184 removed the
`source` filter/column (`invoice_payment`/`manual`/`csv_import`) from
this same list -- the user found it added noise without adding value;
`source` still exists on `AccountTransaction` internally (it decides
whether a row is deletable from this list at all) but is no longer
shown or filterable.

**Bug fixed in issue #189:** `_account_bookings_base`'s `UNION ALL`
never included `IncomingInvoicePayment` at all -- since issue #181
gave it an `account_id` and issue #188 started actively creating
tagged rows via invoice matching, any expense payment tagged to an
account had been silently invisible on that account's own bookings
page (while still correctly appearing in the club-wide bookings list,
issue #180, which was built with all three row types from the start).
Now a third `UNION ALL` branch, shown as a negative amount (an
outgoing InvoicePayment is a credit; an incoming one is a debit,
matching AccountTransaction's existing sign convention), linked to
`/finances/incoming-invoices/{id}`, and not deletable from this list
(same as an outgoing InvoicePayment -- remove it via the incoming
invoice's own payment-delete route instead). Also added an "assigned"
filter (linked to an outgoing/incoming invoice, or not) reusing the
`source` column that issue #184 stopped showing directly.

## Incoming invoices

`IncomingInvoice` (issue #178) is the mirror image of `Invoice` -- a
bill the club *received* from a supplier/vendor -- but far simpler:
recorded directly by hand at `/finances/incoming-invoices`, no
generation/finalization phases, no payment/reminder tracking. A single
invoice can carry several cost positions (`IncomingInvoiceLineItem`),
each with its own free-text `description` (what was actually bought --
distinct from the category, since e.g. three positions can all fall
under the same category yet describe different purchases) and tagged
with its own `FinanceCategory` (`category_id`, nullable, `ON DELETE
SET NULL` -- same historization-over-deletion precedent as
`InvoiceItemDefinition.category_id`: deleting a category later must
never destroy a historical bookkeeping record).

The scanned/photographed bill itself, if any, is never stored in this
app's own database or filesystem (the app doesn't store media at all).
Instead, `cloud_filename` just names a file inside **one shared**
Nextcloud folder configured for all incoming invoices (`ClubSetting`
key `incoming_invoices_cloud_folder`; configured on `/admin/integrations`
-- the "Nextcloud" card, alongside the shared connection credentials
and the per-parcel documents feature it also powers -- moved there
from the incoming-invoices page itself in issue #191, since it's a
system-admin-level setting like every other integration credential)
-- deliberately simpler than the per-parcel `ParcelCloudFolder` pattern
(`app/parcel_cloud_folders.py`), since there's no per-entity turnover
concept here that would need its own history table. Uploading/
downloading reuses the same `get_nextcloud_provider()` connection
(`app/cloud_storage.py`) `ParcelCloudFolder` already uses. Deleting an
`IncomingInvoice` only removes the DB row; an already-uploaded
attachment is left in the cloud folder untouched (this app's own data
is never the source of truth for the file itself).

`IncomingInvoicePayment` (issue #181) tracks when a bill was actually
paid -- same shape as `InvoicePayment` (amount, `paid_on`, optional
note/`FinanceAccount`), supporting partial payments the same way.
`IncomingInvoice.payment_status` (`open`/`partially_paid`/`paid`)
mirrors `Invoice.payment_status` minus the reminder-fee concept, which
incoming invoices don't have. Recorded directly on the incoming
invoice's own detail page (there's no "run" grouping several incoming
invoices together the way outgoing invoices have).

`external_contact_id` (optional, `ON DELETE SET NULL`) links the
invoice to the supplier in the external contacts module
(docs/module-external-contacts.md). It sits *alongside* the free-text
`sender` and doesn't replace it: search, the accounting statement and
bank matching keep reading `sender`. Picking a contact on the form
only fills in `sender` for you (ADR 0096).

## Cash-based accounting statement

`/finances/accounting-statement` (issue #179) is a per-calendar-year
income/expense breakdown by `FinanceCategory`, for handing to the tax
office -- built entirely in `app/accounting_statement.py`, no new
tables. Genuinely cash-based on both sides (issue #182): nothing
counts until it has actually been paid. Income comes from
`InvoicePayment`, expenses from `IncomingInvoicePayment` -- both dated
by `paid_on`, not by when the invoice was created/recorded. Neither
payment type has a category of its own, so each payment's amount is
split proportionally across its invoice's line-item categories,
weighted by each category's share of the invoice/incoming-invoice
total (shared logic: `_split_payment_by_category`) -- which only works
for invoices whose line items carry `category_id`
(`InvoiceLineItem.category_id` since #179) and incoming invoices that
have a payment recorded at all (`IncomingInvoicePayment` since #181);
anything predating those changes shows as "Uncategorized" or simply
doesn't appear until paid. `AccountTransaction` (issue #174's ledger)
is deliberately excluded -- it has no category either. See
[ADR 0060](./ADR/0060-cash-accounting-statement-income-categorization.md)
and [ADR 0061](./ADR/0061-accounting-statement-fully-cash-based.md)
for the full reasoning and accepted limitations. Exportable as PDF
(`app/accounting_statement_pdf.py`), same shared page chrome as every
other PDF in this app.

## All bookings (club-wide)

`/finances/bookings` (issue #180) lists every invoice payment across
the whole club -- `InvoicePayment` and `IncomingInvoicePayment`
combined into one chronological, filterable list (date range,
category, free-text search across sender/recipient/description,
amount range, income/expense direction). Built in `app/bookings.py`,
entirely in Python rather than a SQL `UNION ALL` (contrast with the
per-account bookings list, issue #174's `_account_bookings_base` in
`app/routers/finances.py`) because a single payment can touch several
categories via its invoice's line items -- a one-to-many relationship
that doesn't collapse into one row cleanly. Fine at real-world club
scale; would need a proper paginated SQL query if that ever stops
holding. `AccountTransaction` is excluded here too, same reasoning as
[ADR 0060](./ADR/0060-cash-accounting-statement-income-categorization.md):
no sender/recipient, no category.

## Matching a booking to an open invoice

Recording a manual booking or importing a CSV (issue #188) now offers
a match step before creating anything: `app/invoice_matching.py`'s
`find_matching_invoices()` looks for open (`payment_status != paid`)
invoices whose amount matches -- outgoing `Invoice`s for a positive
booking amount, `IncomingInvoice`s for a negative one -- and flags
whether the counterparty name overlaps the invoice's recipient/sender.
Picking a suggested match creates a real `InvoicePayment`/
`IncomingInvoicePayment` (tagged to the account) instead of a generic
`AccountTransaction`; declining (or no candidates existing) falls back
to the same generic-booking behavior as before. Manual add is a
three-step flow (`/manual/preview` -> `/manual/confirm`); CSV import
gained a middle "match" step between column mapping and actually
creating rows (`/import/match` -> `/import/finalize`), reviewed one
row at a time. See
[ADR 0063](./ADR/0063-invoice-payment-matching-for-bookings.md) for
why this is a deliberate, user-confirmed reopening of ADR 0059's
reconciliation-is-out-of-scope stance, not a general auto-matching
feature.

## Key decisions

**Person-scoped billing is not a special case of parcel billing** --
see [ADR 0042](./ADR/0042-invoice-item-targeting-plot-scoped-vs-person-scoped.md).
This was a real architectural correction made after an initial bolt-on
flag (`applies_to_members_without_parcel`, since removed) caused a form
that didn't make sense (a parcel picker showing up for a fee that was
supposed to be about people, not plots) and, separately, a real bug
where catalog-applied items always hardcoded `applies_to_all_parcels=True`
regardless of the source template, silently double-billing parcel
tenants for what was meant to be a person-only fee. Both issues went
away once plot-scope and person-scope became fully independent fields
routed purely by `pricing_mode`.

**Scope pickers stay editable at any time before the next invoice run
generates, not locked after first save.** Once a run is finalized,
its item definitions (and therefore their scope) are historical and
untouched; anything still `DRAFT` remains freely editable, including
switching a template's or item's parcel/member scope repeatedly before
the club actually runs invoices.

**Preview/finalize is one-way by design.** `compute_invoices_for_run`
never writes to the DB specifically so it can be called for a preview
as many times as needed with zero risk; `finalize_run` is the only
place invoice numbers get assigned, and it runs exactly once per run.
