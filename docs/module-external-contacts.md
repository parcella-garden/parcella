# Module: External contacts

People and companies the club deals with who aren't members:
suppliers, craftsmen, utilities, authorities. A contact is a **company**
or a **person**, and a person may work at one company. The list shows
each company with its people beneath it. Why this is its own table and
not a kind of member: ADR 0096. Why companies and people share one
table: ADR 0110.

Module flag: `external_contacts`. On by default, since it opens no
public endpoint and stores no outbound credentials.

Permission module: `external_contacts` (`app/permissions.py`).
ADMIN/BOARD get full access. Everyone else gets nothing by default
(unlike members_parcels, there's no baseline read), so a group has to
grant read, write or delete, e.g. to a treasurer.

## Data model

```
external_contacts            – company or person (kind), a person's company_id + position,
                               address, IBAN, notes, cloud folder, soft delete
external_contact_phones      – n per contact (number, label, is_primary)
external_contact_emails      – n per contact (address, label, is_primary)
external_contact_tags        – own tag pool, names unique ignoring case
external_contact_tag_links   – contact <-> tag
incoming_invoices.external_contact_id   – optional link (SET NULL), company or person
purchase_requests.external_contact_id   – optional link (SET NULL), company or person
```

- `kind` -- `COMPANY` or `PERSON` (migration 0109). It's fixed once
  saved. When it isn't given (old CSV files, API clients), a contact
  with a first or last name is a person.
- **Company:** `company_name`, never a person name. Unique ignoring
  case among non-deleted companies (`uq_external_contacts_company`).
- **Person:** `first_name` / `last_name` (either part or both),
  `position` ("Sachbearbeiter", "Inhaber"), optional `company_id` → a
  company. `company_name` is always NULL; `organisation_name` reads it
  from the company. A given name is unique ignoring case
  (`uq_external_contacts_person`). Members don't take part in this
  check.
- Every field is optional (migration 0098). A contact with nothing
  filled in shows as "Unnamed contact" (`external_contacts.unnamed`).
- Both uniqueness rules are checked up front in
  `app/services/external_contacts.py`, which gives a 409 with a
  readable message.
- `street` / `postal_code` / `city` / `iban` -- on a company its own.
  On a person only where it differs from the company's: entered
  together with the company, the values fill in what the company lacks,
  and equal ones are dropped (`place_address_on_company()`). The
  person's page shows the company's address and IBAN when it has none.
- `deleted_at` -- soft delete (ADR 0005). A deleted contact's name can
  be used again. A company with non-deleted people can't be deleted:
  move or delete them first.
- `display_name` -- a company's name; a person as "Company (First
  Last)", or just the name without a company. Used in the pickers and
  on linked records. `company` is `lazy="selectin"` (with `join_depth`)
  so this works wherever a contact is loaded; `people` is not, so
  `selectinload(ExternalContact.people)` wherever it's read.

## Where things live

- `app/services/external_contacts.py` -- create, update, delete, phones,
  emails and tags. Shared by the web UI and the API (ADR 0070).
- `app/contact_filters.py` -- `ContactListFilter` (search + tag), shared
  by the list, CSV export, Previous/Next and the API list.
  `apply_top_level()` gives the list's rows (companies and persons
  without a company) where the row or one of its people matches;
  `apply()` is the flat list the API uses. The search
  covers every text field, notes included, so a FreeScout ticket number
  noted there finds the contact (members and applicants search the same
  way).
- `app/routers/external_contacts.py` -- web UI under `/contacts/`, plus
  `picker_contacts()` / `resolve_picked_contact()` for other modules'
  forms. The pickers group each company with its people
  (`picker_groups()`, `external_contacts/_picker_options.html`).
- `app/routers/api_external_contacts.py` -- `/api/v1/external-contacts`:
  CRUD, phones, emails, tags, `kind` / `company_id` list filters and
  `POST /{id}/merge-into/{target_id}`. A duplicate name, or deleting a
  company with people, is a 409. On a person, `company_name` links the
  company of that name (created if needed), `company_id` by id.

## Companies and people

- **Form:** a Company / Person switch on a new contact. A person's
  "Company" field offers the existing companies; a name that doesn't
  exist yet creates the company (`resolve_company()`). "Add person" on
  a company's page opens the form with the company filled in.
- **Company page:** a People card (each person with phones and
  emails), and the incoming invoices and purchase requests linked to
  the company *or* any of its people.
