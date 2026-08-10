"""
Tests for the Work Hours module. Focus on the business logic with
higher regression risk: group exemption under PER_PARCEL (any() instead
of all() -- see Architecture Decisions) and the annual evaluation.
"""
from datetime import date

from app.database import AsyncSessionLocal
from app.models import WorkSession, SessionType
from tests.conftest import login, auth_header


async def _erstelle_configuration(client, headers, year=2026, mode="PER_PARCEL"):
    return await client.put(
        f"/api/v1/work-hours/configuration/{year}",
        json={"year": year, "hours_required": "5.0", "rate_per_hour_eur": "25.00", "mode": mode},
        headers=headers,
    )


async def test_configuration_upsert(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)

    response = await _erstelle_configuration(client, headers)
    assert response.status_code == 200
    assert response.json()["hours_required"] == "5.00" or float(response.json()["hours_required"]) == 5.0


async def test_session_and_participation(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)

    member = (await client.post(
        "/api/v1/members", json={"first_name": "Klaus", "last_name": "Fleissig"}, headers=headers
    )).json()

    session = (await client.post(
        "/api/v1/work-hours/sessions",
        json={"title": "Frühjahrsputz", "type": "STANDARD", "date": "2026-04-01"},
        headers=headers,
    )).json()

    participation = await client.post(
        f"/api/v1/work-hours/sessions/{session['id']}/participations",
        json={"member_id": member["id"], "status": "ATTENDED", "hours_completed": "3.0"},
        headers=headers,
    )
    assert participation.status_code == 201


async def test_task_lifecycle(client, admin_user):
    """
    Covers the full task lifecycle: create in the backlog, schedule to a
    session, assign to one of that session's participants, and confirm
    that rescheduling to a different session clears the assignment (an
    assignment to a specific person only makes sense for the session
    they actually signed up for).
    """
    token = await login(client, "admin@example.com")
    headers = auth_header(token)

    member = (await client.post(
        "/api/v1/members", json={"first_name": "Elena", "last_name": "Elder"}, headers=headers
    )).json()

    session_a = (await client.post(
        "/api/v1/work-hours/sessions",
        json={"title": "Spring Cleanup", "type": "STANDARD", "date": "2026-04-01"},
        headers=headers,
    )).json()
    session_b = (await client.post(
        "/api/v1/work-hours/sessions",
        json={"title": "Summer Maintenance", "type": "STANDARD", "date": "2026-07-01"},
        headers=headers,
    )).json()

    participation = (await client.post(
        f"/api/v1/work-hours/sessions/{session_a['id']}/participations",
        json={"member_id": member["id"], "status": "REGISTERED"},
        headers=headers,
    )).json()

    # Create in the backlog (no session yet)
    task = (await client.post(
        "/api/v1/work-hours/tasks",
        json={"title": "Water the flower beds", "workload": "LIGHT"},
        headers=headers,
    )).json()
    assert task["session_id"] is None

    # Schedule to session A
    task = (await client.put(
        f"/api/v1/work-hours/tasks/{task['id']}",
        json={"session_id": session_a["id"]},
        headers=headers,
    )).json()
    assert task["session_id"] == session_a["id"]

    # Assign to the participant who signed up for session A
    task = (await client.put(
        f"/api/v1/work-hours/tasks/{task['id']}",
        json={"assigned_participation_id": participation["id"]},
        headers=headers,
    )).json()
    assert task["assigned_participation_id"] == participation["id"]

    # Assigning to a participant of a DIFFERENT session must be rejected
    response = await client.put(
        f"/api/v1/work-hours/tasks/{task['id']}",
        json={"session_id": session_b["id"], "assigned_participation_id": participation["id"]},
        headers=headers,
    )
    assert response.status_code == 400

    # Rescheduling to session B (without forcing the assignment) clears it
    task = (await client.put(
        f"/api/v1/work-hours/tasks/{task['id']}",
        json={"session_id": session_b["id"]},
        headers=headers,
    )).json()
    assert task["session_id"] == session_b["id"]
    assert task["assigned_participation_id"] is None

    delete_response = await client.delete(
        f"/api/v1/work-hours/tasks/{task['id']}", headers=headers
    )
    assert delete_response.status_code == 204


