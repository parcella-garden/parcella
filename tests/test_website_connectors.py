"""
Website connectors (ADR 0104/0105): the Markdown folder connector
against an in-memory cloud storage, the Parcella plugin connector
against a mocked CMS (including its HMAC signature), the one-CMS-at-a-
time dropdown on Admin -> Integrations, and the website REST API.

The WordPress connector's own tests live in tests/test_announcements.py.
"""
import json
import time
from datetime import date

import httpx
import pytest

from app.cloud_storage import CloudFileEntry, CloudStorageError, CloudStorageProvider
from app.website_connectors import BlogPostNotFoundError, BlogPublishError, DraftContent
from app.website_connectors.markdown_folder import (
    MarkdownFolderPublisher, _header_value, _is_draft, slugify, split_front_matter, summarize,
)
from app.website_connectors.parcella_plugin import PROTOCOL, ParcellaPluginPublisher, sign
from tests.conftest import auth_header, login

from tests.test_announcements import _TINY_PNG_BYTES  # noqa: E402


class InMemoryStorage(CloudStorageProvider):
    """Folders must exist before files go in, like on Nextcloud."""

    def __init__(self, folders=()):
        self.folders = {f.strip("/") for f in folders}
        self.files = {}

    async def test_connection(self):
        return None

    async def list_files(self, path):
        path = path.strip("/")
        if path not in self.folders:
            raise CloudStorageError(f"Folder '{path}' was not found.")
        return [CloudFileEntry(name=name, is_directory=False) for (folder, name) in self.files if folder == path]

    async def upload_file(self, path, filename, content):
        path = path.strip("/")
        if path not in self.folders:
            raise CloudStorageError(f"Folder '{path}' likely doesn't exist.")
        self.files[(path, filename)] = content

    async def download_file(self, path, filename):
        try:
            return self.files[(path.strip("/"), filename)]
        except KeyError:
            raise CloudStorageError(f"File '{filename}' was not found in '{path}'.")

    async def delete_file(self, path, filename):
        self.files.pop((path.strip("/"), filename), None)

    async def create_folder(self, path):
        accumulated = ""
        for segment in path.strip("/").split("/"):
            accumulated = f"{accumulated}/{segment}" if accumulated else segment
            self.folders.add(accumulated)

    async def aclose(self):
        return None

    def text(self, filename, folder="site/content/posts"):
        return self.files[(folder, filename)].decode("utf-8")


MD_CONFIG = {
    "posts_path": "site/content/posts",
    "media_path": "site/content/media",
    "media_url_prefix": "/media",
    "site_url": "https://club.example.org",
    "filename_pattern": "{date}-{slug}.md",
    "url_pattern": "/{slug}.html",
    "author": "Vorstand",
    "categories": "aktuelles, newsletter",
}


def _md_connector(storage=None):
    storage = storage or InMemoryStorage(["site/content/posts", "site/content/media"])
    return MarkdownFolderPublisher(storage, dict(MD_CONFIG)), storage


def _content(**overrides):
    values = dict(
        title='Wasser wird am 11. April wieder angestellt: "Größe" zählt',
        markdown="## Hinweis\n\nAb dem **11. April** gibt es wieder Wasser in der Anlage.\n\nMehr Text.",
        html="<p>irrelevant</p>", source_id="ann-1",
    )
    values.update(overrides)
    return DraftContent(**values)


# ---------------------------------------------------------------------------
# Markdown folder connector
# ---------------------------------------------------------------------------

def test_slugify_follows_the_site_rules():
    assert slugify("Wasser wird am 11. April wieder angestellt – Größe") == "wasser-wird-am-11-april-wieder-angestellt-groesse"
    assert slugify("../../etc/passwd") == "etc-passwd"
    assert slugify("!!!") == "post"
    assert len(slugify("x" * 300)) <= 80


def test_summary_is_the_first_real_paragraph_as_plain_text():
    assert summarize("## Title\n\nSome **bold** and a [link](https://x).\n\nSecond.") == "Some bold and a link."


