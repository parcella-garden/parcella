"""
Issue #167: a member whose membership hasn't started yet (member_since
in the future -- a pending application) must not count as an actual
member anywhere active_member_filter() (app/database.py) is used --
the member list itself, invoices, meeting sign-in sheets, dashboard
counts, etc. Before this fix, active_member_filter() only checked
deleted_at/member_until, never member_since, so a pending applicant
was silently treated as fully active everywhere.

member_since IS NULL is unaffected (treated as "already started", same
as every member before this field existed).

Follow-up (same issue): Member.is_active -- a second, Python-side
mirror of active_member_filter() used by the member list's status
badge and the REST API's active_only filter -- was missed in the
original fix and still showed a pending application as active.

The dedicated /members/?pending_only=true view this issue also added
was removed again in issue #256: applications live in the applicants
module now.
"""
from datetime import date, timedelta

from sqlalchemy import select

from tests.conftest import login, auth_header
from app.database import AsyncSessionLocal, active_member_filter
from app.models import Member, MemberParcel, Parcel, ClubSetting


async def _enable_finances_module():
    async with AsyncSessionLocal() as session:
        session.add(ClubSetting(key="modul_finances", value="true", description="test"))
        await session.commit()


async def _make_run(client, year="2026"):
    r_create = await client.post("/finances/runs", data={
        "year": year, "subject": "Upcoming member test", "issued_date": f"{year}-08-01",
        "due_date": f"{year}-09-01", "footer_text": "",
    })
    assert r_create.status_code in (302, 303)
    return r_create.headers["location"].rstrip("/").split("/")[-1]


async def test_active_member_filter_excludes_future_member_since():
    async with AsyncSessionLocal() as session:
        upcoming = Member(first_name="Upcoming", last_name="Applicant", member_since=date.today() + timedelta(days=30))
        started = Member(first_name="Already", last_name="Started", member_since=date.today() - timedelta(days=1))
        no_since = Member(first_name="NoSince", last_name="Legacy", member_since=None)
        session.add_all([upcoming, started, no_since])
        await session.commit()

        result = await session.execute(select(Member.last_name).where(active_member_filter()))
        last_names = {row[0] for row in result.all()}

    assert "Applicant" not in last_names, "a member whose membership hasn't started yet must not count as active"
    assert "Started" in last_names
    assert "Legacy" in last_names, "member_since IS NULL must be treated as already-started, not excluded"


async def test_members_list_excludes_upcoming_member_by_default(client, admin_user):
    await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})

    async with AsyncSessionLocal() as session:
        session.add(Member(first_name="Pending", last_name="Applicant", member_since=date.today() + timedelta(days=30)))
        await session.commit()

    r_default = await client.get("/members/")
    assert r_default.status_code == 200
    assert "Applicant, Pending" not in r_default.text

    r_include_inactive = await client.get("/members/?include_inactive=true")
    assert r_include_inactive.status_code == 200
    assert "Applicant, Pending" in r_include_inactive.text, "the existing include_inactive escape hatch must still surface them"


async def test_signin_sheet_excludes_upcoming_member(client, admin_user):
    await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})

    async with AsyncSessionLocal() as session:
        parcel = Parcel(plot_number="UPCOMING-1")
        upcoming_member = Member(
            first_name="Pending", last_name="Tenant", member_since=date.today() + timedelta(days=30),
        )
        session.add_all([parcel, upcoming_member])
        await session.flush()
        session.add(MemberParcel(member_id=upcoming_member.id, parcel_id=parcel.id, is_invoice_address=True))
        await session.commit()

    response = await client.post("/members/signin-sheet", data={"headline": "Test"})
    assert response.status_code == 200
    assert "Pending Tenant" not in response.text


