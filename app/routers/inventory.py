"""
Inventory module web router.

An asset register for what the club owns (and what members store on
club property, tracked with the same financial fields -- see
InventoryItem's docstring in app/models.py), grouped into
freely-configurable categories, plus a lending system for borrowable
items. See docs/module-inventory.md for the full design.

Gated by the "inventory" module permission (see app/permissions.py):
ADMIN/BOARD always have full access; other roles need a group grant.
Viewing requires "read"; creating/editing/retiring items, managing
categories, and checking items in/out require "write"; hard-deleting
an item or a category requires "delete".

Route registration order matters here: /categories/, /new, and
/loans/... are all registered before the single-segment /{item_id}
catch-all, so a request like GET /inventory/categories/ can't
accidentally be swallowed by /{item_id} treating "categories" as an
item ID.
"""
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Optional

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db, active_member_filter
from app.models import (
    InventoryCategory, InventoryItem, InventoryOwnerType, ItemLoan, Member,
)
from app.permissions import require_permission
from app.module_flags import require_module
from app.i18n import t_for
from app.templating import templates
from app.services.errors import ServiceError
from app.services.inventory import (
    create_category, delete_category, create_item, update_item,
    retire_item, checkout_loan, return_loan,
)

router = APIRouter(
    prefix="/inventory",
    tags=["inventory"],
    dependencies=[Depends(require_module("inventory"))],
)


# Form input that isn't a number/date used to raise a bare ValueError --
# an Internal Server Error, e.g. for "5 €" as a loan fee (issue #315).
# These raise a ServiceError instead, which the handlers show as a message.

def _parse_decimal(value: Optional[str]) -> Optional[Decimal]:
    """An amount like "5", "2,50" or "2.50"; empty = None. Anything else
    (text, a currency sign, NaN/Infinity, a negative amount) is refused."""
    value = (value or "").strip().replace(",", ".")
    if not value:
        return None
    try:
        amount = Decimal(value)
    except InvalidOperation:
        raise ServiceError("inventory.errors.invalid_amount", http_status=400)
    if not amount.is_finite() or amount < 0:
        raise ServiceError("inventory.errors.invalid_amount", http_status=400)
    return amount


def _parse_date(value: Optional[str]) -> Optional[date]:
    value = (value or "").strip()
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise ServiceError("inventory.errors.invalid_date", http_status=400)


def _parse_quantity(value: Optional[str]) -> int:
    value = (value or "").strip()
    if not value:
        return 1
    try:
        quantity = int(value)
    except ValueError:
        raise ServiceError("inventory.errors.invalid_quantity", http_status=400)
    if quantity < 1:
        raise ServiceError("inventory.errors.invalid_quantity", http_status=400)
    return quantity


async def _get_item_or_404(db: AsyncSession, item_id: str) -> InventoryItem:
    result = await db.execute(
        select(InventoryItem)
        .options(
            selectinload(InventoryItem.category),
            selectinload(InventoryItem.owner_member),
            selectinload(InventoryItem.loans).selectinload(ItemLoan.member),
        )
        .where(InventoryItem.id == item_id)
    )
    item = result.scalar_one_or_none()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


# ---------------------------------------------------------------------------
# Items -- list
# ---------------------------------------------------------------------------

@router.get("/", response_class=HTMLResponse)
async def inventory_list(
    request: Request, category_id: str = "", include_retired: bool = False,
    db: AsyncSession = Depends(get_db),
):
    user = await require_permission(request, db, "inventory", "read")

    query = (
        select(InventoryItem)
        .options(selectinload(InventoryItem.category), selectinload(InventoryItem.loans))
        .order_by(InventoryItem.name)
    )
    if not include_retired:
        query = query.where(InventoryItem.retired_at.is_(None))
    if category_id:
        query = query.where(InventoryItem.category_id == category_id)
    result = await db.execute(query)
    items = result.scalars().all()

    categories_result = await db.execute(select(InventoryCategory).order_by(InventoryCategory.name))
    categories = categories_result.scalars().all()

    # Group for display: (category-or-None, [items])
    by_category = {}
    for item in items:
        by_category.setdefault(item.category, []).append(item)
    grouped = sorted(by_category.items(), key=lambda pair: (pair[0].name if pair[0] else "\uffff"))

    return templates.TemplateResponse("inventory/list.html", {
        "request": request, "user": user, "grouped": grouped, "categories": categories,
        "category_id": category_id, "include_retired": include_retired,
    })


