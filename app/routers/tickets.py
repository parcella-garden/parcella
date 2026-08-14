"""
Ticket system router (web UI): overview, create, detail, assign,
status changes, messages/notes.

Stage 1: manual ticket management, no email fetching yet (that comes
in stage 2). Assignment notification by email already works, since the
general SMTP infrastructure (app/email_service.py) is reused.

Business logic shared with app/routers/api_tickets.py lives in
app/services/tickets.py (ADR 0070) -- this router owns authentication,
the fine-grained permission check, Form(...) parsing, and rendering
(templates/redirects/flash messages).
"""
from datetime import date
from typing import Optional

from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import (
    Ticket, TicketMessage, TicketAttachment, TicketStatus, MessageDirection, User,
    AttachmentStorageBackend,
)
from app.permissions import require_permission
from app.module_flags import require_module, MODULE_DEFAULTS
from app.services.errors import ServiceError
from app.services.tickets import (
    filtered_tickets_query, create_ticket, change_status, bulk_change_status,
    assign_ticket, bulk_assign_tickets, set_member, set_spam_status,
    bulk_set_spam_status, add_message,
)
from app.ticket_utils import find_members_by_email
from app.ticket_mailer import process_incoming_mails, get_ticket_attachments_folder, sanitize_attachment_filename
from app.ticket_attachment_storage import read_local
from app.spam_filter import check_for_spam
from app.avatars import avatar_url
from app.cloud_storage import get_nextcloud_provider, CloudStorageError
from app.i18n import t_for, DEFAULT_LANGUAGE

router = APIRouter(
    prefix="/tickets",
    tags=["tickets"],
    dependencies=[Depends(require_module("tickets"))],
)
from app.templating import templates


def _lang(request: Request) -> str:
    return getattr(request.state, "language", DEFAULT_LANGUAGE)


def _service_error_to_http(request: Request, e: ServiceError) -> HTTPException:
    return HTTPException(status_code=e.http_status, detail=t_for(request, e.key, **e.params))


async def _load_ticket_with_details(db: AsyncSession, ticket_id: str) -> Optional[Ticket]:
    result = await db.execute(
        select(Ticket)
        .options(
            selectinload(Ticket.assigned_to),
            selectinload(Ticket.member),
            selectinload(Ticket.messages).selectinload(TicketMessage.authored_by),
            selectinload(Ticket.messages).selectinload(TicketMessage.attachments),
        )
        .where(Ticket.id == ticket_id)
    )
    return result.scalar_one_or_none()


async def _reactivate_due_tickets(db: AsyncSession) -> int:
    """
    Actually resets postponed tickets whose postponed_until has been
    reached back to ACTIVE/ASSIGNED (not just computed on the fly via
    is_due) -- not a background job, but executed lazily on the next
    load of the ticket list, since there's no scheduler infrastructure.
    Returns the number of reactivated tickets.
    """
    result = await db.execute(
        select(Ticket).where(
            Ticket.status == TicketStatus.POSTPONED,
            Ticket.postponed_until <= date.today(),
        )
    )
    due_tickets = result.scalars().all()
    for ticket in due_tickets:
        ticket.status = TicketStatus.ASSIGNED if ticket.assigned_to_id else TicketStatus.ACTIVE
        ticket.postponed_until = None
    if due_tickets:
        await db.commit()
    return len(due_tickets)


# ---------------------------------------------------------------------------
# Overview
# ---------------------------------------------------------------------------

TICKETS_PAGE_SIZE = 50


