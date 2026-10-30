"""
Issue #263: the dashboard's Members card shows the average age of active
members to one decimal place. Exact ages (fraction since the last
birthday included), only members with a date of birth on file, same
population as the card's headline count (active_member_filter()).
"""
from datetime import date, timedelta

import pytest

from app.birthdays import DAYS_PER_YEAR, average_age, exact_age
from app.database import AsyncSessionLocal
from app.models import Member
from tests.conftest import auth_header, login


def test_exact_age_counts_the_fraction_since_the_last_birthday():
    today = date(2026, 10, 30)
    assert exact_age(date(1976, 10, 30), today) == pytest.approx(50.0, abs=0.01)
    # Half a year past the 50th birthday is 50.5, not 50.
    assert exact_age(date(1976, 4, 30), today) == pytest.approx(50.5, abs=0.01)


async def test_average_age_is_none_without_any_birth_dates(client):
    async with AsyncSessionLocal() as session:
        session.add(Member(first_name="No", last_name="Birthday"))
        await session.commit()
        assert await average_age(session) is None


async def test_average_age_skips_former_members_and_missing_birth_dates(client):
    today = date.today()
    async with AsyncSessionLocal() as session:
        session.add(Member(first_name="Forty", last_name="Ish", date_of_birth=today - timedelta(days=round(40 * DAYS_PER_YEAR))))
        session.add(Member(first_name="Sixty", last_name="Ish", date_of_birth=today - timedelta(days=round(60 * DAYS_PER_YEAR))))
        session.add(Member(first_name="No", last_name="Birthday"))
        session.add(Member(
            first_name="Former", last_name="Member",
            date_of_birth=today - timedelta(days=round(90 * DAYS_PER_YEAR)),
            member_until=today - timedelta(days=1),
        ))
        await session.commit()
        assert await average_age(session) == pytest.approx(50.0, abs=0.01)


async def test_dashboard_and_api_show_the_average_age(client, admin_user):
    today = date.today()
    async with AsyncSessionLocal() as session:
        session.add(Member(first_name="A", last_name="Member", date_of_birth=today - timedelta(days=round(42 * DAYS_PER_YEAR))))
        session.add(Member(first_name="B", last_name="Member", date_of_birth=today - timedelta(days=round(43 * DAYS_PER_YEAR))))
        await session.commit()

    await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})
    r = await client.get("/")
    assert r.status_code == 200
    # Default region is de_DE (decimal comma), independent of the English UI.
    assert "Average age 42,5 years" in r.text

    token = await login(client, "admin@example.com")
    r = await client.get("/api/v1/stats", headers=auth_header(token))
    assert r.status_code == 200
    assert r.json()["members_average_age"] == pytest.approx(42.5, abs=0.01)


async def test_dashboard_hides_the_line_without_any_birth_dates(client, admin_user):
    await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})
    r = await client.get("/")
    assert r.status_code == 200
    assert "Average age" not in r.text
