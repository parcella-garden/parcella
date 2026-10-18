"""
API router: Purchase Requests -- four-eyes principle for club expenses.

Business logic shared with app/routers/purchase_requests.py (HTML)
lives in app/services/purchase_requests.py (ADR 0070) -- this router
owns bearer-token authentication, the permission check, Pydantic body
parsing, and JSON response serialization.

Approve/reject use require_api_full_access, NOT require_api_permission:
approval authority is deliberately narrower than ordinary module write
access (see docs/module-purchase-requests.md), mirroring the HTML
side's require_admin (Group-aware full-access check) rather than the
fine-grained per-module Group permission.
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import PurchaseRequest, PurchaseRequestStatus, User
from app.api_auth import require_api_permission, require_api_full_access
from app.i18n import t_for, DEFAULT_LANGUAGE
from app.module_flags import require_module
from app.services.errors import ServiceError
from app.services.purchase_requests import (
    create_purchase_request, send_confirmation_email, approve_purchase_request, reject_purchase_request,
)
from app.services.external_contacts import get_contact
from app.schemas import (
    PurchaseRequestCreate, PurchaseRequestOut, PurchaseRequestDetailOut, PurchaseRequestRejectRequest,
)

router = APIRouter(
    prefix="/api/v1/purchase-requests",
    tags=["API: Purchase Requests"],
    dependencies=[Depends(require_module("purchase_requests"))],
)


async def _load_with_details(db: AsyncSession, request_id: str) -> Optional[PurchaseRequest]:
    result = await db.execute(
        select(PurchaseRequest)
        .options(selectinload(PurchaseRequest.approvals))
        .where(PurchaseRequest.id == request_id)
    )
    return result.scalar_one_or_none()


@router.get("", response_model=List[PurchaseRequestOut], summary="List purchase requests")
async def purchase_requests_list(
    status_filter: Optional[str] = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission("purchase_requests", "read")),
):
    query = select(PurchaseRequest).order_by(PurchaseRequest.created_at.desc())
    if status_filter:
        query = query.where(PurchaseRequest.status == PurchaseRequestStatus(status_filter))
    result = await db.execute(query)
    return result.scalars().all()


@router.get(
    "/{request_id}", response_model=PurchaseRequestDetailOut,
    summary="Retrieve purchase request incl. approvals",
)
async def purchase_request_get(
    request_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission("purchase_requests", "read")),
):
    pr = await _load_with_details(db, request_id)
    if not pr:
        raise HTTPException(status_code=404, detail="Purchase request not found")
    return pr


@router.post(
    "", response_model=PurchaseRequestOut, status_code=status.HTTP_201_CREATED,
    summary="Create purchase request",
    description="Without requester_email, the calling user is registered as the requester "
                "themselves. With requester_email, a confirmation link is sent by email "
                "(deep-link confirmation without login).",
)
async def purchase_request_create(
    daten: PurchaseRequestCreate, request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission("purchase_requests", "write")),
):
    if daten.external_contact_id and await get_contact(db, daten.external_contact_id) is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="External contact not found")
    pr = await create_purchase_request(
        db,
        title=daten.title, justification=daten.justification, link=daten.link,
        estimated_cost_eur=daten.estimated_cost_eur, created_by_id=user.id,
        requester_name=daten.requester_name,
        requester_email=(str(daten.requester_email) if daten.requester_email else None),
        external_contact_id=daten.external_contact_id or None,
    )
    await db.commit()
    await db.refresh(pr)

    if pr.confirmation_token:
        base_url = str(request.base_url).rstrip("/")
        confirmation_link = f"{base_url}/purchase-requests/confirm/{pr.confirmation_token}"
        lang = getattr(request.state, "language", DEFAULT_LANGUAGE)
        await send_confirmation_email(
            pr, admin_name=user.name, confirmation_link=confirmation_link, lang=lang, db=db,
        )

    return pr


@router.post(
    "/{request_id}/approve", response_model=PurchaseRequestDetailOut,
    summary="Grant approval",
    description="Requires full module access (ADMIN/BOARD role, or a grants_full_access/"
                "grants_system_admin group) -- the same, narrower-than-write-access "
                "authority the web UI requires. The requester may not approve their own "
                "request. Once 2 distinct approvals are reached, the status switches to APPROVED.",
)
async def purchase_request_approve(
    request_id: str, request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_full_access),
):
    pr = await _load_with_details(db, request_id)
    if not pr:
        raise HTTPException(status_code=404, detail="Purchase request not found")

    if pr.status != PurchaseRequestStatus.OPEN:
        raise HTTPException(status_code=409, detail=f"Purchase request is already {pr.status.value}")

    if any(a.user_id == user.id for a in pr.approvals):
        raise HTTPException(status_code=409, detail="You have already approved this.")

    try:
        await approve_purchase_request(db, pr, acting_user_id=user.id)
    except ServiceError as e:
        raise HTTPException(status_code=e.http_status, detail=t_for(request, e.key, **e.params))

    await db.commit()
    return await _load_with_details(db, request_id)


@router.post(
    "/{request_id}/reject", response_model=PurchaseRequestOut,
    summary="Reject purchase request",
    description="Requires full module access, same as approve. A single rejection is enough (veto principle).",
)
async def purchase_request_reject(
    request_id: str,
    daten: PurchaseRequestRejectRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_full_access),
):
    pr = await _load_with_details(db, request_id)
    if not pr:
        raise HTTPException(status_code=404, detail="Purchase request not found")

    if pr.status != PurchaseRequestStatus.OPEN:
        raise HTTPException(status_code=409, detail=f"Purchase request is already {pr.status.value}")

    await reject_purchase_request(db, pr, acting_user_id=user.id, reason=daten.rejection_reason)
    await db.commit()
    await db.refresh(pr)
    return pr
