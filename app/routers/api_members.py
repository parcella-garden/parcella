"""
API router: Members -- full CRUD via REST.

Business logic shared with app/routers/members.py (HTML) lives in
app/services/members.py (ADR 0070) -- this router owns bearer-token
authentication, the fine-grained permission check (require_api_permission,
Group-based like the HTML side), Pydantic body parsing, and JSON
response serialization.
"""
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import Member, MemberParcel, User
from app.api_auth import require_api_permission
from app.services.members import (
    active_members_query, create_member, update_member,
    add_phone, remove_phone, add_email, remove_email,
)
from app.schemas import (
    MemberOut, MemberDetailOut, MemberCreate, MemberUpdate,
    PhoneOut, PhoneCreate, EmailAddressOut, EmailAddressCreate,
    MemberAssignmentBrief,
)

router = APIRouter(prefix="/api/v1/members", tags=["API: Members"])


async def _get_member_or_404(db: AsyncSession, member_id: str, with_details: bool = False) -> Member:
    query = select(Member).where(Member.id == member_id, Member.deleted_at.is_(None))
    if with_details:
        query = query.options(
            selectinload(Member.phone_numbers),
            selectinload(Member.email_addresses),
            selectinload(Member.parcel_assignments).selectinload(MemberParcel.parcel),
        )
    else:
        query = query.options(
            selectinload(Member.phone_numbers),
            selectinload(Member.email_addresses),
        )
    result = await db.execute(query)
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    return member


def _to_detail_schema(member: Member) -> MemberDetailOut:
    out = MemberDetailOut.model_validate(member)
    out.parcels = [
        MemberAssignmentBrief(
            parcel_id=z.parcel.id,
            plot_number=z.parcel.plot_number,
            is_invoice_address=z.is_invoice_address,
        )
        for z in member.parcel_assignments
    ]
    return out


@router.get(
    "",
    response_model=List[MemberOut],
    summary="List members",
    description="Returns all (non-deleted) members. Supports full-text search and pagination.",
)
async def members_list(
    search: Optional[str] = Query(None, description="Search in first/last name and city"),
    active_only: bool = Query(False, description="Only active memberships (member_since already started, member_until in the future or empty)"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission("members_parcels", "read")),
):
    query = (
        select(Member)
        .options(selectinload(Member.phone_numbers), selectinload(Member.email_addresses))
        .where(Member.deleted_at.is_(None))
    )
    if search:
        query = query.where(
            or_(
                Member.first_name.ilike(f"%{search}%"),
                Member.last_name.ilike(f"%{search}%"),
                Member.city.ilike(f"%{search}%"),
            )
        )
    # active_only pushed into SQL via the same active_member_filter()
    # the HTML side uses (ADR 0070), applied BEFORE pagination -- it
    # used to filter in Python after limit/offset, which could return
    # fewer than `limit` rows or skip an active member depending on
    # which rows the page happened to land on.
    if active_only:
        query = active_members_query(query)
    query = query.order_by(Member.last_name, Member.first_name).limit(limit).offset(offset)

    result = await db.execute(query)
    return result.scalars().all()


@router.get(
    "/{member_id}",
    response_model=MemberDetailOut,
    summary="Retrieve a single member",
    description="Returns a member including assigned parcels, phone numbers, and email addresses.",
)
async def member_get(
    member_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission("members_parcels", "read")),
):
    member = await _get_member_or_404(db, member_id, with_details=True)
    return _to_detail_schema(member)


@router.post(
    "",
    response_model=MemberOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create new member",
)
async def member_create(
    data: MemberCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission("members_parcels", "write")),
):
    member = await create_member(db, **data.model_dump())
    await db.commit()
    await db.refresh(member, attribute_names=["phone_numbers", "email_addresses"])
    return member


@router.put(
    "/{member_id}",
    response_model=MemberOut,
    summary="Update member",
    description="Partial update: only the fields provided are changed.",
)
async def member_update(
    member_id: str,
    data: MemberUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission("members_parcels", "write")),
):
    member = await _get_member_or_404(db, member_id)
    await update_member(db, member, **data.model_dump(exclude_unset=True))
    await db.commit()
    await db.refresh(member, attribute_names=["phone_numbers", "email_addresses"])
    return member


@router.delete(
    "/{member_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete member (soft delete)",
    description="Marks the member as deleted (deleted_at set). Data remains in the database.",
)
async def member_delete(
    member_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission("members_parcels", "delete")),
):
    member = await _get_member_or_404(db, member_id)
    member.deleted_at = datetime.now(timezone.utc)
    await db.commit()


# ---------------------------------------------------------------------------
# Phone numbers (sub-resource)
# ---------------------------------------------------------------------------

@router.post(
    "/{member_id}/phone_numbers",
    response_model=PhoneOut,
    status_code=status.HTTP_201_CREATED,
    summary="Add phone number",
)
async def phone_add(
    member_id: str,
    data: PhoneCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission("members_parcels", "write")),
):
    await _get_member_or_404(db, member_id)
    phone = await add_phone(db, member_id, **data.model_dump())
    await db.commit()
    await db.refresh(phone)
    return phone


@router.delete(
    "/{member_id}/phone_numbers/{phone_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove phone number",
)
async def phone_remove(
    member_id: str,
    phone_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission("members_parcels", "delete")),
):
    if not await remove_phone(db, member_id, phone_id):
        raise HTTPException(status_code=404, detail="Phone number not found")
    await db.commit()


# ---------------------------------------------------------------------------
# Email addresses (sub-resource)
# ---------------------------------------------------------------------------

@router.post(
    "/{member_id}/email-addresses",
    response_model=EmailAddressOut,
    status_code=status.HTTP_201_CREATED,
    summary="Add email address",
)
async def email_add(
    member_id: str,
    data: EmailAddressCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission("members_parcels", "write")),
):
    await _get_member_or_404(db, member_id)
    email_obj = await add_email(
        db, member_id, address=str(data.address), label=data.label, is_primary=data.is_primary,
    )
    await db.commit()
    await db.refresh(email_obj)
    return email_obj


@router.delete(
    "/{member_id}/email-addresses/{email_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove email address",
)
async def email_remove(
    member_id: str,
    email_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission("members_parcels", "delete")),
):
    if not await remove_email(db, member_id, email_id):
        raise HTTPException(status_code=404, detail="Email address not found")
    await db.commit()
