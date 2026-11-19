#!/usr/bin/env bash
# Local Parcella instance for taking the user-docs screenshots.
#
# WITH DOCKER (the normal contributor route) you don't need this script:
#
#   docker compose -f docker-compose.dev.yml build web
#   docker compose -f docker-compose.dev.yml run --rm --entrypoint alembic web upgrade head
#   docker compose -f docker-compose.dev.yml up -d db web        # http://localhost:8000
#   user-docs/tools/dev_server.sh seed-py | docker compose -f docker-compose.dev.yml exec -T web python -
#   python user-docs/tools/seed_docs_data.py        # extra fake data via the web UI (needs httpx)
#     (instead of seed-py you can: log in as admin@parcella.local / admin1234, Admin -> Sample data -> Add,
#      Admin -> Settings -> tick every module, language English -> Save)
#
# WITHOUT DOCKER (e.g. a sandbox where Docker Hub is unreachable) this
# script runs PostgreSQL 16 and uvicorn directly on the host:
#
#   user-docs/tools/dev_server.sh setup   # once: py3.12 venv, deps, initdb, migrations
#   user-docs/tools/dev_server.sh start   # postgres + uvicorn (background)
#   user-docs/tools/dev_server.sh seed    # sample data + every module on + English + extra fake data
#   user-docs/tools/dev_server.sh stop
#   user-docs/tools/dev_server.sh status
#
# Paths can be overridden through the environment variables below.
set -euo pipefail

REPO="$(cd "$(dirname "$0")/../.." && pwd)"
WORK="${PARCELLA_DEV_DIR:-$(dirname "$REPO")}"      # where venv/pgdata/log live
VENV="${VENV:-$WORK/venv312}"
PGDATA="${PGDATA:-$WORK/pgdata}"
APP_LOG="${APP_LOG:-$WORK/app.log}"
PGPORT="${PGPORT:-5432}"
APP_PORT="${APP_PORT:-8000}"
export DATABASE_URL="${DATABASE_URL:-postgresql+asyncpg://parcella:changeme@127.0.0.1:$PGPORT/parcella}"
export ENVIRONMENT="${ENVIRONMENT:-development}"   # dev default SECRET_KEY, non-secure cookie over http

# Postgres binaries: system ones if present, else the `pgserver` PyPI wheel.
pgbin() {
  if [ -n "${PG_BIN:-}" ]; then echo "$PG_BIN"; return; fi
  local d
  d="$("$VENV/bin/python" -c 'import pgserver,os;print(os.path.dirname(pgserver.__file__))' 2>/dev/null || true)"
  if [ -n "$d" ] && [ -x "$d/pginstall/bin/postgres" ]; then echo "$d/pginstall/bin"; return; fi
  ls -d /usr/lib/postgresql/16/bin 2>/dev/null || { echo "no PostgreSQL 16 binaries found" >&2; exit 1; }
}

# postgres refuses to run as root -> use the `postgres` system user then.
as_pg() { if [ "$(id -u)" = 0 ]; then (cd /tmp && runuser -u postgres -- "$@"); else "$@"; fi; }

cmd_setup() {
  if [ ! -x "$VENV/bin/python" ]; then
    # asyncpg 0.29 doesn't build on Python 3.13 -> pin 3.12 via uv.
    python3 -m pip install -q uv
    python3 -m uv python install 3.12
    python3 -m uv venv -p 3.12 "$VENV"
  fi
  VIRTUAL_ENV="$VENV" python3 -m uv pip install -r "$REPO/requirements.txt" pgserver playwright pyyaml
  local PG; PG="$(pgbin)"
  if [ ! -f "$PGDATA/PG_VERSION" ]; then
    mkdir -p "$PGDATA"; [ "$(id -u)" = 0 ] && chown postgres:postgres "$PGDATA"; chmod 700 "$PGDATA"
    as_pg "$PG/initdb" -D "$PGDATA" -U parcella --auth=trust -E UTF8 --locale=C.UTF-8
    cmd_start_db
    "$PG/psql" -h 127.0.0.1 -p "$PGPORT" -U parcella -d postgres \
      -c "ALTER USER parcella PASSWORD 'changeme'" -c "CREATE DATABASE parcella"
  fi
  cmd_start_db
  (cd "$REPO" && "$VENV/bin/alembic" upgrade head)
  # Chromium for Playwright; if its CDN is blocked, screenshots.py
  # falls back to a system Chrome (--browser-path / auto-detect).
  "$VENV/bin/playwright" install chromium || echo "playwright install failed -- use a system Chrome"
}

