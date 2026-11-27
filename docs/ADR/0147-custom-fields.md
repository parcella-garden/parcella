# 0147: Custom fields on members and parcels

**Status:** accepted (issue #443, kermie, 2026-11-27 -- "all of that
indeed might change later": a first version to try out)

## Context

Clubs want to record things Parcella has no column for: a member's
occupation; on a parcel a summer house (with area and build date) or a
pool (diameter, height, removed in winter). A new column per wish
doesn't scale and is club-specific (CONTRIBUTING: genericity).

## Decision

- **Defined by system admins** under Admin → Custom fields (the admin
  panel's rule, ADR 0039). Entering values needs only the existing
  `members_parcels` write permission: no new permission.
- **Two tables.** `custom_fields`: one row per field, with `target`
  (MEMBER / PARCEL), `kind`, `label`, `help_text`, `unit` (numbers),
  `options` (choices, JSON), `required`, `position`, `archived_at`, and
  a fixed `key` (slug of the first label) for exports and the API.
  `custom_field_values`: one row per owner and field with typed columns
  (`value_text` / `value_number` / `value_date` / `value_bool`), like
  ProcessField (ADR 0136), and two nullable foreign keys `member_id` /
  `parcel_id` with a check that exactly one is set. Real foreign keys
  instead of a polymorphic "owner id": deleting a member or parcel
  cascades to its values, and nothing can point at the wrong table.
- **A group is a field** of kind GROUP (a yes/no) whose sub-fields point
  at it via `parent_id`; one level only. A sub-field only counts while
  its group is ticked: required only then, and **unticking clears its
  sub-fields** ("no pool, no pool data"). Groups are once per member or
  parcel, not repeatable (kermie's call) -- repeatable groups would be a
  third table and much heavier forms, filters, CSV and API.
- **A value row exists only for a ticked yes/no or a filled-in field**,
  so "empty", "no" and "no row" are the same thing. The list filter
  relies on that ("has a pool" = "has a row").
- **Archive or delete.** Archiving hides the field (a group with its
  sub-fields) from forms, lists and exports, and the values stay; saving
  a form never touches archived fields' values. **Deleting** removes the
  field with its values (a group with its sub-fields) for good -- kermie
  asked for it after the first smoke test: a field set up by mistake or
  for a one-off survey shouldn't linger. This is a deliberate exception
  to ADR 0005: a field definition is configuration, not club history.
  The confirmation names the number of values that go with it.
  `delete_field` is a plain DELETE statement (the database cascades the
  values), so the ORM can't turn sub-fields into top-level fields by
  nulling their `parent_id`.
- **The type is locked** once any value exists, and never changes to or
  from a group: converting stored values between kinds isn't worth it.
- **Where they show:** edit form and detail page ("Further details"),
  a filter on the member and parcel lists (part of `MemberListFilter`,
  so stored announcement audiences and "Write to" work with it too),
  CSV export/import columns, and the REST API by key.
- **Personal data:** member fields are personal data. They are not
  offered to AI interfaces (the MCP server has no access to them), in
  line with the no-personal-data-to-AI rule.

## Rejected

- **A JSON column on members/parcels:** no per-field validation or
  type, awkward to filter and to keep consistent with archived fields.
- **Reusing the process tables:** processes have stages and a lifecycle;
  custom fields are plain attributes. The pattern is shared, the tables
  aren't.
- **Per-field permissions:** not asked for; easy to add later on the
  field row.

## Consequences

- Numbers are stored with two decimals (`Numeric(14, 2)`).
- Field labels are typed in the club's language; there are no per-
  language labels (unlike tags, ADR 0098) yet.
- More targets (external contacts, inventory, metering points) need a
  new enum value, a foreign-key column on the value table and the
  form/detail hooks of that module.
