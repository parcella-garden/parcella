"""Applicants for a garden plot."""

import enum
from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, Text, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func, text

from app.database import Base
from app.models._common import new_uuid


# ---------------------------------------------------------------------------
# Applicants: people applying for a free garden plot (docs/module-applicants.md)
# ---------------------------------------------------------------------------

class ApplicantStatus(str, enum.Enum):
    NEW = "NEW"              # just applied, nobody has looked at it yet
    CONTACTED = "CONTACTED"  # the board got in touch
    OFFERED = "OFFERED"      # a plot was offered
    ACCEPTED = "ACCEPTED"    # wants the offered plot -- handover still being negotiated (issue #252)
    REJECTED = "REJECTED"    # the club declined, or the applicant wants no further offers
    CLOSED = "CLOSED"        # a parcel was assigned ("Assign a parcel", ADR 0101)
    # No WITHDRAWN (issue #253): an applicant who turns an offer down is
    # either REJECTED (no more offers) or back to CONTACTED (stays on the
    # waiting list). Migration 0113 renamed the enum label to CLOSED.


# Statuses an application is still being worked on in -- the list page's
# "open" filter. ACCEPTED stays open until the parcel is actually handed
# over (issue #252); the handover moves it to CLOSED.
APPLICANT_OPEN_STATUSES = (
    ApplicantStatus.NEW, ApplicantStatus.CONTACTED, ApplicantStatus.OFFERED, ApplicantStatus.ACCEPTED,
)


class ApplicantSource(str, enum.Enum):
    WEBSITE = "WEBSITE"  # a public form (website, WordPress plugin, API)
    MANUAL = "MANUAL"    # entered by the board, e.g. after a phone call


class Applicant(Base):
    """
    Someone who applied for a free garden plot -- deliberately not a
    Member: most applicants never get a plot, and their data must not
    end up in the member list. Only the email address is required; the
    public form asks for name, phone and a free-text message as
    optional extras.

    Unlike almost everything else in Parcella, an applicant can be
    hard-deleted (ADR 0091): it's personal data of a non-member, held
    only for the application, not club history -- GDPR wins over the
    historization rule (ADR 0005) here. Status changes are still
    written to change_history while the row exists.
    """
    __tablename__ = "applicants"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    status: Mapped[ApplicantStatus] = mapped_column(
        SAEnum(ApplicantStatus), default=ApplicantStatus.NEW, nullable=False, index=True
    )
    source: Mapped[ApplicantSource] = mapped_column(
        SAEnum(ApplicantSource), default=ApplicantSource.WEBSITE, nullable=False
    )
    board_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # When the applicant ticked the data-protection consent box (public
    # forms only -- a manual entry records none).
    consent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    applied_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    status_changed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    created_by_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    created_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[created_by_id])

    @property
    def display_name(self) -> str:
        """Name if given, the email address otherwise."""
        name = " ".join(part for part in (self.first_name, self.last_name) if part)
        return name or self.email

    def __repr__(self) -> str:
        return f"<Applicant {self.email} {self.status.value}>"
