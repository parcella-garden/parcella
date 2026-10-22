"""
Cloud storage providers (ADR 0106): the generic WebDAV provider, the
S3 provider (incl. the SigV4 signature against AWS's documented
example), and the one-storage-at-a-time dropdown and API.

NextcloudProvider's own tests live in tests/test_cloud_storage.py.
"""
from datetime import datetime, timezone
from urllib.parse import parse_qs, urlsplit

import httpx
import pytest

from app.cloud_storage import (
    CloudStorageError, NextcloudProvider, S3Provider, WebDAVProvider, _EMPTY_SHA256, sigv4_headers,
)
from tests.conftest import auth_header, login


# ---------------------------------------------------------------------------
# SigV4
# ---------------------------------------------------------------------------

def test_sigv4_matches_the_aws_documentation_example():
    # "GET Object" example from the AWS S3 SigV4 documentation.
    headers = sigv4_headers(
        method="GET", host="examplebucket.s3.amazonaws.com", path="/test.txt", query={},
        headers={"Range": "bytes=0-9"}, payload_hash=_EMPTY_SHA256,
        access_key_id="AKIAIOSFODNN7EXAMPLE", secret_access_key="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
        region="us-east-1", now=datetime(2013, 5, 24, tzinfo=timezone.utc),
    )
    assert headers["Authorization"] == (
        "AWS4-HMAC-SHA256 Credential=AKIAIOSFODNN7EXAMPLE/20130524/us-east-1/s3/aws4_request, "
        "SignedHeaders=host;range;x-amz-content-sha256;x-amz-date, "
        "Signature=f0e8bdb87c964420e857bd35b5d6ed310bd44f0170aba48dd91039c6036bdb41"
    )


# ---------------------------------------------------------------------------
# Generic WebDAV
# ---------------------------------------------------------------------------

_LISTING = """<?xml version="1.0"?>
<d:multistatus xmlns:d="DAV:">
  <d:response><d:href>https://dav.example.com/dav/club/Parzellen%20Alt/</d:href>
    <d:propstat><d:prop><d:resourcetype><d:collection/></d:resourcetype></d:prop></d:propstat></d:response>
  <d:response><d:href>/dav/club/Parzellen%20Alt/G%C3%BCnther/</d:href>
    <d:propstat><d:prop><d:resourcetype><d:collection/></d:resourcetype></d:prop></d:propstat></d:response>
  <d:response><d:href>/dav/club/Parzellen%20Alt/Vertrag%20(1).pdf</d:href>
    <d:propstat><d:prop><d:getcontentlength>42</d:getcontentlength><d:resourcetype/></d:prop></d:propstat></d:response>
</d:multistatus>"""


async def test_webdav_listing_works_with_full_url_and_path_hrefs():
    seen = []

    def handler(request):
        seen.append((request.method, request.url.raw_path.decode()))
        return httpx.Response(207, text=_LISTING)

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    provider = WebDAVProvider("https://dav.example.com/dav/club", "u", "p", client=client)
    entries = await provider.list_files("Parzellen Alt")

    assert seen == [("PROPFIND", "/dav/club/Parzellen%20Alt")]
    assert [(e.name, e.is_directory, e.size) for e in entries] == [
        ("Günther", True, None), ("Vertrag (1).pdf", False, 42),
    ]
    await client.aclose()


async def test_webdav_rejects_dot_dot_and_reports_bad_credentials():
    client = httpx.AsyncClient(transport=httpx.MockTransport(lambda r: httpx.Response(401)))
    provider = WebDAVProvider("https://dav.example.com/dav", "u", "wrong", client=client)
    with pytest.raises(CloudStorageError, match=r"\.\."):
        await provider.download_file("docs", "../../secret")
    with pytest.raises(CloudStorageError, match="rejected the credentials"):
        await provider.test_connection()
    await client.aclose()


