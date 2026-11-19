# Handing over a parcel

A tenant gives notice, the parcel is inspected and valued, offered to
the waiting list, and finally a new tenant signs and gets the keys.
This takes weeks or months and involves several board members. This
guide shows what Parcella records along the way and how a
[process](../glossary.md#process) keeps track of the steps it doesn't
record by itself.

## What Parcella does -- and doesn't -- track

| Part of the handover | In Parcella |
|---|---|
| The notice of termination | Parcel status **terminated**, with the date logged automatically and an optional **Termination note**. |
| Old and new tenants | Ending the old [tenancy](../glossary.md#tenancy) keeps it as history; the new tenancy starts on the handover date. **Assign a parcel** on an application does both in one step. |
| The old tenant's membership | Ends automatically with **Assign a parcel** if they hold no other parcel. |
| Documents folder | The old tenants' cloud folder is retired on the handover date; a new one takes over. |
| Inspection, [valuation](../glossary.md#valuation), offer, viewing, contract, keys | Not built in. Track them with a **process** (step 1). |
| [Deposit](../glossary.md#deposit) | No deposit feature. Note amount and date in the process; record the money in **Finances** if you use it (step 7). |
| Final meter readings | Parcella keeps **one reading per meter per year**. Note handover readings in the process (step 6). |
| Price between old and new tenant | **Not tracked, on purpose.** What the new tenant pays the old one for the garden house and plants is a private matter between the two. Parcella has no field for it -- don't add one to your process template either. |

!!! info "Who can do this"
    Parcel and tenancy changes need **write** on **Members & Parcels**;
    **Assign a parcel** also needs **write** on **Applicants**. Process
    templates need full access (board or administrator); working on a
    process needs **write** on **Processes**.

## 1. Prepare a handover process template (once)

The **Processes** module comes with an example **Plot handover**
template. Start from it and adapt it to your club's sequence.

1. Open **Processes → Templates** (the page is called **Process
   templates**).
2. Under **Start from an example**, click **Use** next to **Plot
   handover**. Parcella creates an ordinary template you can change
   freely. It is about a **Plot**, so each process belongs to one
   parcel and shows up on that parcel's page.
3. The example has six stages: **Inspection**, **Valuation**,
   **Listing**, **New tenant**, **Contract and deposit** and
   **Closing**. To match the usual sequence below, add and rename
   stages in the editor (type a **Stage name** and click **Add**; drag
   stages to reorder; add fields by typing a label and pressing Enter):

| Stage | Example fields | Field type |
|---|---|---|
| Notice of termination *(new, first)* | Notice received on (required) · Notice letter | Date · Files (PDF, photos) |
| **Inspection** | **Date of the inspection** · **Defects found** · **Photos of the defects** · **All defects resolved** | from the example |
| **Valuation** | **Appraiser** · **Date of the valuation** · **Valuation report** | from the example |
| **Listing** → rename to "Offer to the waiting list" | **Listing text** · **Published on** | from the example |
| Viewing *(new)* | Viewing date · Interested applicants (notes) | Date · Long text |
| **New tenant** | **New tenant** (an applicant) · **Contact established** · **Documents sent** | from the example |
| **Contract and deposit** | **Purchase agreement confirmed** · **Deposit** · **Deposit received on** | from the example |
| **Closing** → split into "Signing" and "Final checklist" | Signing: **Signed by the new tenant**, **Countersigned by the board**. Final checklist: **Keys handed over**, **Meters read**, **Handover protocol** | from the example |

4. In the "Final checklist" stage, add **Number** fields for the handover
   meter readings, e.g. "Water meter reading at handover" and
   "Electricity meter reading at handover" (see step 6).

Mark a field **Required** if the process must not move on without it.
Changes to a template only affect processes started afterwards.

!!! tip
    **Purchase agreement confirmed** is just a checkbox: the board
    confirms that old and new tenant agreed. The price itself stays
    between the two of them.

More: [Processes](../modules/processes.md).

## 2. Record the notice

When the tenant's notice of termination arrives:

1. Open the parcel under **Parcels** and click **Edit**.
2. Set **Status** to **terminated**. Parcella logs the time of the
   status change; the parcel page then shows **Terminated on**.
3. Optionally add a **Termination note** (reason, notice date,
   remarks).
4. Click **Save changes**.

The tenant stays a current tenant -- and keeps receiving the parcel's
invoices -- until the tenancy actually ends. Don't end the tenancy now;
**Assign a parcel** does that on the handover date (step 5).

## 3. Start the process

1. On the parcel's page, in the **Processes** card, click **Start a
   process**.
2. Choose your handover **Template**. Optionally give the process a
   **Title**.
3. Click **Start**.
4. Fill in the first stage's fields and click **Save**. When the stage
   is complete, click **Done -- next stage**.

The process appears on the parcel page with its current stage, and in
**Processes** for everyone working on it. Files you upload (letters,
photos, the valuation report) go into the parcel's cloud folder if one
is set, otherwise into Parcella's own storage.

To go back to an earlier stage, click **Go back**, choose the stage
and give a **Reason**. If the handover falls through, **Abort the
process** with a reason.

## 4. Inspection, valuation, offer, viewing

Work through these stages in the process as they happen. The
[valuation](../glossary.md#valuation) report goes into **Valuation
report**; the text of the offer into **Listing text**.

To find interested people, open **Applicants** with the **Open**
filter -- the list is sorted by application date. Set those you offer
the parcel to **Plot offered**, and the one who takes it to
**Accepted**. With the **Announcements** module on, tick several
applicants and click **Write to the selected applicants** to send the
offer by email.

More: [Applicants](../modules/applicants.md).

## 5. Hand the parcel over to the new tenant

Once the contract is signed -- or with a future date, as soon as it's
fixed:

1. Open the new tenant's application and click **Assign a parcel**.
2. Choose this parcel under **Terminated parcel** and set the
   **Handover date**.
3. Add a partner under **Further applicants (co-tenants)** if they take
   the parcel over together.
4. If you use cloud storage, enter the **Documents folder for the new
   tenants**. The old tenants' folder is retired on the handover date
   either way.
5. Click **Preview**, check the old and new tenants, then click **Hand
   over parcel** and confirm.

On the handover date:

- the old tenancy ends and moves to **Former tenants** on the parcel
  page;
- an old tenant without another parcel leaves the club (**Member
  until** is the day before the handover date);
- the applicants become members, tenants and invoice recipients;
- the parcel is **active** again.

See [Welcoming a new member](new-member.md), steps 5 and 6, for the
details and for completing the new member's record.

### If the new tenant isn't an applicant

For example a family member taking over. Do it by hand:

1. On the parcel page, in **Current tenants**, click the pencil icon
   next to the old tenant (**Edit tenancy**), set **Tenant until** to
   the last day and click **Save changes**. Or, to end it today, click
   the **End tenancy** icon and confirm *"End this tenancy? (history is
   preserved)"*.
2. If the old tenant leaves the club, open their member page, click
   **Edit**, set **Member until** and click **Save changes**. Don't
   delete them -- see the warning below.
3. Assign the new tenant: **Choose member…**, the start date, **Use as
   invoice address**, **Assign**. Create them first under **Members →
   New member** if needed.
4. Edit the parcel and set **Status** back to **active**.

!!! tip "Recording a notice"
    A tenant who has given notice stays the invoice address until they
    leave: set their **Tenant until** in **Edit tenancy** and leave **Use
    as invoice address** ticked. Once that day has passed, the box is
    cleared by itself -- make sure the new tenant is the invoice address
    by then.

!!! warning "End, don't delete"
    Ending a tenancy or a membership keeps the history: who held which
    parcel when, and which hours and invoices belonged to whom. Deleting
    a member removes them from every evaluation, including the work
    hours of years they were a tenant in.

## 6. Final meter readings

Parcella stores one reading per meter and year, and that's the reading
the annual invoice is based on. There is no separate "handover
reading".

- Write the readings on the day of the handover into the process
  (the "Final checklist" stage from step 1) and tick **Meters read**.
- Don't enter them as the year's reading on the metering point unless
  that is really what you want: the annual reading later in the year
  **replaces** it.
- The annual water and electricity invoice for the parcel goes to
  whoever is the invoice recipient when the [invoice
  run](../glossary.md#invoice-run) is finalized -- after a handover, the
  new tenant -- for the whole year's consumption. How old and new
  tenant split that is up to them and your club's rules; settle it
  outside Parcella, using the readings in the process.

If a meter is exchanged at the handover, see [Collecting meter
readings](meter-readings.md#a-meter-is-replaced).

## 7. Deposit and money

Parcella has no deposit field on the parcel or the member. Use the
process for the record: **Deposit** (amount) and **Deposit received
on** in the **Contract and deposit** stage.

If you use the **Finances** module, record the money itself too:

- **Received deposit**: open **Finances → Overview → Accounts**, click
  **Bookings** next to the account the money arrived on, and use **Add
  booking** (or **Import CSV** with your bank statement).
- **Returning the old tenant's deposit**: the same, as a negative
  amount.

<!-- TODO(verify): confirm with the treasurer whether a deposit should rather be billed as a one-off invoice run (a "Fixed amount per parcel" item scoped to this parcel) so it gets an invoice number. -->

**Work hours.** A tenant who leaves during the year still owes that
year's [mandatory hours](../glossary.md#mandatory-hours). With billing
per parcel, their hours count together with the new tenant's, and a
shortfall is billed to the parcel's invoice recipient at the time of
the invoice run -- the new tenant. If that
isn't what your club wants, settle it by hand. See [Running the annual
invoices](annual-invoicing.md).

**Open invoices** of the old tenant stay as they are; the invoice
number, recipient and address are kept on each invoice, so you can
still collect and remind.

## 8. Close the process

When the last stage is done, click **Complete the process**. A
completed process is read-only and stays on the parcel page, with its
full **History**.

## Related

- [Parcels](../modules/parcels.md)
- [Applicants](../modules/applicants.md)
- [Members](../modules/members.md)
- [Processes](../modules/processes.md)
- [Water and electricity](../modules/metering.md)
- [Bank accounts and bookings](../modules/finances/bank-accounts.md)
- [Welcoming a new member](new-member.md)
- Glossary: [deposit](../glossary.md#deposit),
  [valuation](../glossary.md#valuation),
  [notice of termination](../glossary.md#notice-of-termination),
  [tenancy](../glossary.md#tenancy)
