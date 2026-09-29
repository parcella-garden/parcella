"""
Blog channel for the announcements module: publishes a draft post to
the club's CMS. Only WordPress is implemented so far, behind a small
BlogPublisher interface so another CMS (TYPO3, Joomla, ...) can be
added later as a new class rather than a rewrite of this one.

WordPress's REST API supports draft creation natively via an
Application Password (WP 5.6+) -- no custom plugin needed on the
WordPress side for this direction. That's the opposite direction from
the public-signup connector: there, an external WordPress plugin pushes
data INTO Parcella; here, Parcella pushes a draft OUT to WordPress
using WordPress's own built-in REST API and its own built-in
authentication mechanism.

Credentials (site URL, username, application password) are stored per
club in ClubSettings, configured on the Admin -> Integrations page
(alongside the public-signup API token) rather than Admin -> Settings
-- Integrations is where every Parcella <-> other-system connection
lives, in either direction. The application password is encrypted with
app.crypto_utils (Fernet), and an empty field on save means "leave the
existing value unchanged," same convention used for SMTP.

The publisher never gets to choose to actually publish: every post is
created with status="draft". Whether and when to make it public is a
decision for a human in the WordPress admin, same as the blog channel
was originally scoped.
"""
import base64
import logging
from dataclasses import dataclass
from typing import Optional

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ClubSetting
from app.crypto_utils import decrypt, DecryptionError

logger = logging.getLogger(__name__)


class BlogPublishError(Exception):
    """Raised for any failure talking to the CMS -- network, auth, or
    an unexpected response shape. The router turns this into a FAILED
    AnnouncementDelivery with this message shown to the admin."""


class BlogPostNotFoundError(BlogPublishError):
    """update_post() target no longer exists on the CMS (deleted by
    hand). The router falls back to creating a fresh draft."""


@dataclass
class BlogDraftResult:
    edit_url: str
    post_id: int


class BlogPublisher:
    """Interface every CMS connector implements. WordPressPublisher is
    the only implementation today; a future TYPO3/Joomla connector
    would be a new class implementing the same two methods, not a
    change to this one."""

    async def test_connection(self) -> None:
        """Raises BlogPublishError if the credentials or site aren't
        reachable/valid. Returns None on success."""
        raise NotImplementedError

    async def publish_draft(
        self, title: str, html_content: str,
        image_bytes: Optional[bytes] = None, image_filename: Optional[str] = None,
        image_mime: Optional[str] = None,
    ) -> BlogDraftResult:
        raise NotImplementedError

    async def update_post(
        self, post_id: str, title: str, html_content: str,
        image_bytes: Optional[bytes] = None, image_filename: Optional[str] = None,
        image_mime: Optional[str] = None, clear_image: bool = False,
    ) -> BlogDraftResult:
        """Overwrites title/content (and the featured image, only if
        image_bytes is given, or removes it with clear_image) of an
        existing post. Must NOT touch the
        post's publish status -- see WordPressPublisher.update_post."""
        raise NotImplementedError


