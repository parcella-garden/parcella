# Operations

Practical commands and troubleshooting for day-to-day operation.

## Basic Docker commands

```bash
# Build the container (needed after changes to requirements.txt or Dockerfile)
docker compose build web

# Start the container
docker compose up -d

# Restart the container (sufficient for pure Python code/template changes,
# since uvicorn runs in --reload mode)
docker compose restart web

# View logs
docker compose logs web --tail=30

# Check status
docker compose ps
```

## Database migrations

```bash
# Apply migrations (also runs automatically on container startup)
docker compose run --rm --entrypoint alembic web upgrade head

# Generate a new migration after a model change
docker compose run --rm web alembic revision --autogenerate -m "Short description"

# Check the current state
docker compose run --rm --entrypoint alembic web current

# Check all "heads" (in case of a "Multiple head revisions" error)
docker compose run --rm --entrypoint alembic web heads
```

**Important:** revision names (`revision: str = "..."`) must stay under
32 characters -- the `alembic_version` table has a `VARCHAR(32)` column.

**On a "Multiple head revisions" error:** usually caused by two migrations
created in parallel with the same `down_revision`. Fix: delete one of the
two migration files, and if necessary correct the `alembic_version` entry
in the DB directly:
```bash
docker compose exec db psql -U parcella -c "UPDATE alembic_version SET version_num = '<correct_revision>' WHERE version_num = '<wrong_revision>';"
```

## SMTP setup

SMTP credentials can be entered under `/admin/settings` (the database
takes precedence) or via the `.env` file (fallback if DB values are
missing):

```
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=user@example.com
SMTP_PASSWORD=...
SMTP_FROM=verein@example.com
SMTP_TLS=true
```

The SMTP password is stored encrypted in the database (see
[Architecture Decisions](./ADR/0006-passwords-hashing-vs-encryption.md)). An SMTP
server can safely be configured even while the app is still running
under `localhost` -- sending mail is an outbound connection from the
container to the mail server, independent of how the app itself is
reached.

### Email log

