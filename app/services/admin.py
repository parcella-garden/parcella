"""Admin area: database helpers without HTTP (issue #416).

Called by the routes in app/routers/admin/.
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import (
    Announcement,
    CalendarEvent,
    ChangeHistory,
    ClubSetting,
    CouncilAbsence,
    CouncilPresence,
    GroupMembership,
    InventoryItem,
    Invitation,
    ItemLoan,
    MeterReading,
    ParcelCloudFolder,
    PurchaseRequest,
    PurchaseRequestApproval,
    Task,
    TaskAssignee,
    WorkSession,
    WorkTask,
)
from app.cloud_storage import CloudStorageError
from app.cloud_backup import is_backup_filename


# Every FK-to-users.id in the schema (see ADR 0040/audit) -- a user can
# only be permanently deleted if none of these reference them; anyone
# with a real footprint has to be deactivated instead (ADR 0005).
USER_REFERENCE_CHECKS = [
    (Invitation, Invitation.invited_by_id),
    (GroupMembership, GroupMembership.user_id),
    (ParcelCloudFolder, ParcelCloudFolder.set_by_user_id),
    (WorkSession, WorkSession.created_by_id),
    (WorkTask, WorkTask.created_by_id),
    (ChangeHistory, ChangeHistory.changed_by_id),
    (MeterReading, MeterReading.recorded_by_id),
    (PurchaseRequest, PurchaseRequest.requested_by_id),
    (PurchaseRequest, PurchaseRequest.created_by_id),
    (PurchaseRequest, PurchaseRequest.rejected_by_id),
    (PurchaseRequestApproval, PurchaseRequestApproval.user_id),
    (CalendarEvent, CalendarEvent.created_by_id),
    (CouncilPresence, CouncilPresence.user_id),
    (CouncilAbsence, CouncilAbsence.user_id),
    (Announcement, Announcement.created_by_id),
    (InventoryItem, InventoryItem.created_by_id),
    (ItemLoan, ItemLoan.created_by_id),
    (TaskAssignee, TaskAssignee.user_id),
    (Task, Task.created_by_id),
]


async def user_has_history(db: AsyncSession, user_id: str) -> bool:
    """True if any row anywhere in the schema still references this
    user -- see USER_REFERENCE_CHECKS. A hard delete is only offered
    when this is False."""
    for model, column in USER_REFERENCE_CHECKS:
        result = await db.execute(select(model.id).where(column == user_id).limit(1))
        if result.scalar_one_or_none() is not None:
            return True
    return False


# ---------------------------------------------------------------------------
# Cloud backups: scheduled uploads of backup_download's zip to the club's
# connected Nextcloud folder, with retention pruning and a restore-from-
# cloud picker. See app/cloud_backup.py and docs/ADR/0055-scheduled-cloud-backups.md.
# ---------------------------------------------------------------------------

async def list_cloud_backups(provider, folder: str):
    """Returns cloud backup entries (name/size/last_modified), newest
    first, or an empty list if the folder doesn't exist yet or a
    transient error occurs -- a listing failure here shouldn't block
    rendering the settings page itself."""
    if not folder:
        return []
    try:
        entries = await provider.list_files(folder)
    except CloudStorageError:
        return []
    return sorted(
        (e for e in entries if not e.is_directory and is_backup_filename(e.name)),
        key=lambda e: e.name, reverse=True,
    )


async def upsert_club_setting(db: AsyncSession, key: str, value: Optional[str], description: str = "") -> None:
    result = await db.execute(select(ClubSetting).where(ClubSetting.key == key))
    entry = result.scalar_one_or_none()
    if entry:
        entry.value = value
    else:
        db.add(ClubSetting(key=key, value=value, description=description))
