# Running the annual invoices

Once a year the club bills every parcel: lease, water, electricity,
insurance, missed work hours, maybe a membership fee or a one-off
[levy](../glossary.md#general-levy). In Parcella this is an
[invoice run](../glossary.md#invoice-run): you define the line items
once, check a preview of every single invoice, finalize to assign
invoice numbers, and then send them out -- by email, on paper, or into
each parcel's cloud folder. Afterwards you record payments and send
[reminders](../glossary.md#dunning).

!!! info "Who can do this"
    Everything here needs **write** permission on **Finances**. The
    **Finances** module is **off** on a new installation; switch it on
    under **Administration → Settings → Feature areas** (see
    [Turning modules on and off](../administration/modules.md)).

!!! warning "Finalizing can't be undone"
    Until you finalize, nothing is saved as an invoice and nothing is
    sent -- change the items as often as you like. Finalizing assigns
    permanent invoice numbers and locks the run. Download a backup
    first (**Administration → Users → Download backup**).

## 1. Check the finance settings (once)

1. Open **Administration → Settings** and find **Finance settings**.
2. Fill in the club's bank details: **Bank name**, **IBAN**, **BIC**,
   **Account holder**. They appear in the footer of every invoice.
3. Check the **Invoice number format**. The default is the year and a
   running number; you can use your own, for example `R-{year}-{number}`.
   `{number}` is required.
4. Leave **Next invoice number (override)** empty, unless the first
   invoice run in Parcella must continue a numbering you used before.
   It's used once and then cleared.
5. Make sure **Email (SMTP)** is set up if you want to email invoices.
6. Click **Save settings**.

## 2. Prepare the item catalog (once, then reuse)

The item catalog holds the line items you bill every year, so you don't
have to define them again for each run.

1. Open **Finances → Overview** and click **Item catalog**.
2. Under **New item template**, fill in **Order** (position on the
   invoice), **Name**, **Description**, the **Pricing mode**, the
   **Unit price** and optionally a **Category**.
3. Choose who it applies to (see below) and click the **+** button.

| Pricing mode | What it bills |
|---|---|
| **Fixed amount per parcel** | The unit price once per parcel -- e.g. the lease. |
| **Fixed amount per person** | The unit price once per *member* -- e.g. a membership fee, also for members without a parcel. |
| **Per leased m²** | Unit price × the parcel's area. |
| **Share of the communal area lease** | The communal area (Area B), split evenly over the billed parcels, × unit price. |
| **Public burdens (own area + communal area share)** | The parcel's own area plus its share of the communal area, × unit price. |
| **General levy (split evenly across all parcels)** | The unit price is a *total* amount that is split evenly over all billed parcels. |
| **Water usage (from module)** | The parcel's water consumption × the water price for the year. |
| **Electricity usage (from module)** | The parcel's electricity consumption × the electricity price for the year. |
| **Insurance cost (from module)** | The parcel's insurance, one line per insurance type. |
| **Work-hours shortfall (from module)** | Missing [mandatory hours](../glossary.md#mandatory-hours) × the hourly rate. |

**Who an item applies to.** Parcel-based items have **Applies to every
parcel**; untick it to pick individual **Parcels**. **Fixed amount per
person** has **Applies to every member** and a **Members** picker
instead. The four "from module" items choose their parcels by
themselves -- **Automatic (...)** is shown instead of a picker -- and
their unit price is **Computed automatically**.

More: [Invoice runs](../modules/finances/invoice-runs.md).

## 3. Check the numbers the automatic items use

The "from module" items take their numbers from other modules. Check
them for the year you are billing **before** you finalize.

**Water and electricity**

1. Open **Water → Configuration** and check that a price (**Price per
   m³**)
   exists for the year (in **Price history**). If not, enter **Year**
   and price under **New/update price** and click **Save**. Do the same
   under **Electricity → Configuration**.
2. Open **Water → Overview**. If it says some metering points still have
   no reading for the year, collect them first -- see [Collecting meter
   readings](meter-readings.md). A parcel without a reading for the year
   gets no water line at all.
3. Open **Water → Evaluation** for the year and look for parcels with
   **no reading** or implausible consumption.

**Work hours**

1. Open **Work Sessions → Sessions & Overview** and check the year's
   **Hours Configuration**: required hours and **Hourly Rate**.
2. Open **Work Sessions → Annual Evaluation** for the year. Check the
   **Open** and **Owed** columns -- that's what will be billed.
   Missing attendance, sponsorships or exemptions? Fix them now (see
   [Organising a work session](work-session.md)).

**Insurance**

1. Open **Insurance → Configuration** and **Insurance → Parcels** and
   check the year's prices and each parcel's insurance.

!!! tip "Who gets the invoice"
    A parcel invoice goes to the parcel's current tenants marked **Use
    as invoice address**. Parcels without such a tenant get no invoice.
    Check this on the parcel pages before you finalize -- especially
    after a handover.

## 4. Create the invoice run

1. Open **Finances → Outgoing Invoices** (the page is called **Annual
   invoices**).
2. Click **New invoice run**.
3. Enter the **Year** being billed, a **Subject** (e.g. "Annual invoice
   2026"), the **Issued date** and the **Due date**.
4. Optionally write a **Footer text**. It may contain
   `{invoice_number}`, `{parcel_number}`, `{invoice_address}` and
   `{due_date}`, which are filled in per invoice.
5. Click **Create**.

The run is a **Draft**. Open it with **Open**.

## 5. Add the line items

1. On the run's page, under **Add from item catalog**, tick the
   catalog items for this year and click **Add selected items**.
2. For anything that's only billed this year, fill in **Add item** at
   the bottom, the same way as in the catalog.
3. Check the **Item definitions** table: order, prices, who each item
   applies to. You can still edit or delete items while the run is a
   draft.

## 6. Preview

1. Click **Preview** at the top of the run's page.
2. The page says how many invoices would be generated and lists them
   under **Computed invoices**, with recipient and subtotal.
3. Open a few with **PDF** and check them: address, line items,
   amounts, footer.
4. To fix something, go **Back to invoice run**, change the items, and
   preview again. Nothing has been saved or sent yet.

If it says *"No invoices would be generated"*, check the items' parcel
scope and the tenants' **Use as invoice address** flag.

## 7. Finalize

1. On the preview page, click **Finalize & assign invoice numbers** and
   confirm.
2. Parcella creates the invoices with permanent numbers. The run's page
   now says it is finalized and lists the **Invoices**.

Recipient names and addresses are stored on each invoice as they are at
this moment. Later address changes don't rewrite finalized invoices.

## 8. Send the invoices

1. On the finalized run's page, find the **Delivery** card.
2. Click **Send emails & upload to cloud**.
    - Invoices are emailed (PDF attached) to invoice recipients who
      have **May receive information by email** and an email address.
    - If the parcel has a documents folder in cloud storage, the
      invoice is also uploaded there.
    - Clicking again only sends what hasn't been sent yet.
3. Click **Download print bundle**. It contains a letter for every
   tenant who doesn't get invoices by email, as one PDF to print and
   post: one letter per address, naming the people there without email.
   That includes someone whose housemate got the email.
   They are then marked as included in a print bundle.

The **Delivery** column shows per invoice whether it was **Emailed**,
**Included in a print bundle** or **Uploaded to cloud storage**. To send
a single invoice again, open it and click **Resend email**.

More: [Invoices, payments and reminders](../modules/finances/invoices.md).

## 9. Record payments

**By hand**

1. Open the run (or **All invoices** on **Annual invoices** to search
   across runs by invoice number, recipient or amount).
2. Click **Payment** on the invoice's row.
3. Enter the **Amount**, **Paid on**, optionally a **Note** and the
   **Account** it arrived on, and click **Add payment**.

Partial payments are fine; the status changes from **Open** to
**Partially paid** to **Paid** by itself.

**From the bank statement**

1. Once: open **Finances → Overview → Accounts** and add your bank
   account under **New account**.
2. Click **Bookings** next to the account, then **Import CSV**.
3. Upload the statement exported from your online banking. On **Map CSV
   columns**, map at least **Date** and **Amount**; **Description**,
   **Sender / recipient** and **IBAN** help with matching.
4. On **Match rows to invoices**, Parcella suggests open invoices with
   the same amount for each incoming payment. Pick the right one to
   record it as a payment on that invoice, or choose **Record as a
   generic booking**.
5. Click **Import CSV** at the bottom of the page to create the
   bookings and payments.

More: [Bank accounts and bookings](../modules/finances/bank-accounts.md).

## 10. Send reminders

1. After the due date, open **Finances → Reminders**. **Overdue
   invoices** lists every unpaid invoice past its due date, with how
   long it's overdue and how many reminders were sent.
2. Click **Open** next to an invoice.
3. Optionally enter a **Fee (optional)** and a **Message (optional)**.
4. Click **Send reminder**.

Parcella creates the next reminder as a PDF (**Reminder #1**, **#2**,
…), adds the fee to the amount owed, and emails it if the member
agreed to email; otherwise it's marked **For printing/postal** for you
to print and post. There are no fixed dunning levels -- you decide when
to send the next one.

## Related

- [Finances](../modules/finances/index.md)
- [Invoice runs](../modules/finances/invoice-runs.md)
- [Invoices, payments and reminders](../modules/finances/invoices.md)
- [Bank accounts and bookings](../modules/finances/bank-accounts.md)
- [Categories, budget and statement](../modules/finances/bookkeeping.md)
- [Water and electricity](../modules/metering.md)
- [Work hours](../modules/work-hours.md)
- [Insurance](../modules/insurance.md)
- [Collecting meter readings](meter-readings.md)
