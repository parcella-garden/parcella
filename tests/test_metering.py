"""
Tests for metering (water & electricity). Focus: the monotonicity
check (a reading may not decrease) and consumption calculation.
"""
import base64
from datetime import date

from app.database import AsyncSessionLocal
from app.models import Meter, MeterReading, MeteringMedium, MeteringPoint, MeteringPointType
from tests.conftest import login, auth_header


def _b64_csv(text: str) -> str:
    return base64.b64encode(text.encode("utf-8")).decode("ascii")


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


async def test_metering_points_csv_export_import_round_trip(client, admin_user):
    """Issue #225: exporting the metering-points CSV and importing a
    new row for a not-yet-covered parcel creates a matching
    MeteringPoint+Meter; re-importing the same export is a no-op
    (existing type+parcel-number/label pairs are skipped, matching
    parcels_import_csv's own "skip existing" convention)."""
    token = await login(client, "admin@example.com")
    headers = auth_header(token)

    csv01_id = (await client.post("/api/v1/parcels", json={"plot_number": "CSV-01"}, headers=headers)).json()["id"]
    await client.post("/api/v1/parcels", json={"plot_number": "CSV-02"}, headers=headers)

    login_response = await client.post(
        "/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"},
    )
    assert login_response.status_code in (302, 303)

    create = await client.post(
        "/water/metering-points/new",
        data={
            "type": "PARCEL", "parcel_id": csv01_id, "number": "W-CSV-01",
            "installed_at": "2024-03-01", "calibrated_until": "2030", "initial_reading": "10,0",
        },
        follow_redirects=False,
    )
    assert create.status_code in (302, 303)

    export = await client.get("/water/metering-points/export/csv")
    assert export.status_code == 200
    assert "Type;Parcel number;Label;Meter number;Installed on;Calibrated until;Initial reading" in export.text
    assert "CSV-01" in export.text
    assert "W-CSV-01" in export.text

    # Add a hand-written row for the not-yet-covered second parcel,
    # simulating a self-hoster importing water points for parcels
    # that already have electricity points entered by hand.
    extra_row = "PARCEL;CSV-02;;W-CSV-02;2025-05-15;2031;5,0\n"
    csv_text = export.text + extra_row
    import_response = await client.post(
        "/water/metering-points/import/finalize",
        data={
            "csv_content_b64": _b64_csv(csv_text), "delimiter": ";",
            "map_0": "type", "map_1": "parcel_number", "map_2": "label", "map_3": "meter_number",
            "map_4": "installed_on", "map_5": "calibrated_until", "map_6": "initial_reading",
        },
        follow_redirects=False,
    )
    assert import_response.status_code in (302, 303)
    assert "imported" in import_response.headers["location"]

    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    from app.database import AsyncSessionLocal

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(MeteringPoint)
            .options(selectinload(MeteringPoint.parcel), selectinload(MeteringPoint.meters))
            .where(MeteringPoint.medium == MeteringMedium.WATER)
        )
        points = result.scalars().all()
        # Exactly one PARCEL-type point per parcel -- the re-imported
        # CSV-01 row was skipped as already existing, CSV-02 was created.
        by_plot = {p.parcel.plot_number: p for p in points if p.parcel}
        assert set(by_plot) == {"CSV-01", "CSV-02"}
        new_meter = by_plot["CSV-02"].meters[0]
        assert new_meter.number == "W-CSV-02"
        assert new_meter.calibrated_until == 2031
        assert float(new_meter.initial_reading) == 5.0


