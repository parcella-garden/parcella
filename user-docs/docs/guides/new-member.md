# Welcoming a new member

Someone applies for a garden, gets offered a parcel, says yes -- and
becomes a member and tenant. This guide follows that path through
Parcella, from the application to the welcome.

There are two ways to make someone a member:

- **From an application** (steps 1-6): the person is on your
  [waiting list](../glossary.md#applicant) in **Applicants**.
  **Assign a parcel** then does the member record, the
  [tenancy](../glossary.md#tenancy) and the invoice address in one go.
  This is the usual way.
- **By hand** (step 7): for someone who never went through the waiting
  list, or a parcel that isn't terminated.

!!! info "Who can do this"
    Working with applications needs **write** permission on
    **Applicants**; assigning the parcel also needs **write** on
    **Members & Parcels**. Board members and administrators have both.
    The **Applicants** module is on by default.

## 1. The application comes in

Applications arrive in two ways:

- **From your website**, if the club has the application form there and
  the **Public applicant-form API** is switched on (see
  [Integrations](../administration/integrations.md)). They appear by
  themselves.
- **By hand**, for applications by phone, letter or in person: open
  **Applicants**, click **New applicant**, fill in at least the **Email
  address** (the only required field), plus **First name**, **Last
  name**, **Phone**, **Applicant's message** and a **Board note** if you
  like, and click **Save**.

To enter an old application from a paper waiting list, set **Applied**
to the original date. The application date decides the order of the
waiting list.

New applications show a counter next to **Applicants** in the sidebar
and on the dashboard until someone has moved them on.

!!! tip "Red flag"
    If an applicant's name, email or phone matches an external contact
    carrying your "red flag" tag, the list and the applicant's page show
    a **Red flag** warning. See [Applicants](../modules/applicants.md).

## 2. Get in touch

1. Open **Applicants** and click the new application.
2. In the **Contact applicant** box, check and edit the text of the
   email. The subject is *"Thank you for registering to our waiting
   list!"*.
3. Click **Send** and confirm.

Parcella emails the text to the applicant and sets the status to
**Contacted**. The box is only there while the status is **New**. If
you got in touch another way, just change the status by hand (next
step).

The default text of this email can be changed in **Administration →
Settings → Applicants → Text of the email to new applicants**.

## 3. Track the application's status

As things move on, open the application, pick the new **Status** and
click **Save**:

| Status | Meaning |
|---|---|
| **New** | Just arrived. |
| **Contacted** | You've been in touch; the applicant is on the waiting list. |
| **Plot offered** | You offered a specific parcel. |
| **Accepted** | The applicant wants the parcel; the handover is being arranged. |
| **Rejected** | No further offers. |
| **Closed (parcel assigned)** | Set automatically by **Assign a parcel** (step 5). |

If an applicant turns a parcel down but wants to stay on the list, set
them back to **Contacted**. Every status change is listed under
**Status history** on the application's page.

## 4. Make sure the parcel is terminated

**Assign a parcel** only offers parcels with the status **terminated**
-- the parcel someone has left or is about to leave.

1. Open the parcel under **Parcels** and click **Edit**.
2. Set **Status** to **terminated**, optionally add a **Termination
   note**, and click **Save changes**.

If the outgoing tenant is still in the middle of leaving, see
[Handing over a parcel](parcel-handover.md) -- it covers the whole
handover including the old tenant's side.

## 5. Assign the parcel

1. Open the application and click **Assign a parcel**. (The button is
   there for every open application -- **New**, **Contacted**, **Plot
   offered** or **Accepted**.)
2. Choose the **Terminated parcel**. The list shows each parcel with its
   current tenants.
3. Set the **Handover date** -- the day the new tenant takes over. It
   may lie in the future.
4. Optionally tick **Further applicants (co-tenants)** -- for example a
   partner who applied separately and takes the parcel over together
   with this applicant.
5. Optionally enter the **Documents folder for the new tenants** (only
   shown if you may manage cloud folders).
6. Click **Preview**.
7. Check the **Handover of parcel … on …** box:
    - **Old tenants**: their tenancy ends on the handover date. If they
      don't hold another parcel, their membership ends the day before.
    - **New tenants and invoice recipients**: each applicant either
      **becomes a new member** (name, email and phone are taken from
      the application) or, if an active member already uses the same
      email address, is linked to that existing member.
8. Click **Hand over parcel** and confirm.

What happens in one step:

- The applicants become members, with **Member since** set to the
  handover date.
- They become tenants of the parcel from the handover date, with **Use
  as invoice address** set.
- The old tenants become former tenants -- the history stays on the
  parcel page.
- The parcel's status goes back to **active**.
- The applications are set to **Closed (parcel assigned)**.
  <!-- TODO(verify): the preview text says the applications are set to "Accepted", but the handover actually sets "Closed (parcel assigned)". One of the two should be fixed in the app. -->

With a handover date in the future, the old tenants stay tenants,
members and invoice recipients until that day; the new ones are shown
as upcoming ("from …") on the parcel page and take over on the date.

## 6. Complete the new member's record

The handover copies only name, email and phone. Fill in the rest:

1. Open **Members** and click the new member (or follow the link from
   the parcel page).
2. Click **Edit** and add **Date of birth**, **IBAN**, the address
   (**Street and house number**, **Postal code**, **City**).
3. Tick **May receive information by email** if the member agrees to
   club information by email. Without it, invoices and announcements go
   to the print pile instead of the inbox.
4. Under **Tags**, tick existing tags or type new ones (for example
   "hedge team"), comma-separated.
5. Click **Save changes**.

!!! warning "Email consent is off until you tick it"
    Members created by **Assign a parcel** don't have **May receive
    information by email** set yet. Check this before the next invoice
    run, or their invoice will only be in the print bundle.

You can also add tags directly on the member's page, in the **Tags**
card, with **Add tag**.

## 7. Without an application: create the member by hand

1. Open **Members** and click **New member**.
2. Fill in **First name** and **Last name** (required), the address,
   **Date of birth**, **IBAN**, **Member since**, an **Email address**
   and **Phone number**, **May receive information by email** and any
   **Tags**.
3. Click **Create member**.
4. On the member's page, in **Assigned parcels**, pick the parcel under
   **Choose parcel…**, leave **Use as invoice address** ticked if this
   member should get the parcel's invoices, and click **Assign**.

Alternatively, assign from the parcel's page: **Current tenants →
Choose member… → Assign**, where you can also enter the start date.
To correct the start date later, use the pencil icon next to the
tenant on the parcel page (**Edit tenancy**, field **Tenant since**).

If an old tenant is still on the parcel, end their tenancy first -- see
[Handing over a parcel](parcel-handover.md).

## 8. Welcome the new member

Parcella has no automatic welcome email. Two things help:

**A process for the onboarding.** The **Processes** module comes with
an example template, **Member onboarding**, with three stages:
**Welcome** (**Welcome meeting**, **Statutes and garden rules handed
over**), **Paperwork** (**Signed membership form**, **Direct debit
mandate received**) and **Wrap-up** (**Added to the mailing list**,
**Notes**).

1. Once: open **Processes → Templates**, and under **Start from an
   example** click **Use** next to **Member onboarding**. Adjust the
   stages and fields if you like. (Creating templates needs full
   access.)
2. For each new member: on the member's page, in the **Processes**
   card, click **Start a process**, choose the **Template** and click
   **Start**.
3. Fill in the fields as things get done and click **Done -- next
   stage**. Required fields must be filled before you can move on.

**A personal message.** With the **Announcements** module on, tick the
new member in the **Members** list and click **Write to selected**.

## Related

- [Applicants](../modules/applicants.md)
- [Members](../modules/members.md)
- [Parcels](../modules/parcels.md)
- [Processes](../modules/processes.md)
- [Announcements](../modules/announcements.md)
- [Handing over a parcel](parcel-handover.md)
- Glossary: [applicant](../glossary.md#applicant),
  [tenancy](../glossary.md#tenancy),
  [invoice address](../glossary.md#invoice-address)
