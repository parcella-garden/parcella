"""
Tests for metering (water & electricity). Focus: the monotonicity
check (a reading may not decrease) and consumption calculation.
"""
from datetime import date

from app.database import AsyncSessionLocal
from app.models import Meter, MeterReading, MeteringMedium, MeteringPoint, MeteringPointType
from tests.conftest import login, auth_header


async def test_metering_point_create_and_reading(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)

    parcel = (await client.post(
        "/api/v1/parcels", json={"plot_number": "G200"}, headers=headers
    )).json()

    metering_point = (await client.post(
        "/api/v1/water/metering-points",
        json={
            "type": "PARCEL", "parcel_id": parcel["id"],
            "number": "W-12345", "initial_reading": "0.0",
        },
        headers=headers,
    )).json()
    assert metering_point["current_meter"]["number"] == "W-12345"

    entry = await client.post(
        f"/api/v1/water/metering-points/{metering_point['id']}/readings",
        json={"year": 2026, "date": "2026-10-01", "reading": "12.5"},
        headers=headers,
    )
    assert entry.status_code == 201


async def test_reading_may_not_decrease(client, admin_user):
    """
    Core rule of the plausibility check: a new reading must be at
    least as high as the previous one of the same water meter.
    """
    token = await login(client, "admin@example.com")
    headers = auth_header(token)

    metering_point = (await client.post(
        "/api/v1/water/metering-points",
        json={"type": "CLUB", "label": "Vereinsheim", "number": "W-99999", "initial_reading": "0.0"},
        headers=headers,
    )).json()

    r1 = await client.post(
        f"/api/v1/water/metering-points/{metering_point['id']}/readings",
        json={"year": 2025, "date": "2025-10-01", "reading": "50.0"},
        headers=headers,
    )
    assert r1.status_code == 201

    # A lower reading in the following year must be rejected
    r2 = await client.post(
        f"/api/v1/water/metering-points/{metering_point['id']}/readings",
        json={"year": 2026, "date": "2026-10-01", "reading": "30.0"},
        headers=headers,
    )
    assert r2.status_code == 422

    # A higher reading is perfectly fine
    r3 = await client.post(
        f"/api/v1/water/metering-points/{metering_point['id']}/readings",
        json={"year": 2026, "date": "2026-10-01", "reading": "75.0"},
        headers=headers,
    )
    assert r3.status_code == 201


async def test_consumption_calculation(client, admin_user):
    """Consumption = current reading minus last reading (or initial reading)."""
    token = await login(client, "admin@example.com")
    headers = auth_header(token)

    metering_point = (await client.post(
        "/api/v1/water/metering-points",
        json={"type": "MAIN_METER", "label": "Hauptzähler", "number": "W-1", "initial_reading": "100.0"},
        headers=headers,
    )).json()

    await client.post(
        f"/api/v1/water/metering-points/{metering_point['id']}/readings",
        json={"year": 2026, "date": "2026-10-01", "reading": "150.0"},
        headers=headers,
    )

    evaluation = (await client.get("/api/v1/water/evaluation/2026", headers=headers)).json()
    zeile = next(z for z in evaluation if z["metering_point_id"] == metering_point["id"])
    assert float(zeile["consumption"]) == 50.0  # 150 - initial reading 100


async def test_electricity_and_water_separate(client, admin_user):
    """Water and electricity MeteringPoints must be independent, separate lists."""
    token = await login(client, "admin@example.com")
    headers = auth_header(token)

    await client.post(
        "/api/v1/water/metering-points",
        json={"type": "CLUB", "label": "Nur Wasser", "number": "W-A", "initial_reading": "0"},
        headers=headers,
    )
    await client.post(
        "/api/v1/electricity/metering-points",
        json={"type": "CLUB", "label": "Nur Strom", "number": "S-A", "initial_reading": "0"},
        headers=headers,
    )

    wasser_liste = (await client.get("/api/v1/water/metering-points", headers=headers)).json()
    strom_liste = (await client.get("/api/v1/electricity/metering-points", headers=headers)).json()

    assert len(wasser_liste) == 1
    assert len(strom_liste) == 1
    assert wasser_liste[0]["label"] == "Nur Wasser"
    assert strom_liste[0]["label"] == "Nur Strom"


# ---------------------------------------------------------------------------
# ADR 0070: shared service layer + unified (Group-based, not role-only)
# authorization for the API.
# ---------------------------------------------------------------------------

