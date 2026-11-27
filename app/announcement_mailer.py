"""
Email channel for the announcements module.

Recipients are current club members -- active_member_filter(), the
same canonical "active member" definition used by /members/'s own
list and API (see app/services/members.py's docstring re: issue #167,
two independent reimplementations of "active" drifting apart) -- who
have email_notifications = True (this is the "e-mail info = yes" flag
from the original feature request). Deliberately NOT scoped to current
parcel residents (an earlier version was, matching the original
feature request's literal wording): a member who is still within
their membership period but has given up their parcel lease is still
a club member and still expects to hear about club matters (issue
#236's Daniel Hetzger case -- member until 2026-12-31, lease ended
2026-06-30, should still receive announcements).
A member with no stored email address is silently skipped rather than
treated as an error -- that's a data-completeness issue for Members
admin, not an announcements-sending failure.

Uses the exact same body_html as the blog channel (see
docs/module-announcements.md -- "same container" is a deliberate
product decision, not an oversight), wrapped in a minimal email
template with the header image and the club's branding.

Sending is per-recipient, but AnnouncementDelivery tracks channel-level
status only (not one row per recipient) -- see the model's docstring
in app/models/ for why. A partial failure (some recipients bounced/
failed) still counts as SENT, with the failure count noted in
error_message, since the announcement did go out; a total failure
(zero successful sends, or zero recipients found) is recorded as
FAILED so it's visually distinct and inviting a retry.

Sending is paced (EMAIL_BATCH_SIZE per EMAIL_BATCH_PAUSE_SECONDS)
rather than firing every email at once, to avoid tripping an SMTP
relay's rate limits on a large club roster. Because pacing an 800-name
list at a handful per minute can take well over an hour, the actual
send runs as a FastAPI background task (see run_paced_email_send,
scheduled from the router) rather than inside the request/response
cycle -- the endpoint marks the delivery SENDING and returns
immediately, and the background task updates the same
AnnouncementDelivery row as it progresses and again when it finishes.
The background task opens its own DB session (AsyncSessionLocal),
since the request-scoped session closes once the response has been
sent -- same pattern as app.main's ticket-inbox polling loop.

Issue #242 added messages to *filtered* members (Announcement.
audience_filter, created from /members/): resolve_audience() splits
whoever the stored member-list filter matches into email recipients,
letter recipients (app/announcement_letters.py) and unreachable ones.
Since issue #403 (association law, ADR 0142) consent decides: email
only to members who allow information by email, a letter to the others
-- members without consent at one postal address share one letter. This
replaces ADR 0095, which ignored the email-info opt-out here.

Issue #397 added notices to the leaseholders of parcels picked on
/parcels/ (Announcement.audience_parcel_ids). That's leasehold law, not
association law (ADR 0142): one notice per parcel -- a couple holding
two parcels gets two -- to its current leaseholders jointly. Email to
each leaseholder who consented (email notifications on), one letter per
postal address for the others, also when a housemate got the email.
Every email and letter names its parcel.

Issue #247 added messages to applicants picked on /applicants/
(Announcement.audience_applicant_ids, ADR 0112): email only, and an
address shared by several picked applications gets the message once.
"""
import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional, Tuple

from markupsafe import escape
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import AsyncSessionLocal, active_member_filter
from app.models import (
    Announcement, AnnouncementChannel, AnnouncementDelivery,
    AnnouncementDeliveryStatus, Applicant, Member, MemberParcel, Parcel,
)
from app.email_service import send_email
from app.member_filters import MemberListFilter
from app.insurance_utils import _normalized_address
from app.branding import load_branding
from app.i18n import load_current_language, t_for, translate as t_for_language

logger = logging.getLogger(__name__)

# Deliberately conservative default -- "five or ten per minute" was the
# ask. Both numbers are read at call time (not baked into a constant
# closure), so a future admin-configurable setting can replace these
# without changing the pacing logic itself.
EMAIL_BATCH_SIZE = 8
EMAIL_BATCH_PAUSE_SECONDS = 60