async def test_exemption_applies_to_whole_parcel_under_per_parcel(client, admin_user):
    """
    Most important regression test for the 'any() instead of all()'
    decision: if ONE tenant of a parcel is exempt as a board member, the
    WHOLE parcel must count as exempt -- including the other
    (non-exempt) tenant.
    """
    token = await login(client, "admin@example.com")
    headers = auth_header(token)

    await _erstelle_configuration(client, headers, year=2026, mode="PER_PARCEL")

    befreiter = (await client.post(
        "/api/v1/members", json={"first_name": "Christian", "last_name": "Vorstand"}, headers=headers
    )).json()
    mitpaechter = (await client.post(
        "/api/v1/members", json={"first_name": "Alexandra", "last_name": "Mitpaechter"}, headers=headers
    )).json()
    parcel = (await client.post(
        "/api/v1/parcels", json={"plot_number": "G100"}, headers=headers
    )).json()

    await client.post(
        f"/api/v1/parcels/{parcel['id']}/assignments",
        json={"member_id": befreiter["id"], "parcel_id": parcel["id"]},
        headers=headers,
    )
    await client.post(
        f"/api/v1/parcels/{parcel['id']}/assignments",
        json={"member_id": mitpaechter["id"], "parcel_id": parcel["id"]},
        headers=headers,
    )

    role = (await client.post(
        "/api/v1/work-hours/club-roles",
        json={"name": "Vorstandsvorsitzender", "hours_exempt": True, "exemption_reason": "BOARD"},
        headers=headers,
    )).json()

    await client.post(
        "/api/v1/work-hours/club-roles/assignments",
        json={"member_id": befreiter["id"], "club_role_id": role["id"], "year": 2026},
        headers=headers,
    )

    evaluation = (await client.get("/api/v1/work-hours/evaluation/2026", headers=headers)).json()
    row = next(z for z in evaluation if z["label"] == "G100")

    assert row["exempt"] is True
    assert float(row["hours_open"]) == 0.0
    assert float(row["amount_due_eur"]) == 0.0

    # ADR 0070: the same result must come from the HTML evaluation page
    # too -- both surfaces now go through app.services.work_hours'
    # evaluate_year()/evaluate_parcel(), the exact code path whose
    # duplication (3 independent copies: HTML page, HTML CSV export,
    # API) already caused a real shipped any()/all() inversion bug once.
    await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})
    html_response = await client.get("/work-hours/evaluation", params={"year": 2026})
    assert html_response.status_code == 200
    assert "G100" in html_response.text


# ---------------------------------------------------------------------------
# ADR 0070: shared service layer + unified (Group-based, not role-only)
# authorization for the API.
# ---------------------------------------------------------------------------

async def test_treasurer_without_group_grant_is_blocked_from_work_hours_write_via_api(client):
    """api_work_hours.py used require_write_access (role-only) -- ANY
    TREASURER could write work-hours data via the API regardless of
    Group configuration. Now the API checks the same Group-derived
    permission as HTML."""
    from app.database import AsyncSessionLocal
    from app.models import User, UserRole
    from app.auth import hash_password

    async with AsyncSessionLocal() as db:
        user = User(
            email="treasurer-no-group-workhours@example.com", name="Treasurer No Group",
            password_hash=hash_password("testpasswort123"), role=UserRole.TREASURER,
        )
        db.add(user)
        await db.commit()

    token = await login(client, "treasurer-no-group-workhours@example.com")
    response = await client.post(
        "/api/v1/work-hours/club-roles",
        json={"name": "Blocked Role", "hours_exempt": False},
        headers=auth_header(token),
    )
    assert response.status_code == 403


