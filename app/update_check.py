"""
Update check: lets an admin know when a newer Parcella version has
been released, without requiring the admin to watch the GitHub repo
themselves.

Only checks GitHub releases (a metadata-only public API call, no
credentials needed) -- it does NOT verify that a pullable Docker image
actually exists for that release yet (release.yml's `test` job runs
before `publish`, but there's still a window between the tag existing
and the image landing on GHCR).

Result is cached in ClubSettings (update_check_latest_version,
update_check_checked_at) via refresh_update_check_cache(), run
periodically by a background loop (see app/main.py), so viewing the
admin dashboard never itself triggers an outbound call.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import ClubSetting

GITHUB_REPO = "parcella-garden/parcella"
LATEST_RELEASE_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"

KEY_ENABLED = "update_check_enabled"
KEY_LATEST_VERSION = "update_check_latest_version"
KEY_CHECKED_AT = "update_check_checked_at"


def _version_tuple(version: str) -> tuple:
    return tuple(int(part) for part in version.split("."))


def is_newer(latest: str, current: str) -> bool:
    """False (not "unknown, assume yes") for anything that doesn't parse as dotted integers."""
    try:
        return _version_tuple(latest) > _version_tuple(current)
    except (ValueError, AttributeError):
        return False


async def fetch_latest_release_version() -> Optional[str]:
    """
    Returns the latest GitHub release's tag (leading "v" stripped), or
    None if there is no release yet or the request failed -- both
    treated the same way by the caller (nothing to report).
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                LATEST_RELEASE_URL, headers={"Accept": "application/vnd.github+json"}
            )
    except httpx.HTTPError:
        return None

    if response.status_code != 200:
        return None

    tag = response.json().get("tag_name", "")
    return tag.lstrip("v") or None


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


async def is_enabled(db: AsyncSession) -> bool:
    value = await _get_setting(db, KEY_ENABLED)
    return (value or "true").strip().lower() in ("true", "1", "ja", "an")


async def refresh_update_check_cache(db: AsyncSession) -> None:
    """Queries GitHub and updates the cached result. Skipped entirely if disabled."""
    if not await is_enabled(db):
        return

    latest_version = await fetch_latest_release_version()
    await _set_setting(
        db, KEY_LATEST_VERSION, latest_version,
        "Latest Parcella version seen on GitHub releases (cache, see app/update_check.py)",
    )
    await _set_setting(
        db, KEY_CHECKED_AT, datetime.now(timezone.utc).isoformat(),
        "When the update check last ran (cache, see app/update_check.py)",
    )
    await db.commit()


@dataclass
class UpdateStatus:
    enabled: bool
    current_version: str
    latest_version: Optional[str]
    checked_at: Optional[datetime]
    update_available: bool


async def get_update_status(db: AsyncSession) -> UpdateStatus:
    enabled = await is_enabled(db)
    latest_version = await _get_setting(db, KEY_LATEST_VERSION)
    checked_at_raw = await _get_setting(db, KEY_CHECKED_AT)
    checked_at = datetime.fromisoformat(checked_at_raw) if checked_at_raw else None

    return UpdateStatus(
        enabled=enabled,
        current_version=settings.app_version,
        latest_version=latest_version,
        checked_at=checked_at,
        update_available=bool(latest_version) and is_newer(latest_version, settings.app_version),
    )
