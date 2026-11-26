# Admin backup: on-demand download only, no server-side storage

**Context:** Issue #117, "add a backup possibility to administration
panel" -- previously there was no backup feature of any kind (no
`pg_dump` code, no documented procedure). Three real design choices had
to be made, none of them obvious in hindsight, so they're recorded here
rather than left for a future maintainer to reverse-engineer.

**Decision 1: direct download, nothing ever written to server disk.** An
admin clicks a button; the server runs `pg_dump` and returns the result
straight to the browser as a file attachment (`app/routers/admin.py`,
`backup_download`). No backup file is ever saved to a server directory or
volume. The alternative -- store backups server-side with a retention
policy and a "past backups" list in the admin panel -- was considered and
rejected: this app's database is the single most sensitive dataset in the
system (every member's personal data plus club finances in one file), and
a stored-on-server design multiplies the ways that data can leak (wrong
file permissions, a misconfigured volume mount, a forgotten cleanup job
leaving years of backups sitting around). Download-only means there is
nothing an attacker who compromises the `web` container's filesystem can
find after the fact -- the data only ever exists in the admin's own
browser download and wherever they choose to store it next.

**Decision 2: gated by `require_system_admin` only, no module flag.**
Every other pure admin-panel operational action in this app (the update
check-now button, sample-data add/remove) is gated the same way, per
`app/permissions.py`'s explicit statement that the admin panel is
carved out of the module/permission system entirely and "stay[s]
admin/board-only regardless of group configuration." A backup covering
the whole database is exactly this category of feature, not a
per-association-configurable module area, so it gets no new
`modul_backup`-style flag in `app/module_flags.py`.

**Decision 3: plain SQL (`pg_dump`'s default format), not custom
format.** Custom format (`-F c`) was the initial choice -- built-in
compressed, restorable selectively via `pg_restore` -- but it produces a
binary file with no readable content, which surprised the admin who
actually downloaded one (reasonably: `pg_dump` ships as plain SQL by
default, and this app's admins are club board members, not necessarily
DB experts). Plain SQL means the file can be opened in a text editor and
restored with a plain `psql`, at the cost of no built-in compression and
no selective restore -- both worth giving up for a feature whose whole
point is "an admin can understand and use this without extra tooling
knowledge." `--clean --if-exists` is passed to `pg_dump` so the emitted
script includes `DROP ... IF EXISTS` ahead of each `CREATE`, keeping it
restorable directly into a database that already has the same objects
(the equivalent of `pg_restore --clean --if-exists`, but embedded in the
script itself since plain SQL has no separate restore-time flags).

**Decision 4: the download bundles `app/static/uploads/` alongside the
SQL dump, as a zip.** A DB-only backup leaves dangling references: the
branding logo and announcement images are stored as files under
`app/static/uploads/`, referenced by filename from `ClubSetting`/
`Announcement` rows, but the file bytes themselves aren't in the
database. Restoring the DB alone into a fresh instance would show
broken images. `backup_download` walks `UPLOAD_DIR` (reused from
`app/branding.py`, not redefined) and adds every file it finds under an
`uploads/` prefix in the zip -- generic by construction, so any future
upload directory added under that same tree is included automatically
without this endpoint needing to know about it by name.

**Amended by issue #415 (pending kermie's OK):** the dump and the zip no
longer live in memory (a big club's backup held the dump twice, plus the
zip, in RAM). `build_backup_zip_file()` writes both to `tempfile.mkstemp`
files (mode 0600, the container's own `/tmp`, never a volume), and the
download streams the zip and deletes it once sent; the dump is deleted
as soon as it's zipped. Decision 1's point stands -- no backup is ever
*kept* on the server -- but for the seconds a download takes, it is on
the container's disk, and a process killed in exactly that window
leaves a file in `/tmp` until the container is recreated.

**Known limitation, not solved by this feature: encrypted fields don't
travel.** SMTP/WordPress/Nextcloud credentials are stored encrypted
with a key derived from `SECRET_KEY` (`app/crypto_utils.py`), which is
`.env`-only, deliberately outside the database and outside this backup.
Restoring a dump into an instance with a *different* `SECRET_KEY`
leaves those fields undecryptable garbage -- see
[Operations](../operations.md#backups--restore) for what that means in
practice. This wasn't solved here because bundling `SECRET_KEY` into an
otherwise access-controlled-only-by-`require_system_admin` download
would hand out the one secret that makes every other encrypted value
recoverable, in the same file people are told to "store somewhere
safe" -- a materially bigger risk than the inconvenience of re-entering
those credentials after a restore onto new infrastructure.

**Mechanics, for completeness:** `pg_dump` runs from inside the `web`
container against the `db` service over the network (same pattern as
Alembic migrations already running from `web`), using connection details
parsed from `settings.database_url`. The `postgresql-client-16` package
is installed via the PGDG apt repository, pinned to the exact same major
version as the `db`/`db_test` services' PostgreSQL 16.

**Correction (added when building restore, ADR 0054):** this originally
installed the plain `postgresql-client` meta-package from Debian
trixie's own repo (v17), reasoning that `pg_dump` is backward-compatible
with older servers -- true for *dumping*, but not sufficient once
restore existed too: a v17 `pg_dump` embeds a `SET transaction_timeout
= 0;` preamble line (a v17-only GUC) that a v16 server's `psql` rejects
outright. Pinning to the exact matching version via PGDG avoids this
whole class of version-skew issue rather than special-casing one
symptom of it. The database password is passed to the subprocess via
its environment (`PGPASSWORD`),
never as a CLI argument or connection-string URI, so it never appears in
a process listing. The full dump is written to a temporary file (since
#415; before that, buffered in memory) and only sent once `pg_dump` has
exited successfully -- deliberately not streamed from `pg_dump`, so a failed dump
never partially streams a corrupt file that looks like a successful
download.

**Out of scope:** there is no restore-from-UI feature. Restoring a
downloaded backup is a deliberately manual, `psql`-on-the-command-line
operation (see [Operations](../operations.md#backups--restore)) --
building a restore-from-upload feature would mean accepting an arbitrary
SQL/binary file from an admin's browser and feeding it to `psql`/
`pg_restore` against the live database, a much larger blast-radius
feature than this issue asked for.

**Update:** superseded for restore specifically by
[ADR 0054](./0054-admin-restore-from-backup.md), which reverses this one
paragraph (and only this paragraph) after the user weighed the tradeoff
directly -- see that ADR for the safeguards judged sufficient to accept
it. Everything else in this ADR still stands.
