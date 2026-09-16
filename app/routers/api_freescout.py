"""
FreeScout conversation bridge router (REST API). See app/routers/freescout.py
for the equivalent web UI and the shared background/reasoning; both talk
to app.models.FreescoutConversationLink and app.freescout_client.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db, current_tenant_filter
from app.models import FreescoutConversationLink, MemberParcel, TaskList, User
from app.api_auth import require_api_permission, require_admin_api
from app.module_flags import require_module
from app.freescout_client import FreeScoutError, get_freescout_client
from app.freescout_sync import HIDDEN_STATUSES
from app.task_board import create_task
from app.schemas import (
    FreescoutConversationLinkOut, FreescoutConversationLinkMemberUpdate,
    FreescoutConversationLinkParcelUpdate, FreescoutAddToTaskBoardRequest, FreescoutReplyCreate,
)

router = APIRouter(
    prefix="/api/v1/freescout",
    tags=["freescout"],
    dependencies=[Depends(require_module("freescout_bridge"))],
)


async def _get_link_or_404(db: AsyncSession, link_id: str) -> FreescoutConversationLink:
    link = await db.get(FreescoutConversationLink, link_id)
    if not link:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return link


async def _single_current_parcel_id(db: AsyncSession, member_id: str):
    result = await db.execute(
        select(MemberParcel.parcel_id).where(MemberParcel.member_id == member_id, current_tenant_filter())
    )
    parcel_ids = result.scalars().all()
    return parcel_ids[0] if len(parcel_ids) == 1 else None


@router.get("/conversations", response_model=list[FreescoutConversationLinkOut])
async def list_conversations(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission("freescout_bridge", "read")),
):
    result = await db.execute(
        select(FreescoutConversationLink)
        .where(FreescoutConversationLink.freescout_status.notin_(HIDDEN_STATUSES))
        .order_by(FreescoutConversationLink.freescout_updated_at.desc())
    )
    return result.scalars().all()


@router.get("/conversations/{link_id}", response_model=FreescoutConversationLinkOut)
async def get_conversation(
    link_id: str, db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission("freescout_bridge", "read")),
):
    return await _get_link_or_404(db, link_id)


@router.put("/conversations/{link_id}/member", response_model=FreescoutConversationLinkOut)
async def set_member(
    link_id: str, data: FreescoutConversationLinkMemberUpdate, db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission("freescout_bridge", "write")),
):
    link = await _get_link_or_404(db, link_id)
    link.member_id = data.member_id
    link.parcel_id = await _single_current_parcel_id(db, data.member_id) if data.member_id else None
    await db.commit()
    await db.refresh(link)
    return link


@router.put("/conversations/{link_id}/parcel", response_model=FreescoutConversationLinkOut)
async def set_parcel(
    link_id: str, data: FreescoutConversationLinkParcelUpdate, db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission("freescout_bridge", "write")),
):
    link = await _get_link_or_404(db, link_id)
    link.parcel_id = data.parcel_id
    await db.commit()
    await db.refresh(link)
    return link


@router.post("/conversations/{link_id}/task", response_model=FreescoutConversationLinkOut)
async def add_to_task_board(
    link_id: str, data: FreescoutAddToTaskBoardRequest, db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin_api),
):
    """Creates a new task (pre-filled from the conversation) or links to
    an existing one -- admin/board only, matching the task board's own
    gating, not the finer freescout_bridge permission."""
    link = await _get_link_or_404(db, link_id)

    if data.task_id:
        link.task_id = data.task_id
    else:
        target_list_id = data.list_id
        if not target_list_id:
            result = await db.execute(select(TaskList).order_by(TaskList.position).limit(1))
            first_list = result.scalar_one_or_none()
            if first_list is None:
                raise HTTPException(status_code=400, detail="No lists exist on the board yet")
            target_list_id = first_list.id
        task = await create_task(
            db, title=link.subject, description=f"Source: FreeScout conversation #{link.freescout_conversation_id}",
            due_date=None, priority=None, tags=[], list_id=target_list_id,
            assigned_to_ids=[], created_by_id=user.id,
        )
        link.task_id = task.id

    await db.commit()
    await db.refresh(link)
    return link


@router.post("/conversations/{link_id}/reply", status_code=status.HTTP_204_NO_CONTENT)
async def reply_to_customer(
    link_id: str, data: FreescoutReplyCreate, db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission("freescout_bridge", "write")),
):
    link = await _get_link_or_404(db, link_id)
    client = await get_freescout_client(db)
    if client is None:
        raise HTTPException(status_code=400, detail="FreeScout is not configured")
    try:
        await client.create_thread(link.freescout_conversation_id, data.text, by_user_id=user.id)
    except FreeScoutError as e:
        raise HTTPException(status_code=502, detail=str(e))
