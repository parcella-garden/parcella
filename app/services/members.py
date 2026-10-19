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

from sqlalchemy import delete, func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import active_member_filter
from app.models import Member, MemberEmail, MemberPhone, MemberTag, member_tag_links
from app.services.errors import ServiceError
from app.tag_translations import clean_translations, find_tag_by_name
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


# ---------------------------------------------------------------------------
# Tags (issue #241, ADR 0093): free-form labels, created on first use.
# Names are unique ignoring case -- typing "water team" on one member
# and "Water team" on the next must land on the same tag, or the
# filter would silently split the group in two.
# ---------------------------------------------------------------------------

TAG_NAME_MAX_LENGTH = 100


async def list_tags(db: AsyncSession) -> list[MemberTag]:
    return list((await db.scalars(select(MemberTag).order_by(func.lower(MemberTag.name)))).all())


def _clean_tag_name(name: Optional[str]) -> str:
    name = " ".join((name or "").split())
    if not name:
        raise ServiceError("members.tags.errors.name_required")
    if len(name) > TAG_NAME_MAX_LENGTH:
        raise ServiceError("members.tags.errors.name_too_long", max=TAG_NAME_MAX_LENGTH)
    return name


async def _tag_by_name(db: AsyncSession, name: str) -> Optional[MemberTag]:
    """By name or any of its translations, ignoring case (ADR 0098)."""
    return find_tag_by_name(await list_tags(db), name)


async def tag_member(
    db: AsyncSession, member_id: str, *, tag_id: Optional[str] = None, name: Optional[str] = None,
) -> MemberTag:
    """Puts a tag on a member: an existing one by id, or by name --
    reusing a tag of that name (any case) or creating it. Tagging twice
    is a no-op."""
    if tag_id:
        tag = await db.get(MemberTag, tag_id)
        if tag is None:
            raise ServiceError("members.tags.errors.not_found", http_status=404)
    else:
        clean = _clean_tag_name(name)
        tag = await _tag_by_name(db, clean)
        if tag is None:
            tag = MemberTag(name=clean)
            db.add(tag)
            await db.flush()
    await db.execute(
        pg_insert(member_tag_links).values(member_id=member_id, tag_id=tag.id).on_conflict_do_nothing()
    )
    await db.flush()
    return tag


async def set_member_tags(
    db: AsyncSession, member_id: str, *, tag_ids: list[str], new_names: str = "",
) -> None:
    """The member form's tag section (issue #241 follow-up): the member
    ends up with exactly the ticked existing tags plus the typed new
    ones (comma-separated; an existing name, any case, is reused)."""
    wanted = {tag_id for tag_id in tag_ids if tag_id}
    for name in (new_names or "").split(","):
        if name.strip():
            tag = await _tag_by_name(db, _clean_tag_name(name))
            if tag is None:
                tag = MemberTag(name=_clean_tag_name(name))
                db.add(tag)
                await db.flush()
            wanted.add(tag.id)
    existing = set((await db.scalars(
        select(member_tag_links.c.tag_id).where(member_tag_links.c.member_id == member_id)
    )).all())
    for tag_id in existing - wanted:
        await untag_member(db, member_id, tag_id)
    for tag_id in wanted - existing:
        await tag_member(db, member_id, tag_id=tag_id)


async def untag_member(db: AsyncSession, member_id: str, tag_id: str) -> bool:
    """Deletes the link row (no historization for labels, ADR 0093).
    The tag itself stays, even if no member carries it any more."""
    result = await db.execute(
        delete(member_tag_links).where(
            member_tag_links.c.member_id == member_id, member_tag_links.c.tag_id == tag_id,
        )
    )
    await db.flush()
    return result.rowcount > 0


async def set_tag_translations(db: AsyncSession, tag: MemberTag, values: dict) -> MemberTag:
    """Per-language names (ADR 0098); an empty field removes that language."""
    tag.translations = clean_translations(
        tag, values, await list_tags(db), max_length=TAG_NAME_MAX_LENGTH, error_prefix="members.tags.errors",
    ) or None
    await db.flush()
    return tag


async def rename_tag(db: AsyncSession, tag: MemberTag, name: str) -> MemberTag:
    clean = _clean_tag_name(name)
    existing = await _tag_by_name(db, clean)
    if existing is not None and existing.id != tag.id:
        raise ServiceError("members.tags.errors.name_taken", http_status=409, name=existing.name)
    tag.name = clean
    await db.flush()
    return tag


async def delete_tag(db: AsyncSession, tag: MemberTag) -> None:
    """Removes the tag from every member (links cascade) and the tag."""
    await db.delete(tag)
    await db.flush()


async def count_tag_members(db: AsyncSession) -> dict[str, int]:
    """Tag id -> how many non-deleted members carry it (tags page)."""
    rows = await db.execute(
        select(member_tag_links.c.tag_id, func.count())
        .join(Member, Member.id == member_tag_links.c.member_id)
        .where(Member.deleted_at.is_(None))
        .group_by(member_tag_links.c.tag_id)
    )
    return dict(rows.all())
