"""
Scheduled cloud backups (issue #141, docs/ADR/0055-scheduled-cloud-backups.md):
uploads a fresh backup (app/backup.py's build_backup_zip, the same
zip shape the manual local download produces) to the club's connected
Nextcloud folder on a configurable schedule, prunes old backups beyond
a retention count, and records the outcome in ClubSettings -- read by
both the background scheduler (app/main.py) and the manual "back up to
cloud now" button (app/routers/admin.py), so both share one source of
truth for "did the last run succeed."

Deliberately no Linux cron: the schedule is driven by an in-process
asyncio loop, the same pattern already used for the ticket-mailbox poll
and the update check (see app/main.py).
"""
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ClubSetting
from app.backup import build_backup_zip, BackupError
from app.cloud_storage import get_cloud_storage_provider, CloudStorageError, CloudFileEntry

KEY_ENABLED = "cloud_backup_enabled"
KEY_FOLDER = "cloud_backup_folder"
KEY_FREQUENCY = "cloud_backup_frequency"
KEY_RETENTION_COUNT = "cloud_backup_retention_count"
KEY_LAST_RUN_AT = "cloud_backup_last_run_at"
KEY_LAST_RUN_STATUS = "cloud_backup_last_run_status"
KEY_LAST_RUN_ERROR = "cloud_backup_last_run_error"

FREQUENCY_CHOICES = ("hourly", "daily", "weekly", "monthly")
DEFAULT_FREQUENCY = "daily"
DEFAULT_RETENTION_COUNT = 10

# Fixed-duration approximations, not calendar-aware -- consistent with
# the existing background loops (app/main.py), which are all simple
# fixed-interval ticks rather than wall-clock-aligned schedules.
CLOUD_BACKUP_FREQUENCY_SECONDS = {
    "hourly": 60 * 60,
    "daily": 24 * 60 * 60,
    "weekly": 7 * 24 * 60 * 60,
    "monthly": 30 * 24 * 60 * 60,
}

BACKUP_NAME_PREFIX = "parcella-backup-"
BACKUP_NAME_SUFFIX = ".zip"


def is_backup_filename(name: str) -> bool:
    """Whether a cloud file entry's name matches the naming pattern
    build_backup_zip() produces -- used both to filter the "existing
    backups" list shown to an admin and to decide what the retention
    sweep is allowed to touch (so it never deletes an unrelated file
    someone else put in the same folder)."""
    return name.startswith(BACKUP_NAME_PREFIX) and name.endswith(BACKUP_NAME_SUFFIX)


@dataclass
class CloudBackupSettings:
    enabled: bool
    folder: str
    frequency: str
    retention_count: int
    last_run_at: Optional[datetime]
    last_run_status: Optional[str]  # "success" | "error" | None (never run)
    last_run_error: Optional[str]


async def _get_setting(db: AsyncSession, key: str) -> Optional[str]:
    result = await db.execute(select(ClubSetting).where(ClubSetting.key == key))
    entry = result.scalar_one_or_none()
    return entry.value if entry else None


async def _set_setting(db: AsyncSession, key: str, value: Optional[str], description: str) -> None:
    result = await db.execute(select(ClubSetting).where(ClubSetting.key == key))
    entry = result.scalar_one_or_none()
    if entry:
        entry.value = value
    else:
        db.add(ClubSetting(key=key, value=value, description=description))


async def get_cloud_backup_settings(db: AsyncSession) -> CloudBackupSettings:
    """All settings in one round trip -- same shape as
    app/update_check.py's get_update_status()."""
    enabled_raw = await _get_setting(db, KEY_ENABLED)
    folder = await _get_setting(db, KEY_FOLDER) or ""
    frequency = await _get_setting(db, KEY_FREQUENCY) or DEFAULT_FREQUENCY
    retention_raw = await _get_setting(db, KEY_RETENTION_COUNT)
    last_run_at_raw = await _get_setting(db, KEY_LAST_RUN_AT)

    try:
        retention_count = int(retention_raw) if retention_raw else DEFAULT_RETENTION_COUNT
    except ValueError:
        retention_count = DEFAULT_RETENTION_COUNT

    return CloudBackupSettings(
        enabled=(enabled_raw or "false").strip().lower() in ("true", "1", "ja", "an"),
        folder=folder,
        frequency=frequency if frequency in FREQUENCY_CHOICES else DEFAULT_FREQUENCY,
        retention_count=retention_count,
        last_run_at=datetime.fromisoformat(last_run_at_raw) if last_run_at_raw else None,
        last_run_status=await _get_setting(db, KEY_LAST_RUN_STATUS),
        last_run_error=await _get_setting(db, KEY_LAST_RUN_ERROR),
    )


