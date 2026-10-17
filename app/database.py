from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.config import settings

engine = create_async_engine(
    settings.database_url,
    echo=settings.is_development,
    pool_pre_ping=True,
    pool_recycle=1800,  # proactively refresh connections after 30 min,
                        # prevents "MissingGreenlet" errors on long-idle/
                        # stale connections
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Creates all tables (development only; Alembic handles production)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

from datetime import date as _date
from sqlalchemy import and_ as _and_

def active_member_filter():
    """
    Default filter for active members:
    - not soft-deleted (deleted_at IS NULL)
    - membership already started (member_since IS NULL or today or earlier)
    - membership not expired (member_until IS NULL or in the future)

    member_since IS NULL is treated as "already started" (no
    restriction), same as member_until IS NULL means "no end date" --
    this keeps every pre-existing member without a member_since value
    unaffected (issue #167: a member whose membership hasn't started
    yet -- a pending application -- must not count as an actual member
    anywhere this shared filter is used: invoices, meeting sign-in
    sheets, dashboard counts, birthdays, work-hours/inventory/ticket
    member pickers, etc.).

    Usage: .where(active_member_filter())
    """
    from app.models import Member
    return _and_(
        Member.deleted_at.is_(None),
        (Member.member_since.is_(None)) | (Member.member_since <= _date.today()),
        (Member.member_until.is_(None)) | (Member.member_until >= _date.today())
    )


def current_tenant_filter():
    """
    Default filter for current MemberParcel tenancy rows:
    - never terminated (assigned_until IS NULL), or
    - terminated with a future end date (assigned_until in the future --
      the termination hasn't taken effect yet, see issue #130)

    Strict ">" (not ">="), matching MemberParcel.is_current: a tenancy
    becomes former on its assigned_until date itself, not the day before.

    Usage: .where(current_tenant_filter())
    """
    from app.models import MemberParcel
    return (MemberParcel.assigned_until.is_(None)) | (MemberParcel.assigned_until > _date.today())


def tenant_in_year_filter(year: int):
    """
    MemberParcel rows that were in effect on at least one day of `year`
    -- SQL twin of MemberParcel.overlaps_year(), used by the work-hours
    evaluation (issue #239): a lease cancelled partway through the year
    still owes that year's hours, so "current today" is the wrong test
    there.

    Usage: .where(tenant_in_year_filter(2026))
    """
    from app.models import MemberParcel
    return _and_(
        (MemberParcel.assigned_from.is_(None)) | (MemberParcel.assigned_from <= _date(year, 12, 31)),
        (MemberParcel.assigned_until.is_(None)) | (MemberParcel.assigned_until > _date(year, 1, 1)),
    )