async def get_active_recipient_emails(db: AsyncSession) -> List[Tuple[Member, str]]:
    """Current club members (active_member_filter()) with
    email_notifications=True and at least one stored email address --
    not scoped to current parcel residents, see module docstring. One
    (member, email) pair per member, using their primary email if
    marked, otherwise the first one on file."""
    result = await db.execute(
        select(Member)
        .where(active_member_filter(), Member.email_notifications.is_(True))
        .options(selectinload(Member.email_addresses))
    )
    members = result.scalars().all()

    recipients: List[Tuple[Member, str]] = []
    for member in members:
        address = primary_email(member)
        if address:
            recipients.append((member, address))
    return recipients


def primary_email(member: Member) -> Optional[str]:
    """The member's primary email if marked, otherwise the first one on
    file (email_addresses must be loaded)."""
    emails = member.email_addresses
    if not emails:
        return None
    return next((e for e in emails if e.is_primary), emails[0]).address


def has_postal_address(member: Member) -> bool:
    """Enough of an address to put on an envelope."""
    return bool((member.street or "").strip() and ((member.city or "").strip() or (member.postal_code or "").strip()))


@dataclass
class Audience:
    """Who a (targeted) announcement reaches, and how. A member can be
    in both `email` and `letter` (letters_for_all). For a message to
    applicants (issue #247) `email` holds (Applicant, address) pairs,
    one per distinct address, and `duplicates` counts the picked
    applications whose address was already in the list."""
    email: List[Tuple[Member, str]] = field(default_factory=list)
    letter: List[Member] = field(default_factory=list)
    unreachable: List[Member] = field(default_factory=list)
    duplicates: int = 0
    # One entry per letter to print: the members it's addressed to.
    # One member each, except for notices to picked parcels (#397),
    # where leaseholders sharing a postal address get one letter.
    letter_groups: List[List[Member]] = field(default_factory=list)
    # Notices to picked parcels only: the plot number each email
    # (parallel to `email`) and each letter (parallel to
    # `letter_groups`) is about.
    email_refs: List[str] = field(default_factory=list)
    letter_refs: List[str] = field(default_factory=list)

    @property
    def member_count(self) -> int:
        ids = {m.id for m, _ in self.email} | {m.id for m in self.letter} | {m.id for m in self.unreachable}
        return len(ids)


async def resolve_audience(db: AsyncSession, announcement: Announcement) -> Audience:
    """Recipients of `announcement`, resolved now (the filter is stored,
    the people behind it can change until the message is sent).

    Club news (no audience): email to get_active_recipient_emails();
    since issue #399 also letters, by the members rule (ADR 0142): to
    every active member without email consent who has a postal address
    (everyone with letters_for_all), one per address. Targeted (issue #242): everyone the
    stored MemberListFilter matches -- email to each who consented
    (email notifications on) and has an address (issue #403); a letter
    to the others (or to everyone with letters_for_all) who have a
    postal address, one per address; whoever gets neither is
    unreachable."""
    if not announcement.is_targeted:
        return await _resolve_club_news_audience(db, announcement.letters_for_all)
    if announcement.is_applicant_message:
        return await _resolve_applicant_audience(db, announcement.audience_applicant_ids)

    if announcement.is_parcel_message:
        return await _resolve_parcel_audience(db, announcement.audience_parcel_ids, announcement.letters_for_all)

    members = (await db.scalars(
        MemberListFilter.from_dict(announcement.audience_filter).apply()
        .options(selectinload(Member.email_addresses))
    )).all()
    audience = Audience()
    for member in members:
        address = primary_email(member) if member.email_notifications else None
        if address:
            audience.email.append((member, address))
        if (address is None or announcement.letters_for_all) and has_postal_address(member):
            audience.letter.append(member)
        elif address is None:
            audience.unreachable.append(member)
    # Association law (issue #403): members who share a postal address
    # get one letter naming all of them.
    audience.letter_groups = group_by_postal_address(audience.letter)
    return audience


