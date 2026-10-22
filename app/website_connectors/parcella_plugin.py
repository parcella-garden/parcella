"""
Parcella plugin connector: talks to any CMS that runs a plugin
implementing the Parcella Website Plugin Protocol v1
(docs/website-plugin-protocol.md) -- TYPO3, Contao, Drupal, Joomla or
anything else. Parcella has one client for all of them; each CMS only
needs its own small plugin, which third parties can write and extend
without changing Parcella (ADR 0105).

Every request is signed with HMAC-SHA256 over timestamp, method, path
and body, using a secret the plugin generates and the admin pastes into
Parcella. The plugin rejects unsigned, mis-signed and stale requests.
"""
import base64
import hashlib
import hmac
import json
import time
from typing import Optional
from urllib.parse import quote, urlsplit

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.website_connectors.base import (
    BlogPostNotFoundError, BlogPublishError, ConfigField, DraftContent, DraftResult, WebsiteConnector,
)

PROTOCOL = "parcella-website/1"


def sign(secret: str, timestamp: str, method: str, path: str, body: bytes) -> str:
    """The protocol's signature: hex HMAC-SHA256 of
    "<timestamp>\\n<METHOD>\\n<path>\\n" + body. Including method and path
    means a captured request can't be replayed against another endpoint."""
    message = f"{timestamp}\n{method.upper()}\n{path}\n".encode("utf-8") + body
    return "sha256=" + hmac.new(secret.encode("utf-8"), message, hashlib.sha256).hexdigest()


class ParcellaPluginPublisher(WebsiteConnector):
    type = "parcella_plugin"
    config_fields = [
        ConfigField("endpoint_url", kind="url", required=True, placeholder="https://example.org/parcella/v1", hint=True),
        ConfigField("shared_secret", kind="secret", required=True, hint=True),
    ]

    def __init__(self, endpoint_url: str, shared_secret: str, client: Optional[httpx.AsyncClient] = None):
        self.endpoint_url = endpoint_url.rstrip("/")
        self.shared_secret = shared_secret
        self._client = client
        self._owns_client = client is None

    @classmethod
    async def build(cls, config: dict, db: AsyncSession) -> "ParcellaPluginPublisher":
        return cls(endpoint_url=config["endpoint_url"], shared_secret=config["shared_secret"])

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=20.0)
        return self._client

    async def aclose(self) -> None:
        if self._owns_client and self._client is not None:
            await self._client.aclose()
            self._client = None

    async def _request(self, method: str, subpath: str, payload: Optional[dict] = None) -> httpx.Response:
        url = f"{self.endpoint_url}{subpath}"
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8") if payload is not None else b""
        timestamp = str(int(time.time()))
        headers = {
            "X-Parcella-Protocol": PROTOCOL,
            "X-Parcella-Timestamp": timestamp,
            "X-Parcella-Signature": sign(self.shared_secret, timestamp, method, urlsplit(url).path, body),
            "User-Agent": f"Parcella/{settings.app_version}",
        }
        if payload is not None:
            headers["Content-Type"] = "application/json"
        client = await self._get_client()
        try:
            return await client.request(method, url, headers=headers, content=body)
        except httpx.HTTPError as e:
            raise BlogPublishError(f"Could not reach {self.endpoint_url}: {e}") from e

    @staticmethod
    def _payload(content: DraftContent, include_image: bool) -> dict:
        payload = {
            "title": content.title,
            "markdown": content.markdown,
            "html": content.html,
            "summary": content.summary,
            "language": content.language,
            "source_id": content.source_id,
        }
        if include_image:
            payload["image"] = None
            if content.image_bytes and content.image_filename and content.image_mime:
                payload["image"] = {
                    "filename": content.image_filename,
                    "mime": content.image_mime,
                    "data_base64": base64.b64encode(content.image_bytes).decode("ascii"),
                }
        return payload

    @staticmethod
    def _json(response: httpx.Response) -> dict:
        try:
            data = response.json()
        except ValueError as e:
            raise BlogPublishError("The plugin's answer isn't valid JSON.") from e
        if not isinstance(data, dict):
            raise BlogPublishError("The plugin's answer isn't a JSON object.")
        return data

    def _check(self, response: httpx.Response, action: str) -> None:
        if response.status_code == 401:
            raise BlogPublishError("The plugin rejected Parcella's signature -- check the shared secret.")
        if response.status_code not in (200, 201):
            raise BlogPublishError(f"The plugin rejected the {action} (HTTP {response.status_code}): {response.text[:200]}")

    def _result(self, data: dict) -> DraftResult:
        post_id = data.get("id")
        if post_id in (None, ""):
            raise BlogPublishError("The plugin's answer has no draft id.")
        edit_url = data.get("edit_url")
        if not (isinstance(edit_url, str) and edit_url.startswith(("https://", "http://"))):
            edit_url = None
        return DraftResult(post_id=str(post_id)[:100], edit_url=edit_url, location=None if edit_url else str(post_id))

    async def test_connection(self) -> None:
        response = await self._request("GET", "/ping")
        self._check(response, "connection test")
        data = self._json(response)
        if data.get("protocol") != PROTOCOL:
            raise BlogPublishError(
                f"The plugin speaks {data.get('protocol')!r}, but Parcella expects {PROTOCOL!r}."
            )

    async def publish_draft(self, content: DraftContent) -> DraftResult:
        response = await self._request("POST", "/drafts", self._payload(content, include_image=True))
        self._check(response, "draft")
        return self._result(self._json(response))

    async def update_post(
        self, post_id: str, content: DraftContent, image_changed: bool = False,
    ) -> DraftResult:
        response = await self._request(
            "PUT", f"/drafts/{quote(post_id, safe='')}", self._payload(content, include_image=image_changed),
        )
        if response.status_code in (404, 410):
            raise BlogPostNotFoundError(f"Draft {post_id} no longer exists in the CMS.")
        self._check(response, "update")
        return self._result(self._json(response))

    async def get_public_url_if_published(self, post_id: str) -> Optional[str]:
        try:
            response = await self._request("GET", f"/drafts/{quote(post_id, safe='')}")
        except BlogPublishError:
            return None
        if response.status_code != 200:
            return None
        try:
            data = self._json(response)
        except BlogPublishError:
            return None
        url = data.get("public_url")
        if data.get("status") == "published" and isinstance(url, str) and url.startswith(("https://", "http://")):
            return url
        return None
