"""
Tests for the cloud storage connector (app/cloud_storage.py,
app/parcel_cloud_folders.py, and the parcel Documents routes).

NextcloudProvider is exercised against an httpx.MockTransport, the same
approach used for WordPressPublisher in tests/test_announcements.py --
no real Nextcloud instance is reachable from this test environment.
"""
import pytest
from sqlalchemy import select

from tests.conftest import login, auth_header
from app.database import AsyncSessionLocal
from app.models import ParcelCloudFolder

PROPFIND_LISTING = """<?xml version="1.0"?>
<d:multistatus xmlns:d="DAV:">
  <d:response>
    <d:href>/remote.php/dav/files/board/parcels/G016/</d:href>
    <d:propstat>
      <d:prop>
        <d:displayname>G016</d:displayname>
        <d:resourcetype><d:collection/></d:resourcetype>
      </d:prop>
      <d:status>HTTP/1.1 200 OK</d:status>
    </d:propstat>
  </d:response>
  <d:response>
    <d:href>/remote.php/dav/files/board/parcels/G016/lease.pdf</d:href>
    <d:propstat>
      <d:prop>
        <d:displayname>lease.pdf</d:displayname>
        <d:getcontentlength>12345</d:getcontentlength>
        <d:getlastmodified>Mon, 01 Jun 2026 10:00:00 GMT</d:getlastmodified>
        <d:resourcetype/>
      </d:prop>
      <d:status>HTTP/1.1 200 OK</d:status>
    </d:propstat>
  </d:response>
  <d:response>
    <d:href>/remote.php/dav/files/board/parcels/G016/photos/</d:href>
    <d:propstat>
      <d:prop>
        <d:displayname>photos</d:displayname>
        <d:resourcetype><d:collection/></d:resourcetype>
      </d:prop>
      <d:status>HTTP/1.1 200 OK</d:status>
    </d:propstat>
  </d:response>
</d:multistatus>"""


def _nextcloud_mock_transport(
    propfind_status=207, propfind_body=PROPFIND_LISTING,
    put_status=201, get_status=200, get_body=b"file bytes",
):
    import httpx as httpx_module

    def handler(request: httpx_module.Request) -> httpx_module.Response:
        if request.method == "PROPFIND":
            return httpx_module.Response(propfind_status, text=propfind_body)
        if request.method == "PUT":
            return httpx_module.Response(put_status)
        if request.method == "GET":
            return httpx_module.Response(get_status, content=get_body)
        return httpx_module.Response(404)

    return httpx_module.MockTransport(handler)


# ---------------------------------------------------------------------------
# NextcloudProvider (WebDAV) unit tests
# ---------------------------------------------------------------------------

async def test_nextcloud_list_files_parses_propfind_response():
    import httpx as httpx_module
    from app.cloud_storage import NextcloudProvider

    mock_client = httpx_module.AsyncClient(transport=_nextcloud_mock_transport())
    provider = NextcloudProvider(
        base_url="https://cloud.example.org", username="board", app_password="secret",
        client=mock_client,
    )
    entries = await provider.list_files("parcels/G016")
    await provider.aclose()

    names = {e.name for e in entries}
    assert names == {"lease.pdf", "photos"}

    lease = next(e for e in entries if e.name == "lease.pdf")
    assert lease.is_directory is False
    assert lease.size == 12345

    photos = next(e for e in entries if e.name == "photos")
    assert photos.is_directory is True

    assert [e.name for e in entries] == ["photos", "lease.pdf"]


async def test_nextcloud_list_files_404_raises_cloud_storage_error():
    import httpx as httpx_module
    from app.cloud_storage import NextcloudProvider, CloudStorageError

    mock_client = httpx_module.AsyncClient(transport=_nextcloud_mock_transport(propfind_status=404, propfind_body=""))
    provider = NextcloudProvider(
        base_url="https://cloud.example.org", username="board", app_password="secret",
        client=mock_client,
    )
    with pytest.raises(CloudStorageError):
        await provider.list_files("parcels/does-not-exist")
    await provider.aclose()


async def test_nextcloud_test_connection_401_raises_cloud_storage_error():
    import httpx as httpx_module
    from app.cloud_storage import NextcloudProvider, CloudStorageError

    def handler(request: httpx_module.Request) -> httpx_module.Response:
        return httpx_module.Response(401)

    mock_client = httpx_module.AsyncClient(transport=httpx_module.MockTransport(handler))
    provider = NextcloudProvider(
        base_url="https://cloud.example.org", username="board", app_password="wrong",
        client=mock_client,
    )
    with pytest.raises(CloudStorageError):
        await provider.test_connection()
    await provider.aclose()