async def test_monotonicity_error_uses_shared_i18n_text_not_hardcoded_german(client, admin_user):
    """ADR 0070: the API used to resolve check_monotonicity()'s
    (key, params) via format_monotonicity_error_de() -- always German,
    regardless of the club's configured language -- instead of the
    shared i18n catalog the HTML side uses via t_for(). Both now share
    one code path (app.services.metering.record_reading)."""
    token = await login(client, "admin@example.com")
    headers = auth_header(token)

    metering_point = (await client.post(
        "/api/v1/water/metering-points",
        json={"type": "CLUB", "label": "i18n test", "number": "W-I18N", "initial_reading": "0.0"},
        headers=headers,
    )).json()
    await client.post(
        f"/api/v1/water/metering-points/{metering_point['id']}/readings",
        json={"year": 2025, "date": "2025-10-01", "reading": "50.0"},
        headers=headers,
    )

    response = await client.post(
        f"/api/v1/water/metering-points/{metering_point['id']}/readings",
        json={"year": 2026, "date": "2026-10-01", "reading": "30.0"},
        headers=headers,
    )
    assert response.status_code == 422
    detail = response.json()["detail"]
    # Static portions of the shared en.json text -- not asserting exact
    # Decimal formatting of {new_value}/{previous_value}, which depends
    # on DB numeric precision.
    assert "must not be smaller than the previous reading" in detail
    assert "Zählerstand" not in detail  # not the old hard-coded-German text


async def test_metering_point_delete_button_present_and_deletes_cascade(client, admin_user):
    """Issue #211: the HTML POST delete route (and its API equivalent)
    already existed and cascade-deletes meters/readings -- the
    metering-points list page just never had a delete button wired up
    to it. Pure UI-wiring gap, not a missing capability."""
    login_response = await client.post(
        "/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"}
    )
    assert login_response.status_code in (302, 303)

    async with AsyncSessionLocal() as session:
        point = MeteringPoint(medium=MeteringMedium.WATER, type=MeteringPointType.CLUB, label="ToDelete")
        session.add(point)
        await session.flush()
        meter = Meter(metering_point_id=point.id, number="W-DEL-1", is_active=True, initial_reading=0)
        session.add(meter)
        await session.flush()
        reading = MeterReading(meter_id=meter.id, year=2026, date=date(2026, 1, 1), reading=10)
        session.add(reading)
        await session.commit()
        point_id, meter_id, reading_id = point.id, meter.id, reading.id

    list_response = await client.get("/water/metering-points")
    assert list_response.status_code == 200
    assert f'action="/water/metering-points/{point_id}/delete"' in list_response.text

    delete_response = await client.post(f"/water/metering-points/{point_id}/delete")
    assert delete_response.status_code == 302

    async with AsyncSessionLocal() as session:
        assert await session.get(MeteringPoint, point_id) is None
        assert await session.get(Meter, meter_id) is None
        assert await session.get(MeterReading, reading_id) is None


async def test_treasurer_without_group_grant_is_blocked_from_water_write_via_api(client):
    """ADR 0070: api_metering.py used require_write_access (role-only)
    -- ANY TREASURER could write metering data via the API regardless
    of Group configuration. Now the API checks the same Group-derived
    permission as HTML ("water"/"electricity" modules)."""
    from app.database import AsyncSessionLocal
    from app.models import User, UserRole
    from app.auth import hash_password

    async with AsyncSessionLocal() as db:
        user = User(
            email="treasurer-no-group-water@example.com", name="Treasurer No Group",
            password_hash=hash_password("testpasswort123"), role=UserRole.TREASURER,
        )
        db.add(user)
        await db.commit()

    token = await login(client, "treasurer-no-group-water@example.com")
    response = await client.post(
        "/api/v1/water/metering-points",
        json={"type": "CLUB", "label": "Blocked", "number": "W-BLOCK", "initial_reading": "0.0"},
        headers=auth_header(token),
    )
    assert response.status_code == 403