async def test_readings_csv_export_import_applies_monotonicity_check(client, admin_user):
    """Issue #225: readings CSV import reuses record_reading(), so a
    bulk-imported reading is rejected by the same monotonicity check a
    manually entered one would be -- it's skipped, not a hard failure
    for the whole file."""
    token = await login(client, "admin@example.com")
    headers = auth_header(token)

    metering_point = (await client.post(
        "/api/v1/water/metering-points",
        json={"type": "CLUB", "label": "Vereinsheim CSV", "number": "W-READ-01", "initial_reading": "0.0"},
        headers=headers,
    )).json()

    await client.post(
        f"/api/v1/water/metering-points/{metering_point['id']}/readings",
        json={"year": 2024, "date": "2024-10-01", "reading": "50.0"},
        headers=headers,
    )

    login_response = await client.post(
        "/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"},
    )
    assert login_response.status_code in (302, 303)

    export = await client.get("/water/readings/export/csv", params={"year": 2024})
    assert export.status_code == 200
    assert "50,0" in export.text

    csv_body = (
        "Type;Parcel number;Label;Meter number;Year;Date;Reading;Note\n"
        # Valid: a higher reading for a later year -- must be recorded.
        "CLUB;;Vereinsheim CSV;W-READ-01;2025;2025-10-01;80,0;imported\n"
        # Implausible: lower than the 2024 reading -- must be skipped, not crash the import.
        "CLUB;;Vereinsheim CSV;W-READ-01;2026;2026-10-01;10,0;imported\n"
    )
    import_response = await client.post(
        "/water/readings/import/finalize",
        data={
            "csv_content_b64": _b64_csv(csv_body), "delimiter": ";",
            "map_0": "type", "map_1": "parcel_number", "map_2": "label", "map_3": "ignore",
            "map_4": "year", "map_5": "date", "map_6": "reading", "map_7": "note",
        },
        follow_redirects=False,
    )
    assert import_response.status_code in (302, 303)
    assert "skipped" in import_response.headers["location"]

    from sqlalchemy import select

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Meter).where(Meter.number == "W-READ-01"))
        meter = result.scalar_one()
        result = await db.execute(select(MeterReading).where(MeterReading.meter_id == meter.id))
        readings = {r.year: float(r.reading) for r in result.scalars().all()}
        assert readings == {2024: 50.0, 2025: 80.0}


async def test_readings_import_join_is_parcel_number_not_meter_number(client, admin_user):
    """Two parcels sharing the same placeholder meter number ("ohne",
    ADR 0081/0082's real recurring value for "no distinct meter") must
    not be confused with each other on readings import -- the lookup
    key is (type, parcel number), never meter number, precisely
    because meter number isn't a real identifier in this app (ADR
    0082). Regression test for that join staying parcel-number-based
    rather than accidentally drifting to meter-number matching."""
    token = await login(client, "admin@example.com")
    headers = auth_header(token)

    parcel_a_id = (await client.post(
        "/api/v1/parcels", json={"plot_number": "OHNE-A"}, headers=headers
    )).json()["id"]
    parcel_b_id = (await client.post(
        "/api/v1/parcels", json={"plot_number": "OHNE-B"}, headers=headers
    )).json()["id"]

    await client.post(
        "/api/v1/water/metering-points",
        json={"type": "PARCEL", "parcel_id": parcel_a_id, "number": "ohne", "initial_reading": "0.0"},
        headers=headers,
    )
    await client.post(
        "/api/v1/water/metering-points",
        json={"type": "PARCEL", "parcel_id": parcel_b_id, "number": "ohne", "initial_reading": "0.0"},
        headers=headers,
    )

    login_response = await client.post(
        "/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"},
    )
    assert login_response.status_code in (302, 303)

    csv_body = (
        "Type;Parcel number;Label;Meter number;Year;Date;Reading;Note\n"
        "PARCEL;OHNE-A;;ohne;2025;2025-10-01;11,0;\n"
        "PARCEL;OHNE-B;;ohne;2025;2025-10-01;22,0;\n"
    )
    import_response = await client.post(
        "/water/readings/import/finalize",
        data={
            "csv_content_b64": _b64_csv(csv_body), "delimiter": ";",
            "map_0": "type", "map_1": "parcel_number", "map_2": "label", "map_3": "ignore",
            "map_4": "year", "map_5": "date", "map_6": "reading", "map_7": "note",
        },
        follow_redirects=False,
    )
    assert import_response.status_code in (302, 303)

    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(MeteringPoint)
            .options(selectinload(MeteringPoint.parcel), selectinload(MeteringPoint.meters).selectinload(Meter.readings))
            .where(MeteringPoint.medium == MeteringMedium.WATER, MeteringPoint.parcel_id.in_([parcel_a_id, parcel_b_id]))
        )
        points_by_plot = {p.parcel.plot_number: p for p in result.scalars().all()}

        reading_a = points_by_plot["OHNE-A"].meters[0].readings[0]
        reading_b = points_by_plot["OHNE-B"].meters[0].readings[0]
        assert float(reading_a.reading) == 11.0
        assert float(reading_b.reading) == 22.0