async def test_nextcloud_upload_conflict_raises_cloud_storage_error():
    import httpx as httpx_module
    from app.cloud_storage import NextcloudProvider, CloudStorageError

    mock_client = httpx_module.AsyncClient(transport=_nextcloud_mock_transport(put_status=409))
    provider = NextcloudProvider(
        base_url="https://cloud.example.org", username="board", app_password="secret",
        client=mock_client,
    )
    with pytest.raises(CloudStorageError):
        await provider.upload_file("parcels/missing-folder", "file.pdf", b"data")
    await provider.aclose()


async def test_nextcloud_download_returns_bytes():
    import httpx as httpx_module
    from app.cloud_storage import NextcloudProvider

    mock_client = httpx_module.AsyncClient(transport=_nextcloud_mock_transport(get_body=b"hello world"))
    provider = NextcloudProvider(
        base_url="https://cloud.example.org", username="board", app_password="secret",
        client=mock_client,
    )
    content = await provider.download_file("parcels/G016", "lease.pdf")
    await provider.aclose()
    assert content == b"hello world"


# ---------------------------------------------------------------------------
# Path sanitization
# ---------------------------------------------------------------------------

def test_sanitize_relative_path_rejects_parent_traversal():
    from app.parcel_cloud_folders import sanitize_relative_path, InvalidCloudPathError

    with pytest.raises(InvalidCloudPathError):
        sanitize_relative_path("../../etc/passwd")


def test_sanitize_relative_path_rejects_empty():
    from app.parcel_cloud_folders import sanitize_relative_path, InvalidCloudPathError

    with pytest.raises(InvalidCloudPathError):
        sanitize_relative_path("   ")


def test_sanitize_relative_path_normalizes_slashes():
    from app.parcel_cloud_folders import sanitize_relative_path

    assert sanitize_relative_path("/parcels/G016/") == "parcels/G016"
    assert sanitize_relative_path("parcels//G016") == "parcels/G016"


def test_join_dav_path_rejects_parent_traversal_in_filename():
    """sanitize_relative_path only ever sees the board-entered folder
    path -- the filename passed to download_file/upload_file comes
    straight from a query parameter / uploaded filename with no such
    check, so _join_dav_path itself must reject '..' (flagged by an
    external pentest)."""
    from app.cloud_storage import _join_dav_path, CloudStorageError

    with pytest.raises(CloudStorageError):
        _join_dav_path("parcels/G016", "../../etc/passwd")


async def test_nextcloud_download_rejects_traversal_filename():
    import httpx as httpx_module
    from app.cloud_storage import NextcloudProvider, CloudStorageError

    mock_client = httpx_module.AsyncClient(transport=_nextcloud_mock_transport())
    provider = NextcloudProvider(
        base_url="https://cloud.example.org", username="board", app_password="secret",
        client=mock_client,
    )
    with pytest.raises(CloudStorageError):
        await provider.download_file("parcels/G016", "../../other-parcel/secret.pdf")
    await provider.aclose()


# ---------------------------------------------------------------------------
# End-to-end: module flag, admin config, folder lifecycle, upload/download
# ---------------------------------------------------------------------------

async def web_login(client, email: str, password: str = "testpasswort123") -> None:
    response = await client.post("/auth/login", data={"email": email, "password": password})
    assert response.status_code in (302, 303)


async def _enable_cloud_storage(client, headers):
    response = await client.put(
        "/api/v1/club-settings/modul_cloud_storage", json={"value": "true"}, headers=headers,
    )
    assert response.status_code == 200, response.text


async def _create_member_and_parcel(client, headers, plot_number="G016"):
    member = (await client.post(
        "/api/v1/members", json={"first_name": "Ada", "last_name": "Gärtnerin"}, headers=headers,
    )).json()
    parcel = (await client.post(
        "/api/v1/parcels", json={"plot_number": plot_number}, headers=headers,
    )).json()
    assignment = (await client.post(
        f"/api/v1/parcels/{parcel['id']}/assignments",
        json={"member_id": member["id"], "parcel_id": parcel["id"]},
        headers=headers,
    )).json()
    return member, parcel, assignment


