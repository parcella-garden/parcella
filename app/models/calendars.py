"""Calendar: events, custom calendars, council presence and absence."""

import secrets
import enum
from datetime import datetime, date
from typing import Optional, List
from sqlalchemy import String, Boolean, Date, DateTime, Text, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base
from app.models._common import new_uuid


class CalendarEventType(str, enum.Enum):
    """What kind of manually-created community calendar entry this is.
    Work sessions are NOT part of this enum -- they already have their
    own date/time on the WorkSession model, and the community calendar
    reads them directly rather than duplicating them into a second table
    (see docs/module-calendar.md for the reasoning)."""
    MEMBER_MEETING = "MEMBER_MEETING"
    PARCEL_INSPECTION = "PARCEL_INSPECTION"
    OTHER = "OTHER"


class CalendarEvent(Base):
    """
    A manually-created entry on the community calendar: a full-member
    meeting, a parcel inspection by the board, or anything else worth
    announcing. Deliberately separate from WorkSession -- work sessions
    already have their own date/time and are merged into the community
    calendar view/ICS feed at read time instead of being copied here.
    """
    __tablename__ = "calendar_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    event_type: Mapped[CalendarEventType] = mapped_column(
        SAEnum(CalendarEventType), default=CalendarEventType.OTHER, nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    start_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    start_time: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)  # "HH:MM"
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    end_time: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)
    created_by_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    created_by: Mapped[Optional["User"]] = relationship("User")
    # Issue #314: NULL = the community calendar (public feed!); set = one
    # of the admin-defined calendars, which never reach the public feed.
    # See docs/ADR/0131.
    calendar_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("custom_calendars.id", ondelete="RESTRICT"), nullable=True, index=True
    )
    calendar: Mapped[Optional["CustomCalendar"]] = relationship("CustomCalendar", back_populates="events")

    def __repr__(self) -> str:
        return f"<CalendarEvent {self.title!r} on {self.start_date}>"


class CustomCalendar(Base):
    """
    An admin-defined calendar besides the built-in ones (issue #314):
    "Vorstandssitzungen", "Vereinsheim", ... Its entries are ordinary
    CalendarEvent rows with calendar_id set. Unlike the community
    calendar it is never public: the page needs calendar read
    permission (plus full access if full_access_only), the ICS feed the
    installation's secret ICS token. Ending one archives it
    (is_active=False) instead of deleting it and its history (ADR 0005).
    """
    __tablename__ = "custom_calendars"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    color: Mapped[str] = mapped_column(String(7), nullable=False, default="#2e7d32")
    full_access_only: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
    # The calendar's own ICS secret -- NOT the installation-wide ICS token,
    # which every calendar reader can see: with that, a board-only
    # calendar's feed would be open to everyone (security review, #314).
    # Rotated whenever full_access_only changes, and on request.
    feed_token: Mapped[str] = mapped_column(String(64), nullable=False, default=lambda: secrets.token_urlsafe(32))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    events: Mapped[List["CalendarEvent"]] = relationship("CalendarEvent", back_populates="calendar")

    def __repr__(self) -> str:
        return f"<CustomCalendar {self.name!r}>"


class CouncilPresence(Base):
    """
    A scheduled slot where a specific board/council member will be
    on-site (e.g. office hours for members with questions). One row per
    person per slot -- if two council members cover the same time
    together, that's two rows.
    """
    __tablename__ = "council_presence"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    time_from: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)
    time_until: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)
    note: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship("User")

    def __repr__(self) -> str:
        return f"<CouncilPresence {self.user_id} on {self.date}>"


class CouncilAbsence(Base):
    """
    A self-reported absence period (e.g. vacation) for anyone with a
    system account -- not restricted to the board/council despite the
    name, matching the original request that "everybody with access to
    the system" can log their own absence. Named for its primary use
    case (knowing when a council member is unreachable), not as an
    access restriction.
    """
    __tablename__ = "council_absence"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    start_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    note: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship("User")

    def __repr__(self) -> str:
        return f"<CouncilAbsence {self.user_id} {self.start_date}-{self.end_date}>"
