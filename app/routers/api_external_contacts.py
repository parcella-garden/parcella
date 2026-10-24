"""
API router: External contacts -- suppliers, craftsmen, authorities
(docs/module-external-contacts.md, ADR 0096): companies and persons,
a person optionally at one company (ADR 0110).

Business logic shared with app/routers/external_contacts.py (HTML)
lives in app/services/external_contacts.py (ADR 0070) -- this router
owns bearer-token authentication, the permission check, Pydantic body
parsing and JSON serialization. A duplicate contact person name is a
409 (the service's own status), other rule violations a 422.
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api_auth import require_api_permission
from app.contact_filters import ContactListFilter
from app.database import get_db
from app.i18n import t_for
from app.models import ExternalContact, ExternalContactKind, ExternalContactTag, User
from app.module_flags import require_module
from app.schemas import (
    EmailAddressCreate, EmailAddressOut, ExternalContactCreate, ExternalContactOut,
    ExternalContactTagOut, ExternalContactUpdate, MemberTagAssign, MemberTagRename,
    PhoneCreate, PhoneOut,
)
from app.services.errors import ServiceError
from app.services.external_contacts import (
    add_email, add_phone, create_contact, delete_tag, get_contact, list_tags, merge_companies, remove_email,
    remove_phone, rename_tag, soft_delete_contact, tag_contact, untag_contact, update_contact,
)

MODULE = "external_contacts"

router = APIRouter(
    prefix="/api/v1/external-contacts",
    tags=["API: External contacts"],
    dependencies=[Depends(require_module(MODULE))],
)

_DETAIL_OPTIONS = (
    selectinload(ExternalContact.phone_numbers),
    selectinload(ExternalContact.email_addresses),
    selectinload(ExternalContact.tags),
)


def _service_error(request: Request, error: ServiceError) -> HTTPException:
    code = error.http_status if error.http_status in (404, 409) else status.HTTP_422_UNPROCESSABLE_ENTITY
    return HTTPException(status_code=code, detail=t_for(request, error.key, **error.params))


async def _get_contact_or_404(db: AsyncSession, contact_id: str) -> ExternalContact:
    contact = await db.scalar(
        select(ExternalContact).options(*_DETAIL_OPTIONS)
        .where(ExternalContact.id == contact_id, ExternalContact.deleted_at.is_(None))
        .execution_options(populate_existing=True)
    )
    if contact is None:
        raise HTTPException(status_code=404, detail="External contact not found")
    return contact


async def _get_tag_or_404(db: AsyncSession, tag_id: str) -> ExternalContactTag:
    tag = await db.get(ExternalContactTag, tag_id)
    if tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag


@router.get("", response_model=List[ExternalContactOut], summary="List external contacts")
async def contacts_list(
    search: str = Query("", description="Company, name, city, email or phone (substring)"),
    tag: str = Query("", description="Tag id"),
    kind: Optional[ExternalContactKind] = Query(None, description="Only companies or only persons"),
    company_id: str = Query("", description="Only the people of this company"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission(MODULE, "read")),
):
    query = ContactListFilter.from_query(search, tag).apply()
    if kind is not None:
        query = query.where(ExternalContact.kind == kind)
    if company_id:
        query = query.where(ExternalContact.company_id == company_id)
    return (await db.scalars(query.options(*_DETAIL_OPTIONS).limit(limit).offset(offset))).all()


@router.post("", response_model=ExternalContactOut, status_code=status.HTTP_201_CREATED, summary="Create an external contact")
async def contact_create(
    data: ExternalContactCreate, request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission(MODULE, "write")),
):
    fields = data.model_dump()
    fields["kind"] = data.kind.value if data.kind else None
    try:
        contact = await create_contact(db, **fields)
    except ServiceError as e:
        raise _service_error(request, e)
    await db.commit()
    return await _get_contact_or_404(db, contact.id)


# --- Tags (registered before /{contact_id}) ---------------------------------

@router.get("/tags", response_model=List[ExternalContactTagOut], summary="List external contact tags")
async def tags_list(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission(MODULE, "read")),
):
    return await list_tags(db)


@router.patch("/tags/{tag_id}", response_model=ExternalContactTagOut, summary="Rename an external contact tag")
async def tag_rename(
    tag_id: str, data: MemberTagRename, request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission(MODULE, "write")),
):
    tag = await _get_tag_or_404(db, tag_id)
    try:
        await rename_tag(db, tag, data.name)
    except ServiceError as e:
        raise _service_error(request, e)
    await db.commit()
    return tag


@router.delete("/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete an external contact tag")
async def tag_delete(
    tag_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission(MODULE, "delete")),
):
    await delete_tag(db, await _get_tag_or_404(db, tag_id))
    await db.commit()


# --- One contact ------------------------------------------------------------

@router.get("/{contact_id}", response_model=ExternalContactOut, summary="Get one external contact")
async def contact_get(
    contact_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission(MODULE, "read")),
):
    return await _get_contact_or_404(db, contact_id)


@router.put("/{contact_id}", response_model=ExternalContactOut, summary="Update an external contact (partial)")
async def contact_update(
    contact_id: str, data: ExternalContactUpdate, request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission(MODULE, "write")),
):
    contact = await _get_contact_or_404(db, contact_id)
    fields = data.model_dump(exclude_unset=True)
    if data.kind:
        fields["kind"] = data.kind.value
    try:
        await update_contact(db, contact, **fields)
    except ServiceError as e:
        raise _service_error(request, e)
    await db.commit()
    return await _get_contact_or_404(db, contact_id)


@router.delete(
    "/{contact_id}", status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an external contact (soft delete; 409 for a company that still has people)",
)
async def contact_delete(
    contact_id: str, request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission(MODULE, "delete")),
):
    try:
        await soft_delete_contact(db, await _get_contact_or_404(db, contact_id))
    except ServiceError as e:
        raise _service_error(request, e)
    await db.commit()


@router.post(
    "/{contact_id}/merge-into/{target_id}", response_model=ExternalContactOut,
    summary="Merge a company into another one (moves people, phones, emails, tags and links; soft-deletes it)",
)
async def contact_merge(
    contact_id: str, target_id: str, request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission(MODULE, "delete")),
):
    source = await _get_contact_or_404(db, contact_id)
    target = await get_contact(db, target_id)
    if target is None:
        raise HTTPException(status_code=404, detail="External contact not found")
    try:
        await merge_companies(db, source, target)
    except ServiceError as e:
        raise _service_error(request, e)
    await db.commit()
    return await _get_contact_or_404(db, target_id)


@router.post(
    "/{contact_id}/tags", response_model=ExternalContactTagOut, status_code=status.HTTP_201_CREATED,
    summary="Tag an external contact", description="By `tag_id`, or by `name` (reuses a tag of that name, any case, or creates it).",
)
async def contact_tag_add(
    contact_id: str, data: MemberTagAssign, request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission(MODULE, "write")),
):
    if bool(data.tag_id) == bool(data.name):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Pass exactly one of tag_id and name")
    await _get_contact_or_404(db, contact_id)
    try:
        tag = await tag_contact(db, contact_id, tag_id=data.tag_id, name=data.name)
    except ServiceError as e:
        raise _service_error(request, e)
    await db.commit()
    return tag


@router.delete("/{contact_id}/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Remove a tag from an external contact")
async def contact_tag_remove(
    contact_id: str, tag_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission(MODULE, "write")),
):
    if not await untag_contact(db, contact_id, tag_id):
        raise HTTPException(status_code=404, detail="Contact doesn't carry this tag")
    await db.commit()


@router.post("/{contact_id}/phone_numbers", response_model=PhoneOut, status_code=status.HTTP_201_CREATED, summary="Add phone number")
async def phone_add(
    contact_id: str, data: PhoneCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission(MODULE, "write")),
):
    await _get_contact_or_404(db, contact_id)
    phone = await add_phone(db, contact_id, **data.model_dump())
    await db.commit()
    await db.refresh(phone)
    return phone


@router.delete("/{contact_id}/phone_numbers/{phone_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Remove phone number")
async def phone_remove(
    contact_id: str, phone_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission(MODULE, "delete")),
):
    if not await remove_phone(db, contact_id, phone_id):
        raise HTTPException(status_code=404, detail="Phone number not found")
    await db.commit()


@router.post("/{contact_id}/email-addresses", response_model=EmailAddressOut, status_code=status.HTTP_201_CREATED, summary="Add email address")
async def email_add(
    contact_id: str, data: EmailAddressCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission(MODULE, "write")),
):
    await _get_contact_or_404(db, contact_id)
    email_obj = await add_email(db, contact_id, address=str(data.address), label=data.label, is_primary=data.is_primary)
    await db.commit()
    await db.refresh(email_obj)
    return email_obj


@router.delete("/{contact_id}/email-addresses/{email_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Remove email address")
async def email_remove(
    contact_id: str, email_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission(MODULE, "delete")),
):
    if not await remove_email(db, contact_id, email_id):
        raise HTTPException(status_code=404, detail="Email address not found")
    await db.commit()
