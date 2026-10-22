"""
Cloud storage connectors: lets a club link Parcella to a file-storage
backend it already runs, so board members can browse, upload to, and
download from a per-parcel folder (and invoices, contact documents,
backups, the Markdown website) without leaving Parcella.

One backend at a time, chosen from a dropdown on Admin -> Integrations
-> Cloud storage (ADR 0106), through the shared ProviderRegistry
(app/provider_registry.py, same pattern as the website connectors):
Nextcloud, any WebDAV server (ownCloud, Seafile, HiDrive, Hetzner
Storage Box, ...), or S3-compatible object storage (AWS, Hetzner Object
Storage, MinIO, Wasabi, ...). Every feature asks for
get_cloud_storage_provider(db) and only talks to the CloudStorageProvider
interface, never to a specific backend.

Scope, deliberately: this connects Parcella's board/admin users to
files. It does NOT manage which individual members can see a given
folder -- that access is granted directly in the storage itself (e.g.
Nextcloud shares/"Freigaben"), independent of and invisible to Parcella.
See docs/module-cloud-storage.md for the reasoning, including why ending
a tenancy in Parcella does not revoke any share.
"""
import hashlib
import hmac
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional
from urllib.parse import quote, unquote, urlsplit
from xml.etree import ElementTree

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.provider_registry import ConfigField, ProviderRegistry

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
    """Interface every cloud storage connector implements. A new backend
    is a new subclass plus one entry in CLOUD_STORAGE below -- not a
    change to this class or to any feature that stores files.

    Originally list/upload/download only, deliberately narrow for v1 --
    no delete, no folder creation, since the folder a club points
    Parcella at was expected to already exist. Extended for issue #141
    (scheduled cloud backups, see docs/ADR/0055-scheduled-cloud-backups.md):
    that feature needs to create its own destination folder on first
    run and prune old backups beyond a retention count, so `delete_file`
    and `create_folder` were added -- scoped narrowly to that use case,
    not a general "let board tooling delete member files" decision.
    """

    type: str = ""
    config_fields: List[ConfigField] = []

    @classmethod
    async def build(cls, config: dict, db: AsyncSession) -> "CloudStorageProvider":
        raise NotImplementedError

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

    async def aclose(self) -> None:
        """Releases network clients. Safe to call more than once."""


def _path_parts(*segments: str) -> List[str]:
    """Splits folder/file name segments into path parts. Each segment may
    itself be a multi-part relative path (e.g. "parcels/G016").

    Rejects '..' segments: the folder path is validated before it gets
    here (sanitize_relative_path), but the filename passed to
    download_file/upload_file comes straight from a query parameter /
    uploaded filename with no such check, and could otherwise walk this
    join outside the intended folder within the storage account
    (flagged by an external pentest)."""
    parts = [
        part for s in segments if s
        for part in s.strip("/").split("/")
        if part and part != "."
    ]
    if any(part == ".." for part in parts):
        raise CloudStorageError("Invalid path: '..' is not allowed.")
    return parts


def _join_dav_path(*segments: str) -> str:
    """Builds a URL-safe path from folder/file name segments, quoting each
    one individually so slashes stay as path separators but spaces,
    umlauts, parentheses etc. are encoded correctly (and the separator
    isn't percent-encoded into "%2F" along with them)."""
    return "/".join(quote(part, safe="") for part in _path_parts(*segments))


def _capitalized(text: str) -> str:
    return text[:1].upper() + text[1:]


# ---------------------------------------------------------------------------
# WebDAV (generic) and Nextcloud
# ---------------------------------------------------------------------------

