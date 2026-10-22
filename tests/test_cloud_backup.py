"""
Scheduled cloud backups (issue #141, docs/ADR/0055-scheduled-cloud-backups.md).

NextcloudProvider is exercised against an httpx.MockTransport, same
approach as tests/test_cloud_storage.py -- no real Nextcloud instance is
reachable from this test environment. Anything touching
build_backup_zip()/restore_from_zip_bytes() runs a REAL pg_dump/psql
against the test Postgres database, per this repo's testing philosophy
(docs/testing.md).
"""
from datetime import datetime, timedelta, timezone

import httpx as httpx_module
import pytest

from app.database import AsyncSessionLocal
from app.models import ClubSetting, Member
from app.cloud_storage import NextcloudProvider
from app.cloud_backup import (
    CloudBackupSettings, is_backup_due, is_backup_filename,
    get_cloud_backup_settings, run_cloud_backup_now,
)


async def web_login(client, email: str, password: str = "testpasswort123") -> None:
    response = await client.post("/auth/login", data={"email": email, "password": password})
    assert response.status_code in (302, 303)


async def _set_setting(key: str, value: str) -> None:
    async with AsyncSessionLocal() as session:
        session.add(ClubSetting(key=key, value=value))
        await session.commit()


async def _enable_cloud_storage_module() -> None:
    await _set_setting("modul_cloud_storage", "true")


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


def _mock_transport(
    propfind_status=207, propfind_body="<d:multistatus xmlns:d=\"DAV:\"></d:multistatus>",
    put_status=201, mkcol_status=201, delete_status=204, get_status=200, get_body=b"",
):
    def handler(request: httpx_module.Request) -> httpx_module.Response:
        if request.method == "PROPFIND":
            return httpx_module.Response(propfind_status, text=propfind_body)
        if request.method == "PUT":
            return httpx_module.Response(put_status)
        if request.method == "MKCOL":
            return httpx_module.Response(mkcol_status)
        if request.method == "DELETE":
            return httpx_module.Response(delete_status)
        if request.method == "GET":
            return httpx_module.Response(get_status, content=get_body)
        return httpx_module.Response(404)

    return httpx_module.MockTransport(handler)


def _provider(transport=None, **transport_kwargs) -> NextcloudProvider:
    mock_client = httpx_module.AsyncClient(transport=transport or _mock_transport(**transport_kwargs))
    return NextcloudProvider(
        base_url="https://cloud.example.org", username="board", app_password="secret",
        client=mock_client,
    )


def _listing_with(*names_and_flags: tuple) -> str:
    """Builds a PROPFIND multistatus body listing the given (name,
    is_directory) entries, all sitting in the same requested folder."""
    responses = []
    for name, is_dir in names_and_flags:
        resourcetype = "<d:resourcetype><d:collection/></d:resourcetype>" if is_dir else "<d:resourcetype/>"
        responses.append(f"""
  <d:response>
    <d:href>/remote.php/dav/files/board/backups/{name}</d:href>
    <d:propstat>
      <d:prop>
        <d:displayname>{name}</d:displayname>
        {resourcetype}
      </d:prop>
      <d:status>HTTP/1.1 200 OK</d:status>
    </d:propstat>
  </d:response>""")
    return f'<?xml version="1.0"?><d:multistatus xmlns:d="DAV:">{"".join(responses)}</d:multistatus>'


# ---------------------------------------------------------------------------
# Pure unit tests
# ---------------------------------------------------------------------------

def test_is_backup_filename():
    assert is_backup_filename("parcella-backup-20260730-143000.zip")
    assert not is_backup_filename("random-file.zip")
    assert not is_backup_filename("parcella-backup-20260730-143000.sql")


def _cfg(enabled=True, frequency="daily", last_run_at=None) -> CloudBackupSettings:
    return CloudBackupSettings(
        enabled=enabled, folder="backups", frequency=frequency, retention_count=5,
        last_run_at=last_run_at, last_run_status=None, last_run_error=None,
    )


def test_is_backup_due_never_run_before():
    assert is_backup_due(_cfg(last_run_at=None)) is True


def test_is_backup_due_false_when_disabled():
    now = datetime.now(timezone.utc)
    assert is_backup_due(_cfg(enabled=False, last_run_at=now - timedelta(days=10)), now=now) is False