async def test_metering_points_import_wizard_maps_reordered_german_headers(client, admin_user):
    """Issue #227: the column-mapping wizard (ADR 0062's pattern,
    generalized in docs/ADR/0083) lets a CSV whose headers don't match
    Parcella's own export -- different names, different order, German
    instead of English -- still be imported, by guessing a mapping the
    user confirms rather than requiring an exact fixed header row."""
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await client.post("/api/v1/parcels", json={"plot_number": "WIZ-01"}, headers=headers)

    login_response = await client.post(
        "/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"},
    )
    assert login_response.status_code in (302, 303)

    # Reordered, German-headed CSV -- a different shape from the app's own export.
    csv_text = (
        "Parzellennummer;Typ;Zählernummer;Anfangszählerstand\n"
        "WIZ-01;PARCEL;W-WIZ-01;3,5\n"
    )
    preview = await client.post(
        "/water/metering-points/import/preview",
        files={"file": ("import.csv", csv_text.encode("utf-8"), "text/csv")},
    )
    assert preview.status_code == 200
    # The alias guesser correctly maps each German header despite the
    # reordering -- confirmed by which <option> the template pre-selects.
    assert 'value="parcel_number" selected' in preview.text
    assert 'value="type" selected' in preview.text
    assert 'value="meter_number" selected' in preview.text
    assert 'value="initial_reading" selected' in preview.text

    import_response = await client.post(
        "/water/metering-points/import/finalize",
        data={
            "csv_content_b64": _b64_csv(csv_text), "delimiter": ";",
            "map_0": "parcel_number", "map_1": "type", "map_2": "meter_number", "map_3": "initial_reading",
        },
        follow_redirects=False,
    )
    assert import_response.status_code in (302, 303)
    assert "imported" in import_response.headers["location"]

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(MeteringPoint)
            .options(selectinload(MeteringPoint.parcel), selectinload(MeteringPoint.meters))
            .where(MeteringPoint.medium == MeteringMedium.WATER)
        )
        by_plot = {p.parcel.plot_number: p for p in result.scalars().all() if p.parcel}
        assert "WIZ-01" in by_plot
        meter = by_plot["WIZ-01"].meters[0]
        assert meter.number == "W-WIZ-01"
        assert float(meter.initial_reading) == 3.5


async def test_readings_import_wizard_maps_reordered_german_headers(client, admin_user):
    """Same wizard, for the readings importer."""
    from sqlalchemy import select

    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await client.post(
        "/api/v1/water/metering-points",
        json={"type": "CLUB", "label": "Vereinsheim WIZ", "number": "W-WIZ-READ", "initial_reading": "0.0"},
        headers=headers,
    )

    login_response = await client.post(
        "/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"},
    )
    assert login_response.status_code in (302, 303)

    csv_text = (
        "Bezeichnung;Typ;Jahr;Datum;Zählerstand\n"
        "Vereinsheim WIZ;CLUB;2025;2025-11-01;42,0\n"
    )
    preview = await client.post(
        "/water/readings/import/preview",
        files={"file": ("import.csv", csv_text.encode("utf-8"), "text/csv")},
    )
    assert preview.status_code == 200
    assert 'value="label" selected' in preview.text
    assert 'value="type" selected' in preview.text
    assert 'value="year" selected' in preview.text
    assert 'value="date" selected' in preview.text
    assert 'value="reading" selected' in preview.text

    import_response = await client.post(
        "/water/readings/import/finalize",
        data={
            "csv_content_b64": _b64_csv(csv_text), "delimiter": ";",
            "map_0": "label", "map_1": "type", "map_2": "year", "map_3": "date", "map_4": "reading",
        },
        follow_redirects=False,
    )
    assert import_response.status_code in (302, 303)
    assert "recorded" in import_response.headers["location"]

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Meter).where(Meter.number == "W-WIZ-READ"))
        meter = result.scalar_one()
        result = await db.execute(select(MeterReading).where(MeterReading.meter_id == meter.id))
        readings = {r.year: float(r.reading) for r in result.scalars().all()}
        assert readings == {2025: 42.0}