async def test_fixed_per_person_invoice_excludes_upcoming_member(client, admin_user):
    await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})
    await _enable_finances_module()

    async with AsyncSessionLocal() as session:
        upcoming_member = Member(
            first_name="Pending", last_name="Payer", member_since=date.today() + timedelta(days=30),
            street="Gartenweg 1", postal_code="12345", city="Testort",
        )
        started_member = Member(
            first_name="Actual", last_name="Payer",
            street="Gartenweg 2", postal_code="12345", city="Testort",
        )
        session.add_all([upcoming_member, started_member])
        await session.commit()

    run_id = await _make_run(client)
    r_item = await client.post(f"/finances/runs/{run_id}/items", data={
        "order_number": "10", "name": "Membership fee", "description": "",
        "pricing_mode": "fixed_per_person", "unit_price": "25.00",
        "applies_to_all_members": "on",
    })
    assert r_item.status_code in (302, 303)

    r_preview = await client.get(f"/finances/runs/{run_id}/preview")
    assert r_preview.status_code == 200
    assert "Pending Payer" not in r_preview.text
    assert "Actual Payer" in r_preview.text


async def test_member_is_active_property_reflects_member_since():
    async with AsyncSessionLocal() as session:
        upcoming = Member(first_name="Upcoming", last_name="Applicant", member_since=date.today() + timedelta(days=30))
        started = Member(first_name="Already", last_name="Started", member_since=date.today() - timedelta(days=1))
        session.add_all([upcoming, started])
        await session.commit()

    assert upcoming.is_active is False, "Member.is_active must mirror active_member_filter()'s member_since check"
    assert started.is_active is True


async def test_pending_only_filter_is_gone(client, admin_user):
    """Issue #256: the "pending applications only" checkbox is gone from
    the member list, and a stale ?pending_only=true link just shows the
    normal list -- an active member included."""
    await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})

    async with AsyncSessionLocal() as session:
        session.add(Member(first_name="Already", last_name="Active", member_since=date.today() - timedelta(days=1)))
        await session.commit()

    response = await client.get("/members/")
    assert response.status_code == 200
    assert 'name="pending_only"' not in response.text

    response = await client.get("/members/?pending_only=true")
    assert response.status_code == 200
    assert "Active, Already" in response.text


async def test_rest_api_active_only_excludes_upcoming_member(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)

    async with AsyncSessionLocal() as session:
        session.add(Member(first_name="Pending", last_name="ApiApplicant", member_since=date.today() + timedelta(days=30)))
        session.add(Member(first_name="Actual", last_name="ApiMember"))
        await session.commit()

    response = await client.get("/api/v1/members?active_only=true", headers=headers)
    assert response.status_code == 200
    names = {(m["first_name"], m["last_name"]) for m in response.json()}

    assert ("Pending", "ApiApplicant") not in names
    assert ("Actual", "ApiMember") in names


async def test_rest_api_active_only_filters_before_pagination_not_after(client, admin_user):
    """ADR 0070: active_only used to filter in Python AFTER limit/offset
    had already been applied in SQL, so a page full of upcoming/inactive
    members (sorted earlier alphabetically) could push real active
    members off the page entirely -- fewer than `limit` rows back, or
    none at all, despite active members existing further down the
    table. Now active_member_filter() (the same one the HTML side always
    used) is applied in SQL before pagination, exactly like the HTML
    list view."""
    token = await login(client, "admin@example.com")
    headers = auth_header(token)

    async with AsyncSessionLocal() as session:
        # Sorted first (by last_name) but NOT active -- would have
        # occupied the whole page under the old Python-post-filter bug.
        session.add(Member(first_name="A1", last_name="AAA Upcoming", member_since=date.today() + timedelta(days=30)))
        session.add(Member(first_name="A2", last_name="AAB Upcoming", member_since=date.today() + timedelta(days=30)))
        # Sorted later, genuinely active.
        session.add(Member(first_name="Z1", last_name="ZZZ Active"))
        session.add(Member(first_name="Z2", last_name="ZZY Active"))
        await session.commit()

    response = await client.get("/api/v1/members?active_only=true&limit=2", headers=headers)
    assert response.status_code == 200
    names = {(m["first_name"], m["last_name"]) for m in response.json()}

    assert len(names) == 2
    assert names == {("Z2", "ZZY Active"), ("Z1", "ZZZ Active")}
