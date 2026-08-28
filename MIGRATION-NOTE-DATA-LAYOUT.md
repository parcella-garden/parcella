# Migrating to the ./data/ runtime layout -- note for existing installations

As of this version, `docker-compose.prod.yml` has been renamed to
`docker-compose.yml` (so a bare `docker compose pull && docker compose up
-d` works with no `-f` flag, ever), and its Postgres/uploads/ticket-
attachments storage moved from scattered/missing mounts to one tidy
`./data/` folder next to the compose file. Existing installations need a
**one-time manual migration** to move data into the new layout.

**Do this before your next `pull`/`up` cycle, not after.** Uploads and
ticket attachments have never had a volume mount in the old
`docker-compose.prod.yml` -- they only exist inside the *currently
running* container's writable layer. If that container is already gone
(e.g. `docker compose down --rmi all` or similar), that data is already
lost; this migration can't recover it.

## Before anything: back up

```bash
docker compose -f docker-compose.prod.yml exec -T db \
  pg_dump -U parcella -d parcella --clean --if-exists > backup-before-migration.sql
```

(Or use the admin panel's "Download backup" button -- same effect, and it
also bundles uploads/ticket attachments.)

## One-time steps

1. Stop the running stack (don't remove containers/volumes yet):

   ```bash
   docker compose -f docker-compose.prod.yml stop
   ```

2. Create the new data folders, owned by the right user. Postgres's
   official image self-heals ownership; the app's own image does not
   (it runs as a fixed non-root uid/gid 1000 with no chown step) --
   pre-create and own these two:

   ```bash
   mkdir -p ./data/postgres ./data/uploads ./data/ticket_attachments
   sudo chown -R 1000:1000 ./data/uploads ./data/ticket_attachments
   ```

3. Copy your existing Postgres data into `./data/postgres`. Which command
   depends on what your current install already looks like:

   - **If you're already bind-mounting `./postgres_data`** (per ADR 0076
     -- you have a `docker-compose.override.yml` with a `db.volumes`
     entry): just move the directory:

     ```bash
     mv ./postgres_data/* ./data/postgres/
     ```

   - **If you're still on the original named volume**
     (`gartenverein_postgres_data`, never customized):

     ```bash
     docker run --rm \
       -v gartenverein_postgres_data:/from \
       -v "$(pwd)/data/postgres:/to" \
       alpine sh -c "cp -a /from/. /to/"
     ```

4. Copy uploads and ticket attachments out of the old container -- this
   is the *only* existing copy of this data, since it has never had a
   volume mount:

   ```bash
   docker compose -f docker-compose.prod.yml up -d web
   CID=$(docker compose -f docker-compose.prod.yml ps -q web)
   docker cp "$CID":/app/app/static/uploads/. ./data/uploads/
   docker cp "$CID":/app/app/private_uploads/ticket_attachments/. ./data/ticket_attachments/
   docker compose -f docker-compose.prod.yml down
   ```

5. Re-fetch the new compose file (the point of the rename -- after this,
   no more `-f` flag, ever):

   ```bash
   curl -O https://raw.githubusercontent.com/parcella-garden/parcella/main/docker-compose.yml
   ```

   If your `docker-compose.override.yml` has a `db.volumes` entry for
   `./postgres_data`, remove that clause now -- the new base file already
   bind-mounts `./data/postgres` by default, so it's redundant (keep it
   only if you actually want a *different* host path).

6. Start normally:

   ```bash
   docker compose up -d
   ```

7. Verify before cleaning up: log in, confirm the club logo/avatars/an
   announcement image and an existing ticket attachment still load. Only
   once confirmed, remove the old named volume (`docker volume rm
   gartenverein_postgres_data`) or the old `./postgres_data` directory.

## For a completely new / empty installation

No manual step needed -- `./data/` is created automatically on first
`docker compose up -d` (the permission note in step 2 above still
applies on a fresh install too: pre-create and `chown` `data/uploads` and
`data/ticket_attachments` before your first `up -d`).
