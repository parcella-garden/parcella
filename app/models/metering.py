"""Water and electricity metering: points, meters, readings, prices."""

import enum
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List
from sqlalchemy import String, Integer, Boolean, Date, DateTime, Text, Numeric, ForeignKey, Enum as SAEnum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func, text

from app.database import Base
from app.models._common import new_uuid


# ---------------------------------------------------------------------------
# Metering: generic module for water AND electricity meters
#
# A MeteringPoint has a "medium" (WATER or ELECTRICITY) and a "type"
# (main meter, parcel, club connection). The consumption logic is
# identical for both media -- only unit, display rounding, and icon
# differ (see app/routers/metering.py).
# ---------------------------------------------------------------------------

class MeteringMedium(str, enum.Enum):
    WATER = "WATER"
    ELECTRICITY = "ELECTRICITY"


class MeteringPointType(str, enum.Enum):
    MAIN_METER = "MAIN_METER"  # Handover point from the public utility
    PARCEL = "PARCEL"          # Connection at a parcel
    CLUB = "CLUB"              # Club-owned connection point (clubhouse, wash area, etc.)


class MeteringPoint(Base):
    """
    A metering point for a medium (water or electricity). Either
    coupled to a parcel, a club-owned connection point, or the main
    meter for the overall supply from the public utility.

    A parcel can have both a water and an electricity MeteringPoint
    (two rows, distinguished via "medium").
    """
    __tablename__ = "metering_points"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    medium: Mapped[MeteringMedium] = mapped_column(SAEnum(MeteringMedium), nullable=False)
    type: Mapped[MeteringPointType] = mapped_column(SAEnum(MeteringPointType), nullable=False)

    parcel_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("parcels.id", ondelete="SET NULL"), nullable=True, index=True
    )
    # For MAIN_METER/CLUB metering points (no parcel): free-form name.
    label: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # Issue #336: a point without supply for a while (water shut off for
    # the winter, a plot's power disconnected) is switched off rather
    # than deleted (ADR 0005) -- it drops out of reading entry and the
    # "readings missing" count, its history stays. Independent of the
    # meter's own is_active, which only tracks meter exchanges.
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true", nullable=False)
    inactive_since: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    # Issue #341: multiplier between what the display shows and what was
    # really consumed -- e.g. x20 on a bulk buyer's current-transformer
    # main meter. Readings stay the raw display values; the metering
    # module's consumption is (reading - previous) * factor. Metering
    # only: invoices and other modules never see it (ADR 0138).
    factor: Mapped[Decimal] = mapped_column(
        Numeric(10, 4), default=Decimal("1"), server_default="1", nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    parcel: Mapped[Optional["Parcel"]] = relationship("Parcel", back_populates="metering_points")
    meters: Mapped[List["Meter"]] = relationship(
        "Meter", back_populates="metering_point", cascade="all, delete-orphan"
    )

    @property
    def display_name(self) -> str:
        if self.parcel:
            return f"Parcel {self.parcel.plot_number}"
        return self.label or "Unbenannter Zählpunkt"

    @property
    def current_meter(self) -> Optional["Meter"]:
        active = [z for z in self.meters if z.is_active]
        return active[0] if active else None

    def __repr__(self) -> str:
        return f"<MeteringPoint {self.medium.value}:{self.display_name}>"


class Meter(Base):
    """
    The physical meter (water meter or electricity meter) on a
    MeteringPoint. When swapped, the old meter is deactivated
    (removed_at set) and a new one with a new number is created -- the
    history stays fully intact.

    `number` is a free-text label, not an enforced-unique identifier
    (see ADR 0082) -- a meter's real identity is its row id. An
    earlier attempt (ADR 0081) scoped a uniqueness constraint per
    medium instead of removing it; reverted, see ADR 0082.
    """
    __tablename__ = "meters"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    metering_point_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("metering_points.id", ondelete="CASCADE"), nullable=False, index=True
    )
    number: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    calibrated_until: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True,
        comment="Year until which calibration is valid (water typically +6, electricity typically +8 years)"
    )
    installed_at: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    removed_at: Mapped[Optional[date]] = mapped_column(Date, nullable=True, comment="NULL = still installed")
    initial_reading: Mapped[float] = mapped_column(Numeric(12, 1), default=0, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    metering_point: Mapped["MeteringPoint"] = relationship("MeteringPoint", back_populates="meters")
    readings: Mapped[List["MeterReading"]] = relationship(
        "MeterReading", back_populates="meter", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Meter {self.number}>"


class MeterReading(Base):
    """
    An annual reading of a meter (water or electricity).
    """
    __tablename__ = "meter_readings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    meter_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("meters.id", ondelete="CASCADE"), nullable=False, index=True
    )
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    reading: Mapped[float] = mapped_column(Numeric(12, 1), nullable=False)
    recorded_by_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    meter: Mapped["Meter"] = relationship("Meter", back_populates="readings")
    recorded_by: Mapped[Optional["User"]] = relationship("User")

    __table_args__ = (
        UniqueConstraint("meter_id", "year", name="uq_meter_year"),
    )


class MeteringPriceConfiguration(Base):
    """
    Annual price per unit (EUR per m³ or per kWh) for one medium --
    drives the water_usage/electricity_usage invoice pricing modes
    (app/invoice_generation.py), same "computed automatically" pattern
    as WorkHoursConfiguration's rate_per_hour_eur and the insurance
    module's premiums. Historized per year like WorkHoursConfiguration
    (ADR 0005): old years' prices must stay intact for past runs.

    Restored (see docs/ADR/0056's second Update note) after a brief
    revert to manual per-invoice pricing -- the user confirmed they
    actually want the price set once per year here, with the item
    form's price field hidden/computed automatically, same as
    insurance_cost/work_hours_shortfall.
    """
    __tablename__ = "metering_price_configuration"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    medium: Mapped[MeteringMedium] = mapped_column(SAEnum(MeteringMedium), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    price_per_unit: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False)
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    __table_args__ = (
        UniqueConstraint("medium", "year", name="uq_metering_price_medium_year"),
    )

    def __repr__(self) -> str:
        return f"<MeteringPriceConfiguration {self.medium} {self.year}: {self.price_per_unit}€>"