class WebDAVProvider(CloudStorageProvider):
    """Any WebDAV server: PROPFIND to list, PUT/GET/DELETE for files,
    MKCOL for folders. `root_url` is the WebDAV address of the folder
    that Parcella's paths are relative to."""

    type = "webdav"
    label = "the WebDAV server"
    config_fields = [
        ConfigField("root_url", kind="url", required=True, placeholder="https://dav.example.com/remote.php/webdav", hint=True),
        ConfigField("username", required=True),
        ConfigField("password", kind="secret", required=True),
    ]

    def __init__(self, root_url: str, username: str, password: str, client: Optional[httpx.AsyncClient] = None):
        self.root_url = root_url.rstrip("/")
        self.username = username
        self.password = password
        # A client can be injected (tests use this with an
        # httpx.MockTransport, since no real server is reachable from
        # Parcella's own test/CI environment); otherwise one is created
        # lazily and owned/closed by this instance.
        self._client = client
        self._owns_client = client is None

    @classmethod
    async def build(cls, config: dict, db: AsyncSession) -> "WebDAVProvider":
        return cls(root_url=config["root_url"], username=config["username"], password=config["password"])

    @property
    def _dav_root(self) -> str:
        return self.root_url

    @property
    def _host_label(self) -> str:
        return urlsplit(self.root_url).netloc or self.root_url

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=20.0, auth=(self.username, self.password))
        return self._client

    async def aclose(self) -> None:
        if self._owns_client and self._client is not None:
            await self._client.aclose()
            self._client = None

    def _folder_url(self, path: str) -> str:
        joined = _join_dav_path(path)
        return f"{self._dav_root}/{joined}" if joined else self._dav_root

    def _file_url(self, path: str, filename: str) -> str:
        return f"{self._dav_root}/{_join_dav_path(path, filename)}"

    def _rejected(self) -> CloudStorageError:
        return CloudStorageError(f"{_capitalized(self.label)} rejected the credentials (401 Unauthorized).")

    async def test_connection(self) -> None:
        client = await self._get_client()
        try:
            response = await client.request("PROPFIND", self._dav_root, headers={"Depth": "0"})
        except httpx.HTTPError as e:
            raise CloudStorageError(f"Could not reach {self._host_label}: {e}") from e

        if response.status_code == 401:
            raise CloudStorageError(
                f"{_capitalized(self.label)} rejected the credentials (401 Unauthorized). "
                "Check the username and password."
            )
        if response.status_code == 404:
            raise CloudStorageError(f"No WebDAV folder at this address ({self._dav_root}).")
        if response.status_code not in (200, 207):
            raise CloudStorageError(f"Unexpected response from {self.label} (HTTP {response.status_code}).")

    async def list_files(self, path: str) -> List[CloudFileEntry]:
        client = await self._get_client()
        url = self._folder_url(path)
        try:
            response = await client.request(
                "PROPFIND", url, headers={"Depth": "1", "Content-Type": "application/xml"},
                content=_PROPFIND_BODY,
            )
        except httpx.HTTPError as e:
            raise CloudStorageError(f"Could not reach {self._host_label}: {e}") from e

        if response.status_code == 401:
            raise self._rejected()
        if response.status_code == 404:
            raise CloudStorageError(
                f"Folder '{path}' was not found on {self.label}. "
                "Check the configured path (it must already exist)."
            )
        if response.status_code != 207:
            raise CloudStorageError(f"Unexpected response from {self.label} (HTTP {response.status_code}).")

        return self._parse_propfind(response.text, url)

    def _parse_propfind(self, xml_text: str, requested_url: str) -> List[CloudFileEntry]:
        try:
            root = ElementTree.fromstring(xml_text)
        except ElementTree.ParseError as e:
            raise CloudStorageError(f"Could not parse the file listing: {e}") from e

        # Servers answer with an absolute path or a full URL in <href>,
        # percent-encoded in their own way; comparing the decoded paths
        # works for all of them.
        requested_path = unquote(urlsplit(requested_url).path).rstrip("/")

        entries: List[CloudFileEntry] = []
        for response_el in root.findall(f"{_DAV_NS}response"):
            href_el = response_el.find(f"{_DAV_NS}href")
            if href_el is None or not href_el.text:
                continue
            href_path = unquote(urlsplit(href_el.text).path).rstrip("/")
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
            raise CloudStorageError(f"Could not reach {self._host_label}: {e}") from e

        if response.status_code == 401:
            raise self._rejected()
        if response.status_code == 409:
            raise CloudStorageError(
                f"{_capitalized(self.label)} rejected the upload (folder '{path}' likely doesn't exist)."
            )
        if response.status_code not in (200, 201, 204):
            raise CloudStorageError(f"Upload to {self.label} failed (HTTP {response.status_code}).")

    async def download_file(self, path: str, filename: str) -> bytes:
        client = await self._get_client()
        url = self._file_url(path, filename)
        try:
            response = await client.get(url)
        except httpx.HTTPError as e:
            raise CloudStorageError(f"Could not reach {self._host_label}: {e}") from e

        if response.status_code == 401:
            raise self._rejected()
        if response.status_code == 404:
            raise CloudStorageError(f"File '{filename}' was not found in '{path}'.")
        if response.status_code != 200:
            raise CloudStorageError(f"Download from {self.label} failed (HTTP {response.status_code}).")
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
            raise CloudStorageError(f"Could not reach {self._host_label}: {e}") from e

        if response.status_code == 401:
            raise self._rejected()
        if response.status_code in (200, 204, 404):
            return
        raise CloudStorageError(f"Delete on {self.label} failed (HTTP {response.status_code}).")

    async def create_folder(self, path: str) -> None:
        """MKCOL each path segment in turn -- WebDAV's MKCOL returns
        409 Conflict if an intermediate parent collection doesn't
        exist yet, it does not create nested collections in one call
        (unlike e.g. `mkdir -p`). A 405 Method Not Allowed for a
        segment that already exists is treated as success (the
        documented MKCOL behavior for an existing collection), making
        the whole operation idempotent and safe to call before every
        backup run."""
        client = await self._get_client()
        accumulated = ""
        for segment in _path_parts(path):
            accumulated = f"{accumulated}/{segment}" if accumulated else segment
            url = self._folder_url(accumulated)
            try:
                response = await client.request("MKCOL", url)
            except httpx.HTTPError as e:
                raise CloudStorageError(f"Could not reach {self._host_label}: {e}") from e

            if response.status_code == 401:
                raise self._rejected()
            if response.status_code in (201, 405):
                continue
            raise CloudStorageError(
                f"Could not create folder '{accumulated}' on {self.label} (HTTP {response.status_code})."
            )


