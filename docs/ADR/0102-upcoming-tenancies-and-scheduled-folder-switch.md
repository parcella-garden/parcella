# Upcoming tenancies, and the cloud folder switching on the handover date

**Context:** the parcel handover (ADR 0101) first allowed only dates up
to today. `MemberParcel.is_current` looked only at `assigned_until`, so
with a future date the incoming tenants would have counted as current,
and been billed, alongside the outgoing tenants who were still in their
notice period. kermie wanted future handovers to work: old tenants
become former tenants on their own once their end date has passed.
kermie also pointed out that the parcel's Nextcloud folder changes with
the tenants. A handover never leaves the parcel vacant, so
`deactivate_if_vacant()` never fired, and the new tenants inherited the
old tenants' folder. That broke the rule set out in
docs/module-cloud-storage.md.

## Decision 1: a tenancy is current only once it has started

`MemberParcel.is_current` and its SQL twin `current_tenant_filter()`
now also require `assigned_from IS NULL OR assigned_from <= today`.
There are two new properties:

- `is_upcoming`: `assigned_from` is in the future, and the tenancy
  wasn't ended before it began.
- `is_former`: `assigned_until <= today`, the same strict boundary as
  before.

Every tenancy is exactly one of current, upcoming or former. For a
handover on a future date D, the old tenants are current until D and
the new ones from D. They never overlap.

Where each one is used:

- **Readers of "who is the tenant now"** (invoicing, sign-in sheets,
  insurance, work-hours plot lists, FreeScout matching, public API)
  keep using `is_current` / `current_tenant_filter()`. They now
  correctly skip upcoming tenants. No call site changed.
- **The invoice-flag write rule** (`app/services/parcels.py`) switched
  from `is_current` to `not is_former`. An upcoming tenant must be able
  to hold `is_invoice_address`, because they are the next recipient.
  Read paths check `is_current` anyway (ADR 0058).
- **Vacancy** (`deactivate_if_vacant`) uses the new
  `current_or_upcoming_tenant_filter()`. A parcel whose new tenants move
  in next week isn't vacant.
- **Parcel page:** the tenant table lists current and upcoming tenants.
  An upcoming tenant gets a "from …" badge and a tenant serving notice
  gets an "until …" badge. "Former tenants" now selects `is_former`.
  With the old `not is_current` test, upcoming tenants would have shown
  up there.

**Other ways a tenancy can start in the future:** setting a future
"from" date on the normal assign form now also yields an upcoming
tenant. That was the intended meaning all along. On dev, only two rows
had a future `assigned_from`, and both were already ended, so nothing
visible changed. Tests: `tests/test_upcoming_tenancies.py` checks that
the Python properties and the SQL filters agree at every boundary.

## Decision 2: the handover moves the cloud folder, on the handover date

`ParcelCloudFolder` gets two dates (migration 0102):

- `active_until`: the active folder retires on this day.
- `active_from`: a scheduled row (`is_active=False`,
  `deactivated_at=NULL`) takes over on this day.

`schedule_handover_folders()` (`app/parcel_cloud_folders.py`) runs
inside the handover transaction:

- **D today or earlier:** the old folder is retired now. The picked
  folder, if any, becomes active now.
- **D in the future:** the old folder gets `active_until = D`. The
  picked folder, if any, is scheduled with `active_from = D`. A newer
  handover replaces an older schedule.

`apply_scheduled_folder_switches()` runs from an hourly background loop
(`_cloud_folder_schedule_loop` in `app/main.py`, the same style as the
other loops). It retires folders whose `active_until` has passed, then
activates due scheduled folders, retiring whatever is active on that
parcel first. That order keeps the one-active-folder-per-parcel index
satisfied. On the handover day, the switch can therefore lag by up to
an hour.

The old folder is **always** retired, whoever records the handover. That
is the safety rule. **Picking** the new folder is only offered to users
with full access when the `cloud_storage` module is on, the same rule as
for folders everywhere else. The handover form reuses the parcel page's
Nextcloud folder picker through the shared `browse_folder_picker()`. The
API's `new_folder_path` gets a 403 without full access or the module.

**Still not done (unchanged from docs/module-cloud-storage.md):**
Parcella doesn't create, rename or share folders in Nextcloud, and it
doesn't revoke the old tenants' shares. Renaming the old folder would
also carry the old tenants' documents over to the new ones, which is
exactly what the retire-and-replace approach avoids.
