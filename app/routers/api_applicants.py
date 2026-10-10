"""
API router: Applicants -- people who applied for a free garden plot
(docs/module-applicants.md).

Business logic shared with app/routers/applicants.py (HTML) lives in
app/services/applicants.py (ADR 0070) -- this router owns bearer-token
authentication, the permission check, Pydantic body parsing, and JSON
response serialization. Same "applicants" module permission as the web
UI; DELETE removes the applicant for good (ADR 0091).

The public submit endpoint (the website's application form) is not
here -- see app/routers/api_public.py.
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import Applicant, ApplicantSource, ApplicantStatus, User
from app.api_auth import require_api_permission
from app.i18n import t_for
from app.module_flags import require_module
from app.services.errors import ServiceError
from app.services.applicants import create_applicant, delete_applicant, update_applicant
from app.schemas import ApplicantCreate, ApplicantOut, ApplicantUpdate

router = APIRouter(
    prefix="/api/v1/applicants",
    tags=["API: Applicants"],
    dependencies=[Depends(require_module("applicants"))],
)


async def _get_or_404(db: AsyncSession, applicant_id: str) -> Applicant:
    applicant = (await db.execute(select(Applicant).where(Applicant.id == applicant_id))).scalar_one_or_none()
    if applicant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Applicant not found")
    return applicant


def _service_error(request: Request, error: ServiceError) -> HTTPException:
    return HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=t_for(request, error.key, **error.params))


@router.get("", response_model=List[ApplicantOut], summary="List applicants")
async def applicants_list(
    status_filter: Optional[ApplicantStatus] = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission("applicants", "read")),
):
    query = select(Applicant).order_by(Applicant.applied_at.desc())
    if status_filter is not None:
        query = query.where(Applicant.status == status_filter)
    return (await db.execute(query)).scalars().all()


@router.post("", response_model=ApplicantOut, status_code=status.HTTP_201_CREATED, summary="Add an applicant by hand")
async def applicant_create(
    payload: ApplicantCreate, request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission("applicants", "write")),
):
    try:
        return await create_applicant(
            db, **payload.model_dump(), source=ApplicantSource.MANUAL, created_by_id=user.id,
        )
    except ServiceError as e:
        raise _service_error(request, e)


@router.get("/{applicant_id}", response_model=ApplicantOut, summary="Get one applicant")
async def applicant_get(
    applicant_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission("applicants", "read")),
):
    return await _get_or_404(db, applicant_id)


@router.patch("/{applicant_id}", response_model=ApplicantOut, summary="Change contact data, status or board note")
async def applicant_update(
    applicant_id: str, payload: ApplicantUpdate, request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission("applicants", "write")),
):
    applicant = await _get_or_404(db, applicant_id)
    changes = payload.model_dump(exclude_unset=True)
    if changes.get("email", "") is None or changes.get("status", "") is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="email and status can't be null")
    try:
        return await update_applicant(db, applicant, changed_by_id=user.id, **changes)
    except ServiceError as e:
        raise _service_error(request, e)


@router.delete("/{applicant_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete an applicant for good")
async def applicant_delete(
    applicant_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission("applicants", "delete")),
):
    await delete_applicant(db, await _get_or_404(db, applicant_id))
    return Response(status_code=status.HTTP_204_NO_CONTENT)
