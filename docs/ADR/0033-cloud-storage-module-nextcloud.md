# Cloud storage module (Nextcloud)

**Connector pattern, structured like `app/blog_publisher.py`.** A
narrow `CloudStorageProvider` interface (`test_connection`,
`list_files`, `upload_file`, `download_file`) with `NextcloudProvider`
as the only implementation today -- a future Google Drive or
S3-compatible backend would be a new class, not a change to existing
code. Credentials live in `ClubSettings`, same as SMTP and the
WordPress blog integration: base URL and username in plain text, the
app password Fernet-encrypted via `app.crypto_utils`, and an empty
field on save means "leave the existing value unchanged."

**The folder assignment is scoped to the parcel, not to a single
`MemberParcel` row.** A parcel can have several co-tenants (couples,
families) with separate `MemberParcel` rows for the same lease period,
and they share one folder -- one row per tenancy period, not one per
person. Only one `ParcelCloudFolder` per parcel may be `is_active` at a
time, enforced with a Postgres partial unique index
(`postgresql_where=is_active`), not just application logic.

**Deliberately scoped out of v1: Parcella does not manage who can see
a folder's contents.** That access is granted directly in Nextcloud
(shares), independent of and invisible to Parcella. Ending a tenancy in
Parcella deactivates the *pointer* to the folder (so new tenants moving
in don't inherit it) but does **not** revoke the old tenants' Nextcloud
share -- a board member has to do that by hand, in Nextcloud, today.
Flagged as a good v1.1 candidate: a reminder/checklist item on the
tenancy-end flow prompting the board member to go revoke the share,
rather than silently assuming it happened.

**`deactivate_if_vacant` runs automatically; reconfiguring afterwards
is a deliberate, separate action.** Whenever a `MemberParcel`
assignment ends (`assigned_until` gets set), the parcel's active folder
is deactivated if that was its last remaining resident. Nothing
re-activates or points a new tenant at the old folder automatically --
a board member sets a fresh path once the new tenancy actually starts,
same reasoning as `retired_at` in the inventory module: an automatic
action here would be guessing at intent the system doesn't have.

**No delete, no folder creation, in v1.** The connector only
lists/uploads/downloads. The folder a club points Parcella at is
expected to already exist (usually already shared with the relevant
members in Nextcloud itself); letting board tooling delete files from
someone's personal cloud storage is a bigger, separately-considered
decision than this module needed to make.

**Update:** `delete_file`/`create_folder` were added in
[ADR 0055](./0055-scheduled-cloud-backups.md) (issue #141, scheduled
cloud backups) -- scoped narrowly to that feature's own retention sweep
and destination-folder setup, not a general reversal of the reasoning
above.

**Update (issue #201):** the file listing rendered folders but had no
way to open them -- fixed by adding a browse subpath (`cloud_path`)
threaded through the list/download/upload routes, still going through
`list_files`/`download_file`/`upload_file` on the existing interface.
When richer in-browser previewing (PDFs, images) came up as a natural
next ask, it was deliberately deferred rather than solved via
Nextcloud's own viewer/Share API: the club wants Seafile, Google
Drive, and S3-compatible backends to remain realistic future options,
so anything built here should keep working through the
`CloudStorageProvider` interface (or plain browser capability, like
inline PDF rendering) rather than a capability only Nextcloud happens
to expose. See docs/module-cloud-storage.md for detail.

**A WebDAV path-encoding bug was found and fixed while building
this.** `_join_dav_path` originally quoted each function argument as
one opaque unit (`quote(segment, safe="")`), which is correct for a
single file/folder *name* but wrong for a full relative path like
`"kgv_dokumente/parzellen/G016"` passed as one argument -- the
internal `/` separators got percent-encoded into `%2F` right along
with the rest, so requests went to
`.../parcels%2FG016` instead of `.../parcels/G016`. Nextcloud's PROPFIND
still returned data (querying the parent collection instead of the
target folder), which made the bug non-obvious: it surfaced as an
extra, unexpected entry in the file listing rather than an outright
error. Fixed by splitting every argument on `/` before quoting each
resulting component individually. Caught by
`test_nextcloud_list_files_parses_propfind_response` in
`tests/test_cloud_storage.py`, which asserts the exact set of entries
returned, not just that *some* entries came back.

