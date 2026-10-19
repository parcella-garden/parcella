"""
API router: club settings (club master data, area sizes, etc.).

Secrets stored in ClubSetting (integration passwords and API keys,
encrypted; the ICS feed and public form tokens, plaintext) are never
served or written here: any API account could read this list, and a
leaked feed token exposes every member's birthday. Integrations are
configured on the admin pages only.
"""
import re
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import ClubSetting, ClubBoardMember, User
from app.api_auth import get_current_api_user, require_admin_api
from app.schemas import ClubSettingOut, ClubSettingUpdate, BoardMemberOut

router = APIRouter(prefix="/api/v1/club-settings", tags=["API: Club Settings"])

# Matches every credential key in use (smtp_password, nextcloud_app_password,
# freescout_api_key, spam_api_key, ics_secret_token, public_signup_api_token,
# ...) and any new one named the same way.
_SECRET_KEY_RE = re.compile(r"(password|token|secret|api_key)$")


def is_secret_setting(key: str) -> bool:
    return bool(_SECRET_KEY_RE.search(key.lower()))


@router.get(
    "",
    response_model=List[ClubSettingOut],
    summary="Retrieve all club settings",
    description="Returns club master data such as name, address, and A/B/C area sizes as a key-value list.",
)
async def settings_list(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_api_user),
):
    result = await db.execute(select(ClubSetting))
    return [entry for entry in result.scalars().all() if not is_secret_setting(entry.key)]


@router.get(
    "/board-members",
    response_model=List[BoardMemberOut],
    summary="Retrieve board members",
    description="Returns the members currently listed as board members on admin -> settings -> club settings (issue #111). Read/write of the list itself happens via that admin page, not this API.",
)
async def board_members_list(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_api_user),
):
    result = await db.execute(
        select(ClubBoardMember).options(selectinload(ClubBoardMember.member))
    )
    return result.scalars().all()


# NOTE: /board-members must stay registered above /{key} -- a dynamic
# single-segment path pattern registered first would otherwise shadow it
# (FastAPI matches routes in registration order).
@router.get(
    "/{key}",
    response_model=ClubSettingOut,
    summary="Retrieve a single setting",
)
async def setting_get(
    key: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_api_user),
):
    if is_secret_setting(key):
        raise HTTPException(status_code=404, detail="Setting not found")
    result = await db.execute(
        select(ClubSetting).where(ClubSetting.key == key)
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Setting not found")
    return entry


@router.put(
    "/{key}",
    response_model=ClubSettingOut,
    summary="Set or update a setting",
    description="Creates the key if it does not exist yet (upsert). Admin/board only.",
)
async def setting_set(
    key: str,
    daten: ClubSettingUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin_api),
):
    if is_secret_setting(key):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Credentials and tokens can only be set on the admin pages",
        )
    result = await db.execute(
        select(ClubSetting).where(ClubSetting.key == key)
    )
    entry = result.scalar_one_or_none()

    if entry:
        entry.value = daten.value
    else:
        entry = ClubSetting(key=key, value=daten.value)
        db.add(entry)

    await db.commit()
    await db.refresh(entry)
    return entry
