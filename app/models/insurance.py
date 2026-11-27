"""Property and accident insurance."""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Integer, Boolean, DateTime, Numeric, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base
from app.models._common import new_uuid


# ---------------------------------------------------------------------------
# Insurance module: property and accident insurance per parcel
# ---------------------------------------------------------------------------

class PropertyInsurancePackage(Base):
    """
    A selectable property insurance package for a given year (e.g.
    "Package 1" = 40 €, "Package 2" = 60 € etc.). The number and
    amounts of packages are freely configurable and can change yearly.
    """
    __tablename__ = "property_insurance_packages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    amount_eur: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<PropertyInsurancePackage {self.year} {self.name}: {self.amount_eur}€>"


class InsuranceConfiguration(Base):
    """
    Annual configuration of the accident insurance amounts. Property
    insurance is configured separately via PropertyInsurancePackage
    (several packages per year); accident insurance has exactly one
    base and additional amount per year.
    """
    __tablename__ = "insurance_configuration"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    year: Mapped[int] = mapped_column(Integer, nullable=False, unique=True, index=True)
    accident_base_amount_eur: Mapped[float] = mapped_column(
        Numeric(8, 2), nullable=False,
        comment="Covers all members in the same household (same address)"
    )
    accident_additional_amount_eur: Mapped[float] = mapped_column(
        Numeric(8, 2), nullable=False,
        comment="Per additional co-insured person outside the household"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<InsuranceConfiguration {self.year}>"


class ParcelInsurance(Base):
    """
    A parcel's insurance status for a given year: property insurance
    (optional, with a chosen package) and accident insurance (optional,
    the base amount covers the automatically detected household --
    see household_grouping() in app/insurance_utils.py).

    has_accident_insurance is the master switch for accident insurance
    being active on this parcel at all. Within that, household_members
    and additional_persons independently control who's actually covered
    (issue #204): household_members is opt-OUT (seeded with the whole
    detected household by default, e.g. so the leaser specifically can
    be removed while staying billed for a named additional person, e.g.
    an outside relative); additional_persons is opt-IN as before. The
    base fee applies once if household_members is non-empty, same as
    additional_persons already governs the per-head extra fee.
    """
    __tablename__ = "parcel_insurance"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    parcel_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("parcels.id", ondelete="CASCADE"), nullable=False, index=True
    )
    year: Mapped[int] = mapped_column(Integer, nullable=False)

    has_property_insurance: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    property_package_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("property_insurance_packages.id", ondelete="SET NULL"), nullable=True
    )

    has_accident_insurance: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    parcel: Mapped["Parcel"] = relationship("Parcel")
    property_package: Mapped[Optional["PropertyInsurancePackage"]] = relationship("PropertyInsurancePackage")
    household_members: Mapped[List["AccidentInsuranceHouseholdMember"]] = relationship(
        "AccidentInsuranceHouseholdMember", back_populates="parcel_insurance", cascade="all, delete-orphan"
    )
    additional_persons: Mapped[List["AccidentInsuranceAdditionalPerson"]] = relationship(
        "AccidentInsuranceAdditionalPerson", back_populates="parcel_insurance", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("parcel_id", "year", name="uq_parcel_insurance_year"),
    )

    def __repr__(self) -> str:
        return f"<ParcelInsurance {self.parcel_id} {self.year}>"


class AccidentInsuranceHouseholdMember(Base):
    """
    A household member explicitly covered by a parcel's accident
    insurance for a year. Seeded with the whole auto-detected household
    (household_grouping() in app/insurance_utils.py) when a
    ParcelInsurance row is first created, so it defaults to "everyone
    covered" -- but each member can be individually removed, e.g. the
    leaser opts out for themselves while a named additional person
    stays insured (issue #204). Opt-OUT, symmetric to
    AccidentInsuranceAdditionalPerson's opt-IN for people outside the
    household.
    """
    __tablename__ = "accident_insurance_household_members"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    parcel_insurance_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("parcel_insurance.id", ondelete="CASCADE"), nullable=False, index=True
    )
    member_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("members.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    parcel_insurance: Mapped["ParcelInsurance"] = relationship(
        "ParcelInsurance", back_populates="household_members"
    )
    member: Mapped["Member"] = relationship("Member")

    __table_args__ = (
        UniqueConstraint("parcel_insurance_id", "member_id", name="uq_accident_household_member"),
    )

    def __repr__(self) -> str:
        return f"<AccidentInsuranceHouseholdMember {self.parcel_insurance_id} {self.member_id}>"


class AccidentInsuranceAdditionalPerson(Base):
    """
    A member added to a parcel's accident insurance for an extra fee,
    in addition to the automatically detected household (e.g. a
    resident who doesn't live at the same address as the parcel's
    other residents).
    """
    __tablename__ = "accident_insurance_additional_persons"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    parcel_insurance_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("parcel_insurance.id", ondelete="CASCADE"), nullable=False, index=True
    )
    member_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("members.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    parcel_insurance: Mapped["ParcelInsurance"] = relationship(
        "ParcelInsurance", back_populates="additional_persons"
    )
    member: Mapped["Member"] = relationship("Member")

    __table_args__ = (
        UniqueConstraint("parcel_insurance_id", "member_id", name="uq_insurance_member"),
    )