`Admin -> Email log` (`/admin/email-log`, issue #270, [ADR
0120](./ADR/0120-email-log-smtp-result-only.md)) lists every email
Parcella tried to send: date/time (in the club's time zone), recipient,
subject, attachment count, and **Sent** or **Failed** with the error. It
filters by status and by recipient, 50 per page; `GET /api/v1/email-log`
returns the same for the ADMIN role.

"Sent" means the SMTP server accepted the message. A bounce that comes
back later (mailbox full, address gone) lands in the sending mailbox and
is **not** shown here. "Failed" covers what the server refused straight
away (unknown recipient on the club's own server, authentication or
relay errors), a server that couldn't be reached, and "SMTP not
configured".

Entries are deleted after `Admin -> Settings -> Email log` days (default
90, 1-3650), on regular site use at most once an hour.

## Backups & restore

A system admin can download a full backup on demand from `/admin/`
("Download backup" -- see
[ADR 0053](./ADR/0053-admin-backup-download-only.md)). It's a zip
laid out like the install's `./data/` folder (issue #327, ADR 0134):
`data/postgres/parcella.sql` (a one-click `pg_dump`, plain SQL, readable
text -- the consistent form of the database files), `data/uploads/` (the
branding logo, announcement images, user avatars, and process files kept
locally under `uploads/private/` -- ADR 0136) and
`data/secrets/secret_key` (the encryption key in use). Nothing is ever written to server disk, so
there's no backup file to find or clean up on the server itself; the
downloaded `.zip` is the only copy, and it's the admin's responsibility
to store it somewhere safe. **It holds the key to the stored
SMTP/website/cloud passwords**, so treat it like those passwords.

**Automatic backups to a connected cloud solution:** `Admin -> System ->
Cloud backups` (`/admin/backup/cloud` -- see
[ADR 0055](./ADR/0055-scheduled-cloud-backups.md)) can upload that same
zip to a folder in your connected Nextcloud on a schedule
(hourly/daily/weekly/monthly), keeping only the newest N backups and
pruning older ones automatically. Requires the `cloud_storage` module
enabled and a working Nextcloud connection under **Admin ->
Integrations** first. No Linux cron involved -- the schedule is an
in-process check every 15 minutes, same style as the update-check and
FreeScout conversation polling loops.

**Restoring, the normal way:** a system admin can also upload that same
zip back through `/admin/backup/restore` ("Restore from backup" -- see
[ADR 0054](./ADR/0054-admin-restore-from-backup.md)) and restore both
the database and `app/static/uploads/` in one step -- or, from the
Cloud backups page, restore directly from any backup already sitting
in the cloud, without downloading and re-uploading it by hand. Both are
destructive, irreversible actions -- they replace the entire current
database and every uploaded file with the backup's contents -- so both
require typing the literal confirmation phrase `RESTORE` before running
anything. If you want to be able to undo a restore, download a fresh
backup of the current state *first*.

**Restoring manually, e.g. when the app itself is unreachable** (container
won't start, admin panel broken) and the UI isn't an option:

The zip is laid out like the install's `./data/` folder (issue #327):
`data/postgres/parcella.sql` (the database as a dump -- not the raw
`data/postgres/` files, which can't be copied safely while the database
runs), `data/uploads/` and `data/secrets/secret_key`. Backups made before
that have the flat layout `parcella-backup-<time>.sql`, `uploads/`, no key;
the admin restore accepts both.

```bash
unzip parcella-backup-20260730-143000.zip -d restore/
docker compose exec -T db psql -U parcella -d parcella < restore/data/postgres/parcella.sql
```

Uploads and the key are plain host directories (bind-mounted under
`./data/`, no `docker cp` needed) -- for a published-image deploy:

```bash
cp -r restore/data/uploads/. data/uploads/
cp restore/data/secrets/secret_key data/secrets/secret_key   # then: docker compose restart web
```

Copy the key only when this server's stored passwords should come from
the backup (a move to a new server) and you didn't set `SECRET_KEY` in
`.env` -- a key in `.env` always wins.

For a dev/source checkout, the equivalent path is `app/static/uploads/`
(already live-mounted via `docker-compose.dev.yml`'s `./app` bind mount).

**Warning:** the backup was generated with `--clean --if-exists`, so the
SQL script itself contains `DROP ... IF EXISTS` statements ahead of each
`CREATE` -- restoring it drops existing objects before recreating them.
Never run this against a live database whose current data you still
need -- restore into an empty database (or a throwaway one) instead,
then swap it in deliberately. The in-app restore path guards against
this with the confirmation phrase; the manual command above has no such
guard, so treat it with the same care.

Neither restore path runs `alembic upgrade head` for you -- see the next
point, which applies identically whichever path you use.

**What the backup does *not* cover -- read this before relying on one:**

- **Encrypted fields travel with the key (ADR 0134).** SMTP/WordPress/
  Nextcloud credentials are stored encrypted with a key derived from
  `SECRET_KEY` (`app/crypto_utils.py`). The backup carries that key, and
  restoring it on an instance with a different key re-encrypts those
  settings with the instance's own key -- no restart, nobody logged out.
  Only a *manual* restore (`psql` + `cp`, below) skips that step: there,
  either copy `secrets/secret_key` from the zip to `data/secrets/` before
  starting the container, or re-enter the credentials afterward.
- **Restoring an older backup into a newer Parcella version:** should
  work, but isn't automatic. Restore the dump, then run
  `docker compose run --rm --entrypoint alembic web upgrade head` --
  migrations are additive and forward-only, so as long as no migration
  file has been rewritten after release (this project never does that),
  Alembic will bring the restored schema up to whatever version you're
  currently running. The one sharp edge: a migration that does a raw
  `ALTER TYPE ... ADD VALUE` for an enum has to get the value's *name*
  casing exactly right (see the enum sharp edge in
  [CLAUDE.md](../CLAUDE.md)) -- this has been gotten wrong once in this
  codebase's history, and Postgres has no way to undo a bad
  `ADD VALUE` afterward.
- **Test the restore path itself, occasionally, on a throwaway
  database** -- rather than assuming a backup is good just because the
  download succeeded. A backup you've never restored is a hypothesis,
  not a guarantee.

## First login

On the very first startup (empty `users` table), an admin account is
created automatically:

- Email: `admin@parcella.local`
- Password: `admin1234`

This account is flagged `must_change_password`, so the first login lands
on the change-password form and every other page redirects back to it
until a new password is set. The REST API refuses to issue a token for
the account in that state as well -- see
[ADR 0065](./ADR/0065-credential-and-deployment-hardening.md).

## Security-relevant settings

- **`SECRET_KEY`: generated unless you set one (ADR 0121).** It signs
  session cookies and the 24-hour login JWTs, and encrypts stored
  SMTP/Nextcloud/WordPress passwords. Personal API tokens (`pct_...`,
  ADR 0126) don't depend on it: they're stored as a hash and survive a
  key change. With `SECRET_KEY` empty (the published compose
  file's default), the entrypoint writes a random key to
  `./data/secrets/secret_key` (mode 0600) on first start and the app
  reads it from there. An explicitly set `SECRET_KEY` always wins. With
  `ENVIRONMENT` set to anything other than `development`, the app still
  refuses to start on the built-in default key (published in the public
  repository). Installs that used to run on that default get their
  stored passwords re-encrypted with the generated key on every start
  (`python -m app.secret_bootstrap rekey`, idempotent).

  Changing the key later logs everyone out and makes already-encrypted
  settings unreadable. Since issue #327 the key is part of every backup
  (download and cloud, ADR 0134), so a restore re-encrypts the stored
  settings onto whatever key the restoring instance uses.

- **`ENVIRONMENT=production` is the published compose file's default.**
  It is what makes the session and CSRF cookies `Secure` (HTTPS-only;
  browsers make an exception for `http://localhost`) and what enables
  the HSTS response header. `docker-compose.dev.yml` keeps
  `development`.

- **Nothing is published beyond localhost.** The published compose file
  binds the app to `127.0.0.1:8000` and doesn't publish Postgres at all.
  Docker writes its own iptables rules, so a published port bypasses
  `ufw`/firewalld -- a firewall doesn't make `0.0.0.0` bindings safe.

- **Run behind the reverse proxy with forwarded headers.** Login
  throttling and the public signup API's rate limit key on the client
  IP. Behind a proxy, every request appears to come from the proxy
  unless uvicorn runs with `--proxy-headers` (the published compose
  file's default command) *and* the proxy sets the header:

  ```nginx
  proxy_set_header X-Forwarded-For $remote_addr;
  proxy_set_header X-Forwarded-Proto $scheme;
  ```

  `$remote_addr`, not nginx's usual `$proxy_add_x_forwarded_for`: the
  latter keeps whatever `X-Forwarded-For` the visitor sent and appends
  the real address, and with `--forwarded-allow-ips=*` uvicorn takes
  the *leftmost* entry -- the visitor's own claim. Anyone could then
  send a fresh made-up IP with every request and never hit a login or
  form limit (audit 2026-11-26). Overwriting the header leaves exactly
  one entry, the real one.

  `--proxy-headers` alone only trusts forwarded headers from
  127.0.0.1. A proxy on the Docker host connects through the Docker
  network gateway (e.g. `172.19.0.1`), so uvicorn also needs
  `--forwarded-allow-ips` -- otherwise every visitor shares the
  gateway's address and the throttles become one global bucket: 30
  failed logins from anyone block all logins, 10 against one address
  lock that account for everybody (security audit 2026-10-19, hit on the
  reference installation). Check with
  `docker compose logs web | grep -oE '[0-9.]+:[0-9]+ - "' | sort | uniq -c`:
  real client addresses should show up, not just the gateway.

  Only trust forwarded headers when a trusted proxy really is in front:
  a directly-exposed app would then believe whatever IP a client claims.
  `--forwarded-allow-ips=*` (the published compose file's default) is
  fine only because the port is published on `127.0.0.1` *and* the
  proxy overwrites `X-Forwarded-For` (above); if you ever
  publish it more widely, override `command:` and list the proxy's
  address instead.

- **Content Security Policy.** Everything loads from the app's own
  origin: Bootstrap, Bootstrap Icons, EasyMDE, SortableJS and Chart.js
  are self-hosted under `app/static/vendor/<package>@<version>/`
  (`app/security_headers.py` allows no CDN). A new vendor library goes
  there too, in a new versioned folder.

## Common failure patterns

| Symptom | Likely cause |
|---|---|
| Prod: `docker compose pull` says nothing to pull, `up -d` doesn't actually update | `docker-compose.yml` was hand-edited (e.g. `web:` switched to `build:` for a reverse-proxy tweak) instead of putting customizations in a `docker-compose.override.yml` -- see ADR 0076, ADR 0077, and the README's Production section. This fails **silently**: no error, just no update. |
| `invalid input value for enum` | Enum value in Python != enum value in DB (case mismatch) |
| `MultipleResultsFound` | `scalar_one_or_none()` used on a query that can return multiple hits |
| `MissingGreenlet` on start/restart | `scalar_one_or_none()` on a table with multiple rows (e.g. a user-count check) |
| `MissingGreenlet` on a single page | Lazy-load on a freshly created object without eagerly loaded relationships |
| CSV import: every row shows "error" | Delimiter mismatch (Excel may save with comma instead of semicolon) |
| Dev build: root-owned files in the project folder | Container ran as root; set `UID`/`GID` in `.env` before `docker compose -f docker-compose.dev.yml build` (only affects a locally-built image -- the published image's entrypoint fixes ownership of its data folders and drops to uid/gid 1000, see ADR 0121) |
| Every form POST answers 403 "Security check failed" | CSRF cookie missing or stale -- reload the page; if it persists on a fresh page, check that the reverse proxy isn't stripping cookies |
| A new form works locally but 403s for everyone else | The form is missing `{{ csrf_field() }}` (see ADR 0064) |
| Login answers 429 | Too many failed attempts from this address; wait 15 minutes (see ADR 0065) |
| App won't start: "SECRET_KEY is still the built-in development default" | `ENVIRONMENT` is not `development` and no real `SECRET_KEY` is set |
