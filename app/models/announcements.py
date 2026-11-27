"""Announcements and their deliveries."""

import enum
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Boolean, DateTime, Text, ForeignKey, Enum as SAEnum, UniqueConstraint, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func, text

from app.database import Base
from app.models._common import new_uuid


class AnnouncementChannel(str, enum.Enum):
    BLOG = "BLOG"
    EMAIL = "EMAIL"
    PRINT = "PRINT"
    # One addressed letter per recipient without email (issue #242) --
    # only for announcements to filtered members, see Announcement.
    LETTER = "LETTER"


class AnnouncementDeliveryStatus(str, enum.Enum):
    PENDING = "PENDING"
    SENDING = "SENDING"
    SENT = "SENT"
    FAILED = "FAILED"


class Announcement(Base):
    """
    A single piece of club news/information, authored once here and
    delivered out to up to three channels (blog draft via CMS API,
    member email, printable PDF one-pager). See docs/module-announcements.md
    for the overall design.

    body_markdown is the single canonical source text, used as-is for
    both the blog draft and the email (same container, per product
    decision -- no separate email override). body_html is derived from
    it at save time (markdown -> HTML -> sanitized) and cached here so
    it isn't re-rendered on every read; it is NOT hand-edited directly.

    print_text_override is the one deliberate exception: nullable
    Markdown that, when set, is used for the PDF instead of
    body_markdown. It starts empty (full text is used), gets
    auto-filled with a shortened version if the full text doesn't fit
    on one printed page, and remains freely hand-editable afterward --
    it is a real editable field, not just a computed preview.

    There is deliberately no overall status (draft/published/...):
    what has gone out where is entirely per channel, on
    AnnouncementDelivery -- see docs/ADR/0087.
    """
    __tablename__ = "announcements"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body_markdown: Mapped[str] = mapped_column(Text, nullable=False)
    body_html: Mapped[str] = mapped_column(Text, nullable=False, default="")
    image_filename: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    # Issue #318: alt text for the banner image. NULL = none given; the
    # website channels then fall back to the title (what the CMS plugins
    # always did), Parcella's own pages keep alt="". See docs/ADR/0128.
    image_alt: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    # Issue #317: a short plain-text summary (one line, max 300 chars).
    # NULL = none; it's the email's preview line (preheader) and the
    # website excerpt/teaser. See docs/ADR/0129.
    summary: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    print_text_override: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # A QR code to the published website post on the printed notice even
    # when the text fits as-is -- for a print text that's only a teaser.
    # Off: the QR code appears only when the text had to be shortened.
    # See docs/ADR/0133.
    print_qr_code: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false", nullable=False)
    # The random part of the announcement's short link /a/<token>, which
    # the printed QR code points to: it forwards to the website post once
    # that's public, so a notice can be printed before the post goes live.
    # Created on the first print with a website connector. ADR 0133.
    public_link_token: Mapped[Optional[str]] = mapped_column(String(43), unique=True, nullable=True)
    # Issue #242: a message to filtered members instead of club news.
    # NULL = the classic announcement to every active member with
    # "email info" (blog/email/print channels). Otherwise a stored
    # app.member_filters.MemberListFilter (to_dict()), resolved to
    # recipients each time it's shown or sent; channels are then EMAIL
    # (everyone in the filter with an address, ignoring the email-info
    # opt-out) and LETTER (those without one, or everyone with
    # letters_for_all). See docs/ADR/0095.
    audience_filter: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    letters_for_all: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false", nullable=False)
    # Issue #247: a message to the applicants ticked on /applicants/
    # (issue #246) -- a list of Applicant ids, fixed at creation (a
    # hand-picked selection, not a filter). Email only; one email per
    # distinct address. Mutually exclusive with audience_filter. See
    # docs/ADR/0112.
    audience_applicant_ids: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    # A notice to the leaseholders of parcels picked on /parcels/ (issue
    # #397) -- a list of Parcel ids, fixed at creation. Leasehold law,
    # not association law (ADR 0142): one notice per parcel, to its
    # current leaseholders jointly -- email to each who consented, one
    # letter per address for the others -- naming the parcel. Mutually
    # exclusive with audience_filter/audience_applicant_ids.
    audience_parcel_ids: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    created_by_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    created_by: Mapped[Optional["User"]] = relationship("User")
    deliveries: Mapped[List["AnnouncementDelivery"]] = relationship(
        "AnnouncementDelivery", back_populates="announcement", cascade="all, delete-orphan"
    )

    @property
    def image_url(self) -> Optional[str]:
        # Must match UPLOAD_DIR in app/routers/announcements.py
        # ("app/static/uploads/announcements/") -- unlike the singleton
        # club logo (served straight from /static/uploads/), each
        # announcement's image lives in its own subfolder.
        return f"/static/uploads/announcements/{self.image_filename}" if self.image_filename else None

    @property
    def is_targeted(self) -> bool:
        """A message to filtered members (issue #242), to picked
        applicants (issue #247) or to the leaseholders of picked parcels
        (issue #397), not club news."""
        return (
            self.audience_filter is not None or self.audience_applicant_ids is not None
            or self.audience_parcel_ids is not None
        )

    @property
    def is_applicant_message(self) -> bool:
        """A message to applicants picked on /applicants/ (issue #247)."""
        return self.audience_applicant_ids is not None

    @property
    def is_parcel_message(self) -> bool:
        """A notice to the leaseholders of parcels picked on /parcels/ (issue #397)."""
        return self.audience_parcel_ids is not None

    def delivery_for(self, channel: "AnnouncementChannel") -> Optional["AnnouncementDelivery"]:
        return next((d for d in self.deliveries if d.channel == channel), None)

    def __repr__(self) -> str:
        return f"<Announcement {self.title!r}>"