# ---------------------------------------------------------------------------
# Categories (registered before /{item_id} -- see module docstring)
# ---------------------------------------------------------------------------

@router.get("/categories/", response_class=HTMLResponse)
async def categories_list(request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_permission(request, db, "inventory", "write")
    result = await db.execute(select(InventoryCategory).order_by(InventoryCategory.name))
    categories = result.scalars().all()
    return templates.TemplateResponse("inventory/categories.html", {
        "request": request, "user": user, "categories": categories, "error": None,
    })


@router.post("/categories/new")
async def category_create(request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_permission(request, db, "inventory", "write")
    form = await request.form()

    try:
        await create_category(db, name=form.get("name") or "", description=form.get("description"))
    except ServiceError as e:
        result = await db.execute(select(InventoryCategory).order_by(InventoryCategory.name))
        return templates.TemplateResponse("inventory/categories.html", {
            "request": request, "user": user, "categories": result.scalars().all(),
            "error": e.key,
        }, status_code=e.http_status)

    await db.commit()
    return RedirectResponse(url="/inventory/categories/", status_code=303)


@router.post("/categories/{category_id}/delete")
async def category_delete(category_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    """Items in this category are not deleted -- see the API's
    delete_category for the same note; category_id is just cleared."""
    await require_permission(request, db, "inventory", "delete")
    category = await delete_category(db, category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    await db.commit()
    return RedirectResponse(url="/inventory/categories/", status_code=303)


# ---------------------------------------------------------------------------
# Active loans overview (registered before /{item_id} for the same
# route-ordering reason as categories)
# ---------------------------------------------------------------------------

@router.get("/loans/active", response_class=HTMLResponse)
async def active_loans_overview(request: Request, db: AsyncSession = Depends(get_db)):
    """Board-wide view of everything currently checked out, across
    every item -- "who has what out right now," not scoped to one
    item's detail page."""
    user = await require_permission(request, db, "inventory", "read")
    result = await db.execute(
        select(ItemLoan)
        .options(selectinload(ItemLoan.item), selectinload(ItemLoan.member))
        .where(ItemLoan.returned_date.is_(None))
        .order_by(ItemLoan.borrowed_date)
    )
    loans = result.scalars().all()
    return templates.TemplateResponse("inventory/active_loans.html", {
        "request": request, "user": user, "loans": loans,
    })


@router.post("/loans/{loan_id}/return")
async def loan_return(loan_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    await require_permission(request, db, "inventory", "write")
    result = await db.execute(select(ItemLoan).where(ItemLoan.id == loan_id))
    loan = result.scalar_one_or_none()
    if loan is None:
        raise HTTPException(status_code=404, detail="Loan not found")
    if await return_loan(db, loan):
        await db.commit()
    return RedirectResponse(url=f"/inventory/{loan.item_id}", status_code=303)


# ---------------------------------------------------------------------------
# Items -- create / edit (registered before /{item_id})
# ---------------------------------------------------------------------------

async def _item_form_context(request, db, user, item=None, error=None):
    categories_result = await db.execute(select(InventoryCategory).order_by(InventoryCategory.name))
    members_result = await db.execute(
        select(Member).where(active_member_filter()).order_by(Member.last_name, Member.first_name)
    )
    return {
        "request": request, "user": user, "item": item, "error": error,
        "categories": categories_result.scalars().all(),
        "members": members_result.scalars().all(),
        "InventoryOwnerType": InventoryOwnerType,
    }


@router.get("/new", response_class=HTMLResponse)
async def item_new_form(request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_permission(request, db, "inventory", "write")
    return templates.TemplateResponse("inventory/form.html", await _item_form_context(request, db, user))


def _item_fields_from_form(form: dict) -> dict:
    owner_type = form.get("owner_type") or "CLUB"
    return dict(
        name=form.get("name") or "",
        description=(form.get("description") or "").strip() or None,
        category_id=(form.get("category_id") or "").strip() or None,
        owner_type=owner_type,
        owner_member_id=(form.get("owner_member_id") or "").strip() or None,
        storage_location=(form.get("storage_location") or "").strip() or None,
        purchase_date=_parse_date(form.get("purchase_date")),
        purchase_price=_parse_decimal(form.get("purchase_price")),
        current_value=_parse_decimal(form.get("current_value")),
        current_value_updated_at=_parse_date(form.get("current_value_updated_at")),
        replacement_cost=_parse_decimal(form.get("replacement_cost")),
        quantity_total=_parse_quantity(form.get("quantity_total")),
        is_borrowable=form.get("is_borrowable") == "true",
        default_loan_fee=_parse_decimal(form.get("default_loan_fee")),
        notes=(form.get("notes") or "").strip() or None,
    )


@router.post("/new")
async def item_create(request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_permission(request, db, "inventory", "write")
    form = await request.form()

    try:
        item = await create_item(db, **_item_fields_from_form(form), created_by_id=user.id)
    except ServiceError as e:
        return templates.TemplateResponse(
            "inventory/form.html",
            await _item_form_context(request, db, user, error=e.key),
            status_code=e.http_status,
        )

    await db.commit()
    return RedirectResponse(url=f"/inventory/{item.id}", status_code=303)


@router.get("/{item_id}/edit", response_class=HTMLResponse)
async def item_edit_form(item_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_permission(request, db, "inventory", "write")
    item = await _get_item_or_404(db, item_id)
    return templates.TemplateResponse("inventory/form.html", await _item_form_context(request, db, user, item=item))


@router.post("/{item_id}/edit")
async def item_update(item_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_permission(request, db, "inventory", "write")
    item = await _get_item_or_404(db, item_id)
    form = await request.form()

    try:
        await update_item(db, item, **_item_fields_from_form(form))
    except ServiceError as e:
        return templates.TemplateResponse(
            "inventory/form.html",
            await _item_form_context(request, db, user, item=item, error=e.key),
            status_code=e.http_status,
        )

    await db.commit()
    return RedirectResponse(url=f"/inventory/{item.id}", status_code=303)


@router.post("/{item_id}/retire")
async def item_retire(item_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    await require_permission(request, db, "inventory", "write")
    item = await _get_item_or_404(db, item_id)
    await retire_item(db, item)
    await db.commit()
    return RedirectResponse(url=f"/inventory/{item.id}", status_code=303)


@router.post("/{item_id}/delete")
async def item_delete(item_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    await require_permission(request, db, "inventory", "delete")
    item = await _get_item_or_404(db, item_id)
    await db.delete(item)
    await db.commit()
    return RedirectResponse(url="/inventory/", status_code=303)


@router.post("/{item_id}/loans/checkout")
async def loan_checkout(item_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_permission(request, db, "inventory", "write")
    item = await _get_item_or_404(db, item_id)
    form = await request.form()

    try:
        await checkout_loan(
            db, item,
            member_id=(form.get("member_id") or "").strip(),
            quantity=_parse_quantity(form.get("quantity")),
            borrowed_date=_parse_date(form.get("borrowed_date")),
            fee_charged=_parse_decimal(form.get("fee_charged")),
            note=(form.get("note") or "").strip() or None,
            created_by_id=user.id,
        )
    except ServiceError as e:
        # Back to the item page with the message and what was typed, not a
        # bare error response (issue #315).
        # checkout_loan() validates before it changes anything, so there
        # is nothing to roll back (a rollback would also expire the item's
        # eagerly loaded relationships the template needs).
        return templates.TemplateResponse("inventory/detail.html", {
            **await _item_detail_context(request, db, user, item),
            "checkout_error": t_for(request, e.key, **e.params),
            "checkout_entered": {k: form.get(k) or "" for k in ("member_id", "quantity", "borrowed_date", "fee_charged", "note")},
        }, status_code=e.http_status)

    await db.commit()
    return RedirectResponse(url=f"/inventory/{item.id}", status_code=303)


# ---------------------------------------------------------------------------
# Item detail -- MUST be registered after /new, /categories/*, /loans/*
# and /{item_id}/* above, since it's the single-segment catch-all.
# ---------------------------------------------------------------------------

@router.get("/{item_id}", response_class=HTMLResponse)
async def item_detail(item_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_permission(request, db, "inventory", "read")
    item = await _get_item_or_404(db, item_id)
    return templates.TemplateResponse("inventory/detail.html", await _item_detail_context(request, db, user, item))


async def _item_detail_context(request: Request, db: AsyncSession, user, item: InventoryItem) -> dict:
    members_result = await db.execute(
        select(Member).where(active_member_filter()).order_by(Member.last_name, Member.first_name)
    )
    loans_sorted = sorted(item.loans, key=lambda loan: loan.borrowed_date, reverse=True)
    return {
        "request": request, "user": user, "item": item,
        "loans": loans_sorted, "members": members_result.scalars().all(),
        "today": date.today().isoformat(),
    }
