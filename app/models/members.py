"""Members, member tags, phone numbers and e-mail addresses."""

from datetime import datetime, date
from typing import Optional, List
from sqlalchemy import String, Boolean, Date, DateTime, Text, ForeignKey, Column, Table, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base
from app.models._common import new_uuid


# ---------------------------------------------------------------------------
# Club members
# ---------------------------------------------------------------------------

class Member(Base):
    __tablename__ = "members"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)

    # Personal data
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    date_of_birth: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Address
    street: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    postal_code: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Bank details
    iban: Mapped[Optional[str]] = mapped_column(String(34), nullable=True)

    # Membership
    member_since: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    member_until: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Communication
    email_notifications: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # The member doesn't want birthday presents (issue #269) -- shown on
    # the birthday list and its PDF for whoever hands presents out. Who
    # gets a present at all (board every year, others on milestones...)
    # is club policy and not modelled.
    birthday_present_declined: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false", nullable=False
    )

    # Notes (internal)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # The member's customer record in each helpdesk lives in
    # HelpdeskCustomerId (ADR 0107), not here.

    # Audit
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    phone_numbers: Mapped[List["MemberPhone"]] = relationship(
        "MemberPhone", back_populates="member", cascade="all, delete-orphan"
    )
    email_addresses: Mapped[List["MemberEmail"]] = relationship(
        "MemberEmail", back_populates="member", cascade="all, delete-orphan"
    )
    parcel_assignments: Mapped[List["MemberParcel"]] = relationship(
        "MemberParcel", back_populates="member"
    )
    # Free-form labels (issue #241) -- see MemberTag. Not lazy-loadable
    # under asyncio: selectinload(Member.tags) wherever it's read.
    tags: Mapped[List["MemberTag"]] = relationship(
        "MemberTag", secondary="member_tag_links", back_populates="members",
        order_by="MemberTag.name",
    )

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def is_active(self) -> bool:
        """Python-side mirror of app/database.py's active_member_filter()
        -- keep the two in sync (issue #167: this one was missed when
        the member_since check was added to the SQL filter, so the
        member list's status badge and the REST API's active_only
        filter kept showing a pending application as active)."""
        return self.deleted_at is None and (
            self.member_since is None or self.member_since <= date.today()
        ) and (
            self.member_until is None or self.member_until >= date.today()
        )

    def __repr__(self) -> str:
        return f"<Member {self.full_name}>"


class MemberTag(Base):
    """
    A free-form label on members ("water responsible", "extended
    board", "hedge team" ...), issue #241 -- for finding and filtering
    people, nothing else. Deliberately not ClubRole: that one is a
    per-year office that can exempt from work hours (see
    docs/ADR/0093); a tag carries no meaning the app acts on and no
    history. Removing a tag from a member deletes the link row -- a
    label isn't club history, so ADR 0005's historization doesn't apply.
    """
    __tablename__ = "member_tags"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    # {language code: name shown in that language}, e.g. {"en": "red flag"}
    # for "Rote Liste" -- see app/tag_translations.py, ADR 0098.
    translations: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    members: Mapped[List["Member"]] = relationship(
        "Member", secondary="member_tag_links", back_populates="tags"
    )

    def __repr__(self) -> str:
        return f"<MemberTag {self.name}>"


member_tag_links = Table(
    "member_tag_links",
    Base.metadata,
    Column("member_id", String(36), ForeignKey("members.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", String(36), ForeignKey("member_tags.id", ondelete="CASCADE"), primary_key=True, index=True),
)


class MemberPhone(Base):
    """Multiple phone numbers per member."""
    __tablename__ = "member_phones"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    member_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("members.id", ondelete="CASCADE"), nullable=False, index=True
    )
    number: Mapped[str] = mapped_column(String(50), nullable=False)
    label: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # e.g. "Mobile", "Landline"
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    member: Mapped["Member"] = relationship("Member", back_populates="phone_numbers")


class MemberEmail(Base):
    """Multiple email addresses per member."""
    __tablename__ = "member_emails"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    member_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("members.id", ondelete="CASCADE"), nullable=False, index=True
    )
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    label: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # e.g. "Personal", "Work"
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    member: Mapped["Member"] = relationship("Member", back_populates="email_addresses")
