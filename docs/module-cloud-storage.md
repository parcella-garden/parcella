# Cloud storage module

Connects Parcella to a club's existing file storage (Nextcloud, any WebDAV
server, or S3-compatible object storage; one at a time, ADR 0106) so board/admin
users can browse, upload to, and download from a per-parcel document
folder without leaving Parcella -- lease agreements, membership
paperwork, ticket correspondence. Off by default (`cloud_storage`
module flag defaults to `False`), since it stores outbound credentials
and, once configured, lets board members move real member paperwork
in and out of the club's cloud storage.

## Data model

```
parcel_cloud_folders  -- one row per (parcel, tenancy period); at most
                          one active row per parcel at a time
```

**`ParcelCloudFolder`** holds `relative_path` (the folder's location
inside the club's Nextcloud account), `is_active`, and who set it
(`set_by_user_id`). Scoped to the **parcel**, not to a single
`MemberParcel` row -- a parcel can have several co-tenants (couples,
families) with separate `MemberParcel` rows for the same lease period,
and they share one folder. Older rows are kept (`is_active=False`) as
history rather than deleted, the same pattern as ended `MemberParcel`
assignments elsewhere in the project. A Postgres partial unique index
(`postgresql_where=is_active`) enforces "at most one active folder per
parcel" at the database level, not just in application code.

No new table is needed for credentials -- those live in the existing
`club_settings` key-value table (`nextcloud_base_url`,
`nextcloud_username`, `nextcloud_app_password`), same as the SMTP and
WordPress blog integrations.

## The connector: `app/cloud_storage.py`

A small `CloudStorageProvider` interface and three backends, chosen from
the dropdown on Admin -> Integrations -> Cloud storage (ADR 0106, same
`ProviderRegistry` as the website connectors in `app/provider_registry.py`):

- `WebDAVProvider`: any WebDAV server (`PROPFIND` to list, `PUT`/`GET`/
  `DELETE` for files, `MKCOL` for folders) below a configured root URL.
  It compares the decoded `<href>` paths, so servers that answer with a
  full URL or a path, encoded their own way, all work.
- `NextcloudProvider`: a `WebDAVProvider` whose root is
  `{base_url}/remote.php/dav/files/{username}`, with an app password.
- `S3Provider`: S3-compatible object storage, path-style addressing,
  SigV4-signed with the standard library (`sigv4_headers`, tested against
  AWS's documented example). A "folder" is a key prefix; `create_folder`
  writes an empty `<folder>/` marker, and a prefix with neither marker
  nor content counts as missing, like WebDAV's 404. An optional path
  prefix keeps Parcella's files under one sub-path of the bucket.

Every feature calls `get_cloud_storage_provider(db)` and only uses the
interface. Settings: `cloud_storage_provider` (active type) and
`cloud_storage_<type>_<field>`; migration 0106 moved the old
`nextcloud_*` keys over. Nextcloud Deck sync keeps its own `deck_*`
settings (ADR 0086). Not built yet: Google Drive, OneDrive and Dropbox,
which need an OAuth login flow instead of stored credentials.

Originally list/upload/download only, deliberately narrow for v1 -- no
delete, no folder creation. The folder a club points Parcella at is
expected to already exist and typically is already shared with the
relevant members directly in Nextcloud. Board tooling deleting files
from someone's personal cloud storage is a bigger, separately-considered
decision than this module needed to make.

**`delete_file`/`create_folder` added (issue #141, see
[ADR 0055](./ADR/0055-scheduled-cloud-backups.md)):** the scheduled
cloud-backups feature needs both -- creating its own destination
folder on first run, and pruning old backups beyond a configured
retention count. Scoped narrowly to that feature managing its own
backup files in its own configured folder, not a general reversal of
the reasoning above.

Every failure mode (network error, 401, 404, unexpected status,
unparseable XML) raises `CloudStorageError` with a message meant to be
shown directly to the board member who triggered the action -- not a
generic "something went wrong."

`load_nextcloud_configuration()` treats a partially-filled
configuration (e.g. URL and username saved, but no app password yet) as
"not configured" rather than attempting a connection and failing
confusingly.

## Lifecycle rules: `app/parcel_cloud_folders.py`

`sanitize_relative_path()` normalizes a board-entered path and rejects
anything containing a `..` segment -- the path is later joined onto a
WebDAV URL, so path traversal here isn't just a UI nuisance, it could
reach outside the intended folder tree on the storage side. That
covers the folder path, but not the `filename` that
`download_file`/`upload_file` take directly from a query parameter /
uploaded filename with no equivalent check -- so `_join_dav_path()`
itself (`app/cloud_storage.py`) also rejects `..` segments, as the
choke point both callers go through (flagged by an external pentest).

`deactivate_if_vacant(db, parcel_id)` is the one safety-relevant rule:
called after any action that can end a resident's tenancy (setting
`MemberParcel.assigned_until`), it deactivates the parcel's active
folder once the parcel has zero residents left with an open-ended
assignment. This runs automatically from `mitglied_zuordnung_
aktualisieren` and `mitglied_entfernen` in `app/routers/parcels.py` --
so a fresh set of tenants moving in after a full turnover never sees or
inherits the departing tenants' folder path. Re-configuring the folder
for the new tenancy is a **separate, deliberate action** a board member
takes afterwards; nothing points a new tenant at a folder automatically.

**Handover to applicants ([ADR 0102](./ADR/0102-upcoming-tenancies-and-scheduled-folder-switch.md)).**
A handover never leaves the parcel vacant, so the check above can't see
that turnover. The handover therefore retires the old folder itself, on
the handover date: right away for a date today or earlier, otherwise via
`active_until` and the hourly `apply_scheduled_folder_switches()` loop.
The board can pick the new tenants' folder in the same form (the same
picker, through `browse_folder_picker()`). It is stored as a scheduled
row (`active_from`) and takes over on that date. The vacancy check
itself now counts upcoming tenants as residents too
(`current_or_upcoming_tenant_filter()`).

