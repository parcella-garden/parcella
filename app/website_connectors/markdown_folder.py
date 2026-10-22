"""
Markdown folder connector: writes each draft as a Markdown file with a
YAML front-matter header into a folder on the club's cloud storage.
For static websites that are built from such a folder -- Hugo, Jekyll,
Eleventy, Astro, or a home-grown generator like kgv-goldene-hoehe's,
which rebuilds its site from a Nextcloud folder every ~30 minutes.

A draft is a file with `draft: true` in its header. A human publishes
it by deleting that line; Parcella never adds it back on a later
update, and never deletes a file (ADR 0104).

Talks to cloud storage only through CloudStorageProvider
(app/cloud_storage.py), so it isn't tied to Nextcloud.
"""
import json
import re
import unicodedata
import uuid
from datetime import date
from typing import List, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from app.cloud_storage import CloudStorageError, CloudStorageProvider, get_cloud_storage_provider
from app.parcel_cloud_folders import InvalidCloudPathError, sanitize_relative_path
from app.website_connectors.base import (
    BlogPostNotFoundError, BlogPublishError, ConfigField, DraftContent, DraftResult, WebsiteConnector,
)

# Front-matter keys Parcella owns and rewrites on every update. Any other
# key (draft, categories, author, date, url, ...) is left exactly as the
# human last saved it, the same way the WordPress connector keeps
# categories and the publish status.
OWNED_KEYS = ("title", "summary", "image")

_POST_FILENAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*\.md$")
_TRANSLITERATIONS = {"ä": "ae", "ö": "oe", "ü": "ue", "Ä": "Ae", "Ö": "Oe", "Ü": "Ue", "ß": "ss"}
SLUG_MAX_LENGTH = 80
SUMMARY_MAX_LENGTH = 200


def slugify(title: str) -> str:
    """ASCII-only, lowercase, dash-separated -- the rule in the site's
    own Readme ("keine Leerzeichen, keine Umlaute"), and the reason a
    title can never smuggle a path separator into the filename."""
    text = "".join(_TRANSLITERATIONS.get(ch, ch) for ch in title)
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    slug = slug[:SLUG_MAX_LENGTH].rstrip("-")
    return slug or "post"


def summarize(markdown: str) -> str:
    """First real paragraph as plain text, shortened at a word boundary."""
    for block in re.split(r"\n\s*\n", markdown):
        block = block.strip()
        if not block or block.startswith(("#", "!", ":::", "|", "```")):
            continue
        text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", block)
        text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
        text = re.sub(r"[*_`>#]+", "", text)
        text = re.sub(r"^\s*[-+]\s+", "", text, flags=re.MULTILINE)
        text = " ".join(text.split())
        if not text:
            continue
        if len(text) <= SUMMARY_MAX_LENGTH:
            return text
        return text[:SUMMARY_MAX_LENGTH].rsplit(" ", 1)[0].rstrip(",.;:") + " …"
    return ""


def yaml_string(value: str) -> str:
    """A JSON string literal is a valid YAML double-quoted scalar, so
    json.dumps quotes, escapes and newline-proofs any title safely."""
    return json.dumps(value, ensure_ascii=False)


def split_front_matter(text: str) -> Tuple[List[str], str]:
    """(header lines without the --- fences, body). Raises
    BlogPublishError if the file has no front-matter header."""
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        raise BlogPublishError("The existing post file has no front-matter header.")
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return lines[1:index], "\n".join(lines[index + 1:]).lstrip("\n")
    raise BlogPublishError("The existing post file's front-matter header isn't closed.")


def _line_key(line: str) -> Optional[str]:
    match = re.match(r"^([A-Za-z0-9_-]+)\s*:", line)
    return match.group(1) if match else None


def _render(header: List[str], body: str) -> str:
    return "---\n" + "\n".join(header) + "\n---\n\n" + body.strip() + "\n"


def _is_draft(header: List[str]) -> bool:
    return any(re.match(r"^draft\s*:\s*(true|yes|on)\s*$", line.strip(), re.IGNORECASE) for line in header)


def _header_value(header: List[str], key: str) -> Optional[str]:
    for line in header:
        if _line_key(line) == key:
            raw = line.split(":", 1)[1].strip()
            try:
                value = json.loads(raw)
                return value if isinstance(value, str) else raw
            except ValueError:
                return raw.strip("'\"")
    return None


