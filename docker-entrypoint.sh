#!/bin/bash
set -e

# Root phase (ADR 0121): Docker creates a missing bind-mount source folder
# (./data/uploads, ./data/secrets) as root:root 0755, which the app user
# can't write to. Fix ownership, then drop privileges and re-run this
# script as appuser -- the same pattern the official Postgres image uses.
# Skipped entirely when the container is already started as non-root.
if [ "$(id -u)" = "0" ]; then
  APP_UID="$(id -u appuser)"
  APP_GID="$(id -g appuser)"
  for dir in /app/app/static/uploads /app/secrets; do
    mkdir -p "$dir"
    # Only when the top level is wrong, so a large uploads folder isn't
    # walked on every start.
    if [ "$(stat -c %u:%g "$dir")" != "$APP_UID:$APP_GID" ]; then
      chown -R "$APP_UID:$APP_GID" "$dir"
    fi
  done
  chmod 700 /app/secrets
  export HOME=/home/appuser USER=appuser
  exec setpriv --reuid="$APP_UID" --regid="$APP_GID" --init-groups "$0" "$@"
fi

echo "Waiting for the database..."
until python -c "
import asyncio
import asyncpg
import os
import sys

url = os.environ.get('DATABASE_URL', '').replace('postgresql+asyncpg://', 'postgresql://')

async def check():
    try:
        conn = await asyncpg.connect(url)
        await conn.close()
        return True
    except Exception:
        return False

sys.exit(0 if asyncio.run(check()) else 1)
"; do
  sleep 1
done
echo "Database reachable."

# No SECRET_KEY configured: generate one on first start and keep it in
# ./data/secrets/secret_key (no-op when SECRET_KEY is set).
python -m app.secret_bootstrap ensure

echo "Running database migrations..."
# Note: an existing database from before Alembic was introduced needs a
# one-time manual "alembic stamp head" instead of "upgrade head", see
# MIGRATION-NOTE.md
alembic upgrade head

# Installs that used to run on the public default key: re-encrypt their
# stored passwords with the generated one (idempotent, no-op otherwise).
python -m app.secret_bootstrap rekey

echo "Starting application..."
exec "$@"
