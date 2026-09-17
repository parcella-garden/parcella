"""
FreeScout conversation poller: fetches new/updated conversations from
the configured mailbox and upserts app.models.FreescoutConversationLink
rows. Called every 5 minutes from app/main.py's lifespan (same
asyncio-loop-in-lifespan pattern as the old ticket-IMAP poller /
update-check / cloud-backup loops -- no Celery, no separate worker).

Idempotent by design: conversations are upserted by
freescout_conversation_id (find-or-create, never a blind insert), so a
re-poll of an already-seen conversation updates the existing row instead
of duplicating it -- safe under retries, duplicate FreeScout webhooks
aren't even a concern here since this project polls rather than
receives events.

Only conversation *metadata* is persisted here. The actual message
transcript is fetched live from FreeScout's API when a conversation's
detail page is opened (app/routers/freescout.py) -- never duplicated
into this table. See docs/module-freescout-bridge.md.
"""
import logging
from datetime import datetime, timezone
from typing import Optional, Tuple

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import current_tenant_filter
from app.freescout_client import FreeScoutClient, FreeScoutError
from app.member_matching import find_members_by_email
from app.models import FreescoutConversationLink, Member, MemberParcel

logger = logging.getLogger(__name__)

# FreeScout conversation statuses (app.models.FreescoutConversationLink.
# freescout_status, stored as FreeScout's own raw string) that are no
# longer actionable -- excluded from the staff-facing list views
# (app/routers/freescout.py, app/routers/api_freescout.py) and the
# dashboard's "needs association" stat, but still synced/kept up to
# date normally: a closed conversation that gets reopened in FreeScout
# must still have an accurate, already-matched member_id waiting for it,
# not silently stale rows nobody bothered to keep synced.
HIDDEN_STATUSES = ("closed", "deleted")


def _parse_datetime(value: Optional[str]) -> datetime:
    """Parses FreeScout's documented ISO-8601 UTC format
    ("YYYY-MM-DDThh:mm:ssZ"). datetime.fromisoformat() handles the
    trailing "Z" natively (Python 3.11+; this project targets 3.12) --
    no need for an extra dependency."""
    if not value:
        return datetime.now(timezone.utc)
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        logger.warning(f"Could not parse FreeScout timestamp {value!r}, using now() instead.")
        return datetime.now(timezone.utc)


def _extract_customer(conversation: dict) -> dict:
    """FreeScout embeds the customer either directly under "customer" or
    under "_embedded.customer" depending on endpoint/version -- accept
    either shape rather than assuming one."""
    customer = conversation.get("customer") or conversation.get("_embedded", {}).get("customer") or {}
    email = customer.get("email")
    if not email:
        emails = customer.get("emails") or []
        email = emails[0]["value"] if emails and isinstance(emails[0], dict) else (emails[0] if emails else None)
    name_parts = [customer.get("firstName"), customer.get("lastName")]
    name = " ".join(p for p in name_parts if p) or None
    return {"id": customer.get("id"), "email": email, "name": name}


async def _current_single_parcel_id(db: AsyncSession, member_id: str) -> Optional[str]:
    result = await db.execute(
        select(MemberParcel.parcel_id).where(MemberParcel.member_id == member_id, current_tenant_filter())
    )
    parcel_ids = result.scalars().all()
    return parcel_ids[0] if len(parcel_ids) == 1 else None


async def _resolve_member_and_parcel(
    db: AsyncSession, customer_id: Optional[int], customer_email: Optional[str],
) -> Tuple[Optional[str], Optional[str]]:
    """Matching hierarchy (docs/module-freescout-bridge.md):
    1. Member.freescout_customer_id == customer_id -- exact, persisted.
    2. Else find_members_by_email() -- exactly one match auto-associates
       and backfills freescout_customer_id for next time; more than one
       (ambiguous) or zero (no match) leaves it unassociated. Never
       guesses.
    Parcel is auto-set only when the resolved member has exactly one
    *current* parcel; left None (shown as a selector in the UI) otherwise.
    """
    member: Optional[Member] = None

    if customer_id is not None:
        result = await db.execute(
            select(Member).where(Member.freescout_customer_id == customer_id, Member.deleted_at.is_(None))
        )
        member = result.scalar_one_or_none()

    if member is None and customer_email:
        candidates = await find_members_by_email(db, customer_email)
        if len(candidates) == 1:
            member = candidates[0]
            if customer_id is not None and member.freescout_customer_id is None:
                member.freescout_customer_id = customer_id
        # len == 0 (no match) or > 1 (ambiguous): leave unassociated,
        # surfaced in the staff UI for manual association -- never guess.

    if member is None:
        return None, None

    parcel_id = await _current_single_parcel_id(db, member.id)
    return member.id, parcel_id