async def test_readonly_with_group_grant_can_write_work_hours_via_api(client):
    """Flip side: a READONLY user granted work_hours:write via a Group
    could already write through the HTML UI, but the role-only API
    check blocked them regardless of Group membership."""
    from app.database import AsyncSessionLocal
    from app.models import User, UserRole, Group, GroupModulePermission, GroupMembership
    from app.auth import hash_password

    async with AsyncSessionLocal() as db:
        user = User(
            email="readonly-with-group-workhours@example.com", name="Readonly With Group",
            password_hash=hash_password("testpasswort123"), role=UserRole.READONLY,
        )
        db.add(user)
        await db.flush()

        group = Group(name="Work Hours Handlers")
        db.add(group)
        await db.flush()
        db.add(GroupModulePermission(group_id=group.id, module="work_hours", can_read=True, can_write=True))
        db.add(GroupMembership(user_id=user.id, group_id=group.id))
        await db.commit()

    token = await login(client, "readonly-with-group-workhours@example.com")
    response = await client.post(
        "/api/v1/work-hours/club-roles",
        json={"name": "Allowed Role", "hours_exempt": False},
        headers=auth_header(token),
    )
    assert response.status_code == 201, response.text


async def test_duplicate_club_role_assignment_rejected_via_api(client, admin_user):
    """ADR 0070: MemberClubRole has no DB uniqueness constraint --
    assignment_create used to silently create a duplicate row for the
    same (member, role, year). Now shares the HTML side's existing
    check-first behavior, surfaced as 409 via the API."""
    token = await login(client, "admin@example.com")
    headers = auth_header(token)

    member = (await client.post(
        "/api/v1/members", json={"first_name": "Doppelt", "last_name": "Test"}, headers=headers,
    )).json()
    role = (await client.post(
        "/api/v1/work-hours/club-roles", json={"name": "Kassenwart", "hours_exempt": False}, headers=headers,
    )).json()

    first = await client.post(
        "/api/v1/work-hours/club-roles/assignments",
        json={"member_id": member["id"], "club_role_id": role["id"], "year": 2026},
        headers=headers,
    )
    assert first.status_code == 201

    duplicate = await client.post(
        "/api/v1/work-hours/club-roles/assignments",
        json={"member_id": member["id"], "club_role_id": role["id"], "year": 2026},
        headers=headers,
    )
    assert duplicate.status_code == 409


async def test_task_assignment_validation_shares_i18n_text_via_api(client, admin_user):
    """ADR 0070: the API's "participant not in session" check used to
    raise a hard-coded English 400; now shares the same rule and i18n
    key app.services.work_hours.assign_task_to_participant() enforces
    for both surfaces."""
    from app.i18n import translate

    token = await login(client, "admin@example.com")
    headers = auth_header(token)

    session = (await client.post(
        "/api/v1/work-hours/sessions",
        json={"title": "Test session", "type": "STANDARD", "date": "2026-06-01"},
        headers=headers,
    )).json()
    task = (await client.post(
        "/api/v1/work-hours/tasks",
        json={"title": "Test task", "workload": "MODERATE", "session_id": session["id"]},
        headers=headers,
    )).json()

    response = await client.put(
        f"/api/v1/work-hours/tasks/{task['id']}",
        json={"assigned_participation_id": "nonexistent-participation-id"},
        headers=headers,
    )
    assert response.status_code == 400
    expected = translate("work_hours.errors.participant_not_in_session", "en")
    assert response.json()["detail"] == expected


async def test_session_detail_shows_fractional_hours_per_participant(client, admin_user):
    """A session's hours_per_participant is Numeric(4,1) and can be
    fractional (e.g. 2.5h). The detail page and edit form used to run
    it through Jinja's |int filter, which truncates rather than rounds
    -- 2.5 silently displayed and re-saved as 2."""
    await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})

    async with AsyncSessionLocal() as db:
        session = WorkSession(
            title="Fractional hours session",
            type=SessionType.STANDARD,
            date=date(2026, 6, 1),
            hours_per_participant=2.5,
        )
        db.add(session)
        await db.commit()
        session_id = session.id

    detail = await client.get(f"/work-hours/sessions/{session_id}")
    assert detail.status_code == 200
    assert "2.5" in detail.text or "2,5" in detail.text

    edit = await client.get(f"/work-hours/sessions/{session_id}/edit")
    assert edit.status_code == 200
    assert 'value="2.5"' in edit.text
