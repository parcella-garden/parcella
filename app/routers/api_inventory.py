"""
API-Router: Inventory -- categories, items, and the lending system.

Business logic shared with app/routers/inventory.py (HTML) lives in
app/services/inventory.py (ADR 0070) -- this router owns bearer-token
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
from app.models import InventoryCategory, InventoryItem, ItemLoan, User
from app.api_auth import require_api_permission
from app.module_flags import require_module
from app.i18n import t_for
from app.services.errors import ServiceError
from app.services.inventory import (
    create_category, delete_category, create_item, update_item,
    retire_item, checkout_loan, return_loan,
)
from app.schemas import (
    InventoryCategoryOut, InventoryCategoryCreate,
    InventoryItemOut, InventoryItemCreate, InventoryItemUpdate,
    ItemLoanOut, ItemLoanCreate, ItemLoanReturn,
)

router = APIRouter(
    prefix="/api/v1/inventory",
    tags=["API: Inventory"],
    dependencies=[Depends(require_module("inventory"))],
)


def _service_error_to_http(request: Request, e: ServiceError) -> HTTPException:
    # These specific short codes (missing_name/duplicate_name/
    # missing_owner_member) map to the HTML template's own error
    # namespaces -- see app/services/inventory.py's docstrings.
    key_map = {
        "missing_name": "inventory.form.error_missing_name",
        "duplicate_name": "inventory.categories.error_duplicate_name",
        "missing_owner_member": "inventory.form.error_missing_owner_member",
    }
    key = key_map.get(e.key, e.key)
    return HTTPException(status_code=e.http_status, detail=t_for(request, key, **e.params))


# ---------------------------------------------------------------------------
# Categories
# ---------------------------------------------------------------------------

@router.get("/categories", response_model=List[InventoryCategoryOut], summary="List categories")
async def list_categories(
    db: AsyncSession = Depends(get_db), user: User = Depends(require_api_permission("inventory", "read")),
):
    result = await db.execute(select(InventoryCategory).order_by(InventoryCategory.name))
    return result.scalars().all()


@router.post(
    "/categories", response_model=InventoryCategoryOut, status_code=status.HTTP_201_CREATED,
    summary="Create a category",
)
async def create_category_endpoint(
    payload: InventoryCategoryCreate, request: Request,
    db: AsyncSession = Depends(get_db), user: User = Depends(require_api_permission("inventory", "write")),
):
    try:
        category = await create_category(db, name=payload.name, description=payload.description)
    except ServiceError as e:
        raise _service_error_to_http(request, e)
    await db.commit()
    await db.refresh(category)
    return category


@router.put("/categories/{category_id}", response_model=InventoryCategoryOut, summary="Update a category")
async def update_category(
    category_id: str, payload: InventoryCategoryCreate,
    db: AsyncSession = Depends(get_db), user: User = Depends(require_api_permission("inventory", "write")),
):
    """No HTML counterpart exists for editing a category (only create/
    delete) -- API-only, so this stays router-local rather than moving
    into the shared service."""
    result = await db.execute(select(InventoryCategory).where(InventoryCategory.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    category.name = payload.name
    category.description = payload.description
    await db.commit()
    await db.refresh(category)
    return category


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a category")
async def delete_category_endpoint(
    category_id: str, db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission("inventory", "delete")),
):
    """Items in this category are NOT deleted -- their category_id is
    just cleared (ON DELETE SET NULL), so removing a category never
    loses inventory data."""
    category = await delete_category(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    await db.commit()


# ---------------------------------------------------------------------------
# Items
# ---------------------------------------------------------------------------

def _item_out(item: InventoryItem) -> InventoryItemOut:
    """InventoryItemOut needs the computed quantity_on_loan/available_quantity
    properties, which from_attributes picks up fine since they're plain
    @property on the model -- this helper just makes that explicit at
    call sites rather than relying on it implicitly everywhere."""
    return InventoryItemOut.model_validate(item)


async def _reload_item(db: AsyncSession, item_id: str) -> InventoryItem:
    """Re-fetches the item with everything InventoryItemOut needs
    eager-loaded, after a commit. Deliberately NOT db.refresh(item,
    attribute_names=["loans"]): that only refreshes the one named
    relationship, but a commit expires every attribute on the object,
    so a later access of a plain column (e.g. updated_at, touched by
    onupdate=func.now()) would still trigger an async-unsafe lazy load
    -- the exact "lazy-load crash" risk already documented elsewhere in
    this project. A full re-query sidesteps the issue entirely.
    """
    result = await db.execute(
        select(InventoryItem).options(selectinload(InventoryItem.loans)).where(InventoryItem.id == item_id)
    )
    return result.scalar_one()


@router.get("/items", response_model=List[InventoryItemOut], summary="List items")
async def list_items(
    category_id: Optional[str] = Query(None),
    is_borrowable: Optional[bool] = Query(None),
    include_retired: bool = Query(False, description="Include retired items (excluded by default)"),
    db: AsyncSession = Depends(get_db), user: User = Depends(require_api_permission("inventory", "read")),
):
    query = select(InventoryItem).options(selectinload(InventoryItem.loans)).order_by(InventoryItem.name)
    if not include_retired:
        query = query.where(InventoryItem.retired_at.is_(None))
    if category_id:
        query = query.where(InventoryItem.category_id == category_id)
    if is_borrowable is not None:
        query = query.where(InventoryItem.is_borrowable == is_borrowable)
    result = await db.execute(query)
    return [_item_out(item) for item in result.scalars().all()]


@router.get("/items/{item_id}", response_model=InventoryItemOut, summary="Get an item")
async def get_item(
    item_id: str, db: AsyncSession = Depends(get_db), user: User = Depends(require_api_permission("inventory", "read")),
):
    result = await db.execute(
        select(InventoryItem).options(selectinload(InventoryItem.loans)).where(InventoryItem.id == item_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return _item_out(item)


@router.post("/items", response_model=InventoryItemOut, status_code=status.HTTP_201_CREATED, summary="Create an item")
async def create_item_endpoint(
    payload: InventoryItemCreate, request: Request,
    db: AsyncSession = Depends(get_db), user: User = Depends(require_api_permission("inventory", "write")),
):
    try:
        item = await create_item(db, **payload.model_dump(), created_by_id=user.id)
    except ServiceError as e:
        raise _service_error_to_http(request, e)
    await db.commit()
    item = await _reload_item(db, item.id)
    return _item_out(item)


@router.put("/items/{item_id}", response_model=InventoryItemOut, summary="Update an item")
async def update_item_endpoint(
    item_id: str, payload: InventoryItemUpdate, request: Request,
    db: AsyncSession = Depends(get_db), user: User = Depends(require_api_permission("inventory", "write")),
):
    result = await db.execute(
        select(InventoryItem).options(selectinload(InventoryItem.loans)).where(InventoryItem.id == item_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    try:
        await update_item(db, item, **payload.model_dump())
    except ServiceError as e:
        raise _service_error_to_http(request, e)

    await db.commit()
    item = await _reload_item(db, item.id)
    return _item_out(item)


@router.post("/items/{item_id}/retire", response_model=InventoryItemOut, summary="Retire an item")
async def retire_item_endpoint(
    item_id: str, db: AsyncSession = Depends(get_db), user: User = Depends(require_api_permission("inventory", "write")),
):
    """Marks the item as no longer owned/in service without deleting
    it -- see InventoryItem.retired_at's docstring in app/models.py for
    why this exists as a separate action from DELETE."""
    result = await db.execute(
        select(InventoryItem).options(selectinload(InventoryItem.loans)).where(InventoryItem.id == item_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    await retire_item(db, item)
    await db.commit()
    item = await _reload_item(db, item.id)
    return _item_out(item)


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete an item")
async def delete_item(
    item_id: str, db: AsyncSession = Depends(get_db), user: User = Depends(require_api_permission("inventory", "delete")),
):
    """A genuine hard delete, for data-entry mistakes -- also deletes
    any loan history for this item (cascade). For an item that was
    real and is now sold/scrapped/lost, use retire instead so the
    financial and loan history survives."""
    result = await db.execute(select(InventoryItem).where(InventoryItem.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    await db.delete(item)
    await db.commit()


# ---------------------------------------------------------------------------
# Loans
# ---------------------------------------------------------------------------

@router.get("/loans", response_model=List[ItemLoanOut], summary="List loans (all items)")
async def list_all_loans(
    outstanding_only: bool = Query(True, description="Only loans not yet returned (default)"),
    db: AsyncSession = Depends(get_db), user: User = Depends(require_api_permission("inventory", "read")),
):
    """Cross-item view of who currently has what borrowed -- the board
    overview, not scoped to a single item."""
    query = select(ItemLoan).order_by(ItemLoan.borrowed_date.desc())
    if outstanding_only:
        query = query.where(ItemLoan.returned_date.is_(None))
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/items/{item_id}/loans", response_model=List[ItemLoanOut], summary="List loans for an item")
async def list_item_loans(
    item_id: str, db: AsyncSession = Depends(get_db), user: User = Depends(require_api_permission("inventory", "read")),
):
    result = await db.execute(
        select(ItemLoan).where(ItemLoan.item_id == item_id).order_by(ItemLoan.borrowed_date.desc())
    )
    return result.scalars().all()


@router.post(
    "/items/{item_id}/loans", response_model=ItemLoanOut, status_code=status.HTTP_201_CREATED,
    summary="Check out (borrow) some quantity of an item",
)
async def create_loan(
    item_id: str, payload: ItemLoanCreate, request: Request,
    db: AsyncSession = Depends(get_db), user: User = Depends(require_api_permission("inventory", "write")),
):
    result = await db.execute(
        select(InventoryItem).options(selectinload(InventoryItem.loans)).where(InventoryItem.id == item_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    try:
        loan = await checkout_loan(
            db, item, member_id=payload.member_id, quantity=payload.quantity,
            borrowed_date=payload.borrowed_date, fee_charged=payload.fee_charged,
            note=payload.note, created_by_id=user.id,
        )
    except ServiceError as e:
        raise _service_error_to_http(request, e)

    await db.commit()
    await db.refresh(loan)
    return loan


@router.post("/loans/{loan_id}/return", response_model=ItemLoanOut, summary="Mark a loan as returned")
async def return_loan_endpoint(
    loan_id: str, payload: ItemLoanReturn,
    db: AsyncSession = Depends(get_db), user: User = Depends(require_api_permission("inventory", "write")),
):
    result = await db.execute(select(ItemLoan).where(ItemLoan.id == loan_id))
    loan = result.scalar_one_or_none()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    if not await return_loan(db, loan, returned_date=payload.returned_date):
        raise HTTPException(status_code=400, detail="This loan was already marked as returned")
    await db.commit()
    await db.refresh(loan)
    return loan
