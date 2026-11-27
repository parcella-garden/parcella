"""Purchase requests with two-person approval."""

import enum
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Boolean, DateTime, Text, Numeric, ForeignKey, Enum as SAEnum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base
from app.models._common import new_uuid


# ---------------------------------------------------------------------------
# Purchase Requests (four-eyes principle for club expenses)
# ---------------------------------------------------------------------------

class PurchaseRequestStatus(str, enum.Enum):
    OPEN = "OPEN"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class PurchaseRequest(Base):
    """
    A request for a club expense. Must be approved by two different
    board members before the purchase may proceed -- the requester
    themselves doesn't count as an approver (four-eyes principle).
    """
    __tablename__ = "purchase_requests"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    justification: Mapped[str] = mapped_column(Text, nullable=False)
    link: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    estimated_cost_eur: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)

    status: Mapped[PurchaseRequestStatus] = mapped_column(
        SAEnum(PurchaseRequestStatus), default=PurchaseRequestStatus.OPEN, nullable=False, index=True
    )

    # Requester: either a system user (requested_by_id) OR an external
    # person without a login (requester_name/-email), e.g. when the
    # board creates a request on someone else's behalf.
    requested_by_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    requester_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    requester_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    created_by_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    # Deep-link confirmation by the (external) requester
    confirmation_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, unique=True)
    confirmed_by_requester: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    confirmed_by_requester_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    rejected_by_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    rejected_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Optional supplier from the external contacts module (ADR 0096).
    external_contact_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("external_contacts.id", ondelete="SET NULL"), nullable=True, index=True
    )

    requested_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[requested_by_id])
    created_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[created_by_id])
    rejected_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[rejected_by_id])
    external_contact: Mapped[Optional["ExternalContact"]] = relationship("ExternalContact")
    approvals: Mapped[List["PurchaseRequestApproval"]] = relationship(
        "PurchaseRequestApproval", back_populates="purchase_request", cascade="all, delete-orphan"
    )
    comments: Mapped[List["PurchaseRequestComment"]] = relationship(
        "PurchaseRequestComment", back_populates="purchase_request", cascade="all, delete-orphan",
        order_by="PurchaseRequestComment.created_at",
    )

    @property
    def requester_display_name(self) -> str:
        if self.requested_by:
            return self.requested_by.name
        # Empty when nobody is known; templates show the translated
        # "Unknown" (issue #364: this returned hard-coded German).
        return self.requester_name or self.requester_email or ""

    @property
    def approval_count(self) -> int:
        return len(self.approvals)

    def __repr__(self) -> str:
        return f"<PurchaseRequest {self.title!r} ({self.status.value})>"


class PurchaseRequestApproval(Base):
    """A single approval by a board member for a PurchaseRequest."""
    __tablename__ = "purchase_request_approvals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    purchase_request_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("purchase_requests.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    approved_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    purchase_request: Mapped["PurchaseRequest"] = relationship("PurchaseRequest", back_populates="approvals")
    user: Mapped["User"] = relationship("User")

    __table_args__ = (
        UniqueConstraint("purchase_request_id", "user_id", name="uq_purchase_request_approval"),
    )


class PurchaseRequestComment(Base):
    """A comment in the discussion on a purchase request (issue #249),
    e.g. "we already have a labelling machine". Append-only like
    TaskComment. Each new comment is emailed to the requester and to
    everyone who commented or approved before (not to its author)."""
    __tablename__ = "purchase_request_comments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    purchase_request_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("purchase_requests.id", ondelete="CASCADE"), nullable=False, index=True
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_by_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    purchase_request: Mapped["PurchaseRequest"] = relationship("PurchaseRequest", back_populates="comments")
    created_by: Mapped[Optional["User"]] = relationship("User")

    def __repr__(self) -> str:
        return f"<PurchaseRequestComment purchase_request={self.purchase_request_id}>"
