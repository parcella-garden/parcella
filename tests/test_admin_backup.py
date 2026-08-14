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
    assert len(sql_names) == 1

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
    assert "uploads/logo.png" in names
    assert "uploads/announcements/example.png" in names
    assert zf.read("uploads/logo.png") == b"fake-logo-bytes"


async def test_backup_download_bundles_local_ticket_attachments(client, admin_user, monkeypatch, tmp_path):
    """ADR 0072: locally-stored ticket attachments (Nextcloud fallback)
    have no volume mount in docker-compose.prod.yml, same as
    app/static/uploads/ -- this backup zip is what makes them survive a
    redeploy, so it must bundle them too."""
    attachments_dir = tmp_path / "ticket_attachments"
    attachments_dir.mkdir(parents=True)
    (attachments_dir / "abc123").write_bytes(b"fake-attachment-bytes")
    monkeypatch.setattr("app.backup.TICKET_ATTACHMENT_STORAGE_DIR", attachments_dir)

    await web_login(client, "admin@example.com")
    resp = await client.post("/admin/backup/download")
    assert resp.status_code == 200

    zf = zipfile.ZipFile(io.BytesIO(resp.content))
    names = set(zf.namelist())
    assert "ticket_attachments/abc123" in names
    assert zf.read("ticket_attachments/abc123") == b"fake-attachment-bytes"


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
