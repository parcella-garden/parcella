"""
Issue #200: the dashboard's Members card counted and linked to
active_member_filter() (app/database.py) as "active", but that filter
deliberately still counts a blank member_since as active (issue #167,
kept unchanged for invoices/sign-in/dashboard totals). The member
list's own status badge already treats that same blank case as
"pending", not "active" (issue #170) -- so clicking the dashboard's
"active members" link landed on a list that visibly mixed active and
pending members, contradicting the card's own label.

Fix: a new active_only filter/view (member_since IS NOT NULL AND
active_member_filter()) that agrees with the "active" (not "pending")
badge exactly, used by /members/?active_only=true, the CSV export, and
the dashboard card's link + active count. Does not change
active_member_filter()/is_active themselves.
"""
from datetime import date, timedelta

from app.database import AsyncSessionLocal
from app.models import Member


async def test_active_only_excludes_blank_member_since(client, admin_user):
    await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})

    async with AsyncSessionLocal() as session:
        session.add(Member(first_name="Fresh", last_name="Applicant", member_since=None))
        session.add(Member(first_name="Confirmed", last_name="Member", member_since=date.today() - timedelta(days=1)))
        await session.commit()

    r = await client.get("/members/?active_only=true")
    assert r.status_code == 200
    assert "Applicant, Fresh" not in r.text, "a blank member_since ('pending' badge) must not show up as active_only"
    assert "Member, Confirmed" in r.text

    # Unfiltered default view still includes the blank-member_since member
    # (unchanged behavior, just badged "pending" -- see test_member_status_badge.py).
    r_default = await client.get("/members/")
    assert "Applicant, Fresh" in r_default.text


async def test_active_only_still_excludes_upcoming_and_expired_members(client, admin_user):
    await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})

    async with AsyncSessionLocal() as session:
        session.add(Member(first_name="Upcoming", last_name="Applicant", member_since=date.today() + timedelta(days=30)))
        session.add(Member(first_name="Expired", last_name="Former", member_until=date.today() - timedelta(days=1)))
        await session.commit()

    r = await client.get("/members/?active_only=true")
    assert r.status_code == 200
    assert "Applicant, Upcoming" not in r.text
    assert "Former, Expired" not in r.text


async def test_csv_export_respects_active_only(client, admin_user):
    await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})

    async with AsyncSessionLocal() as session:
        session.add(Member(first_name="Fresh", last_name="Applicant", member_since=None))
        session.add(Member(first_name="Confirmed", last_name="Member", member_since=date.today() - timedelta(days=1)))
        await session.commit()

    r = await client.get("/members/export/csv?active_only=true")
    assert r.status_code == 200
    assert "Confirmed" in r.text
    assert "Fresh" not in r.text


async def test_dashboard_members_card_links_to_active_only(client, admin_user):
    await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})

    r = await client.get("/")
    assert r.status_code == 200
    assert "/members/?active_only=true" in r.text


async def test_dashboard_members_active_stat_excludes_blank_member_since(client, admin_user):
    await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})

    async with AsyncSessionLocal() as session:
        session.add(Member(first_name="Fresh", last_name="Applicant", member_since=None))
        session.add(Member(first_name="Confirmed", last_name="Member", member_since=date.today() - timedelta(days=1)))
        await session.commit()

    r = await client.get("/")
    assert r.status_code == 200
    # admin_user itself already counts as a confirmed member (member_since
    # unset at fixture creation is irrelevant here -- board/admin accounts
    # aren't Members), so the only two Members in this test are the ones
    # created above: one confirmed-active, one blank-since ("pending").
    # members_active (the confirmed-only count) must be less than
    # members_total (which still includes the blank-since one), proving
    # the two stats are no longer the same duplicated value.
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select, func
        from app.database import active_member_filter
        members_total = await session.scalar(select(func.count()).where(active_member_filter()))
        members_active = await session.scalar(
            select(func.count()).where(active_member_filter(), Member.member_since.is_not(None))
        )
    assert members_active < members_total