async def test_readonly_with_group_grant_can_write_water_via_api(client):
    """Flip side: a READONLY user granted water:write via a Group could
    already write metering data through the HTML UI, but the role-only
    API check blocked them regardless of Group membership."""
    from app.database import AsyncSessionLocal
    from app.models import User, UserRole, Group, GroupModulePermission, GroupMembership
    from app.auth import hash_password

    async with AsyncSessionLocal() as db:
        user = User(
            email="readonly-with-group-water@example.com", name="Readonly With Group",
            password_hash=hash_password("testpasswort123"), role=UserRole.READONLY,
        )
        db.add(user)
        await db.flush()

        group = Group(name="Water Handlers")
        db.add(group)
        await db.flush()
        db.add(GroupModulePermission(group_id=group.id, module="water", can_read=True, can_write=True))
        db.add(GroupMembership(user_id=user.id, group_id=group.id))
        await db.commit()

    token = await login(client, "readonly-with-group-water@example.com")
    response = await client.post(
        "/api/v1/water/metering-points",
        json={"type": "CLUB", "label": "Allowed", "number": "W-ALLOW", "initial_reading": "0.0"},
        headers=auth_header(token),
    )
    assert response.status_code == 201, response.text


# ---------------------------------------------------------------------------
# Meter number is a free-text label, not an enforced-unique identifier
# (ADR 0082) -- reproduces a real prod 500 (POST
# /electricity/metering-points/new -> IntegrityError on a since-removed
# uniqueness constraint) hit when a placeholder number like "ohne" ("none")
# was already used by another meter, same or different medium.
# ---------------------------------------------------------------------------

async def test_duplicate_meter_number_allowed_same_and_across_media(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)

    water = await client.post(
        "/api/v1/water/metering-points",
        json={"type": "CLUB", "label": "No distinct meter (water)", "number": "ohne", "initial_reading": "0"},
        headers=headers,
    )
    assert water.status_code == 201, water.text

    electricity_first = await client.post(
        "/api/v1/electricity/metering-points",
        json={"type": "CLUB", "label": "No distinct meter (electricity 1)", "number": "ohne", "initial_reading": "0"},
        headers=headers,
    )
    assert electricity_first.status_code == 201, electricity_first.text

    electricity_second = await client.post(
        "/api/v1/electricity/metering-points",
        json={"type": "CLUB", "label": "No distinct meter (electricity 2)", "number": "ohne", "initial_reading": "0"},
        headers=headers,
    )
    assert electricity_second.status_code == 201, electricity_second.text


# ---------------------------------------------------------------------------
# A TERMINATED parcel (lease cancelled) must still be offered when adding a
# new metering point (issue #219) -- e.g. to record a final handover
# reading before a new tenant moves in. The "new metering point" form's
# parcel dropdown used to filter to ParcelStatus.ACTIVE only, silently
# hiding every terminated parcel with no error. DELETED parcels must still
# stay excluded, so this also guards against overbroadening the fix.
# ---------------------------------------------------------------------------

async def test_terminated_parcel_still_offered_when_adding_metering_point(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)

    terminated = (await client.post(
        "/api/v1/parcels", json={"plot_number": "TERM-01"}, headers=headers
    )).json()
    r = await client.put(f"/api/v1/parcels/{terminated['id']}", json={"status": "TERMINATED"}, headers=headers)
    assert r.status_code == 200, r.text

    deleted = (await client.post(
        "/api/v1/parcels", json={"plot_number": "DEL-01"}, headers=headers
    )).json()
    r = await client.put(f"/api/v1/parcels/{deleted['id']}", json={"status": "DELETED"}, headers=headers)
    assert r.status_code == 200, r.text

    login_response = await client.post(
        "/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"},
    )
    assert login_response.status_code in (302, 303)

    page = await client.get("/electricity/metering-points/new")
    assert page.status_code == 200
    assert "TERM-01" in page.text
    assert "DEL-01" not in page.text


# ---------------------------------------------------------------------------
# Overview stat tile: count of parcels without a metering point (issue #223)
# ---------------------------------------------------------------------------

