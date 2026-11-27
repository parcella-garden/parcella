"""Parcels, tenancies (member <-> parcel) and parcel cloud folders."""

import enum
from datetime import datetime, date
from typing import Optional, List
from sqlalchemy import String, Boolean, Date, DateTime, Text, Numeric, ForeignKey, Enum as SAEnum, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base
from app.models._common import new_uuid


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class ParcelStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    TERMINATED = "TERMINATED"
    DELETED = "DELETED"
    # Club-managed common area (paths, playground, etc.), issue #168 --
    # tracked as a real Parcel row (so its area_sqm is entered like any
    # other plot) but excluded from Area A (see app/area_utils.py) and
    # structurally never leased to a member. Freely switchable back to
    # ACTIVE if the club decides to lease it out after all.
    COMMUNAL = "COMMUNAL"


# ---------------------------------------------------------------------------
# Parcels
# ---------------------------------------------------------------------------

class Parcel(Base):
    __tablename__ = "parcels"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)

    # Plot number (e.g. "G093", "G26/27")
    plot_number: Mapped[str] = mapped_column(String(20), nullable=False, unique=True, index=True)

    # Area
    area_sqm: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)

    # GPS coordinates (optional, filled in by hand) -- Numeric(9,6): 3
    # integer digits + 6 decimals covers longitude's full -180..180
    # range at ~11cm precision, standard GPS storage convention.
    latitude: Mapped[Optional[float]] = mapped_column(Numeric(9, 6), nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Numeric(9, 6), nullable=True)

    # Status
    status: Mapped[ParcelStatus] = mapped_column(
        SAEnum(ParcelStatus), default=ParcelStatus.ACTIVE, nullable=False
    )

    # Termination (who terminated and when)
    termination_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Notes
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Audit
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    member_assignments: Mapped[List["MemberParcel"]] = relationship(
        "MemberParcel", back_populates="parcel"
    )
    metering_points: Mapped[List["MeteringPoint"]] = relationship(
        "MeteringPoint", back_populates="parcel"
    )
    cloud_folders: Mapped[List["ParcelCloudFolder"]] = relationship(
        "ParcelCloudFolder", back_populates="parcel",
        order_by="ParcelCloudFolder.created_at.desc()",
    )

    def __repr__(self) -> str:
        return f"<Parcel {self.plot_number}>"


# ---------------------------------------------------------------------------
# Assignment table Member <-> Parcel (m:n with metadata)
# ---------------------------------------------------------------------------