def test_nextcloud_is_webdav_with_the_user_root():
    provider = NextcloudProvider("https://cloud.example.com/", "Vor stand", "pw")
    assert isinstance(provider, WebDAVProvider)
    assert provider._dav_root == "https://cloud.example.com/remote.php/dav/files/Vor%20stand"


# ---------------------------------------------------------------------------
# S3
# ---------------------------------------------------------------------------

_S3_LIST = """<?xml version="1.0" encoding="UTF-8"?>
<ListBucketResult xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
  <IsTruncated>false</IsTruncated>
  <Contents><Key>club/parcels/G016/</Key><Size>0</Size></Contents>
  <Contents><Key>club/parcels/G016/Pachtvertrag Müller.pdf</Key><Size>13</Size><LastModified>2026-10-22T10:00:00Z</LastModified></Contents>
  <CommonPrefixes><Prefix>club/parcels/G016/Unterlagen/</Prefix></CommonPrefixes>
</ListBucketResult>"""


def _s3(handler):
    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    return S3Provider(
        "https://s3.example.com", "eu-central-1", "verein", "AKID", "secret", path_prefix="club", client=client,
    ), client


async def test_s3_listing_uses_prefix_and_delimiter():
    seen = []

    def handler(request):
        seen.append(request)
        return httpx.Response(200, text=_S3_LIST)

    provider, client = _s3(handler)
    entries = await provider.list_files("parcels/G016")

    request = seen[0]
    assert request.url.path == "/verein"
    assert parse_qs(urlsplit(str(request.url)).query)["prefix"] == ["club/parcels/G016/"]
    assert request.headers["Authorization"].startswith("AWS4-HMAC-SHA256 Credential=AKID/")
    assert "/eu-central-1/s3/aws4_request" in request.headers["Authorization"]
    assert [(e.name, e.is_directory, e.size) for e in entries] == [
        ("Unterlagen", True, None), ("Pachtvertrag Müller.pdf", False, 13),
    ]
    await client.aclose()


async def test_s3_missing_folder_is_reported_like_webdav():
    empty = """<ListBucketResult xmlns="http://s3.amazonaws.com/doc/2006-03-01/"><IsTruncated>false</IsTruncated></ListBucketResult>"""

    def handler(request):
        if request.method == "HEAD":
            return httpx.Response(404)
        return httpx.Response(200, text=empty)

    provider, client = _s3(handler)
    with pytest.raises(CloudStorageError, match="was not found"):
        await provider.list_files("nowhere")
    await client.aclose()


async def test_s3_upload_quotes_the_key_and_signs_the_payload():
    seen = []

    def handler(request):
        seen.append(request)
        return httpx.Response(200)

    provider, client = _s3(handler)
    await provider.upload_file("parcels/G016", "Vertrag (1) ä.pdf", b"%PDF")
    request = seen[0]
    assert request.method == "PUT"
    assert request.url.raw_path.decode() == "/verein/club/parcels/G016/Vertrag%20%281%29%20%C3%A4.pdf"
    assert request.headers["x-amz-content-sha256"] != _EMPTY_SHA256
    await client.aclose()


async def test_s3_create_folder_writes_markers_for_each_level():
    seen = []

    def handler(request):
        seen.append((request.method, request.url.raw_path.decode()))
        return httpx.Response(200)

    provider, client = _s3(handler)
    await provider.create_folder("a/b")
    assert seen == [("PUT", "/verein/club/a/"), ("PUT", "/verein/club/a/b/")]
    await client.aclose()


async def test_s3_access_denied_is_a_clear_error():
    provider, client = _s3(lambda request: httpx.Response(403, text="<Error/>"))
    with pytest.raises(CloudStorageError, match="rejected the credentials"):
        await provider.test_connection()
    await client.aclose()


# ---------------------------------------------------------------------------
# Admin card and API: one storage at a time
# ---------------------------------------------------------------------------

async def web_login(client, email: str, password: str = "testpasswort123") -> None:
    response = await client.post("/auth/login", data={"email": email, "password": password})
    assert response.status_code in (302, 303)