def test_is_backup_due_false_when_not_enough_time_elapsed():
    now = datetime.now(timezone.utc)
    cfg = _cfg(frequency="daily", last_run_at=now - timedelta(hours=1))
    assert is_backup_due(cfg, now=now) is False


def test_is_backup_due_true_when_enough_time_elapsed():
    now = datetime.now(timezone.utc)
    cfg = _cfg(frequency="daily", last_run_at=now - timedelta(days=2))
    assert is_backup_due(cfg, now=now) is True


def test_is_backup_due_boundary_exactly_at_frequency():
    now = datetime.now(timezone.utc)
    cfg = _cfg(frequency="hourly", last_run_at=now - timedelta(hours=1))
    assert is_backup_due(cfg, now=now) is True


# ---------------------------------------------------------------------------
# NextcloudProvider: delete_file / create_folder
# ---------------------------------------------------------------------------

async def test_create_folder_walks_segments_and_tolerates_405():
    calls = []

    def handler(request: httpx_module.Request) -> httpx_module.Response:
        if request.method == "MKCOL":
            calls.append(str(request.url))
            # First segment already exists (405), second is newly created (201).
            status = 405 if len(calls) == 1 else 201
            return httpx_module.Response(status)
        return httpx_module.Response(404)

    provider = _provider(transport=httpx_module.MockTransport(handler))
    await provider.create_folder("backups/parcella")
    await provider.aclose()

    assert len(calls) == 2
    assert calls[0].endswith("/backups")
    assert calls[1].endswith("/backups/parcella")


async def test_create_folder_401_raises():
    provider = _provider(mkcol_status=401)
    with pytest.raises(Exception):
        await provider.create_folder("backups")
    await provider.aclose()


async def test_delete_file_404_is_treated_as_success():
    provider = _provider(delete_status=404)
    await provider.delete_file("backups", "gone-already.zip")  # must not raise
    await provider.aclose()


async def test_delete_file_401_raises():
    provider = _provider(delete_status=401)
    with pytest.raises(Exception):
        await provider.delete_file("backups", "file.zip")
    await provider.aclose()


# ---------------------------------------------------------------------------
# run_cloud_backup_now
# ---------------------------------------------------------------------------

async def test_run_cloud_backup_now_uploads_real_dump_and_records_success(monkeypatch):
    await _set_setting("cloud_backup_enabled", "true")
    await _set_setting("cloud_backup_folder", "backups")
    await _set_setting("cloud_backup_retention_count", "10")

    uploaded = {}

    def handler(request: httpx_module.Request) -> httpx_module.Response:
        if request.method == "MKCOL":
            return httpx_module.Response(201)
        if request.method == "PUT":
            uploaded["filename"] = str(request.url).rsplit("/", 1)[-1]
            uploaded["content"] = request.content
            return httpx_module.Response(201)
        if request.method == "PROPFIND":
            return httpx_module.Response(207, text=_listing_with((uploaded.get("filename", "x.zip"), False)))
        return httpx_module.Response(404)

    provider = _provider(transport=httpx_module.MockTransport(handler))

    async def fake_get_nextcloud_provider(db, client=None):
        return provider

    monkeypatch.setattr("app.cloud_backup.get_cloud_storage_provider", fake_get_nextcloud_provider)

    async with AsyncSessionLocal() as db:
        await run_cloud_backup_now(db)

    async with AsyncSessionLocal() as db:
        cfg = await get_cloud_backup_settings(db)
    assert cfg.last_run_status == "success"
    assert cfg.last_run_error is None
    assert uploaded["filename"].startswith("parcella-backup-")
    assert uploaded["filename"].endswith(".zip")


async def test_run_cloud_backup_now_records_error_when_upload_fails(monkeypatch):
    await _set_setting("cloud_backup_enabled", "true")
    await _set_setting("cloud_backup_folder", "backups")

    provider = _provider(put_status=500)

    async def fake_get_nextcloud_provider(db, client=None):
        return provider

    monkeypatch.setattr("app.cloud_backup.get_cloud_storage_provider", fake_get_nextcloud_provider)

    async with AsyncSessionLocal() as db:
        await run_cloud_backup_now(db)  # must not raise

    async with AsyncSessionLocal() as db:
        cfg = await get_cloud_backup_settings(db)
    assert cfg.last_run_status == "error"
    assert cfg.last_run_error


