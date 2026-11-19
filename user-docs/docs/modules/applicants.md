# Applicants

The applicant list is your club's waiting list for free garden plots.
Applications from the form on your website arrive here on their own;
you can also enter applications that came by phone or on paper. You
track whom you have contacted and offered a plot, and when a plot
becomes free you hand it over -- the applicant becomes a member and the
new tenant in one step.

Applicants are kept apart from the member list on purpose. Most
applicants never get a plot, so their data mustn't end up in member
counts, invoices, work hours or mailings.

!!! info "Who can use this"
    The **Applicants** module is on by default. It can be switched off
    under [Turning modules on and off](../administration/modules.md).

    - **Seeing** the list and the applications needs *read* permission
      on **Applicants**.
    - **Adding** an applicant, **editing** contact data, status and
      board note, and **contacting** a new applicant needs *write*
      permission.
    - **Deleting** an applicant for good needs *delete* permission.
    - **Assign a parcel** needs *write* permission on both
      **Applicants** and **Members & Parcels**.

    Board members and administrators have all of these. A group can
    grant them to others, e.g. whoever handles plot allocation (see
    [Groups](../administration/groups.md)).

    Applications from your website only arrive while the separate
    **Public applicant-form API** module is switched on. It's off by
    default, because it lets people outside the club write into
    Parcella. See [Applications from your website](#applications-from-your-website).

## Where you notice new applications

- The **Applicants** entry in the main menu shows a red number: the
  applications nobody has looked at yet (status **New**). It disappears
  once every new application has been moved on to another status.
- The [dashboard](../getting-started/dashboard.md) has a **New
  applications** card with the same number, "not looked at yet". It
  opens the list filtered to new applications.

Parcella doesn't email the board about a new application -- the
number in the menu and on the dashboard is the signal.

## Statuses

Every application goes through these statuses. You set them on the
[application page](#application-page); only **Closed (parcel assigned)**
is set by Parcella itself.

| Status | Meaning |
|---|---|
| **New** | Just arrived; nobody has looked at it yet. |
| **Contacted** | The board has been in touch -- e.g. sent the first email. The applicant is on the waiting list. |
| **Plot offered** | A plot has been offered. |
| **Accepted** | The applicant wants the offered plot; the handover is still being arranged. |
| **Rejected** | The club declined, or the applicant wants no further offers. |
| **Closed (parcel assigned)** | The applicant got a parcel through **Assign a parcel**. |

**New**, **Contacted**, **Plot offered** and **Accepted** count as
*open*. If an applicant turns down an offer but wants to stay on the
waiting list, set them back to **Contacted**. If they want no further
offers, set **Rejected**.

## Applicant list

![Applicant list](../assets/screenshots/applicants/list.png)

Open **Applicants** in the main menu. The list shows the applications,
most recent application date first.

### Filter and search

| Field / button | What it does |
|---|---|
| **New** | Only applications with status **New**. Only shown while there are new applications -- and then the list opens with this filter. |
| **Open** | Applications that are **New**, **Contacted**, **Plot offered** or **Accepted**. The list opens with this filter when there are no new applications. |
| **Closed** | Applications that are **Closed (parcel assigned)** or **Rejected**. |
| **All** | Every application. |
| **Name, email, phone, message, notes…** | Searches first and last name, email address, phone number, the applicant's message and the board note. Combines with the filter buttons. Because the board note is searched, a ticket number you noted there finds the applicant. |
| **Search** | Applies the search. |
| **Reset** | Clears the search, keeps the filter button. |

### Columns

| Column | What it shows |
|---|---|
| Checkbox | Selects the applicant for **Write to the selected applicants** (see below). |
| **Name** | First and last name, or the email address if no name was given. Click it to open the application. |
| **Email** | Click to write from your own mail program. |
| **Phone** | |
| **Applied** | The application date. It decides the order of the waiting list. |
| **Status** | See [Statuses](#statuses). |
| Eye button | Opens the application. |

Two kinds of badges can appear next to the name:

- **2×**, **3×** … -- this email address has applied more than once.
  Parcella doesn't merge repeated applications; each one stays a
  separate entry, so no message gets lost. You decide what to do with
  them. The application page lists the others.
- **Red flag** -- the applicant's name, email address or phone number
  matches an [external contact](external-contacts.md) that carries
  your club's red-flag tag. Hover over the badge to see which contact
  and which details match. There are no red flags while the External
  contacts module is off.

### Writing to selected applicants

While the **Announcements** module is on, board members and
administrators see a checkbox on every row.

| Button | What it does |
|---|---|
| **Select all** | Ticks every applicant the current filter and search show. |
| **Select none** | Clears all ticks. |
| ***N* selected** | Counts the ticked applicants. |
| **Write to the selected applicants** | Starts a new [announcement](announcements.md) to the ticked applicants. It goes out by email only, once per address -- someone who applied twice gets one email. Disabled until you tick someone. |

### Adding an applicant by hand

**New applicant** (top right, needs write permission) opens the
[New applicant](#new-applicant) form.

## New applicant

![New applicant form](../assets/screenshots/applicants/form-new.png)

For applications that didn't come through the website -- by phone, by
letter, or from an old paper waiting list. Applications from the
website form appear in the list on their own.

| Field | What it does |
|---|---|
| **Email address** \* | Required -- the only required field. Must be a valid email address, otherwise "Please enter a valid email address." |
| **First name** / **Last name** | Optional here, but needed before you can assign a parcel. |
| **Phone** | |
| **Applied** | The application date. "Leave blank for today. Change it to enter an older application, e.g. from a paper waiting list -- it decides the order." A date in the future is refused. |
| **Applicant's message** | What the applicant wrote or told you. |
| **Board note** | "Internal -- never shown to the applicant." |

Click **Save**. The application starts with status **New**, its source
is **Entered by hand** (with your name), and it has no privacy consent
date -- that's only recorded for applications from the website. **Back**
returns to the list without saving.

## Application page

![Application page](../assets/screenshots/applicants/detail.png)

Click an applicant in the list to open their application.

If the applicant matches a red-flagged external contact, a red **Red
flag** box at the top names the contact and the matching details (name,
email, phone). Users who may see external contacts can click through to
the contact.

### Application

The left-hand card holds everything you can edit.

| Field | What it does |
|---|---|
| **Status** | See [Statuses](#statuses). Every change is recorded in the **Status history**. |
| **Email address** \*, **First name**, **Last name**, **Phone** | The applicant's contact data. |
| **Applied** | The application date. Change it to move an application to its right place in the queue, e.g. when you enter an old paper application. A change is recorded in the status history, because it moves the applicant up or down. Future dates are refused. |
| **Applicant's message** | The text the applicant sent. |
| **Board note** | Internal notes, never shown to the applicant -- e.g. "called on 3 May, prefers a small plot". |

Click **Save** to store your changes. Without write permission you see
the data, but can't save. Changes to contact data and the board note
aren't recorded in the history.

### Buttons at the top

| Button | What it does |
|---|---|
| **Back** | Returns to the applicant list. |
| **Delete** | Deletes the application for good after you confirm "Delete this applicant for good? This can't be undone." Its status history goes with it. Needs delete permission. |

!!! info "Why applicants can be deleted for good"
    Almost everything else in Parcella keeps its history. Applicants
    are the exception: their data is held only for the application, so
    you must be able to remove it completely -- when someone asks you
    to, or once the application is over. Your club can also have old
    applications deleted automatically; see
    [Automatic deletion](#automatic-deletion).

### Contact applicant

Only shown on a **New** application, to users with write permission.
It's the first step of the workflow: a thank-you email that confirms
the applicant is on the waiting list.

| Field / button | What it does |
|---|---|
| **To:** | The applicant's email address. |
| **Subject:** | "Thank you for registering to our waiting list!" (in the language you use Parcella in). |
| Message | The email's text, ready to edit. The applicant's name and the club's name are already filled in. |
| **Send** | After you confirm, emails the text to the applicant and sets the status to **Contacted**. |

After sending, a green notice says "The email was sent and the status
set to "Contacted"." The box then disappears, because the application
is no longer new.

If the email can't be sent, nothing changes: the status stays **New**,
your edited text stays in the box, and you see "The email could not be
sent -- please check the SMTP settings." Fix the mail settings and try
again.

The starting text comes from **Text of the email to new applicants**
under [Club settings](../administration/settings.md) → **Applicants**.
If that's empty, Parcella uses its built-in text in the language you
use Parcella in. Applicants have no language setting of their own, so
if your club writes its own text, write it in the language your
applicants speak.

!!! note
    Parcella doesn't keep a copy of the email. Only the status change to
    **Contacted** shows that it went out.

### Assign a parcel

Only shown on an open application, to users with write permission on
both **Applicants** and **Members & Parcels**. **Assign a parcel** hands
a terminated parcel over to the applicant -- see
[Assign a parcel](#assign-a-parcel) below.

### Details

| Line | What it shows |
|---|---|
| **Applied** | The application date. |
| **Source** | **Website form**, or **Entered by hand** with the name of the user who entered it. |
| **Privacy consent (applicant)** | When the applicant ticked the data-protection box on the website form. Empty for applications entered by hand. This is the applicant's consent -- not an approval by the board. |
| **Status changed** | When the status last changed. |

All dates are shown without a time of day.

### Other applications from this address

Only shown if the same email address has applied more than once. Lists
the other applications with date and status; click a date to open one.

### Processes

If the [Processes](processes.md) module is on and you may see
processes, a **Processes** card lists the processes about this
applicant. **Start a process** starts a new one.

### Status history

Every status change and every change of the application date, with
date, time and the user who made it -- newest first. Changes made by
Parcella itself (a handover) appear here too.

## Assign a parcel

![Assign a parcel](../assets/screenshots/applicants/assign-parcel.png)

When a parcel becomes free, this page hands it to one or more
applicants in a single step. Open it with **Assign a parcel** on an
application.

!!! info "Before you start"
    - The parcel must have the status **terminated**. Set it in the
      [parcel form](parcels.md#new-parcel-and-edit-parcel) first. If no
      parcel is terminated, the page tells you so.
    - Every applicant who takes over the parcel needs a first and a last
      name on their application.

### Step 1: parcel and handover date

| Field | What it does |
|---|---|
| **Terminated parcel** | The parcel to hand over. Only terminated parcels are offered, each with its current tenants' names. |
| **Handover date** | The day the new tenants take over. Today by default. It may lie in the future: the old tenants then stay tenants, members and invoice recipients until that day, and the new tenants show as upcoming on the parcel page. |
| **Further applicants (co-tenants)** | Optional: other open applicants who take over the parcel together with this one, e.g. a couple who applied separately. |
| **Documents folder for the new tenants** | Only for board members and administrators while the **Cloud storage** module is on. The folder that becomes the parcel's documents folder on the handover date. **Browse cloud storage** lets you click through your storage and choose **Use this folder**. Create and share the folder in your cloud storage yourself. Optional -- you can also set it on the parcel page later. |
| **Preview** | Shows what will happen. Nothing is changed yet. |

### Step 2: check the preview

The preview card, **Handover of parcel *X* on *date***, lists exactly
what will happen:

- **Old tenants** -- each current tenant's tenancy ends on the
  handover date. If they hold no other parcel, their membership ends
  the day before ("membership ends after *date*"). If they still hold
  another parcel, they keep their membership; the preview names that
  parcel.
- **New tenants and invoice recipients** -- each applicant either
  "becomes a new member" (name, email and phone are taken from the
  application) or, if an active member already has the applicant's
  email address, is linked to that member ("already a member").
- **Documents folder** -- which folder is retired on the handover date
  and which one takes over. If you can't manage folders yourself, a
  note says that someone with full access sets the new folder later.

If something is wrong -- the parcel isn't terminated, an applicant's
application is already closed or has no name -- an error message
explains it and nothing happens.

Click **Hand over parcel** and confirm. Parcella then, in one go:

1. ends the old tenancies on the handover date (they stay in the
   parcel's history as former tenants),
2. ends the membership of old tenants who hold no other parcel,
3. creates the new members -- their **Member since** is the handover
   date -- and makes them tenants and invoice recipients of the
   parcel,
4. sets the parcel back to **active**,
5. sets the applications to **Closed (parcel assigned)**.

You land on the parcel page afterwards.

<!-- TODO(verify): the preview's closing sentence says the applications are set to "Accepted", but the handover actually sets them to "Closed (parcel assigned)". The UI text looks outdated. -->

!!! tip "Complete the new member afterwards"
    Only name, email address and phone number are copied from the
    application. Open the new member and add the address, IBAN and
    whether they may receive information by email -- that box starts
    unticked for members created this way.

## Applications from your website

Most applications come through a form on your club's website. Once
it's set up, every submitted form appears in the applicant list as a
**New** application with the source **Website form** and the date the
applicant gave their privacy consent.

What the form asks for: email address (required), first and last name,
phone, a message, and a privacy-consent checkbox that must be ticked.
Parcella protects the form against spam: hidden fields that only bots
fill in, an optional captcha, and a limit of a few submissions per hour
from the same visitor.

To set it up:

1. Switch on the **Public applicant-form API** module under
   [Turning modules on and off](../administration/modules.md).
2. Under [Integrations](../administration/integrations.md), enter your
   website's address so Parcella accepts forms from it. The page also
   lists the addresses the form sends to.
3. Put the form on your website:
    - **WordPress**: install the Parcella Connector plugin and place the
      `[parcella_applicant_form]` shortcode on a page.
    - **Any other website**: a plain HTML form that sends the fields
      above to Parcella. Your web designer finds the details under
      Integrations.

What applicants see is described in [For gardeners](../gardeners/index.md).

!!! note
    Parcella doesn't send the applicant an automatic confirmation.
    Use [Contact applicant](#contact-applicant) for the first reply.

## Automatic deletion

Under [Club settings](../administration/settings.md) → **Applicants**,
**Delete applications after (months)** lets Parcella delete old
applications for you. Every application whose status hasn't changed
for that many months is deleted for good -- **whatever its status**,
and without notice to anyone. The months count from the last status
change, or from the application date if the status never changed.

Leave the field blank or at 0 (the default) to keep applications until
you delete them by hand. The check runs in the background while people
use Parcella, at most once an hour.

!!! warning
    Automatic deletion also removes open applications that have simply
    been waiting a long time. If your waiting list is long, choose a
    period longer than the usual wait, or move long-waiting applicants'
    status on from time to time.

## Related

- [Parcels](parcels.md) -- terminating a parcel before a handover
- [Members](members.md) -- completing the new member's data
- [Handing over a parcel](../guides/parcel-handover.md)
- [Announcements](announcements.md) -- writing to selected applicants
- [External contacts](external-contacts.md) -- the red-flag tag
- [Integrations](../administration/integrations.md) -- the website form
