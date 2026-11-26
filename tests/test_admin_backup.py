"""
Issue #117: "add a backup possibility to administration panel".

Direct-download only (ADR 0053): a system admin triggers a real pg_dump
against the (test) database and gets the result back as a zip download
-- nothing is ever written to server disk. This test runs a REAL
pg_dump subprocess against db_test, not a mock, per this repo's "real
Postgres, not fakes" testing philosophy (docs/testing.md).

The zip also bundles app/static/uploads/ (branding logo, announcement
images) alongside the SQL dump -- those files are referenced by
filename from DB rows but aren't themselves part of the dump, so a
DB-only backup would leave dangling references on restore.
"""
import io
import zipfile


async def web_login(client, email: str, password: str = "testpasswort123") -> None:
    response = await client.post("/auth/login", data={"email": email, "password": password})
    assert response.status_code in (302, 303)


async def test_backup_download_returns_a_valid_zip_with_sql_dump(client, admin_user):
    await web_login(client, "admin@example.com")

    resp = await client.post("/admin/backup/download")

    assert resp.status_code == 200
    content_disposition = resp.headers["content-disposition"]
    assert "attachment" in content_disposition
    assert ".zip" in content_disposition

    zf = zipfile.ZipFile(io.BytesIO(resp.content))
    sql_names = [n for n in zf.namelist() if n.endswith(".sql")]
    # Issue #327: laid out like the install's ./data/ folder.
    assert sql_names == ["data/postgres/parcella.sql"]

    sql_bytes = zf.read(sql_names[0])
    # Plain-format pg_dump's standard preamble -- proves this is a real,
    # structurally valid dump, not just "some bytes came back".
    assert b"PostgreSQL database dump" in sql_bytes
    # --clean --if-exists must have embedded DROP statements, so the
    # script is restorable directly into a database with existing objects.
    assert b"DROP TABLE IF EXISTS" in sql_bytes


async def test_backup_download_bundles_uploaded_files(client, admin_user, monkeypatch, tmp_path):
    upload_dir = tmp_path / "uploads"
    (upload_dir / "announcements").mkdir(parents=True)
    (upload_dir / "logo.png").write_bytes(b"fake-logo-bytes")
    (upload_dir / "announcements" / "example.png").write_bytes(b"fake-announcement-bytes")
    monkeypatch.setattr("app.backup.UPLOAD_DIR", upload_dir)

    await web_login(client, "admin@example.com")
    resp = await client.post("/admin/backup/download")
    assert resp.status_code == 200

    zf = zipfile.ZipFile(io.BytesIO(resp.content))
    names = set(zf.namelist())
    assert "data/uploads/logo.png" in names
    assert "data/uploads/announcements/example.png" in names
    assert zf.read("data/uploads/logo.png") == b"fake-logo-bytes"


async def test_backup_download_requires_admin(client):
    """No session at all -- require_user (app/auth.py) redirects to login."""
    resp = await client.post("/admin/backup/download", follow_redirects=False)
    assert resp.status_code == 303


async def test_backup_download_shows_error_when_pg_dump_binary_missing(client, admin_user, monkeypatch):
    monkeypatch.setattr("app.backup.PG_DUMP_BINARY", "/nonexistent/pg_dump")

    await web_login(client, "admin@example.com")
    resp = await client.post("/admin/backup/download", follow_redirects=False)

    assert resp.status_code == 302
    assert "error=" in resp.headers["location"]


async def test_backup_contains_the_secret_key(client, admin_user):
    """Issue #327 / ADR 0134: the zip carries the key in use, so the
    encrypted settings in the dump stay readable after a restore elsewhere."""
    from app.config import settings

    await web_login(client, "admin@example.com")
    resp = await client.post("/admin/backup/download")
    zf = zipfile.ZipFile(io.BytesIO(resp.content))
    assert zf.read("data/secrets/secret_key").decode("utf-8").strip() == settings.secret_key
    # Nothing outside data/: the zip mirrors the install's data folder.
    assert all(name.startswith("data/") for name in zf.namelist())


async def test_backup_download_leaves_no_temporary_files(client, admin_user, monkeypatch):
    """Issue #415: dump and zip go through temporary files, not memory;
    both are gone once the download has been sent."""
    import os
    import tempfile
    created = []
    real_mkstemp = tempfile.mkstemp

    def recording_mkstemp(*args, **kwargs):
        fd, name = real_mkstemp(*args, **kwargs)
        created.append(name)
        return fd, name

    monkeypatch.setattr("app.backup.tempfile.mkstemp", recording_mkstemp)
    await web_login(client, "admin@example.com")
    resp = await client.post("/admin/backup/download")
    assert resp.status_code == 200 and zipfile.ZipFile(io.BytesIO(resp.content)).testzip() is None
    assert len(created) == 2 and not any(os.path.exists(name) for name in created)


async def test_backup_on_a_full_disk_reports_a_backup_error(client, admin_user, monkeypatch):
    """A full /tmp while zipping is a BackupError (friendly redirect, and
    the cloud backup records it), not a 500 -- and leaves no temp files."""
    import os
    import tempfile
    created = []
    real_mkstemp = tempfile.mkstemp

    def recording_mkstemp(*args, **kwargs):
        fd, name = real_mkstemp(*args, **kwargs)
        created.append(name)
        return fd, name

    def disk_full(*args, **kwargs):
        raise OSError(28, "No space left on device")

    monkeypatch.setattr("app.backup.tempfile.mkstemp", recording_mkstemp)
    monkeypatch.setattr("app.backup._write_zip", disk_full)
    await web_login(client, "admin@example.com")
    resp = await client.post("/admin/backup/download")
    assert resp.status_code == 302 and "error=" in resp.headers["location"]
    assert len(created) == 2 and not any(os.path.exists(name) for name in created)
