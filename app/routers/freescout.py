"""
FreeScout conversation bridge router (web UI): a staff-facing view of
FreescoutConversationLink rows (app/models.py), the local cross-reference
to FreeScout conversations synced by app/freescout_sync.py. Gated by the
freescout_bridge module flag AND Group-based permission (read/write),
same model the removed ticket module used -- ADMIN/BOARD bypass as always.

The full message transcript is fetched live from FreeScout's API on
every detail-page load (never stored locally, see
docs/module-freescout-bridge.md) -- FreeScout remains the single
canonical store for actual conversation content.
"""
from typing import Optional

from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db, active_member_filter, current_tenant_filter
from app.models import FreescoutConversationLink, Member, MemberParcel, Parcel, Task, TaskList
from app.auth import require_admin, require_user
from app.permissions import require_permission
from app.i18n import t_for
from app.module_flags import require_module
from app.member_matching import find_members_by_email
from app.freescout_client import FreeScoutError, get_freescout_client
from app.freescout_sync import HIDDEN_STATUSES
from app.task_board import create_task, next_position

router = APIRouter(
    prefix="/freescout",
    tags=["freescout"],
    dependencies=[Depends(require_module("freescout_bridge"))],
)
from app.templating import templates


async def _get_link_or_404(db: AsyncSession, link_id: str, request: Request) -> FreescoutConversationLink:
    result = await db.execute(
        select(FreescoutConversationLink)
        .options(selectinload(FreescoutConversationLink.member), selectinload(FreescoutConversationLink.parcel))
        .where(FreescoutConversationLink.id == link_id)
    )
    link = result.scalar_one_or_none()
    if not link:
        raise HTTPException(status_code=404, detail=t_for(request, "freescout.errors.conversation_not_found"))
    return link


async def _all_members(db: AsyncSession):
    result = await db.execute(select(Member).where(active_member_filter()).order_by(Member.last_name, Member.first_name))
    return result.scalars().all()


async def _current_parcels(db: AsyncSession, member_id: str):
    result = await db.execute(
        select(Parcel).join(MemberParcel, MemberParcel.parcel_id == Parcel.id)
        .where(MemberParcel.member_id == member_id, current_tenant_filter())
    )
    return result.scalars().all()


async def _all_lists(db: AsyncSession):
    result = await db.execute(select(TaskList).order_by(TaskList.position))
    return result.scalars().all()


