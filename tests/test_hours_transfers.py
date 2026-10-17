"""
Issue #243: a member who did more work hours than required can give
some to another member (ADR 0094). Only the giver's surplus for the
year can be given; transfers count in calculate_hours_for_member(), so
the evaluation (both modes) and invoicing follow automatically.
"""
from app.database import AsyncSessionLocal
from app.services.work_hours import calculate_hours_for_member
from tests.conftest import auth_header, login
from tests.test_work_hours import _erstelle_configuration  # 5 h required, 25 EUR/h


async def _setup(client, mode):
    headers = auth_header(await login(client, "admin@example.com"))
    assert (await _erstelle_configuration(client, headers, year=2026, mode=mode)).status_code in (200, 201)
    return headers


async def _member(client, headers, last_name, plot=None):
    member = (await client.post(
        "/api/v1/members", json={"first_name": "Test", "last_name": last_name}, headers=headers
    )).json()
    if plot:
        parcel = (await client.post("/api/v1/parcels", json={"plot_number": plot}, headers=headers)).json()
        await client.post(
            f"/api/v1/parcels/{parcel['id']}/assignments",
            json={"member_id": member["id"], "parcel_id": parcel["id"]}, headers=headers,
        )
        member["parcel_id"] = parcel["id"]
    return member


async def _worked(client, headers, member, hours):
    session = (await client.post(
        "/api/v1/work-hours/sessions",
        json={"title": "Einsatz", "type": "STANDARD", "date": "2026-04-01"}, headers=headers,
    )).json()
    response = await client.post(
        f"/api/v1/work-hours/sessions/{session['id']}/participations",
        json={"member_id": member["id"], "status": "ATTENDED", "hours_completed": str(hours)}, headers=headers,
    )
    assert response.status_code == 201, response.text


async def _transfer(client, headers, giver, receiver, hours):
    return await client.post("/api/v1/work-hours/transfers", json={
        "giver_member_id": giver["id"], "receiver_member_id": receiver["id"], "year": 2026, "hours": str(hours),
    }, headers=headers)


async def _total(member_id):
    async with AsyncSessionLocal() as db:
        return (await calculate_hours_for_member(db, member_id, 2026))["total"]


async def test_per_member_gives_only_the_surplus(client, admin_user):
    headers = await _setup(client, "PER_MEMBER")
    busy = await _member(client, headers, "Fleissig", "T1")
    friend = await _member(client, headers, "Nachbar", "T2")
    await _worked(client, headers, busy, 8)

    too_much = await _transfer(client, headers, busy, friend, 3.5)
    assert too_much.status_code == 422 and "3.0" in too_much.json()["detail"]
    assert (await _transfer(client, headers, busy, busy, 1)).status_code == 422

    given = await _transfer(client, headers, busy, friend, 3)
    assert given.status_code == 201, given.text
    assert await _total(busy["id"]) == 5.0 and await _total(friend["id"]) == 3.0
    assert (await _transfer(client, headers, busy, friend, 0.5)).status_code == 422  # surplus used up

    rows = {r["label"]: r for r in (await client.get("/api/v1/work-hours/evaluation/2026", headers=headers)).json()}
    assert rows["Test Fleissig"]["fulfilled"] is True
    assert float(rows["Test Nachbar"]["hours_open"]) == 2.0

    listed = (await client.get("/api/v1/work-hours/transfers?year=2026", headers=headers)).json()
    assert [float(t["hours"]) for t in listed] == [3.0]
    assert (await client.delete(f"/api/v1/work-hours/transfers/{listed[0]['id']}", headers=headers)).status_code == 204
    assert await _total(friend["id"]) == 0.0


async def test_per_parcel_keeps_the_givers_plot_fulfilled(client, admin_user):
    """Pooled hours: the giver can't push their own plot below its
    requirement, and can't give a co-tenant's hours either."""
    headers = await _setup(client, "PER_PARCEL")
    giver = await _member(client, headers, "Geber", "T10")
    cotenant = await _member(client, headers, "Mitpaechter")
    await client.post(
        f"/api/v1/parcels/{giver['parcel_id']}/assignments",
        json={"member_id": cotenant["id"], "parcel_id": giver["parcel_id"]}, headers=headers,
    )
    receiver = await _member(client, headers, "Empfaenger", "T11")
    await _worked(client, headers, giver, 2)
    await _worked(client, headers, cotenant, 6)  # plot T10: 8 h, 3 h surplus -- but only 2 h are the giver's

    capped = await _transfer(client, headers, giver, receiver, 2.5)
    assert capped.status_code == 422 and "2.0" in capped.json()["detail"]
    assert (await _transfer(client, headers, giver, receiver, 2)).status_code == 201

    rows = {r["label"]: r for r in (await client.get("/api/v1/work-hours/evaluation/2026", headers=headers)).json()}
    assert float(rows["T10"]["hours_completed"]) == 6.0 and rows["T10"]["fulfilled"] is True
    assert float(rows["T11"]["hours_completed"]) == 2.0
    # The co-tenant's 1 h of remaining surplus is still capped by the plot.
    assert (await _transfer(client, headers, cotenant, receiver, 1.5)).status_code == 422
    assert (await _transfer(client, headers, cotenant, receiver, 1)).status_code == 201


async def test_helper_without_a_plot_gives_all_hours_via_the_web_ui(client, admin_user):
    headers = await _setup(client, "PER_PARCEL")
    helper = await _member(client, headers, "Helfer")
    receiver = await _member(client, headers, "Empfaenger", "T20")
    await _worked(client, headers, helper, 4)

    await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})
    page = await client.get("/work-hours/transfers?year=2026")
    assert page.status_code == 200 and "Test Helfer" in page.text

    form = {"year": "2026", "giver_member_id": helper["id"], "receiver_member_id": receiver["id"], "hours": "4,0"}
    response = await client.post("/work-hours/transfers/new", data=form)
    assert response.status_code == 303 and "error" not in response.headers["location"]
    refused = await client.post("/work-hours/transfers/new", data={**form, "hours": "1"})
    assert refused.status_code == 303 and "error=" in refused.headers["location"]

    evaluation = await client.get("/work-hours/evaluation?year=2026")
    assert evaluation.status_code == 200
    assert "+4,0 h" in evaluation.text or "+4.0 h" in evaluation.text
    assert "Test Helfer" in (await client.get("/work-hours/transfers?year=2026")).text


async def test_nan_hours_and_per_member_helper(client, admin_user):
    """Review findings: float("nan") passed every comparison; a helper
    without a lease owes nothing in PER_MEMBER mode either."""
    headers = await _setup(client, "PER_MEMBER")
    helper = await _member(client, headers, "Helfer")
    receiver = await _member(client, headers, "Empfaenger", "T30")
    await _worked(client, headers, helper, 4)
    assert (await _transfer(client, headers, helper, receiver, 4)).status_code == 201

    await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})
    form = {"year": "2026", "giver_member_id": receiver["id"], "receiver_member_id": helper["id"], "hours": "nan"}
    response = await client.post("/work-hours/transfers/new", data=form)
    assert "error=" in response.headers["location"]
    assert await _total(helper["id"]) == 0.0
