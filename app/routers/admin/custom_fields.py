"""Custom fields for members and parcels: definition, order, archive (issue #443, ADR 0147).

System admins only, like the whole admin panel (ADR 0039). Entering the
values happens on the member and parcel forms.
"""
import urllib.parse

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import require_system_admin
from app.database import get_db
from app.i18n import t_for
from app.models import CustomField, CustomFieldKind, CustomFieldTarget
from app.services import custom_fields as cf
from app.services.errors import ServiceError
from app.templating import templates

router = APIRouter()


def _page_url(target: CustomFieldTarget, error: str = "") -> str:
    url = f"/admin/custom-fields?target={target.value}"
    return url + (f"&error={urllib.parse.quote(error)}" if error else "")


async def _field_or_404(db: AsyncSession, field_id: str) -> CustomField:
    field = await db.get(CustomField, field_id)
    if field is None:
        raise HTTPException(status_code=404)
    return field


def _target_or_404(request: Request, value: str) -> CustomFieldTarget:
    try:
        return cf.parse_target(value)
    except ServiceError:
        raise HTTPException(status_code=404)


@router.get("/custom-fields", response_class=HTMLResponse)
async def custom_fields_page(request: Request, target: str = "MEMBER", error: str = "", db: AsyncSession = Depends(get_db)):
    user = await require_system_admin(request, db)
    target = _target_or_404(request, target)
    fields = await cf.list_fields(db, target, include_archived=True)
    return templates.TemplateResponse(request, "admin/custom_fields.html", {
        "request": request, "user": user, "target": target, "targets": list(CustomFieldTarget),
        "fields": fields, "groups": [f for f in fields if f.kind == CustomFieldKind.GROUP and not f.archived_at],
        "kinds": list(CustomFieldKind), "sub_kinds": cf.SUB_FIELD_KINDS, "error": error[:300],
    })


@router.post("/custom-fields")
async def custom_field_create(
    request: Request,
    target: str = Form(...), label: str = Form(""), kind: str = Form(""), parent_id: str = Form(""),
    unit: str = Form(""), options: str = Form(""), help_text: str = Form(""), required: bool = Form(False),
    db: AsyncSession = Depends(get_db),
):
    await require_system_admin(request, db)
    target = _target_or_404(request, target)
    try:
        await cf.create_field(
            db, target, label=label, kind=kind, parent_id=parent_id or None, unit=unit,
            options_text=options, help_text=help_text, required=required,
        )
    except ServiceError as e:
        await db.rollback()
        return RedirectResponse(_page_url(target, t_for(request, e.key, **e.params)), status_code=303)
    await db.commit()
    return RedirectResponse(_page_url(target), status_code=303)


@router.get("/custom-fields/{field_id}/edit", response_class=HTMLResponse)
async def custom_field_edit_page(field_id: str, request: Request, error: str = "", db: AsyncSession = Depends(get_db)):
    user = await require_system_admin(request, db)
    field = await _field_or_404(db, field_id)
    kind_locked = field.kind == CustomFieldKind.GROUP or await cf.has_values(db, field)
    return templates.TemplateResponse(request, "admin/custom_field_edit.html", {
        "request": request, "user": user, "field": field, "kind_locked": kind_locked,
        "sub_kinds": cf.SUB_FIELD_KINDS, "error": error[:300],
    })


@router.post("/custom-fields/{field_id}/edit")
async def custom_field_update(
    field_id: str, request: Request,
    label: str = Form(""), kind: str = Form(""), unit: str = Form(""), options: str = Form(""),
    help_text: str = Form(""), required: bool = Form(False),
    db: AsyncSession = Depends(get_db),
):
    await require_system_admin(request, db)
    field = await _field_or_404(db, field_id)
    try:
        await cf.update_field(
            db, field, label=label, kind=kind or None, unit=unit, options_text=options,
            help_text=help_text, required=required,
        )
    except ServiceError as e:
        await db.rollback()
        message = urllib.parse.quote(t_for(request, e.key, **e.params))
        return RedirectResponse(f"/admin/custom-fields/{field_id}/edit?error={message}", status_code=303)
    await db.commit()
    return RedirectResponse(_page_url(field.target), status_code=303)


@router.post("/custom-fields/{field_id}/archive")
async def custom_field_archive(field_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    await require_system_admin(request, db)
    field = await _field_or_404(db, field_id)
    await cf.set_archived(db, field, True)
    await db.commit()
    return RedirectResponse(_page_url(field.target), status_code=303)


@router.post("/custom-fields/{field_id}/restore")
async def custom_field_restore(field_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    await require_system_admin(request, db)
    field = await _field_or_404(db, field_id)
    target = field.target
    try:
        await cf.set_archived(db, field, False)
    except ServiceError as e:
        await db.rollback()
        return RedirectResponse(_page_url(target, t_for(request, e.key, **e.params)), status_code=303)
    await db.commit()
    return RedirectResponse(_page_url(target), status_code=303)


@router.post("/custom-fields/{field_id}/move")
async def custom_field_move(field_id: str, request: Request, direction: str = Form("down"), db: AsyncSession = Depends(get_db)):
    await require_system_admin(request, db)
    field = await _field_or_404(db, field_id)
    await cf.move_field(db, field, -1 if direction == "up" else 1)
    await db.commit()
    return RedirectResponse(_page_url(field.target), status_code=303)
