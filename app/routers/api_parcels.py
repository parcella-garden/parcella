"""
API router: Parcels -- full CRUD via REST, including member assignment.

Business logic shared with app/routers/parcels.py (HTML) lives in
app/services/parcels.py (ADR 0070) -- this router owns bearer-token
authentication, the fine-grained permission check (require_api_permission,
Group-based like the HTML side), Pydantic body parsing, and JSON
response serialization.
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import Parcel, ParcelStatus, MemberParcel, Member, User
from app.api_auth import require_api_permission
from app.i18n import t_for
from app.parcel_cloud_folders import deactivate_if_vacant
from app.services.errors import ServiceError
from app.services.parcels import create_parcel, update_parcel, assign_member, remove_assignment
from app.schemas import (
    ParcelOut, ParcelDetailOut, ParcelCreate, ParcelUpdate, ParcelAssignmentBrief,
    AssignmentCreate, AssignmentOut,
)

router = APIRouter(prefix="/api/v1/parcels", tags=["API: Parcels"])


def _service_error_to_http(request: Request, e: ServiceError) -> HTTPException:
    # Deliberately always 409 here, independent of e.http_status (which
    # is the HTML side's 400) -- 409 CONFLICT is this API's pre-existing
    # convention for a duplicate plot number, kept as-is; only the text
    # (now i18n'd via the same key HTML uses, previously hard-coded
    # English here) changes.
    return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=t_for(request, e.key, **e.params))


async def _get_parcel_or_404(db: AsyncSession, parcel_id: str, with_details: bool = False) -> Parcel:
    query = select(Parcel).where(Parcel.id == parcel_id)
    if with_details:
        query = query.options(
            selectinload(Parcel.member_assignments).selectinload(MemberParcel.member)
        )
    result = await db.execute(query)
    parcel = result.scalar_one_or_none()
    if not parcel:
        raise HTTPException(status_code=404, detail="Parcel not found")
    return parcel


def _to_detail_schema(parcel: Parcel) -> ParcelDetailOut:
    out = ParcelDetailOut.model_validate(parcel)
    out.members = [
        ParcelAssignmentBrief(
            member_id=z.member.id,
            name=z.member.full_name,
            is_invoice_address=z.is_invoice_address,
        )
        for z in parcel.member_assignments
    ]
    return out


@router.get(
    "",
    response_model=List[ParcelOut],
    summary="List parcels",
)
async def parcels_list(
    search: Optional[str] = Query(None, description="Search in plot number"),
    status_filter: Optional[ParcelStatus] = Query(None, alias="status"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission("members_parcels", "read")),
):
    query = select(Parcel).order_by(Parcel.plot_number).limit(limit).offset(offset)

    if search:
        query = query.where(Parcel.plot_number.ilike(f"%{search}%"))
    if status_filter:
        query = query.where(Parcel.status == status_filter)

    result = await db.execute(query)
    return result.scalars().all()


@router.get(
    "/{parcel_id}",
    response_model=ParcelDetailOut,
    summary="Retrieve a single parcel",
    description="Returns a parcel including assigned members.",
)
async def parcel_get(
    parcel_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission("members_parcels", "read")),
):
    parcel = await _get_parcel_or_404(db, parcel_id, with_details=True)
    return _to_detail_schema(parcel)


@router.post(
    "",
    response_model=ParcelOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create new parcel",
)
async def parcel_create(
    data: ParcelCreate, request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission("members_parcels", "write")),
):
    try:
        parcel = await create_parcel(
            db, plot_number=data.plot_number, area_sqm=data.area_sqm,
            latitude=data.latitude, longitude=data.longitude, notes=data.notes,
        )
    except ServiceError as e:
        raise _service_error_to_http(request, e)
    await db.commit()
    await db.refresh(parcel)
    return parcel


@router.put(
    "/{parcel_id}",
    response_model=ParcelOut,
    summary="Update parcel",
    description="Partial update: only the fields provided are changed. Also covers status changes (active/terminated/deleted) and termination data.",
)
async def parcel_update(
    parcel_id: str, data: ParcelUpdate, request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission("members_parcels", "write")),
):
    parcel = await _get_parcel_or_404(db, parcel_id)

    try:
        await update_parcel(db, parcel, acting_user=user, **data.model_dump(exclude_unset=True))
    except ServiceError as e:
        raise _service_error_to_http(request, e)

    await db.commit()
    await db.refresh(parcel)
    return parcel


@router.delete(
    "/{parcel_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Mark parcel as deleted",
    description="Sets the status to 'deleted' (no actual DB deletion, history is preserved).",
)
async def parcel_delete(
    parcel_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission("members_parcels", "delete")),
):
    parcel = await _get_parcel_or_404(db, parcel_id)
    await update_parcel(db, parcel, acting_user=user, status=ParcelStatus.DELETED)
    await db.commit()


# ---------------------------------------------------------------------------
# Member assignment (sub-resource)
# ---------------------------------------------------------------------------

@router.post(
    "/{parcel_id}/assignments",
    response_model=AssignmentOut,
    status_code=status.HTTP_201_CREATED,
    summary="Assign member to a parcel",
    description="Enables multiple parcels per member and multiple members sharing a parcel. "
                "Reactivates a former (ended) assignment for the same member/parcel pair "
                "instead of creating a duplicate, if one already exists.",
)
async def member_assign(
    parcel_id: str,
    data: AssignmentCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission("members_parcels", "write")),
):
    if data.parcel_id != parcel_id:
        raise HTTPException(status_code=400, detail="parcel_id in body must match the URL")

    await _get_parcel_or_404(db, parcel_id)

    member_result = await db.execute(
        select(Member).where(Member.id == data.member_id, Member.deleted_at.is_(None))
    )
    if not member_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Member not found")

    assignment, _created = await assign_member(
        db, parcel_id, data.member_id,
        is_invoice_address=data.is_invoice_address,
        assigned_from=data.assigned_from, assigned_until=data.assigned_until,
    )
    await db.commit()
    await db.refresh(assignment)
    return assignment


@router.delete(
    "/{parcel_id}/assignments/{assignment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove member assignment",
    description="Ends an active assignment (soft -- history preserved), or hard-deletes an "
                "already-ended one -- same distinction the web UI makes between "
                "ending a tenancy and cleaning up a historical entry.",
)
async def assignment_remove(
    parcel_id: str,
    assignment_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission("members_parcels", "delete")),
):
    result = await db.execute(
        select(MemberParcel).where(
            MemberParcel.id == assignment_id, MemberParcel.parcel_id == parcel_id
        )
    )
    assignment = result.scalar_one_or_none()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    await remove_assignment(db, assignment)
    await db.commit()
    await deactivate_if_vacant(db, parcel_id)