class MemberParcel(Base):
    """
    Connects members with parcels.
    Enables double gardens (one member, multiple parcels)
    as well as community gardens (multiple members, one parcel).
    """
    __tablename__ = "member_parcels"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    member_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("members.id", ondelete="CASCADE"), nullable=False, index=True
    )
    parcel_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("parcels.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Is this member's address used as the parcel's invoice address?
    is_invoice_address: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Assignment period
    assigned_from: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    assigned_until: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    member: Mapped["Member"] = relationship("Member", back_populates="parcel_assignments")
    parcel: Mapped["Parcel"] = relationship("Parcel", back_populates="member_assignments")

    @property
    def is_current(self) -> bool:
        """
        Whether this tenancy is still in effect today. Unlike
        Member.is_active (">="), this uses a strict ">": ending a
        tenancy sets assigned_until = today, and that tenant becomes
        former the same day, not the day before (see
        tests/test_members_signin_sheet.py::test_signin_sheet_excludes_former_residents).
        A future assigned_until (termination recorded, not yet in
        effect -- issue #130) still counts as current.

        A future assigned_from doesn't yet (ADR 0102): a parcel handed
        over ahead of time has its old tenants current until the
        handover date and the new ones only from then on -- otherwise
        both households would be billed in between. Such a tenancy is
        is_upcoming instead. SQL twin: app.database.current_tenant_filter().
        """
        today = date.today()
        return (
            (self.assigned_from is None or self.assigned_from <= today)
            and (self.assigned_until is None or self.assigned_until > today)
        )

    @property
    def is_upcoming(self) -> bool:
        """Starts in the future and hasn't been ended before it began."""
        return (
            self.assigned_from is not None and self.assigned_from > date.today()
            and not self.is_former
        )

    @property
    def is_former(self) -> bool:
        """Has actually ended (same strict boundary as is_current). The
        test for "may this tenancy hold is_invoice_address": an upcoming
        tenant must be able to (they're the next invoice recipient),
        a former one never (ADR 0058)."""
        return self.assigned_until is not None and self.assigned_until <= date.today()

    def overlaps_year(self, year: int) -> bool:
        """
        Whether this tenancy was in effect on at least one day of
        `year` -- the work-hours evaluation's notion of "tenant"
        (issue #239): a lease that ends partway through the year still
        owes that year's hours, unlike is_current, which only knows
        about today. Same strict ">" for assigned_until as is_current
        (an assigned_until of Jan 1 means the tenancy was already over
        on Jan 1). SQL twin: app.database.tenant_in_year_filter().
        """
        return (
            (self.assigned_from is None or self.assigned_from <= date(year, 12, 31))
            and (self.assigned_until is None or self.assigned_until > date(year, 1, 1))
        )

    __table_args__ = (
        UniqueConstraint("member_id", "parcel_id", name="uq_member_parcel"),
        # ADR 0035's original DB-level backstop here (dropped in
        # migration 0069, issue #172) required assigned_until IS NULL,
        # which also rejected a future-dated termination (notice given,
        # not yet moved out) even though that tenant is still current
        # per is_current/ADR 0052. A CHECK constraint can't reference
        # "today" safely (it isn't re-evaluated as time passes), so
        # there's no equivalent immutable check for "is_current" --
        # correctness now relies on every read path using is_current
        # (or current_tenant_filter() in SQL) instead of trusting a
        # stored is_invoice_address in isolation. See ADR 0058.
    )


# ---------------------------------------------------------------------------
# Cloud storage: per-parcel folder path in a connected cloud backend
# (Nextcloud today). See app/cloud_storage.py and app/parcel_cloud_folders.py.
# ---------------------------------------------------------------------------

class ParcelCloudFolder(Base):
    """
    The cloud-storage folder path currently assigned to a parcel (e.g.
    a Nextcloud path holding the current tenants' lease paperwork).

    Scoped to the parcel, not to a single MemberParcel row: a parcel can
    have several co-tenants at once (couples, families), each with their
    own MemberParcel row for the same lease period, and this folder is
    shared by all of them -- one folder per tenancy period, not one per
    person.

    Only one row per parcel should have is_active=True at a time; older
    rows are kept (is_active=False) as history rather than deleted, same
    principle as ended MemberParcel assignments. is_active is flipped to
    False automatically when the parcel's last active resident's tenancy
    ends (see app.parcel_cloud_folders.deactivate_if_vacant) -- so a
    fresh set of tenants moving in after a full turnover never inherits
    the previous tenants' folder; a board member must deliberately set a
    new one.
    """
    __tablename__ = "parcel_cloud_folders"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    parcel_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("parcels.id", ondelete="CASCADE"), nullable=False, index=True
    )
    relative_path: Mapped[str] = mapped_column(String(500), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    set_by_user_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    deactivated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    # Scheduled switch for a parcel handed over on a future date (ADR
    # 0102): the active folder retires on active_until; a not-yet-active
    # row (is_active False, deactivated_at NULL) takes over on
    # active_from. app.parcel_cloud_folders.apply_scheduled_folder_switches
    # carries both out.
    active_from: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    active_until: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    parcel: Mapped["Parcel"] = relationship("Parcel", back_populates="cloud_folders")
    set_by_user: Mapped[Optional["User"]] = relationship("User")

    __table_args__ = (
        Index(
            "uq_parcel_cloud_folders_one_active_per_parcel",
            "parcel_id", unique=True,
            postgresql_where=(is_active == True),  # noqa: E712
        ),
    )
