"""Work hours: configuration, club roles, sponsorships, transfers, sessions, tasks."""

import enum
from datetime import datetime, date, timedelta
from typing import Optional, List
from sqlalchemy import String, Integer, Boolean, Date, DateTime, Text, Numeric, ForeignKey, Enum as SAEnum, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base
from app.models._common import new_uuid


# ---------------------------------------------------------------------------
# Work hours configuration (year-based)
# ---------------------------------------------------------------------------

class WorkHoursMode(str, enum.Enum):
    PER_PARCEL = "PER_PARCEL"    # Hours apply per parcel (default)
    PER_MEMBER = "PER_MEMBER"    # Hours apply per member


class WorkHoursConfiguration(Base):
    """
    Annual configuration of the required work hours.
    Historized -- old values are kept for evaluating past years.
    """
    __tablename__ = "work_hours_configuration"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    year: Mapped[int] = mapped_column(Integer, nullable=False, unique=True, index=True)
    hours_required: Mapped[float] = mapped_column(Numeric(5, 1), nullable=False)
    rate_per_hour_eur: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False)
    mode: Mapped[WorkHoursMode] = mapped_column(
        SAEnum(WorkHoursMode), default=WorkHoursMode.PER_PARCEL, nullable=False
    )
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<WorkHoursConfiguration {self.year}: {self.hours_required}h @ {self.rate_per_hour_eur}€>"


# ---------------------------------------------------------------------------
# Club roles (extended board, etc.)
# ---------------------------------------------------------------------------

class ExemptionReason(str, enum.Enum):
    BOARD = "BOARD"
    EXTENDED_BOARD = "EXTENDED_BOARD"
    ILLNESS = "ILLNESS"
    AGE = "AGE"
    OTHER = "OTHER"


class ClubRole(Base):
    """
    Roles within the club (board, extended board, assessor, etc.).
    Separate from the app's user system (UserRole) -- this is about
    club offices, not access permissions.
    """
    __tablename__ = "club_roles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    hours_exempt: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    exemption_reason: Mapped[Optional[ExemptionReason]] = mapped_column(
        SAEnum(ExemptionReason), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    assignments: Mapped[List["MemberClubRole"]] = relationship(
        "MemberClubRole", back_populates="club_role"
    )

    def __repr__(self) -> str:
        return f"<ClubRole {self.name}>"


class MemberClubRole(Base):
    """
    Assignment of Member -> ClubRole for a given year.
    The exemption always applies to the entire calendar year (even if
    the role is relinquished partway through the year).
    """
    __tablename__ = "member_club_roles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    member_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("members.id", ondelete="CASCADE"), nullable=False, index=True
    )
    club_role_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("club_roles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    valid_from: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    valid_until: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    member: Mapped["Member"] = relationship("Member")
    club_role: Mapped["ClubRole"] = relationship("ClubRole", back_populates="assignments")

    __table_args__ = (
        UniqueConstraint("member_id", "club_role_id", "year", name="uq_member_club_role_year"),
    )


# ---------------------------------------------------------------------------
# Sponsorships
# ---------------------------------------------------------------------------

class Sponsorship(Base):
    """
    A member takes on sponsorship of an area (e.g. hedge, playground).
    The sponsorship counts as a flat fulfillment of required work hours.
    """
    __tablename__ = "sponsorships"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    member_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("members.id", ondelete="SET NULL"), nullable=True, index=True
    )
    area: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    credited_hours: Mapped[float] = mapped_column(
        Numeric(5, 1), nullable=False,
        comment="Flat hours credited per year"
    )
    valid_from: Mapped[Optional[date]] = mapped_column(
        Date, nullable=True, comment="NULL = not yet claimed/scheduled"
    )
    valid_until: Mapped[Optional[date]] = mapped_column(Date, nullable=True, comment="NULL = still ongoing")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    member: Mapped[Optional["Member"]] = relationship("Member")

    def __repr__(self) -> str:
        return f"<Sponsorship {self.area} → {self.member_id}>"


# ---------------------------------------------------------------------------
# Work Sessions
# ---------------------------------------------------------------------------

class SessionType(str, enum.Enum):
    STANDARD = "STANDARD"    # Scheduled date, signup possible
    SPECIAL = "SPECIAL"      # Spontaneous/unplanned (painting a garden bench, etc.)


class HoursTransfer(Base):
    """
    A member gives some of their work hours for a year to another member
    (issue #243) -- e.g. someone who already did more than required helps
    out a neighbour. Counted in calculate_hours_for_member() as +hours
    for the receiver and -hours for the giver, so both evaluation modes
    and invoicing see it without special cases. Only the giver's surplus
    for that year can be given (checked when the transfer is created,
    app/services/work_hours.py:create_hours_transfer). A wrong entry is
    deleted, not historized -- it's a correction, not club history.
    See docs/ADR/0094.
    """
    __tablename__ = "hours_transfers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    giver_member_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("members.id", ondelete="CASCADE"), nullable=False, index=True
    )
    receiver_member_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("members.id", ondelete="CASCADE"), nullable=False, index=True
    )
    year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    hours: Mapped[float] = mapped_column(Numeric(5, 1), nullable=False)
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_by_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    giver: Mapped["Member"] = relationship("Member", foreign_keys=[giver_member_id])
    receiver: Mapped["Member"] = relationship("Member", foreign_keys=[receiver_member_id])
    created_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[created_by_id])

    __table_args__ = (
        CheckConstraint("hours > 0", name="ck_hours_transfers_positive"),
        CheckConstraint("giver_member_id <> receiver_member_id", name="ck_hours_transfers_not_self"),
    )

    def __repr__(self) -> str:
        return f"<HoursTransfer {self.year} {self.hours}h>"


