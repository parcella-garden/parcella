# Rename docker-compose.prod.yml to docker-compose.yml; bind-mount all runtime data under ./data/

**Context:** two separate but related pains, both traced back to the same
root cause -- the published-image compose file was never named what
Compose actually looks for by default.

1. **Every command needs `-f docker-compose.prod.yml`, forever.** ADR 0076
   already documents one real incident this caused: kermie's own prod
   instance stayed silently on v1.0.6 after a hand-edited compose file
   broke `pull`, precisely because the non-default filename meant nothing
   in the documented flow (or the admin panel's own update notice) could
   ever detect the divergence. Fixing *that* incident meant teaching
   people to pass a *second* explicit `-f` for a
   `docker-compose.override.yml` too -- more flags to remember, not fewer.
2. **A real, currently-live data-loss bug**, found while chasing #1:
   `app/static/uploads/` (logos, avatars, announcement images) and
   `app/private_uploads/ticket_attachments/` have never had a volume mount
   in `docker-compose.prod.yml`. Every redeploy has silently discarded
   them -- masked so far only by the fact that the manual/cloud backup
   feature (`app/backup.py`) happens to bundle both directories anyway,
   which is a mitigation, not a fix.

Kermie's ask, verbatim: install and update should be "download one
`docker-compose.yml` file... besides this file, there shall just be one
folder" -- i.e. zero flags, one data directory, nothing else to think
about.

## Decision 1: rename, don't just add env-var sugar

`docker-compose.prod.yml` -> `docker-compose.yml` (Compose's own
default-discovered filename). The existing `docker-compose.yml`
(dev/build-from-source flow) -> `docker-compose.dev.yml`.

This **inverts** which flow gets the zero-flag default -- deliberate:
self-hosters running the published image vastly outnumber contributors
building from source, and contributors are expected to pass one extra
flag (`run_tests.sh`, `CONTRIBUTING.md`, `CLAUDE.md`'s dev loop, and the
README's dev quick-start were all updated to `-f docker-compose.dev.yml`
as part of this change -- they previously worked *by accident*, relying
on Compose's default-file-discovery landing on the dev file only because
nothing else claimed that name).

**Bonus, discovered while implementing this:** because the base file is
now named `docker-compose.yml`, Compose auto-merges a
`docker-compose.override.yml` sitting next to it with **zero** `-f`
flags on any command -- confirmed experimentally (`docker compose config`
with just the two default-named files present resolves the merge with no
flags at all). This retires the entire "add a second `-f` for your
override file" caveat ADR 0076 had to teach.

**Rejected alternative:** set `COMPOSE_FILE` in `.env` instead of
renaming. Considered for the dev-flow fix specifically and rejected --
`.env` is exactly the file self-hosters copy from `.env.example` into
their own deployment folder too; a stray `COMPOSE_FILE` value leaking
across contexts via copy-paste is an action-at-a-distance risk explicit
`-f` flags on `run_tests.sh`/docs don't have.

## Decision 2: one `./data/` folder, three bind mounts, no named volume

```yaml
services:
  db:
    volumes:
      - ./data/postgres:/var/lib/postgresql/data
  web:
    volumes:
      - ./data/uploads:/app/app/static/uploads
      - ./data/ticket_attachments:/app/app/private_uploads/ticket_attachments
```

The named volume `gartenverein_postgres_data` is dropped from the prod
file entirely. Named volumes are opaque (`docker volume inspect` needed
just to find them on disk) -- exactly why kermie's own box had already
ended up hand-migrated to a `./postgres_data` bind mount before this
change (ADR 0076). Bind-mounting by default retires that whole class of
override for new installs; his own override's `db.volumes` clause is now
redundant and can be dropped (kept only if a *different* host path than
the new default is wanted).

`docker-compose.dev.yml` is untouched -- its bind-mounted source dirs and
named Postgres volume stay exactly as they were; it was never in scope
for this redesign.

## Decision 3: the web image's non-root user needs pre-created, correctly-owned directories

The published `web` image runs as a fixed non-root `appuser` (uid/gid
1000, `Dockerfile`), baked in at CI build time with no `--build-arg`
override. Docker auto-creates a missing bind-mount source directory
`root:root 0755` on the host -- mode 0755 gives non-owners no write bit,
so a fresh `./data/uploads` would `PermissionError` on the very first
upload. Postgres's own official image self-heals this (its entrypoint
chowns before dropping privileges); this project's image does not.

**Chosen fix: document a pre-`up` step** (`mkdir -p
./data/{uploads,ticket_attachments} && sudo chown -R 1000:1000
./data/uploads ./data/ticket_attachments`), in both the README's
production flow and the migration doc. **Rejected for now:** changing
the entrypoint to start as root and drop privileges after chowning, like
Postgres does -- a real option, but a bigger and separate change to the
image itself, not bundled into a docs/compose-layout change.

## Migration path for existing installations

Existing installs (a named `gartenverein_postgres_data` volume, or
kermie's already-hand-migrated `./postgres_data` bind mount, plus
never-mounted uploads/attachments living only in a container's writable
layer) need a one-time manual migration to avoid data loss --
**especially** the uploads/attachments, which have no volume mount today
and are only ever present in the currently-running container. New file:
[MIGRATION-NOTE-DATA-LAYOUT.md](../../MIGRATION-NOTE-DATA-LAYOUT.md),
following the same numbered-steps, backup-first, "new install needs
nothing" structure as the project's existing Alembic-adoption precedent
(`MIGRATION-NOTE.md`).

## Versioning

This is a **MAJOR** version bump under the project's semver discipline:
the documented download URL changes (`docker-compose.prod.yml` ->
`docker-compose.yml`), and existing installs require a manual migration
step to avoid losing data. The actual version number is a release-time
decision, not made here.

## Not solved here

- **No `.dockerignore` exists anywhere in the repo.** `COPY . .` in the
  `Dockerfile` copies the entire build context -- including `.git/` --
  into every locally-built dev image. Unrelated to this ADR's scope, but
  surfaced while researching it and worth a follow-up so it isn't lost.
- **The appuser ownership gotcha** is worked around with documentation,
  not an entrypoint fix (see Decision 3). A future change could make the
  image self-heal ownership the way Postgres's official image does.

## Supersedes (without editing)

ADR 0068 and ADR 0076 both describe the now-renamed
`docker-compose.prod.yml` and, in ADR 0076's case, the then-missing-mount
assumptions this ADR fixes. Both remain accurate as history of what was
true when written; this ADR is the current state going forward.
