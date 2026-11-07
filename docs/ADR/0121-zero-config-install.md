# Zero-config install: localhost-only ports, self-healing entrypoint, generated SECRET_KEY

**Context:** issue #296. Installing the published image took ten commands
(download `.env`, edit passwords/`SECRET_KEY`/`ENVIRONMENT`/SMTP, `mkdir`,
`sudo chown`, a separate `alembic upgrade head`, then `up -d`). kermie's
ask: download `docker-compose.yml`, run `docker compose up -d`, done. Two
supported ways in: `http://localhost` on the machine itself, and HTTPS via
a reverse proxy in production. Nothing reachable from the internet
directly.

Checking every step showed most of them weren't needed:

- `alembic upgrade head` already runs in `docker-entrypoint.sh` on every
  start; the separate command did the same twice.
- SMTP is configured in the admin panel; `load_smtp_configuration()`
  (`app/email_service.py`) reads the database first and the env vars only
  as a fallback.
- `mkdir data/...`: Docker creates missing bind-mount sources itself.

The others hid real issues, and one security bug: the published compose
file published Postgres on `0.0.0.0:5432` with the default password
`changeme`, and defaulted to `ENVIRONMENT=development` (no `Secure`
cookies, no HSTS, SQL echo logging).

## Decision 1: bind to localhost, publish nothing else

- `db` has no `ports:` at all; `web` reaches it over the compose network.
- `web` publishes `127.0.0.1:8000:8000`.
- `ENVIRONMENT` defaults to `production` in the published file
  (`docker-compose.dev.yml` keeps `development`).
- uvicorn runs with `--proxy-headers --forwarded-allow-ips=*` by default.
  That is safe only because of the localhost binding: the README already
  argued this for the override example; now it's the base.

Binding to localhost is what makes `ENVIRONMENT=production` the default
workable. Browsers treat `http://localhost` as a secure context and send
`Secure` cookies there, so the local trial works. The awkward case,
plain HTTP to a LAN IP where a `Secure` cookie would silently break login,
can't happen with the default because the port isn't reachable from the
LAN. Anyone who opens it up does so explicitly via an override.

Docker's own iptables rules bypass `ufw`/firewalld, so "the firewall only
allows 80/443" never protected a `0.0.0.0` binding. Not publishing is the
only reliable default.

## Decision 2: the image fixes bind-mount ownership itself

ADR 0077 Decision 3 documented a `sudo chown 1000:1000 data/uploads` step
and deferred the alternative. This ADR does the alternative: the
`Dockerfile` no longer sets `USER appuser`, so the entrypoint starts as
root. It `chown`s `/app/app/static/uploads` and `/app/secrets` to
appuser (only when the top level is wrong, so a large uploads folder isn't
walked each start). Then it re-executes itself via `setpriv --reuid
--regid --init-groups` (util-linux, already in the base image), setting
`HOME`. Everything else (DB wait, migrations, uvicorn) runs as appuser
exactly as before. This is the same pattern as the official Postgres
image. A container started as non-root (`--user`) skips the root phase.

Side effect: `docker compose exec web ...` now opens a root shell by
default; use `exec -u appuser` where it matters.

## Decision 3: generate SECRET_KEY into a file, re-key old installs

`app/secret_bootstrap.py`, called from the entrypoint:

- `SECRET_KEY` set in the environment: used as-is, nothing else happens.
- Empty: `ensure` (before migrations) creates `/app/secrets/secret_key`
  (`secrets.token_urlsafe(48)`, `O_EXCL`, mode 0600, folder 0700),
  bind-mounted from `./data/secrets/`. `app/config.py` reads that file
  whenever `SECRET_KEY` is empty, and still refuses to start in
  production if neither exists.
- `rekey` (after migrations) re-encrypts every `club_settings` value that
  decrypts with the public default key. Those are installs that ran the
  old file without `.env`, i.e. on `ENVIRONMENT=development` with the
  default key. It is idempotent and runs on every start, so a crash
  between creating the key and re-keying can't strand the values.
  Sessions and 24h API JWTs signed with the old key become invalid:
  everyone logs in once more.

**Why a file and not the database:** the key encrypts values in that same
database. Storing it next to them would make every DB dump (including the
app's own cloud backup archive) self-decrypting. For the same reason the
key file is not added to the app's backup archive; the docs say to back
up the whole `data/` folder.

**Why the secret folder isn't under `app/static/`:** everything there is
served publicly by `StaticFiles`.

**Rejected: refuse to start old installs until the admin sets a key.**
Safe, but a manual step on update for exactly the people who never
touched `.env` -- the opposite of this change's point.

## Backward compatibility and versioning

Installs with a `.env` that sets `SECRET_KEY`/`ENVIRONMENT` behave as
before. Two behaviour changes for installs that adopt the new file:

- the app port is localhost-only; LAN access needs a `ports: !override`;
- installs that relied on the dev default switch to production, with a
  generated key.

Nothing is removed and no manual migration is required, so this is a
MINOR release.

**`docker compose pull` does not update the compose file** (ADR 0076).
Existing installs keep publishing 5432 until they re-download it, so the
release notes and the README's update section say so explicitly.

## Supersedes (without editing)

ADR 0077 Decision 3 (document a manual `chown`). The rest of ADR 0077
stands.
