"""
The interface every website connector implements (ADR 0104).

A website connector takes an announcement and turns it into a draft on
the club's website -- a WordPress post, a Markdown file in a static
site's content folder, or a post in any CMS that runs a Parcella plugin
(docs/website-plugin-protocol.md). Exactly one connector is active at a
time, chosen on Admin -> Integrations -> Website.

Connectors only ever create drafts. Whether and when a draft goes
public is a decision for a human in the CMS itself; updating an
existing draft must never change its publish state.
"""
from dataclasses import dataclass
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession


class BlogPublishError(Exception):
    """Raised for any failure talking to the website -- network, auth,
    or an unexpected response. The router turns this into a FAILED
    AnnouncementDelivery with this message shown to the admin."""


class BlogPostNotFoundError(BlogPublishError):
    """update_post() target no longer exists on the website (deleted by
    hand). The router falls back to creating a fresh draft."""


@dataclass
class DraftContent:
    """Everything a connector may need to build a draft. Markdown-based
    targets use `markdown`, HTML-based ones use `html` -- both are the
    same announcement text."""
    title: str
    markdown: str
    html: str
    summary: str = ""
    image_bytes: Optional[bytes] = None
    image_filename: Optional[str] = None
    image_mime: Optional[str] = None
    language: str = "en"
    source_id: str = ""


@dataclass
class DraftResult:
    """`post_id` identifies the draft on the website for later updates
    (stored as AnnouncementDelivery.external_id). `edit_url` is a link
    for the admin, if the website has one; `location` is a plain-text
    fallback (e.g. "content/posts/20261022-title.md") shown instead."""
    post_id: str
    edit_url: Optional[str] = None
    location: Optional[str] = None


@dataclass
class ConfigField:
    """One setting a connector needs, rendered generically on Admin ->
    Integrations and in the REST API. Stored as the ClubSetting
    `website_<connector type>_<key>`. `kind` is one of text, url, path,
    secret, list (comma-separated). Secrets are encrypted at rest and
    never shown or returned again. Labels come from the translation key
    `website.connectors.<type>.fields.<key>`; with `hint=True` also
    `website.connectors.<type>.hints.<key>`."""
    key: str
    kind: str = "text"
    required: bool = False
    default: str = ""
    placeholder: str = ""
    hint: bool = False


class WebsiteConnector:
    """Base class. A new CMS is one subclass plus one line in
    app/website_connectors/registry.py -- no change to this class, the
    announcements router, or the admin page."""

    type: str = ""
    config_fields: List[ConfigField] = []

    @classmethod
    async def build(cls, config: dict, db: AsyncSession) -> "WebsiteConnector":
        """Creates a ready-to-use connector from its (decrypted)
        configuration. `db` is there for connectors that depend on
        another integration, like the Markdown folder on cloud storage.
        Raises BlogPublishError if a required dependency is missing."""
        raise NotImplementedError

    async def test_connection(self) -> None:
        """Raises BlogPublishError if the website isn't reachable or the
        credentials/paths are wrong. Returns None on success."""
        raise NotImplementedError

    async def publish_draft(self, content: DraftContent) -> DraftResult:
        raise NotImplementedError

    async def update_post(
        self, post_id: str, content: DraftContent, image_changed: bool = False,
    ) -> DraftResult:
        """Overwrites title, text and -- only if `image_changed` -- the
        image of an existing draft (a changed image with no image bytes
        means: remove it). Must NOT touch the publish state. Raises
        BlogPostNotFoundError if the draft is gone."""
        raise NotImplementedError

    async def get_public_url_if_published(self, post_id: str) -> Optional[str]:
        """The post's public URL once a human has published it, else
        None (still a draft, deleted, or unreachable -- all mean "no
        working link for a QR code yet"). Always asks live."""
        raise NotImplementedError

    async def aclose(self) -> None:
        """Releases network clients. Safe to call more than once."""
