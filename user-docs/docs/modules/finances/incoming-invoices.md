# Incoming invoices

Incoming invoices are the bills the club receives: the water supplier,
the insurer, the hardware store. Recording them here, split into
positions with a bookkeeping category each, and noting when they were
paid gives you the expense side of the
[accounting statement](bookkeeping.md#accounting-statement).

!!! info "Who can use this"
    Part of the **Finances** module (off by default). Viewing needs
    **Finances** read permission; recording invoices, linking contacts
    and adding payments need write permission; deleting an invoice or a
    payment needs delete permission. Uploading and downloading the
    scanned bill (attachment) is only possible for board members and
    administrators, and only when the **Cloud storage** module is on and
    an incoming invoices folder is set up. See [Finances](index.md).

## Incoming invoices list

![Incoming invoices](../../assets/screenshots/finances/incoming-invoice-list.png)

Open it with **Finances → Incoming Invoices** or the **Incoming
Invoices** card on the dashboard. The list is sorted by invoice date,
newest first.

**Top bar**

| Button | What it does |
|---|---|
| **Record incoming invoice** | Opens the form for a new incoming invoice (see below). Needs write permission. |
| **Back to Finances** | Back to the finances dashboard. |

**Filter**

| Filter | What it does |
|---|---|
| **Invoice no.** | Invoices whose number contains this text. |
| **Sender** | Invoices whose sender contains this text. |
| **Min. amount** / **Max. amount** | Invoice total at least / at most this much. |
| **Payment status** | **All**, **Open**, **Partially paid** or **Paid**. |
| **Filter** / **Reset** | Applies the filter / clears it. |

**Table**

| Column / button | What it shows |
|---|---|
| **Date** | The invoice date. |
| **Sender** | Who sent the bill; click it to open the [incoming invoice](#incoming-invoice). |
| **Invoice no.** | The supplier's invoice number, if entered. |
| **Categories** | One line per position: its category (or "Uncategorized") and its description. |
| **Amount** | The invoice total (sum of all positions). |
| **Payment status** | **Open**, **Partially paid** or **Paid**, from the payments recorded. |
| Download icon | Downloads the attached bill. Only shown when there is an attachment and you may use cloud storage. |
| Bin icon | Deletes the incoming invoice, with its positions and payments, after a confirmation. Needs delete permission. |

If nothing has been recorded yet: "No incoming invoices recorded yet."

!!! note "Deleting keeps the attachment"
    "Really delete this incoming invoice? This does not delete the
    attachment from the cloud folder." The scanned bill stays in the
    shared folder; remove it there by hand if you need to.

## Record incoming invoice

Click **Record incoming invoice**. A dialog opens:

| Field | What it does |
|---|---|
| **Contact** | Optional. Only shown when the [External contacts](../external-contacts.md) module is on and you may read contacts. Picking a supplier from your contacts fills in **Sender** for you ("Picking a contact fills in the sender."), unless you already typed one. **— none —** links no contact. |
| **Sender** | Required. The supplier's name, as you want it to appear in lists, bank matching and the accounting statement. |
| **Invoice no.** | Optional. The supplier's invoice number. |
| **Invoice date** | Required, pre-filled with today. |
| **Note** | Optional. |
| **Positions** | One row per cost position (see below). |
| **Add position** | Adds another position row. Every row except the first has a remove button. |
| **Attachment** | Optional. The scanned or photographed bill. "Uploaded to the shared cloud folder above." Only shown to board members and administrators when cloud storage and an incoming invoices folder are set up. |
| **Save** | Saves the invoice. You see "Saved.". |
| **Cancel** | Closes the dialog without saving. |

Each position has three fields:

| Field | What it does |
|---|---|
| Category | Optional [bookkeeping category](bookkeeping.md#bookkeeping-categories). "—" means none; the position then shows as "Uncategorized". |
| **Description (what was purchased)** | Optional free text, e.g. "Lawn mower service". Several positions can share a category but describe different purchases. |
| Amount | The position's amount, e.g. `249,90`. A position without a valid amount is left out. |

!!! warning "Check before saving"
    Sender, date, positions and amounts can't be edited after saving;
    only the linked contact and the payments can be changed later. If
    something is wrong, delete the incoming invoice and record it again.

If the attachment can't be uploaded, the invoice is still saved and the
error from the cloud storage is shown at the top of the list. The
attachment's file name in the cloud folder starts with an internal
number, so two bills with the same file name never overwrite each other.
The folder itself is set under **Integrations** →
**Incoming invoices folder**, see
[Integrations](../../administration/integrations.md).

## Incoming invoice

![Incoming invoice](../../assets/screenshots/finances/incoming-invoice-detail.png)

Opens when you click a sender in the list. The title is "Incoming
invoice — *sender*".

**Top bar**

| Button | What it does |
|---|---|
| **Download attachment** | Downloads the attached bill from the cloud folder. Only shown when there is an attachment and you may use cloud storage. |
| **Back to incoming invoices** | Back to the list. |

**Invoice** card

| Field | What it shows |
|---|---|
| **Sender** | The sender as entered. |
| **Contact** | The linked external contact, as a link to the contact if you may see contacts ("deleted" if the contact has since been deleted). With write permission a drop-down and **Save** let you link a different contact or none. Changing the contact does **not** change the **Sender** text. |
| **Invoice no.** | The supplier's invoice number. |
| **Date** | The invoice date. |
| **Note** | The note. |
| **Amount** | The invoice total. |
| **Payment status** | **Open**, **Partially paid** or **Paid**. |

**Positions** card: each position with its category ("code · title",
or "Uncategorized"), description and amount, and the **Subtotal**.

**Payments** card: every payment recorded for this bill with date,
amount, account and note. A bin icon deletes a payment (needs delete
permission, asks "Delete this payment?"). If there are none: "No
payments recorded yet."

To record a payment (write permission):

| Field | What it does |
|---|---|
| **Amount** | Required. What the club paid, as a positive number. Partial payments are fine. |
| **Paid on** | Required, pre-filled with today. This date decides in which year the expense counts in the accounting statement. |
| **Note** | Optional. |
| **Account** | Optional. The [account](bank-accounts.md#accounts) the money left from; only active accounts are offered. The payment then appears, as a negative amount, in that account's bookings. |
| **Add payment** | Saves the payment. |

The status becomes **Paid** once the payments reach the invoice total.
Incoming invoices have no reminders or fees.

!!! tip "Paying from the bank statement"
    Instead of entering the payment here, you can import your bank
    statement on the account's bookings page: a negative booking with
    the same amount as an open incoming invoice is offered as a match
    and recorded as its payment. See
    [Bank accounts and bookings](bank-accounts.md#possible-matching-invoices).

!!! note "Only paid bills count"
    The accounting statement and the budget plan count an expense on the
    day it was paid. An incoming invoice without a payment doesn't show
    up there at all.

## Related

- [External contacts](../external-contacts.md) -- a supplier's contact
  page lists the incoming invoices linked to it.
- [Purchase requests](../purchase-requests.md) -- approving a purchase
  happens there; the resulting bill is recorded here by hand.
  <!-- TODO(verify): there is no link between a purchase request and an incoming invoice in the code; confirm this is the intended workflow. -->
- [Categories, budget and statement](bookkeeping.md)
- [Integrations](../../administration/integrations.md) -- the shared
  cloud folder for attachments.