async def _resolve_club_news_audience(db: AsyncSession, letters_for_all: bool) -> Audience:
    """Club news (issue #399): the email recipients as before (active
    members with consent and an address); letters for the other active
    members with a postal address, grouped by address."""
    audience = Audience(email=await get_active_recipient_emails(db))
    emailed = {m.id for m, _ in audience.email}
    members = (await db.scalars(
        select(Member).where(active_member_filter()).order_by(Member.last_name, Member.first_name)
    )).all()
    for member in members:
        if (member.id not in emailed or letters_for_all) and has_postal_address(member):
            audience.letter.append(member)
        elif member.id not in emailed:
            audience.unreachable.append(member)
    audience.letter_groups = group_by_postal_address(audience.letter)
    return audience


async def _resolve_parcel_audience(db: AsyncSession, parcel_ids: List[str], letters_for_all: bool) -> Audience:
    """Issue #397, leasehold law (ADR 0142): per picked parcel, in plot
    number order, its current leaseholders. Email to each who consented
    (email notifications on and an address; one per address within a
    parcel); the others get a letter, one per postal address, naming
    them -- also when someone they live with got the email. With
    letters_for_all, everyone with a postal address gets the letter too.
    A deleted parcel or member is simply gone."""
    parcels = (await db.scalars(
        select(Parcel)
        .where(Parcel.id.in_(parcel_ids or []))
        .options(selectinload(Parcel.member_assignments).selectinload(MemberParcel.member)
                 .selectinload(Member.email_addresses))
        .order_by(Parcel.plot_number)
    )).all()
    audience = Audience()
    for parcel in parcels:
        leaseholders = sorted(
            (a.member for a in parcel.member_assignments if a.is_current and a.member.deleted_at is None),
            key=lambda m: ((m.last_name or "").lower(), (m.first_name or "").lower(), m.id),
        )
        seen, by_post = set(), []
        for member in leaseholders:
            address = primary_email(member) if member.email_notifications else None
            if address and address.strip().lower() in seen:
                audience.duplicates += 1
            elif address:
                seen.add(address.strip().lower())
                audience.email.append((member, address))
                audience.email_refs.append(parcel.plot_number)
            if (address is None or letters_for_all) and has_postal_address(member):
                by_post.append(member)
            elif address is None:
                audience.unreachable.append(member)
        for group in group_by_postal_address(by_post):
            audience.letter.extend(group)
            audience.letter_groups.append(group)
            audience.letter_refs.append(parcel.plot_number)
    return audience


def group_by_postal_address(members: List[Member]) -> List[List[Member]]:
    """Members who share a postal address (ignoring case and blanks,
    same comparison as the invoice copies), in first-seen order: one
    letter per address -- for member messages (#403) and, per parcel,
    for notices to parcels (#397)."""
    groups: dict = {}
    for member in members:
        groups.setdefault(_normalized_address(member), []).append(member)
    return list(groups.values())


async def _resolve_applicant_audience(db: AsyncSession, applicant_ids: List[str]) -> Audience:
    """Issue #247: the picked applicants, one email per address --
    compared ignoring case and surrounding blanks, the oldest
    application keeps the slot. A deleted applicant is simply gone."""
    applicants = (await db.scalars(
        select(Applicant).where(Applicant.id.in_(applicant_ids or [])).order_by(Applicant.applied_at)
    )).all()
    audience = Audience()
    seen = set()
    for applicant in applicants:
        address = (applicant.email or "").strip()
        if not address:
            continue
        if address.lower() in seen:
            audience.duplicates += 1
            continue
        seen.add(address.lower())
        audience.email.append((applicant, address))
    return audience


