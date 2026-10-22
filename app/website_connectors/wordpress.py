"""
WordPress connector: creates draft posts through WordPress's own REST
API, authenticated with an Application Password (WP 5.6+). No plugin is
needed on the WordPress side for this direction. (The parcella-connector
plugin in integrations/wordpress/ handles the other direction: forms on
the WordPress site posting INTO Parcella.)

Moved here from app/blog_publisher.py when the blog channel became
CMS-agnostic (ADR 0104); behaviour is unchanged.
"""
import base64
from typing import Optional

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.security_headers import content_disposition
from app.website_connectors.base import (
    BlogPostNotFoundError, BlogPublishError, ConfigField, DraftContent, DraftResult, WebsiteConnector,
)


class WordPressPublisher(WebsiteConnector):
    type = "wordpress"
    config_fields = [
        ConfigField("site_url", kind="url", required=True, placeholder="https://example.com"),
        ConfigField("username", required=True),
        ConfigField("app_password", kind="secret", required=True, hint=True),
    ]

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

    @classmethod
    async def build(cls, config: dict, db: AsyncSession) -> "WordPressPublisher":
        return cls(
            site_url=config["site_url"], username=config["username"],
            application_password=config["app_password"],
        )

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
            self._client = None

    def _edit_url(self, post_id) -> str:
        return f"{self.site_url}/wp-admin/post.php?post={post_id}&action=edit"

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

    async def _upload_media(self, client: httpx.AsyncClient, content: DraftContent) -> int:
        headers = self._auth_header()
        headers["Content-Disposition"] = content_disposition(content.image_filename)
        headers["Content-Type"] = content.image_mime
        try:
            response = await client.post(
                f"{self.site_url}/wp-json/wp/v2/media", headers=headers, content=content.image_bytes,
            )
        except httpx.HTTPError as e:
            raise BlogPublishError(f"Could not reach {self.site_url}: {e}") from e

        if response.status_code not in (200, 201):
            raise BlogPublishError(f"Image upload to WordPress failed (HTTP {response.status_code}): {response.text[:200]}")
        return response.json()["id"]

    @staticmethod
    def _has_image(content: DraftContent) -> bool:
        return bool(content.image_bytes and content.image_filename and content.image_mime)

    async def publish_draft(self, content: DraftContent) -> DraftResult:
        client = await self._get_client()

        featured_media_id = None
        if self._has_image(content):
            featured_media_id = await self._upload_media(client, content)

        payload = {"title": content.title, "content": content.html, "status": "draft"}
        if featured_media_id is not None:
            payload["featured_media"] = featured_media_id

        try:
            response = await client.post(f"{self.site_url}/wp-json/wp/v2/posts", headers=self._auth_header(), json=payload)
        except httpx.HTTPError as e:
            raise BlogPublishError(f"Could not reach {self.site_url}: {e}") from e

        if response.status_code not in (200, 201):
            raise BlogPublishError(f"WordPress rejected the draft (HTTP {response.status_code}): {response.text[:200]}")

        post_id = response.json()["id"]
        return DraftResult(post_id=str(post_id), edit_url=self._edit_url(post_id))

    async def update_post(
        self, post_id: str, content: DraftContent, image_changed: bool = False,
    ) -> DraftResult:
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

        payload = {"title": content.title, "content": content.html}
        if image_changed:
            if self._has_image(content):
                payload["featured_media"] = await self._upload_media(client, content)
            else:
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

        return DraftResult(post_id=str(post_id), edit_url=self._edit_url(post_id))

    async def get_public_url_if_published(self, post_id: str) -> Optional[str]:
        """Asks WordPress live whether a human has published this post
        and, if so, returns its current public URL -- never anything
        cached at draft-creation time, since the publish state (and in
        principle the permalink) can change after the fact."""
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