async def save_cloud_backup_settings(
    db: AsyncSession, *, enabled: bool, folder: str, frequency: str, retention_count: int,
) -> None:
    if frequency not in FREQUENCY_CHOICES:
        raise ValueError(f"invalid frequency: {frequency!r}")
    if retention_count < 1:
        raise ValueError("retention_count must be at least 1")

    await _set_setting(db, KEY_ENABLED, "true" if enabled else "false",
                        "Whether scheduled cloud backups are on (see app/cloud_backup.py)")
    await _set_setting(db, KEY_FOLDER, folder,
                        "Destination folder in the connected cloud storage for scheduled backups")
    await _set_setting(db, KEY_FREQUENCY, frequency,
                        "How often a scheduled cloud backup runs: hourly/daily/weekly/monthly")
    await _set_setting(db, KEY_RETENTION_COUNT, str(retention_count),
                        "How many scheduled cloud backups to keep before pruning the oldest")
    await db.commit()


def is_backup_due(cfg: CloudBackupSettings, now: Optional[datetime] = None) -> bool:
    """Pure function, no I/O. False if disabled; True if never run
    before; else True iff frequency's worth of time has elapsed since
    the last run."""
    if not cfg.enabled:
        return False
    if cfg.last_run_at is None:
        return True
    now = now or datetime.now(timezone.utc)
    elapsed = (now - cfg.last_run_at).total_seconds()
    return elapsed >= CLOUD_BACKUP_FREQUENCY_SECONDS[cfg.frequency]


async def _record_run(db: AsyncSession, status: str, error: Optional[str]) -> None:
    await _set_setting(db, KEY_LAST_RUN_AT, datetime.now(timezone.utc).isoformat(),
                        "When the last scheduled/manual cloud backup ran (see app/cloud_backup.py)")
    await _set_setting(db, KEY_LAST_RUN_STATUS, status,
                        "Outcome of the last cloud backup run: success/error")
    await _set_setting(db, KEY_LAST_RUN_ERROR, error,
                        "Error message from the last cloud backup run, if any (cleared on success)")
    await db.commit()


async def _sweep_retention(provider, folder: str, retention_count: int) -> None:
    entries: List[CloudFileEntry] = await provider.list_files(folder)
    backups = sorted(
        (e for e in entries if not e.is_directory and is_backup_filename(e.name)),
        key=lambda e: e.name,  # timestamp-named, so lexicographic order == chronological
    )
    stale = backups[: max(0, len(backups) - retention_count)]
    for entry in stale:
        await provider.delete_file(folder, entry.name)


async def run_cloud_backup_now(db: AsyncSession) -> None:
    """Builds a backup, uploads it to the configured cloud folder,
    prunes old backups beyond the retention count, and always records
    last_run_at/last_run_status/last_run_error -- even on failure.

    Deliberately does NOT check cfg.enabled -- that flag only gates
    whether the *automatic scheduler* triggers this (see is_backup_due,
    called by the polling loop before this function). The manual "back
    up to cloud now" button must work regardless of whether automatic
    scheduling is turned on; a bug once had this function silently
    no-op (and the HTTP handler then reported a false "success", since
    last_run_status was simply never touched) whenever the schedule
    happened to be off.

    Never raises: both the unattended scheduler loop and the manual
    "back up now" HTTP handler call this exact function, then re-read
    get_cloud_backup_settings(db) to learn what happened. One source
    of truth (ClubSettings), read back by whoever needs to react,
    rather than two error-reporting paths that could disagree."""
    cfg = await get_cloud_backup_settings(db)

    provider = await get_cloud_storage_provider(db)
    if provider is None:
        await _record_run(db, "error", "No cloud storage is set up under Admin -> Integrations.")
        return

    try:
        await provider.create_folder(cfg.folder)
        filename, content = await build_backup_zip()
        await provider.upload_file(cfg.folder, filename, content)
        await _sweep_retention(provider, cfg.folder, cfg.retention_count)
    except (BackupError, CloudStorageError) as e:
        await _record_run(db, "error", str(e)[:500])
        return
    finally:
        await provider.aclose()

    await _record_run(db, "success", None)
