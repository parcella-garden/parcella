# Invoice runs

An invoice run is one batch of invoices, usually "the annual invoices
2026". You describe once which lines go on the invoices and how each
amount is calculated. Parcella then works out the invoice for every
parcel (and for every member billed directly), lets you check each one
as a PDF, and only gives out invoice numbers when you finalize.

!!! info "Who can use this"
    Part of the **Finances** module (off by default). Reading needs
    **Finances** read permission; creating runs, editing items,
    finalizing and sending need write permission; deleting a run or an
    item needs delete permission. Board members and administrators can
    do everything. See [Finances](index.md).

A run is always in one of two states:

| Status | Meaning |
|---|---|
| **Draft** | The run is being prepared. Items can be added, changed and removed freely, the preview is recalculated every time you open it, and the whole run can still be deleted. No invoice exists yet. |
| **Finalized** | Invoices with permanent numbers have been created. The items are frozen, the run can no longer be deleted, and you now send the invoices and record payments. There is no way back to draft. |

## Annual invoices (list of runs)

![Annual invoices](../../assets/screenshots/finances/run-list.png)

Open it with **Finances → Outgoing Invoices**, or the **Outgoing
Invoices** card on the dashboard. It lists every invoice run, newest
year first.

**Top bar**

| Button | What it does |
|---|---|
| **New invoice run** | Opens the form for a new run (see below). Only shown with write permission. |
| **All invoices** | Opens the list of every invoice across all runs, see [Invoices](invoices.md#invoices-all-runs). |
| **Back to Finances** | Back to the finances dashboard. |

**Filter**

| Filter | What it does |
|---|---|
| **Year** | Shows only runs of exactly this year. |
| **Subject** | Shows runs whose subject contains this text (upper/lower case doesn't matter). |
| **Status** | **All**, **Draft** or **Finalized**. |
| **Filter** / **Reset** | Applies the filter / clears all filters. |

**Invoice runs table**

| Column / button | What it shows |
|---|---|
| **Year** | The year the run bills. |
| **Subject** | The run's subject, as printed on the invoices. |
| **Status** | **Draft** (yellow) or **Finalized** (green). |
| **Items** | How many item definitions (invoice lines) the run has. |
| **Open** | Opens the run. |
| Bin icon | Deletes the run with all its item definitions, after a confirmation. Only shown for draft runs and with delete permission. A finalized run can never be deleted. |

If there are no runs yet, the table says "No invoice runs yet."; if
your filter matches nothing, "No invoice runs match the filter."

### New invoice run

Click **New invoice run** in the top bar. A dialog opens:

| Field | What it does |
|---|---|
| **Year** | Required. Pre-filled with the current year. This year decides which meter readings, insurance records and work-hours evaluation the usage-based items use, and which year the invoice numbers count in. |
| **Subject** | Required. The heading of every invoice, e.g. "Annual invoice 2026". |
| **Issued date** | Required. Pre-filled with today. Printed on the invoices as the invoice date. |
| **Due date** | Required. Printed on the invoices. It also decides when an unpaid invoice counts as overdue and shows up under [Reminders](invoices.md#reminders). |
| **Footer text** | Optional. Printed below the line items on every invoice of the run, e.g. your payment instructions. You can use these placeholders, which are filled in per invoice: `{invoice_number}`, `{parcel_number}`, `{invoice_address}` (recipient names and address), `{due_date}`. |
| **Create** | Creates the run as a draft and opens it. |
| **Cancel** | Closes the dialog without saving. |

!!! tip "Placeholders in the footer text"
    A typical footer is "Please transfer the amount by {due_date},
    quoting {invoice_number} as reference." If the footer text contains
    a curly brace that isn't one of the four placeholders, the text is
    printed exactly as you typed it, without filling in anything.
    On a member invoice (one without a parcel) there is no parcel
    number to fill in, so avoid `{parcel_number}` if the run will also
    produce member invoices.
    <!-- TODO(verify): by the code, a member invoice's footer prints the literal word "None" for {parcel_number}; confirm in a real PDF. -->

The year, subject, dates and footer text can't be changed after the run
is created. <!-- TODO(verify): no edit route for run header fields exists; if a mistake is made in a draft run, the only way is to delete and recreate it. -->

## Invoice run (draft)

![Draft invoice run](../../assets/screenshots/finances/run-detail.png)

The page title shows year and subject, e.g. "2026 — Annual invoice".
While the run is a draft, this page is where you put together its
lines ("item definitions").

**Top bar**

| Button | What it does |
|---|---|
| **Preview** | Opens the [preview](#preview-invoices). Only shown once the run has at least one item. |
| **Back to invoice runs** | Back to the list. |

### Item definitions

Each row is one kind of line that can appear on the invoices. With
write permission every row is directly editable; change the fields and
click the tick icon at the end of the row to save that row. Without
write permission you see the same information as plain text.

| Column / field | What it does |
|---|---|
| **Order** | Sorting number. Lines appear on the invoice in this order. A new item is pre-filled with ten more than the highest order number so far, leaving room to slot an item in between later. |
| **Name** | Required. The line's text on the invoice, e.g. "Lease". |
| **Description** | Optional, the small grey field below the name. Printed in small type under the name on the invoice. |
| **Pricing** | How the amount is calculated, see [Calculation bases](#calculation-bases) below. Changing it changes which of the other fields are shown. |
| **Unit price** | The price per unit (per parcel, per person, per m² ...). For general levy it is the total to be split. Hidden for the four automatic pricing modes, which show "Computed automatically" instead. Enter it with a decimal comma or point, e.g. `12,50`. |
| **Applies to** | Who the line is for. Depending on the pricing mode this is a switch **All parcels** / *n* parcel(s), a switch **All members** / *n* member(s), or a fixed note such as "Automatic (insurance evaluation)". See [Who gets a line](#who-gets-a-line). |
| **Category** | Optional [bookkeeping category](bookkeeping.md#bookkeeping-categories). It is copied onto every invoice line, so payments of this invoice are split into the right categories in the [accounting statement](bookkeeping.md#accounting-statement). |
| Tick icon | Saves the row. Needs write permission. |
| Bin icon | Deletes the item after a confirmation ("Delete this item definition?"). Needs delete permission. |

When you switch a row's **Applies to** switch off, an extra row opens
below it with the parcel or member picker (see [The picker](#the-picker)).

!!! note
    Items can only be changed while the run is a draft. Trying to save
    an item on a finalized run is refused with "This invoice run is
    already finalized; its item definitions can no longer be changed."

### Add from item catalog

Shown with write permission when your [item catalog](#item-catalog)
contains templates this run doesn't have yet. Every remaining template
is listed with its pricing mode, unit price and scope, and **is ticked
by default**. Untick what you don't want and click **Add selected
items**. Each ticked template becomes a new item on this run, with all
its settings, including a specific parcel or member selection.

**Manage catalog** takes you to the item catalog.

A template counts as "already added" when the run has an item with
exactly the same name. So if you rename or delete the item on the run,
the template is offered again; if you rename the template after adding
it, it is offered again too.

When there is nothing left to offer you see a short note instead:
"Every catalog item has already been added to this run." or, if the
catalog is empty, "No catalog items yet -- add reusable items once and
pick from them here every year." Both have a **Manage catalog** button.

### Add item

Below the catalog, a form to add a one-off item by hand. It has the
same fields as the table (**Order**, **Name**, **Description**,
**Pricing mode**, **Unit price**, **Category**), then the scope switch
(**Applies to every parcel** or **Applies to every member**, both on by
default) and, when you switch it off, the picker. Click the **+**
button to add the item.

## Calculation bases

The **Pricing mode** decides how Parcella calculates the line for each
parcel or member. Every amount is rounded to the cent per line; the
invoice total is the sum of its lines.

| Pricing mode | Billed to | Quantity × price | Where the numbers come from |
|---|---|---|---|
| **Fixed amount per parcel** | Each parcel in scope | 1 × unit price | You enter the amount, e.g. a club fee per parcel. |
| **Fixed amount per person** | Each member in scope, on their own invoice | 1 × unit price | You enter the amount, e.g. the membership fee. Billed per member, whether or not they have a parcel. |
| **Per leased m²** | Each parcel in scope | parcel area × unit price | The area stored on the parcel. A parcel without an area gets no line. |
| **Share of the communal area lease** | Each parcel in scope | (communal area ÷ number of billed parcels) × unit price | The communal area ("Area B") from [Club settings](../../administration/settings.md). The share is rounded to 0.1 m². |
| **Public burdens (own area + communal area share)** | Each parcel in scope | (parcel area + communal area share) × unit price | As above, plus the parcel's own area, at one rate per m². |
| **General levy (split evenly across all parcels)** | Each parcel in scope | 1 × (total ÷ number of billed parcels) | You enter the **total** the club needs to collect as unit price; each parcel pays an equal share, rounded to the cent. |
| **Water usage (from module)** | Every parcel with a water meter | the year's consumption × price per unit | Consumption and price come from [Water and electricity](../metering.md). |
| **Electricity usage (from module)** | Every parcel with an electricity meter | the year's consumption × price per unit | As for water. |
| **Insurance cost (from module)** | Every parcel with insurance for the year | one line per insurance component | From [Insurance](../insurance.md). |
| **Work-hours shortfall (from module)** | Every parcel or member who owes money for missing work hours | 1 × amount owed | From the [work-hours evaluation](../work-hours.md) of the run's year. |

Details for each mode:

**Fixed amount per parcel / per person.** If you leave **Unit price**
empty, the item bills nothing.

**Per leased m².** Uses the area recorded for each parcel. Check that
every parcel has its area filled in before you finalize -- a parcel
without one silently gets no lease line.

**Share of the communal area lease.** The communal area is split evenly
among exactly the parcels that receive this item (those in its scope
that also have someone to invoice). That way the shares add up to the
whole communal area and the club collects the full lease. If the
communal area is zero or not set up, the item bills nothing at all.
The communal area is worked out in Club settings as total area minus
the parcels' area minus the municipal area.

**Public burdens** ("Öffentliche Lasten", see the
[glossary](../../glossary.md)). Like the communal share, but added to
the parcel's own area and billed at one combined rate. If the communal
area isn't set up, the parcel's own area is still billed -- the
communal part simply counts as 0 m².

**General levy** ("Umlage", see the [glossary](../../glossary.md)). Use
it for a one-off cost the club passes on, e.g. a legal fee of 1,200.00
split across 40 parcels = 30.00 each. Only parcels that are actually
billed count, so vacant parcels never "eat" a share. Because each share
is rounded to the cent, the total collected can differ from the amount
you entered by a few cents.

**Water usage / Electricity usage.** For every parcel with a parcel
metering point of that kind, Parcella takes the current meter's
consumption in the run's year (that year's reading minus the reading
before it) and multiplies it by the price per unit set for that year in
the metering module. You don't enter a unit price here.

- A parcel without a reading for the year gets no line.
- If no price is set for that medium and year, nobody is billed for it.
- After a meter exchange during the year, the consumption of **both**
  meters is billed: the old one up to its final reading (entered in the
  exchange form) and the new one from its initial reading.

!!! warning "Metering points with a factor"
    If a metering point has a factor (multiplier) in the metering
    module, the metering screens show the multiplied consumption, but
    the invoice bills the **raw** difference of the meter readings.
    Check such parcels in the preview.


**Insurance cost.** Billed for every parcel that has an insurance record
for the run's year. Instead of one lump sum, the invoice shows one line
per component the parcel actually has: "Property insurance (*package*)",
"Accident insurance (household)" and, if applicable, "Accident
insurance (+*n* additional person(s))". These line texts are fixed,
in the club's language -- the item's own name isn't used for them.
Amounts come from the insurance prices set up for that year.

**Work-hours shortfall.** Bills whatever the work-hours evaluation for
the run's year says is owed, at exactly that amount. Exempt and
fulfilled parcels or members are not billed. Whether this ends up on
the parcel invoice or on a separate member invoice depends on how work
hours are counted that year: per parcel puts it on the parcel's
invoice, per member puts it on each member's own invoice.

## Who gets a line

**Plot-based modes** (fixed per parcel, per m², communal share, public
burdens, general levy) use the **Applies to every parcel** switch:

- On (default): every parcel that can be billed.
- Off: only the parcels you tick in the picker.

**Fixed amount per person** uses **Applies to every member** instead:

- On (default): every active member.
- Off: only the members you tick.

**The four automatic modes** (water, electricity, insurance, work-hours
shortfall) have no picker. Who is billed follows from the other module:
having a meter, an insurance record, or a shortfall. A note such as
"Automatic (parcels with an active water meter)" is shown instead.
(Despite the wording, a metering point that has been switched off is
still included in the run.)

Which parcels can be billed at all:

- A parcel gets an invoice only if at least one **current** tenant is
  marked **Use as invoice address**. Tenants who gave notice for a
  future date still count until they have actually left.
- A terminated parcel is still billed if it has such a tenant (for
  example a new tenant who took over before the status was changed
  back). Only deleted parcels are always skipped.
- If several invoice-address tenants live at different addresses, the
  invoice is addressed to the largest group that shares one address.
- A parcel whose lines all come out empty gets no invoice.

Member invoices (from **Fixed amount per person**, or work-hours
shortfall counted per member) are separate invoices addressed to the
member at their own address. They show **No parcel (member)** instead
of a parcel number. A tenant who is also billed a per-person fee
therefore gets two invoices: one for the parcel, one for themselves.
All per-person lines for the same member are combined on one invoice.

### The picker

When a scope switch is off, a picker appears with the label
**Parcels** or **Members**.

| Control | What it does |
|---|---|
| **Show list** / **Hide list** | Opens or closes the list of checkboxes. |
| **Search…** | Narrows the list to matching parcel numbers or names. "No matches" appears when nothing fits. |
| **Select all** / **Select none** | Ticks or unticks every entry **currently visible** -- so you can search first and then select just those. |

The parcel picker lists active parcels; the member picker lists active
members.

!!! tip
    The scope stays editable until you finalize. You can change it as
    often as you like while preparing the run.

## Preview invoices

<!-- TODO(verify): no screenshot -- the preview page is two clicks away from a fixed URL (run list -> run -> Preview), which the screenshot tool can't follow, and the sample data has no invoice runs. -->

Click **Preview** on a draft run. Parcella calculates every invoice the
run would produce, right now, without saving or sending anything. The
page title is "Preview — *year* *subject*".

The blue box at the top says how many invoices would be generated and
reminds you: "Nothing is saved or sent yet — review the PDFs below, then
finalize when ready."

| Column / button | What it shows |
|---|---|
| **Parcel** | The parcel number, or **No parcel (member)** for a member invoice. |
| **Recipient** | The names the invoice will be addressed to. |
| **Subtotal** | The invoice total. |
| **PDF** | Opens the invoice as a PDF in a new tab, exactly as it will look, with "Preview" as invoice number and a "Preview — not yet finalized or sent" banner. |
| **Finalize & assign invoice numbers** | Finalizes the run, after a confirmation. Only shown with write permission while the run is a draft. |
| **Back to invoice run** | Back to the run, to correct items. |

If the list is empty, the page says "No invoices would be generated —
check the item definitions' parcel scope and the affected members'
invoice-address flag."

!!! tip "The preview is always live"
    Nothing is stored for the preview. Each time you open it, it reads
    the current parcels, tenants, meter readings, insurance and work
    hours. Correct data in those modules, then simply reload.

### What finalizing does

When you click **Finalize & assign invoice numbers** and confirm
("Finalize this run? Invoice numbers will be permanently assigned and
item definitions can no longer be changed. This cannot be undone."):

1. Parcella calculates the invoices one last time, exactly like the
   preview.
2. Each invoice gets a permanent number, in the order of the preview
   list. The format comes from **Invoice number format** in
   [Club settings](../../administration/settings.md) (default
   *year*/*number*, e.g. `2026/1`). Numbering continues from the
   highest number already used in the same year, across all runs, and
   starts at 1 for the year's first invoice.
3. The recipients' names and addresses are copied onto the invoices.
   Later changes to a member's address don't rewrite an invoice
   that has already been issued.
4. The run becomes **Finalized** and its items are frozen.

If **Next invoice number (override)** is filled in in Club settings,
this run starts at that number instead, and the setting is cleared
afterwards. If that would reuse a number already given out in the same
year, finalizing stops with an error message and nothing is created.

A run without any item can't be finalized: "This invoice run has no
item definitions yet — add at least one before finalizing."

## Invoice run (finalized)

Once finalized, the run page shows a green note "This invoice run is
finalized. Invoice numbers are permanent and item definitions can no
longer be changed." The item list is gone; instead you see delivery
and the run's invoices.

### Delivery

Shown with write permission.

| Button | What it does |
|---|---|
| **Send emails & upload to cloud** | Emails every invoice of the run that hasn't been emailed yet, with the PDF attached, and uploads every invoice that hasn't been uploaded yet to its parcel's cloud folder. Running it again only picks up what's still missing. |
| **Download print bundle** | Downloads one PDF containing every invoice whose recipient can't be reached by email, ready to print and put in window envelopes. Those invoices are marked as printed. |

**Who gets an email:** a current invoice-address tenant of the parcel
(or, for a member invoice, the member) who has **May receive
information by email** switched on and at least one email address
stored. The primary address is used. Everyone else is left for the
print bundle: "Members without email notifications stay for the print
bundle below."

**Cloud upload** only happens if cloud storage is set up and the parcel
has a cloud folder. Member invoices are never uploaded, because there
is no member folder. Failed uploads are skipped silently and tried
again next time.

!!! note "Print bundle"
    The bundle is put together from who can be reached by email, not
    from what has been sent. You can download it before or after
    sending emails and it always contains the same invoices -- including
    ones you already printed last time. If every invoice can go by
    email, you get the message "Every invoice in this run has a member
    who is reachable by email -- nothing left to print."

### Filter

Above the invoice table you can narrow the list. It works like the
filter on [All invoices](invoices.md#invoices-all-runs): **Invoice
no.**, **Recipient**, **Parcel** (contains this text), **Min. amount**,
**Max. amount** (invoice subtotal) and **Status** (**All**, **Open**,
**Partially paid**, **Paid**). **Filter** applies it, **Reset** clears it.

### Invoices

| Column / button | What it shows |
|---|---|
| **Invoice no.** | The invoice number; click it to open the [invoice](invoices.md#invoice). |
| **Parcel** | Parcel number, or **No parcel (member)**. |
| **Recipient** | The recipient names. |
| **Subtotal** | The invoice amount. |
| **Payment status** | **Open** (red, nothing paid), **Partially paid** (yellow) or **Paid** (green). |
| **Delivery** | Icons for what has happened: envelope = "Emailed", printer = "Included in a print bundle", cloud = "Uploaded to cloud storage". Hover over an icon to see its meaning. |
| **Payment** | Opens the payment dialog for this invoice (see below). Needs write permission. |
| **PDF** | Opens the invoice PDF in a new tab. |

### Payment dialog

The quickest way to record payments for many invoices: click
**Payment** on a row, enter the payment, and you are back on the run
page, ready for the next one. The dialog title is "Payment — Invoice
*number*".

It lists the payments recorded so far (date, amount, account, note),
each with a bin icon to delete it (needs delete permission, asks
"Delete this payment?"). If there are none: "No payments recorded yet."

| Field | What it does |
|---|---|
| **Amount** | Required. The amount received, e.g. `45,00`. Partial payments are fine; record each one separately. |
| **Paid on** | Required. Pre-filled with today. This date decides in which year the income counts in the accounting statement. |
| **Note** | Optional, e.g. "bank transfer". |
| **Account** | Optional. The [account](bank-accounts.md#accounts) the money arrived in. Only active accounts are offered. The payment then shows up in that account's bookings. |
| **Add payment** | Saves the payment. |

The payment status updates by itself: once the payments reach the
invoice amount plus any reminder fees, the invoice is **Paid**. See
[Payments](invoices.md#payments).

## Item catalog

![Item catalog](../../assets/screenshots/finances/item-templates.png)

Open it from the **Item catalog** card on the dashboard or with
**Manage catalog** on a draft run. The catalog holds your recurring
invoice lines ("item templates") so you don't have to type them again
every year. Templates are independent of any run; you pull them into a
run with [Add from item catalog](#add-from-item-catalog).

The screen has the same fields as a run's items:

- **New item template** (with write permission): **Order**, **Name**,
  **Description**, **Pricing mode**, **Unit price**, **Category**, the
  scope switch (**Applies to every parcel** / **Applies to every
  member**) and the [picker](#the-picker). Click the **+** button to save.
- **Item templates**: one editable row per template with the columns
  **Order**, **Name**, **Pricing**, **Unit price**, **Applies to** and
  **Category**. Change a row and click its tick icon to save it; the
  bin icon deletes it (needs delete permission).

After saving you see "Saved.". If the catalog is empty: "No item
templates yet -- add one above."

The pricing modes and scope rules are exactly the ones described under
[Calculation bases](#calculation-bases) and [Who gets a line](#who-gets-a-line).

!!! note "Templates and runs are independent"
    Adding a template to a run copies it. Changing a template later
    does not change runs that already used it, and deleting a template
    leaves those runs' items untouched ("Delete this item template?
    Runs that already used it keep their items, just without a link
    back to the template."). Prices that change every year are best
    updated in the catalog before you add the items to the new run.

## Related

- [Running the annual invoices](../../guides/annual-invoicing.md) -- the
  whole process step by step.
- [Invoices, payments and reminders](invoices.md)
- [Water and electricity](../metering.md), [Insurance](../insurance.md),
  [Work hours](../work-hours.md) -- where the automatic amounts come from.
- [Club settings](../../administration/settings.md) -- invoice number
  format, bank details, areas.
