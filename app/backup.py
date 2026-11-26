"""
Shared core for database backup/restore (issue #117, ADR 0053/0054),
reused by both the manual local download/upload flow
(app/routers/admin.py) and the scheduled cloud-backup flow
(app/cloud_backup.py, issue #141/ADR 0055) -- one pg_dump/psql
implementation, two entry points for getting the bytes in and out.

Deliberately no FastAPI/HTTP imports here: build_backup_zip() and
restore_from_zip_bytes() raise plain exceptions (BackupError,
RestoreZipError) rather than returning HTTP responses, so callers that
aren't handling a request (the cloud-backup scheduler) don't have to
fake one.
"""
import asyncio
import io
import os
import shutil
import urllib.parse
import zipfile
from pathlib import Path
from datetime import datetime, timezone
from typing import Tuple

from app.branding import UPLOAD_DIR
from app.config import settings

PG_DUMP_BINARY = "pg_dump"  # module-level constant so tests can monkeypatch it
PSQL_BINARY = "psql"  # module-level constant so tests can monkeypatch it
RESTORE_CONFIRM_PHRASE = "RESTORE"
MAX_RESTORE_UPLOAD_BYTES = 200 * 1024 * 1024
MAX_RESTORE_UNCOMPRESSED_BYTES = 2 * 1024 * 1024 * 1024
# Issue #327 / ADR 0134: the zip mirrors the install's ./data/ folder --
# data/postgres/ (the database, as a dump), data/uploads/ and
# data/secrets/secret_key, so the stored SMTP/website/cloud passwords still
# work after a restore elsewhere. Restore also accepts the older layout
# (top-level *.sql, uploads/, secrets/secret_key).
DATA_PREFIX = "data/"
SQL_MEMBER = "data/postgres/parcella.sql"
UPLOADS_PREFIX = "data/uploads"
SECRET_KEY_MEMBER = "data/secrets/secret_key"
MAX_SECRET_KEY_BYTES = 1024


class BackupError(Exception):
    """Raised when pg_dump or psql fails, times out, or can't be
    started at all (e.g. binary not found)."""


class RestoreZipError(ValueError):
    """Raised when an uploaded/downloaded backup zip is malformed or
    unsafe (wrong shape, zip-slip attempt)."""


async def build_backup_zip() -> Tuple[str, bytes]:
    """Runs pg_dump (plain SQL, --clean --if-exists) and bundles it
    together with everything under app/static/uploads/ (the branding
    logo, announcement images) -- files referenced by filename from DB
    rows but not themselves part of the dump -- into a single in-memory
    zip, laid out like the install's ./data/ folder (data/postgres/,
    data/uploads/, data/secrets/). That directory is also bind-mounted under ./data/ in
    docker-compose.yml (see ADR 0077), but this backup remains useful as
    an out-of-band copy, e.g. when moving to a new host. Since issue #327
    (ADR 0134) it also holds the SECRET_KEY in use (secrets/secret_key):
    together with the dump that's all of ./data/ that matters, and the
    encrypted settings in the dump stay readable on a new host. Whoever
    has the zip can read those settings -- store it accordingly. Returns (filename,
    zip_bytes). Raises BackupError on any pg_dump failure/timeout --
    never returns partial/corrupt bytes."""
    db_url = urllib.parse.urlsplit(settings.database_url)
    env = {**os.environ, "PGPASSWORD": db_url.password or ""}
    cmd = [
        PG_DUMP_BINARY,
        "-h", db_url.hostname or "localhost",
        "-p", str(db_url.port or 5432),
        "-U", db_url.username or "",
        "-F", "p",
        "--clean", "--if-exists",
        db_url.path.lstrip("/"),
    ]

    try:
        process = await asyncio.create_subprocess_exec(
            *cmd, env=env,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=300)
    except (OSError, asyncio.TimeoutError) as e:
        raise BackupError(str(e)[:500]) from e

    if process.returncode != 0:
        raise BackupError(stderr.decode("utf-8", errors="replace").strip()[:500])

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(SQL_MEMBER, stdout)
        # The effective key, whether it came from .env or data/secrets/.
        zf.writestr(SECRET_KEY_MEMBER, settings.secret_key + "\n")
        for base_dir, prefix in ((UPLOAD_DIR, UPLOADS_PREFIX),):
            if base_dir.is_dir():
                for file_path in sorted(base_dir.rglob("*")):
                    if file_path.is_file():
                        zf.write(file_path, arcname=f"{prefix}/{file_path.relative_to(base_dir)}")

    return f"parcella-backup-{timestamp}.zip", zip_buffer.getvalue()


