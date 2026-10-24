# External contacts: companies and people in one table

**Context:** ADR 0096 made an external contact "a company plus the
contact person there", one row each. In practice a firm often has
several people the club talks to: the bank has an advisor and a clerk,
the city's allotment office has two case workers. Each became its own
row with the same `company_name` repeated. The company's address, IBAN,
tags and documents folder sat on one of those rows or were copied onto
all of them, and changing the address meant editing every row. The
request was a real two-level structure: one company with any number of
people under it.

**Decision:** `external_contacts` stays the only table. Each row has a
`kind` (`ExternalContactKind`: `COMPANY` or `PERSON`). A person may
belong to one company through `company_id`, a self-reference, and can
have a `position` there (migration 0109).

- **One table, not a separate `external_companies` table.** Phones,
  emails, tags, the cloud documents folder, notes, soft delete, the
  links from incoming invoices and purchase requests, the pickers, the
  red-flag lookup and the API all already work on a contact. With one
  table they work for companies and people alike, without a second set
  of tables and services. ADR 0096 already accepted one duplicated set
  (members vs. contacts). A third copy would be weight without benefit.
  This is the same shape as e.g. Odoo's `res.partner`. Companies get
  their switchboard number and `info@` address for free, and an invoice
  can point at the company or at a specific person there.
- **What lives where.** A company has `company_name` and never a person
  name. A person has first/last name and `company_name` is always NULL.
  A person's company name is read through the relationship
  (`organisation_name`). Because of this split, the two partial unique
  indexes from migration 0098 already mean "person name unique" and
  "company name unique" and didn't need to change.
- **Address and IBAN belong to the company.** A person can have their
  own, but only where it differs from the company's. When a person is
  entered together with their company (form, CSV row, API), that
  address and IBAN fill in what the company doesn't have yet. A value
  equal to the company's is dropped (`place_address_on_company()`). The
  person's page shows the company's address when the person has none.
- **Linking a company by name.** Everywhere a person comes with a
  company *name* (the web form, the CSV "Firma" column, the API's
  `company_name`), `resolve_company()` links the company of that name,
  ignoring case, or creates it. So old CSV files and old API clients
  keep working unchanged, and the form needs no separate "create
  company first" step. The API also takes `company_id` directly.
- **The kind is fixed once saved.** Turning a company with people into
  a person, or the other way round, raises questions (where do its
  people go?) that a "create new, merge, delete" covers just as well.
- **Merging companies.** Exact-name matching can't tell that
  "Commerzbank" and "Commerzbank AG" are one firm. `merge_companies()`
  moves people, phones, emails, tags and the invoice and purchase-request
  links to the target. It fills in address, IBAN and documents folder
  where the target has none, appends the notes, and soft-deletes the
  source. Merging needs the delete permission, the same as deleting.
- **A company with people can't be deleted.** Deleting it would leave
  them pointing at a deleted company. The user moves or deletes them
  first (409 in the API).
- **The list shows companies with their people beneath.** Top-level
  rows are companies and persons without a company
  (`ContactListFilter.apply_top_level()`). A search or tag hit on a
  person shows their company's row with the person highlighted.
  `apply()` stays the flat list for the API.
- **Red flag.** A company carrying the red-flag tag flags its people
  too (ADR 0098).
- **`company` is `lazy="selectin"`.** `display_name` ("Company (First
  Last)") reads it, and contacts are shown from many modules. A single
  forgotten `selectinload` would be a `MissingGreenlet` 500. A
  self-referential eager load needs `join_depth`, or it silently doesn't
  happen at all; 1 is enough, since a company has no company.

**Migration (0109):** a row with a person name became a `PERSON`, every
other row a `COMPANY`. Persons with a `company_name` were grouped by
that name (ignoring case and surrounding blanks) and linked to the
company-only row of that name. If there was none, a company was created
from the group's data. Address, IBAN and documents folder moved to the
company where it had none. They were cleared on the person where equal,
and kept where they differed, so nothing is lost. A company known only
from deleted people is created deleted. The downgrade copies the
company name and address back onto the persons; the companies stay
behind as company-only contacts, which the old model allows.

**Consequences:**

- The API is extended, not changed. `kind`, `company_id` and `position`
  are new. `company_name` is still accepted on a person and still
  returned for one, now read from the company. There are new `kind` and
  `company_id` list filters and a `merge-into` endpoint.
- The CSV gets "Typ" and "Position" columns. A file without "Typ"
  imports as before: a row with a name is a person.
- A person can't belong to two companies. A freelancer working for two
  firms is entered twice under different names, or once without a
  company.
- People aren't historized when they leave a firm (ADR 0005 would ask
  for an end date). Moving them to the new company or deleting them is
  the current answer.