## Web UI and permissions

Viewing and mutating are both board/admin-only (`require_admin`, which
permits `ADMIN` and `BOARD` roles) -- unlike modules such as Inventory
where viewing is open to any member. A parcel's "Documents" card only
renders when the `cloud_storage` module flag is on *and* the logged-in
user is admin/board; the three mutating routes
(`POST /parcels/{id}/cloud-folder`,
`POST /parcels/{id}/cloud-folder/upload`,
`GET /parcels/{id}/cloud-folder/download`) are additionally gated with
`Depends(require_module("cloud_storage"))`, returning 404 if the module
is disabled.

Credentials are configured on **Admin -> Integrations**, alongside the
WordPress blog connection -- same page, same "test connection before
saving" pattern, same "leave the app password field blank to keep the
existing one" convention.

**Folder browsing (issue #201):** the file listing originally rendered
a folder icon for subfolders but no link -- a board member could see
that "photos" existed but had no way to open it. `?cloud_path=<subpath>`
on `GET /parcels/{id}` now carries the subpath (relative to the
parcel's configured folder root) currently being browsed; folder rows
link into it, and a breadcrumb trail (built server-side as a list of
`{name, cloud_path}` dicts, not string-spliced in the template) lets a
board member jump back to any ancestor level or the root. Download and
upload both take the same `cloud_path` (query param and hidden form
field respectively) so a file picked up two folders deep actually comes
from/goes to that folder, not always the configured root.

`sanitize_browse_subpath()` (`app/parcel_cloud_folders.py`) validates
this query param. It deliberately differs from `sanitize_relative_path()`
above it in one way: an empty result is valid here (it means "the
folder's own root"), where the admin-entered folder path treats empty
as a required-field error. A `..` segment is silently dropped back to
the root rather than raising -- this value only ever originates from a
link Parcella itself generated or a hand-edited URL, and
`_join_dav_path()` (`app/cloud_storage.py`) still rejects `..`
defensively at the point the path actually reaches a WebDAV request,
same "sanitize at ingestion + defensive pass at use" pattern this
module already followed for the configured folder path itself.

**Picking the initial folder path:** the browsing above only ever works
*within* an already-saved `relative_path` -- it never helped choose that
value in the first place, which still had to be hand-typed. `?cloud_pick=1`
(with `?pick_path=<subpath>`, both on `GET /parcels/{id}`) adds a second,
parallel browse mode that lists the Nextcloud account tree from its own
root instead of the parcel's configured folder, **filtered to
directories only** (there's nothing to "pick" about a file). It reuses
`sanitize_browse_subpath()` for `pick_path` (root-relative here, not
folder-relative) and the same breadcrumb-building shape, kept in
entirely separate template context variables (`cloud_picker_*`) so it
never collides with the `cloud_path` state above. A "Use this folder"
button at any level posts straight to the existing, unmodified
`POST /parcels/{id}/cloud-folder` save route -- no new backend route,
no new validation, just a different value arriving at the same door.
Deliberately still server-rendered (full page reload), not a JSON/AJAX
modal, to stay consistent with the browsing pattern above and match
implementation surface to what was actually asked for.

## External contacts' documents (ADR 0097)

A second, simpler consumer of the same connector: a club-wide base
folder (`ClubSetting` `external_contacts_cloud_folder`, set on the
integrations page) holds one hand-made subfolder per external contact.
Each contact picks its subfolder by name. Unlike parcel folders, access
follows the `external_contacts` permission row, not full access only.
See docs/module-external-contacts.md.

## Scheduled cloud backups (`app/cloud_backup.py`, issue #141)

A second, independent consumer of this connector: `Admin -> System ->
Cloud backups` (`/admin/backup/cloud`) lets an admin turn on automatic
uploads of the database + uploads backup (the same zip
`app/backup.py`'s `build_backup_zip()` produces for the manual local
download, issue #117) to a configured folder in this same Nextcloud
connection, on an hourly/daily/weekly/monthly schedule, with a
retention count pruning older backups. Gated on this module being
enabled *and* a Nextcloud connection actually being configured -- shown
as a guided message pointing back here otherwise, not a hard 404. See
[ADR 0055](./ADR/0055-scheduled-cloud-backups.md) for the scheduling
mechanism (an in-process loop, not cron), the retention semantics, and
why `delete_file`/`create_folder` exist on the connector at all.

## Key decisions

**Parcella does not manage who can see a folder's contents.** Read/write
access to the actual files is granted directly in Nextcloud (shares),
independent of and invisible to Parcella. This is a deliberate scope
boundary, not an oversight: **ending a tenancy in Parcella deactivates
the folder *pointer*** (so the next tenant doesn't inherit it in the UI)
**but does not revoke the previous tenants' Nextcloud share.** A board
member has to do that by hand, directly in Nextcloud, today. This is a
known gap -- see "Still to do" below.

**Manual re-linking after a turnover, not automatic reuse.** Same
reasoning as `retired_at` in the inventory module: guessing that a new
tenant should inherit the old folder (or a folder at a derived path)
would be the system assuming intent it doesn't actually have. A board
member sets the new path once the new tenancy is confirmed.

**Quantity of implementation surface matches the actual request:**
list/upload/download/**browse-into-subfolders** covers "browse and get
documents in and out"; nothing about in-app previewing, versioning, or
comment threads was asked for. When issue #201 asked for in-browser PDF
previewing as a follow-up, the answer was still no, deliberately: the
free win (browsers already render PDFs/images natively; the download
route would just need `Content-Disposition: inline` with the real
mimetype instead of forcing an attachment download) is a real future
option, but embedding Nextcloud's own viewer via its Share API was
rejected -- see "Deliberately backend-agnostic" below.

**Deliberately backend-agnostic, even where a Nextcloud-specific
shortcut exists.** Nextcloud has its own web viewer and a Share API
that could produce an embeddable preview link with very little code --
but reaching for it would quietly re-couple this module to Nextcloud
past the `CloudStorageProvider` interface boundary ADR 0033 set up on
purpose. The club explicitly wants Seafile, Google Drive, and
S3-compatible backends to stay realistic future options, not just
theoretically possible. Any new feature here should keep working
through `list_files`/`upload_file`/`download_file`/etc., or through
browser-native capability (like inline PDF rendering), not through a
capability only Nextcloud happens to expose.

## A WebDAV path-encoding bug found while building this

`_join_dav_path()` builds the URL path for a WebDAV request from
folder/file name segments. The first version quoted each **function
argument** as one opaque unit
(`quote(segment, safe="")`) -- correct for a single file or folder
*name*, but wrong when an argument is itself a full relative path like
`"kgv_dokumente/parzellen/G016"`: the internal `/` characters got
percent-encoded into `%2F` right along with the rest of the string, so
requests went to `.../parcels%2FG016` instead of `.../parcels/G016`.

This was non-obvious because Nextcloud's `PROPFIND` didn't error --
`%2F` inside a path segment just made the server treat the whole thing
as one (nonexistent-as-such) name, and depending on the exact
mock/server behavior it could still return *a* response, e.g. by
resolving to a parent collection. The bug surfaced as an unexpected
extra entry in the parsed file listing rather than a clean failure.
Fixed by splitting every argument on `/` before quoting each resulting
path component individually, so multi-segment relative paths and
single file/folder names both encode correctly. Covered by
`test_nextcloud_list_files_parses_propfind_response` in
`tests/test_cloud_storage.py`, which asserts the exact set of returned
entries rather than just "list_files doesn't raise."

## Still to do (v1.1 candidate)

**No reminder or automation to revoke the Nextcloud share when a
tenancy ends.** `deactivate_if_vacant()` only updates Parcella's own
pointer; the actual Nextcloud share (who can open the folder) is left
untouched. A club relying on this module needs a manual process today
("when a tenant leaves, remember to also revoke their Nextcloud share")
that Parcella doesn't currently prompt for. A future version could
surface a checklist item or banner on the tenancy-end flow
(`mitglied_entfernen` / the "remove" action in `app/routers/parcels.py`)
reminding the board member to go do this by hand in Nextcloud, without
Parcella attempting to manage Nextcloud shares directly (which would
need Nextcloud's separate Sharing API and credentials/permissions
scoped beyond WebDAV file access).

**No in-browser preview for PDFs/images.** Raised as a follow-up to
issue #201; deferred, not rejected. `download_file` currently responds
with `Content-Disposition: attachment`, forcing a download instead of
letting the browser render a PDF or image inline -- switching that to
`inline` with the file's real mimetype (instead of the current
`application/octet-stream`) for previewable types would be a small,
backend-agnostic change (no new dependency, works through the existing
interface) whenever this is actually requested again.