async def test_metering_points_import_wizard_defaults_to_parcel_when_type_not_mapped(client, admin_user):
    """Issue #227 follow-up: a real self-hosted export for a single
    medium is often all-PARCEL rows with no Type column at all (just
    parcel number, meter number, calibrated until, initial reading).
    Requiring Type to be mapped before import silently blocked this
    shape of file -- it should default every row to PARCEL instead."""
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await client.post("/api/v1/parcels", json={"plot_number": "NOTYPE-01"}, headers=headers)

    login_response = await client.post(
        "/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"},
    )
    assert login_response.status_code in (302, 303)

    csv_text = (
        "Parzellennummer,Zählernummer,Geeicht bis,Anfangsstand\n"
        "NOTYPE-01,8DEL2143010321,2028,31\n"
    )
    preview = await client.post(
        "/water/metering-points/import/preview",
        files={"file": ("import.csv", csv_text.encode("utf-8"), "text/csv")},
    )
    assert preview.status_code == 200
    # No "type" option is (or can be) selected -- there's no Type column.
    assert 'value="type" selected' not in preview.text

    import_response = await client.post(
        "/water/metering-points/import/finalize",
        data={
            "csv_content_b64": _b64_csv(csv_text), "delimiter": ",",
            "map_0": "parcel_number", "map_1": "meter_number",
            "map_2": "calibrated_until", "map_3": "initial_reading",
        },
        follow_redirects=False,
    )
    assert import_response.status_code in (302, 303)
    assert "error" not in import_response.headers["location"]
    assert "imported" in import_response.headers["location"]

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(MeteringPoint)
            .options(selectinload(MeteringPoint.parcel), selectinload(MeteringPoint.meters))
            .where(MeteringPoint.medium == MeteringMedium.WATER)
        )
        by_plot = {p.parcel.plot_number: p for p in result.scalars().all() if p.parcel}
        assert "NOTYPE-01" in by_plot
        assert by_plot["NOTYPE-01"].type == MeteringPointType.PARCEL
        assert by_plot["NOTYPE-01"].meters[0].number == "8DEL2143010321"


async def test_metering_points_import_wizard_empty_mapping_shows_error_banner(client, admin_user):
    """The error-redirect path (empty file, or nothing mapped at all)
    must actually be visible -- a prior bug set ?error=... on the
    redirect but the list template only ever rendered ?message=,
    so the error silently vanished."""
    login_response = await client.post(
        "/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"},
    )
    assert login_response.status_code in (302, 303)

    import_response = await client.post(
        "/water/metering-points/import/finalize",
        data={"csv_content_b64": _b64_csv("A,B\n1,2\n"), "delimiter": ","},
        follow_redirects=False,
    )
    assert import_response.status_code in (302, 303)
    assert "error=" in import_response.headers["location"]

    followed = await client.get(import_response.headers["location"])
    assert followed.status_code == 200
    assert "alert-danger" in followed.text


async def test_metering_points_import_wizard_lists_skip_reasons(client, admin_user):
    """Requested after a real import: a bare count ("3 skipped") isn't
    enough to act on -- the message should name which rows were skipped
    and why."""
    import urllib.parse

    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await client.post("/api/v1/parcels", json={"plot_number": "SKIP-01"}, headers=headers)

    login_response = await client.post(
        "/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"},
    )
    assert login_response.status_code in (302, 303)

    # First import creates SKIP-01's water point.
    csv_text = "Parcel number,Type,Meter number\nSKIP-01,PARCEL,W-SKIP-01\n"
    first = await client.post(
        "/water/metering-points/import/finalize",
        data={
            "csv_content_b64": _b64_csv(csv_text), "delimiter": ",",
            "map_0": "parcel_number", "map_1": "type", "map_2": "meter_number",
        },
        follow_redirects=False,
    )
    assert first.status_code in (302, 303)

    # Re-import the same row (already exists) plus one for a parcel that
    # doesn't exist (parcel not found) plus one with an invalid type.
    csv_text = (
        "Parcel number,Type,Meter number\n"
        "SKIP-01,PARCEL,W-SKIP-01\n"
        "SKIP-GHOST,PARCEL,W-GHOST\n"
        "SKIP-01,BOGUS,W-SKIP-01\n"
    )
    second = await client.post(
        "/water/metering-points/import/finalize",
        data={
            "csv_content_b64": _b64_csv(csv_text), "delimiter": ",",
            "map_0": "parcel_number", "map_1": "type", "map_2": "meter_number",
        },
        follow_redirects=False,
    )
    assert second.status_code in (302, 303)
    location = urllib.parse.unquote(second.headers["location"])
    assert "SKIP-01: already exists" in location
    assert "SKIP-GHOST: parcel not found" in location
    assert "SKIP-01: invalid type" in location


