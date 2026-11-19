# External contacts

External contacts is the club's address book for everyone who isn't a
member: suppliers, craftsmen, the water company, the city council. A
contact is either a **company** or a **person**, and a person can work
at a company. You can link contacts to incoming invoices and purchase
requests, tag them, and keep their documents in the club's cloud.

!!! info "Who can use this"
    Board members and administrators always have full access. Everyone
    else sees nothing of this module until a group grants **External
    contacts** permissions (see [Groups](../administration/groups.md)):

    - **Read** -- see the list and contact pages, export CSV, see the
      tags page, download documents.
    - **Write** -- create and edit contacts, add phone numbers, e-mail
      addresses and tags, rename tags, import CSV, choose a contact's
      document folder and upload documents.
    - **Delete** -- delete contacts, phone numbers, e-mail addresses
      and tags, and merge companies.

    The module is switched on with **External contacts** under
    [Turning modules on and off](../administration/modules.md). It is
    on by default.

## Companies and people

- A **company** has a company name, an address, an IBAN and its own
  phone numbers and e-mail addresses.
- A **person** has a first and last name, a position (e.g. "Clerk",
  "Owner") and optionally a company. If the person has no address or
  IBAN of their own, their page shows the company's.
- Whether a contact is a company or a person is decided when you
  create it and can't be changed later.