- **Person page:** a link to the company, its address and IBAN if the
  person has none. Documents live with the company; the person's page
  links there, unless the person still has a folder of their own from
  before.
- **Merge** (company page, delete permission): for two spellings of one
  firm. People, phones, emails, tags and the invoice and
  purchase-request links move to the chosen company. Address, IBAN and
  documents folder fill in where it has none, notes are appended, and
  the merged company is soft-deleted.

## CSV import / export

- Export columns: Typ; Firma; Vorname; Nachname; Position; Strasse;
  PLZ; Ort; IBAN; E-Mail-Adressen; Telefonnummern; Tags; Notizen.
  "Typ" is "Firma" or "Person". Each company comes first, followed by
  its people (their "Firma" filled in), so a file imports back with the
  company existing before its people. Multiple values sit in one cell,
  separated by `;`. The export follows the list's current filter.
- Import is the two-step column-mapping wizard (ADR 0083), with German
  and English header aliases. Our own export maps automatically.
- Each row is a company or a person: "Typ" says which; without it, a
  row with a name is a person. It is matched ignoring case: a person by
  name, a company by company name. Completely empty rows are skipped
  silently.
  - A person's "Firma" links the company of that name, which is created
    if needed. The row's address and IBAN fill in what that company
    doesn't have yet, and stay on the person only where they differ. An
    old-style file (one row = company + person + company address)
    therefore ends up as one company with its people.
  - A match updates the fields that are non-empty in the CSV, and adds
    phones, emails and tags the contact doesn't have yet. Nothing is
    ever removed.
  - No match creates a new contact.

## Documents (cloud storage)

Letters, offers and contracts exchanged with a contact are kept in the
connected cloud storage, not in Parcella (ADR 0097). This needs the
`cloud_storage` module and its connection.

- **Base folder:** one club-wide setting, on Administration →
  Integrations → Nextcloud card ("Folder for external contacts'
  documents"). For kgv-goldene-hoehe this is `kgv_dokumente/extern`.
  The `ClubSetting` key is `external_contacts_cloud_folder`. Leave it
  empty to switch the card off.
- **Per contact:** subfolders of the base folder are created by hand in
  the cloud. On the contact's page a user with write access picks one
  from a dropdown ("Change folder" re-picks it). Only the name is
  stored, in `external_contacts.cloud_folder` (migration 0099).
- **The documents card:**
  - lists the folder, including any subfolders (e.g. Eingang/Ausgang
    for received/sent, if the club organises it that way)
  - lets you browse into them
  - downloads with read access
  - uploads into the folder currently shown, with write access
- Deleting and moving files happens in the cloud.
- Code: `app/contact_documents.py` (setting, path rules) and the
  "Documents" section of `app/routers/external_contacts.py`.

## Tags: translations and the applicant red flag

Same per-language tag names as member tags (ADR 0098): set on
`/contacts/tags`, stored in `external_contact_tags.translations`, shown via
`tag_name()`.

The same page picks the **red-flag tag** (`ClubSetting`
`applicant_red_flag_tag_id`, shown while the applicants module is on).
An applicant whose name, email or phone matches a non-deleted contact
with that tag gets a red badge (a tagged company flags its people too) on `/applicants/` and a warning on their
detail page. It's computed live in `find_red_flags()`
(`app/services/applicants.py`); see `docs/module-applicants.md`.

## Links from other modules

- **Incoming invoices** (finances): an optional "Contact" picker on the
  create form. Picking one fills in `sender`. On the detail page the
  link can be set or changed later. `sender` stays the required
  free-text field, because search, the accounting statement and bank
  matching read it (ADR 0096).
- **Purchase requests**: an optional "Supplier (contact)" on the create
  form and the detail page. The API accepts `external_contact_id` on
  create.
- The contact's detail page lists both, if the user may read that
  module and it's switched on.
- Pickers show only when this module is on and the user may read
  contacts.

## Known gaps

- No incoming-invoice REST API exists yet, so the invoice link can only
  be set in the web UI.
- No setting of `external_contact_id` on existing purchase requests via
  the API (no PR update endpoint exists).
- Company names match exactly (ignoring case). Two spellings of one
  firm become two companies until someone merges them.
- A person belongs to at most one company, and leaving a firm isn't
  historized: move the person, or delete them.
- A contact can't switch between company and person once saved.
- No REST endpoint for merging persons (only companies merge).
- Inventory or calendar entries can't be linked to a contact yet.
- Renaming a contact's folder in the cloud breaks its link until
  someone re-picks it on the contact page.
- No REST API for contact documents.
