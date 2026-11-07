"""
Zero-config SECRET_KEY for the published image (ADR 0121).

If SECRET_KEY isn't set in the environment, the container generates one on
first start and keeps it in a file under the bind-mounted ./data/secrets/
folder, so a fresh install needs no .env at all. `app/config.py` reads that
file whenever SECRET_KEY is empty.

Older installs that never set SECRET_KEY ran on the public development
default, and their stored secrets (SMTP / provider / Deck passwords in
`club_settings`) are encrypted with it. `rekey` re-encrypts every value the
default key can still decrypt with the file key. It is idempotent, so the
entrypoint runs it on every start: a value already encrypted with the file
key simply doesn't decrypt with the default and is left alone.

Deliberately imports nothing from `app.config` at module level: `ensure`
has to run *before* Settings() is first built, because Settings refuses to
start in production without a key.

Usage (from docker-entrypoint.sh):
    python -m app.secret_bootstrap ensure   # before alembic
    python -m app.secret_bootstrap rekey    # after alembic
"""
import asyncio
import logging
import os
import secrets
import sys
from pathlib import Path
from typing import Optional

# The built-in development fallback. It is published in a public repo, so an
# installation still running on it has forgeable session cookies, forgeable
# API tokens and readable stored passwords. Lives here (not in app.config)
# so this module can use it without building Settings.
DEFAULT_SECRET_KEY = "dev-secret-key-change-in-production"

DEFAULT_SECRET_FILE = "/app/secrets/secret_key"

logger = logging.getLogger("parcella.secret_bootstrap")


def secret_file_path() -> Path:
    return Path(os.environ.get("SECRET_KEY_FILE") or DEFAULT_SECRET_FILE)


def env_secret_key() -> str:
    return (os.environ.get("SECRET_KEY") or "").strip()


def read_secret_file(path: Optional[Path] = None) -> Optional[str]:
    """The persisted key, or None if there's no (non-empty, readable) file."""
    path = path or secret_file_path()
    try:
        value = path.read_text(encoding="utf-8").strip()
    except (FileNotFoundError, NotADirectoryError, PermissionError):
        return None
    return value or None


def ensure_secret_file(path: Optional[Path] = None) -> tuple[str, bool]:
    """Returns (key, created). Creates the file with mode 0600 if missing.
    O_EXCL so two containers starting at once can't both write a key."""
    path = path or secret_file_path()
    existing = read_secret_file(path)
    if existing:
        return existing, False
    path.parent.mkdir(parents=True, exist_ok=True)
    key = secrets.token_urlsafe(48)
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        # Lost a race, or an empty file is lying around.
        existing = read_secret_file(path)
        if existing:
            return existing, False
        path.unlink()
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        fh.write(key + "\n")
    return key, True


def rekey_values(rows: list[tuple[str, str]], new_key: str) -> dict[str, str]:
    """Given (key, value) rows, returns {key: new_value} for every value that
    decrypts with the public default key, re-encrypted with new_key.
    Plaintext and values encrypted with any other key are left out."""
    from cryptography.fernet import InvalidToken

    from app.crypto_utils import _looks_like_fernet_token, fernet_for

    if new_key == DEFAULT_SECRET_KEY:
        return {}
    old, new = fernet_for(DEFAULT_SECRET_KEY), fernet_for(new_key)
    updates = {}
    for key, value in rows:
        if not value or not _looks_like_fernet_token(value):
            continue
        try:
            plaintext = old.decrypt(value.encode("utf-8"))
        except (InvalidToken, ValueError):
            continue
        updates[key] = new.encrypt(plaintext).decode("utf-8")
    return updates


async def rekey_database(database_url: str, new_key: str) -> int:
    """Applies rekey_values to club_settings. Returns the number of rows
    changed; 0 when the table doesn't exist yet."""
    import asyncpg

    conn = await asyncpg.connect(database_url.replace("postgresql+asyncpg://", "postgresql://"))
    try:
        exists = await conn.fetchval("SELECT to_regclass('public.club_settings') IS NOT NULL")
        if not exists:
            return 0
        rows = await conn.fetch("SELECT key, value FROM club_settings WHERE value IS NOT NULL")
        updates = rekey_values([(r["key"], r["value"]) for r in rows], new_key)
        if updates:
            async with conn.transaction():
                await conn.executemany(
                    "UPDATE club_settings SET value = $2, updated_at = now() WHERE key = $1",
                    list(updates.items()),
                )
        return len(updates)
    finally:
        await conn.close()


def main(argv: list[str]) -> int:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    command = argv[1] if len(argv) > 1 else ""
    if env_secret_key():
        # An explicitly configured key always wins; nothing to manage.
        return 0
    if command == "ensure":
        _, created = ensure_secret_file()
        if created:
            print(f"Generated a new SECRET_KEY in {secret_file_path()} -- keep it with your backups.")
        return 0
    if command == "rekey":
        key = read_secret_file()
        if not key:
            print("No SECRET_KEY file to re-key with.", file=sys.stderr)
            return 1
        count = asyncio.run(rekey_database(os.environ["DATABASE_URL"], key))
        if count:
            print(f"Re-encrypted {count} stored setting(s) from the old default key to the new SECRET_KEY.")
        return 0
    print("usage: python -m app.secret_bootstrap ensure|rekey", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
