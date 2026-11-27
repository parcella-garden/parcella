"""Item catalog (invoice item templates)."""
from fastapi import APIRouter
from fastapi import Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models import (
    FinanceCategory,
    InvoiceItemTemplate,
    InvoiceItemTemplateMember,
    InvoiceItemTemplateParcel,
    InvoicePricingMode,
)
from app.permissions import require_permission
from app.l10n import parse_decimal
from app.templating import templates
from app.routers.finances._common import _AUTOMATIC_PRICING_MODES, _dedupe_ids
from app.services.finances import list_active_members, list_active_parcels, list_item_templates

router = APIRouter()


# ---------------------------------------------------------------------------
# Item catalog: reusable line-item templates a board member curates
# directly, replacing the old "copy items from another run" mechanism
# (issue #66) -- see InvoiceItemTemplate's docstring in app/models/finances.py.
# ---------------------------------------------------------------------------

@router.get("/item-templates", response_class=HTMLResponse)
async def item_template_list(request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_permission(request, db, "finances", "read")

    item_templates = await list_item_templates(db)
    next_order = max((t.order_number for t in item_templates), default=0) + 10
    categories_result = await db.execute(select(FinanceCategory).order_by(FinanceCategory.code))
    categories = list(categories_result.scalars().all())
    parcels = await list_active_parcels(db)
    members = await list_active_members(db)

    return templates.TemplateResponse(request, "finances/item_template_list.html", {
        "request": request, "user": user, "item_templates": item_templates, "next_order": next_order,
        "pricing_modes": list(InvoicePricingMode), "categories": categories, "parcels": parcels, "members": members,
    })


@router.post("/item-templates")
async def item_template_create(
    request: Request,
    order_number: int = Form(0),
    name: str = Form(...),
    description: str = Form(""),
    pricing_mode: str = Form(...),
    unit_price: str = Form(""),
    applies_to_all_parcels: str = Form(""),
    applies_to_all_members: str = Form(""),
    parcel_ids: list[str] = Form([]),
    member_ids: list[str] = Form([]),
    category_id: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    await require_permission(request, db, "finances", "write")

    try:
        mode = InvoicePricingMode(pricing_mode)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid pricing_mode")

    applies_all_parcels = applies_to_all_parcels == "on"
    applies_all_members = applies_to_all_members == "on"
    template = InvoiceItemTemplate(
        order_number=order_number,
        name=name.strip(),
        description=description.strip() or None,
        pricing_mode=mode,
        unit_price=parse_decimal(unit_price) if mode not in _AUTOMATIC_PRICING_MODES else None,
        applies_to_all_parcels=applies_all_parcels,
        applies_to_all_members=applies_all_members,
        category_id=category_id.strip() or None,
    )
    db.add(template)
    await db.flush()

    if not applies_all_parcels:
        for parcel_id in _dedupe_ids(parcel_ids):
            db.add(InvoiceItemTemplateParcel(invoice_item_template_id=template.id, parcel_id=parcel_id))
    if not applies_all_members:
        for member_id in _dedupe_ids(member_ids):
            db.add(InvoiceItemTemplateMember(invoice_item_template_id=template.id, member_id=member_id))

    await db.commit()
    return RedirectResponse("/finances/item-templates?success=1", status_code=302)


@router.post("/item-templates/{template_id}/edit")
async def item_template_update(
    template_id: str,
    request: Request,
    order_number: int = Form(0),
    name: str = Form(...),
    description: str = Form(""),
    pricing_mode: str = Form(...),
    unit_price: str = Form(""),
    applies_to_all_parcels: str = Form(""),
    applies_to_all_members: str = Form(""),
    parcel_ids: list[str] = Form([]),
    member_ids: list[str] = Form([]),
    category_id: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    """Edits a template, including its scope (specific parcels or
    specific members, depending on pricing mode) -- freely editable at
    any time, same as a run's own item (see item_update)."""
    await require_permission(request, db, "finances", "write")

    result = await db.execute(
        select(InvoiceItemTemplate)
        .options(
            selectinload(InvoiceItemTemplate.parcel_scopes), selectinload(InvoiceItemTemplate.member_scopes),
        )
        .where(InvoiceItemTemplate.id == template_id)
    )
    template = result.scalar_one_or_none()
    if not template:
        raise HTTPException(status_code=404)

    try:
        mode = InvoicePricingMode(pricing_mode)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid pricing_mode")

    applies_all_parcels = applies_to_all_parcels == "on"
    applies_all_members = applies_to_all_members == "on"
    template.order_number = order_number
    template.name = name.strip()
    template.description = description.strip() or None
    template.pricing_mode = mode
    template.unit_price = parse_decimal(unit_price) if mode not in _AUTOMATIC_PRICING_MODES else None
    template.applies_to_all_parcels = applies_all_parcels
    template.applies_to_all_members = applies_all_members
    template.category_id = category_id.strip() or None

    # See item_update's identical comment above -- the flush() between
    # delete and re-add is required to avoid a transient unique-
    # constraint violation when a scope is unchanged from before.
    for scope in list(template.parcel_scopes):
        await db.delete(scope)
    await db.flush()
    if not applies_all_parcels:
        for parcel_id in _dedupe_ids(parcel_ids):
            db.add(InvoiceItemTemplateParcel(invoice_item_template_id=template.id, parcel_id=parcel_id))
    for scope in list(template.member_scopes):
        await db.delete(scope)
    await db.flush()
    if not applies_all_members:
        for member_id in _dedupe_ids(member_ids):
            db.add(InvoiceItemTemplateMember(invoice_item_template_id=template.id, member_id=member_id))

    await db.commit()
    return RedirectResponse("/finances/item-templates?success=1", status_code=302)


@router.post("/item-templates/{template_id}/delete")
async def item_template_delete(template_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    await require_permission(request, db, "finances", "delete")

    result = await db.execute(select(InvoiceItemTemplate).where(InvoiceItemTemplate.id == template_id))
    template = result.scalar_one_or_none()
    if template:
        await db.delete(template)
        await db.commit()
    return RedirectResponse("/finances/item-templates?success=1", status_code=302)