async def test_markdown_draft_is_written_with_header_and_draft_flag():
    connector, storage = _md_connector()
    result = await connector.publish_draft(_content())

    today = date.today()
    expected_name = f"{today:%Y%m%d}-wasser-wird-am-11-april-wieder-angestellt-groesse-zaehlt.md"
    assert result.post_id == expected_name
    assert result.location == f"site/content/posts/{expected_name}"
    assert result.edit_url is None

    header, body = split_front_matter(storage.text(expected_name))
    assert _header_value(header, "title") == 'Wasser wird am 11. April wieder angestellt: "Größe" zählt'
    assert _header_value(header, "date") == today.isoformat()
    assert _header_value(header, "url") == "/wasser-wird-am-11-april-wieder-angestellt-groesse-zaehlt.html"
    assert _header_value(header, "author") == "Vorstand"
    assert 'categories: ["aktuelles", "newsletter"]' in header
    assert _header_value(header, "summary") == "Ab dem 11. April gibt es wieder Wasser in der Anlage."
    assert header[-1] == "draft: true"
    assert _is_draft(header)
    assert body.startswith("## Hinweis")


async def test_markdown_draft_image_goes_into_year_month_folder():
    connector, storage = _md_connector()
    result = await connector.publish_draft(_content(
        image_bytes=_TINY_PNG_BYTES, image_filename="abc.png", image_mime="image/png",
    ))
    today = date.today()
    image_files = [(f, n) for (f, n) in storage.files if f == f"site/content/media/{today:%Y}/{today:%m}"]
    assert len(image_files) == 1 and image_files[0][1].endswith(".png")

    header, _ = split_front_matter(storage.text(result.post_id))
    assert _header_value(header, "image") == f"/media/{today:%Y}/{today:%m}/{image_files[0][1]}"


async def test_markdown_name_collision_gets_a_suffix():
    connector, storage = _md_connector()
    first = await connector.publish_draft(_content(title="Arbeitseinsatz"))
    second = await connector.publish_draft(_content(title="Arbeitseinsatz"))
    assert first.post_id != second.post_id
    assert second.post_id.endswith("-arbeitseinsatz-2.md")
    header, _ = split_front_matter(storage.text(second.post_id))
    assert _header_value(header, "url") == "/arbeitseinsatz-2.html"


async def test_markdown_update_keeps_what_a_human_changed():
    connector, storage = _md_connector()
    result = await connector.publish_draft(_content(
        image_bytes=_TINY_PNG_BYTES, image_filename="abc.png", image_mime="image/png",
    ))

    # A board member publishes the post (deletes "draft: true") and
    # changes the categories by hand.
    text = storage.text(result.post_id)
    text = text.replace("draft: true\n", "").replace('["aktuelles", "newsletter"]', '["freie-gaerten"]')
    storage.files[("site/content/posts", result.post_id)] = text.encode("utf-8")
    old_header, _ = split_front_matter(text)
    old_image = _header_value(old_header, "image")

    await connector.update_post(result.post_id, _content(title="Neuer Titel", markdown="Neuer Text."))

    header, body = split_front_matter(storage.text(result.post_id))
    assert _header_value(header, "title") == "Neuer Titel"
    assert body.strip() == "Neuer Text."
    assert not _is_draft(header)  # never re-added
    assert 'categories: ["freie-gaerten"]' in header
    assert _header_value(header, "image") == old_image  # image unchanged -> kept
    assert len([k for k in storage.files if k[0] == "site/content/posts"]) == 1


async def test_markdown_update_can_remove_the_image():
    connector, storage = _md_connector()
    result = await connector.publish_draft(_content(
        image_bytes=_TINY_PNG_BYTES, image_filename="abc.png", image_mime="image/png",
    ))
    await connector.update_post(result.post_id, _content(), image_changed=True)
    header, _ = split_front_matter(storage.text(result.post_id))
    assert _header_value(header, "image") is None
    assert _is_draft(header)


async def test_markdown_update_of_deleted_file_raises_not_found():
    connector, _storage = _md_connector()
    with pytest.raises(BlogPostNotFoundError):
        await connector.update_post("20260101-gone.md", _content())


async def test_markdown_update_rejects_a_path_as_post_id():
    connector, _storage = _md_connector()
    with pytest.raises(BlogPublishError):
        await connector.update_post("../secret.md", _content())


async def test_markdown_public_url_only_once_published():
    connector, storage = _md_connector()
    result = await connector.publish_draft(_content(title="Kartoffeln"))
    assert await connector.get_public_url_if_published(result.post_id) is None

    text = storage.text(result.post_id).replace("draft: true\n", "")
    storage.files[("site/content/posts", result.post_id)] = text.encode("utf-8")
    assert await connector.get_public_url_if_published(result.post_id) == "https://club.example.org/kartoffeln.html"