def _assert_within_upload_dir(relative: str, base: Path) -> Path:
    """Zip-slip guard: rejects any member whose resolved path would
    land outside `base`, however it got there."""
    base_resolved = base.resolve()
    target = (base / relative).resolve()
    if target != base_resolved and base_resolved not in target.parents:
        raise RestoreZipError(f"path escapes upload directory: {relative!r}")
    return target


_RESTORE_DIR_PREFIXES = {"uploads": UPLOAD_DIR}


def _validate_restore_zip(zf: zipfile.ZipFile):
    """Exactly one database dump (data/postgres/*.sql, or a top-level *.sql
    in the older layout); every other member is the key
    (data/secrets/secret_key or secrets/secret_key) or starts with one of
    _RESTORE_DIR_PREFIXES ('data/uploads/' or 'uploads/') and resolves
    inside that prefix's directory. Hand-rolled rather than
    ZipFile.extractall(): Python's extractall silently rewrites a
    '..'-containing name instead of rejecting it, and we want
    fail-closed rejection of a malformed backup, not silent
    reinterpretation. Writing bytes ourselves via open()/write() (not
    extract()) also means a crafted symlink-type zip entry can never
    become an actual symlink on disk."""
    total = 0
    sql_members = []
    secret_key = None
    dir_entries = {prefix: [] for prefix in _RESTORE_DIR_PREFIXES}
    for info in zf.infolist():
        if info.is_dir():
            continue
        raw_name = info.filename
        if "\x00" in raw_name or raw_name.startswith("/") or raw_name.startswith("\\"):
            raise RestoreZipError(f"unsafe member name: {raw_name!r}")
        total += info.file_size
        if total > MAX_RESTORE_UNCOMPRESSED_BYTES:
            raise RestoreZipError("zip expands too large")
        # Both layouts map onto the same three kinds of member: the data/
        # one (issue #327) and the older flat one.
        name = raw_name[len(DATA_PREFIX):] if raw_name.startswith(DATA_PREFIX) else raw_name
        is_new_layout = raw_name.startswith(DATA_PREFIX)
        if (is_new_layout and name.startswith("postgres/") and "/" not in name[len("postgres/"):]
                and name.endswith(".sql")) or (not is_new_layout and "/" not in name and name.endswith(".sql")):
            sql_members.append(raw_name)
        elif name == "secrets/secret_key":
            if info.file_size > MAX_SECRET_KEY_BYTES:
                raise RestoreZipError("secret key file too large")
            try:
                secret_key = zf.read(info).decode("utf-8").strip() or None
            except UnicodeDecodeError as e:
                raise RestoreZipError("secret key file is not text") from e
        else:
            for prefix, base_dir in _RESTORE_DIR_PREFIXES.items():
                if name.startswith(f"{prefix}/"):
                    relative = name[len(prefix) + 1:]
                    _assert_within_upload_dir(relative, base_dir)
                    dir_entries[prefix].append((relative, info))
                    break
            else:
                raise RestoreZipError(f"unexpected member: {raw_name!r}")
    if len(sql_members) != 1:
        raise RestoreZipError(f"expected exactly one database dump (.sql), found {len(sql_members)}")
    return zf.read(sql_members[0]), dir_entries["uploads"], secret_key