class MarkdownFolderPublisher(WebsiteConnector):
    type = "markdown_folder"
    config_fields = [
        ConfigField("posts_path", kind="path", required=True, placeholder="website/content/posts", hint=True),
        ConfigField("media_path", kind="path", placeholder="website/content/media", hint=True),
        ConfigField("media_url_prefix", default="/media", placeholder="/media", hint=True),
        ConfigField("site_url", kind="url", placeholder="https://example.org", hint=True),
        ConfigField("filename_pattern", default="{date}-{slug}.md", placeholder="{date}-{slug}.md", hint=True),
        ConfigField("url_pattern", default="/{slug}.html", placeholder="/{slug}.html", hint=True),
        ConfigField("author"),
        ConfigField("categories", kind="list", placeholder="news", hint=True),
    ]

    def __init__(self, storage: CloudStorageProvider, config: dict):
        self.storage = storage
        self.posts_path = config["posts_path"]
        self.media_path = config.get("media_path") or ""
        self.media_url_prefix = "/" + (config.get("media_url_prefix") or "/media").strip("/")
        self.site_url = (config.get("site_url") or "").rstrip("/")
        self.filename_pattern = config.get("filename_pattern") or "{date}-{slug}.md"
        self.url_pattern = config.get("url_pattern") or ""
        self.author = config.get("author") or ""
        self.categories = [c.strip() for c in (config.get("categories") or "").split(",") if c.strip()]

    @classmethod
    async def build(cls, config: dict, db: AsyncSession) -> "MarkdownFolderPublisher":
        storage = await get_storage_provider(db)
        if storage is None:
            raise BlogPublishError(
                "Cloud storage isn't configured yet -- the Markdown folder writes into it. "
                "Set it up under Admin -> Integrations -> Nextcloud first."
            )
        return cls(storage, config)

    async def aclose(self) -> None:
        await self.storage.aclose()

    # -- helpers -----------------------------------------------------------

    def _filename(self, slug: str, today: date, attempt: int) -> str:
        suffix = "" if attempt == 1 else f"-{attempt}"
        try:
            name = self.filename_pattern.format(date=today.strftime("%Y%m%d"), slug=slug + suffix)
        except (KeyError, IndexError, ValueError) as e:
            raise BlogPublishError("The filename pattern may only use {date} and {slug}.") from e
        if not _POST_FILENAME_RE.match(name):
            raise BlogPublishError(f"The filename pattern produced an invalid file name: {name!r}.")
        return name

    def _public_path(self, slug: str) -> Optional[str]:
        if not self.url_pattern:
            return None
        try:
            return self.url_pattern.format(slug=slug)
        except (KeyError, IndexError, ValueError) as e:
            raise BlogPublishError("The post URL pattern may only use {slug}.") from e

    def _location(self, filename: str) -> str:
        return f"{self.posts_path}/{filename}"

    async def _upload_image(self, content: DraftContent, today: date) -> Optional[str]:
        """Stores the image under <media>/YYYY/MM/ with a fresh uuid name
        and returns its public path, or None if there's nowhere to put it."""
        if not (content.image_bytes and content.image_filename and self.media_path):
            return None
        extension = ""
        if "." in content.image_filename:
            extension = "." + re.sub(r"[^a-z0-9]", "", content.image_filename.rsplit(".", 1)[1].lower())[:5]
        folder = f"{self.media_path}/{today:%Y}/{today:%m}"
        name = f"{uuid.uuid4()}{extension}"
        try:
            await self.storage.create_folder(folder)
            await self.storage.upload_file(folder, name, content.image_bytes)
        except CloudStorageError as e:
            raise BlogPublishError(f"Image upload failed: {e}") from e
        return f"{self.media_url_prefix}/{today:%Y}/{today:%m}/{name}"

    def _owned_lines(self, content: DraftContent, image_path: Optional[str]) -> dict:
        lines = {"title": f"title: {yaml_string(content.title)}"}
        summary = content.summary or summarize(content.markdown)
        if summary:
            lines["summary"] = f"summary: {yaml_string(summary)}"
        if image_path:
            lines["image"] = f"image: {yaml_string(image_path)}"
        return lines

    async def _read(self, filename: str) -> str:
        if not _POST_FILENAME_RE.match(filename or ""):
            raise BlogPublishError("Stored post reference isn't a valid file name.")
        try:
            entries = await self.storage.list_files(self.posts_path)
        except CloudStorageError as e:
            raise BlogPublishError(str(e)) from e
        if filename not in {e.name for e in entries if not e.is_directory}:
            raise BlogPostNotFoundError(f"{self._location(filename)} no longer exists.")
        try:
            return (await self.storage.download_file(self.posts_path, filename)).decode("utf-8")
        except CloudStorageError as e:
            raise BlogPublishError(str(e)) from e

    async def _write(self, filename: str, text: str) -> None:
        try:
            await self.storage.upload_file(self.posts_path, filename, text.encode("utf-8"))
        except CloudStorageError as e:
            raise BlogPublishError(str(e)) from e

    # -- interface ---------------------------------------------------------

    async def test_connection(self) -> None:
        try:
            await self.storage.list_files(self.posts_path)
            if self.media_path:
                await self.storage.list_files(self.media_path)
        except CloudStorageError as e:
            raise BlogPublishError(str(e)) from e

    async def publish_draft(self, content: DraftContent) -> DraftResult:
        today = date.today()
        slug = slugify(content.title)
        try:
            existing = {e.name for e in await self.storage.list_files(self.posts_path)}
        except CloudStorageError as e:
            raise BlogPublishError(str(e)) from e

        attempt = 1
        while self._filename(slug, today, attempt) in existing:
            attempt += 1
        filename = self._filename(slug, today, attempt)
        final_slug = slug if attempt == 1 else f"{slug}-{attempt}"

        image_path = await self._upload_image(content, today)
        owned = self._owned_lines(content, image_path)
        header = [owned["title"], f"date: {yaml_string(today.isoformat())}"]
        public_path = self._public_path(final_slug)
        if public_path:
            header.append(f"url: {yaml_string(public_path)}")
        if self.author:
            header.append(f"author: {yaml_string(self.author)}")
        if self.categories:
            header.append("categories: [" + ", ".join(yaml_string(c) for c in self.categories) + "]")
        header += [owned[k] for k in ("summary", "image") if k in owned]
        if content.source_id:
            header.append(f"parcella_announcement: {yaml_string(content.source_id)}")
        header.append("draft: true")

        await self._write(filename, _render(header, content.markdown))
        return DraftResult(post_id=filename, location=self._location(filename))

    async def update_post(
        self, post_id: str, content: DraftContent, image_changed: bool = False,
    ) -> DraftResult:
        header, _old_body = split_front_matter(await self._read(post_id))

        image_path = None
        if image_changed:
            image_path = await self._upload_image(content, date.today())
        owned = self._owned_lines(content, image_path)
        replace = set(OWNED_KEYS) if image_changed else {"title", "summary"}

        new_header, placed = [], set()
        for line in header:
            key = _line_key(line)
            if key in replace:
                if key in owned and key not in placed:
                    new_header.append(owned[key])
                    placed.add(key)
                continue
            new_header.append(line)
        missing = [owned[k] for k in OWNED_KEYS if k in replace and k in owned and k not in placed]
        # New owned lines go before "draft:" so a human still finds that
        # line last, where the site's Readme tells them to look for it.
        draft_index = next((i for i, l in enumerate(new_header) if _line_key(l) == "draft"), len(new_header))
        new_header[draft_index:draft_index] = missing

        await self._write(post_id, _render(new_header, content.markdown))
        return DraftResult(post_id=post_id, location=self._location(post_id))

    async def get_public_url_if_published(self, post_id: str) -> Optional[str]:
        if not self.site_url:
            return None
        try:
            header, _body = split_front_matter(await self._read(post_id))
        except BlogPublishError:
            return None
        if _is_draft(header):
            return None
        path = _header_value(header, "url")
        if not path:
            return None
        return path if path.startswith(("http://", "https://")) else f"{self.site_url}/{path.lstrip('/')}"


async def get_storage_provider(db: AsyncSession) -> Optional[CloudStorageProvider]:
    """The club's cloud storage. Nextcloud is the only provider today;
    a module-level function so tests can swap in an in-memory one."""
    return await get_cloud_storage_provider(db)


def validate_path(value: str) -> str:
    """Same rules as every other board-entered cloud folder path."""
    try:
        return sanitize_relative_path(value)
    except InvalidCloudPathError as e:
        raise BlogPublishError(str(e)) from e
