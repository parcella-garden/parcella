"""
Documents for external contacts, kept in the connected cloud storage
(docs/module-external-contacts.md, ADR 0097).

One club-wide base folder (ClubSetting EXTERNAL_CONTACTS_FOLDER_SETTING,
e.g. "kgv_dokumente/extern", set on the admin integrations page) holds
one subfolder per contact. The board creates those subfolders by hand
in the cloud and picks one on each contact (ExternalContact.cloud_folder
stores just its name). Received vs. sent is up to the club: whatever
subfolders exist inside a contact's folder can be browsed.

Backend-agnostic on purpose: everything goes through the
CloudStorageProvider interface (app/cloud_storage.py), nothing here
knows it's Nextcloud.
"""
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ClubSetting
from app.parcel_cloud_folders import InvalidCloudPathError

EXTERNAL_CONTACTS_FOLDER_SETTING = "external_contacts_cloud_folder"


async def load_base_folder(db: AsyncSession) -> Optional[str]:
    value = await db.scalar(select(ClubSetting.value).where(ClubSetting.key == EXTERNAL_CONTACTS_FOLDER_SETTING))
    return value or None


def sanitize_folder_name(raw: str) -> str:
    """A contact's folder is exactly one level below the base folder --
    a single name, no path separators, no '..'."""
    name = (raw or "").strip()
    if not name or "/" in name or "\\" in name or name in (".", ".."):
        raise InvalidCloudPathError("Invalid folder name.")
    return name


def upload_filename(raw: Optional[str]) -> str:
    """The uploaded file's own name without any client-side directory
    part (some browsers send a full Windows path), so it can't land in
    a different subfolder than the one being browsed."""
    name = (raw or "").replace("\\", "/").rsplit("/", 1)[-1].strip()
    if not name or name in (".", ".."):
        raise InvalidCloudPathError("Invalid file name.")
    return name


def contact_folder_path(base_folder: str, cloud_folder: str, browse_path: str = "") -> str:
    """Full relative path in the cloud for a contact's folder, or a
    subfolder of it being browsed (already sanitized by the caller via
    sanitize_browse_subpath)."""
    path = f"{base_folder}/{cloud_folder}"
    return f"{path}/{browse_path}" if browse_path else path

