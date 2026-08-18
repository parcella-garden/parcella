# Module: Members & Parcels (Core)

The core module -- always active, cannot be disabled (unlike the optional
modules such as Work Hours or Water/Electricity).

## Data model

```
members               – club members (core data)
member_phones          – n phone numbers per member
member_emails          – n email addresses per member
parcels                – garden parcels
member_parcels          – m:n member <-> parcel assignment
change_history          – generic audit log (see below)
```

## Key decisions

**Optional GPS coordinates (`Parcel.latitude`/`longitude`).** Both
nullable `Numeric(9, 6)` (3 integer digits + 6 decimals, covering
longitude's full -180..180 range at ~11cm precision -- standard GPS
storage convention), filled in by hand like `area_sqm`. Validated in
`app/services/parcels.py` (`_validate_coordinates()`) to stay within
real latitude/longitude bounds, same `ServiceError` pattern as the
plot-number-uniqueness check. When both are set, the parcel detail page
links out to `https://www.openstreetmap.org/?mlat=...&mlon=...` --
OpenStreetMap rather than a hardcoded Google Maps embed, since it needs
no API key/account and matches the project's general preference for
configurable/generic over vendor-specific (see CLAUDE.md). Deliberately
**not** exposed on `PublicParcelOut` (`/api/v1/public/parcels`, see
`docs/module-public-api.md`) -- that endpoint already omits the
parcel's own id specifically to avoid handing unauthenticated callers
anything beyond the bare plot number (an external pentest flagged even
the id as IDOR reconnaissance value); a member's plot's precise GPS
location would be a real privacy regression there, not just unrelated
data.

**m:n assignment from the start.** A member can have multiple parcels
(multiple gardens), and a parcel can have multiple members (couples,
families). The assignment table `member_parcels` carries
`assigned_from`/`assigned_until` (date fields) for tenancy history.
Originally also had an `is_primary_tenant` role distinction; removed
(see [Architecture Decisions](./ADR/0018-removed-the-primary-co-tenant-role-distinction.md)) since the
board holds every resident of a parcel jointly responsible, with no
hierarchy between them.

