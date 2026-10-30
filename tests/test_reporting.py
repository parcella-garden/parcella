"""
Reporting module (issue #264): each figure in app/reporting.py, the
page and the API. Definitions: docs/module-reporting.md.
"""
from datetime import date, datetime, timezone

import pytest

from app.database import AsyncSessionLocal
from app.models import (
    Applicant, HoursTransfer, Member, MemberParcel, MeteringMedium, MeteringPoint, MeteringPointType, Parcel,
    ParcelStatus,
)
from app.reporting import (
    applicants_per_quarter_report, applicants_per_year_report, cancelled_plots_report, electricity_report,
    generation_of, generations_report, hours_transfers_report, members_per_year_report, work_hours_category,
)
from tests.conftest import auth_header, login

TODAY = date(2026, 10, 30)


def _values(report, series=0):
    return dict(zip(report.labels, report.series[series].values))


@pytest.mark.parametrize("year, expected", [
    (1930, "silent"), (1945, "silent"), (1946, "boomers"), (1964, "boomers"), (1965, "gen_x"),
    (1980, "gen_x"), (1981, "millennials"), (1996, "millennials"), (1997, "gen_z"), (2012, "gen_z"),
    (2013, "alpha"),
])
def test_generation_boundaries(year, expected):
    assert generation_of(year) == expected


async def test_generations_count_active_members_and_report_missing_birth_dates(client):
    async with AsyncSessionLocal() as session:
        session.add_all([
            Member(first_name="A", last_name="Boomer", date_of_birth=date(1950, 1, 1)),
            Member(first_name="B", last_name="Boomer", date_of_birth=date(1964, 12, 31)),
            Member(first_name="C", last_name="Millennial", date_of_birth=date(1990, 6, 1)),
            Member(first_name="D", last_name="NoBirthday"),
            Member(first_name="E", last_name="Former", date_of_birth=date(1950, 1, 1), member_until=date(2020, 1, 1)),
        ])
        await session.commit()
        report = await generations_report(session, TODAY)

    assert _values(report) == {"silent": 0, "boomers": 2, "gen_x": 0, "millennials": 1, "gen_z": 0, "alpha": 0}
    assert report.note_params == {"count": 1}


async def test_members_per_year_counts_blank_join_date_in_every_year(client):
    async with AsyncSessionLocal() as session:
        session.add_all([
            Member(first_name="Always", last_name="There"),  # no member_since
            Member(first_name="Joined", last_name="2024", member_since=date(2024, 3, 1)),
            Member(first_name="Left", last_name="2025", member_since=date(2022, 1, 1), member_until=date(2025, 6, 30)),
            Member(first_name="Deleted", last_name="X", member_since=date(2022, 1, 1),
                   deleted_at=datetime(2026, 1, 1, tzinfo=timezone.utc)),
        ])
        await session.commit()
        report = await members_per_year_report(session, TODAY)

    assert report.labels == ["2022", "2023", "2024", "2025", "2026"]
    assert _values(report) == {"2022": 2, "2023": 2, "2024": 3, "2025": 2, "2026": 2}
    assert report.note_params == {"count": 1}


async def test_cancelled_plots_are_leases_ending_in_the_year(client):
    async with AsyncSessionLocal() as session:
        member = Member(first_name="Te", last_name="Nant")
        parcels = [Parcel(plot_number=f"R{i}", status=ParcelStatus.ACTIVE) for i in range(4)]
        session.add_all([member, *parcels])
        await session.flush()
        session.add_all([
            MemberParcel(member_id=member.id, parcel_id=parcels[0].id, assigned_until=date(2024, 12, 31)),
            MemberParcel(member_id=member.id, parcel_id=parcels[1].id, assigned_until=date(2026, 3, 31)),
            MemberParcel(member_id=member.id, parcel_id=parcels[2].id, assigned_until=date(2026, 12, 31)),  # scheduled
            MemberParcel(member_id=member.id, parcel_id=parcels[3].id),  # running lease
        ])
        await session.commit()
        report = await cancelled_plots_report(session, TODAY)

    assert _values(report) == {"2024": 1, "2025": 0, "2026": 2}


async def test_applicants_per_quarter_and_year(client):
    async with AsyncSessionLocal() as session:
        for applied in (datetime(2025, 2, 1), datetime(2026, 4, 1), datetime(2026, 5, 1), datetime(2026, 10, 1)):
            session.add(Applicant(email="a@example.com", applied_at=applied.replace(tzinfo=timezone.utc)))
        await session.commit()
        per_quarter = await applicants_per_quarter_report(session, TODAY)
        per_year = await applicants_per_year_report(session, TODAY)

    assert _values(per_quarter) == {
        "2025 Q1": 1, "2025 Q2": 0, "2025 Q3": 0, "2025 Q4": 0,
        "2026 Q1": 0, "2026 Q2": 2, "2026 Q3": 0, "2026 Q4": 1,
    }
    assert _values(per_year) == {"2025": 1, "2026": 3}