- A company name can exist only once, and so can a person's name
  (capital letters don't matter). Members don't count -- a contact may
  have the same name as a member.
- Every field is optional. A contact without any name shows as
  **Unnamed contact**.

## Contact list

![External contacts](../assets/screenshots/external-contacts/list.png)

**External contacts** in the navigation lists every company, with its
people indented below it, and every person who doesn't belong to a
company. The list is sorted alphabetically by company name, or by last
name for people without a company.

| Field / button | What it does |
|---|---|
| **CSV import** | Opens the [import dialog](#csv-import). Needs write permission. |
| **CSV export** | Downloads the list as a CSV file (see [CSV export](#csv-export)). Uses the current search and tag filter. |
| **Manage tags** | Opens the [tags page](#contact-tags). |
| **New contact** | Opens the [contact form](#contact-form). Needs write permission. |
| Search box | Searches company name, first and last name, position, street, postal code, city, IBAN, notes, phone numbers and e-mail addresses. Click **Search** to apply. |
| **All tags** / a tag | Shows only contacts with that tag. Only shown once tags exist. |
| **Reset** | Clears search and tag filter. Only shown while a filter is active. |

| Column | What it shows |
|---|---|
| **Name** | A building icon for companies, a person icon for people; the name links to the contact page. People show their position after the name. |
| **Tags** | The contact's tags. Click a tag to filter the list by it. |
| **Phone** | The first phone number. |
| **Email** | The first e-mail address, as a mail link. |
| Eye button | Opens the contact. |

When a search or tag matches a person, their company is listed too,
and the matching person is highlighted beneath it. The footer shows
how many entries (companies and people without a company) are listed.

## Contact form

![New external contact](../assets/screenshots/external-contacts/form-new.png)

**New contact** opens an empty form, **Edit** on a contact page the
filled-in one. **Add person** on a company's page opens it as a new
person with the company already filled in.

On a new contact, first choose **Company** or **Person** at the top.
The form then shows only the fields for that kind.

### Company / Person

| Field | Shown for | What it does |
|---|---|---|
| **First name**, **Last name** | Person | The person's name. Either part is enough. |
| **Company name** | Company | The company's name. |
| **Company (optional)** | Person | The company the person works at. Suggests existing companies as you type. An existing company is linked; a new name creates that company. Leave empty for a person on their own. On **Edit**, clearing it removes the person from the company. |
| **Position** | Person | E.g. "Clerk, Owner". |
| **Email**, **Phone** | New contacts | The first e-mail address and phone number. Add more later on the contact page. |

The note "All fields are optional. A company name and a person's name
may each exist only once." reminds you of the [rules above](#companies-and-people).

### Address & bank details

| Field | What it does |
|---|---|
| **Street**, **Postal code**, **City** | The postal address. |
| **IBAN** | Bank account, e.g. for paying the supplier's invoices. Up to 34 characters. |

For a person at a company: "Leave empty to use the company's. Entered
with a new company, it becomes the company's address." If the company
has no address or IBAN yet, what you enter is stored on the company;
if it's the same as the company's, it isn't stored twice. Only an
address or IBAN that really differs stays with the person.

### Notes and Tags

| Field | What it does |
|---|---|
| **Notes** | Free text -- opening hours, customer number, a ticket number. The list's search finds it. |
| Tag checkboxes | Tick existing tags. |
| **New tags, comma-separated** | Type new tags; they are created and added. |

Click **Create contact** (new) or **Save changes** (edit), or
**Cancel**. If a company or person with the same name already exists,
the form comes back with a message such as "A company called … already
exists." and keeps what you typed.

## Contact page

<!-- TODO(verify): no screenshot -- the sample data contains no external contacts, so the screenshot tool has no contact page to open. Add one once sample data seeds contacts. -->

### Buttons

| Button | What it does |
|---|---|
| **Edit** | Opens the contact form. Needs write permission. |
| **Previous** / **Next** | The previous or next entry of the list, keeping your search and tag filter. Keyboard: ++ctrl+left++ and ++ctrl+right++. |
| **Back to list** | Returns to the list with the same filter. |

### Company / Person

| Field | What it shows |
|---|---|
| **Company** (company) | The company name. |
| **Name**, **Position**, **Company** (person) | The person's name, position and a link to their company. A deleted company is marked "(deleted)". |
| **Address** | The contact's address. For a person without one, the company's, marked **Company address**. |
| **IBAN** | The contact's IBAN. For a person without one, the company's, marked **Company IBAN**. |

### People

Only on a company's page: every person at the company, with position,
phone numbers and e-mail addresses. **Add person** creates a new
person at this company (write permission). "No people at this company
yet." if there are none.

### Tags

The contact's tags; click one to see all contacts with it. With write
permission, the **x** on a tag removes it from this contact, and the
field **Add a tag…** adds an existing or new tag (up to 100
characters). **Manage tags** opens the [tags page](#contact-tags).

### Phone numbers and Email addresses

| Field / button | What it does |
|---|---|
| Number / address | Click to call or to write an e-mail. A label is shown in brackets. |
| Number / address field, **Label (optional)**, **+** | Adds another number or address, e.g. labelled "Office" or "Invoices". Needs write permission. |
| Bin button | Removes the number or address. Needs delete permission. |

### Incoming invoices and Purchase requests

Lists the [incoming invoices](finances/incoming-invoices.md) and
[purchase requests](purchase-requests.md) linked to this contact --
on a company's page also those linked to its people, with the person's
name after the entry. Each card is only shown if that module is on and
you may read it.

| Card | Columns |
|---|---|
| **Incoming invoices** | Invoice date, invoice number (or sender), total amount. |
| **Purchase requests** | Date created, title, estimated cost. |

### Documents

Shown when the cloud storage module is on. Letters, offers and
contracts aren't stored in Parcella but in a folder in the club's
cloud; this card shows that folder.

- An administrator first sets the base folder under
  [Integrations](../administration/integrations.md) (**Folder for
  external contacts' documents**). Until then the card says so.
- The folder for each contact is created by hand in the cloud, inside
  the base folder. On the contact page, someone with write permission
  then picks it from the **Folder** list and clicks **Save folder**.
  **Change folder** picks a different one; **— no folder —** unlinks
  it (the files stay in the cloud).
- Once a folder is picked, the card lists its files and subfolders.
  Click a subfolder to open it, a file to download it. The path above
  the list leads back up.
- With write permission, **Upload** puts a file into the folder that
  is currently shown.
- Deleting, renaming and moving files is done in the cloud itself.

Documents belong to the company: a person's page links to the
company's documents instead ("Documents are kept with the company:").

!!! warning
    If you rename a contact's folder in the cloud, Parcella loses
    track of it. Pick it again on the contact page.

### Notes

The notes, if any.

### Danger zone

Shown with delete permission.

| Field / button | What it does |
|---|---|
| **Merge into** + **Merge** | Only on a company's page. For two entries of the same firm (e.g. "Müller GmbH" and "Mueller GmbH"): choose the company to keep and click **Merge**, then confirm. People, phone numbers, e-mail addresses, tags and linked invoices and purchase requests move to the chosen company. Its address, IBAN and documents folder are filled in from this one where it has none; notes are added to its notes. This company is then deleted, and the kept one opens. |
| **Delete contact** | Deletes the contact after a confirmation. It disappears from the list and the pickers, but linked invoices and purchase requests still show it (marked "deleted" where they show it). Its name becomes free again. A company that still has people can't be deleted: "This company still has people. Move or delete them first." |

## Contact tags

![Contact tags](../assets/screenshots/external-contacts/tags.png)

**Manage tags** opens **Contact tags**. Contact tags are separate from
member tags. **Back to contacts** returns to the list.

| Field / button | What it does |
|---|---|
| **Flags applicants:** | Choose one tag (or **— none —**) and click **Save**. Applicants whose name, e-mail address or phone number matches a contact with this tag get a red flag in the applicants list and a warning on their page -- useful for a "do not lease" tag. A tagged company flags its people too. Only shown when the applicants module is on and tags exist; changing it needs write permission. See [Applicants](applicants.md). |
| Tag name + tick button | Renames the tag on every contact. Needs write permission. A name that already exists is refused. |
| **{count} contact(s)** | Opens the list filtered by this tag. |
| Bin button | Deletes the tag from every contact, after a confirmation. Needs delete permission. |
| **Translations** | Opens one field per language. A tag's name can be shown differently per language; empty fields show the tag's own name. **Save translations** stores them (write permission). |

New tags are created on a contact or in the contact form, not on this
page.

## CSV export

**CSV export** downloads `external-contacts.csv`: semicolon-separated,
one row per company or person, with the columns Typ, Firma, Vorname,
Nachname, Position, Strasse, PLZ, Ort, IBAN, E-Mail-Adressen,
Telefonnummern, Tags, Notizen (type, company, first name, last name,
position, street, postal code, city, IBAN, e-mail addresses, phone
numbers, tags, notes). "Typ" is "Firma" or "Person". Each company comes
first, followed by its people. Several e-mail addresses, numbers or
tags share one cell, separated by semicolons.

The file can be imported again unchanged.

## CSV import

The import has two steps and needs write permission.

### Step 1: choose the file

**CSV import** on the list opens **Import contacts from CSV**. Choose a
`.csv` file (semicolon or comma separated, with a header row) and click
**Import**. Nothing is saved yet.

### Step 2: Import contacts

<!-- TODO(verify): no screenshot -- this screen is only reachable by uploading a file, which the screenshot tool can't do from a URL. -->

The **Assign columns** card shows each column of your file with its
heading and the first five rows. For each column, choose the field it
goes into, or **— ignore —**:

**Type (company/person)**, **Company name**, **First name**, **Last
name**, **Position**, **Street**, **Postal code**, **City**, **IBAN**,
**Email addresses**, **Phone numbers**, **Tags**, **Notes**.

Parcella pre-selects the field for common German and English
headings, and maps its own export completely. No field is required.
Click **Import** to run it; **Back** cancels.

How each row is handled:

- **Company or person:** the type column says "Firma"/"Company" or
  "Person". Without it, a row with a first or last name is a person,
  otherwise a company.
- **Existing contacts are updated:** a company is matched by its name,
  a person by first and last name (capital letters don't matter). The
  match gets every field that is filled in the file; phone numbers,
  e-mail addresses and tags it doesn't have yet are added. Nothing is
  ever removed or emptied.
- **New contacts** are created for rows without a match.
- **A person's company:** the company column links the person to the
  company of that name, which is created if needed. The row's address
  and IBAN fill in what that company is missing and stay on the person
  only where they differ.
- Completely empty rows are skipped.

Afterwards the list shows a summary, e.g. "3 contact(s) created, 1
updated.", plus the first problems if rows were skipped (e.g. a
duplicate name).

## Where contacts are picked elsewhere

When this module is on and you may read contacts, other modules offer a
contact picker. Companies appear as a group with their people beneath
them; deleted contacts aren't offered.

| Where | Label | What it does |
|---|---|---|
| [Incoming invoices](finances/incoming-invoices.md) -- new invoice | **Contact** | Picking a contact fills in the sender. The sender stays a free-text field. |
| Incoming invoice page | **Contact** | Set or change the linked contact later. |
| [Purchase requests](purchase-requests.md) -- new request and request page | **Supplier (contact)** | The supplier for the purchase. Can be changed in any status. |

## Related

- [Applicants](applicants.md) -- red flags from tagged contacts
- [Integrations](../administration/integrations.md) -- cloud storage and
  the documents base folder
- [Groups](../administration/groups.md) -- giving the treasurer access
  to contacts