async def sync_freescout_conversations(db: AsyncSession, client: FreeScoutClient) -> int:
    """Fetches conversations updated since the last successful sync and
    upserts them, then reconciles deletions (see _reconcile_deletions).
    Returns the number of conversations upserted this run (deletions
    detected by reconciliation are not counted -- they're a correction,
    not new activity)."""
    last_updated = await db.scalar(select(func.max(FreescoutConversationLink.freescout_updated_at)))
    updated_since = last_updated.strftime("%Y-%m-%dT%H:%M:%SZ") if last_updated else None

    conversations = await client.list_all_conversations(updated_since=updated_since)
    count = 0
    for conversation in conversations:
        await _upsert_conversation(db, conversation)
        count += 1

    if count:
        await db.commit()

    await _reconcile_deletions(db, client)
    return count


async def _reconcile_deletions(db: AsyncSession, client: FreeScoutClient) -> None:
    """FreeScout represents a deleted conversation via a separate `state`
    field (or simply a 404 on refetch), not via the `status` values
    (active/pending/closed/spam) the incremental updatedSince-based sync
    above watches -- a deleted conversation just stops being returned by
    list_all_conversations() rather than being reported as changed, so it
    can never be caught there. Instead, re-check every currently-visible
    (non-hidden) local row directly by ID; one lightweight GET per row,
    bounded by how many conversations Parcella has actually synced so
    far, not by the mailbox's full history -- acceptable at a small
    club's traffic volume (same trade-off already accepted elsewhere in
    this project, e.g. docs/module-public-api.md)."""
    result = await db.execute(
        select(FreescoutConversationLink).where(FreescoutConversationLink.freescout_status.notin_(HIDDEN_STATUSES))
    )
    changed = False
    for link in result.scalars().all():
        try:
            current_status = await client.get_conversation_state(link.freescout_conversation_id)
        except FreeScoutError as e:
            logger.warning(f"Could not check FreeScout conversation {link.freescout_conversation_id}: {e}")
            continue

        if current_status is None:
            link.freescout_status = "deleted"
            changed = True
        elif current_status != link.freescout_status:
            link.freescout_status = current_status
            changed = True

    if changed:
        await db.commit()


async def _upsert_conversation(db: AsyncSession, conversation: dict) -> None:
    freescout_id = conversation["id"]
    customer = _extract_customer(conversation)

    result = await db.execute(
        select(FreescoutConversationLink).where(FreescoutConversationLink.freescout_conversation_id == freescout_id)
    )
    link = result.scalar_one_or_none()

    member_id, parcel_id = (None, None)
    # Only re-run matching for rows that don't already have a member --
    # once staff has associated (or the automation auto-matched) a
    # conversation, a re-poll must never silently re-guess or clobber it.
    if link is None or link.member_id is None:
        if customer.get("email"):
            member_id, parcel_id = await _resolve_member_and_parcel(db, customer.get("id"), customer.get("email"))

    if link is None:
        link = FreescoutConversationLink(
            freescout_conversation_id=freescout_id,
            freescout_mailbox_id=conversation.get("mailboxId"),
            subject=conversation.get("subject", ""),
            customer_email=customer.get("email") or "",
            customer_name=customer.get("name"),
            freescout_status=conversation.get("status", "active"),
            message_count=conversation.get("threadsCount"),
            member_id=member_id,
            parcel_id=parcel_id,
            freescout_updated_at=_parse_datetime(conversation.get("updatedAt")),
        )
        db.add(link)
    else:
        link.subject = conversation.get("subject", link.subject)
        link.customer_email = customer.get("email") or link.customer_email
        link.customer_name = customer.get("name") or link.customer_name
        link.freescout_status = conversation.get("status", link.freescout_status)
        if conversation.get("threadsCount") is not None:
            link.message_count = conversation.get("threadsCount")
        link.freescout_updated_at = _parse_datetime(conversation.get("updatedAt"))
        if member_id is not None:
            link.member_id = member_id
            link.parcel_id = parcel_id

    await db.flush()
