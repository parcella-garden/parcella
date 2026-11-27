# Migrating to Alembic -- note for existing installations

You already have a running database with test data (created via the old
`Base.metadata.create_all()`). As of this version, **Alembic** takes over
schema management. To keep your data, you need **one manual step**
before the container is rebuilt.

## One-time step (only when switching over)

1. Deploy the new files (see below), but do **not** yet run
   `docker compose up` with the new entrypoint.

2. Start the container with the OLD setup as usual (so the DB is
   running):
   ```bash
   docker compose up -d db
   ```

3. "Stamp" Alembic in the `web` container (or locally with the same
   DATABASE_URL) -- this marks migration `0001_initial` as already
   applied, WITHOUT recreating the tables:
   ```bash
   docker compose run --rm web alembic stamp head
   ```

4. Then start normally:
   ```bash
   docker compose up -d
   ```

From now on, the container automatically checks on every start whether
new migrations are pending (`alembic upgrade head` runs in
`docker-entrypoint.sh`), and only applies what's new since `0001_initial`.

## For a completely new / empty installation

No manual step needed -- `alembic upgrade head` automatically creates all
tables from the `0001_initial` migration on first start.

## Creating a new migration (going forward, on model changes)

```bash
docker compose run --rm web alembic revision --autogenerate -m "Short description"
```

Alembic then automatically compares `app/models/` with the current DB
state and proposes the necessary `CREATE`/`ALTER` statements. ALWAYS
review the generated file in `migrations/versions/` before applying it.