async def test_cloud_folder_disabled_by_default(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)

    response = await client.get("/api/v1/club-settings/modul_cloud_storage", headers=headers)
    if response.status_code == 200:
        assert response.json()["value"] not in ("true", "1", "ja", "an")


async def test_board_can_set_and_correct_folder_path(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _enable_cloud_storage(client, headers)
    _, parcel, _ = await _create_member_and_parcel(client, headers)

    await web_login(client, "admin@example.com")

    response = await client.post(
        f"/parcels/{parcel['id']}/cloud-folder",
        data={"relative_path": "kgv_dokumente/parzellen/G016/2026-01_G016_Gaertnerin"},
    )
    assert response.status_code in (302, 303)

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(ParcelCloudFolder).where(ParcelCloudFolder.parcel_id == parcel["id"])
        )
        folders = result.scalars().all()
    assert len(folders) == 1
    assert folders[0].is_active is True
    assert folders[0].relative_path == "kgv_dokumente/parzellen/G016/2026-01_G016_Gaertnerin"

    response = await client.post(
        f"/parcels/{parcel['id']}/cloud-folder",
        data={"relative_path": "kgv_dokumente/parzellen/G016/2026-01_G016_Gaertnerin_fixed"},
    )
    assert response.status_code in (302, 303)

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(ParcelCloudFolder).where(ParcelCloudFolder.parcel_id == parcel["id"])
        )
        folders = result.scalars().all()
    assert len(folders) == 1
    assert folders[0].relative_path.endswith("_fixed")


async def test_readonly_user_cannot_set_folder_path(client, admin_user):
    from app.models import User, UserRole
    from app.auth import hash_password

    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _enable_cloud_storage(client, headers)
    _, parcel, _ = await _create_member_and_parcel(client, headers)

    async with AsyncSessionLocal() as session:
        session.add(User(
            email="readonly@example.com", name="Nur Lesen",
            password_hash=hash_password("testpasswort123"), role=UserRole.READONLY,
        ))
        await session.commit()

    await web_login(client, "readonly@example.com")
    response = await client.post(
        f"/parcels/{parcel['id']}/cloud-folder",
        data={"relative_path": "kgv_dokumente/parzellen/G016/should-not-work"},
    )
    assert response.status_code == 403


async def test_folder_deactivates_when_last_resident_tenancy_ends(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _enable_cloud_storage(client, headers)
    _, parcel, assignment = await _create_member_and_parcel(client, headers)

    await web_login(client, "admin@example.com")
    await client.post(
        f"/parcels/{parcel['id']}/cloud-folder",
        data={"relative_path": "kgv_dokumente/parzellen/G016/2026-01_G016_Gaertnerin"},
    )

    response = await client.post(f"/parcels/{parcel['id']}/member/{assignment['id']}/remove")
    assert response.status_code in (302, 303)

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(ParcelCloudFolder).where(ParcelCloudFolder.parcel_id == parcel["id"])
        )
        folder = result.scalar_one()
    assert folder.is_active is False
    assert folder.deactivated_at is not None


async def test_folder_stays_active_when_a_coresident_remains(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _enable_cloud_storage(client, headers)

    member1, parcel, assignment1 = await _create_member_and_parcel(client, headers)
    member2 = (await client.post(
        "/api/v1/members", json={"first_name": "Bruno", "last_name": "Mitgärtner"}, headers=headers,
    )).json()
    await client.post(
        f"/api/v1/parcels/{parcel['id']}/assignments",
        json={"member_id": member2["id"], "parcel_id": parcel["id"]},
        headers=headers,
    )

    await web_login(client, "admin@example.com")
    await client.post(
        f"/parcels/{parcel['id']}/cloud-folder",
        data={"relative_path": "kgv_dokumente/parzellen/G016/2026-01_G016_shared"},
    )

    response = await client.post(f"/parcels/{parcel['id']}/member/{assignment1['id']}/remove")
    assert response.status_code in (302, 303)

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(ParcelCloudFolder).where(ParcelCloudFolder.parcel_id == parcel["id"])
        )
        folder = result.scalar_one()
    assert folder.is_active is True


