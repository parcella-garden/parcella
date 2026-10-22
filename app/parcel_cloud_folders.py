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

A parcel handed over to applicants (ADR 0101/0102) is never vacant,
so deactivate_if_vacant can't catch that turnover: schedule_handover_folders
retires the old folder on the handover date and optionally switches to
a folder the board picked for the new tenants -- immediately for a
handover dated today or earlier, on the date itself otherwise
(apply_scheduled_folder_switches, run by the background loop in
app/main.py).
"""
from datetime import date, datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.cloud_storage import CloudStorageError, get_cloud_storage_provider
from app.database import current_or_upcoming_tenant_filter
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
    assignment. If the parcel now has no current or upcoming resident
    (assigned_until IS NULL or still in the future -- an upcoming tenant
    moving in later counts too, ADR 0102), its active cloud folder (if
    any) is deactivated -- see module docstring."""
    result = await db.execute(
        select(MemberParcel.id).where(
            MemberParcel.parcel_id == parcel_id, current_or_upcoming_tenant_filter(),
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


async def get_scheduled_folder(db: AsyncSession, parcel_id: str) -> Optional[ParcelCloudFolder]:
    """The folder waiting to take over on a future handover date, if any."""
    result = await db.execute(
        select(ParcelCloudFolder).where(
            ParcelCloudFolder.parcel_id == parcel_id,
            ParcelCloudFolder.is_active.is_(False),
            ParcelCloudFolder.deactivated_at.is_(None),
            ParcelCloudFolder.active_from.is_not(None),
        )
    )
    return result.scalar_one_or_none()


def _retire(folder: ParcelCloudFolder) -> None:
    folder.is_active = False
    folder.deactivated_at = datetime.now(timezone.utc)


async def schedule_handover_folders(
    db: AsyncSession, parcel_id: str, *, handover_date: date,
    new_relative_path: Optional[str], set_by_user_id: Optional[str],
) -> None:
    """The folder side of a parcel handover. Flush only -- runs inside
    the handover's own transaction. Raises InvalidCloudPathError for an
    unsafe new path (validated before anything else is touched)."""
    new_path = sanitize_relative_path(new_relative_path) if new_relative_path else None

    # A previously scheduled switch is superseded by this handover.
    pending = await get_scheduled_folder(db, parcel_id)
    if pending is not None:
        pending.deactivated_at = datetime.now(timezone.utc)

    active = await get_active_folder(db, parcel_id)
    if handover_date <= date.today():
        if active is not None:
            _retire(active)
            await db.flush()  # free the one-active-per-parcel index first
        if new_path:
            db.add(ParcelCloudFolder(
                parcel_id=parcel_id, relative_path=new_path, is_active=True,
                set_by_user_id=set_by_user_id, active_from=handover_date,
            ))
    else:
        if active is not None:
            active.active_until = handover_date
        if new_path:
            db.add(ParcelCloudFolder(
                parcel_id=parcel_id, relative_path=new_path, is_active=False,
                set_by_user_id=set_by_user_id, active_from=handover_date,
            ))
    await db.flush()


async def apply_scheduled_folder_switches(db: AsyncSession) -> int:
    """Carries out switches whose date has come: retires active folders
    past their active_until, then activates scheduled folders whose
    active_from has arrived (retiring whatever is active on that parcel
    first). Returns how many folders changed; commits."""
    today = date.today()
    changed = 0
    result = await db.execute(
        select(ParcelCloudFolder).where(
            ParcelCloudFolder.is_active.is_(True), ParcelCloudFolder.active_until <= today,
        )
    )
    for folder in result.scalars().all():
        _retire(folder)
        changed += 1
    await db.flush()

    result = await db.execute(
        select(ParcelCloudFolder).where(
            ParcelCloudFolder.is_active.is_(False),
            ParcelCloudFolder.deactivated_at.is_(None),
            ParcelCloudFolder.active_from <= today,
        )
    )
    for folder in result.scalars().all():
        active = await get_active_folder(db, folder.parcel_id)
        if active is not None:
            _retire(active)
            await db.flush()
        folder.is_active = True
        await db.flush()
        changed += 1
    if changed:
        await db.commit()
    return changed


async def browse_folder_picker(
    db: AsyncSession, raw_pick_path: str, *, root_label: str, not_configured_message: str,
) -> dict:
    """The folder picker's state for one page view: browse the Nextcloud
    account tree from its root, directories only (docs/module-cloud-storage.md).
    Shared by the parcel page and the handover page. Returns path,
    breadcrumbs ([{name, pick_path}]), entries (None on error) and error."""
    path = sanitize_browse_subpath(raw_pick_path)
    breadcrumbs = [{"name": root_label, "pick_path": ""}]
    accumulated = []
    for segment in path.split("/") if path else []:
        accumulated.append(segment)
        breadcrumbs.append({"name": segment, "pick_path": "/".join(accumulated)})

    entries, error = None, None
    provider = await get_cloud_storage_provider(db)
    if provider is None:
        error = not_configured_message
    else:
        try:
            entries = [e for e in await provider.list_files(path) if e.is_directory]
        except CloudStorageError as e:
            error = str(e)
        finally:
            await provider.aclose()
    return {"path": path, "breadcrumbs": breadcrumbs, "entries": entries, "error": error}