@router.get("/", response_class=HTMLResponse)
async def tickets_overview(
    request: Request,
    filter: str = "active",  # active | mine | waiting | postponed | closed | spam | all
    search: str = "",
    db: AsyncSession = Depends(get_db),
):
    user = await require_permission(request, db, "tickets", "read")

    reactivated_count = await _reactivate_due_tickets(db)

    query = filtered_tickets_query(filter, search, user.id).limit(TICKETS_PAGE_SIZE)
    result = await db.execute(query)
    tickets = result.scalars().all()

    postponed_count_result = await db.execute(
        select(Ticket).where(Ticket.status == TicketStatus.POSTPONED)
    )
    postponed_count = len(postponed_count_result.scalars().all())

    waiting_count_result = await db.execute(
        select(Ticket).where(Ticket.status == TicketStatus.WAITING)
    )
    waiting_count = len(waiting_count_result.scalars().all())

    spam_count_result = await db.execute(
        select(Ticket).where(Ticket.spam_suspected == True, Ticket.status != TicketStatus.DELETED)
    )
    spam_count = len(spam_count_result.scalars().all())

    # For the "assign" selector in bulk editing
    users_result = await db.execute(select(User).where(User.is_active == True).order_by(User.name))
    all_active_users = users_result.scalars().all()

    return templates.TemplateResponse("tickets/overview.html", {
        "request": request, "user": user,
        "tickets": tickets, "filter": filter, "search": search,
        "reactivated_count": reactivated_count,
        "postponed_count": postponed_count, "waiting_count": waiting_count,
        "spam_count": spam_count, "all_active_users": all_active_users,
        "TicketStatus": TicketStatus,
        "page_size": TICKETS_PAGE_SIZE,
        "has_more": len(tickets) == TICKETS_PAGE_SIZE,
    })