async def _resolve_image_url(announcement: Announcement, base_url: str) -> Optional[str]:
    return f"{base_url}{announcement.image_url}" if announcement.image_url else None


def build_announcement_email_html(
    announcement: Announcement, club_name: str, image_url: Optional[str], test_banner: bool = False,
    banner_text: Optional[str] = None, reference: Optional[str] = None,
) -> str:
    """Wraps the announcement's canonical body_html (same content as
    the blog draft) in a minimal, branded email shell. test_banner adds
    a small notice at the top so a test send is never mistaken for the
    real thing, without changing the actual announcement content being
    previewed. `reference` ("Parcel 12", notices to picked parcels,
    issue #397) is shown above the title."""
    reference_block = (
        f'<p style="font-weight: bold; margin-bottom: 0.25rem;">{escape(reference)}</p>' if reference else ""
    )
    image_block = (
        f'<p><img src="{image_url}" alt="{escape(announcement.image_alt or "")}" style="max-width: 100%; height: auto; border-radius: 4px;"></p>'
        if image_url else ""
    )
    banner = (
        '<p style="background: #fef3c7; color: #92400e; padding: 8px 12px; border-radius: 4px; '
        f'font-size: 0.85rem;">{banner_text}</p>'
        if test_banner else ""
    )
    # The summary (issue #317) as preheader: invisible in the mail itself,
    # shown by mail clients as the preview line under the subject.
    preheader = (
        '<div style="display: none; max-height: 0; overflow: hidden; mso-hide: all;">'
        f'{escape(announcement.summary)}</div>'
        if announcement.summary else ""
    )
    return f"""
    <html><body style="font-family: sans-serif; color: #1f2937; max-width: 600px; margin: 0 auto;">
    {preheader}
    {banner}
    <p style="color: #6b7280; font-size: 0.85rem; margin-bottom: 0.5rem;">{escape(club_name)}</p>
    {reference_block}
    <h2 style="margin-top: 0;">{escape(announcement.title)}</h2>
    {image_block}
    <div>{announcement.body_html}</div>
    </body></html>
    """


async def send_test_email(announcement: Announcement, db: AsyncSession, request, address: str) -> bool:
    """Sends the announcement content to a single address for review,
    completely separate from the real send: it doesn't touch
    AnnouncementDelivery and isn't paced, since it's exactly one
    email."""
    branding = await load_branding(db)
    base_url = str(request.base_url).rstrip("/")
    image_url = await _resolve_image_url(announcement, base_url)
    banner_text = t_for(request, "email.announcement_test_banner")
    html_body = build_announcement_email_html(
        announcement, branding["club_name"], image_url, test_banner=True, banner_text=banner_text,
    )
    return await send_email(address, f"[Test] {announcement.title}", html_body, db=db)


async def start_paced_email_send(announcement: Announcement, db: AsyncSession) -> Tuple[AnnouncementDelivery, int]:
    """Synchronous part of sending, run inside the request: figures out
    who would receive it and marks the delivery row SENDING (or FAILED
    immediately if there's no one to send to). Returns the delivery row
    and recipient count so the router can decide whether to schedule
    the background task at all. Caller commits."""
    recipients = (await resolve_audience(db, announcement)).email

    delivery = announcement.delivery_for(AnnouncementChannel.EMAIL)
    if delivery is None:
        delivery = AnnouncementDelivery(announcement_id=announcement.id, channel=AnnouncementChannel.EMAIL)
        db.add(delivery)

    if not recipients:
        delivery.status = AnnouncementDeliveryStatus.FAILED
        delivery.error_message = (
            "No recipients found (none of the selected applicants exists any more)."
            if announcement.is_applicant_message else
            "No recipients found (nobody in the selected members has a stored email address)."
            if announcement.is_targeted else
            "No recipients found (no current members with email notifications enabled and a stored email address)."
        )
        delivery.sent_at = datetime.now(timezone.utc)
        return delivery, 0

    delivery.status = AnnouncementDeliveryStatus.SENDING
    delivery.error_message = f"0 of {len(recipients)} sent so far."
    delivery.sent_at = None
    return delivery, len(recipients)