class ParticipationStatus(str, enum.Enum):
    REGISTERED = "REGISTERED"    # Signed up
    ATTENDED = "ATTENDED"        # Showed up, hours get credited
    NO_SHOW = "NO_SHOW"          # Signed up but didn't show


class WorkSession(Base):
    """
    A scheduled or spontaneous work session in the club.
    """
    __tablename__ = "work_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    type: Mapped[SessionType] = mapped_column(
        SAEnum(SessionType), default=SessionType.STANDARD, nullable=False
    )
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    time_from: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)   # "08:00"
    time_until: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)  # "12:00"
    max_participants: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    hours_per_participant: Mapped[Optional[float]] = mapped_column(
        Numeric(4, 1), nullable=True,
        comment="Default value; can be overridden per participation"
    )
    # Issue: public self-service signup (app/routers/api_public.py) had
    # no notion of "too close to / after the event" -- NULL means only
    # the baseline "date hasn't passed yet" rule applies (see
    # public_signup_open below). Deliberately public-signup-only: a
    # board member adding a participant in Parcella itself is unaffected
    # (that flow normally records attendance *after* a session).
    signup_deadline_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    # "Mark reviewed" (ADR 0079 follow-up): a board member has looked at
    # this session's participants and wants the "New" badges/count to
    # stop showing the ones they've already seen. NULL = never reviewed,
    # the 14-day rolling window alone applies. A participation added
    # AFTER this timestamp still counts as new -- reviewing clears what
    # exists so far, it doesn't suppress future sign-ups.
    signups_reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    participations: Mapped[List["SessionParticipation"]] = relationship(
        "SessionParticipation", back_populates="session", cascade="all, delete-orphan"
    )
    created_by: Mapped[Optional["User"]] = relationship("User")

    @property
    def available_spots(self) -> Optional[int]:
        if self.max_participants is None:
            return None
        registered = sum(1 for t in self.participations if t.status != ParticipationStatus.NO_SHOW)
        return max(0, self.max_participants - registered)

    @property
    def public_signup_open(self) -> bool:
        """Whether app/routers/api_public.py's public self-service
        signup still accepts registrations for this session -- checked
        both when listing upcoming sessions and again at submit time
        (defense in depth: a stale page shouldn't be able to sneak a
        signup through after the window closes). Does NOT apply to
        staff adding a participant in Parcella itself, which normally
        records attendance after the fact and must keep working for
        past sessions."""
        today = date.today()
        if self.date < today:
            return False
        if self.signup_deadline_days:
            return today <= self.date - timedelta(days=self.signup_deadline_days)
        return True

    def __repr__(self) -> str:
        return f"<WorkSession {self.date} {self.title}>"


class SessionParticipation(Base):
    """
    A member's participation in a work session.
    """
    __tablename__ = "session_participations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    session_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("work_sessions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    member_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("members.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[ParticipationStatus] = mapped_column(
        SAEnum(ParticipationStatus), default=ParticipationStatus.REGISTERED, nullable=False
    )
    hours_completed: Mapped[Optional[float]] = mapped_column(
        Numeric(4, 1), nullable=True,
        comment="Overrides the session's hours_per_participant when set"
    )
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    session: Mapped["WorkSession"] = relationship("WorkSession", back_populates="participations")
    member: Mapped["Member"] = relationship("Member")

    __table_args__ = (
        UniqueConstraint("session_id", "member_id", name="uq_session_member"),
    )


class TaskWorkload(str, enum.Enum):
    """How physically demanding a task is. This exists so whoever is
    coordinating a work session can match tasks to the people who signed
    up for it -- the app itself never stores or infers anything about a
    member's health, age, or ability; that judgment call stays entirely
    with the human coordinator, who knows the people involved."""
    LIGHT = "LIGHT"
    MODERATE = "MODERATE"
    DEMANDING = "DEMANDING"


class WorkTask(Base):
    """
    A task for the work-hours program: something that needs doing,
    optionally scheduled to a specific work session, and optionally
    assigned to one specific person who signed up for that session.

    Deliberately a three-stage lifecycle, each stage optional:
    1. Backlog: session_id is NULL -- "things we know need doing,"
       not yet tied to a specific date.
    2. Scheduled: session_id is set, assigned_participation_id is NULL --
       this session will cover the task, but no specific person yet.
    3. Assigned: assigned_participation_id is set -- one specific
       signed-up participant is doing this specific task.
    """
    __tablename__ = "work_tasks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    workload: Mapped[TaskWorkload] = mapped_column(
        SAEnum(TaskWorkload), default=TaskWorkload.MODERATE, nullable=False
    )
    session_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("work_sessions.id", ondelete="SET NULL"), nullable=True, index=True
    )
    assigned_participation_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("session_participations.id", ondelete="SET NULL"), nullable=True, index=True
    )
    is_done: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_by_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    session: Mapped[Optional["WorkSession"]] = relationship("WorkSession")
    assigned_participation: Mapped[Optional["SessionParticipation"]] = relationship("SessionParticipation")
    created_by: Mapped[Optional["User"]] = relationship("User")

    def __repr__(self) -> str:
        return f"<WorkTask {self.title!r}>"
