"""
Cloud storage connectors: lets a club link Parcella to a file-storage
backend it already runs (Nextcloud today; Google Drive, S3-compatible
storage, or others could follow later as new classes) so board members
can browse, upload to, and download from a per-parcel folder without
leaving Parcella.

Structured the same way as app/website_connectors/: a small
CloudStorageProvider interface, one concrete implementation per
backend, and credentials stored per club in ClubSettings (configured on
Admin -> Integrations, alongside the other outbound connections). The
Nextcloud application password is encrypted with app.crypto_utils, and
an empty field on save means "leave the existing value unchanged" --
same convention as SMTP and the website connector secrets.

Scope, deliberately: this connects Parcella's board/admin users to
files. It does NOT manage which individual members can see a given
folder -- that access is granted directly in Nextcloud itself (shares/
"Freigaben"), independent of and invisible to Parcella. See
docs/module-cloud-storage.md for the reasoning, including why ending a
tenancy in Parcella does not revoke any Nextcloud share.
"""
import logging
from dataclasses import dataclass
from typing import List, Optional
from urllib.parse import quote
from xml.etree import ElementTree

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ClubSetting
from app.crypto_utils import decrypt, DecryptionError

logger = logging.getLogger(__name__)

_DAV_NS = "{DAV:}"

_PROPFIND_BODY = """<?xml version="1.0" encoding="utf-8" ?>
<d:propfind xmlns:d="DAV:">
  <d:prop>
    <d:displayname/>
    <d:getcontentlength/>
    <d:getlastmodified/>
    <d:resourcetype/>
  </d:prop>
</d:propfind>"""


class CloudStorageError(Exception):
    """Raised for any failure talking to a cloud storage backend --
    network, auth, a missing/misconfigured folder, or an unexpected
    response shape. Routers turn this into a flashed error message for
    the board member who triggered the action."""


@dataclass
class CloudFileEntry:
    name: str
    is_directory: bool
    size: Optional[int] = None
    last_modified: Optional[str] = None


class CloudStorageProvider:
    """Interface every cloud storage connector implements.
    NextcloudProvider is the only implementation today; a future
    Google Drive or S3-compatible connector would be a new class
    implementing the same methods, not a change to this one.

    Originally list/upload/download only, deliberately narrow for v1 --
    no delete, no folder creation, since the folder a club points
    Parcella at was expected to already exist. Extended for issue #141
    (scheduled cloud backups, see docs/ADR/0055-scheduled-cloud-backups.md):
    that feature needs to create its own destination folder on first
    run and prune old backups beyond a retention count, so `delete_file`
    and `create_folder` were added -- scoped narrowly to that use case,
    not a general "let board tooling delete member files" decision.
    """

    async def test_connection(self) -> None:
        """Raises CloudStorageError if the credentials or server
        aren't reachable/valid. Returns None on success."""
        raise NotImplementedError

    async def list_files(self, path: str) -> List[CloudFileEntry]:
        raise NotImplementedError

    async def upload_file(self, path: str, filename: str, content: bytes) -> None:
        raise NotImplementedError

    async def download_file(self, path: str, filename: str) -> bytes:
        raise NotImplementedError

    async def delete_file(self, path: str, filename: str) -> None:
        raise NotImplementedError

    async def create_folder(self, path: str) -> None:
        raise NotImplementedError


def _join_dav_path(*segments: str) -> str:
    """Builds a URL-safe WebDAV path from folder/file name segments,
    quoting each one individually so slashes stay as path separators
    but spaces, umlauts, parentheses etc. in folder/file names are
    encoded correctly. Each segment may itself be a multi-part relative
    path (e.g. "parcels/G016") -- it's split on "/" before quoting, so
    the separator isn't percent-encoded into "%2F" along with it.

    Rejects '..' segments: the folder path is validated before it gets
    here (sanitize_relative_path), but the filename passed to
    download_file/upload_file comes straight from a query parameter /
    uploaded filename with no such check, and could otherwise walk this
    join outside the intended folder within the Nextcloud account
    (flagged by an external pentest)."""
    parts = [
        part for s in segments if s
        for part in s.strip("/").split("/")
        if part and part != "."
    ]
    if any(part == ".." for part in parts):
        raise CloudStorageError("Invalid path: '..' is not allowed.")
    return "/".join(quote(part, safe="") for part in parts)


