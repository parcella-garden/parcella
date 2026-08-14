"""
Restore-from-backup (companion to tests/test_admin_backup.py's download
feature; see docs/ADR/0054-admin-restore-from-backup.md for why this
reverses ADR 0053's original "no restore-from-UI" stance).

All tests run a REAL psql restore against the real db_test database, per
this repo's testing philosophy (docs/testing.md). --single-transaction
means a failed restore always rolls back completely, so tests that
expect failure can assert pre-existing data survives untouched.
"""
import io
import zipfile

from app.database import AsyncSessionLocal
from app.models import Member


async def web_login(client, email: str, password: str = "testpasswort123") -> None:
    response = await client.post("/auth/login", data={"email": email, "password": password})
    assert response.status_code in (302, 303)


async def _create_member(first_name: str, last_name: str) -> str:
    async with AsyncSessionLocal() as session:
        member = Member(first_name=first_name, last_name=last_name)
        session.add(member)
        await session.commit()
        await session.refresh(member)
        return member.id


async def _member_exists(member_id: str) -> bool:
    async with AsyncSessionLocal() as session:
        return await session.get(Member, member_id) is not None


def _minimal_valid_zip() -> bytes:
    """A zip shaped like a real backup, but with a trivial, always-safe
    SQL statement -- enough to pass psql without actually changing
    anything, for tests focused on the zip-handling/uploads logic
    rather than the DB-restore logic itself (which the round-trip and
    rollback tests already cover directly)."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as zf:
        zf.writestr("backup.sql", "SELECT 1;")
    return buffer.getvalue()


async def test_restore_round_trip_restores_deleted_member(client, admin_user):
    await web_login(client, "admin@example.com")
    member_id = await _create_member("Restore", "Roundtrip")

    download = await client.post("/admin/backup/download")
    assert download.status_code == 200
    backup_zip_bytes = download.content

    async with AsyncSessionLocal() as session:
        member = await session.get(Member, member_id)
        await session.delete(member)
        await session.commit()
    assert not await _member_exists(member_id)

    restore = await client.post(
        "/admin/backup/restore",
        data={"confirm_phrase": "RESTORE"},
        files={"backup_zip": ("backup.zip", backup_zip_bytes, "application/zip")},
        follow_redirects=False,
    )
    assert restore.status_code == 302
    assert "success=1" in restore.headers["location"]
    assert await _member_exists(member_id)


async def test_restore_wrong_confirm_phrase_is_rejected(client, admin_user):
    await web_login(client, "admin@example.com")
    member_id = await _create_member("Untouched", "Sentinel")

    resp = await client.post(
        "/admin/backup/restore",
        data={"confirm_phrase": "wrong"},
        files={"backup_zip": ("backup.zip", _minimal_valid_zip(), "application/zip")},
        follow_redirects=False,
    )
    assert resp.status_code == 302
    assert "error=" in resp.headers["location"]
    assert await _member_exists(member_id)


async def test_restore_malformed_zip_is_rejected(client, admin_user):
    await web_login(client, "admin@example.com")
    member_id = await _create_member("Untouched", "Sentinel")

    resp = await client.post(
        "/admin/backup/restore",
        data={"confirm_phrase": "RESTORE"},
        files={"backup_zip": ("backup.zip", b"not actually a zip file", "application/zip")},
        follow_redirects=False,
    )
    assert resp.status_code == 302
    assert "error=" in resp.headers["location"]
    assert await _member_exists(member_id)


async def test_restore_rejects_zip_slip_attempt(client, admin_user, tmp_path):
    await web_login(client, "admin@example.com")
    member_id = await _create_member("Untouched", "Sentinel")

    escape_target = tmp_path / "evil.txt"

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as zf:
        zf.writestr("backup.sql", "SELECT 1;")
        zf.writestr(f"uploads/../../{escape_target.name}", b"pwned")
    malicious_zip = buffer.getvalue()

    resp = await client.post(
        "/admin/backup/restore",
        data={"confirm_phrase": "RESTORE"},
        files={"backup_zip": ("backup.zip", malicious_zip, "application/zip")},
        follow_redirects=False,
    )
    assert resp.status_code == 302
    assert "error=" in resp.headers["location"]
    assert await _member_exists(member_id)
    assert not escape_target.exists()


async def test_restore_uploads_is_a_full_mirror(client, admin_user, monkeypatch, tmp_path):
    (tmp_path / "orphan.png").write_bytes(b"leftover-from-before")
    monkeypatch.setattr("app.backup.UPLOAD_DIR", tmp_path)

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as zf:
        zf.writestr("backup.sql", "SELECT 1;")
        zf.writestr("uploads/logo.png", b"fresh-from-backup")
    backup_zip_bytes = buffer.getvalue()

    await web_login(client, "admin@example.com")
    resp = await client.post(
        "/admin/backup/restore",
        data={"confirm_phrase": "RESTORE"},
        files={"backup_zip": ("backup.zip", backup_zip_bytes, "application/zip")},
        follow_redirects=False,
    )
    assert resp.status_code == 302
    assert "success=1" in resp.headers["location"]

    assert not (tmp_path / "orphan.png").exists()
    assert (tmp_path / "logo.png").read_bytes() == b"fresh-from-backup"


async def test_restore_ticket_attachments_is_a_full_mirror(client, admin_user, monkeypatch, tmp_path):
    """Same full-mirror-replace behavior as UPLOAD_DIR, for the second
    directory added by ADR 0072."""
    (tmp_path / "orphan-attachment").write_bytes(b"leftover-from-before")
    monkeypatch.setattr("app.backup.TICKET_ATTACHMENT_STORAGE_DIR", tmp_path)

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as zf:
        zf.writestr("backup.sql", "SELECT 1;")
        zf.writestr("ticket_attachments/fresh-attachment", b"fresh-from-backup")
    backup_zip_bytes = buffer.getvalue()

    await web_login(client, "admin@example.com")
    resp = await client.post(
        "/admin/backup/restore",
        data={"confirm_phrase": "RESTORE"},
        files={"backup_zip": ("backup.zip", backup_zip_bytes, "application/zip")},
        follow_redirects=False,
    )
    assert resp.status_code == 302
    assert "success=1" in resp.headers["location"]

    assert not (tmp_path / "orphan-attachment").exists()
    assert (tmp_path / "fresh-attachment").read_bytes() == b"fresh-from-backup"


async def test_restore_rolls_back_completely_on_sql_failure(client, admin_user):
    await web_login(client, "admin@example.com")
    member_id = await _create_member("Untouched", "Sentinel")

    broken_sql = (
        "CREATE TABLE zzz_restore_test_marker (id int);\n"
        "SELECT * FROM this_table_does_not_exist_at_all;\n"
    )
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as zf:
        zf.writestr("backup.sql", broken_sql)
    broken_zip = buffer.getvalue()

    resp = await client.post(
        "/admin/backup/restore",
        data={"confirm_phrase": "RESTORE"},
        files={"backup_zip": ("backup.zip", broken_zip, "application/zip")},
        follow_redirects=False,
    )
    assert resp.status_code == 302
    assert "error=" in resp.headers["location"]

    # --single-transaction must have rolled back the whole script,
    # including the CREATE TABLE that ran before the failing statement.
    assert await _member_exists(member_id)
    async with AsyncSessionLocal() as session:
        from sqlalchemy import text
        result = await session.execute(
            text("SELECT to_regclass('public.zzz_restore_test_marker')")
        )
        assert result.scalar() is None


async def test_restore_requires_admin(client):
    resp = await client.post(
        "/admin/backup/restore",
        data={"confirm_phrase": "RESTORE"},
        files={"backup_zip": ("backup.zip", _minimal_valid_zip(), "application/zip")},
        follow_redirects=False,
    )
    assert resp.status_code == 303