async def test_upload_and_download_use_configured_folder(client, admin_user, monkeypatch):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _enable_cloud_storage(client, headers)
    _, parcel, _ = await _create_member_and_parcel(client, headers)

    await web_login(client, "admin@example.com")
    await client.post(
        f"/parcels/{parcel['id']}/cloud-folder",
        data={"relative_path": "kgv_dokumente/parzellen/G016/2026-01_G016_Gaertnerin"},
    )

    import httpx as httpx_module
    from app.cloud_storage import NextcloudProvider as RealNextcloudProvider

    mock_client = httpx_module.AsyncClient(transport=_nextcloud_mock_transport(get_body=b"lease contents"))

    async def fake_get_nextcloud_provider(db, client=None):
        return RealNextcloudProvider(
            base_url="https://cloud.example.org", username="board", app_password="secret",
            client=mock_client,
        )

    monkeypatch.setattr("app.routers.parcels.get_nextcloud_provider", fake_get_nextcloud_provider)

    upload_response = await client.post(
        f"/parcels/{parcel['id']}/cloud-folder/upload",
        files={"file": ("lease.pdf", b"new lease bytes", "application/pdf")},
    )
    assert upload_response.status_code in (302, 303)
    assert "cloud_upload_ok" in upload_response.headers["location"]

    download_response = await client.get(
        f"/parcels/{parcel['id']}/cloud-folder/download", params={"filename": "lease.pdf"},
    )
    assert download_response.status_code == 200
    assert download_response.content == b"lease contents"