async def test_readings_import_wizard_requires_year_mapped_even_with_date_mapped(client, admin_user):
    """Regression guard: Year must NOT be silently derived from Date's
    calendar year -- an annual reading taken in January can still
    belong to the previous year's billing cycle (e.g. read on
    2026-01-19 but attributed to 2025), so a Date-only mapping must
    leave every row invalid rather than guess."""
    from sqlalchemy import select

    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    parcel_id = (await client.post(
        "/api/v1/parcels", json={"plot_number": "NOYEAR-01"}, headers=headers
    )).json()["id"]
    await client.post(
        "/api/v1/water/metering-points",
        json={"type": "PARCEL", "parcel_id": parcel_id, "number": "W-NOYEAR", "initial_reading": "0.0"},
        headers=headers,
    )

    login_response = await client.post(
        "/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"},
    )
    assert login_response.status_code in (302, 303)

    csv_text = "Parzellennummer;Ablesedatum;Zählerstand\nNOYEAR-01;19.01.2026;42,0\n"
    import_response = await client.post(
        "/water/readings/import/finalize",
        data={
            "csv_content_b64": _b64_csv(csv_text), "delimiter": ";",
            "map_0": "parcel_number", "map_1": "date", "map_2": "reading",
        },
        follow_redirects=False,
    )
    assert import_response.status_code in (302, 303)
    assert "skipped" in import_response.headers["location"]

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Meter).where(Meter.number == "W-NOYEAR"))
        meter = result.scalar_one()
        result = await db.execute(select(MeterReading).where(MeterReading.meter_id == meter.id))
        assert result.scalars().all() == []


async def test_readings_import_wizard_default_year_applies_when_year_not_mapped(client, admin_user):
    """An explicit, human-stated 'this whole batch is year X' default
    is safe (unlike guessing from the reading date) since the importer
    states it deliberately for the run, not the app inferring it."""
    from sqlalchemy import select

    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    parcel_id = (await client.post(
        "/api/v1/parcels", json={"plot_number": "DEFYEAR-01"}, headers=headers
    )).json()["id"]
    await client.post(
        "/api/v1/water/metering-points",
        json={"type": "PARCEL", "parcel_id": parcel_id, "number": "W-DEFYEAR", "initial_reading": "0.0"},
        headers=headers,
    )

    login_response = await client.post(
        "/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"},
    )
    assert login_response.status_code in (302, 303)

    csv_text = "Parzellennummer;Ablesedatum;Zählerstand\nDEFYEAR-01;19.01.2026;42,0\n"
    import_response = await client.post(
        "/water/readings/import/finalize",
        data={
            "csv_content_b64": _b64_csv(csv_text), "delimiter": ";", "default_year": "2025",
            "map_0": "parcel_number", "map_1": "date", "map_2": "reading",
        },
        follow_redirects=False,
    )
    assert import_response.status_code in (302, 303)

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Meter).where(Meter.number == "W-DEFYEAR"))
        meter = result.scalar_one()
        result = await db.execute(select(MeterReading).where(MeterReading.meter_id == meter.id))
        readings = {r.year: float(r.reading) for r in result.scalars().all()}
        assert readings == {2025: 42.0}