async def test_markdown_bad_filename_pattern_is_a_clear_error():
    storage = InMemoryStorage(["site/content/posts"])
    connector = MarkdownFolderPublisher(storage, {**MD_CONFIG, "filename_pattern": "{year}/{slug}.md"})
    with pytest.raises(BlogPublishError):
        await connector.publish_draft(_content())


async def test_markdown_test_connection_reports_missing_folder():
    connector = MarkdownFolderPublisher(InMemoryStorage([]), dict(MD_CONFIG))
    with pytest.raises(BlogPublishError):
        await connector.test_connection()


# ---------------------------------------------------------------------------
# Parcella plugin connector (docs/website-plugin-protocol.md)
# ---------------------------------------------------------------------------

SECRET = "s3cret-shared-with-the-plugin"


def _plugin_transport(seen, *, protocol=PROTOCOL, draft_status="draft", update_status=200):
    def handler(request: httpx.Request) -> httpx.Response:
        timestamp = request.headers["X-Parcella-Timestamp"]
        assert abs(int(timestamp) - time.time()) < 60
        expected = sign(SECRET, timestamp, request.method, request.url.path, request.content)
        if request.headers.get("X-Parcella-Signature") != expected:
            return httpx.Response(401, json={"error": "bad signature"})
        seen.append((request.method, request.url.path, json.loads(request.content) if request.content else None))

        if request.url.path.endswith("/ping"):
            return httpx.Response(200, json={"protocol": protocol, "name": "Test CMS", "version": "1.0.0"})
        if request.method == "POST" and request.url.path.endswith("/drafts"):
            return httpx.Response(201, json={"id": "42", "edit_url": "https://cms.example.org/edit/42"})
        if request.method == "PUT":
            if update_status != 200:
                return httpx.Response(update_status, json={"error": "gone"})
            return httpx.Response(200, json={"id": "42", "edit_url": "https://cms.example.org/edit/42"})
        if request.method == "GET" and "/drafts/" in request.url.path:
            return httpx.Response(200, json={"status": draft_status, "public_url": "https://cms.example.org/news/42"})
        return httpx.Response(404)

    return httpx.MockTransport(handler)


def _plugin(seen, secret=SECRET, **kwargs):
    client = httpx.AsyncClient(transport=_plugin_transport(seen, **kwargs))
    return ParcellaPluginPublisher("https://cms.example.org/parcella/v1", secret, client=client), client


async def test_plugin_draft_is_signed_and_carries_the_content():
    seen = []
    connector, client = _plugin(seen)
    await connector.test_connection()
    result = await connector.publish_draft(_content(
        image_bytes=_TINY_PNG_BYTES, image_filename="abc.png", image_mime="image/png",
    ))
    assert result.post_id == "42"
    assert result.edit_url == "https://cms.example.org/edit/42"

    method, path, body = seen[-1]
    assert (method, path) == ("POST", "/parcella/v1/drafts")
    assert body["markdown"].startswith("## Hinweis")
    assert body["source_id"] == "ann-1"
    assert body["image"]["mime"] == "image/png"
    await client.aclose()


async def test_plugin_rejects_a_wrong_secret():
    seen = []
    connector, client = _plugin(seen, secret="wrong")
    with pytest.raises(BlogPublishError, match="shared secret"):
        await connector.test_connection()
    await client.aclose()


async def test_plugin_protocol_mismatch_fails_the_test():
    seen = []
    connector, client = _plugin(seen, protocol="parcella-website/99")
    with pytest.raises(BlogPublishError, match="expects"):
        await connector.test_connection()
    await client.aclose()


async def test_plugin_update_without_image_change_sends_no_image_key():
    seen = []
    connector, client = _plugin(seen)
    await connector.update_post("42", _content())
    method, path, body = seen[-1]
    assert (method, path) == ("PUT", "/parcella/v1/drafts/42")
    assert "image" not in body
    await client.aclose()


async def test_plugin_update_of_deleted_draft_raises_not_found():
    seen = []
    connector, client = _plugin(seen, update_status=404)
    with pytest.raises(BlogPostNotFoundError):
        await connector.update_post("42", _content())
    await client.aclose()


async def test_plugin_public_url_only_when_published():
    seen = []
    connector, client = _plugin(seen)
    assert await connector.get_public_url_if_published("42") is None
    await client.aclose()

    connector, client = _plugin(seen, draft_status="published")
    assert await connector.get_public_url_if_published("42") == "https://cms.example.org/news/42"
    await client.aclose()


