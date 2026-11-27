"""Links to conversations in the external helpdesk."""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base
from app.models._common import new_uuid


# ---------------------------------------------------------------------------
# FreeScout conversation bridge
# ---------------------------------------------------------------------------
# Parcella no longer implements its own ticket/helpdesk system (ADR 0080):
# support conversations live in the club's helpdesk -- FreeScout, Zammad,
# Znuny, osTicket, Zendesk, Freshdesk, one at a time (ADR 0107, app/helpdesk/).
# This table is a lightweight cross-reference only -- NOT a mirror of the
# helpdesk's messages/attachments. The transcript is fetched live when a
# conversation's detail page is opened (app/routers/support.py), never
# stored here. Populated/updated by the poll loop (app/main.py); member/
# parcel association can additionally be corrected by staff in the UI.

class HelpdeskConversationLink(Base):
    """
    A cross-reference to one conversation in the club's helpdesk: which
    Parcella member/parcel it belongs to, and optionally which Parcella
    task it was promoted to. Rows of a helpdesk that isn't active anymore
    stay (hidden), so switching back finds them again.
    """
    __tablename__ = "helpdesk_conversation_links"
    __table_args__ = (
        UniqueConstraint("provider", "external_id", name="uq_helpdesk_conversation_provider_external"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)

    # Which helpdesk (app.helpdesk.registry type, e.g. "freescout") and
    # the conversation's id there -- a string, since not every helpdesk
    # uses integers.
    provider: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    external_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    # Mailbox/group/queue the conversation is in, as the helpdesk names it.
    mailbox_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)

    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    customer_email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    customer_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # One of app.helpdesk.base's STATUS_* values (active, pending, closed,
    # spam, deleted) -- the helpdesk owns the lifecycle; Parcella only maps
    # its states onto these so lists and badges work the same everywhere.
    status: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    # From the helpdesk's conversation list, if it exposes one. Shown to
    # staff as a hint for deciding which conversations are worth promoting
    # to a task -- a displayed signal, not an automatic trigger.
    message_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Matching hierarchy: HelpdeskCustomerId first (exact, persisted), else
    # find_members_by_email() (app/member_matching.py). Left NULL when
    # ambiguous (more than one member shares the address) or unmatched (a
    # non-member inquiry) -- never guessed.
    member_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("members.id", ondelete="SET NULL"), nullable=True, index=True
    )
    # Auto-set only when the resolved member has exactly one *current*
    # parcel (MemberParcel.is_current / app/database.py's
    # current_tenant_filter()); left NULL and shown as a selector in the
    # UI when the member has more than one.
    parcel_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("parcels.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Set only by the manual "Create task"/"Link to existing task" action
    # (app/routers/support.py) -- a loose, nullable cross-domain FK
    # (SET NULL, not a hard-ownership pattern): deleting the task must
    # not delete or break this link row, it just becomes unlinked again.
    task_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True, index=True
    )

    external_updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    last_synced_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    member: Mapped[Optional["Member"]] = relationship("Member")
    parcel: Mapped[Optional["Parcel"]] = relationship("Parcel")
    task: Mapped[Optional["Task"]] = relationship("Task")

    # The pre-ADR-0107 field names, kept read-only for the deprecated
    # /api/v1/freescout endpoints so existing API clients keep working.
    @property
    def freescout_conversation_id(self) -> int:
        return int(self.external_id) if self.external_id.isdigit() else 0

    @property
    def freescout_mailbox_id(self) -> int:
        return int(self.mailbox_id) if self.mailbox_id and self.mailbox_id.isdigit() else 0

    @property
    def freescout_status(self) -> str:
        return self.status

    @property
    def freescout_updated_at(self) -> datetime:
        return self.external_updated_at

    def __repr__(self) -> str:
        return f"<HelpdeskConversationLink {self.provider}:{self.external_id}>"


class HelpdeskCustomerId(Base):
    """
    Persistent identity mapping from a member to their customer record in
    a helpdesk. Set lazily -- the first time the member is matched to an
    inbound conversation, not proactively -- so a member who never
    contacts support never gets pushed into any helpdesk. One row per
    member and helpdesk, since every helpdesk numbers its customers
    differently.
    """
    __tablename__ = "helpdesk_customer_ids"
    __table_args__ = (
        UniqueConstraint("provider", "customer_id", name="uq_helpdesk_customer_provider_customer"),
        UniqueConstraint("member_id", "provider", name="uq_helpdesk_customer_member_provider"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    member_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("members.id", ondelete="CASCADE"), nullable=False, index=True
    )
    provider: Mapped[str] = mapped_column(String(30), nullable=False)
    customer_id: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
