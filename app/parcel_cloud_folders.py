"""
Lifecycle rules for ParcelCloudFolder (see app/models.py for the table
and the reasoning behind scoping it to the parcel rather than a single
MemberParcel row).

The one safety-relevant rule lives here: deactivate_if_vacant. It must
be called after any action that can end a resident's tenancy (setting
MemberParcel.assigned_until), so that once a parcel has zero remaining
active residents, its cloud folder is marked inactive immediately --
new tenants moving in later never see or inherit the departing
tenants' folder path. Re-configuring the folder for the new tenancy is
a deliberate, separate action a board member takes afterwards.
"""
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import current_tenant_filter
from app.models import MemberParcel, ParcelCloudFolder


class InvalidCloudPathError(Exception):
    """Raised when a submitted relative path is unsafe or malformed."""


def sanitize_relative_path(raw_path: str) -> str:
    """Normalizes a board-entered relative folder path and rejects
    anything that could escape the Nextcloud account's file root.
    Intentionally strict: this path is later joined onto a WebDAV URL,
    so a stray '..' segment could otherwise reach outside the intended
    folder tree."""
    path = raw_path.strip().strip("/")
    if not path:
        raise InvalidCloudPathError("Please enter a folder path.")

    segments = [seg for seg in path.split("/") if seg not in ("", ".")]
    if any(seg == ".." for seg in segments):
        raise InvalidCloudPathError("The path may not contain '..'.")
    if not segments:
        raise InvalidCloudPathError("Please enter a folder path.")

    return "/".join(segments)


def sanitize_browse_subpath(raw_path: str) -> str:
    """Normalizes the `cloud_path` query param used to browse into a
    subfolder of the parcel's configured cloud folder (issue #201).
    Unlike sanitize_relative_path() above, an empty result is valid
    here -- it means "the configured folder's own root", not an error.
    A '..' segment (or anything else that doesn't survive normalization)
    is silently dropped back to the root rather than raising, since this
    only ever reaches here from a link Parcella itself generated or a
    hand-edited URL -- _join_dav_path() (app/cloud_storage.py) still
    rejects '..' defensively when the resulting path is actually used
    for a WebDAV request."""
    path = (raw_path or "").strip().strip("/")
    if not path:
        return ""
    segments = [seg for seg in path.split("/") if seg not in ("", ".")]
    if any(seg == ".." for seg in segments):
        return ""
    return "/".join(segments)


async def get_active_folder(db: AsyncSession, parcel_id: str) -> Optional[ParcelCloudFolder]:
    result = await db.execute(
        select(ParcelCloudFolder).where(
            ParcelCloudFolder.parcel_id == parcel_id, ParcelCloudFolder.is_active.is_(True),
        )
    )
    return result.scalar_one_or_none()


async def set_active_folder(
    db: AsyncSession, parcel_id: str, raw_path: str, set_by_user_id: str,
) -> ParcelCloudFolder:
    """Sets (or corrects) the parcel's currently-active folder path.
    If an active folder already exists for this parcel, its path is
    updated in place (e.g. fixing a typo mid-tenancy) rather than
    spawning a new history row -- a new row is only created when there
    is no active folder, i.e. after a full turnover."""
    relative_path = sanitize_relative_path(raw_path)

    active = await get_active_folder(db, parcel_id)
    if active:
        active.relative_path = relative_path
        await db.commit()
        return active

    folder = ParcelCloudFolder(
        parcel_id=parcel_id, relative_path=relative_path,
        is_active=True, set_by_user_id=set_by_user_id,
    )
    db.add(folder)
    await db.commit()
    return folder


async def deactivate_if_vacant(db: AsyncSession, parcel_id: str) -> None:
    """Call this after any change that can end a MemberParcel
    assignment. If the parcel now has no current resident (assigned_until
    IS NULL or still in the future), its active cloud folder (if any) is
    deactivated -- see module docstring."""
    result = await db.execute(
        select(MemberParcel.id).where(
            MemberParcel.parcel_id == parcel_id, current_tenant_filter(),
        )
    )
    still_has_active_resident = result.first() is not None
    if still_has_active_resident:
        return

    active = await get_active_folder(db, parcel_id)
    if active:
        active.is_active = False
        active.deactivated_at = datetime.now(timezone.utc)
        await db.commit()
