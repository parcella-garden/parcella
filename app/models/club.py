"""Club master data, board members, sample-data tracking, change history, e-mail log."""

import enum
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, DateTime, Text, ForeignKey, Enum as SAEnum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base
from app.models._common import new_uuid


# ---------------------------------------------------------------------------
# Club settings (key-value for flexibility)
# ---------------------------------------------------------------------------

class ClubSetting(Base):
    """
    Flexible settings table for club master data.
    Enables later extension without a schema change.
    """
    __tablename__ = "club_settings"

    key: Mapped[str] = mapped_column(String(100), primary_key=True)
    value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Known keys (for documentation):
    # verein_name, verein_strasse, verein_plz, verein_ort
    # flaeche_gesamt_qm, flaeche_a_qm, flaeche_b_qm, flaeche_c_qm
    # vereinsnummer, registergericht


class ClubBoardMember(Base):
    """
    Board members listed on admin -> settings -> club settings (issue
    #111) -- a plain "who's currently on the board" display list, picked
    from Member via a searchable multi-select. Deliberately separate from
    ClubRole/MemberClubRole (app/routers/work_hours.py), which tracks
    BOARD/EXTENDED_BOARD membership for annual work-hours exemption over
    dated validity ranges -- a different concern with different lifetime
    semantics, not something this reuses.
    """
    __tablename__ = "club_board_members"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    member_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("members.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    member: Mapped["Member"] = relationship("Member")

    __table_args__ = (
        UniqueConstraint("member_id", name="uq_club_board_member"),
    )

    @property
    def full_name(self) -> str:
        """For BoardMemberOut (API) -- requires `member` eagerly loaded (selectinload)."""
        return self.member.full_name


class SampleDataRecord(Base):
    """
    Tracks every row created by the admin "add sample data" feature
    (see app/sample_data.py), so "remove all sample data" can delete
    exactly what was generated -- never guessed by naming pattern, and
    never anything an admin entered themselves. entity_type is a model
    class name (e.g. "Member", "WorkSession"); removal looks each one
    up via a fixed model registry, not dynamic imports.
    """
    __tablename__ = "sample_data_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    module: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    entity_id: Mapped[str] = mapped_column(String(36), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        UniqueConstraint("entity_type", "entity_id", name="uq_sample_data_record"),
    )




# ---------------------------------------------------------------------------
# Change history (generic audit log for field changes)
# ---------------------------------------------------------------------------

class ChangeHistory(Base):
    """
    Generic audit log: logs field changes on arbitrary entities (e.g.
    Parcel.area_sqm). Enables traceability without needing a separate
    history table for every table.
    """
    __tablename__ = "change_history"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    entity_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    field_name: Mapped[str] = mapped_column(String(100), nullable=False)
    old_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    new_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    changed_by_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )

    changed_by: Mapped[Optional["User"]] = relationship("User")

    def __repr__(self) -> str:
        return f"<ChangeHistory {self.entity_type}:{self.entity_id} {self.field_name}>"


class EmailLogStatus(str, enum.Enum):
    """What the SMTP server said when Parcella handed the message over
    (issue #270). SENT means accepted for delivery, not delivered: a
    later bounce arrives as a mail in the sending mailbox, which
    Parcella doesn't read (ADR 0120)."""
    SENT = "SENT"
    FAILED = "FAILED"


class EmailLog(Base):
    """One row per outgoing email (issue #270, ADR 0120), written by
    app.email_service.send_email(). Deleted after the retention period
    (`email_log_retention_days`, default 90) -- recipient addresses are
    personal data."""
    __tablename__ = "email_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    sent_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    recipient: Mapped[str] = mapped_column(String(320), nullable=False, index=True)
    subject: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    status: Mapped[EmailLogStatus] = mapped_column(SAEnum(EmailLogStatus), nullable=False, index=True)
    # The SMTP error (or "SMTP not configured") for a FAILED row.
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    attachment_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0", nullable=False)

    def __repr__(self) -> str:
        return f"<EmailLog {self.recipient} {self.status.value}>"
