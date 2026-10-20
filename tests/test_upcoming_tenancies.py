"""
ADR 0102: MemberParcel.is_current also requires the tenancy to have
started -- a future assigned_from makes it upcoming, not current, so a
parcel handed over ahead of time never has two current households.
Python property and SQL filter must agree.
"""
from datetime import date, timedelta

from sqlalchemy import select

from app.database import AsyncSessionLocal, current_or_upcoming_tenant_filter, current_tenant_filter
from app.models import Member, MemberParcel, Parcel

TODAY = date.today()
CASES = {
    # name: (assigned_from, assigned_until, current, upcoming, former)
    "open_ended": (None, None, True, False, False),
    "started_today": (TODAY, None, True, False, False),
    "starts_tomorrow": (TODAY + timedelta(days=1), None, False, True, False),
    "notice_given": (TODAY - timedelta(days=100), TODAY + timedelta(days=5), True, False, False),
    "ended_today": (TODAY - timedelta(days=100), TODAY, False, False, True),
    "ended_before_it_began": (TODAY + timedelta(days=10), TODAY - timedelta(days=1), False, False, True),
}


async def test_current_upcoming_former_python_and_sql_agree():
    async with AsyncSessionLocal() as db:
        parcel = Parcel(plot_number="U1")
        db.add(parcel)
        await db.flush()
        rows = {}
        for name, (start, end, *_ ) in CASES.items():
            member = Member(first_name=name, last_name="Test")
            db.add(member)
            await db.flush()
            rows[name] = MemberParcel(member_id=member.id, parcel_id=parcel.id, assigned_from=start, assigned_until=end)
            db.add(rows[name])
        await db.commit()

        for name, (_, _, current, upcoming, former) in CASES.items():
            row = rows[name]
            assert (row.is_current, row.is_upcoming, row.is_former) == (current, upcoming, former), name

        current_ids = set((await db.execute(select(MemberParcel.id).where(current_tenant_filter()))).scalars())
        assert current_ids == {rows[n].id for n, c in CASES.items() if c[2]}
        not_former_ids = set((await db.execute(
            select(MemberParcel.id).where(current_or_upcoming_tenant_filter())
        )).scalars())
        assert not_former_ids == {rows[n].id for n, c in CASES.items() if not c[4]}