# ---------------------------------------------------------------------------
# Admin -> Integrations -> Website: one dropdown, one CMS at a time
# ---------------------------------------------------------------------------

async def web_login(client, email: str, password: str = "testpasswort123") -> None:
    response = await client.post("/auth/login", data={"email": email, "password": password})
    assert response.status_code in (302, 303)


async def test_switching_the_dropdown_keeps_the_other_settings(client, admin_user):
    await web_login(client, "admin@example.com")
    await client.post("/admin/integrations/website", data={
        "website_connector": "wordpress",
        "website_wordpress_site_url": "https://blog.example.com",
        "website_wordpress_username": "board",
        "website_wordpress_app_password": "pw",
    })
    response = await client.post("/admin/integrations/website", data={
        "website_connector": "markdown_folder",
        "website_markdown_folder_posts_path": "/site/content/posts/",
    })
    assert "website_saved=1" in response.headers["location"]

    from app.database import AsyncSessionLocal
    from app.website_connectors.registry import get_active_type, load_config

    async with AsyncSessionLocal() as session:
        assert await get_active_type(session) == "markdown_folder"
        assert (await load_config(session, "markdown_folder"))["posts_path"] == "site/content/posts"
        # WordPress is switched off but its settings are still there.
        assert (await load_config(session, "wordpress"))["app_password"] == "pw"

    page = await client.get("/admin/integrations")
    assert 'value="markdown_folder" selected' in page.text


async def test_path_with_dot_dot_is_rejected(client, admin_user):
    await web_login(client, "admin@example.com")
    response = await client.post("/admin/integrations/website", data={
        "website_connector": "markdown_folder",
        "website_markdown_folder_posts_path": "site/../../other",
    })
    assert "website_error=" in response.headers["location"]

    from app.database import AsyncSessionLocal
    from app.website_connectors.registry import get_active_type
    async with AsyncSessionLocal() as session:
        assert await get_active_type(session) is None


async def test_choosing_none_switches_the_website_channel_off(client, admin_user):
    await web_login(client, "admin@example.com")
    await client.post("/admin/integrations/website", data={
        "website_connector": "markdown_folder", "website_markdown_folder_posts_path": "site/posts",
    })
    await client.post("/admin/integrations/website", data={"website_connector": ""})

    from app.database import AsyncSessionLocal
    from app.website_connectors import get_active_connector
    async with AsyncSessionLocal() as session:
        assert await get_active_connector(session) is None


async def test_board_member_cannot_change_the_website(client, admin_user, board_user):
    await web_login(client, "vorstand@example.com")
    response = await client.post("/admin/integrations/website", data={"website_connector": "wordpress"})
    assert response.status_code == 403


# ---------------------------------------------------------------------------
# End to end: an announcement becomes a Markdown file
# ---------------------------------------------------------------------------

async def test_announcement_becomes_a_markdown_draft(client, admin_user, monkeypatch, tmp_path):
    monkeypatch.setattr("app.routers.announcements.UPLOAD_DIR", tmp_path)
    monkeypatch.setattr("app.routers.announcements.PRINT_PDF_DIR", tmp_path / "print")
    storage = InMemoryStorage(["site/content/posts", "site/content/media"])

    async def fake_storage(db):
        return storage

    monkeypatch.setattr("app.website_connectors.markdown_folder.get_storage_provider", fake_storage)

    token = await login(client, "admin@example.com")
    assert (await client.put(
        "/api/v1/club-settings/modul_announcements", json={"value": "true"}, headers=auth_header(token),
    )).status_code == 200
    await web_login(client, "admin@example.com")
    await client.post("/admin/integrations/website", data={
        "website_connector": "markdown_folder",
        "website_markdown_folder_posts_path": "site/content/posts",
        "website_markdown_folder_media_path": "site/content/media",
        "website_markdown_folder_categories": "aktuelles",
    })

    create = await client.post(
        "/announcements/new",
        data={"title": "Neue Kompostboxen", "body_markdown": "Wir haben **neue** Boxen."},
        files={"image": ("bins.png", _TINY_PNG_BYTES, "image/png")},
    )
    announcement_id = create.headers["location"].split("/")[2]

    assert (await client.post(f"/announcements/{announcement_id}/send/blog")).status_code == 303
    posts = [name for (folder, name) in storage.files if folder == "site/content/posts"]
    assert len(posts) == 1 and posts[0].endswith("-neue-kompostboxen.md")
    assert "draft: true" in storage.text(posts[0])

    page = await client.get(f"/announcements/{announcement_id}/edit")
    assert f"site/content/posts/{posts[0]}" in page.text
    assert "Markdown" in page.text

    # Edit and send again: same file, updated text.
    await client.post(f"/announcements/{announcement_id}/edit", data={
        "title": "Neue Kompostboxen", "body_markdown": "Jetzt mit Deckel.",
    })
    assert (await client.post(f"/announcements/{announcement_id}/send/blog")).status_code == 303
    posts = [name for (folder, name) in storage.files if folder == "site/content/posts"]
    assert len(posts) == 1
    assert "Jetzt mit Deckel." in storage.text(posts[0])

    # Nothing changed since: the channel has nothing new to deliver.
    unchanged = await client.post(
        f"/api/v1/announcements/{announcement_id}/website-draft", headers=auth_header(token),
    )
    assert unchanged.status_code == 409

    # The same update through the REST API.
    await client.post(f"/announcements/{announcement_id}/edit", data={
        "title": "Neue Kompostboxen", "body_markdown": "Jetzt mit Deckel und Schloss.",
    })
    response = await client.post(
        f"/api/v1/announcements/{announcement_id}/website-draft", headers=auth_header(token),
    )
    assert response.status_code == 200, response.text
    assert response.json()["status"] == "SENT"
    assert response.json()["external_id"] == posts[0]
    assert "Jetzt mit Deckel und Schloss." in storage.text(posts[0])


