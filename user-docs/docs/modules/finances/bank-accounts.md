# Bank accounts and bookings

Here you record the club's real accounts -- giro accounts, a savings
account, the cash box -- and see everything that was booked on each of
them. You can add bookings by hand or import your bank statement as a
CSV file. While doing so, Parcella offers to match each booking to an
open invoice, so an incoming transfer is recorded as the member's
payment straight away.

!!! info "Who can use this"
    Part of the **Finances** module (off by default). Viewing accounts
    and bookings, and exporting CSV, needs **Finances** read permission.
    Creating or changing accounts, adding bookings and importing need
    write permission; deleting accounts or bookings needs delete
    permission. Board members and administrators can do everything.
    See [Finances](index.md).

!!! note "Not a full ledger"
    An account's bookings list is a record of money movements, not
    double-entry bookkeeping. There is no opening balance and no running
    balance. Bookings that aren't tied to an invoice (a bank fee, a
    refund) have no category, so they don't appear in the
    [accounting statement](bookkeeping.md#accounting-statement).

## Accounts

![Accounts](../../assets/screenshots/finances/account-list.png)

Open it with the **Accounts** card on the finances dashboard.
**Back to Finances** in the top bar takes you back.

### New account

Shown with write permission.

| Field | What it does |
|---|---|
| **Name** | Required, e.g. "Giro Sparkasse" or "Cash box". Saving without a name shows "A name is required". |
| **Type** | **Bank** or **Cash**. |
| **Account number/IBAN** | Optional, for your reference. |
| **Note** | Optional. |
| **Active** | On by default. Only active accounts are offered when you record a payment. Switch it off for an account you closed: its history stays, but it isn't offered any more. |
| **Add account** | Saves the account. You see "Done.". |

### Accounts list

| Column / button | What it shows |
|---|---|
| **Name**, **Type**, **Account number/IBAN**, **Note**, **Active** | The account's details. With write permission they are editable in the row; click the tick icon to save. |
| **Payments recorded** | The sum of all payments for outgoing invoices that were recorded against this account. Payments of incoming invoices and other bookings are not included. |
| Bookings icon | Opens the account's [bookings](#bookings-of-an-account). |
| Tick icon | Saves the row. Needs write permission. |
| Bin icon | Deletes the account after "Delete this account? It has no bookings." Needs delete permission. Greyed out for an account that has bookings (see below). |

If there are no accounts yet: "No accounts yet -- add one above."

!!! note "Accounts with bookings can't be deleted"
    Only an account without any bookings -- no booking entered by hand
    or imported, no invoice payment recorded on it -- can be deleted.
    For any other account the bin is greyed out ("Has bookings: untick
    “Active” to retire it instead."). Switching **Active** off hides the
    account from the payment forms and keeps all its bookings.

## Bookings of an account

![Bookings of an account](../../assets/screenshots/finances/account-bookings.png)

Open it with the bookings icon on the accounts list. The title is
"Bookings — *account name*". It shows everything booked on this account,
newest first:

- payments of outgoing invoices recorded with this account (positive
  amounts),
- payments of [incoming invoices](incoming-invoices.md) recorded with
  this account (negative amounts),
- other bookings you entered by hand or imported (positive or negative,
  as entered).

The first 50 bookings are shown; more load automatically as you scroll
down. The **Back to Finances** button in the top bar takes you back to
the accounts list (despite its label). On the import screens below, the
same button takes you back to the account's bookings without importing
anything.

### Filter and actions

| Field / button | What it does |
|---|---|
| **Search** | Finds bookings whose reference, description or sender/recipient contains this text. |
| **From** / **To** | Only bookings on or between these dates. |
| **Min. amount** / **Max. amount** | Only bookings with an amount in this range. Remember that outgoing money is negative: to find expenses of 100 or more, set **Max. amount** to `-100`. |
| **Assigned** | **All**, **Assigned to an invoice** (invoice payments) or **Not assigned** (other bookings). Handy to find bank lines that still need checking. |
| **Filter** / **Reset** | Applies the filter / clears it. |
| **Export CSV** | Downloads the bookings that match the current filter as a CSV file (semicolon-separated: date, amount, reference, description, counterparty). Needs only read permission. |
| **Import CSV** | Opens the import dialog, see [Importing a bank statement](#importing-a-bank-statement). Needs write permission. |
| **Add booking** | Opens the dialog for a booking by hand, see [Adding a booking by hand](#adding-a-booking-by-hand). Needs write permission. |

### Bookings table

| Column / button | What it shows |
|---|---|
| **Date** | The booking date. |
| **Amount** | The amount; outgoing money is shown in red with a minus sign. |
| **Reference** | For an invoice payment, the invoice number as a link to the invoice (or incoming invoice). Empty for other bookings. |
| **Description** | The payment note or booking description. |
| **Sender / recipient** | Who paid or was paid: the invoice recipient, the incoming invoice's sender, or the counterparty you entered. |
| Bin icon | Deletes the booking after "Really delete this booking?". Only for bookings entered by hand or imported, and only with delete permission. Invoice payments can't be deleted here -- delete them on the invoice instead. |

If the account has no bookings: "No bookings yet."

After an import or a match, a green message at the top tells you what
happened, e.g. "12 imported, 1 skipped.", "3 booking(s) matched to an
existing invoice.", "2 member IBAN(s) filled in from the import." or,
after a single booking, "Recorded as a payment against the matched
invoice."

## Adding a booking by hand

Click **Add booking**. The dialog asks for:

| Field | What it does |
|---|---|
| **Date** | Required, pre-filled with today. |
| **Amount** | Required. Positive for money coming in, negative for money going out, e.g. `-12,50`. |
| **Description** | Optional. |
| **Sender / recipient** | Optional. Also used to suggest a matching invoice. |
| **Add booking** | Continues to the matching step. |

### Possible matching invoices

<!-- No screenshot: this page is only reached by submitting the form above. -->

Before anything is saved, Parcella looks for open invoices with the
same amount: for a positive amount, outgoing invoices that still have
exactly that much due; for a negative amount, incoming invoices with
that much still unpaid. It shows the booking's **Date**, **Amount** and
**Sender / recipient**, and then the choices:

| Choice | What happens |
|---|---|
| **Record as a generic booking** | Saves a normal booking on the account, not tied to any invoice. |
| One line per matching invoice | Shows the invoice (number and recipient, or sender and number) and "due *amount*". A green "name matches" badge appears when the sender/recipient you entered shares a name with the invoice's recipient or sender. Picking it records the booking as a **payment of that invoice**, with this account, date and the description as note. |
| **Add booking** | Saves your choice. |

At most five invoices are suggested, those with a matching name first.
If exactly one suggestion has a matching name, it is pre-selected;
otherwise **Record as a generic booking** is. If no invoice matches:
"No open invoices match this amount."

!!! tip
    Matching only compares the amount still due, to the cent. An
    invoice with a reminder fee is due with the fee included, and a
    partially paid invoice only with what's left.

## Importing a bank statement

Most banks let you download the account statement as a CSV file. Any
column layout works. Import takes three steps.

**1. Upload.** Click **Import CSV**, choose the file and click **Import
CSV**. "Any CSV works -- upload it, then match its columns to
Parcella's fields on the next screen." Semicolon and comma separated
files are both recognised, as are UTF-8 and older Windows encodings.
An empty file is refused with "That CSV file appears to be empty."

**2. Map CSV columns.** <!-- No screenshot: reached only by uploading a file. -->
"For each column below, choose which Parcella field it belongs to (or
leave it ignored). Date and Amount are required." The page shows your
file's column headings, each with a drop-down, and the first five rows
as a sample.

| Field | Meaning |
|---|---|
| **— Ignore —** | The column isn't used. |
| **Date** | Required. The booking date. Accepted formats: `2026-03-31`, `31.03.2026` and `31.03.26`. |
| **Amount** | Required. Signed amount, with a decimal comma or point (`-12,50` or `-12.50`). Thousands separators are fine, as your bank exports them: `1.234,56`, `1,234.56` or `1 234,56`. |
| **Description** | Optional, e.g. the purpose of payment. |
| **Sender / recipient** | Optional. Used for matching and shown in the list. |
| **IBAN** | Optional. See the tip below. |

Common German and English headings ("Buchungsdatum", "Betrag",
"Verwendungszweck", "Auftraggeber", "IBAN" ...) are pre-selected for
you; check them anyway. Click **Import CSV** to continue. If **Date** or
**Amount** isn't mapped, you're sent back with "Please map at least one
column each to Date and Amount."

**3. Match rows to invoices.** <!-- No screenshot: reached only through the import. -->
"For each row, pick a matching open invoice to record it as a real
payment, or leave it as a generic booking." Each row shows **Date**,
**Amount**, **Sender / recipient** and a **Match** drop-down with
**Don't import**, **Record as a generic booking** and the suggested
invoices (amount due in brackets, a ✓ when the name matches). The
pre-selection works as for a single booking. Rows whose date or amount
couldn't be read show "Invalid row — will be skipped". A row that is
already on this account gets an **Already imported** badge and is preset
to **Don't import**. Click **Import CSV** to save everything.

What gets saved:

- each row with an invoice picked becomes a payment of that invoice on
  this account -- unless that invoice has been paid in full in the
  meantime: then nothing is recorded, and the result message says so;
- each other valid row becomes a normal booking;
- rows set to **Don't import**, and invalid rows, are skipped and
  counted in the result message.

!!! tip "Filling in members' IBANs"
    If you map both **Sender / recipient** and **IBAN**, Parcella looks
    for a member whose name is exactly the sender's name (first name
    last name, or last name first name, upper/lower case ignored). If
    that member has no IBAN stored yet, the IBAN from the statement is
    filled in. Existing IBANs are never overwritten.

!!! tip "Importing the same statement twice"
    A row counts as already imported when this account already has a
    booking with the same date, amount and description (a payment
    recorded against an invoice counts too). Overlapping exports are
    therefore safe: only the new rows are added. Parcella counts rather
    than just compares -- if the file has the same coffee purchase twice
    on one day and the account has it once, one of them is new.

    A row that already exists is only imported if you change its
    **Don't import** to something else. Clicking **Import CSV** twice,
    or sending the page again with the back button, adds nothing.

## Related

- [Invoices, payments and reminders](invoices.md)
- [Incoming invoices](incoming-invoices.md)
- [All bookings](bookkeeping.md#all-bookings) -- every invoice payment
  across all accounts.
- [Members](../members.md) -- where the IBAN is stored.
