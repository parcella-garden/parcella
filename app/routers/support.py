"""
Support router (web UI): a staff-facing view of HelpdeskConversationLink
rows (app/models.py), the local cross-reference to conversations in the
club's helpdesk, synced by app/helpdesk/sync.py. Gated by the
freescout_bridge module flag (the key predates ADR 0107 and stays, since
permissions and nav order hang off it) AND Group-based permission
(read/write) -- ADMIN/BOARD bypass as always.

The transcript is fetched live from the helpdesk on every detail-page
load (never stored locally). Every feature checks the active helpdesk's
capabilities first: osTicket, for one, can't list or show conversations
through its API, and the pages say so instead of failing.

The old /freescout/... addresses redirect here.
"""
from typing import Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth import require_admin
from app.database import active_member_filter, current_tenant_filter, get_db
from app.helpdesk import (
    HELPDESK, HIDDEN_STATUSES, INBOX, READ, REPLY, HelpdeskError, get_active_helpdesk_type,
    get_helpdesk,
)
from app.i18n import t_for
from app.member_matching import find_members_by_email
from app.models import HelpdeskConversationLink, Member, MemberParcel, Parcel, TaskList
from app.module_flags import require_module
from app.permissions import require_permission
from app.task_board import create_task
from app.templating import templates

router = APIRouter(
    prefix="/support",
    tags=["support"],
    dependencies=[Depends(require_module("freescout_bridge"))],
)

legacy_router = APIRouter(prefix="/freescout", include_in_schema=False)


@legacy_router.get("/")
@legacy_router.get("/{link_id}")
async def legacy_redirect(link_id: Optional[str] = None):
    """Bookmarks from before ADR 0107."""
    return RedirectResponse(f"/support/{link_id}" if link_id else "/support/", status_code=301)


async def _helpdesk_context(db: AsyncSession) -> dict:
    """The active helpdesk's name, capabilities and web address, for
    templates -- without building a client."""
    provider_type = await get_active_helpdesk_type(db)
    cls = HELPDESK.get_class(provider_type)
    web_url = None
    if cls is not None:
        config = await HELPDESK.load_config(db, provider_type) or {}
        web_url = (config.get(cls.web_url_field) or "").rstrip("/") or None
    return {
        "helpdesk_type": provider_type,
        "helpdesk_name": cls.label if cls else "",
        "capabilities": cls.capabilities if cls else frozenset(),
        "base_url": web_url,
    }


async def _get_link_or_404(db: AsyncSession, link_id: str, request: Request) -> HelpdeskConversationLink:
    result = await db.execute(
        select(HelpdeskConversationLink)
        .options(selectinload(HelpdeskConversationLink.member), selectinload(HelpdeskConversationLink.parcel))
        .where(HelpdeskConversationLink.id == link_id)
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
    helpdesk = await _helpdesk_context(db)

    conversations = []
    if INBOX in helpdesk["capabilities"]:
        result = await db.execute(
            select(HelpdeskConversationLink)
            .options(selectinload(HelpdeskConversationLink.member))
            .where(
                HelpdeskConversationLink.provider == helpdesk["helpdesk_type"],
                HelpdeskConversationLink.status.notin_(HIDDEN_STATUSES),
            )
            .order_by(HelpdeskConversationLink.external_updated_at.desc())
        )
        conversations = result.scalars().all()

    return templates.TemplateResponse("support/list.html", {
        "request": request, "user": user, "conversations": conversations, **helpdesk,
    })


@router.get("/{link_id}", response_class=HTMLResponse)
async def conversation_detail(link_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_permission(request, db, "freescout_bridge", "read")
    link = await _get_link_or_404(db, link_id, request)
    helpdesk = await _helpdesk_context(db)

    messages = []
    fetch_error = None
    provider = await get_helpdesk(db) if link.provider == helpdesk["helpdesk_type"] else None
    conversation_url = provider.conversation_url(link.external_id) if provider else None
    if provider is None:
        fetch_error = t_for(request, "freescout.detail.not_configured")
    elif not provider.can(READ):
        fetch_error = t_for(request, "freescout.detail.no_read", name=provider.label)
    else:
        try:
            messages = await provider.get_messages(link.external_id)
        except HelpdeskError as e:
            fetch_error = str(e)
        finally:
            await provider.aclose()

    candidate_members = []
    if link.member_id is None and link.customer_email:
        candidate_members = await find_members_by_email(db, link.customer_email)

    member_parcels = await _current_parcels(db, link.member_id) if link.member_id else []

    return templates.TemplateResponse("support/detail.html", {
        "request": request, "user": user, "link": link, "messages": messages, "fetch_error": fetch_error,
        "candidate_members": candidate_members, "all_members": await _all_members(db),
        "member_parcels": member_parcels, "lists": await _all_lists(db),
        "conversation_url": conversation_url, **helpdesk,
    })


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
    return RedirectResponse(f"/support/{link_id}", status_code=302)


@router.post("/{link_id}/parcel")
async def set_parcel(
    link_id: str, request: Request, parcel_id: str = Form(""), db: AsyncSession = Depends(get_db),
):
    await require_permission(request, db, "freescout_bridge", "write")
    link = await _get_link_or_404(db, link_id, request)
    link.parcel_id = parcel_id.strip() or None
    await db.commit()
    return RedirectResponse(f"/support/{link_id}", status_code=302)


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

    cls = HELPDESK.get_class(link.provider)
    description_parts = [t_for(
        request, "freescout.task.source_line",
        name=cls.label if cls else link.provider, conversation_id=link.external_id,
    )]
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
    return RedirectResponse(f"/support/{link_id}", status_code=302)


@router.post("/{link_id}/task/link")
async def link_existing_task(
    link_id: str, request: Request, task_id: str = Form(""), db: AsyncSession = Depends(get_db),
):
    await require_admin(request, db)
    link = await _get_link_or_404(db, link_id, request)
    link.task_id = task_id.strip() or None
    await db.commit()
    return RedirectResponse(f"/support/{link_id}", status_code=302)


@router.post("/{link_id}/reply")
async def reply_to_customer(
    link_id: str, request: Request, text: str = Form(...), db: AsyncSession = Depends(get_db),
):
    """Posts a customer-facing reply through the helpdesk. Entirely
    separate from Parcella's internal task comments (TaskComment) --
    there is no shared 'notes' widget, so an internal remark can never
    be sent to the customer by accident."""
    await require_permission(request, db, "freescout_bridge", "write")
    link = await _get_link_or_404(db, link_id, request)

    provider = await get_helpdesk(db)
    if provider is None or provider.type != link.provider:
        raise HTTPException(status_code=400, detail=t_for(request, "freescout.detail.not_configured"))
    if not provider.can(REPLY):
        await provider.aclose()
        raise HTTPException(status_code=400, detail=t_for(request, "freescout.detail.no_reply", name=provider.label))

    try:
        await provider.reply(link.external_id, text.strip())
    except HelpdeskError as e:
        raise HTTPException(status_code=502, detail=str(e))
    finally:
        await provider.aclose()

    return RedirectResponse(f"/support/{link_id}", status_code=302)
