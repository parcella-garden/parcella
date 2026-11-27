"""Inventory: categories, items, loans."""

import enum
from datetime import datetime, date
from typing import Optional, List
from sqlalchemy import String, Integer, Boolean, Date, DateTime, Text, Numeric, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base
from app.models._common import new_uuid


# ---------------------------------------------------------------------------
# Inventory module: what the club owns (and what members store on club
# property), plus a lending system for borrowable items.
# ---------------------------------------------------------------------------

class InventoryOwnerType(str, enum.Enum):
    CLUB = "CLUB"
    MEMBER = "MEMBER"


class InventoryCategory(Base):
    """
    A freely-created grouping for inventory items (e.g. "Playground",
    "Fences", "Locks & Keys", "Water Infrastructure") -- deliberately
    NOT a fixed enum, since the original request was explicit that
    these need to be configurable by the club itself, not by a code
    change. Same lookup-table shape as ClubRole.
    """
    __tablename__ = "inventory_categories"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    items: Mapped[List["InventoryItem"]] = relationship("InventoryItem", back_populates="category")

    def __repr__(self) -> str:
        return f"<InventoryCategory {self.name!r}>"


class InventoryItem(Base):
    """
    A thing the club owns, or a thing a member owns personally but
    stores on club property (see owner_type/owner_member_id) -- both
    get the same financial fields (purchase price, current value,
    replacement cost), per explicit product decision: personally-owned
    items stored here are still useful to have on record for
    insurance/liability purposes, not just club-owned assets.

    quantity_total is how many physical units of this item exist (e.g.
    "3" for three wheelbarrows bought together and tracked as one
    entry rather than three separate rows) -- see
    available_quantity/is_available below for how loans reduce this.

    retired_at marks an item as no longer owned/in service without
    deleting it -- financial and loan history for a real asset
    register needs to survive disposal, not disappear with it. A
    genuinely mistaken entry can still be hard-deleted; retirement is
    for "we sold/scrapped/lost this," not for undoing data-entry
    errors.
    """
    __tablename__ = "inventory_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    category_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("inventory_categories.id", ondelete="SET NULL"), nullable=True, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    owner_type: Mapped[InventoryOwnerType] = mapped_column(
        SAEnum(InventoryOwnerType), default=InventoryOwnerType.CLUB, nullable=False
    )
    owner_member_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("members.id", ondelete="SET NULL"), nullable=True,
        comment="Set only when owner_type = MEMBER"
    )

    storage_location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    purchase_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    purchase_price: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    current_value: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 2), nullable=True,
        comment="Manually entered/updated -- no automatic depreciation calculation, by design"
    )
    current_value_updated_at: Mapped[Optional[date]] = mapped_column(
        Date, nullable=True, comment="When current_value was last checked/updated, so staleness is visible"
    )
    replacement_cost: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)

    quantity_total: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_borrowable: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    default_loan_fee: Mapped[Optional[float]] = mapped_column(
        Numeric(8, 2), nullable=True, comment="Suggested fee when checking this item out; editable per loan"
    )

    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    retired_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    category: Mapped[Optional["InventoryCategory"]] = relationship("InventoryCategory", back_populates="items")
    owner_member: Mapped[Optional["Member"]] = relationship("Member", foreign_keys=[owner_member_id])
    created_by: Mapped[Optional["User"]] = relationship("User")
    loans: Mapped[List["ItemLoan"]] = relationship(
        "ItemLoan", back_populates="item", cascade="all, delete-orphan"
    )

    @property
    def quantity_on_loan(self) -> int:
        return sum(loan.quantity for loan in self.loans if loan.returned_date is None)

    @property
    def available_quantity(self) -> int:
        return max(0, self.quantity_total - self.quantity_on_loan)

    def __repr__(self) -> str:
        return f"<InventoryItem {self.name!r}>"


class ItemLoan(Base):
    """
    One borrowing of (some quantity of) an item by a member.
    returned_date IS NULL means it's still checked out. quantity lets
    one loan cover more than one unit of an item at once (e.g.
    borrowing 2 of the club's 5 tents for a weekend).
    """
    __tablename__ = "item_loans"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    item_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("inventory_items.id", ondelete="CASCADE"), nullable=False, index=True
    )
    member_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("members.id", ondelete="CASCADE"), nullable=False, index=True
    )
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    borrowed_date: Mapped[date] = mapped_column(Date, nullable=False)
    returned_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    fee_charged: Mapped[Optional[float]] = mapped_column(Numeric(8, 2), nullable=True)
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_by_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    item: Mapped["InventoryItem"] = relationship("InventoryItem", back_populates="loans")
    member: Mapped["Member"] = relationship("Member")
    created_by: Mapped[Optional["User"]] = relationship("User")

    def __repr__(self) -> str:
        status = "returned" if self.returned_date else "outstanding"
        return f"<ItemLoan {self.item_id} x{self.quantity} ({status})>"
