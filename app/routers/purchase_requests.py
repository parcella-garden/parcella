"""
Purchase Requests router (web UI): submit a request, approve, reject,
deep-link confirmation by external requesters.

Four-eyes principle: two different board members must agree before a
PurchaseRequest counts as approved. The requester themselves may not
give either of the two approvals.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import (
    PurchaseRequest, PurchaseRequestApproval, PurchaseRequestComment, PurchaseRequestStatus, User,
)
from app.auth import require_admin
from app.permissions import require_permission
from app.i18n import t_for, DEFAULT_LANGUAGE
from app.module_flags import require_module
from app.services.errors import ServiceError
from app.routers.external_contacts import picker_contacts, resolve_picked_contact
from app.services.purchase_requests import (
    MAX_COMMENT_LENGTH, REQUIRED_APPROVALS, create_purchase_request, send_confirmation_email,
    approve_purchase_request, reject_purchase_request, add_comment, notify_comment,
)

router = APIRouter(
    prefix="/purchase-requests",
    tags=["purchase-requests"],
    dependencies=[Depends(require_module("purchase_requests"))],
)
from app.templating import templates

# How long a requester has to confirm via the emailed deep link before it
# stops working. The token itself never expires cryptographically (it's
# just an itsdangerous signature, looked up verbatim in the DB), so this
# is enforced against PurchaseRequest.created_at instead.
_CONFIRMATION_TOKEN_MAX_AGE_DAYS = 30


def _confirmation_token_expired(pr: PurchaseRequest) -> bool:
    return datetime.now(timezone.utc) - pr.created_at > timedelta(days=_CONFIRMATION_TOKEN_MAX_AGE_DAYS)


async def _load_with_details(db: AsyncSession, request_id: str) -> Optional[PurchaseRequest]:
    result = await db.execute(
        select(PurchaseRequest)
        .options(
            selectinload(PurchaseRequest.requested_by),
            selectinload(PurchaseRequest.created_by),
            selectinload(PurchaseRequest.rejected_by),
            selectinload(PurchaseRequest.approvals).selectinload(PurchaseRequestApproval.user),
            selectinload(PurchaseRequest.external_contact),
            selectinload(PurchaseRequest.comments).selectinload(PurchaseRequestComment.created_by),
        )
        .where(PurchaseRequest.id == request_id)
    )
    return result.scalar_one_or_none()


# ---------------------------------------------------------------------------
# Overview
# ---------------------------------------------------------------------------

@router.get("/", response_class=HTMLResponse)
async def purchase_requests_overview(
    request: Request,
    filter: str = "open",
    db: AsyncSession = Depends(get_db),
):
    user = await require_permission(request, db, "purchase_requests", "read")

    query = (
        select(PurchaseRequest)
        .options(
            selectinload(PurchaseRequest.requested_by),
            selectinload(PurchaseRequest.approvals),
        )
        .order_by(PurchaseRequest.created_at.desc())
    )

    if filter == "open":
        query = query.where(PurchaseRequest.status == PurchaseRequestStatus.OPEN)
    elif filter == "approved":
        query = query.where(PurchaseRequest.status == PurchaseRequestStatus.APPROVED)
    elif filter == "rejected":
        query = query.where(PurchaseRequest.status == PurchaseRequestStatus.REJECTED)
    # "all": no filter

    result = await db.execute(query)
    purchase_requests = result.scalars().all()

    return templates.TemplateResponse("purchase_requests/overview.html", {
        "request": request, "user": user,
        "purchase_requests": purchase_requests, "filter": filter,
        "required_approvals": REQUIRED_APPROVALS,
    })


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------

@router.get("/new", response_class=HTMLResponse)
async def purchase_request_new_page(request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_permission(request, db, "purchase_requests", "write")
    return templates.TemplateResponse("purchase_requests/form.html", {
        "request": request, "user": user, "contacts": await picker_contacts(request, db),
    })


@router.post("/new")
async def purchase_request_create(
    request: Request,
    title: str = Form(...),
    justification: str = Form(...),
    link: str = Form(""),
    estimated_cost_eur: str = Form(""),
    for_other_person: bool = Form(False),
    requester_name: str = Form(""),
    requester_email: str = Form(""),
    external_contact_id: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    user = await require_permission(request, db, "purchase_requests", "write")
    contact_id = await resolve_picked_contact(request, db, external_contact_id)

    estimated_cost = None
    if estimated_cost_eur.strip():
        try:
            estimated_cost = float(estimated_cost_eur.replace(",", "."))
        except ValueError:
            pass

    purchase_request = await create_purchase_request(
        db,
        title=title, justification=justification, link=link, estimated_cost_eur=estimated_cost,
        created_by_id=user.id,
        requester_name=(requester_name if for_other_person else None),
        requester_email=(requester_email if for_other_person and requester_email.strip() else None),
        external_contact_id=contact_id,
    )

    if purchase_request.confirmation_token:
        base_url = str(request.base_url).rstrip("/")
        confirmation_link = f"{base_url}/purchase-requests/confirm/{purchase_request.confirmation_token}"
        lang = getattr(request.state, "language", DEFAULT_LANGUAGE)
        await send_confirmation_email(
            purchase_request, admin_name=user.name, confirmation_link=confirmation_link, lang=lang, db=db,
        )

    await db.commit()
    return RedirectResponse(f"/purchase-requests/{purchase_request.id}", status_code=302)


# ---------------------------------------------------------------------------
# Detail
# ---------------------------------------------------------------------------

@router.get("/{request_id}", response_class=HTMLResponse)
async def purchase_request_detail(request_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_permission(request, db, "purchase_requests", "read")
    pr = await _load_with_details(db, request_id)
    if not pr:
        raise HTTPException(status_code=404, detail=t_for(request, "errors.purchase_request_not_found"))

    is_board_member = getattr(request.state, "is_full_access", False)
    has_already_approved = any(a.user_id == user.id for a in pr.approvals)
    is_requester = pr.requested_by_id == user.id or pr.created_by_id == user.id

    return templates.TemplateResponse("purchase_requests/detail.html", {
        "request": request, "user": user, "pr": pr,
        "required_approvals": REQUIRED_APPROVALS,
        "is_board_member": is_board_member,
        "has_already_approved": has_already_approved,
        "is_requester": is_requester,
        "PurchaseRequestStatus": PurchaseRequestStatus,
        "contacts": await picker_contacts(request, db),
        "max_comment_length": MAX_COMMENT_LENGTH,
    })


@router.post("/{request_id}/comments")
async def purchase_request_comment(
    request_id: str, request: Request, content: str = Form(""), db: AsyncSession = Depends(get_db),
):
    """Issue #249: anyone who can see the request can discuss it; the
    comment is emailed to the requester and the discussion so far."""
    user = await require_permission(request, db, "purchase_requests", "read")
    pr = await db.get(PurchaseRequest, request_id)
    if pr is None:
        raise HTTPException(status_code=404, detail=t_for(request, "errors.purchase_request_not_found"))
    try:
        comment = await add_comment(db, pr, author=user, content=content)
    except ServiceError as e:
        raise HTTPException(status_code=e.http_status, detail=t_for(request, e.key, **e.params))
    await db.commit()
    await notify_comment(
        db, pr, comment, author=user, base_url=str(request.base_url).rstrip("/"),
        lang=getattr(request.state, "language", DEFAULT_LANGUAGE),
    )
    return RedirectResponse(f"/purchase-requests/{request_id}#comment-{comment.id}", status_code=303)


@router.post("/{request_id}/contact")
async def purchase_request_set_contact(
    request_id: str, request: Request, external_contact_id: str = Form(""), db: AsyncSession = Depends(get_db),
):
    """Links (or unlinks, with "") a supplier from the external contacts
    module (ADR 0096). Not an approval-relevant field, so it stays
    editable in every status."""
    await require_permission(request, db, "purchase_requests", "write")
    pr = await db.get(PurchaseRequest, request_id)
    if pr is None:
        raise HTTPException(status_code=404, detail=t_for(request, "errors.purchase_request_not_found"))
    pr.external_contact_id = await resolve_picked_contact(request, db, external_contact_id)
    await db.commit()
    return RedirectResponse(f"/purchase-requests/{request_id}", status_code=303)


# ---------------------------------------------------------------------------
# Approve / Reject (board/admin only)
# ---------------------------------------------------------------------------

@router.post("/{request_id}/approve")
async def purchase_request_approve(request_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_admin(request, db)
    pr = await _load_with_details(db, request_id)
    if not pr:
        raise HTTPException(status_code=404)

    if pr.status != PurchaseRequestStatus.OPEN:
        return RedirectResponse(f"/purchase-requests/{request_id}", status_code=302)

    if any(a.user_id == user.id for a in pr.approvals):
        return RedirectResponse(f"/purchase-requests/{request_id}", status_code=302)

    try:
        await approve_purchase_request(db, pr, acting_user_id=user.id)
    except ServiceError as e:
        raise HTTPException(status_code=e.http_status, detail=t_for(request, e.key, **e.params))

    await db.commit()
    return RedirectResponse(f"/purchase-requests/{request_id}", status_code=302)


@router.post("/{request_id}/reject")
async def purchase_request_reject(
    request_id: str,
    request: Request,
    rejection_reason: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    user = await require_admin(request, db)
    pr = await _load_with_details(db, request_id)
    if not pr:
        raise HTTPException(status_code=404)

    if pr.status != PurchaseRequestStatus.OPEN:
        return RedirectResponse(f"/purchase-requests/{request_id}", status_code=302)

    await reject_purchase_request(db, pr, acting_user_id=user.id, reason=rejection_reason)
    await db.commit()
    return RedirectResponse(f"/purchase-requests/{request_id}", status_code=302)


# ---------------------------------------------------------------------------
# Deep-link confirmation by external requesters (NO login needed)
# ---------------------------------------------------------------------------

@router.get("/confirm/{token}", response_class=HTMLResponse)
async def confirm_page(token: str, request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PurchaseRequest).where(PurchaseRequest.confirmation_token == token))
    pr = result.scalar_one_or_none()
    if not pr or _confirmation_token_expired(pr):
        return templates.TemplateResponse(
            "purchase_requests/confirmation_invalid.html", {"request": request}
        )

    return templates.TemplateResponse("purchase_requests/confirm.html", {
        "request": request, "pr": pr, "token": token,
    })


@router.post("/confirm/{token}")
async def confirm(token: str, request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PurchaseRequest).where(PurchaseRequest.confirmation_token == token))
    pr = result.scalar_one_or_none()
    if not pr or _confirmation_token_expired(pr):
        return templates.TemplateResponse(
            "purchase_requests/confirmation_invalid.html", {"request": request}
        )

    pr.confirmed_by_requester = True
    pr.confirmed_by_requester_at = datetime.now(timezone.utc)
    await db.commit()

    return templates.TemplateResponse("purchase_requests/confirmed.html", {
        "request": request, "pr": pr,
    })
