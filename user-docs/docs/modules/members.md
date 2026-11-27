# Members

The member list is the heart of Parcella: everybody who belongs to your
club, with address, bank details, contact data and the parcels they hold.
Invoices, work hours, mailings, the birthday list and the meeting
sign-in sheet all read from here.

!!! info "Who can use this"
    Members is part of the core and is always switched on. It can't be
    turned off.

    - **Everyone who can log in** can look at the member list, the
      member pages, the tag list, the CSV export and the sign-in sheet.
    - **Adding and editing** members, phone numbers, email addresses,
      tags and parcel assignments needs *write* permission on
      **Members & Parcels**.
    - **Deleting** a member, a phone number, an email address or a tag
      needs *delete* permission on **Members & Parcels**.

    Board members and administrators have all of these. Anyone else gets
    write or delete through a group (see
    [Roles, groups and permissions](../getting-started/roles-and-permissions.md)).

## Member list

![Member list](../assets/screenshots/members/list.png)

Open **Members** in the main menu. The list shows the active members,
sorted by last name and then first name. The footer shows how many
members are in the list right now.

A long list is split into pages of 100 members. Below the table,
**Previous** and **Next** move between pages, "Page 2 of 17" says where
you are, and "Showing 101–200 of 1612" which members you see. The search
and filters stay set while you page through. Coming back from a member
page with **Back** takes you to the page that member is on.

### Buttons at the top