async def test_run_cloud_backup_now_still_works_when_automatic_schedule_disabled(monkeypatch):
    """Regression test for a real bug: cloud_backup_enabled only gates
    the automatic scheduler (is_backup_due), not a manual "back up to
    cloud now" click. run_cloud_backup_now must still actually back up
    (and record success) even when the schedule is off -- it must not
    silently no-op, which previously also meant the HTTP handler
    reported a false "success" since last_run_status was never touched."""
    await _set_setting("cloud_backup_enabled", "false")
    await _set_setting("cloud_backup_folder", "backups")

    called = False

    def handler(request: httpx_module.Request) -> httpx_module.Response:
        nonlocal called
        called = True
        if request.method == "MKCOL":
            return httpx_module.Response(201)
        if request.method == "PUT":
            return httpx_module.Response(201)
        if request.method == "PROPFIND":
            return httpx_module.Response(207, text=_listing_with())
        return httpx_module.Response(404)

    provider = _provider(transport=httpx_module.MockTransport(handler))

    async def fake_get_nextcloud_provider(db, client=None):
        return provider

    monkeypatch.setattr("app.cloud_backup.get_cloud_storage_provider", fake_get_nextcloud_provider)

    async with AsyncSessionLocal() as db:
        await run_cloud_backup_now(db)

    assert called is True
    async with AsyncSessionLocal() as db:
        cfg = await get_cloud_backup_settings(db)
    assert cfg.last_run_status == "success"


async def test_run_cloud_backup_now_records_error_when_not_configured(monkeypatch):
    await _set_setting("cloud_backup_enabled", "true")

    async def fake_get_nextcloud_provider(db, client=None):
        return None

    monkeypatch.setattr("app.cloud_backup.get_cloud_storage_provider", fake_get_nextcloud_provider)

    async with AsyncSessionLocal() as db:
        await run_cloud_backup_now(db)

    async with AsyncSessionLocal() as db:
        cfg = await get_cloud_backup_settings(db)
    assert cfg.last_run_status == "error"
    assert cfg.last_run_error  # explanatory message, not silent


# ---------------------------------------------------------------------------
# Retention sweep
# ---------------------------------------------------------------------------

async def test_retention_sweep_deletes_oldest_beyond_count(monkeypatch):
    await _set_setting("cloud_backup_enabled", "true")
    await _set_setting("cloud_backup_folder", "backups")
    await _set_setting("cloud_backup_retention_count", "2")

    existing = [
        "parcella-backup-20260101-000000.zip",
        "parcella-backup-20260102-000000.zip",
        "parcella-backup-20260103-000000.zip",
    ]
    state = {"uploaded_filename": None}
    deleted = []

    def handler(request: httpx_module.Request) -> httpx_module.Response:
        if request.method == "MKCOL":
            return httpx_module.Response(201)
        if request.method == "PUT":
            state["uploaded_filename"] = str(request.url).rsplit("/", 1)[-1]
            return httpx_module.Response(201)
        if request.method == "PROPFIND":
            all_names = existing + [state["uploaded_filename"]]
            return httpx_module.Response(207, text=_listing_with(*[(n, False) for n in all_names]))
        if request.method == "DELETE":
            deleted.append(str(request.url).rsplit("/", 1)[-1])
            return httpx_module.Response(204)
        return httpx_module.Response(404)

    provider = _provider(transport=httpx_module.MockTransport(handler))

    async def fake_get_nextcloud_provider(db, client=None):
        return provider

    monkeypatch.setattr("app.cloud_backup.get_cloud_storage_provider", fake_get_nextcloud_provider)

    async with AsyncSessionLocal() as db:
        await run_cloud_backup_now(db)

    # 4 backups total (3 pre-existing + 1 new), retention=2 -> 2 oldest deleted.
    assert set(deleted) == {"parcella-backup-20260101-000000.zip", "parcella-backup-20260102-000000.zip"}


# ---------------------------------------------------------------------------
# Restore-from-cloud (HTTP), real dump/restore round trip
# ---------------------------------------------------------------------------