class WordPressPublisher(BlogPublisher):
    def __init__(
        self, site_url: str, username: str, application_password: str,
        client: Optional[httpx.AsyncClient] = None,
    ):
        self.site_url = site_url.rstrip("/")
        self.username = username
        self.application_password = application_password
        # A client can be injected (tests use this with an
        # httpx.MockTransport, since no real WordPress site is
        # reachable from Parcella's own test/CI environment); otherwise
        # one is created lazily and owned/closed by this instance.
        self._client = client
        self._owns_client = client is None

    def _auth_header(self) -> dict:
        token = base64.b64encode(f"{self.username}:{self.application_password}".encode("utf-8")).decode("ascii")
        return {"Authorization": f"Basic {token}"}

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=15.0)
        return self._client

    async def aclose(self) -> None:
        if self._owns_client and self._client is not None:
            await self._client.aclose()

    async def test_connection(self) -> None:
        client = await self._get_client()
        try:
            response = await client.get(f"{self.site_url}/wp-json/wp/v2/users/me", headers=self._auth_header())
        except httpx.HTTPError as e:
            raise BlogPublishError(f"Could not reach {self.site_url}: {e}") from e

        if response.status_code == 401:
            raise BlogPublishError(
                "WordPress rejected the credentials (401 Unauthorized). "
                "Check the username and Application Password."
            )
        if response.status_code != 200:
            raise BlogPublishError(f"Unexpected response from WordPress (HTTP {response.status_code}).")

    async def _upload_media(self, client: httpx.AsyncClient, image_bytes: bytes, filename: str, mime: str) -> int:
        headers = self._auth_header()
        headers["Content-Disposition"] = f'attachment; filename="{filename}"'
        headers["Content-Type"] = mime
        try:
            response = await client.post(f"{self.site_url}/wp-json/wp/v2/media", headers=headers, content=image_bytes)
        except httpx.HTTPError as e:
            raise BlogPublishError(f"Could not reach {self.site_url}: {e}") from e

        if response.status_code not in (200, 201):
            raise BlogPublishError(f"Image upload to WordPress failed (HTTP {response.status_code}): {response.text[:200]}")
        return response.json()["id"]

    async def publish_draft(
        self, title: str, html_content: str,
        image_bytes: Optional[bytes] = None, image_filename: Optional[str] = None,
        image_mime: Optional[str] = None,
    ) -> BlogDraftResult:
        client = await self._get_client()

        featured_media_id = None
        if image_bytes and image_filename and image_mime:
            featured_media_id = await self._upload_media(client, image_bytes, image_filename, image_mime)

        payload = {"title": title, "content": html_content, "status": "draft"}
        if featured_media_id is not None:
            payload["featured_media"] = featured_media_id

        try:
            response = await client.post(f"{self.site_url}/wp-json/wp/v2/posts", headers=self._auth_header(), json=payload)
        except httpx.HTTPError as e:
            raise BlogPublishError(f"Could not reach {self.site_url}: {e}") from e

        if response.status_code not in (200, 201):
            raise BlogPublishError(f"WordPress rejected the draft (HTTP {response.status_code}): {response.text[:200]}")

        data = response.json()
        post_id = data["id"]
        edit_url = f"{self.site_url}/wp-admin/post.php?post={post_id}&action=edit"
        return BlogDraftResult(edit_url=edit_url, post_id=post_id)

    async def update_post(
        self, post_id: str, title: str, html_content: str,
        image_bytes: Optional[bytes] = None, image_filename: Optional[str] = None,
        image_mime: Optional[str] = None, clear_image: bool = False,
    ) -> BlogDraftResult:
        """Pushes changed announcement content into the SAME WordPress
        post instead of creating a second one (ADR 0087). The payload
        deliberately has no "status": a post a human already published
        in WordPress stays published. Only title, content and -- when
        the announcement's image changed -- featured_media are sent, so
        SEO plugin fields (Yoast etc. store theirs as separate post
        meta), excerpt, categories and tags set in WordPress survive;
        text edits made directly in WordPress's own editor do not.
        """
        client = await self._get_client()

        featured_media_id = None
        if image_bytes and image_filename and image_mime:
            featured_media_id = await self._upload_media(client, image_bytes, image_filename, image_mime)

        payload = {"title": title, "content": html_content}
        if featured_media_id is not None:
            payload["featured_media"] = featured_media_id
        elif clear_image:
            payload["featured_media"] = 0

        try:
            response = await client.post(
                f"{self.site_url}/wp-json/wp/v2/posts/{post_id}", headers=self._auth_header(), json=payload,
            )
        except httpx.HTTPError as e:
            raise BlogPublishError(f"Could not reach {self.site_url}: {e}") from e

        if response.status_code in (404, 410):
            raise BlogPostNotFoundError(f"WordPress post {post_id} no longer exists.")
        if response.status_code != 200:
            raise BlogPublishError(f"WordPress rejected the update (HTTP {response.status_code}): {response.text[:200]}")

        edit_url = f"{self.site_url}/wp-admin/post.php?post={post_id}&action=edit"
        return BlogDraftResult(edit_url=edit_url, post_id=int(post_id))

    async def get_public_url_if_published(self, post_id: str) -> Optional[str]:
        """Asks WordPress directly whether this post has been published
        (a human still has to do that themselves in the WP admin -- see
        publish_draft's docstring) and, if so, returns its current
        public URL. Returns None if it's still a draft, was deleted, or
        WordPress can't be reached -- callers should treat all of those
        the same way: no working public link to point a QR code at yet.
        Deliberately re-queries live rather than trusting anything
        cached at draft-creation time, since a draft's publish state
        (and even, in principle, its permalink) can change after the
        fact.
        """
        client = await self._get_client()
        try:
            response = await client.get(f"{self.site_url}/wp-json/wp/v2/posts/{post_id}", headers=self._auth_header())
        except httpx.HTTPError:
            return None

        if response.status_code != 200:
            return None

        data = response.json()
        if data.get("status") != "publish":
            return None
        return data.get("link")


async def load_wordpress_configuration(db: AsyncSession) -> Optional[dict]:
    """Loads {site_url, username, app_password} from ClubSettings, or
    None if not (fully) configured yet. All three fields are required
    -- a partially-filled-in configuration is treated as "not
    configured" rather than attempted and failing confusingly."""
    result = await db.execute(
        select(ClubSetting).where(
            ClubSetting.key.in_(["wordpress_site_url", "wordpress_username", "wordpress_app_password"])
        )
    )
    stored = {e.key: e.value for e in result.scalars().all() if e.value}

    site_url = stored.get("wordpress_site_url")
    username = stored.get("wordpress_username")
    try:
        app_password = decrypt(stored.get("wordpress_app_password"))
    except DecryptionError:
        logger.error(
            "Could not decrypt the stored WordPress app password -- did SECRET_KEY change? "
            "Treating the blog connector as not configured until it's re-entered."
        )
        return None

    if not site_url or not username or not app_password:
        return None
    return {"site_url": site_url, "username": username, "app_password": app_password}


async def get_wordpress_publisher(
    db: AsyncSession, client: Optional[httpx.AsyncClient] = None,
) -> Optional[WordPressPublisher]:
    """Returns a configured WordPressPublisher, or None if the club
    hasn't set up WordPress credentials yet."""
    config = await load_wordpress_configuration(db)
    if config is None:
        return None
    return WordPressPublisher(
        site_url=config["site_url"], username=config["username"],
        application_password=config["app_password"], client=client,
    )
