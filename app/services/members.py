"""
Shared member business logic, called by both app/routers/members.py
(HTML) and app/routers/api_members.py (API) -- see ADR 0070.

CRUD only -- there's no business-rule branching here the way tickets'
status transitions or purchase_requests' four-eyes rule have. The one
real bug this closes: `active_member_filter()` (app/database.py, SQL)
and `Member.is_active` (app/models.py, Python) are two independent
reimplementations of "what counts as an active member" that have
already drifted once in production (issue #167, see Member.is_active's
own docstring) -- api_members.py used to post-filter in Python after
pagination instead of pushing active_member_filter() into SQL like the
HTML side always has. Both routers now build their "active" query the
same way, via `active_members_query()` below.
"""
import logging
from datetime import date, datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import active_member_filter
from app.models import Member, MemberEmail, MemberPhone
from app.freescout_client import FreeScoutError, get_freescout_client

logger = logging.getLogger(__name__)


def _clean(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    value = value.strip()
    return value or None


def active_members_query(base_query):
    """Applies the canonical "active member" filter to an existing
    select(Member)-based query, pushed into SQL so it composes safely
    with .limit()/.offset() -- the bug this fixes was filtering in
    Python *after* pagination, which can return fewer than `limit` rows
    or skip an active member entirely depending on offset."""
    return base_query.where(active_member_filter())


async def create_member(
    db: AsyncSession,
    *,
    first_name: str,
    last_name: str,
    street: Optional[str] = None,
    postal_code: Optional[str] = None,
    city: Optional[str] = None,
    date_of_birth: Optional[date] = None,
    iban: Optional[str] = None,
    member_since: Optional[date] = None,
    member_until: Optional[date] = None,
    email_notifications: bool = False,
    notes: Optional[str] = None,
) -> Member:
    member = Member(
        first_name=_clean(first_name),
        last_name=_clean(last_name),
        street=_clean(street),
        postal_code=_clean(postal_code),
        city=_clean(city),
        date_of_birth=date_of_birth,
        iban=_clean(iban),
        member_since=member_since,
        member_until=member_until,
        email_notifications=email_notifications,
        notes=_clean(notes),
    )
    db.add(member)
    await db.flush()
    return member


async def update_member(db: AsyncSession, member: Member, **fields) -> Member:
    """Partial update: only keys present in `fields` are changed. String
    fields are normalized (stripped, blank -> None) the same way for
    both callers."""
    string_fields = {"first_name", "last_name", "street", "postal_code", "city", "iban", "notes"}
    name_changed = (
        ("first_name" in fields and _clean(fields["first_name"]) != member.first_name)
        or ("last_name" in fields and _clean(fields["last_name"]) != member.last_name)
    )
    for key, value in fields.items():
        if key in string_fields and value is not None:
            value = _clean(value)
        setattr(member, key, value)
    await db.flush()

    # Keep an already-linked FreeScout customer's name in sync (see
    # app/freescout_client.py, docs/module-freescout-bridge.md). Only
    # members that have actually been matched to a conversation ever get
    # a freescout_customer_id in the first place (lazy push, not
    # proactive for every member) -- nothing to do otherwise. Never
    # blocks the member update if FreeScout is unreachable/unconfigured.
    if name_changed and member.freescout_customer_id is not None:
        client = await get_freescout_client(db)
        if client is not None:
            try:
                await client.update_customer(
                    member.freescout_customer_id, first_name=member.first_name, last_name=member.last_name,
                )
            except FreeScoutError as e:
                logger.warning(f"Could not update FreeScout customer for member {member.id}: {e}")

    return member


async def soft_delete_member(db: AsyncSession, member: Member) -> None:
    """Sets deleted_at -- already-recorded parcel assignments, work
    sessions etc. remain unchanged, no FK cascade, since there's no
    real DELETE."""
    member.deleted_at = datetime.now(timezone.utc)
    await db.flush()


async def add_phone(
    db: AsyncSession, member_id: str, *, number: str, label: Optional[str] = None, is_primary: bool = False,
) -> MemberPhone:
    phone = MemberPhone(
        member_id=member_id, number=number.strip(), label=_clean(label), is_primary=is_primary,
    )
    db.add(phone)
    await db.flush()
    return phone


async def remove_phone(db: AsyncSession, member_id: str, phone_id: str) -> bool:
    result = await db.execute(
        select(MemberPhone).where(MemberPhone.id == phone_id, MemberPhone.member_id == member_id)
    )
    phone = result.scalar_one_or_none()
    if phone is None:
        return False
    await db.delete(phone)
    await db.flush()
    return True


async def add_email(
    db: AsyncSession, member_id: str, *, address: str, label: Optional[str] = None, is_primary: bool = False,
) -> MemberEmail:
    email_obj = MemberEmail(
        member_id=member_id, address=address.strip().lower(), label=_clean(label), is_primary=is_primary,
    )
    db.add(email_obj)
    await db.flush()
    return email_obj


async def remove_email(db: AsyncSession, member_id: str, email_id: str) -> bool:
    result = await db.execute(
        select(MemberEmail).where(MemberEmail.id == email_id, MemberEmail.member_id == member_id)
    )
    email_obj = result.scalar_one_or_none()
    if email_obj is None:
        return False
    await db.delete(email_obj)
    await db.flush()
    return True