**`is_invoice_address` on `member_parcels`.** Residents of a parcel can
have different snail-mail addresses (each address lives on `Member`
itself -- there's no separate `Address` table); this flag marks which
assigned member's address is used to send that parcel's invoices. Same
shape as the removed `is_primary_tenant` (a plain boolean on the
assignment row, defaulting to `True`, no "exactly one per parcel"
constraint) but a different concern: it selects an address for postal
mail, not a liability rank -- see
[Architecture Decisions](./ADR/0035-invoice-address-flag-on-member-parcel-assignments.md).
A former tenant can never hold this flag; every code path that ends a
tenancy clears it in the same write so invoices don't keep going to
someone who's moved out. "Former" here means `is_current` is `False`
(the tenancy has actually ended, `assigned_until` in the past or
today), not merely "`assigned_until` is set" -- a tenant who gave
notice for a future date is still current and must still be billed
until they actually leave. The original DB-level backstop
(`ck_invoice_address_only_for_current_tenants` CHECK constraint) was
dropped for exactly this reason -- see
[ADR 0058](./ADR/0058-invoice-address-check-constraint-dropped-for-future-terminations.md).
Households (e.g. a couple who should both appear on the invoice letter)
are resolved at document-generation time by matching addresses among
current residents, the same way `household_grouping()` in
`app/insurance_utils.py` already does for insurance -- not by adding
more flags to the assignment row.

**Tenancy history instead of deletion.** When a tenancy ends,
`assigned_until` is set instead of deleting the row. This keeps it
traceable who held which parcel when -- important for questions that come
up years later. If a member later takes on the same parcel again, the
existing (ended) assignment is reactivated instead of creating a second
row (there is a `UniqueConstraint` on `member_id, parcel_id`).

**Active vs. inactive members.** A member counts as active if
`deleted_at IS NULL` and (`member_until IS NULL` or `member_until` is in
the future). The central helper function `active_member_filter()` in
`app/database.py` encapsulates this -- used everywhere only active members
are relevant (dropdowns, reports, assignments). The member list itself
shows only active members by default, with an "Show inactive" checkbox
for the history (e.g. deceased members).

**Current vs. former tenants (`MemberParcel.is_current`, issue #130).**
Same pattern as active members above, applied to tenancy rows: a
`MemberParcel` counts as current if `assigned_until IS NULL` or
`assigned_until` is still in the future -- a termination recorded ahead of
time doesn't take effect until its date arrives. Unlike `Member.is_active`'s
`>=` boundary, this uses a strict `>`: ending a tenancy (`member_remove` in
`app/routers/parcels.py`) sets `assigned_until = today`, and that tenant
must become former the *same* day, not the day before (see
`tests/test_members_signin_sheet.py::test_signin_sheet_excludes_former_residents`).
The query-level helper `current_tenant_filter()` in `app/database.py`
mirrors `active_member_filter()` for SQL-level call sites; in-Python list
filtering over an already-loaded relationship uses the `.is_current`
property directly. `is_invoice_address` now follows the exact same
`is_current` rule (see above) rather than the stricter "no
`assigned_until` at all" it used to require -- a tenant who's given
notice for a future date is still billed until that date actually
arrives.

**Change history (ChangeHistory).** A generic audit log
(`app/change_tracker.py`) that logs field changes on arbitrary entities
(currently used for parcels: area, status, plot number, etc.). Instead of
building a separate history table for every table, there is one shared
`change_history` table with `entity_type`, `entity_id`, `field_name`,
`old_value`, `new_value`. Usage:

```python
tracker = ChangeTracker(parcel, "Parcel", ["plot_number", "area_sqm", "status"])
# ... change fields ...
await tracker.commit(db, user.id)
```

**CSV import with automatic delimiter detection.** An early version hard-
coded a semicolon as the delimiter -- that broke as soon as someone opened
the export file in Excel and saved it again (Excel switches to a comma
depending on locale settings). It now uses `csv.Sniffer()` to detect the
delimiter, with semicolon as the fallback.

**CSV export respects the list page's current filter (issue #198).**
`_filtered_members_query()` in `app/routers/members.py` holds the
`search`/`include_inactive`/`pending_only` WHERE/ORDER BY logic once;
both `members_list` and `members_export_csv` build their query from it
(with their own `.options(...)` eager-loads on top), and the export
button on `/members/` carries the page's current query params through
to `/members/export/csv`. Before this, the export always ran
`active_member_filter()` unconditionally, regardless of what was
actually on screen. The CSV import modal's "here's the expected format"
template link is intentionally left pointing at the plain unfiltered
export -- a full example is more useful as an import template than
whatever subset happens to be filtered at the time.

## General-meeting sign-in sheet

`/members/signin-sheet` generates a PDF (`app/meeting_signin_sheet.py`,
WeasyPrint): current residents, grouped by parcel number, one
signature line each -- for printing and bringing to a physical
members' meeting.

**Not gated by a module flag, and permission-checked the same as the
member list itself (`require_user`).** It's just another view onto
member data that's already visible to anyone who can see the member
list, not a separate feature area with its own security surface --
adding a module flag here would be ceremony without a real decision
behind it.

**Deliberately not constrained to one page**, unlike the announcement
flyer (`app/print_publisher.py`): a real roster can run to several
pages, and there's no "shorten it" option for a list of people who need
to physically sign something. It's a normal multi-page document
sharing the same chrome as every other PDF in the app
(`app/pdf_chrome.py`'s `wrap_document()` -- DIN-style fixed header, the
three-column organization/register-court/bank footer, "Page X of Y" via
`counter(page)`/`counter(pages)`; see docs/ADR/0043 and docs/ADR/0045).

**The headline is a plain editable text field, not a template with
placeholders.** The original ask included an example like "General
meeting on {date}" -- that's illustrative phrasing, not a literal
`{date}` token to substitute. The form pre-fills a sensible default
(today's date) into an ordinary text input; the admin can edit it to
say anything before generating.

**Parcels with multiple current residents get one row per person,
sharing a single rowspan'd parcel-number cell.** Reads like a real
paper sign-in sheet: the parcel number appears once per group, but
every co-tenant still gets their own name and their own signature
line.

**`app/pdf_utils.py` was factored out of `app/print_publisher.py`**
once this became the second PDF generator embedding local images as
base64 data URIs (the club logo, in both cases) -- shared to avoid a
second copy of the same small helper, not because either module
depends on the other.

## Known pitfalls

- `row.get("Column", "")` does NOT protect against `None` values when a
  CSV row has fewer fields than the header row (Python fills those with
  `None`; the default only kicks in when the key is missing entirely).
  Always use `(row.get("Column") or "")`.
- `scalar_one_or_none()` raises an error as soon as more than one row comes
  back -- for duplicate *detection* (where multiple matches can be
  expected), `.scalars().first()` is the right choice.

## Implementation note (ADR 0070)

Member CRUD (create/update/soft-delete, phone/email sub-resources) and
the "active member" query filter live in `app/services/members.py`,
called by both `app/routers/members.py` and `app/routers/api_members.py`.
The API's `active_only` filter now pushes `active_member_filter()` into
SQL before pagination, same as the HTML list view -- it used to filter
in Python afterward, which could return fewer than the requested page
size (see ADR 0070). The API router also now checks permissions the
same fine-grained, `Group`-based way the HTML side does
(`require_api_permission`), not the coarser role-only check most other
API routers still use.

Parcel CRUD, plot-number-uniqueness checking (now enforced on update
too, not just create), and the tenant-assignment lifecycle (assign/
reactivate, edit, end, hard-delete-history) live in
`app/services/parcels.py`, same pairing. This closed the most serious
finding in the whole ADR 0070 rollout after tickets itself:
API-driven parcel edits (`PUT /api/v1/parcels/{id}`), including status
and termination changes, previously wrote no audit trail at all. Three
further real divergences were found and fixed along the way -- a former
tenant could never be reassigned to the same parcel via the API (it
403/409'd on any historical row; HTML always reactivated), the
invoice-address rule (issue #172) wasn't applied on the HTML side's
brand-new-assignment path, and the API's single `DELETE .../assignments/
{id}` endpoint used to hard-delete an *active* assignment unconditionally
-- it now soft-ends an active one and only hard-deletes an already-ended
one, same distinction the HTML UI's two separate actions make.