# ---------------------------------------------------------------------------
# REST API
# ---------------------------------------------------------------------------

async def test_api_lists_connectors_and_never_returns_secrets(client, admin_user):
    await web_login(client, "admin@example.com")
    await client.post("/admin/integrations/website", data={
        "website_connector": "wordpress",
        "website_wordpress_site_url": "https://blog.example.com",
        "website_wordpress_username": "board",
        "website_wordpress_app_password": "top-secret-value",
    })
    token = await login(client, "admin@example.com")

    connectors = await client.get("/api/v1/website/connectors", headers=auth_header(token))
    assert connectors.status_code == 200
    assert {c["type"] for c in connectors.json()} == {"wordpress", "markdown_folder", "parcella_plugin"}

    current = await client.get("/api/v1/website", headers=auth_header(token))
    assert current.status_code == 200
    assert current.json()["active"] == "wordpress"
    assert current.json()["secrets_set"]["wordpress"] == {"app_password": True}
    assert "app_password" not in current.json()["values"]["wordpress"]
    assert "top-secret-value" not in current.text


async def test_api_can_switch_but_not_set_secrets(client, admin_user):
    token = await login(client, "admin@example.com")

    refused = await client.put("/api/v1/website", headers=auth_header(token), json={
        "active": "parcella_plugin", "values": {"endpoint_url": "https://cms.example.org/parcella/v1", "shared_secret": "x"},
    })
    assert refused.status_code == 403

    switched = await client.put("/api/v1/website", headers=auth_header(token), json={
        "active": "parcella_plugin", "values": {"endpoint_url": "https://cms.example.org/parcella/v1"},
    })
    assert switched.status_code == 200, switched.text
    assert switched.json()["active"] == "parcella_plugin"
    assert switched.json()["values"]["parcella_plugin"]["endpoint_url"] == "https://cms.example.org/parcella/v1"

    unknown = await client.put("/api/v1/website", headers=auth_header(token), json={"active": "geocities"})
    assert unknown.status_code == 422

    test = await client.post("/api/v1/website/test", headers=auth_header(token))
    assert test.json() == {"ok": False, "message": "Required fields are missing."}


async def test_api_website_settings_are_admin_only(client, admin_user, board_user):
    token = await login(client, "vorstand@example.com")
    assert (await client.get("/api/v1/website", headers=auth_header(token))).status_code == 403
    assert (await client.put("/api/v1/website", headers=auth_header(token), json={"active": None})).status_code == 403


async def test_plugin_error_text_is_shown_without_json_noise():
    def handler(request):
        return httpx.Response(503, text='{"error":"The content type \\u0022article\\u0022 does not exist."}')

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    connector = ParcellaPluginPublisher("https://cms.example.org/parcella/v1", SECRET, client=client)
    with pytest.raises(BlogPublishError, match='HTTP 503\\): The content type "article" does not exist.'):
        await connector.test_connection()
    await client.aclose()