class NextcloudProvider(WebDAVProvider):
    """Nextcloud is WebDAV with a known root per user
    (`/remote.php/dav/files/<user>`), so it only needs the server
    address -- and an app password rather than the login password."""

    type = "nextcloud"
    label = "Nextcloud"
    config_fields = [
        ConfigField("base_url", kind="url", required=True, placeholder="https://cloud.example.com"),
        ConfigField("username", required=True),
        ConfigField("app_password", kind="secret", required=True, hint=True),
    ]

    def __init__(
        self, base_url: str, username: str, app_password: str,
        client: Optional[httpx.AsyncClient] = None,
    ):
        self.base_url = base_url.rstrip("/")
        super().__init__(
            root_url=f"{self.base_url}/remote.php/dav/files/{quote(username, safe='')}",
            username=username, password=app_password, client=client,
        )
        self.app_password = app_password

    @classmethod
    async def build(cls, config: dict, db: AsyncSession) -> "NextcloudProvider":
        return cls(base_url=config["base_url"], username=config["username"], app_password=config["app_password"])

    @property
    def _host_label(self) -> str:
        return self.base_url

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


# ---------------------------------------------------------------------------
# S3-compatible object storage
# ---------------------------------------------------------------------------

_S3_NS = "{http://s3.amazonaws.com/doc/2006-03-01/}"
_EMPTY_SHA256 = hashlib.sha256(b"").hexdigest()


def _s3_quote(value: str) -> str:
    """URI encoding as SigV4 defines it: everything except unreserved
    characters (A-Z a-z 0-9 - _ . ~)."""
    return quote(value, safe="-_.~")


