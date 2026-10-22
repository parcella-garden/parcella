"""
Helpdesk conversation poller: fetches new/updated conversations from the
active helpdesk and upserts app.models.HelpdeskConversationLink rows.
Called every 5 minutes from app/main.py's lifespan (same
asyncio-loop-in-lifespan pattern as the update-check / cloud-backup
loops -- no Celery, no separate worker). Only runs for a helpdesk with
the INBOX capability.

Idempotent by design: conversations are upserted by (provider,
external_id) -- find-or-create, never a blind insert -- so a re-poll of
an already-seen conversation updates the existing row instead of
duplicating it.

Only conversation *metadata* is persisted here. The actual transcript is
fetched live when a conversation's detail page is opened
(app/routers/support.py) -- never duplicated into this table.
"""
import logging
from typing import Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import current_tenant_filter
from app.helpdesk.base import (
    HIDDEN_STATUSES, INBOX, STATUS_DELETED, HelpdeskConversation, HelpdeskError, HelpdeskProvider,
)
from app.member_matching import find_members_by_email
from app.models import HelpdeskConversationLink, HelpdeskCustomerId, Member, MemberParcel

logger = logging.getLogger(__name__)


async def _current_single_parcel_id(db: AsyncSession, member_id: str) -> Optional[str]:
    result = await db.execute(
        select(MemberParcel.parcel_id).where(MemberParcel.member_id == member_id, current_tenant_filter())
    )
    parcel_ids = result.scalars().all()
    return parcel_ids[0] if len(parcel_ids) == 1 else None


async def remember_customer_id(db: AsyncSession, member_id: str, provider: str, customer_id: Optional[str]) -> None:
    """Stores the member's customer id in this helpdesk, unless the member
    already has one there or the id already belongs to someone."""
    if not customer_id:
        return
    existing = await db.scalar(select(HelpdeskCustomerId.id).where(
        ((HelpdeskCustomerId.member_id == member_id) & (HelpdeskCustomerId.provider == provider))
        | ((HelpdeskCustomerId.provider == provider) & (HelpdeskCustomerId.customer_id == customer_id))
    ))
    if existing is None:
        db.add(HelpdeskCustomerId(member_id=member_id, provider=provider, customer_id=customer_id))


async def customer_id_for(db: AsyncSession, member_id: str, provider: str) -> Optional[str]:
    return await db.scalar(select(HelpdeskCustomerId.customer_id).where(
        HelpdeskCustomerId.member_id == member_id, HelpdeskCustomerId.provider == provider,
    ))


async def _resolve_member_and_parcel(
    db: AsyncSession, provider: str, customer_id: Optional[str], customer_email: Optional[str],
) -> Tuple[Optional[str], Optional[str]]:
    """Matching hierarchy (docs/module-support.md):
    1. A stored HelpdeskCustomerId for this helpdesk -- exact, persisted.
    2. Else find_members_by_email() -- exactly one match auto-associates
       and stores the customer id for next time; more than one
       (ambiguous) or zero (no match) leaves it unassociated. Never
       guesses.
    Parcel is auto-set only when the resolved member has exactly one
    *current* parcel; left None (shown as a selector in the UI) otherwise.
    """
    member: Optional[Member] = None

    if customer_id:
        result = await db.execute(
            select(Member).join(HelpdeskCustomerId, HelpdeskCustomerId.member_id == Member.id).where(
                HelpdeskCustomerId.provider == provider, HelpdeskCustomerId.customer_id == customer_id,
                Member.deleted_at.is_(None),
            )
        )
        member = result.scalar_one_or_none()

    if member is None and customer_email:
        candidates = await find_members_by_email(db, customer_email)
        if len(candidates) == 1:
            member = candidates[0]
            await remember_customer_id(db, member.id, provider, customer_id)
        # len == 0 (no match) or > 1 (ambiguous): leave unassociated,
        # surfaced in the staff UI for manual association -- never guess.

    if member is None:
        return None, None
    return member.id, await _current_single_parcel_id(db, member.id)


async def sync_helpdesk_conversations(db: AsyncSession, provider: HelpdeskProvider) -> int:
    """Fetches conversations updated since the last successful sync of
    this helpdesk and upserts them, then reconciles deletions. Returns
    the number of conversations upserted this run."""
    if not provider.can(INBOX):
        return 0
    last_updated = await db.scalar(
        select(func.max(HelpdeskConversationLink.external_updated_at))
        .where(HelpdeskConversationLink.provider == provider.type)
    )
    conversations = await provider.list_conversations(updated_since=last_updated)
    for conversation in conversations:
        await _upsert_conversation(db, provider.type, conversation)
    if conversations:
        await db.commit()

    await _reconcile_deletions(db, provider)
    return len(conversations)


async def _reconcile_deletions(db: AsyncSession, provider: HelpdeskProvider) -> None:
    """A deleted conversation usually just stops being returned by the
    incremental list rather than being reported as changed, so the sync
    can never notice it there. Instead, re-check every visible local row
    of this helpdesk directly by id -- one lightweight request per row,
    bounded by how many conversations Parcella has synced, which is fine
    at a club's traffic volume."""
    result = await db.execute(
        select(HelpdeskConversationLink).where(
            HelpdeskConversationLink.provider == provider.type,
            HelpdeskConversationLink.status.notin_(HIDDEN_STATUSES),
        )
    )
    changed = False
    for link in result.scalars().all():
        try:
            current = await provider.get_status(link.external_id)
        except HelpdeskError as e:
            logger.warning(f"Could not check {provider.label} conversation {link.external_id}: {e}")
            continue
        current = current or STATUS_DELETED
        if current != link.status:
            link.status = current
            changed = True
    if changed:
        await db.commit()


async def _upsert_conversation(db: AsyncSession, provider: str, conversation: HelpdeskConversation) -> None:
    result = await db.execute(
        select(HelpdeskConversationLink).where(
            HelpdeskConversationLink.provider == provider,
            HelpdeskConversationLink.external_id == conversation.external_id,
        )
    )
    link = result.scalar_one_or_none()

    member_id, parcel_id = (None, None)
    # Only re-run matching for rows that don't already have a member --
    # once staff has associated (or the automation auto-matched) a
    # conversation, a re-poll must never silently re-guess or clobber it.
    if (link is None or link.member_id is None) and conversation.customer_email:
        member_id, parcel_id = await _resolve_member_and_parcel(
            db, provider, conversation.customer_id, conversation.customer_email,
        )

    if link is None:
        db.add(HelpdeskConversationLink(
            provider=provider,
            external_id=conversation.external_id,
            mailbox_id=conversation.mailbox_id,
            subject=(conversation.subject or "")[:255],
            customer_email=conversation.customer_email or "",
            customer_name=conversation.customer_name,
            status=conversation.status,
            message_count=conversation.message_count,
            member_id=member_id,
            parcel_id=parcel_id,
            external_updated_at=conversation.updated_at,
        ))
    else:
        link.subject = (conversation.subject or link.subject)[:255]
        link.customer_email = conversation.customer_email or link.customer_email
        link.customer_name = conversation.customer_name or link.customer_name
        link.status = conversation.status
        if conversation.mailbox_id is not None:
            link.mailbox_id = conversation.mailbox_id
        if conversation.message_count is not None:
            link.message_count = conversation.message_count
        link.external_updated_at = conversation.updated_at
        if member_id is not None:
            link.member_id = member_id
            link.parcel_id = parcel_id

    await db.flush()
