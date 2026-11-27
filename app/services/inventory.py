"""
Shared inventory business logic, called by both app/routers/inventory.py
(HTML) and app/routers/api_inventory.py (API) -- see ADR 0070.

Pure validation/CRUD duplication here, no audit trail or notifications
involved on either side before or after this extraction -- the finding
was category-uniqueness, owner-type validation, and loan-quantity rules
each independently reimplemented, not a data-integrity gap.
"""
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import InventoryCategory, InventoryItem, InventoryOwnerType, ItemLoan
from app.services.errors import ServiceError


async def create_category(db: AsyncSession, *, name: str, description: Optional[str] = None) -> InventoryCategory:
    """ServiceError.key here is a short code ("missing_name",
    "duplicate_name"), not a full translation key -- the HTML template
    (inventory/categories.html) already maps these exact codes to their
    own t() lookups (inventory.categories.error_<code>); kept as-is
    rather than changed to a full key, to avoid a template edit for a
    pattern that already works."""
    name = (name or "").strip()
    if not name:
        raise ServiceError("missing_name", http_status=400)

    existing = await db.execute(select(InventoryCategory).where(InventoryCategory.name == name))
    if existing.scalar_one_or_none():
        raise ServiceError("duplicate_name", http_status=400)

    category = InventoryCategory(name=name, description=(description or "").strip() or None)
    db.add(category)
    await db.flush()
    return category


async def delete_category(db: AsyncSession, category_id: str) -> Optional[InventoryCategory]:
    """Items in this category are NOT deleted -- their category_id is
    just cleared (ON DELETE SET NULL), so removing a category never
    loses inventory data."""
    result = await db.execute(select(InventoryCategory).where(InventoryCategory.id == category_id))
    category = result.scalar_one_or_none()
    if category:
        await db.delete(category)
        await db.flush()
    return category


def validate_owner(owner_type: str, owner_member_id: Optional[str]) -> None:
    """Short code, same reasoning as create_category above -- maps to
    inventory/form.html's own error == 'missing_owner_member' branch."""
    if owner_type == InventoryOwnerType.MEMBER.value and not owner_member_id:
        raise ServiceError("missing_owner_member", http_status=400)


def _owner_member_id(owner_type: str, owner_member_id: Optional[str]) -> Optional[str]:
    return owner_member_id if owner_type == InventoryOwnerType.MEMBER.value else None


async def create_item(
    db: AsyncSession, *, name: str, description: Optional[str], category_id: Optional[str],
    owner_type: str, owner_member_id: Optional[str], storage_location: Optional[str],
    purchase_date: Optional[date], purchase_price: Optional[Decimal], current_value: Optional[Decimal],
    current_value_updated_at: Optional[date], replacement_cost: Optional[Decimal],
    quantity_total: int, is_borrowable: bool, default_loan_fee: Optional[Decimal],
    notes: Optional[str], created_by_id: str,
) -> InventoryItem:
    name = (name or "").strip()
    if not name:
        raise ServiceError("missing_name", http_status=400)
    validate_owner(owner_type, owner_member_id)

    item = InventoryItem(
        name=name, description=description, category_id=category_id,
        owner_type=InventoryOwnerType(owner_type),
        owner_member_id=_owner_member_id(owner_type, owner_member_id),
        storage_location=storage_location,
        purchase_date=purchase_date, purchase_price=purchase_price,
        current_value=current_value, current_value_updated_at=current_value_updated_at,
        replacement_cost=replacement_cost, quantity_total=quantity_total, is_borrowable=is_borrowable,
        default_loan_fee=default_loan_fee, notes=notes, created_by_id=created_by_id,
    )
    db.add(item)
    await db.flush()
    return item


async def update_item(
    db: AsyncSession, item: InventoryItem, *, name: str, description: Optional[str], category_id: Optional[str],
    owner_type: str, owner_member_id: Optional[str], storage_location: Optional[str],
    purchase_date: Optional[date], purchase_price: Optional[Decimal], current_value: Optional[Decimal],
    current_value_updated_at: Optional[date], replacement_cost: Optional[Decimal],
    quantity_total: int, is_borrowable: bool, default_loan_fee: Optional[Decimal], notes: Optional[str],
) -> InventoryItem:
    name = (name or "").strip()
    if not name:
        raise ServiceError("missing_name", http_status=400)
    validate_owner(owner_type, owner_member_id)

    item.name = name
    item.description = description
    item.category_id = category_id
    item.owner_type = InventoryOwnerType(owner_type)
    item.owner_member_id = _owner_member_id(owner_type, owner_member_id)
    item.storage_location = storage_location
    item.purchase_date = purchase_date
    item.purchase_price = purchase_price
    item.current_value = current_value
    item.current_value_updated_at = current_value_updated_at
    item.replacement_cost = replacement_cost
    item.quantity_total = quantity_total
    item.is_borrowable = is_borrowable
    item.default_loan_fee = default_loan_fee
    item.notes = notes
    await db.flush()
    return item


async def retire_item(db: AsyncSession, item: InventoryItem) -> None:
    """Marks the item as no longer owned/in service without deleting it
    -- see InventoryItem.retired_at's docstring in app/models/ for why
    this exists as a separate action from delete."""
    item.retired_at = datetime.now(timezone.utc)
    await db.flush()


async def checkout_loan(
    db: AsyncSession, item: InventoryItem, *, member_id: str, quantity: int,
    borrowed_date: Optional[date], fee_charged: Optional[Decimal], note: Optional[str], created_by_id: str,
) -> ItemLoan:
    if not item.is_borrowable:
        raise ServiceError("inventory.errors.item_not_borrowable", http_status=400)
    if not member_id:
        raise ServiceError("inventory.errors.member_required", http_status=400)
    if quantity < 1 or quantity > item.available_quantity:
        raise ServiceError(
            "inventory.errors.insufficient_quantity", http_status=400,
            available=item.available_quantity, total=item.quantity_total,
        )

    loan = ItemLoan(
        item_id=item.id, member_id=member_id, quantity=quantity,
        borrowed_date=borrowed_date or date.today(),
        fee_charged=fee_charged if fee_charged is not None else item.default_loan_fee,
        note=note, created_by_id=created_by_id,
    )
    db.add(loan)
    await db.flush()
    return loan


async def return_loan(db: AsyncSession, loan: ItemLoan, *, returned_date: Optional[date] = None) -> bool:
    """Returns False (no-op) if the loan was already marked returned --
    caller decides whether that's an error (API) or silently fine (HTML,
    matching its pre-extraction behavior)."""
    if loan.returned_date is not None:
        return False
    loan.returned_date = returned_date or date.today()
    await db.flush()
    return True
