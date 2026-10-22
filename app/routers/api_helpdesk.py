"""
Support / helpdesk REST API (ADR 0107). See app/routers/support.py for
the web UI and the shared reasoning; both work on
app.models.HelpdeskConversationLink and the active helpdesk
(app/helpdesk/).

- /api/v1/helpdesk/conversations...: the current endpoints.
- /api/v1/freescout/conversations...: the same endpoints with the
  pre-ADR-0107 field names, kept (deprecated) so existing API clients
  keep working.
- /api/v1/helpdesk (GET/PUT), /providers, /test: which helpdesk is
  active, shared with the website and cloud storage settings APIs.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api_auth import require_admin_api, require_api_permission
from app.database import current_tenant_filter, get_db
from app.helpdesk import HELPDESK, HIDDEN_STATUSES, REPLY, HelpdeskError, get_active_helpdesk_type, get_helpdesk
from app.models import HelpdeskConversationLink, MemberParcel, TaskList, User
from app.module_flags import require_module
from app.routers.api_provider_settings import create_provider_settings_router
from app.schemas import (
    FreescoutAddToTaskBoardRequest, FreescoutConversationLinkMemberUpdate, FreescoutConversationLinkOut,
    FreescoutConversationLinkParcelUpdate, FreescoutReplyCreate, HelpdeskConversationLinkOut,
)
from app.task_board import create_task

settings_router = create_provider_settings_router(
    HELPDESK, prefix="/api/v1/helpdesk", tag="API: Helpdesk", types_path="providers", errors=(HelpdeskError,),
)


async def _get_link_or_404(db: AsyncSession, link_id: str) -> HelpdeskConversationLink:
    link = await db.get(HelpdeskConversationLink, link_id)
    if not link:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return link


async def _single_current_parcel_id(db: AsyncSession, member_id: str):
    result = await db.execute(
        select(MemberParcel.parcel_id).where(MemberParcel.member_id == member_id, current_tenant_filter())
    )
    parcel_ids = result.scalars().all()
    return parcel_ids[0] if len(parcel_ids) == 1 else None


def create_conversations_router(prefix: str, out_model, tag: str, deprecated: bool = False) -> APIRouter:
    router = APIRouter(
        prefix=prefix, tags=[tag], deprecated=deprecated,
        dependencies=[Depends(require_module("freescout_bridge"))],
    )

    @router.get("/conversations", response_model=list[out_model])
    async def list_conversations(
        db: AsyncSession = Depends(get_db),
        user: User = Depends(require_api_permission("freescout_bridge", "read")),
    ):
        """The active helpdesk's open conversations (none for a helpdesk
        that can't list them, like osTicket)."""
        provider_type = await get_active_helpdesk_type(db)
        result = await db.execute(
            select(HelpdeskConversationLink)
            .where(
                HelpdeskConversationLink.provider == provider_type,
                HelpdeskConversationLink.status.notin_(HIDDEN_STATUSES),
            )
            .order_by(HelpdeskConversationLink.external_updated_at.desc())
        )
        return result.scalars().all()

    @router.get("/conversations/{link_id}", response_model=out_model)
    async def get_conversation(
        link_id: str, db: AsyncSession = Depends(get_db),
        user: User = Depends(require_api_permission("freescout_bridge", "read")),
    ):
        return await _get_link_or_404(db, link_id)

    @router.put("/conversations/{link_id}/member", response_model=out_model)
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

    @router.put("/conversations/{link_id}/parcel", response_model=out_model)
    async def set_parcel(
        link_id: str, data: FreescoutConversationLinkParcelUpdate, db: AsyncSession = Depends(get_db),
        user: User = Depends(require_api_permission("freescout_bridge", "write")),
    ):
        link = await _get_link_or_404(db, link_id)
        link.parcel_id = data.parcel_id
        await db.commit()
        await db.refresh(link)
        return link

    @router.post("/conversations/{link_id}/task", response_model=out_model)
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
            cls = HELPDESK.get_class(link.provider)
            task = await create_task(
                db, title=link.subject,
                description=f"Source: {cls.label if cls else link.provider} conversation #{link.external_id}",
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
        provider = await get_helpdesk(db)
        if provider is None or provider.type != link.provider:
            raise HTTPException(status_code=400, detail="This conversation's helpdesk is not set up")
        try:
            if not provider.can(REPLY):
                raise HTTPException(status_code=400, detail=f"{provider.label} can't send replies through its API")
            await provider.reply(link.external_id, data.text)
        except HelpdeskError as e:
            raise HTTPException(status_code=502, detail=str(e))
        finally:
            await provider.aclose()

    return router


router = create_conversations_router("/api/v1/helpdesk", HelpdeskConversationLinkOut, "API: Helpdesk")
legacy_router = create_conversations_router(
    "/api/v1/freescout", FreescoutConversationLinkOut, "API: FreeScout (deprecated)", deprecated=True,
)