| Button | What it does |
|---|---|
| **CSV Import** | Opens the import dialog for a CSV file (see [Importing members from a CSV file](#importing-members-from-a-csv-file)). Needs write permission. |
| **CSV Export** | Downloads the members *currently shown* as a CSV file. Search, checkboxes and tag filter all apply (see [CSV export](#csv-export)). |
| **Write to these *N* members** | Starts a new announcement to exactly the members in the filtered list. Only shown once you have searched or filtered, while the **Announcements** module is on, and only to board members and administrators. To write to everyone, start the announcement from [Announcements](announcements.md) instead. |
| **Manage tags** | Opens the [Member tags](#member-tags) page. |
| **Sign-in sheet** | Opens the [Meeting sign-in sheet](#meeting-sign-in-sheet). |
| **New member** | Opens an empty [member form](#new-member-and-edit-member). Needs write permission. |

### Search and filters

| Field / button | What it does |
|---|---|
| Search box | Finds members by first or last name, street, postal code, city, IBAN, notes, email address, phone number and parcel number. A parcel number only finds the parcel's *current* tenants -- unless **Show inactive only** is ticked, then it also finds former tenants. Because notes are searched too, a ticket number you noted on a member finds that member. |
| **Show inactive only** | Shows *only* members who are not active: their **Member until** date has passed, or their **Member since** date is still in the future. Use it to look up former or deceased members. |
| **Confirmed active only** | Shows only active members who have a **Member since** date. Members without a start date (shown as *pending*) are left out. |
| **Email info = yes only** | Shows only members who ticked **May receive information by email**. |
| Tag dropdown (**All tags**) | Shows only members with the chosen tag. The dropdown appears once at least one tag exists. You can filter by one tag at a time. |
| **Search** | Applies the search text. The checkboxes and the tag dropdown apply as soon as you change them. |
| **Reset** | Clears every filter. Only shown while a filter is active. |

When **Show inactive only** is ticked, it wins over **Confirmed active
only**. A blue notice above the table reminds you which of the two
filters is on.

Your filter stays with you: if you open a member from a filtered list,
the **Previous** and **Next** buttons on the member page walk through
the same filtered list, and **Back** returns you to it.

### Columns

| Column | What it shows |
|---|---|
| Checkbox | Selects the member for **Export selected** or **Write to selected** (see below). |
| **Name** | Last name, first name -- click it to open the member. The member's tags appear as small grey labels next to the name; click a label to filter the list by that tag. |
| **Member since** | The start of the membership, or "–" if none is recorded. |
| **Parcels** | The plot numbers assigned to the member. <!-- TODO(verify): the list shows every parcel assignment of the member, including tenancies that have already ended -- confirm whether former parcels are meant to appear here. --> |
| **Status** | **active**, **inactive** or **pending** (see below). |
| Eye button | Opens the member page, same as clicking the name. |

The status badge means:

- **active** -- the membership has started and hasn't ended.
- **pending** -- no **Member since** date is recorded yet. A pending
  member still counts as active everywhere else (invoices, meeting
  sign-in sheet, dashboard counts); the badge only tells you that the
  start date hasn't been confirmed.
- **inactive** -- the membership has ended, or hasn't started yet. If
  there's a **Member until** date, the badge shows "since" that date.

### Picking members by hand

Every row has a checkbox, so you can pick a few members out of the list
-- for example, filter for everyone who allows email information, then
tick 12 of them.

| Button | What it does |
|---|---|
| **Select all** | Ticks every member on the current page. |
| **Select all *N* matching the filter** | Only shown when the list has more than one page, after you click **Select all**. Selects every member the filter finds, on all pages. The counter then says "All *N* selected". |
| **Select none** | Clears all ticks. |
| ***N* selected** | Counts the ticked members. |
| **Export selected** | Downloads a CSV file with only the ticked members. Disabled until you tick someone. |
| **Write to selected** | Starts a new announcement to only the ticked members. Only shown while the **Announcements** module is on, and only to board members and administrators. |

!!! warning "Ticks are lost when you change the filter or the page"
    Changing the search, a checkbox or the tag dropdown reloads the
    page, and your ticks are gone. So does moving to another page. Set
    the filter first, then tick. For a large group, narrow the filter
    (or give the members a tag and filter by it) and use **Select all
    *N* matching the filter** instead of ticking row by row.

When you follow the member list link from an announcement that was sent
to picked members, the list shows only those members with the notice
"Showing only the *N* selected members." Click **Show the whole list**
to return to the normal list.

### CSV export

**CSV Export** downloads a file called `members.csv`, separated by
semicolons, with one row per member in the current list. The column
headings are in German, so the file can be imported again as it is:

Vorname, Nachname, Strasse, PLZ, Ort, Geburtsdatum, IBAN, Member seit,
Member bis, E-Mail-Benachrichtigungen, E-Mail-Adressen, Telefonnummern,
Parzellen, Notizen, Tags.

- Dates are written as year-month-day (2024-03-01).
- Email information is written as "Ja" or "Nein".
- Several email addresses, phone numbers, parcels or tags share one
  cell, separated by semicolons.
- Tags are exported with the name you typed, not a translation.
- Whether a member declines birthday presents isn't exported.

!!! tip
    The export always matches what's on screen. To export every active
    member, click **Reset** first. To export former members, tick
    **Show inactive only** first.

## Importing members from a CSV file

Use the import to bring an existing member list -- from a spreadsheet
or an older program -- into Parcella. It works in two steps: you upload
the file, then you tell Parcella which column holds what. Nothing is
saved before you confirm the second step.

For a walkthrough of a first-time import, see
[Importing members and parcels](../guides/csv-import.md).

### Step 1: upload the file

Click **CSV Import** on the member list. The **CSV import** dialog
opens.

| Field / button | What it does |
|---|---|
| File field | Choose a `.csv` file. |
| **Import** | Uploads the file and opens the column mapping. Nothing is saved yet. |

The dialog lists the columns Parcella understands. You don't have to
use those headings -- you map the columns in the next step. Some things
to know about the file:

- Columns may be separated by semicolons or commas. Parcella detects
  which; if it can't tell, it assumes semicolons.
- The first row must be the heading row.
- Dates can be written as 2024-03-01, 01.03.2024 or 01.03.24.
- Several email addresses or phone numbers in one cell are separated by
  semicolons.
- The easiest template is a **CSV export** from Parcella itself -- the
  link in the dialog downloads the full, unfiltered export.

If the file is empty, you're sent back to the list with "That CSV file
appears to be empty."

### Step 2: map the columns

<!-- TODO(verify): no screenshot -- this page is only reached by uploading a file, which the screenshot tool can't do. -->

The **Map CSV columns** page shows every column of your file with its
heading and the first five data rows underneath, so you can see what's
in it. Above each column is a dropdown.

| Field / button | What it does |
|---|---|
| Dropdown per column | Choose the Parcella field this column belongs to: **First name**, **Last name**, **Street**, **Postal code**, **City**, **Date of birth**, **IBAN**, **Member since**, **Member until**, **Email notifications**, **Email addresses**, **Phone numbers**, **Notes** -- or **— Ignore —** to skip the column. Parcella pre-selects a field when it recognises the heading (in English or German, e.g. "Nachname" or "Last name"). |
| **Import** | Imports the rows and returns you to the member list. **First name** and **Last name** must each be mapped to a column, otherwise you get "Please map both the first name and last name columns before importing." |
| **Back** | Returns to the member list without importing anything. |

### What happens on import

For every row, Parcella looks for an existing member with the same
first and last name. If you mapped a **Date of birth** column and the
row has a date of birth, it must match too.

- **No match**: a new member is created, including the email addresses
  and phone numbers from the row.
- **A match**: the existing member is updated, but only with what the
  row actually contains (see below). Email addresses and phone numbers
  are **not** touched on an update -- add or remove those on the member
  page.
- **Several members with that name**: Parcella uses the row's date of
  birth, email addresses and phone numbers to find the right one. The
  member who has one of them is updated; case, spaces and dashes don't
  matter ("0171 234-5678" is the same as "01712345678"). If the row
  still fits more than one member, it is skipped with "Row 4: several
  members are called Hans Meier, skipped." and nobody is changed.
  An email address or phone number alone never matches a member with a
  different name, since couples often share one.
- **First or last name empty**: the row is skipped.

**An update only changes what the file says.** A column you set to
**— Ignore —**, or an empty cell, leaves the member's stored value as it
is. So a file with just names and new addresses updates the addresses
and nothing else.

The **Email notifications** column counts as "no" when it says *nein*,
*no*, *false* or *0*, and as "yes" for anything else that's filled in.
For an existing member, an empty cell or no such column leaves their
choice unchanged -- someone who opted out stays opted out. A new member
without a value gets "yes".

Afterwards the member list shows a summary such as "12 newly imported,
3 updated". If rows were skipped, the summary adds the number of errors
and the details of the first three.

!!! tip "Members with the same name"
    If your club has members with identical names, map the **Date of
    birth**, **Email addresses** or **Phone numbers** column: then each
    row updates the right person. Without any of them, such rows are
    skipped rather than guessed.

## Member page

![Member page](../assets/screenshots/members/detail.png)

Click a name in the member list to open the member page. It shows
everything Parcella knows about the member, and lets you add phone
numbers, email addresses, tags and parcels directly.

### Buttons at the top

| Button | What it does |
|---|---|
| **Edit** | Opens the [edit form](#new-member-and-edit-member). Needs write permission. |
| **Previous** / **Next** | Jumps to the previous or next member *in the list you came from*, with the same filter. You can also press ++ctrl+left++ and ++ctrl+right++ (not while typing in a field). On a Mac, these keys may be taken by the system for switching desktops. |
| **Back** | Returns to the member list, with your filter, on the page this member is on. |

### Master data

Shows **Name**, **Date of birth**, **Address**, **IBAN**, **Member
since**, **Member until**, **Email info** (whether the member may
receive information by email) and **Declines birthday presents**. To
change any of these, click **Edit**.

### Tags

Lists the member's tags. Click a tag to see every member with that tag.

| Field / button | What it does |
|---|---|
| **×** next to a tag | Removes the tag from this member (**Remove tag**). The tag itself stays for other members. Needs write permission. |
| **Add a tag, e.g. water responsible** | Type a tag name and click **+** (**Add tag**). If a tag of that name already exists -- capitals and extra spaces don't matter -- it's reused; otherwise a new tag is created. The field suggests existing tags as you type. Needs write permission. |
| **Manage tags** | Opens the [Member tags](#member-tags) page. |

Removing a tag from a member doesn't leave a history entry: tags are
labels for finding people, not club records.

### Phone numbers and Email addresses

| Field / button | What it does |
|---|---|
| Phone number field + **+** | Adds another phone number. Needs write permission. |
| Email field + **+** | Adds another email address. It must look like an email address. Needs write permission. |
| Trash button | Removes that phone number or email address (**Remove**). Needs delete permission. |

Click an email address to write to the member from your own mail
program.

### Assigned parcels

Lists the parcels assigned to the member.

| Column | What it shows |
|---|---|
| **Plot number** | Click it (or the arrow button) to open the parcel. |
| **Area** | The parcel's area in square metres. |
| **Status** | The parcel's status: **active**, **terminated** or **deleted**. |
| **Invoice address** | Whether this member's address is used for the parcel's invoices. |
| **Since** | The start of the tenancy. |

<!-- TODO(verify): this table lists every assignment of the member, including ended tenancies, and has no "until" column -- confirm whether former parcels are meant to appear here. Also, a communal parcel would show as "deleted" here because the badge only knows active/terminated. -->

To give the member a parcel (needs write permission):

| Field / button | What it does |
|---|---|
| **Choose parcel…** | The parcel to assign. Every parcel is offered, sorted by plot number. |
| **Use as invoice address** | Ticked by default. Invoices for this parcel go to this member's address. |
| **Assign** | Assigns the parcel and opens the parcel page. |

The tenancy starts without a date. To set a start date, or to end a
tenancy, use the parcel page -- see
[Current tenants](parcels.md#current-tenants).

### Processes

If the [Processes](processes.md) module is on and you may see
processes, a **Processes** card lists the processes about this member.
**Start a process** starts a new one for them.

### Notes

The member's internal notes, if there are any. Edit them in the member
form.

### Danger Zone

Only shown to users with delete permission.

**Delete Member** marks the member as deleted after you confirm. The
member disappears from all lists and searches. Their data stays in the
database, and existing parcel assignments, work sessions and other
records stay as they are.

!!! warning "Ending a membership is not deleting"
    For a member who leaves the club -- or has died -- set **Member
    until** in the edit form instead, and end their tenancies on the
    parcel page. They then move to **Show inactive only** and their
    history stays visible. Deleting is meant for records that should
    never have existed, such as a duplicate.
    <!-- TODO(verify): there's no way to restore a deleted member in the app; confirm. Also confirm how a deleted member who is still assigned to a parcel shows up on the parcel page. -->

## New member and Edit member

![New member form](../assets/screenshots/members/form-new.png)

Click **New member** on the member list, or **Edit** on a member page.
Both forms look the same; the new-member form additionally asks for a
first email address and phone number. Fields marked with a red star
are required.

### Personal data

| Field | What it does |
|---|---|
| **First name** \* | Required. |
| **Last name** \* | Required. |
| **Date of birth** | Used for the birthday list and the average age on the dashboard. Also helps the CSV import tell apart members with the same name. |
| **IBAN** | The member's bank account, e.g. for direct debits. |

### Address

| Field | What it does |
|---|---|
| **Street and house number** | |
| **Postal code** | Up to 10 characters. |
| **City** | |

The address is used for letters and invoices. If the member is a
parcel's invoice address, invoices for that parcel go here.

### Membership

| Field | What it does |
|---|---|
| **Member since** | The first day of membership. If it's empty, the member is listed as *pending* but still counts as active. If it lies in the future, the member counts as inactive until that day. |
| **Member until** | The last day of membership. "Leave empty = active member". From the day after, the member counts as inactive. |
| **Email address** | New members only. Optional -- more addresses can be added later on the member page. |
| **Phone number** | New members only. Optional -- more numbers can be added later on the member page. |
| **May receive information by email** | Ticked by default for new members. Untick it if the member doesn't want club information by email. The member list can filter on this. |
| **Declines birthday presents** | Tick it if the member doesn't want birthday presents. It shows on the birthday list, so whoever takes care of presents knows. |

### Notes

| Field | What it does |
|---|---|
| **Internal notes…** | Free text for the board. Notes are searched by the member list search. |

### Tags

| Field | What it does |
|---|---|
| Tag checkboxes | One checkbox per existing tag. Tick or untick to add or remove it. Only shown once tags exist. |
| **New tags, comma-separated** | Type new tags, separated by commas, e.g. "water responsible, hedge team". A name that already exists is reused. |

### Saving

| Button | What it does |
|---|---|
| **Create member** / **Save changes** | Saves the member and opens the member page. |
| **Cancel** | Leaves without saving. |

If a new tag name isn't accepted (for example, it's longer than 100
characters), the rest of the member is still saved and the edit form
opens again so you can fix the tag.
<!-- TODO(verify): in that case the form reopens without an error message. -->

## Member tags

![Member tags](../assets/screenshots/members/tags.png)

Tags are free labels to find members again -- "water responsible",
"extended board", "hedge team". Add them on a member page or in the
member form; rename or delete them here. Open the page with **Manage
tags** on the member list or on a member page.

Each tag has one row:

| Field / button | What it does |
|---|---|
| Tag name + check button | Change the name and click the check button (**Rename**). The new name shows for every member who has the tag. Refused if another tag already has that name. Needs write permission; without it you only see the name. |
| ***N* member(s)** | Opens the member list filtered by this tag. |
| Trash button | **Delete tag** after you confirm. The tag is removed from every member. Needs delete permission. |
| Translate button | Opens the **Translations** of the tag: one name per language Parcella supports. While the club runs in a language, lists, forms and filters show the tag's name in that language; an empty field shows the name you typed. Click **Save translations** to store them. Needs write permission; without it you see the translations as a list. The small number on the button tells how many translations exist. |
| **Back to members** | Returns to the member list. |

The CSV export always uses the name you typed, not a translation.

## Meeting sign-in sheet

![Meeting sign-in sheet](../assets/screenshots/members/signin-sheet.png)

Open it with **Sign-in sheet** on the member list. It produces a PDF
list to print and bring to a general meeting: every current tenant,
grouped by parcel, with a signature line for each.

| Field / button | What it does |
|---|---|
| **Headline** | Shown at the top of the PDF. It starts as "General meeting on" plus today's date; change it to anything you like. If you empty it, the default is used. |
| **Generate PDF** | Downloads the sign-in sheet as a PDF file. |
| **Cancel** | Returns to the member list. |

What's on the sheet:

- One row per person, with the columns **Parcel**, **Name** and
  **Signature**, sorted by plot number and then by last name.
- If several people hold one parcel, the plot number appears once and
  each of them gets their own signature line.
- Only **active members** who are **current tenants** of a parcel are
  listed. Members without a parcel, and tenants who have already left,
  are not on the sheet.
- The PDF carries the club logo and the same header and footer as the
  club's other documents. A long list simply runs over several pages.

!!! tip
    Members who hold no parcel -- honorary members, for example -- are
    not on the sheet. Add them by hand if they may attend.

## Related

- [Parcels](parcels.md) -- assigning and ending tenancies
- [Applicants](applicants.md) -- turning an applicant into a member
- [Welcoming a new member](../guides/new-member.md)
- [Handing over a parcel](../guides/parcel-handover.md)
- [Importing members and parcels](../guides/csv-import.md)
- [Announcements](announcements.md) -- writing to filtered or picked members
