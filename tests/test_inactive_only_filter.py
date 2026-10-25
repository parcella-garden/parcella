"""
Issue #169: /members/?include_inactive=true was the plain complement
of "deleted_at IS NULL" -- i.e. every non-deleted member, active ones
included -- rather than actually filtering to inactive members only.
The real complement of active_member_filter() is an OR (either half
failing makes a member inactive), not the AND active_member_filter()
itself uses.

A member with a blank member_since/member_until (still "active" per
active_member_filter(), unchanged -- see tests/test_upcoming_members.py)
must NOT show up here.
"""
from datetime import date, timedelta

from app.database import AsyncSessionLocal
from app.models import Member


async def test_inactive_only_excludes_active_member(client, admin_user):
    await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})

    async with AsyncSessionLocal() as session:
        session.add(Member(first_name="Fully", last_name="Active", member_since=date.today() - timedelta(days=100)))
        await session.commit()

    response = await client.get("/members/?include_inactive=true")
    assert response.status_code == 200
    assert "Active, Fully" not in response.text, "an active member must not appear in the inactive-only view"


async def test_inactive_only_includes_expired_member(client, admin_user):
    await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})

    async with AsyncSessionLocal() as session:
        session.add(Member(first_name="Long", last_name="Expired", member_until=date.today() - timedelta(days=1)))
        await session.commit()

    r_default = await client.get("/members/")
    assert "Expired, Long" not in r_default.text

    r_inactive = await client.get("/members/?include_inactive=true")
    assert r_inactive.status_code == 200
    assert "Expired, Long" in r_inactive.text


async def test_inactive_only_includes_not_yet_started_member(client, admin_user):
    await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})

    async with AsyncSessionLocal() as session:
        session.add(Member(first_name="Not", last_name="YetStarted", member_since=date.today() + timedelta(days=10)))
        await session.commit()

    r_default = await client.get("/members/")
    assert "YetStarted, Not" not in r_default.text

    r_inactive = await client.get("/members/?include_inactive=true")
    assert r_inactive.status_code == 200
    assert "YetStarted, Not" in r_inactive.text


async def test_inactive_only_excludes_member_with_blank_dates(client, admin_user):
    """A blank member_since/member_until still counts as active per
    active_member_filter() itself (unchanged) -- must not show up here."""
    await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})

    async with AsyncSessionLocal() as session:
        session.add(Member(first_name="Sophia", last_name="Möbius", member_since=None, member_until=None))
        await session.commit()

    response = await client.get("/members/?include_inactive=true")
    assert response.status_code == 200
    assert "Möbius, Sophia" not in response.text