def sigv4_headers(
    *, method: str, host: str, path: str, query: Dict[str, str], headers: Dict[str, str],
    payload_hash: str, access_key_id: str, secret_access_key: str, region: str,
    now: Optional[datetime] = None, service: str = "s3",
) -> Dict[str, str]:
    """AWS Signature Version 4 for one request, standard library only.
    `path` must already be URI-encoded (each segment with _s3_quote).
    Returns the headers to send: the given ones plus x-amz-date,
    x-amz-content-sha256 and Authorization."""
    now = now or datetime.now(timezone.utc)
    amz_date = now.strftime("%Y%m%dT%H%M%SZ")
    date_stamp = now.strftime("%Y%m%d")

    signed = {k.lower(): " ".join(str(v).strip().split()) for k, v in headers.items()}
    signed["host"] = host
    signed["x-amz-content-sha256"] = payload_hash
    signed["x-amz-date"] = amz_date
    signed_header_names = ";".join(sorted(signed))
    canonical_headers = "".join(f"{k}:{signed[k]}\n" for k in sorted(signed))
    canonical_query = "&".join(
        f"{_s3_quote(k)}={_s3_quote(v)}" for k, v in sorted(query.items())
    )
    canonical_request = "\n".join([
        method.upper(), path or "/", canonical_query, canonical_headers, signed_header_names, payload_hash,
    ])
    scope = f"{date_stamp}/{region}/{service}/aws4_request"
    string_to_sign = "\n".join([
        "AWS4-HMAC-SHA256", amz_date, scope, hashlib.sha256(canonical_request.encode("utf-8")).hexdigest(),
    ])

    def _hmac(key: bytes, msg: str) -> bytes:
        return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()

    signing_key = _hmac(_hmac(_hmac(_hmac(f"AWS4{secret_access_key}".encode("utf-8"), date_stamp), region), service), "aws4_request")
    signature = hmac.new(signing_key, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()

    result = dict(headers)
    result["x-amz-date"] = amz_date
    result["x-amz-content-sha256"] = payload_hash
    result["Authorization"] = (
        f"AWS4-HMAC-SHA256 Credential={access_key_id}/{scope}, "
        f"SignedHeaders={signed_header_names}, Signature={signature}"
    )
    return result


class S3Provider(CloudStorageProvider):
    """S3-compatible object storage, path-style addressing
    (`<endpoint>/<bucket>/<key>`), which AWS, Hetzner, MinIO, Wasabi and
    others all accept. S3 has no real folders: a "folder" is a key
    prefix, and create_folder writes an empty `<folder>/` marker so an
    empty folder still shows up in listings, as most S3 tools do."""

    type = "s3"
    config_fields = [
        ConfigField("endpoint_url", kind="url", required=True, placeholder="https://fsn1.your-objectstorage.com", hint=True),
        ConfigField("region", required=True, default="us-east-1", placeholder="eu-central-1", hint=True),
        ConfigField("bucket", required=True),
        ConfigField("access_key_id", required=True),
        ConfigField("secret_access_key", kind="secret", required=True),
        ConfigField("path_prefix", kind="path", hint=True),
    ]

    def __init__(
        self, endpoint_url: str, region: str, bucket: str, access_key_id: str, secret_access_key: str,
        path_prefix: str = "", client: Optional[httpx.AsyncClient] = None,
    ):
        self.endpoint_url = endpoint_url.rstrip("/")
        self.region = region
        self.bucket = bucket
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key
        self.path_prefix = "/".join(_path_parts(path_prefix or ""))
        self._client = client
        self._owns_client = client is None

    @classmethod
    async def build(cls, config: dict, db: AsyncSession) -> "S3Provider":
        return cls(
            endpoint_url=config["endpoint_url"], region=config["region"], bucket=config["bucket"],
            access_key_id=config["access_key_id"], secret_access_key=config["secret_access_key"],
            path_prefix=config.get("path_prefix") or "",
        )

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client

    async def aclose(self) -> None:
        if self._owns_client and self._client is not None:
            await self._client.aclose()
            self._client = None

    def _key(self, *segments: str) -> str:
        return "/".join(([self.path_prefix] if self.path_prefix else []) + _path_parts(*segments))

    async def _request(
        self, method: str, key: str = "", query: Optional[Dict[str, str]] = None, content: bytes = b"",
    ) -> httpx.Response:
        query = query or {}
        endpoint = urlsplit(self.endpoint_url)
        path = f"{endpoint.path.rstrip('/')}/{_s3_quote(self.bucket)}"
        if key:
            path += "/" + "/".join(_s3_quote(part) for part in key.split("/"))
        headers = sigv4_headers(
            method=method, host=endpoint.netloc, path=path, query=query, headers={},
            payload_hash=hashlib.sha256(content).hexdigest() if content else _EMPTY_SHA256,
            access_key_id=self.access_key_id, secret_access_key=self.secret_access_key, region=self.region,
        )
        url = f"{endpoint.scheme}://{endpoint.netloc}{path}"
        if query:
            url += "?" + "&".join(f"{_s3_quote(k)}={_s3_quote(v)}" for k, v in sorted(query.items()))
        client = await self._get_client()
        try:
            return await client.request(method, url, headers=headers, content=content)
        except httpx.HTTPError as e:
            raise CloudStorageError(f"Could not reach {endpoint.netloc}: {e}") from e

    @staticmethod
    def _error(response: httpx.Response, action: str) -> CloudStorageError:
        if response.status_code in (401, 403):
            return CloudStorageError("The S3 storage rejected the credentials (access denied). Check the keys and bucket.")
        if response.status_code == 404:
            return CloudStorageError("The bucket wasn't found. Check the bucket name, endpoint and region.")
        return CloudStorageError(f"{action} on the S3 storage failed (HTTP {response.status_code}).")

    async def test_connection(self) -> None:
        response = await self._request("GET", query={"list-type": "2", "max-keys": "1"})
        if response.status_code != 200:
            raise self._error(response, "Listing")

    async def list_files(self, path: str) -> List[CloudFileEntry]:
        prefix = self._key(path)
        prefix = f"{prefix}/" if prefix else ""
        entries: List[CloudFileEntry] = []
        token = None
        while True:
            query = {"list-type": "2", "prefix": prefix, "delimiter": "/"}
            if token:
                query["continuation-token"] = token
            response = await self._request("GET", query=query)
            if response.status_code != 200:
                raise self._error(response, "Listing")
            try:
                root = ElementTree.fromstring(response.text)
            except ElementTree.ParseError as e:
                raise CloudStorageError(f"Could not parse the file listing: {e}") from e
            for cp in root.findall(f"{_S3_NS}CommonPrefixes"):
                sub = (cp.findtext(f"{_S3_NS}Prefix") or "")[len(prefix):].strip("/")
                if sub:
                    entries.append(CloudFileEntry(name=sub, is_directory=True))
            for obj in root.findall(f"{_S3_NS}Contents"):
                name = (obj.findtext(f"{_S3_NS}Key") or "")[len(prefix):]
                if not name or "/" in name:
                    continue  # the folder's own marker, or deeper levels
                size_text = obj.findtext(f"{_S3_NS}Size")
                entries.append(CloudFileEntry(
                    name=name, is_directory=False,
                    size=int(size_text) if size_text and size_text.isdigit() else None,
                    last_modified=obj.findtext(f"{_S3_NS}LastModified"),
                ))
            token = root.findtext(f"{_S3_NS}NextContinuationToken")
            if root.findtext(f"{_S3_NS}IsTruncated") == "true" and token:
                continue
            break

        if prefix and not entries:
            # S3 can't tell an empty folder from a missing one except by
            # its marker; treat "no marker, nothing in it" as missing,
            # like WebDAV's 404.
            marker = await self._request("HEAD", key=prefix.rstrip("/") + "/")
            if marker.status_code != 200:
                raise CloudStorageError(
                    f"Folder '{path}' was not found on the S3 storage. "
                    "Check the configured path (it must already exist)."
                )
        entries.sort(key=lambda e: (not e.is_directory, e.name.lower()))
        return entries

    async def upload_file(self, path: str, filename: str, content: bytes) -> None:
        response = await self._request("PUT", key=self._key(path, filename), content=content)
        if response.status_code not in (200, 201, 204):
            raise self._error(response, "Upload")

    async def download_file(self, path: str, filename: str) -> bytes:
        response = await self._request("GET", key=self._key(path, filename))
        if response.status_code == 404:
            raise CloudStorageError(f"File '{filename}' was not found in '{path}'.")
        if response.status_code != 200:
            raise self._error(response, "Download")
        return response.content

    async def delete_file(self, path: str, filename: str) -> None:
        """Idempotent, like the WebDAV provider (S3 answers 204 either way)."""
        response = await self._request("DELETE", key=self._key(path, filename))
        if response.status_code not in (200, 204, 404):
            raise self._error(response, "Delete")

    async def create_folder(self, path: str) -> None:
        accumulated = []
        for segment in _path_parts(path):
            accumulated.append(segment)
            response = await self._request("PUT", key=self._key("/".join(accumulated)) + "/")
            if response.status_code not in (200, 201, 204):
                raise self._error(response, "Creating a folder")


# ---------------------------------------------------------------------------
# Which backend is active
# ---------------------------------------------------------------------------

CLOUD_STORAGE = ProviderRegistry(
    active_key="cloud_storage_provider", setting_prefix="cloud_storage", i18n_prefix="cloud_storage.providers",
    providers=(NextcloudProvider, WebDAVProvider, S3Provider), label="cloud storage",
)


async def get_cloud_storage_provider(db: AsyncSession) -> Optional[CloudStorageProvider]:
    """The active, fully configured cloud storage, or None if the club
    hasn't set one up -- callers check for None rather than catching an
    exception for "not set up"."""
    return await CLOUD_STORAGE.get_active(db)