cmd_start_db() {
  local PG; PG="$(pgbin)"
  if "$PG/pg_isready" -q -h 127.0.0.1 -p "$PGPORT"; then return; fi
  as_pg "$PG/pg_ctl" -D "$PGDATA" -l "$PGDATA/server.log" -w \
    -o "-p $PGPORT -k /tmp -c listen_addresses=127.0.0.1" start
}

cmd_start() {
  cmd_start_db
  (cd "$REPO" && "$VENV/bin/alembic" upgrade head 2>&1 | grep -v "sqlalchemy" | tail -2)
  if curl -s -o /dev/null "http://127.0.0.1:$APP_PORT/auth/login"; then echo "app already running"; return; fi
  # setsid + </dev/null: fully detached, so a calling pipe/tool doesn't hang on it
  cd "$REPO"
  setsid nohup "$VENV/bin/uvicorn" app.main:app --host 127.0.0.1 --port "$APP_PORT" \
      > "$APP_LOG" 2>&1 < /dev/null &
  echo $! > "$WORK/uvicorn.pid"
  cd - >/dev/null
  for _ in $(seq 30); do
    curl -s -o /dev/null "http://127.0.0.1:$APP_PORT/auth/login" && { echo "app up: http://127.0.0.1:$APP_PORT"; return; }
    sleep 1
  done
  echo "app didn't come up, see $APP_LOG" >&2; exit 1
}

cmd_stop() {
  if [ -f "$WORK/uvicorn.pid" ]; then kill "$(cat "$WORK/uvicorn.pid")" 2>/dev/null || true; rm -f "$WORK/uvicorn.pid"; fi
  pkill -f "uvicorn app.main:app --host 127.0.0.1 --port $APP_PORT" 2>/dev/null || true
  as_pg "$(pgbin)/pg_ctl" -D "$PGDATA" -m fast stop || true
}

cmd_status() {
  "$(pgbin)/pg_isready" -h 127.0.0.1 -p "$PGPORT" || true
  curl -s -o /dev/null -w "app: HTTP %{http_code} on /auth/login\n" "http://127.0.0.1:$APP_PORT/auth/login" || echo "app: down"
}

# Python run inside the app's environment (also usable via `docker compose exec web python -`).
seed_py() { cat <<'PY'
import asyncio
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models import ClubSetting, User
from app.module_flags import MODULE_DEFAULTS
from app.sample_data import add_sample_data, has_sample_data, SampleDataBlockedError

async def put(db, key, value, desc):
    row = await db.scalar(select(ClubSetting).where(ClubSetting.key == key))
    if row: row.value = value
    else: db.add(ClubSetting(key=key, value=value, description=desc))

async def main():
    async with AsyncSessionLocal() as db:
        if await has_sample_data(db):
            print("sample data already present")
        else:
            try: print("sample data added:", await add_sample_data(db))
            except SampleDataBlockedError as e: print("sample data skipped:", e)
    async with AsyncSessionLocal() as db:
        for name in MODULE_DEFAULTS:      # every module on, so every screen exists
            await put(db, f"modul_{name}", "true", f"Module: {name}")
        await put(db, "language", "en", "UI language")
        # Throwaway docs instance only: keep admin1234 and skip the forced
        # first-login password change, so screenshots.py's defaults work.
        admin = await db.scalar(select(User).where(User.email == "admin@parcella.local"))
        if admin and admin.must_change_password:
            admin.must_change_password = False
            print("modules on: (dev admin: forced password change skipped)")
        await db.commit()
        print("modules on:", ", ".join(MODULE_DEFAULTS))

asyncio.run(main())
PY
}

# (ENVIRONMENT=development turns on SQL echo -> keep only our own lines)
# Step 1 (direct DB): built-in sample data, every module on, English, no forced
# password change. Step 2 (through the web UI's routes, app must be running):
# the extra fake records the screenshots need -- see seed_docs_data.py.
cmd_seed() {
  (cd "$REPO" && seed_py | "$VENV/bin/python" - 2>&1 | grep -E "^(sample data|modules on|Traceback|  File|[A-Za-z]+Error)" )
  "$VENV/bin/python" "$REPO/user-docs/tools/seed_docs_data.py" --base-url "http://127.0.0.1:$APP_PORT"
}

case "${1:-}" in
  setup) cmd_setup ;;
  start) cmd_start ;;
  seed) cmd_seed ;;
  seed-py) seed_py ;;
  stop) cmd_stop ;;
  status) cmd_status ;;
  *) sed -n '2,22p' "$0"; exit 1 ;;
esac