async def test_readings_import_wizard_mapped_year_column_overrides_default_year(client, admin_user):
    """A row's own Year column, when mapped and filled in, always wins
    over the form's default_year fallback."""
    from sqlalchemy import select

    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    parcel_id = (await client.post(
        "/api/v1/parcels", json={"plot_number": "DEFYEAR-02"}, headers=headers
    )).json()["id"]
    await client.post(
        "/api/v1/water/metering-points",
        json={"type": "PARCEL", "parcel_id": parcel_id, "number": "W-DEFYEAR2", "initial_reading": "0.0"},
        headers=headers,
    )

    login_response = await client.post(
        "/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"},
    )
    assert login_response.status_code in (302, 303)

    csv_text = "Parzellennummer;Jahr;Ablesedatum;Zählerstand\nDEFYEAR-02;2024;19.01.2026;42,0\n"
    import_response = await client.post(
        "/water/readings/import/finalize",
        data={
            "csv_content_b64": _b64_csv(csv_text), "delimiter": ";", "default_year": "2025",
            "map_0": "parcel_number", "map_1": "year", "map_2": "date", "map_3": "reading",
        },
        follow_redirects=False,
    )
    assert import_response.status_code in (302, 303)

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Meter).where(Meter.number == "W-DEFYEAR2"))
        meter = result.scalar_one()
        result = await db.execute(select(MeterReading).where(MeterReading.meter_id == meter.id))
        readings = {r.year: float(r.reading) for r in result.scalars().all()}
        assert readings == {2024: 42.0}


async def test_readings_import_wizard_does_not_guess_art_column_as_type(client, admin_user):
    """Regression guard: a real export's 'Art' column (reading kind --
    Jahresablesung/Zwischenablesung) must NOT be guessed as the Type
    field. It collided with "art" as a German alias for "type" and
    would have made the wizard pre-select every such file's reading-kind
    column as Type, silently invalidating every row on import."""
    login_response = await client.post(
        "/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"},
    )
    assert login_response.status_code in (302, 303)

    csv_text = "Parzellennummer;Art;Jahr;Ablesedatum;Zählerstand\n5;Jahresablesung;2025;03.11.2025;42,0\n"
    preview = await client.post(
        "/water/readings/import/preview",
        files={"file": ("import.csv", csv_text.encode("utf-8"), "text/csv")},
    )
    assert preview.status_code == 200
    assert 'value="type" selected' not in preview.text


async def test_readings_import_wizard_matching_meter_number_is_recorded(client, admin_user):
    """When the CSV carries a meter number and it matches the point's
    current meter, the reading is recorded as usual."""
    from sqlalchemy import select

    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    parcel_id = (await client.post(
        "/api/v1/parcels", json={"plot_number": "MMATCH-01"}, headers=headers
    )).json()["id"]
    await client.post(
        "/api/v1/water/metering-points",
        json={"type": "PARCEL", "parcel_id": parcel_id, "number": "W-MMATCH", "initial_reading": "0.0"},
        headers=headers,
    )

    login_response = await client.post(
        "/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"},
    )
    assert login_response.status_code in (302, 303)

    csv_text = "Parzellennummer;Zählernummer;Jahr;Ablesedatum;Zählerstand\nMMATCH-01;W-MMATCH;2025;03.11.2025;42,0\n"
    import_response = await client.post(
        "/water/readings/import/finalize",
        data={
            "csv_content_b64": _b64_csv(csv_text), "delimiter": ";",
            "map_0": "parcel_number", "map_1": "meter_number", "map_2": "year",
            "map_3": "date", "map_4": "reading",
        },
        follow_redirects=False,
    )
    assert import_response.status_code in (302, 303)

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Meter).where(Meter.number == "W-MMATCH"))
        meter = result.scalar_one()
        result = await db.execute(select(MeterReading).where(MeterReading.meter_id == meter.id))
        readings = {r.year: float(r.reading) for r in result.scalars().all()}
        assert readings == {2025: 42.0}