@router.get("/", response_class=HTMLResponse)
async def conversation_list(request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_permission(request, db, "freescout_bridge", "read")

    result = await db.execute(
        select(FreescoutConversationLink)
        .options(selectinload(FreescoutConversationLink.member))
        .where(FreescoutConversationLink.freescout_status.notin_(HIDDEN_STATUSES))
        .order_by(FreescoutConversationLink.freescout_updated_at.desc())
    )
    conversations = result.scalars().all()

    return templates.TemplateResponse("freescout/list.html", {
        "request": request, "user": user, "conversations": conversations, "base_url": await _base_url(db),
    })


@router.get("/{link_id}", response_class=HTMLResponse)
async def conversation_detail(link_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_permission(request, db, "freescout_bridge", "read")
    link = await _get_link_or_404(db, link_id, request)

    threads = []
    fetch_error = None
    client = await get_freescout_client(db)
    if client is None:
        fetch_error = t_for(request, "freescout.detail.not_configured")
    else:
        try:
            conversation = await client.get_conversation(link.freescout_conversation_id)
            threads = conversation.get("_embedded", {}).get("threads", [])
        except FreeScoutError as e:
            fetch_error = str(e)

    candidate_members = []
    if link.member_id is None and link.customer_email:
        candidate_members = await find_members_by_email(db, link.customer_email)

    member_parcels = await _current_parcels(db, link.member_id) if link.member_id else []

    return templates.TemplateResponse("freescout/detail.html", {
        "request": request, "user": user, "link": link, "threads": threads, "fetch_error": fetch_error,
        "candidate_members": candidate_members, "all_members": await _all_members(db),
        "member_parcels": member_parcels, "lists": await _all_lists(db),
        "base_url": await _base_url(db),
    })


async def _base_url(db: AsyncSession) -> Optional[str]:
    from app.freescout_client import load_freescout_base_url
    return await load_freescout_base_url(db)


@router.post("/{link_id}/member")
async def set_member(
    link_id: str, request: Request, member_id: str = Form(""), db: AsyncSession = Depends(get_db),
):
    await require_permission(request, db, "freescout_bridge", "write")
    link = await _get_link_or_404(db, link_id, request)

    link.member_id = member_id.strip() or None
    link.parcel_id = None
    if link.member_id:
        parcels = await _current_parcels(db, link.member_id)
        if len(parcels) == 1:
            link.parcel_id = parcels[0].id
    await db.commit()
    return RedirectResponse(f"/freescout/{link_id}", status_code=302)


@router.post("/{link_id}/parcel")
async def set_parcel(
    link_id: str, request: Request, parcel_id: str = Form(""), db: AsyncSession = Depends(get_db),
):
    await require_permission(request, db, "freescout_bridge", "write")
    link = await _get_link_or_404(db, link_id, request)
    link.parcel_id = parcel_id.strip() or None
    await db.commit()
    return RedirectResponse(f"/freescout/{link_id}", status_code=302)


@router.post("/{link_id}/task")
async def create_task_from_conversation(
    link_id: str, request: Request, list_id: str = Form(""), db: AsyncSession = Depends(get_db),
):
    """Creates a new task pre-filled from the conversation (title =
    subject, description references the member/parcel) and links it --
    admin/board only, matching the task board's own existing gating
    (require_admin), not the finer freescout_bridge Group permission,
    since creating/editing a task already requires that regardless of
    where the request originated."""
    user = await require_admin(request, db)
    link = await _get_link_or_404(db, link_id, request)

    lists = await _all_lists(db)
    if not lists:
        raise HTTPException(status_code=400, detail=t_for(request, "freescout.errors.no_lists"))
    target_list_id = list_id.strip() or lists[0].id

    description_parts = [t_for(request, "freescout.task.source_line", conversation_id=link.freescout_conversation_id)]
    if link.member_id:
        member = await db.get(Member, link.member_id)
        if member:
            description_parts.append(t_for(request, "freescout.task.member_line", name=member.full_name))

    task = await create_task(
        db, title=link.subject, description="\n".join(description_parts),
        due_date=None, priority=None, tags=[], list_id=target_list_id,
        assigned_to_ids=[], created_by_id=user.id,
    )
    link.task_id = task.id
    await db.commit()
    return RedirectResponse(f"/freescout/{link_id}", status_code=302)


@router.post("/{link_id}/task/link")
async def link_existing_task(
    link_id: str, request: Request, task_id: str = Form(""), db: AsyncSession = Depends(get_db),
):
    await require_admin(request, db)
    link = await _get_link_or_404(db, link_id, request)
    link.task_id = task_id.strip() or None
    await db.commit()
    return RedirectResponse(f"/freescout/{link_id}", status_code=302)


@router.post("/{link_id}/reply")
async def reply_to_customer(
    link_id: str, request: Request, text: str = Form(...), db: AsyncSession = Depends(get_db),
):
    """Posts a customer-facing reply through FreeScout's API. Entirely
    separate from Parcella's internal task comments (TaskComment) --
    there is no shared 'notes' widget, so an internal remark can never
    be sent to the customer by accident."""
    user = await require_permission(request, db, "freescout_bridge", "write")
    link = await _get_link_or_404(db, link_id, request)

    client = await get_freescout_client(db)
    if client is None:
        raise HTTPException(status_code=400, detail=t_for(request, "freescout.detail.not_configured"))

    try:
        await client.create_thread(link.freescout_conversation_id, text.strip(), by_user_id=user.id)
    except FreeScoutError as e:
        raise HTTPException(status_code=502, detail=str(e))

    return RedirectResponse(f"/freescout/{link_id}", status_code=302)
