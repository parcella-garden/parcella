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
from app.ticket_attachment_storage import TICKET_ATTACHMENT_STORAGE_DIR
from app.config import settings

PG_DUMP_BINARY = "pg_dump"  # module-level constant so tests can monkeypatch it
PSQL_BINARY = "psql"  # module-level constant so tests can monkeypatch it
RESTORE_CONFIRM_PHRASE = "RESTORE"
MAX_RESTORE_UPLOAD_BYTES = 200 * 1024 * 1024
MAX_RESTORE_UNCOMPRESSED_BYTES = 2 * 1024 * 1024 * 1024


class BackupError(Exception):
    """Raised when pg_dump or psql fails, times out, or can't be
    started at all (e.g. binary not found)."""


class RestoreZipError(ValueError):
    """Raised when an uploaded/downloaded backup zip is malformed or
    unsafe (wrong shape, zip-slip attempt)."""


async def build_backup_zip() -> Tuple[str, bytes]:
    """Runs pg_dump (plain SQL, --clean --if-exists) and bundles it
    together with everything under app/static/uploads/ (the branding
    logo, announcement images) and app/private_uploads/ticket_attachments/
    (locally-stored ticket attachments -- see
    app/ticket_attachment_storage.py) -- files referenced by filename
    from DB rows but not themselves part of the dump -- into a single
    in-memory zip. Neither directory has a volume mount in
    docker-compose.prod.yml, so this backup is the only thing standing
    between a redeploy and silently losing them. Returns (filename,
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
        zf.writestr(f"parcella-backup-{timestamp}.sql", stdout)
        for base_dir, prefix in ((UPLOAD_DIR, "uploads"), (TICKET_ATTACHMENT_STORAGE_DIR, "ticket_attachments")):
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


_RESTORE_DIR_PREFIXES = {"uploads": UPLOAD_DIR, "ticket_attachments": TICKET_ATTACHMENT_STORAGE_DIR}


def _validate_restore_zip(zf: zipfile.ZipFile):
    """Exactly one top-level *.sql member; every other member must start
    with one of _RESTORE_DIR_PREFIXES ('uploads/', 'ticket_attachments/')
    and resolve inside that prefix's directory. Hand-rolled rather than
    ZipFile.extractall(): Python's extractall silently rewrites a
    '..'-containing name instead of rejecting it, and we want
    fail-closed rejection of a malformed backup, not silent
    reinterpretation. Writing bytes ourselves via open()/write() (not
    extract()) also means a crafted symlink-type zip entry can never
    become an actual symlink on disk."""
    total = 0
    sql_members = []
    dir_entries = {prefix: [] for prefix in _RESTORE_DIR_PREFIXES}
    for info in zf.infolist():
        if info.is_dir():
            continue
        name = info.filename
        if "\x00" in name or name.startswith("/") or name.startswith("\\"):
            raise RestoreZipError(f"unsafe member name: {name!r}")
        total += info.file_size
        if total > MAX_RESTORE_UNCOMPRESSED_BYTES:
            raise RestoreZipError("zip expands too large")
        if "/" not in name and name.endswith(".sql"):
            sql_members.append(name)
        else:
            for prefix, base_dir in _RESTORE_DIR_PREFIXES.items():
                if name.startswith(f"{prefix}/"):
                    relative = name[len(prefix) + 1:]
                    _assert_within_upload_dir(relative, base_dir)
                    dir_entries[prefix].append((relative, info))
                    break
            else:
                raise RestoreZipError(f"unexpected member: {name!r}")
    if len(sql_members) != 1:
        raise RestoreZipError(f"expected exactly one top-level .sql file, found {len(sql_members)}")
    return zf.read(sql_members[0]), dir_entries["uploads"], dir_entries["ticket_attachments"]


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
    0054), then mirror-replaces UPLOAD_DIR and
    TICKET_ATTACHMENT_STORAGE_DIR.

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

    sql_bytes, upload_entries, ticket_attachment_entries = _validate_restore_zip(zf)

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

    _mirror_replace_dir(zf, UPLOAD_DIR, upload_entries)
    _mirror_replace_dir(zf, TICKET_ATTACHMENT_STORAGE_DIR, ticket_attachment_entries)