async def test_cloud_storage_module_disabled_returns_404(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    _, parcel, _ = await _create_member_and_parcel(client, headers)

    await web_login(client, "admin@example.com")
    response = await client.post(
        f"/parcels/{parcel['id']}/cloud-folder",
        data={"relative_path": "kgv_dokumente/parzellen/G016/should-not-work"},
    )
    assert response.status_code == 404


async def test_parcel_detail_page_renders_cloud_documents_card(client, admin_user, monkeypatch):
    """Regression coverage for the Documents card in parcels/detail.html
    -- none of the other tests here ever GET that page with an active
    folder configured, so a template bug (bad variable name, unclosed
    tag) would otherwise go uncaught."""
    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _enable_cloud_storage(client, headers)
    _, parcel, _ = await _create_member_and_parcel(client, headers)

    await web_login(client, "admin@example.com")
    await client.post(
        f"/parcels/{parcel['id']}/cloud-folder",
        data={"relative_path": "kgv_dokumente/parzellen/G016/2026-01_G016_Gaertnerin"},
    )

    import httpx as httpx_module
    from app.cloud_storage import NextcloudProvider as RealNextcloudProvider

    mock_client = httpx_module.AsyncClient(transport=_nextcloud_mock_transport())

    async def fake_get_nextcloud_provider(db, client=None):
        return RealNextcloudProvider(
            base_url="https://cloud.example.org", username="board", app_password="secret",
            client=mock_client,
        )

    monkeypatch.setattr("app.routers.parcels.get_nextcloud_provider", fake_get_nextcloud_provider)

    response = await client.get(f"/parcels/{parcel['id']}")
    assert response.status_code == 200
    assert "kgv_dokumente/parzellen/G016/2026-01_G016_Gaertnerin" in response.text
    assert "lease.pdf" in response.text
    assert "photos" in response.text


async def test_parcel_detail_page_renders_without_cloud_folder_configured(client, admin_user):
    """Same page, cloud storage enabled but no folder set yet -- makes
    sure the "no folder configured" branch of the template also renders
    without error."""
    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _enable_cloud_storage(client, headers)
    _, parcel, _ = await _create_member_and_parcel(client, headers)

    await web_login(client, "admin@example.com")
    response = await client.get(f"/parcels/{parcel['id']}")
    assert response.status_code == 200


# ---------------------------------------------------------------------------
# Browsing into subfolders (issue #201) -- folders in the listing were
# rendered but had no link, so a board member could see "photos" exists
# but never actually open it. A _RecordingProvider (rather than the
# httpx mock transport used above) is used here so tests can assert on
# exactly which path each route asked the connector for, without needing
# the mock transport to parse and branch on the WebDAV request path.
# ---------------------------------------------------------------------------

class _RecordingProvider:
    def __init__(self, files_by_path=None):
        self.list_files_calls = []
        self.download_calls = []
        self.upload_calls = []
        self._files_by_path = files_by_path or {}

    async def list_files(self, path):
        self.list_files_calls.append(path)
        return self._files_by_path.get(path, [])

    async def upload_file(self, path, filename, content):
        self.upload_calls.append((path, filename, content))

    async def download_file(self, path, filename):
        self.download_calls.append((path, filename))
        return b"file bytes"

    async def aclose(self):
        pass


async def _setup_folder_with_recording_provider(client, admin_user, monkeypatch, files_by_path=None):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _enable_cloud_storage(client, headers)
    _, parcel, _ = await _create_member_and_parcel(client, headers)

    await web_login(client, "admin@example.com")
    await client.post(
        f"/parcels/{parcel['id']}/cloud-folder",
        data={"relative_path": "kgv_dokumente/parzellen/G016/2026-01_G016_Gaertnerin"},
    )

    provider = _RecordingProvider(files_by_path)

    async def fake_get_nextcloud_provider(db, client=None):
        return provider

    monkeypatch.setattr("app.routers.parcels.get_nextcloud_provider", fake_get_nextcloud_provider)
    return parcel, provider


async def test_folder_entry_links_into_subfolder(client, admin_user, monkeypatch):
    from app.cloud_storage import CloudFileEntry

    root = "kgv_dokumente/parzellen/G016/2026-01_G016_Gaertnerin"
    parcel, provider = await _setup_folder_with_recording_provider(
        client, admin_user, monkeypatch,
        files_by_path={root: [CloudFileEntry(name="photos", is_directory=True)]},
    )

    response = await client.get(f"/parcels/{parcel['id']}")
    assert response.status_code == 200
    assert provider.list_files_calls == [root]
    assert f"/parcels/{parcel['id']}?cloud_path=photos#cloud-documents" in response.text


async def test_navigating_into_subfolder_lists_the_right_path(client, admin_user, monkeypatch):
    from app.cloud_storage import CloudFileEntry

    root = "kgv_dokumente/parzellen/G016/2026-01_G016_Gaertnerin"
    parcel, provider = await _setup_folder_with_recording_provider(
        client, admin_user, monkeypatch,
        files_by_path={f"{root}/photos": [CloudFileEntry(name="2026.jpg", is_directory=False)]},
    )

    response = await client.get(f"/parcels/{parcel['id']}", params={"cloud_path": "photos"})
    assert response.status_code == 200
    assert provider.list_files_calls == [f"{root}/photos"]
    assert "2026.jpg" in response.text
    # Breadcrumb: root folder name is a link back to cloud_path="", "photos" is the current (non-link) crumb.
    assert f"/parcels/{parcel['id']}?cloud_path=#cloud-documents" in response.text


async def test_download_link_carries_current_browse_path(client, admin_user, monkeypatch):
    from app.cloud_storage import CloudFileEntry

    root = "kgv_dokumente/parzellen/G016/2026-01_G016_Gaertnerin"
    parcel, provider = await _setup_folder_with_recording_provider(
        client, admin_user, monkeypatch,
        files_by_path={f"{root}/photos": [CloudFileEntry(name="2026.jpg", is_directory=False)]},
    )

    response = await client.get(f"/parcels/{parcel['id']}", params={"cloud_path": "photos"})
    assert "filename=2026.jpg&cloud_path=photos" in response.text

    download_response = await client.get(
        f"/parcels/{parcel['id']}/cloud-folder/download",
        params={"filename": "2026.jpg", "cloud_path": "photos"},
    )
    assert download_response.status_code == 200
    assert provider.download_calls == [(f"{root}/photos", "2026.jpg")]


async def test_upload_lands_in_currently_browsed_subfolder(client, admin_user, monkeypatch):
    root = "kgv_dokumente/parzellen/G016/2026-01_G016_Gaertnerin"
    parcel, provider = await _setup_folder_with_recording_provider(client, admin_user, monkeypatch)

    response = await client.post(
        f"/parcels/{parcel['id']}/cloud-folder/upload",
        data={"cloud_path": "photos"},
        files={"file": ("2026.jpg", b"jpeg bytes", "image/jpeg")},
    )
    assert response.status_code in (302, 303)
    assert "cloud_path=photos" in response.headers["location"]
    assert provider.upload_calls == [(f"{root}/photos", "2026.jpg", b"jpeg bytes")]


async def test_cloud_path_traversal_attempt_falls_back_to_root(client, admin_user, monkeypatch):
    root = "kgv_dokumente/parzellen/G016/2026-01_G016_Gaertnerin"
    parcel, provider = await _setup_folder_with_recording_provider(client, admin_user, monkeypatch)

    response = await client.get(f"/parcels/{parcel['id']}", params={"cloud_path": "../../etc"})
    assert response.status_code == 200
    assert provider.list_files_calls == [root]


# ---------------------------------------------------------------------------
# Folder picker: browsing the Nextcloud account tree from its root to pick
# a parcel's *initial* relative_path, instead of hand-typing it. Kept fully
# separate from the cloud_path browsing above (which only ever browses
# *within* an already-saved folder) -- see docs/module-cloud-storage.md.
# ---------------------------------------------------------------------------

async def test_picker_mode_lists_directories_only_at_root(client, admin_user, monkeypatch):
    from app.cloud_storage import CloudFileEntry

    parcel, provider = await _setup_folder_with_recording_provider(
        client, admin_user, monkeypatch,
        files_by_path={"": [
            CloudFileEntry(name="kgv_dokumente", is_directory=True),
            CloudFileEntry(name="notes.txt", is_directory=False),
        ]},
    )

    response = await client.get(f"/parcels/{parcel['id']}", params={"cloud_pick": "1"})
    assert response.status_code == 200
    assert provider.list_files_calls[-1] == ""
    assert "kgv_dokumente" in response.text
    assert "notes.txt" not in response.text


async def test_picker_mode_navigates_into_subfolder(client, admin_user, monkeypatch):
    parcel, provider = await _setup_folder_with_recording_provider(client, admin_user, monkeypatch)

    response = await client.get(
        f"/parcels/{parcel['id']}", params={"cloud_pick": "1", "pick_path": "kgv_dokumente"},
    )
    assert response.status_code == 200
    assert provider.list_files_calls[-1] == "kgv_dokumente"


async def test_picker_mode_available_without_existing_cloud_folder(client, admin_user, monkeypatch):
    from app.cloud_storage import CloudFileEntry

    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _enable_cloud_storage(client, headers)
    _, parcel, _ = await _create_member_and_parcel(client, headers)

    provider = _RecordingProvider({"": [CloudFileEntry(name="kgv_dokumente", is_directory=True)]})

    async def fake_get_nextcloud_provider(db, client=None):
        return provider

    monkeypatch.setattr("app.routers.parcels.get_nextcloud_provider", fake_get_nextcloud_provider)

    await web_login(client, "admin@example.com")
    response = await client.get(f"/parcels/{parcel['id']}", params={"cloud_pick": "1"})
    assert response.status_code == 200
    assert "kgv_dokumente" in response.text


async def test_picker_mode_use_this_folder_saves_current_path(client, admin_user, monkeypatch):
    parcel, provider = await _setup_folder_with_recording_provider(client, admin_user, monkeypatch)

    response = await client.get(
        f"/parcels/{parcel['id']}", params={"cloud_pick": "1", "pick_path": "kgv_dokumente/neu"},
    )
    assert 'value="kgv_dokumente/neu"' in response.text

    save_response = await client.post(
        f"/parcels/{parcel['id']}/cloud-folder",
        data={"relative_path": "kgv_dokumente/neu"},
    )
    assert save_response.status_code in (302, 303)
    assert "cloud_folder_saved=1" in save_response.headers["location"]

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(ParcelCloudFolder).where(
                ParcelCloudFolder.parcel_id == parcel["id"], ParcelCloudFolder.is_active.is_(True),
            )
        )
        assert result.scalar_one().relative_path == "kgv_dokumente/neu"


async def test_picker_mode_cloud_storage_error_shows_alert(client, admin_user, monkeypatch):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _enable_cloud_storage(client, headers)
    _, parcel, _ = await _create_member_and_parcel(client, headers)

    class _FailingProvider:
        async def list_files(self, path):
            from app.cloud_storage import CloudStorageError
            raise CloudStorageError("Nextcloud is temporarily unreachable.")

        async def aclose(self):
            pass

    async def fake_get_nextcloud_provider(db, client=None):
        return _FailingProvider()

    monkeypatch.setattr("app.routers.parcels.get_nextcloud_provider", fake_get_nextcloud_provider)

    await web_login(client, "admin@example.com")
    response = await client.get(f"/parcels/{parcel['id']}", params={"cloud_pick": "1"})
    assert response.status_code == 200
    assert "Nextcloud is temporarily unreachable." in response.text