async def test_overview_counts_parcels_without_a_metering_point(client, admin_user):
    import re

    token = await login(client, "admin@example.com")
    headers = auth_header(token)

    covered = (await client.post(
        "/api/v1/parcels", json={"plot_number": "COVERED-01"}, headers=headers
    )).json()
    await client.post(
        "/api/v1/electricity/metering-points",
        json={"type": "PARCEL", "parcel_id": covered["id"], "number": "E-1", "initial_reading": "0"},
        headers=headers,
    )

    # Only a *water* point -- electricity is a separate medium (same rule
    # as test_electricity_and_water_separate), so it still counts as
    # missing on the electricity overview.
    water_only = (await client.post(
        "/api/v1/parcels", json={"plot_number": "WATER-ONLY-01"}, headers=headers
    )).json()
    await client.post(
        "/api/v1/water/metering-points",
        json={"type": "PARCEL", "parcel_id": water_only["id"], "number": "W-1", "initial_reading": "0"},
        headers=headers,
    )

    # TERMINATED but uncovered -- must still count (issue #219 convention).
    terminated_uncovered = (await client.post(
        "/api/v1/parcels", json={"plot_number": "TERM-MISSING-01"}, headers=headers
    )).json()
    r = await client.put(
        f"/api/v1/parcels/{terminated_uncovered['id']}", json={"status": "TERMINATED"}, headers=headers,
    )
    assert r.status_code == 200, r.text

    # DELETED parcels are excluded regardless of coverage.
    deleted_uncovered = (await client.post(
        "/api/v1/parcels", json={"plot_number": "DEL-MISSING-01"}, headers=headers
    )).json()
    r = await client.put(
        f"/api/v1/parcels/{deleted_uncovered['id']}", json={"status": "DELETED"}, headers=headers,
    )
    assert r.status_code == 200, r.text

    login_response = await client.post(
        "/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"},
    )
    assert login_response.status_code in (302, 303)

    page = await client.get("/electricity/")
    assert page.status_code == 200
    match = re.search(r"Missing metering points.*?>\s*(\d+)\s*<", page.text, re.DOTALL)
    assert match, "stat tile label/count not found in rendered page"
    assert match.group(1) == "2"  # water_only + terminated_uncovered

    # Overview tiles link to the filtered metering-points list (issue #224).
    assert "/electricity/metering-points?type=MAIN_METER" in page.text
    assert "/electricity/metering-points?type=PARCEL" in page.text
    assert "/electricity/metering-points?type=CLUB" in page.text
    assert "/electricity/metering-points?missing=1" in page.text


# ---------------------------------------------------------------------------
# Metering-points list: type/missing filters linked from the overview
# stat tiles (issue #224)
# ---------------------------------------------------------------------------

async def test_metering_points_list_type_filter(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)

    main_meter = (await client.post(
        "/api/v1/electricity/metering-points",
        json={"type": "MAIN_METER", "label": "Main", "number": "E-MAIN", "initial_reading": "0"},
        headers=headers,
    )).json()
    club = (await client.post(
        "/api/v1/electricity/metering-points",
        json={"type": "CLUB", "label": "Clubhouse", "number": "E-CLUB", "initial_reading": "0"},
        headers=headers,
    )).json()

    login_response = await client.post(
        "/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"},
    )
    assert login_response.status_code in (302, 303)

    page = await client.get("/electricity/metering-points", params={"type": "CLUB"})
    assert page.status_code == 200
    assert "Clubhouse" in page.text
    assert "Main" not in page.text
    # The active filter is shown with a way to clear it back to the unfiltered list.
    assert "/electricity/metering-points\"" in page.text


async def test_metering_points_list_missing_filter(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)

    covered = (await client.post(
        "/api/v1/parcels", json={"plot_number": "COVERED-02"}, headers=headers
    )).json()
    await client.post(
        "/api/v1/electricity/metering-points",
        json={"type": "PARCEL", "parcel_id": covered["id"], "number": "E-2", "initial_reading": "0"},
        headers=headers,
    )
    uncovered = (await client.post(
        "/api/v1/parcels", json={"plot_number": "MISSING-02"}, headers=headers
    )).json()

    login_response = await client.post(
        "/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"},
    )
    assert login_response.status_code in (302, 303)

    page = await client.get("/electricity/metering-points", params={"missing": "1"})
    assert page.status_code == 200
    assert "MISSING-02" in page.text
    assert "COVERED-02" not in page.text
    assert f"/electricity/metering-points/new?parcel_id={uncovered['id']}" in page.text


async def test_new_metering_point_page_preselects_parcel_from_query_param(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)

    parcel = (await client.post(
        "/api/v1/parcels", json={"plot_number": "PRESEL-01"}, headers=headers
    )).json()

    login_response = await client.post(
        "/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"},
    )
    assert login_response.status_code in (302, 303)

    page = await client.get(f"/electricity/metering-points/new?parcel_id={parcel['id']}")
    assert page.status_code == 200
    assert f'value="{parcel["id"]}" selected' in page.text