class AnnouncementDelivery(Base):
    """
    Tracks one channel's delivery attempt for an announcement. One row
    per (announcement, channel) -- upserted, not appended, so retrying a
    failed send updates the existing row rather than creating a history
    of attempts.

    external_reference holds a human-facing pointer for the admin UI --
    currently only used by BLOG, where it's the WordPress **edit** URL
    (wp-admin/post.php?post=...&action=edit), not a public one, since a
    draft doesn't have a public URL yet.

    external_id holds a raw external identifier for re-querying the
    system of record later, rather than trusting a value cached at
    delivery time -- currently only used by BLOG, storing the
    WordPress post ID as a string. The PRINT channel uses this to ask
    WordPress directly, at PDF-generation time, whether the post has
    since been published and what its current public URL is, rather
    than storing (and risking a stale) public URL here on the BLOG
    delivery row itself.

    content_fingerprint / image_filename record exactly what content
    this channel last delivered successfully (see
    app.announcement_utils.channel_fingerprint). A channel's action is
    only offered again when the current content differs from that --
    so saving unchanged text doesn't re-enable anything, and a change
    to print_text_override only re-enables PRINT. EMAIL never
    re-enables after a successful send, regardless (ADR 0087).

    pdf_filename (PRINT only) is the stored copy of the last generated
    PDF, so it can be downloaded again without regenerating.
    qr_pending (PRINT only) is True when the PDF was shortened but got
    no QR code because the blog post wasn't public yet -- regenerating
    once it is public is the one reason to redo an unchanged PDF.
    """
    __tablename__ = "announcement_deliveries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    announcement_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("announcements.id", ondelete="CASCADE"), nullable=False, index=True
    )
    channel: Mapped[AnnouncementChannel] = mapped_column(SAEnum(AnnouncementChannel), nullable=False)
    status: Mapped[AnnouncementDeliveryStatus] = mapped_column(
        SAEnum(AnnouncementDeliveryStatus), default=AnnouncementDeliveryStatus.PENDING, nullable=False
    )
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    external_reference: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    external_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    # Despite the name, this doubles as a general status-detail field,
    # not strictly an error: while SENDING it holds a progress note
    # ("12 of 800 sent so far"), and on a partial SENT it holds the
    # failure count. It's only ever a true error message when the
    # status is FAILED. Kept as one field rather than adding a second
    # column, since only one of these is ever relevant at a time.
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    content_fingerprint: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    image_filename: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    # The alt text as delivered (issue #318), compared like image_filename
    # so an alt-only edit marks the channel as changed.
    image_alt: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    pdf_filename: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    qr_pending: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    announcement: Mapped["Announcement"] = relationship("Announcement", back_populates="deliveries")

    __table_args__ = (
        UniqueConstraint("announcement_id", "channel", name="uq_announcement_delivery_channel"),
    )

    def __repr__(self) -> str:
        return f"<AnnouncementDelivery {self.announcement_id} {self.channel.value} ({self.status.value})>"