class NextcloudProvider(CloudStorageProvider):
    def __init__(
        self, base_url: str, username: str, app_password: str,
        client: Optional[httpx.AsyncClient] = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.app_password = app_password
        # A client can be injected (tests use this with an
        # httpx.MockTransport, since no real Nextcloud instance is
        # reachable from Parcella's own test/CI environment); otherwise
        # one is created lazily and owned/closed by this instance.
        self._client = client
        self._owns_client = client is None

    @property
    def _dav_root(self) -> str:
        return f"{self.base_url}/remote.php/dav/files/{quote(self.username, safe='')}"

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=20.0, auth=(self.username, self.app_password))
        return self._client

    async def aclose(self) -> None:
        if self._owns_client and self._client is not None:
            await self._client.aclose()

    def _folder_url(self, path: str) -> str:
        joined = _join_dav_path(path)
        return f"{self._dav_root}/{joined}" if joined else self._dav_root

    def _file_url(self, path: str, filename: str) -> str:
        joined = _join_dav_path(path, filename)
        return f"{self._dav_root}/{joined}"

    async def test_connection(self) -> None:
        client = await self._get_client()
        try:
            response = await client.request("PROPFIND", self._dav_root, headers={"Depth": "0"})
        except httpx.HTTPError as e:
            raise CloudStorageError(f"Could not reach {self.base_url}: {e}") from e

        if response.status_code == 401:
            raise CloudStorageError(
                "Nextcloud rejected the credentials (401 Unauthorized). "
                "Check the username and app password."
            )
        if response.status_code == 404:
            raise CloudStorageError(
                f"No such user/WebDAV root on this Nextcloud instance ({self.username})."
            )
        if response.status_code not in (200, 207):
            raise CloudStorageError(f"Unexpected response from Nextcloud (HTTP {response.status_code}).")

    async def list_files(self, path: str) -> List[CloudFileEntry]:
        client = await self._get_client()
        url = self._folder_url(path)
        try:
            response = await client.request(
                "PROPFIND", url, headers={"Depth": "1", "Content-Type": "application/xml"},
                content=_PROPFIND_BODY,
            )
        except httpx.HTTPError as e:
            raise CloudStorageError(f"Could not reach {self.base_url}: {e}") from e

        if response.status_code == 401:
            raise CloudStorageError("Nextcloud rejected the credentials (401 Unauthorized).")
        if response.status_code == 404:
            raise CloudStorageError(
                f"Folder '{path}' was not found on Nextcloud. "
                "Check the configured path (it must already exist)."
            )
        if response.status_code != 207:
            raise CloudStorageError(f"Unexpected response from Nextcloud (HTTP {response.status_code}).")

        return self._parse_propfind(response.text, url)

    def _parse_propfind(self, xml_text: str, requested_url: str) -> List[CloudFileEntry]:
        try:
            root = ElementTree.fromstring(xml_text)
        except ElementTree.ParseError as e:
            raise CloudStorageError(f"Could not parse Nextcloud's file listing: {e}") from e

        requested_path = requested_url.split("/remote.php/dav/", 1)[-1].rstrip("/")

        entries: List[CloudFileEntry] = []
        for response_el in root.findall(f"{_DAV_NS}response"):
            href_el = response_el.find(f"{_DAV_NS}href")
            if href_el is None or not href_el.text:
                continue
            href_path = href_el.text.split("/remote.php/dav/", 1)[-1].rstrip("/")
            # Skip the entry describing the requested folder itself --
            # PROPFIND with Depth:1 includes it alongside its children.
            if href_path == requested_path:
                continue

            propstat = response_el.find(f"{_DAV_NS}propstat")
            if propstat is None:
                continue
            prop = propstat.find(f"{_DAV_NS}prop")
            if prop is None:
                continue

            displayname_el = prop.find(f"{_DAV_NS}displayname")
            name = displayname_el.text if displayname_el is not None and displayname_el.text else href_path.rsplit("/", 1)[-1]

            resourcetype_el = prop.find(f"{_DAV_NS}resourcetype")
            is_directory = resourcetype_el is not None and resourcetype_el.find(f"{_DAV_NS}collection") is not None

            size = None
            size_el = prop.find(f"{_DAV_NS}getcontentlength")
            if size_el is not None and size_el.text:
                try:
                    size = int(size_el.text)
                except ValueError:
                    size = None

            last_modified = None
            modified_el = prop.find(f"{_DAV_NS}getlastmodified")
            if modified_el is not None and modified_el.text:
                last_modified = modified_el.text

            entries.append(CloudFileEntry(
                name=name, is_directory=is_directory, size=size, last_modified=last_modified,
            ))

        entries.sort(key=lambda e: (not e.is_directory, e.name.lower()))
        return entries

    async def upload_file(self, path: str, filename: str, content: bytes) -> None:
        client = await self._get_client()
        url = self._file_url(path, filename)
        try:
            response = await client.put(url, content=content)
        except httpx.HTTPError as e:
            raise CloudStorageError(f"Could not reach {self.base_url}: {e}") from e

        if response.status_code == 401:
            raise CloudStorageError("Nextcloud rejected the credentials (401 Unauthorized).")
        if response.status_code == 409:
            raise CloudStorageError(
                f"Nextcloud rejected the upload (folder '{path}' likely doesn't exist)."
            )
        if response.status_code not in (200, 201, 204):
            raise CloudStorageError(f"Upload to Nextcloud failed (HTTP {response.status_code}).")

    async def download_file(self, path: str, filename: str) -> bytes:
        client = await self._get_client()
        url = self._file_url(path, filename)
        try:
            response = await client.get(url)
        except httpx.HTTPError as e:
            raise CloudStorageError(f"Could not reach {self.base_url}: {e}") from e

        if response.status_code == 401:
            raise CloudStorageError("Nextcloud rejected the credentials (401 Unauthorized).")
        if response.status_code == 404:
            raise CloudStorageError(f"File '{filename}' was not found in '{path}'.")
        if response.status_code != 200:
            raise CloudStorageError(f"Download from Nextcloud failed (HTTP {response.status_code}).")
        return response.content

    async def delete_file(self, path: str, filename: str) -> None:
        """Idempotent by design: a 404 (already gone) is treated as
        success, not an error -- the cloud-backup retention sweep
        (app/cloud_backup.py) calls this and must tolerate a backup
        already removed by an earlier, partially-failed sweep without
        treating that as a failure."""
        client = await self._get_client()
        url = self._file_url(path, filename)
        try:
            response = await client.delete(url)
        except httpx.HTTPError as e:
            raise CloudStorageError(f"Could not reach {self.base_url}: {e}") from e

        if response.status_code == 401:
            raise CloudStorageError("Nextcloud rejected the credentials (401 Unauthorized).")
        if response.status_code in (200, 204, 404):
            return
        raise CloudStorageError(f"Delete on Nextcloud failed (HTTP {response.status_code}).")

    async def create_folder(self, path: str) -> None:
        """MKCOL each path segment in turn -- WebDAV's MKCOL returns
        409 Conflict if an intermediate parent collection doesn't
        exist yet, it does not create nested collections in one call
        (unlike e.g. `mkdir -p`). A 405 Method Not Allowed for a
        segment that already exists is treated as success (Nextcloud's
        documented MKCOL behavior for an existing collection), making
        the whole operation idempotent and safe to call before every
        backup run."""
        client = await self._get_client()
        segments = [s for s in path.strip("/").split("/") if s]
        accumulated = ""
        for segment in segments:
            accumulated = f"{accumulated}/{segment}" if accumulated else segment
            url = self._folder_url(accumulated)
            try:
                response = await client.request("MKCOL", url)
            except httpx.HTTPError as e:
                raise CloudStorageError(f"Could not reach {self.base_url}: {e}") from e

            if response.status_code == 401:
                raise CloudStorageError("Nextcloud rejected the credentials (401 Unauthorized).")
            if response.status_code in (201, 405):
                continue
            raise CloudStorageError(
                f"Could not create folder '{accumulated}' on Nextcloud (HTTP {response.status_code})."
            )


