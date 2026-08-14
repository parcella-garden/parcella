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

## Backups & restore

A system admin can download a full backup on demand from `/admin/`
("Download backup" -- see
[ADR 0053](./ADR/0053-admin-backup-download-only.md)). It's a zip
containing a one-click `pg_dump` (plain SQL, readable text) plus
everything under `app/static/uploads/` (the branding logo, announcement
images, user avatars) and `app/private_uploads/ticket_attachments/`
(locally-stored ticket attachments -- see the ADR on the Nextcloud
fallback) -- nothing is ever written to server disk, so there's no backup
file to find or clean up on the server itself; the downloaded `.zip` is
the only copy, and it's the admin's responsibility to store it
somewhere safe.

**Automatic backups to a connected cloud solution:** `Admin -> System ->
Cloud backups` (`/admin/backup/cloud` -- see
[ADR 0055](./ADR/0055-scheduled-cloud-backups.md)) can upload that same
zip to a folder in your connected Nextcloud on a schedule
(hourly/daily/weekly/monthly), keeping only the newest N backups and
pruning older ones automatically. Requires the `cloud_storage` module
enabled and a working Nextcloud connection under **Admin ->
Integrations** first. No Linux cron involved -- the schedule is an
in-process check every 15 minutes, same style as the update-check and
ticket-mailbox polling loops.

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

```bash
unzip parcella-backup-20260730-143000.zip -d restore/
docker compose exec -T db psql -U parcella -d parcella < restore/parcella-backup-20260730-143000.sql
cp -r restore/uploads/. app/static/uploads/
cp -r restore/ticket_attachments/. app/private_uploads/ticket_attachments/
```

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

- **Encrypted fields don't travel.** SMTP/WordPress/Nextcloud
  credentials are stored encrypted with a key derived from `SECRET_KEY`
  (`app/crypto_utils.py`), which lives only in `.env`, deliberately
  outside the database and outside this backup. Restore a dump into an
  instance whose `SECRET_KEY` differs from the one that created it, and
  those fields decrypt to garbage -- you'll need to re-enter that
  handful of credentials by hand afterward. Keep a copy of `.env`
  (or at least `SECRET_KEY`) alongside your backups if you ever expect
  to restore onto different infrastructure.
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

- **`SECRET_KEY` is mandatory outside development.** With
  `ENVIRONMENT` set to anything other than `development`, the app
  refuses to start while `SECRET_KEY` is still the built-in default
  (that value is published in the public repository, and it signs
  session cookies, signs API tokens, and encrypts stored SMTP/Nextcloud/
  WordPress passwords). Generate one with:

  ```bash
  python -c 'import secrets; print(secrets.token_urlsafe(48))'
  ```

  Changing it later logs everyone out and makes already-encrypted
  settings unreadable -- keep it with your backups (see ADR 0006/0053).

- **Set `ENVIRONMENT=production` on any real installation.** Beyond the
  key check, it is what makes the session and CSRF cookies `Secure`
  (HTTPS-only) and what enables the HSTS response header.

- **Run behind the reverse proxy with forwarded headers.** Login
  throttling and the public signup API's rate limit key on the client
  IP. Behind a proxy, every request appears to come from the proxy
  unless uvicorn runs with `--proxy-headers` *and* the proxy sets the
  header:

  ```nginx
  proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
  proxy_set_header X-Forwarded-Proto $scheme;
  ```

  Only enable `--proxy-headers` when a trusted proxy really is in front:
  a directly-exposed app would then believe whatever IP a client claims.

- **Content Security Policy.** Bootstrap and Bootstrap Icons load from
  `cdn.jsdelivr.net`, which is pinned in the policy
  (`app/security_headers.py`). Serving those assets from somewhere else
  -- or self-hosting them -- means editing the policy, otherwise the
  browser silently refuses to load them.

## Common failure patterns

## Common failure patterns

| Symptom | Likely cause |
|---|---|
| `invalid input value for enum` | Enum value in Python != enum value in DB (case mismatch) |
| `MultipleResultsFound` | `scalar_one_or_none()` used on a query that can return multiple hits |
| `MissingGreenlet` on start/restart | `scalar_one_or_none()` on a table with multiple rows (e.g. a user-count check) |
| `MissingGreenlet` on a single page | Lazy-load on a freshly created object without eagerly loaded relationships |
| CSV import: every row shows "error" | Delimiter mismatch (Excel may save with comma instead of semicolon) |
| Docker: root-owned files in the project folder | Container ran as root; set `UID`/`GID` in `.env` (see `docker-compose.yml`) |
| Every form POST answers 403 "Security check failed" | CSRF cookie missing or stale -- reload the page; if it persists on a fresh page, check that the reverse proxy isn't stripping cookies |
| A new form works locally but 403s for everyone else | The form is missing `{{ csrf_field() }}` (see ADR 0064) |
| Login answers 429 | Too many failed attempts from this address; wait 15 minutes (see ADR 0065) |
| App won't start: "SECRET_KEY is still the built-in development default" | `ENVIRONMENT` is not `development` and no real `SECRET_KEY` is set |
