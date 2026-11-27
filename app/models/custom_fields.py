"""Custom fields on members and parcels, defined by a system admin (issue #443, ADR 0147)."""

import enum
from datetime import date, datetime
from typing import List, Optional

from sqlalchemy import (
    Boolean, CheckConstraint, Date, DateTime, Enum as SAEnum, ForeignKey, Integer, JSON, Numeric,
    String, Text, UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base
from app.models._common import new_uuid


class CustomFieldTarget(str, enum.Enum):
    """What a custom field is attached to."""
    MEMBER = "MEMBER"
    PARCEL = "PARCEL"


class CustomFieldKind(str, enum.Enum):
    TEXT = "TEXT"
    LONG_TEXT = "LONG_TEXT"
    NUMBER = "NUMBER"
    DATE = "DATE"
    CHECKBOX = "CHECKBOX"
    CHOICE = "CHOICE"
    # A yes/no whose sub-fields (parent_id = this field) only apply when
    # it is ticked: "has a pool" -> diameter, height, removed in winter.
    GROUP = "GROUP"


class CustomField(Base):
    """One field definition. Groups are fields of kind GROUP; a sub-field
    points at its group via parent_id (one level only). Archived fields and
    their values are just hidden; deleting removes them for good (ADR 0147)."""
    __tablename__ = "custom_fields"
    __table_args__ = (UniqueConstraint("target", "key", name="uq_custom_fields_target_key"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    target: Mapped[CustomFieldTarget] = mapped_column(SAEnum(CustomFieldTarget), nullable=False, index=True)
    parent_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("custom_fields.id", ondelete="CASCADE"), nullable=True, index=True
    )
    # Stable machine name (slug of the first label), for the API and CSV;
    # the label can change, the key doesn't.
    key: Mapped[str] = mapped_column(String(80), nullable=False)
    label: Mapped[str] = mapped_column(String(200), nullable=False)
    help_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    kind: Mapped[CustomFieldKind] = mapped_column(SAEnum(CustomFieldKind), nullable=False)
    unit: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # NUMBER only, e.g. "m²"
    options: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)  # CHOICE only
    required: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false", nullable=False)
    position: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    archived_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    children: Mapped[List["CustomField"]] = relationship(
        "CustomField", back_populates="parent", order_by="CustomField.position",
    )
    parent: Mapped[Optional["CustomField"]] = relationship(
        "CustomField", back_populates="children", remote_side="CustomField.id",
    )


class CustomFieldValue(Base):
    """A member's or parcel's value for one field -- exactly one of
    member_id / parcel_id is set, one typed column per kind (as in
    ProcessField). A GROUP's yes/no is a value_bool row like a CHECKBOX."""
    __tablename__ = "custom_field_values"
    __table_args__ = (
        UniqueConstraint("field_id", "member_id", name="uq_custom_field_values_member"),
        UniqueConstraint("field_id", "parcel_id", name="uq_custom_field_values_parcel"),
        CheckConstraint("(member_id IS NULL) <> (parcel_id IS NULL)", name="ck_custom_field_values_one_owner"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    field_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("custom_fields.id", ondelete="CASCADE"), nullable=False, index=True
    )
    member_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("members.id", ondelete="CASCADE"), nullable=True, index=True
    )
    parcel_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("parcels.id", ondelete="CASCADE"), nullable=True, index=True
    )
    value_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    value_number: Mapped[Optional[float]] = mapped_column(Numeric(14, 2), nullable=True)
    value_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    value_bool: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    field: Mapped["CustomField"] = relationship("CustomField")