async def test_restore_from_cloud_round_trip(client, admin_user, monkeypatch):
    await web_login(client, "admin@example.com")
    await _enable_cloud_storage_module()
    await _set_setting("cloud_backup_folder", "backups")
    member_id = await _create_member("Restore", "FromCloud")

    from app.backup import build_backup_zip
    filename, zip_bytes = await build_backup_zip()

    async with AsyncSessionLocal() as session:
        member = await session.get(Member, member_id)
        await session.delete(member)
        await session.commit()
    assert not await _member_exists(member_id)

    def handler(request: httpx_module.Request) -> httpx_module.Response:
        if request.method == "GET":
            return httpx_module.Response(200, content=zip_bytes)
        return httpx_module.Response(404)

    provider = _provider(transport=httpx_module.MockTransport(handler))

    async def fake_get_nextcloud_provider(db, client=None):
        return provider

    monkeypatch.setattr("app.routers.admin.get_cloud_storage_provider", fake_get_nextcloud_provider)

    resp = await client.post(
        "/admin/backup/restore-from-cloud",
        data={"confirm_phrase": "RESTORE", "filename": filename},
        follow_redirects=False,
    )
    assert resp.status_code == 302
    assert "success=1" in resp.headers["location"]
    assert await _member_exists(member_id)


async def test_restore_from_cloud_wrong_confirm_phrase_is_rejected(client, admin_user):
    await web_login(client, "admin@example.com")
    member_id = await _create_member("Untouched", "Sentinel")

    resp = await client.post(
        "/admin/backup/restore-from-cloud",
        data={"confirm_phrase": "nope", "filename": "parcella-backup-20260101-000000.zip"},
        follow_redirects=False,
    )
    assert resp.status_code == 302
    assert "error=" in resp.headers["location"]
    assert await _member_exists(member_id)


# ---------------------------------------------------------------------------
# Page gating
# ---------------------------------------------------------------------------

async def test_backup_cloud_page_shows_configure_message_when_module_disabled(client, admin_user):
    await web_login(client, "admin@example.com")
    resp = await client.get("/admin/backup/cloud")
    assert resp.status_code == 200
    assert 'href="/admin/settings"' in resp.text
    assert 'id="cloud-backup-enabled"' not in resp.text


async def test_backup_cloud_page_shows_configure_message_when_nextcloud_not_configured(client, admin_user):
    await _enable_cloud_storage_module()
    await web_login(client, "admin@example.com")
    resp = await client.get("/admin/backup/cloud")
    assert resp.status_code == 200
    assert 'href="/admin/integrations"' in resp.text
    assert 'id="cloud-backup-enabled"' not in resp.text


async def test_backup_cloud_run_now_requires_admin(client):
    resp = await client.post("/admin/backup/cloud/run-now", follow_redirects=False)
    assert resp.status_code == 303


# ---------------------------------------------------------------------------
# Settings save validation
# ---------------------------------------------------------------------------

async def test_backup_cloud_settings_save_rejects_invalid_folder(client, admin_user):
    await web_login(client, "admin@example.com")
    resp = await client.post(
        "/admin/backup/cloud/settings",
        data={"folder": "../../etc", "frequency": "daily", "retention_count": "5"},
        follow_redirects=False,
    )
    assert resp.status_code == 302
    assert "error=" in resp.headers["location"]


async def test_backup_cloud_settings_save_rejects_invalid_retention(client, admin_user):
    await web_login(client, "admin@example.com")
    resp = await client.post(
        "/admin/backup/cloud/settings",
        data={"folder": "backups", "frequency": "daily", "retention_count": "0"},
        follow_redirects=False,
    )
    assert resp.status_code == 302
    assert "error=" in resp.headers["location"]


async def test_backup_cloud_settings_save_accepts_valid_input(client, admin_user):
    await web_login(client, "admin@example.com")
    resp = await client.post(
        "/admin/backup/cloud/settings",
        data={"enabled": "on", "folder": "backups/parcella", "frequency": "weekly", "retention_count": "7"},
        follow_redirects=False,
    )
    assert resp.status_code == 302
    assert "success=1" in resp.headers["location"]

    async with AsyncSessionLocal() as db:
        cfg = await get_cloud_backup_settings(db)
    assert cfg.enabled is True
    assert cfg.folder == "backups/parcella"
    assert cfg.frequency == "weekly"
    assert cfg.retention_count == 7
