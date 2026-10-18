# External contacts: a separate entity, not members with a flag

**Context:** The club deals with people who aren't members: suppliers,
craftsmen, the water utility, the city's allotment office. They were
kept in notes, mailboxes and spreadsheets. The request was "basically
the same as members", but with a company name and a contact person, a
company address and an IBAN, with notes, tags and several phone
numbers and email addresses. They have no date of birth, no membership
dates, no email-info opt-in and no parcels. Company names may repeat;
contact person names may not. A follow-up made every field optional,
names included (migration 0098): a company without a known contact
person, or a phone number nobody has put a name to yet, are real
entries.

**Decision:** A separate `ExternalContact` model with its own phone,
email and tag tables (`app/models.py`, migration 0097). It is a module
of its own (`external_contacts`, on by default, with its own entry in
the permission matrix), under `/contacts/` and
`/api/v1/external-contacts`.

- **Not a `Member` with a type flag.** Nearly every consumer of
  `Member` would have to learn to skip contacts: `active_member_filter()`,
  invoice runs, work-hours eligibility, announcements to all members,
  the general-meeting sign-in sheet, the FreeScout matching and the
  dashboard counts. Missing just one of these would invoice a supplier
  or email the plumber the club newsletter. A separate table can't leak
  into any of them.
- **Uniqueness lives on the person, not the company.** Two people at
  the same firm are normal. Two contact persons with the same name are
  almost always a duplicate entry. With optional names this becomes two
  rules:
  - A given person name (first and/or last) is unique. This is enforced
    by a partial unique index on `(lower(coalesce(first_name, '')),
    lower(coalesce(last_name, '')))`, covering rows that have at least
    one name part.
  - A contact without a person is unique by company. This is enforced
    by a second partial index on `lower(company_name)`, covering rows
    with no name and a company. Otherwise, re-importing an export would
    duplicate every company-only contact.

  A contact with neither a name nor a company has nothing to compare
  and may exist several times. `check_duplicate_free()` in
  `app/services/external_contacts.py` runs first so the user gets a
  readable message (409 in the API) instead of an IntegrityError. Ignoring case matches member tags
  (ADR 0093): "max müller" and "Max Müller" are the same person.
  Excluding soft-deleted rows means a deleted contact frees its name.
  Member names don't take part: a member may also be the club's
  electrician.
- **Its own tag pool** (`ExternalContactTag`), with the same rules as
  member tags (ADR 0093). "Supplier" has no business in the member tag
  filter, and member tags can feed announcements (ADR 0095).
- **Soft delete** (ADR 0005), like members. Linked invoices and purchase
  requests keep pointing at a deleted contact and still show its name.
  Deleted contacts disappear from the pickers.
- **CSV import matches the same way duplicates are defined**: by
  person name if the row has one, else by company among contacts
  without a person. Both are unique, so the match is unambiguous.
  Completely empty rows are skipped. An import adds phones,
  emails and tags and updates non-empty fields, but never removes
  anything. The export uses the same columns, so a file can go out and
  come back in unchanged. `csv_safe()`'s leading apostrophe is stripped
  again on import.

**Links to other modules:** A nullable `external_contact_id`
(`ON DELETE SET NULL`) on `incoming_invoices` and `purchase_requests`.

- On incoming invoices the link sits *alongside* the free-text `sender`
  and doesn't replace it. Search, the cash accounting statement, the
  bookings list and bank-transaction matching all read `sender`.
  Switching them to the contact would break every invoice entered
  before contacts existed, and would force a contact for a one-off bill
  from the hardware store. Picking a contact fills in the sender, and
  the user can still change it.
- On purchase requests the contact is the supplier. It is not part of
  the four-eyes approval and stays editable in every status.
- Pickers only appear when the contacts module is on and the user has
  read access to it (`picker_contacts()`). A submitted id is checked to
  be a non-deleted contact (`resolve_picked_contact()`), so a crafted
  form can't link to a contact the user can't see.

**Consequences:** Two near-identical sets of phone, email and tag
tables and services (member and contact). That's accepted: the shapes
match today, but each side is free to change (e.g. member phones
feeding FreeScout matching) without affecting the other. Don't merge
the tables, and don't give contacts a parcel, invoices or announcements
through the member code paths. If one of those is ever needed, it's a
deliberate feature on the contact side.
