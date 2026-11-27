"""REST API for custom fields (issue #443, ADR 0147).

Definitions are read-only here -- setting them up stays with a system
admin in the web UI. Values are read and written per member or parcel,
by field key, with the same members_parcels permission as the member
and parcel endpoints themselves.
"""
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api_auth import require_api_permission
from app.database import get_db
from app.i18n import t_for
from app.models import CustomFieldTarget, Member, Parcel, User
from app.schemas import CustomFieldOut
from app.services import custom_fields as cf
from app.services.errors import ServiceError

router = APIRouter(prefix="/api/v1", tags=["API: Custom fields"])


def _error(request: Request, error: ServiceError) -> HTTPException:
    code = status.HTTP_404_NOT_FOUND if error.http_status == 404 else status.HTTP_422_UNPROCESSABLE_ENTITY
    return HTTPException(status_code=code, detail=t_for(request, error.key, **error.params))


@router.get("/custom-fields", response_model=List[CustomFieldOut], summary="List custom field definitions")
async def custom_field_definitions(
    request: Request,
    target: str = "MEMBER",
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission("members_parcels", "read")),
):
    """The active custom fields of members (`target=MEMBER`) or parcels
    (`target=PARCEL`), in display order."""
    try:
        target_enum = cf.parse_target(target.upper())
    except ServiceError as e:
        raise _error(request, e)
    fields = await cf.list_fields(db, target_enum)
    keys = {f.id: f.key for f in fields}
    return [
        CustomFieldOut(
            key=f.key, label=f.label, kind=f.kind.value, group=keys.get(f.parent_id), unit=f.unit,
            options=f.options, required=f.required, help_text=f.help_text,
        )
        for f in fields
    ]


async def _owner_or_404(db: AsyncSession, model, owner_id: str):
    owner = await db.get(model, owner_id)
    if owner is None or getattr(owner, "deleted_at", None) is not None:
        raise HTTPException(status_code=404)
    return owner


async def _get(db, target, model, owner_id):
    await _owner_or_404(db, model, owner_id)
    return await cf.api_values(db, target, owner_id)


async def _put(request, db, target, model, owner_id, changes):
    await _owner_or_404(db, model, owner_id)
    try:
        await cf.api_update(db, target, owner_id, changes)
    except ServiceError as e:
        await db.rollback()
        raise _error(request, e)
    await db.commit()
    return await cf.api_values(db, target, owner_id)


_PUT_DOC = ("Sets the given keys only (others stay as they are); `null` or `false` clears a value. "
            "Yes/no fields and groups take `true`/`false`, numbers a number or a numeric string, "
            "dates `YYYY-MM-DD`, choices one of the field's options. A filled-in sub-field ticks "
            "its group; a group set to `false` clears its sub-fields.")


@router.get("/members/{member_id}/custom-fields", response_model=Dict[str, Any], summary="A member's custom field values")
async def member_custom_fields(
    member_id: str, db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission("members_parcels", "read")),
):
    return await _get(db, CustomFieldTarget.MEMBER, Member, member_id)


@router.put("/members/{member_id}/custom-fields", response_model=Dict[str, Any],
            summary="Set a member's custom field values", description=_PUT_DOC)
async def member_custom_fields_update(
    member_id: str, request: Request, changes: Dict[str, Optional[Any]] = Body(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission("members_parcels", "write")),
):
    return await _put(request, db, CustomFieldTarget.MEMBER, Member, member_id, changes)


@router.get("/parcels/{parcel_id}/custom-fields", response_model=Dict[str, Any], summary="A parcel's custom field values")
async def parcel_custom_fields(
    parcel_id: str, db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission("members_parcels", "read")),
):
    return await _get(db, CustomFieldTarget.PARCEL, Parcel, parcel_id)


@router.put("/parcels/{parcel_id}/custom-fields", response_model=Dict[str, Any],
            summary="Set a parcel's custom field values", description=_PUT_DOC)
async def parcel_custom_fields_update(
    parcel_id: str, request: Request, changes: Dict[str, Optional[Any]] = Body(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission("members_parcels", "write")),
):
    return await _put(request, db, CustomFieldTarget.PARCEL, Parcel, parcel_id, changes)
