# Organising a work session

Most clubs ask every parcel (or every member) to put in a number of
[mandatory hours](../glossary.md#mandatory-hours) of community work a
year -- hedge cutting, path repairs, the spring clean-up. This guide
takes one [work session](../glossary.md#work-session) from planning to
the year-end evaluation: create it, let members sign up on the club
website, record who actually came, and see who still owes hours.

!!! info "Who can do this"
    Creating sessions and recording attendance needs **write** permission
    on **Work Sessions**; removing a participant or a transfer needs
    **delete**. The module (**Work-hours management**) is on by default.
    Publishing on the website needs an administrator for the one-time
    setup in step 3.

## 1. Set the year's rules (once a year)

1. Open **Work Sessions → Sessions & Overview**. If the year has no
   rules yet, the page says *"No mandatory-hours configuration for … yet."*
   -- click **Create now →** (or **Hours Configuration** at the bottom).
2. Under **Create / Update Year**, enter:
    - **Year**
    - **Total Mandatory Hours** -- the hours owed per year;
    - **Hourly Rate** -- what an hour not worked costs;
    - **Billing Mode** -- **Per Lease / Parcel** (all tenants of a
      parcel work off the hours together) or **Per Member** (each member
      on their own);
    - optionally a **Note**, e.g. the resolution of the general meeting.
3. Click **Save**.

On the same page, the **Sign-up confirmation email** card controls the
email members get after signing up on the website (step 3).

**Exemptions.** Board members, people with health reasons or above an
age limit are often exempt. Set that up under **Sessions & Overview →
Club Roles**: create a role with **Exempt from mandatory hours** and an
**Exemption Reason**, then assign members to it for the year. If one
tenant of a parcel is exempt, the whole parcel is exempt; an exemption
counts for the whole calendar year.

## 2. Create the session

1. Open **Work Sessions → Sessions & Overview** and click **New
   Session**.
2. Fill in:
    - **Title**, e.g. "Spring Cleanup";
    - **Type**: **Standard (planned)** for sessions you announce, or
      **Special (spontaneous)** for unplanned ones -- special sessions
      never appear on the website;
    - **Date**, **From** and **Until**;
    - **Max. Participants** -- leave empty for unlimited;
    - **Registration deadline (days before)** -- website sign-up closes
      this many days before the session (1 = the day before); empty
      means it closes when the session has passed;
    - **Hours per Participant** -- credited to everyone who attends,
      adjustable per person later;
    - **Description** -- tasks, tools, what to bring.
3. Click **Create Session**.

The session is listed under **Work Sessions …** for its year.

## 3. Publish the sign-up on the club website (one-time setup)

Members sign up on the club website with their **plot number** and,
optionally, their name -- no Parcella login needed. The website never
shows which members live on which parcel.

An administrator sets this up once:

1. **Administration → Settings → Feature areas**: tick **Public signup
   API** and click **Save settings**. It's off by default because it
   opens a public form.
2. **Administration → Integrations → Public Signup API**: note the **API
   token** (for a server-side connector) and add your website under
   **Allowed website origins** (e.g. `https://example.org`), then
   **Save origins**. Optionally tick **Require ALTCHA** against spam.
3. On the website, add the sign-up form -- with the Parcella Connector
   plugin for WordPress, or a plain HTML form for any other site. Your
   web person finds the details in the developer documentation.
   <!-- TODO(verify): link to the gardeners/website-form instructions once that page exists. -->

After that, every new **Standard** session shows up on the website by
itself, as long as its date hasn't passed, its registration deadline
hasn't passed and it isn't full.

**What happens on a sign-up.** Parcella looks up the parcel's current
tenants. If the name typed in matches exactly one of them, only that
member is registered. If no name was given or it doesn't match clearly,
**all** current tenants of the parcel are registered, with a note asking
the board to check -- remove whoever didn't actually sign up. Each newly
registered member gets the confirmation email at the address stored in
Parcella (not the one typed into the form).

More: [Integrations](../administration/integrations.md) and [For
gardeners](../gardeners/index.md).

## 4. Keep an eye on sign-ups

- New sign-ups show a counter next to **Work Sessions** in the sidebar
  and on the dashboard.
- Open the session (click it in the list on **Sessions & Overview**).
  New participants carry a **New** badge. Once you've looked at them,
  click **Mark reviewed**.
- Check the **Note** column: website sign-ups carry the visitor's
  remarks and contact details there, and a warning if the whole parcel
  was registered.
- To add someone by hand (sign-up by phone), use **Select member…** at
  the bottom of the participants table, choose **Registered**, and
  click **Add**.

**Tasks (optional).** If you keep a list of jobs under **Work Sessions →
Tasks**, schedule some for this session there. On the session page you
can then assign each to a participant (**Assigned to**) and see its
**Workload** (**Light**, **Moderate**, **Demanding**). **Manage Tasks**
leads to the full list.

## 5. On the day: print the attendee sheet

1. Open the session and click **Attendee sheet**.
2. Print the PDF. It lists every registered participant with parcel,
   name, expected hours, assigned task and a signature line.

Correct the hours on paper as needed; you type them in afterwards. The
sheet doesn't change anything in Parcella.

## 6. Afterwards: record attendance

1. Open the session.
2. For each participant, choose **Attended** or **No Show** in the
   **Status** drop-down. It saves right away.
3. If someone worked more or less than **Hours per Participant**, type
   the actual hours into their **Hours** field and click the ✓ button.
4. People who came without signing up: **Select member…**, status
   **Attended**, their hours, **Add**.
5. Use the search field above the table to find someone by name or plot
   number.

Only **Attended** participations count towards the hours.

## 7. Sponsorships and hours transfers

**[Sponsorships](../glossary.md#sponsorship)** are areas a member looks
after all year (a hedge, the playground) instead of, or in addition to,
coming to sessions.

1. Open **Work Sessions → Sponsorships**.
2. Under **Create Sponsorship / Add Member**, enter the **Area**, the
   **Member** (or leave it **– not yet assigned –** to advertise the
   area first), a **Description**, the **Credited Hours/Year** and
   **Valid From** / **Valid Until**.
3. Click **Save**.

A sponsorship only credits hours once it has a **Valid From** date and
a member. Several members can share an area -- add a row per member
with the same area name; each gets the full credit.

**[Hours transfers](../glossary.md#hours-transfer)**: a member who did
more than required can give hours to someone else.

1. Open **Work Sessions → Hours transfers**.
2. Under **Give hours**, pick **From (gives)**, **To (receives)**, the
   **Hours** and optionally a **Note**.
3. Click **Transfer hours**.

Only the giver's surplus for the year can be given. Members without a
parcel and exempt members can give all their hours.

## 8. The year-end evaluation

1. Open **Work Sessions → Annual Evaluation** and choose the year.
2. Each row is a parcel (or member, depending on the **Billing Mode**)
   with **Required**, **Sessions**, **Sponsorship**, **Transfers**,
   **Total**, **Open** and **Owed**, and a **Status** of **Fulfilled**,
   **Open** or **Exempt**.
3. Click the arrow at the start of a row (**Show work sessions**) to see
   which sessions the hours came from.
4. **CSV Export** downloads the evaluation.

Tenants who left during the year still owe that year's hours; their
row carries a "lease ended …" badge.

To bill the open hours, add a **Work-hours shortfall (from module)**
item to the annual invoice run -- see [Running the annual
invoices](annual-invoicing.md).

## Related

- [Work hours](../modules/work-hours.md)
- [Calendar](../modules/calendar.md)
- [Integrations](../administration/integrations.md)
- [Running the annual invoices](annual-invoicing.md)
- Glossary: [mandatory hours](../glossary.md#mandatory-hours),
  [exemption](../glossary.md#exemption),
  [sponsorship](../glossary.md#sponsorship),
  [hours transfer](../glossary.md#hours-transfer)