async def run_paced_email_send(announcement_id: str, base_url: str) -> None:
    """Background task: does the actual paced sending and updates the
    EMAIL AnnouncementDelivery row as it goes, then a final time on
    completion. Runs after the triggering request has already
    returned, so it opens its own DB session rather than reusing the
    request's (which is closed by then) -- same pattern as
    app.main's _ticket_inbox_polling_loop.
    """
    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(Announcement).where(Announcement.id == announcement_id))
            announcement = result.scalar_one_or_none()
            if announcement is None:
                return

            branding = await load_branding(db)
            image_url = await _resolve_image_url(announcement, base_url)
            html_body = build_announcement_email_html(announcement, branding["club_name"], image_url)
            audience = await resolve_audience(db, announcement)
            recipients = audience.email
            # Notices to picked parcels (issue #397): each email names its
            # parcel, in the text and the subject.
            language = await load_current_language(db)
            references = [
                t_for_language("announcements.parcels.reference", language, plot=plot) for plot in audience.email_refs
            ]

            delivery_result = await db.execute(
                select(AnnouncementDelivery).where(
                    AnnouncementDelivery.announcement_id == announcement_id,
                    AnnouncementDelivery.channel == AnnouncementChannel.EMAIL,
                )
            )
            delivery = delivery_result.scalar_one_or_none()
            if delivery is None:
                return

            success_count = 0
            failure_count = 0
            for batch_start in range(0, len(recipients), EMAIL_BATCH_SIZE):
                batch = recipients[batch_start:batch_start + EMAIL_BATCH_SIZE]
                for offset, (_member, address) in enumerate(batch):
                    reference = references[batch_start + offset] if references else None
                    if reference:
                        sent = await send_email(
                            address, f"{announcement.title} – {reference}",
                            build_announcement_email_html(announcement, branding["club_name"], image_url, reference=reference),
                            db=db,
                        )
                    else:
                        sent = await send_email(address, announcement.title, html_body, db=db)
                    if sent:
                        success_count += 1
                    else:
                        failure_count += 1

                delivery.error_message = f"{success_count + failure_count} of {len(recipients)} sent so far."
                await db.commit()

                is_last_batch = batch_start + EMAIL_BATCH_SIZE >= len(recipients)
                if not is_last_batch:
                    await asyncio.sleep(EMAIL_BATCH_PAUSE_SECONDS)

            delivery.sent_at = datetime.now(timezone.utc)
            if success_count == 0:
                delivery.status = AnnouncementDeliveryStatus.FAILED
                delivery.error_message = f"All {failure_count} send attempts failed (check SMTP configuration under Admin -> Settings)."
            else:
                delivery.status = AnnouncementDeliveryStatus.SENT
                delivery.error_message = (
                    f"{failure_count} of {len(recipients)} recipients could not be reached." if failure_count else None
                )
            await db.commit()
    except Exception:
        logger.exception(f"Announcement email send failed for announcement {announcement_id}")
        try:
            async with AsyncSessionLocal() as db:
                delivery_result = await db.execute(
                    select(AnnouncementDelivery).where(
                        AnnouncementDelivery.announcement_id == announcement_id,
                        AnnouncementDelivery.channel == AnnouncementChannel.EMAIL,
                    )
                )
                delivery = delivery_result.scalar_one_or_none()
                if delivery is not None:
                    delivery.status = AnnouncementDeliveryStatus.FAILED
                    delivery.error_message = "Sending stopped unexpectedly; please check the server logs and try again."
                    delivery.sent_at = datetime.now(timezone.utc)
                    await db.commit()
        except Exception:
            logger.exception(f"Could not even record the failure for announcement {announcement_id}")
