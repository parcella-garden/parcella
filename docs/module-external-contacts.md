# Module: External contacts

People and companies the club deals with who aren't members:
suppliers, craftsmen, utilities, authorities. Each one is a company
plus the contact person there. Why this is its own table and not a
kind of member: ADR 0096.

Module flag: `external_contacts`. On by default, since it opens no
public endpoint and stores no outbound credentials.

Permission module: `external_contacts` (`app/permissions.py`).
ADMIN/BOARD get full access. Everyone else gets nothing by default
(unlike members_parcels, there's no baseline read), so a group has to
grant read, write or delete, e.g. to a treasurer.

## Data model

```
external_contacts            – company + contact person, address, IBAN, notes, soft delete
external_contact_phones      – n per contact (number, label, is_primary)
external_contact_emails      – n per contact (address, label, is_primary)
external_contact_tags        – own tag pool, names unique ignoring case
external_contact_tag_links   – contact <-> tag
incoming_invoices.external_contact_id   – optional link (SET NULL)
purchase_requests.external_contact_id   – optional link (SET NULL)
```

- Every field is optional (migration 0098). A contact with nothing
  filled in shows as "Unnamed contact" (`external_contacts.unnamed`).
- `company_name` -- may repeat (several people at one firm). A contact
  without a company is fine too, e.g. a self-employed gardener.
- `first_name` / `last_name` -- a given person name (either part or
  both) is unique ignoring case among non-deleted contacts
  (`uq_external_contacts_person`). Members don't take part in this
  check.
- A contact *without* a person is unique by company instead, ignoring
  case (`uq_external_contacts_company`). The same company with a person
  is a different contact. Both rules are checked up front in
  `app/services/external_contacts.py`, which gives a 409 with a
  readable message.
- `street` / `postal_code` / `city` -- the company address.
- `deleted_at` -- soft delete (ADR 0005). A deleted contact's name can
  be used again.
- `display_name` -- "Company (First Last)", or just the person if
  there's no company. Used in the pickers and on linked records.

## Where things live

- `app/services/external_contacts.py` -- create, update, delete, phones,
  emails and tags. Shared by the web UI and the API (ADR 0070).
- `app/contact_filters.py` -- `ContactListFilter` (search + tag), shared
  by the list, CSV export, Previous/Next and the API list. The search
  covers every text field, notes included, so a FreeScout ticket number
  noted there finds the contact (members and applicants search the same
  way).
- `app/routers/external_contacts.py` -- web UI under `/contacts/`, plus
  `picker_contacts()` / `resolve_picked_contact()` for other modules'
  forms.
- `app/routers/api_external_contacts.py` -- `/api/v1/external-contacts`:
  CRUD, phones, emails, tags. A duplicate person name is a 409.

## CSV import / export

- Export columns: Firma; Vorname; Nachname; Strasse; PLZ; Ort; IBAN;
  E-Mail-Adressen; Telefonnummern; Tags; Notizen. Multiple values sit
  in one cell, separated by `;`. The export follows the list's current
  filter.
- Import is the two-step column-mapping wizard (ADR 0083), with German
  and English header aliases. Our own export maps automatically.
- Each row is matched ignoring case: by the person's name if the row
  has one, otherwise by company among contacts without a person.
  Completely empty rows are skipped silently.
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
- No duplicate check on company + address. Two entries for the same
  company with different contact persons are intended.
- Inventory or calendar entries can't be linked to a contact yet.
- Renaming a contact's folder in the cloud breaks its link until
  someone re-picks it on the contact page.
- No REST API for contact documents.