async def load_nextcloud_configuration(db: AsyncSession) -> Optional[dict]:
    """Loads {base_url, username, app_password} from ClubSettings, or
    None if not (fully) configured yet. All three fields are required
    -- a partially-filled-in configuration is treated as "not
    configured" rather than attempted and failing confusingly."""
    result = await db.execute(
        select(ClubSetting).where(
            ClubSetting.key.in_(["nextcloud_base_url", "nextcloud_username", "nextcloud_app_password"])
        )
    )
    stored = {e.key: e.value for e in result.scalars().all() if e.value}

    base_url = stored.get("nextcloud_base_url")
    username = stored.get("nextcloud_username")
    try:
        app_password = decrypt(stored.get("nextcloud_app_password"))
    except DecryptionError:
        logger.error(
            "Could not decrypt the stored Nextcloud app password -- did SECRET_KEY change? "
            "Treating cloud storage as not configured until it's re-entered."
        )
        return None

    if not base_url or not username or not app_password:
        return None
    return {"base_url": base_url, "username": username, "app_password": app_password}


async def get_nextcloud_provider(
    db: AsyncSession, client: Optional[httpx.AsyncClient] = None,
) -> Optional[NextcloudProvider]:
    """Returns a configured NextcloudProvider, or None if the club
    hasn't set up Nextcloud credentials yet."""
    config = await load_nextcloud_configuration(db)
    if config is None:
        return None
    return NextcloudProvider(
        base_url=config["base_url"], username=config["username"],
        app_password=config["app_password"], client=client,
    )