def _hours(sponsorship=0.0):
    return {"sponsorship_hours": sponsorship}


@pytest.mark.parametrize("row, expected", [
    ({"exempt": True, "outstanding_hours": 0, "tenant_details": [{"hours": _hours()}]}, "exempt"),
    ({"exempt": False, "outstanding_hours": 2.5, "tenant_details": [{"hours": _hours(1)}]}, "owes_fee"),
    ({"exempt": False, "outstanding_hours": 0, "tenant_details": [{"hours": _hours()}, {"hours": _hours(3)}]}, "sponsorship"),
    ({"exempt": False, "outstanding_hours": 0, "tenant_details": [{"hours": _hours()}]}, "sessions"),
    # PER_MEMBER rows carry the member's own hours instead of tenant_details.
    ({"exempt": False, "outstanding_hours": 0, "hours": _hours(2)}, "sponsorship"),
    ({"exempt": False, "outstanding_hours": 1, "hours": _hours()}, "owes_fee"),
])
def test_work_hours_category_is_exactly_one_per_row(row, expected):
    assert work_hours_category(row) == expected


async def test_hours_transfers_per_year(client):
    async with AsyncSessionLocal() as session:
        giver, receiver = Member(first_name="G", last_name="Iver"), Member(first_name="R", last_name="Eceiver")
        session.add_all([giver, receiver])
        await session.flush()
        session.add_all([
            HoursTransfer(giver_member_id=giver.id, receiver_member_id=receiver.id, year=2025, hours=2),
            HoursTransfer(giver_member_id=giver.id, receiver_member_id=receiver.id, year=2026, hours=1.5),
            HoursTransfer(giver_member_id=giver.id, receiver_member_id=receiver.id, year=2026, hours=3),
        ])
        await session.commit()
        report = await hours_transfers_report(session, TODAY)

    assert _values(report, 0) == {"2025": 1, "2026": 2}
    assert _values(report, 1) == {"2025": 2.0, "2026": 4.5}


async def test_electricity_counts_active_plots_with_a_parcel_connection(client):
    async with AsyncSessionLocal() as session:
        powered = Parcel(plot_number="E1", status=ParcelStatus.ACTIVE)
        water_only = Parcel(plot_number="E2", status=ParcelStatus.ACTIVE)
        terminated = Parcel(plot_number="E3", status=ParcelStatus.TERMINATED)
        session.add_all([powered, water_only, terminated])
        await session.flush()
        for parcel, medium in ((powered, MeteringMedium.ELECTRICITY), (powered, MeteringMedium.ELECTRICITY),
                               (water_only, MeteringMedium.WATER), (terminated, MeteringMedium.ELECTRICITY)):
            session.add(MeteringPoint(medium=medium, type=MeteringPointType.PARCEL, parcel_id=parcel.id))
        await session.commit()
        report = await electricity_report(session, TODAY)

    assert _values(report) == {"with": 1, "without": 1}


async def test_reporting_page_and_api(client, admin_user):
    async with AsyncSessionLocal() as session:
        session.add(Member(first_name="A", last_name="Boomer", date_of_birth=date(1950, 1, 1)))
        await session.commit()

    await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})
    response = await client.get("/reporting/")
    assert response.status_code == 200
    assert "Members by generation" in response.text
    assert "Baby boomers (1946–1964)" in response.text
    assert 'id="chart-generations"' in response.text
    assert 'href="/reporting/"' in response.text  # nav entry

    token = await login(client, "admin@example.com")
    response = await client.get("/api/v1/reporting", headers=auth_header(token))
    assert response.status_code == 200
    reports = {r["key"]: r for r in response.json()["reports"]}
    generations = reports["generations"]
    assert dict(zip(generations["labels"], generations["series"][0]["values"]))["boomers"] == 1


async def test_reporting_is_off_with_its_module_and_needs_permission(client, admin_user):
    from app.auth import hash_password
    from app.models import User, UserRole

    token = await login(client, "admin@example.com")
    response = await client.put(
        "/api/v1/club-settings/modul_reporting", json={"value": "false"}, headers=auth_header(token),
    )
    assert response.status_code == 200
    await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})
    assert (await client.get("/reporting/")).status_code == 404
    assert (await client.get("/api/v1/reporting", headers=auth_header(token))).status_code == 404

    await client.put("/api/v1/club-settings/modul_reporting", json={"value": "true"}, headers=auth_header(token))
    async with AsyncSessionLocal() as session:
        session.add(User(
            email="readonly@example.com", name="Test-Readonly",
            password_hash=hash_password("testpasswort123"), role=UserRole.READONLY,
        ))
        await session.commit()
    await client.post("/auth/login", data={"email": "readonly@example.com", "password": "testpasswort123"})
    assert (await client.get("/reporting/")).status_code == 403