async def test_switching_storage_keeps_the_other_settings(client, admin_user):
    await web_login(client, "admin@example.com")
    await client.post("/admin/integrations/cloud-storage", data={
        "cloud_storage_provider": "nextcloud",
        "cloud_storage_nextcloud_base_url": "https://cloud.example.com",
        "cloud_storage_nextcloud_username": "board",
        "cloud_storage_nextcloud_app_password": "nc-secret",
    })
    response = await client.post("/admin/integrations/cloud-storage", data={
        "cloud_storage_provider": "s3",
        "cloud_storage_s3_endpoint_url": "https://s3.example.com",
        "cloud_storage_s3_bucket": "verein",
        "cloud_storage_s3_access_key_id": "AKID",
        "cloud_storage_s3_secret_access_key": "s3-secret",
    })
    assert "cloud_storage_saved=1" in response.headers["location"]

    from app.cloud_storage import CLOUD_STORAGE, get_cloud_storage_provider
    from app.database import AsyncSessionLocal

    async with AsyncSessionLocal() as session:
        active = await get_cloud_storage_provider(session)
        assert isinstance(active, S3Provider)
        assert active.region == "us-east-1"  # default applied
        assert (await CLOUD_STORAGE.load_config(session, "nextcloud"))["app_password"] == "nc-secret"
        await active.aclose()

    page = await client.get("/admin/integrations")
    assert 'value="s3" selected' in page.text
    assert "s3-secret" not in page.text and "nc-secret" not in page.text


async def test_cloud_storage_path_prefix_rejects_dot_dot(client, admin_user):
    await web_login(client, "admin@example.com")
    response = await client.post("/admin/integrations/cloud-storage", data={
        "cloud_storage_provider": "s3", "cloud_storage_s3_path_prefix": "club/../other",
    })
    assert "cloud_storage_error=" in response.headers["location"]


async def test_cloud_storage_test_button_reports_failure(client, admin_user, monkeypatch):
    await web_login(client, "admin@example.com")

    async def fake_build(db, provider_type, config):
        return WebDAVProvider(
            config["root_url"], config["username"], config["password"],
            client=httpx.AsyncClient(transport=httpx.MockTransport(lambda r: httpx.Response(401))),
        )

    monkeypatch.setattr("app.routers.admin.CLOUD_STORAGE.build", fake_build)
    response = await client.post("/admin/integrations/cloud-storage/test", data={
        "cloud_storage_provider": "webdav",
        "cloud_storage_webdav_root_url": "https://dav.example.com/dav",
        "cloud_storage_webdav_username": "u",
        "cloud_storage_webdav_password": "wrong",
    })
    assert "cloud_storage_test=failed" in response.headers["location"]


async def test_cloud_storage_api_is_admin_only_and_hides_secrets(client, admin_user, board_user):
    await web_login(client, "admin@example.com")
    await client.post("/admin/integrations/cloud-storage", data={
        "cloud_storage_provider": "webdav",
        "cloud_storage_webdav_root_url": "https://dav.example.com/dav",
        "cloud_storage_webdav_username": "u",
        "cloud_storage_webdav_password": "dav-secret",
    })
    token = await login(client, "admin@example.com")

    types = await client.get("/api/v1/cloud-storage/providers", headers=auth_header(token))
    assert {t["type"] for t in types.json()} == {"nextcloud", "webdav", "s3"}

    current = await client.get("/api/v1/cloud-storage", headers=auth_header(token))
    assert current.json()["active"] == "webdav"
    assert current.json()["secrets_set"]["webdav"] == {"password": True}
    assert "dav-secret" not in current.text

    refused = await client.put("/api/v1/cloud-storage", headers=auth_header(token), json={
        "active": "webdav", "values": {"password": "x"},
    })
    assert refused.status_code == 403

    board_token = await login(client, "vorstand@example.com")
    assert (await client.get("/api/v1/cloud-storage", headers=auth_header(board_token))).status_code == 403