@router.get("/list.json")
async def tickets_list_json(
    request: Request,
    filter: str = "active",
    search: str = "",
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """Fetched by the ticket overview's infinite scroll for every page
    after the first (which the HTML route above already renders)."""
    user = await require_permission(request, db, "tickets", "read")

    query = filtered_tickets_query(filter, search, user.id).limit(TICKETS_PAGE_SIZE).offset(offset)
    result = await db.execute(query)
    tickets = result.scalars().all()

    return {
        "rows": [
            {
                "id": t.id,
                "subject": t.subject,
                "spam_suspected": t.spam_suspected,
                "member_name": t.member.full_name if t.member else None,
                "sender": t.sender_name or t.sender_email,
                "status": t.status.value,
                "assigned_to_name": t.assigned_to.name if t.assigned_to else None,
                "assigned_to_avatar_url": (
                    avatar_url(t.assigned_to.avatar_filename) if t.assigned_to else None
                ),
                "created_at": t.created_at.strftime("%d.%m.%Y %H:%M"),
            }
            for t in tickets
        ],
        "has_more": len(tickets) == TICKETS_PAGE_SIZE,
    }



# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------

@router.get("/new", response_class=HTMLResponse)
async def ticket_new_page(request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_permission(request, db, "tickets", "read")
    return templates.TemplateResponse("tickets/form.html", {"request": request, "user": user})


@router.post("/new")
async def ticket_create(
    request: Request,
    subject: str = Form(...),
    sender_email: str = Form(...),
    sender_name: str = Form(""),
    message: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    await require_permission(request, db, "tickets", "write")

    ticket = await create_ticket(
        db, subject=subject, sender_email=sender_email, sender_name=sender_name, message=message,
    )
    await db.commit()

    return RedirectResponse(f"/tickets/{ticket.id}", status_code=302)


# ---------------------------------------------------------------------------
# Bulk editing (multi-select in the overview)
# ---------------------------------------------------------------------------
# IMPORTANT: these must be registered before the generic
# "/{ticket_id}/..." routes, otherwise e.g. POST /bulk/status would be
# caught by "/{ticket_id}/status" with ticket_id="bulk".

@router.post("/bulk/status")
async def tickets_bulk_status(
    request: Request,
    ticket_ids: list[str] = Form(...),
    new_status_value: str = Form(...),
    postponed_until: str = Form(""),
    filter: str = Form("active"),
    db: AsyncSession = Depends(get_db),
):
    current_user = await require_permission(request, db, "tickets", "write")

    new_status = TicketStatus(new_status_value)
    parsed_postponed_until = date.fromisoformat(postponed_until) if postponed_until.strip() else None
    result = await db.execute(select(Ticket).where(Ticket.id.in_(ticket_ids)))
    tickets = result.scalars().all()

    try:
        await bulk_change_status(db, tickets, new_status, parsed_postponed_until, acting_user=current_user)
    except ServiceError as e:
        raise _service_error_to_http(request, e)

    await db.commit()
    return RedirectResponse(f"/tickets/?filter={filter}", status_code=302)


@router.post("/bulk/assign")
async def tickets_bulk_assign(
    request: Request,
    ticket_ids: list[str] = Form(...),
    user_id: str = Form(""),
    filter: str = Form("active"),
    db: AsyncSession = Depends(get_db),
):
    current_user = await require_permission(request, db, "tickets", "write")

    assignee = None
    if user_id.strip():
        result = await db.execute(select(User).where(User.id == user_id))
        assignee = result.scalar_one_or_none()
        if not assignee:
            raise HTTPException(status_code=404, detail=t_for(request, "errors.user_not_found"))

    result = await db.execute(select(Ticket).where(Ticket.id.in_(ticket_ids)))
    tickets = result.scalars().all()

    await bulk_assign_tickets(db, tickets, assignee, acting_user=current_user, lang=_lang(request))
    await db.commit()

    return RedirectResponse(f"/tickets/?filter={filter}", status_code=302)


@router.post("/bulk/mark-spam")
async def tickets_bulk_mark_spam(
    request: Request,
    ticket_ids: list[str] = Form(...),
    filter: str = Form("active"),
    db: AsyncSession = Depends(get_db),
):
    current_user = await require_permission(request, db, "tickets", "write")
    result = await db.execute(select(Ticket).where(Ticket.id.in_(ticket_ids)))
    bulk_set_spam_status(result.scalars().all(), True, acting_user=current_user)
    await db.commit()
    return RedirectResponse(f"/tickets/?filter={filter}", status_code=302)


@router.post("/bulk/not-spam")
async def tickets_bulk_not_spam(
    request: Request,
    ticket_ids: list[str] = Form(...),
    filter: str = Form("active"),
    db: AsyncSession = Depends(get_db),
):
    current_user = await require_permission(request, db, "tickets", "write")
    result = await db.execute(select(Ticket).where(Ticket.id.in_(ticket_ids)))
    bulk_set_spam_status(result.scalars().all(), False, acting_user=current_user)
    await db.commit()
    return RedirectResponse(f"/tickets/?filter={filter}", status_code=302)


# ---------------------------------------------------------------------------
# Detail
# ---------------------------------------------------------------------------

@router.get("/{ticket_id}", response_class=HTMLResponse)
async def ticket_detail(
    ticket_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user = await require_permission(request, db, "tickets", "read")
    await _reactivate_due_tickets(db)
    ticket = await _load_ticket_with_details(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail=t_for(request, "errors.ticket_not_found"))

    # Possible member candidates (if the sender address belongs to
    # multiple members, or isn't assigned to one yet)
    candidates = await find_members_by_email(db, ticket.sender_email)

    user_result = await db.execute(select(User).where(User.is_active == True).order_by(User.name))
    all_users = user_result.scalars().all()

    return templates.TemplateResponse("tickets/detail.html", {
        "request": request, "user": user, "ticket": ticket,
        "candidates": candidates, "all_users": all_users,
        "TicketStatus": TicketStatus, "MessageDirection": MessageDirection,
        "today": date.today().isoformat(),
    })


@router.get("/{ticket_id}/attachments/{attachment_id}")
async def ticket_attachment_download(
    ticket_id: str, attachment_id: str, request: Request, db: AsyncSession = Depends(get_db),
):
    await require_permission(request, db, "tickets", "read")

    result = await db.execute(
        select(TicketAttachment).join(TicketMessage)
        .where(TicketAttachment.id == attachment_id, TicketMessage.ticket_id == ticket_id)
    )
    attachment = result.scalar_one_or_none()
    if not attachment:
        raise HTTPException(status_code=404)

    if attachment.storage_backend == AttachmentStorageBackend.LOCAL:
        try:
            content = read_local(attachment.local_filename)
        except OSError:
            raise HTTPException(status_code=404)
    else:
        flags = getattr(request.state, "module_flags", {})
        if not flags.get("cloud_storage", MODULE_DEFAULTS.get("cloud_storage", True)):
            raise HTTPException(status_code=404)

        folder_path = await get_ticket_attachments_folder(db)
        provider = await get_nextcloud_provider(db) if folder_path else None
        if not folder_path or provider is None:
            raise HTTPException(status_code=400, detail=t_for(request, "tickets.attachments.cloud_not_configured"))

        try:
            content = await provider.download_file(folder_path, attachment.cloud_filename)
        except CloudStorageError as e:
            raise HTTPException(status_code=502, detail=str(e))
        finally:
            await provider.aclose()

    return Response(
        content=content, media_type=attachment.content_type or "application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{sanitize_attachment_filename(attachment.original_filename)}"'},
    )


# ---------------------------------------------------------------------------
# Assign
# ---------------------------------------------------------------------------

@router.post("/{ticket_id}/assign")
async def ticket_assign(
    ticket_id: str,
    request: Request,
    user_id: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    current_user = await require_permission(request, db, "tickets", "write")
    ticket = await _load_ticket_with_details(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404)

    assignee = None
    if user_id.strip():
        result = await db.execute(select(User).where(User.id == user_id))
        assignee = result.scalar_one_or_none()
        if not assignee:
            raise HTTPException(status_code=404, detail=t_for(request, "errors.user_not_found"))

    await assign_ticket(db, ticket, assignee, acting_user=current_user, lang=_lang(request))
    await db.commit()

    return RedirectResponse(f"/tickets/{ticket_id}", status_code=302)


# ---------------------------------------------------------------------------
# Change status
# ---------------------------------------------------------------------------

@router.post("/{ticket_id}/status")
async def ticket_status_update(
    ticket_id: str,
    request: Request,
    new_status_value: str = Form(...),
    postponed_until: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    current_user = await require_permission(request, db, "tickets", "write")
    ticket = await _load_ticket_with_details(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404)

    parsed_postponed_until = date.fromisoformat(postponed_until) if postponed_until.strip() else None

    try:
        await change_status(db, ticket, TicketStatus(new_status_value), parsed_postponed_until, acting_user=current_user)
    except ServiceError as e:
        raise _service_error_to_http(request, e)

    await db.commit()
    return RedirectResponse(f"/tickets/{ticket_id}", status_code=302)


# ---------------------------------------------------------------------------
# Manually assign a member
# ---------------------------------------------------------------------------

@router.post("/{ticket_id}/member")
async def ticket_member_assign(
    ticket_id: str,
    request: Request,
    member_id: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    await require_permission(request, db, "tickets", "write")
    result = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
    ticket = result.scalar_one_or_none()
    if not ticket:
        raise HTTPException(status_code=404)

    set_member(ticket, member_id)
    await db.commit()
    return RedirectResponse(f"/tickets/{ticket_id}", status_code=302)


# ---------------------------------------------------------------------------
# Spam suspicion: mark manually, or clear a false positive
# ---------------------------------------------------------------------------

@router.post("/{ticket_id}/mark-spam")
async def ticket_mark_spam(
    ticket_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Lets staff flag a ticket the automated check (heuristics + the
    optional external API, app/spam_filter.py) missed -- the filter
    only ever runs once, on arrival, so anything it doesn't catch stays
    unflagged forever without a manual escape hatch."""
    current_user = await require_permission(request, db, "tickets", "write")
    result = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
    ticket = result.scalar_one_or_none()
    if not ticket:
        raise HTTPException(status_code=404)

    set_spam_status(ticket, True, acting_user=current_user)
    await db.commit()
    return RedirectResponse(f"/tickets/{ticket_id}", status_code=302)


@router.post("/{ticket_id}/not-spam")
async def ticket_mark_not_spam(
    ticket_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    current_user = await require_permission(request, db, "tickets", "write")
    result = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
    ticket = result.scalar_one_or_none()
    if not ticket:
        raise HTTPException(status_code=404)

    set_spam_status(ticket, False, acting_user=current_user)
    await db.commit()
    return RedirectResponse(f"/tickets/{ticket_id}", status_code=302)


# ---------------------------------------------------------------------------
# Add message / internal note
# ---------------------------------------------------------------------------

@router.post("/{ticket_id}/message")
async def message_add(
    ticket_id: str,
    request: Request,
    content: str = Form(...),
    direction: str = Form("OUTGOING"),
    db: AsyncSession = Depends(get_db),
):
    user = await require_permission(request, db, "tickets", "write")
    ticket = await _load_ticket_with_details(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404)

    await add_message(db, ticket, content, MessageDirection(direction), acting_user=user)
    await db.commit()

    return RedirectResponse(f"/tickets/{ticket_id}", status_code=302)


# ---------------------------------------------------------------------------
# Ticket mailbox: manual fetch (in addition to background polling)
# ---------------------------------------------------------------------------

@router.post("/inbox/fetch-now")
async def inbox_fetch_now(request: Request, db: AsyncSession = Depends(get_db)):
    await require_permission(request, db, "tickets", "write")
    count = await process_incoming_mails(db)
    import urllib.parse
    message = urllib.parse.quote(f"{count} neue E-Mail(s) verarbeitet.")
    return RedirectResponse(f"/tickets/?message={message}", status_code=302)


# ---------------------------------------------------------------------------
# Backlog re-scan: the spam check (app/spam_filter.py) only ever runs
# once, on arrival of a new incoming mail -- this is the catch-up pass
# for tickets that predate the filter being configured, or a
# configuration change since (e.g. an external API added later).
# ---------------------------------------------------------------------------

RESCAN_SPAM_BATCH_LIMIT = 200


@router.post("/rescan-spam")
async def tickets_rescan_spam(request: Request, db: AsyncSession = Depends(get_db)):
    await require_permission(request, db, "tickets", "write")

    result = await db.execute(
        select(Ticket)
        .options(selectinload(Ticket.messages))
        .where(
            Ticket.spam_suspected == False,
            # Never touches a ticket a human already made a call on --
            # only tickets the automated check has effectively never
            # seen a verdict stick for.
            Ticket.spam_reviewed_by_id.is_(None),
            Ticket.status.not_in([TicketStatus.CLOSED, TicketStatus.DELETED]),
        )
        .order_by(Ticket.created_at)
        .limit(RESCAN_SPAM_BATCH_LIMIT)
    )
    tickets = result.scalars().all()

    flagged = 0
    for ticket in tickets:
        content = next(
            (m.content for m in ticket.messages if m.direction == MessageDirection.INCOMING), "",
        )
        spam_result = await check_for_spam(ticket.sender_email, ticket.subject, content, db)
        if spam_result.is_spam_suspected:
            ticket.spam_suspected = True
            ticket.spam_score = spam_result.score
            ticket.spam_reasoning = spam_result.reasoning
            flagged += 1
    await db.commit()

    import urllib.parse
    message_key = (
        "tickets.overview.rescan_result_message_more"
        if len(tickets) == RESCAN_SPAM_BATCH_LIMIT
        else "tickets.overview.rescan_result_message"
    )
    message = urllib.parse.quote(t_for(request, message_key, scanned=len(tickets), flagged=flagged))
    return RedirectResponse(f"/tickets/?message={message}", status_code=302)