async def test_readings_import_wizard_meter_number_mismatch_is_skipped(client, admin_user):
    """Issue #227 follow-up: if the CSV's meter number doesn't match the
    metering point's *current* meter, the reading may belong to a
    since-replaced meter (exchange_meter() deactivates the old one
    rather than deleting it) -- it must be skipped, not silently
    attached to the wrong physical meter's history."""
    from sqlalchemy import select

    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    parcel_id = (await client.post(
        "/api/v1/parcels", json={"plot_number": "MMISMATCH-01"}, headers=headers
    )).json()["id"]
    point = (await client.post(
        "/api/v1/water/metering-points",
        json={"type": "PARCEL", "parcel_id": parcel_id, "number": "W-OLD", "initial_reading": "0.0"},
        headers=headers,
    )).json()

    login_response = await client.post(
        "/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"},
    )
    assert login_response.status_code in (302, 303)

    # Simulate a meter swap: the parcel's current meter is now W-NEW.
    exchange_response = await client.post(
        f"/water/metering-points/{point['id']}/meter/exchange",
        data={
            "new_number": "W-NEW", "removed_at": "2025-06-01",
            "installed_at": "2025-06-01", "calibrated_until": "", "initial_reading": "0",
        },
        follow_redirects=False,
    )
    assert exchange_response.status_code in (302, 303)

    # A CSV row for the OLD (now-replaced) meter number must not be
    # attached to the new meter's reading history.
    csv_text = "Parzellennummer;Zählernummer;Jahr;Ablesedatum;Zählerstand\nMMISMATCH-01;W-OLD;2025;01.03.2025;42,0\n"
    import_response = await client.post(
        "/water/readings/import/finalize",
        data={
            "csv_content_b64": _b64_csv(csv_text), "delimiter": ";",
            "map_0": "parcel_number", "map_1": "meter_number", "map_2": "year",
            "map_3": "date", "map_4": "reading",
        },
        follow_redirects=False,
    )
    assert import_response.status_code in (302, 303)
    assert "skipped" in import_response.headers["location"]

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Meter).where(Meter.number == "W-NEW"))
        new_meter = result.scalar_one()
        result = await db.execute(select(MeterReading).where(MeterReading.meter_id == new_meter.id))
        assert result.scalars().all() == []


async def test_edit_current_meter_via_api_corrects_data_entry_mistake(client, admin_user):
    """update_meter() is an in-place correction, distinct from
    exchange_meter() -- no new Meter row, no removed_at on the old one,
    just the mistyped fields fixed on the still-current meter."""
    token = await login(client, "admin@example.com")
    headers = auth_header(token)

    metering_point = (await client.post(
        "/api/v1/water/metering-points",
        json={"type": "CLUB", "label": "Edit-Test", "number": "W-TYPO", "initial_reading": "100.0"},
        headers=headers,
    )).json()
    meter_id = metering_point["current_meter"]["id"]

    update = await client.put(
        f"/api/v1/water/metering-points/{metering_point['id']}/meter",
        json={"number": "W-CORRECT", "initial_reading": "10.0"},
        headers=headers,
    )
    assert update.status_code == 200
    body = update.json()
    assert body["id"] == meter_id  # same row, not a new one
    assert body["number"] == "W-CORRECT"
    assert float(body["initial_reading"]) == 10.0

    detail = (await client.get(f"/api/v1/water/metering-points/{metering_point['id']}", headers=headers)).json()
    assert detail["current_meter"]["number"] == "W-CORRECT"
    assert detail["former_meters"] == []  # not treated as an exchange


async def test_edit_current_meter_via_html_form(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)

    metering_point = (await client.post(
        "/api/v1/electricity/metering-points",
        json={"type": "CLUB", "label": "Edit-Test-HTML", "number": "E-TYPO", "calibrated_until": 2030, "initial_reading": "5.0"},
        headers=headers,
    )).json()

    login_response = await client.post(
        "/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"},
    )
    assert login_response.status_code in (302, 303)

    edit = await client.post(
        f"/electricity/metering-points/{metering_point['id']}/meter/edit",
        data={"number": "E-CORRECT", "calibrated_until": "2031", "initial_reading": "7"},
        follow_redirects=False,
    )
    assert edit.status_code in (302, 303)

    detail_page = await client.get(f"/electricity/metering-points/{metering_point['id']}")
    assert "E-CORRECT" in detail_page.text
    assert "E-TYPO" not in detail_page.text

    async with AsyncSessionLocal() as db:
        from sqlalchemy import select
        result = await db.execute(select(Meter).where(Meter.number == "E-CORRECT"))
        meter = result.scalar_one()
        assert meter.calibrated_until == 2031
        assert float(meter.initial_reading) == 7.0
        assert meter.is_active is True