def _mirror_replace_dir(zf: zipfile.ZipFile, target_dir: Path, entries) -> None:
    """Wholesale mirror-replace of target_dir from the zip's entries --
    nothing not in the backup survives, since once the DB is rolled
    back, any file not referenced by it is an orphan by definition.
    Builds the new tree in a sibling temp directory first and swaps it
    in via rename(), so the window where target_dir is missing/partial
    is a single syscall, not "however long the copy takes"."""
    tmp_dir = target_dir.with_name(target_dir.name + ".restore-tmp")
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)
    tmp_dir.mkdir(parents=True)
    for relative, info in entries:
        dest = _assert_within_upload_dir(relative, tmp_dir)
        dest.parent.mkdir(parents=True, exist_ok=True)
        with zf.open(info) as src, open(dest, "wb") as out:
            shutil.copyfileobj(src, out)
    if target_dir.exists():
        shutil.rmtree(target_dir)
    tmp_dir.rename(target_dir)


async def restore_from_zip_bytes(zip_bytes: bytes) -> None:
    """Validates the zip, runs psql --single-transaction (a failure
    rolls back the whole script, database untouched), disposes the
    engine on success (stale prepared-statement-cache fix -- see ADR
    0054), re-encrypts the stored settings if the backup came with a
    different SECRET_KEY (issue #327), then mirror-replaces UPLOAD_DIR.

    Raises RestoreZipError (bad zip shape/zip-slip) or BackupError
    (psql failure/timeout); OSError propagates unchanged from the
    uploads mirror-replace step.

    Deliberately takes no db/Request: closing the CALLER's own DB
    session (avoiding the self-deadlock between require_system_admin's
    open SELECT and --clean's DROP TABLE) is the caller's
    responsibility, done immediately before calling this function --
    only the caller knows which session it's holding, and this
    function has no session to close on its own behalf."""
    try:
        zf = zipfile.ZipFile(io.BytesIO(zip_bytes))
    except zipfile.BadZipFile as e:
        raise RestoreZipError("not a valid zip archive") from e

    sql_bytes, upload_entries, backup_secret_key = _validate_restore_zip(zf)

    db_url = urllib.parse.urlsplit(settings.database_url)
    env = {**os.environ, "PGPASSWORD": db_url.password or ""}
    cmd = [
        PSQL_BINARY,
        "-h", db_url.hostname or "localhost",
        "-p", str(db_url.port or 5432),
        "-U", db_url.username or "",
        "-d", db_url.path.lstrip("/"),
        "-v", "ON_ERROR_STOP=1",
        "--single-transaction",
    ]

    try:
        process = await asyncio.create_subprocess_exec(
            *cmd, env=env,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(process.communicate(input=sql_bytes), timeout=300)
    except (OSError, asyncio.TimeoutError) as e:
        raise BackupError(str(e)[:500]) from e

    if process.returncode != 0:
        raise BackupError(stderr.decode("utf-8", errors="replace").strip()[:500])

    # The DDL above dropped and recreated every table -- drop pooled
    # connections so nobody reuses a prepared-statement cache from
    # before the schema was replaced (asyncpg: "cached plan must not
    # change result type").
    from app.database import engine
    await engine.dispose()
    from app import settings_cache
    settings_cache.clear()  # the restored club settings, not the cached ones

    # Issue #327 / ADR 0134: the restored settings are encrypted with the
    # key of the instance that made the backup. Re-encrypt them with this
    # instance's key instead of switching keys: no restart, nobody logged
    # out, and a key set in .env keeps winning. Same key: nothing to do.
    if backup_secret_key and backup_secret_key != settings.secret_key:
        from app.secret_bootstrap import rekey_database
        try:
            await rekey_database(settings.database_url, settings.secret_key, old_key=backup_secret_key)
        except Exception as e:
            raise BackupError(
                f"The database was restored, but re-encrypting its stored passwords failed: {str(e)[:300]}"
            ) from e

    _mirror_replace_dir(zf, UPLOAD_DIR, upload_entries)
