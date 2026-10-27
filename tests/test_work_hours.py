"""
Tests for the Work Hours module. Focus on the business logic with
higher regression risk: group exemption under PER_PARCEL (any() instead
of all() -- see Architecture Decisions) and the annual evaluation.
"""
from datetime import date, timedelta

from app.database import AsyncSessionLocal
from app.models import WorkSession, SessionType, WorkHoursConfiguration, WorkHoursMode, Sponsorship
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


async def test_staff_can_still_add_participant_to_a_past_session(client, admin_user):
    """The signup deadline / "session already passed" rule
    (WorkSession.public_signup_open) is scoped to the public
    self-service signup API only -- staff adding a participant in
    Parcella itself (normally used to record attendance after the
    fact) must keep working for a session whose date, or configured
    signup_deadline_days, has already lapsed."""
    token = await login(client, "admin@example.com")
    headers = auth_header(token)

    member = (await client.post(
        "/api/v1/members", json={"first_name": "Klaus", "last_name": "Fleissig"}, headers=headers
    )).json()

    yesterday = (date.today() - timedelta(days=1)).isoformat()
    session = (await client.post(
        "/api/v1/work-hours/sessions",
        json={"title": "Past Session", "type": "STANDARD", "date": yesterday, "signup_deadline_days": 30},
        headers=headers,
    )).json()

    # Via the API.
    participation = await client.post(
        f"/api/v1/work-hours/sessions/{session['id']}/participations",
        json={"member_id": member["id"], "status": "ATTENDED"},
        headers=headers,
    )
    assert participation.status_code == 201

    # Via the HTML form, same session.
    other_member = (await client.post(
        "/api/v1/members", json={"first_name": "Erika", "last_name": "Musterfrau"}, headers=headers
    )).json()
    web_login = await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})
    assert web_login.status_code in (302, 303)
    add = await client.post(
        f"/work-hours/sessions/{session['id']}/participants/add",
        data={"member_id": other_member["id"], "status": "ATTENDED"},
    )
    assert add.status_code in (302, 303)


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


async def test_member_with_two_exempt_roles_in_same_year_does_not_crash_evaluation(client, admin_user):
    """A member can hold more than one ClubRole in the same year (e.g.
    chair + treasurer). is_exempt() used scalar_one_or_none() on a
    query that can legitimately match more than one MemberClubRole row
    in that case, raising MultipleResultsFound and 500ing the whole
    evaluation page/API -- reproduced for real in production once real
    membership data had a double-role board member (this exact
    scenario never occurred in the smaller local/test data). The fix
    (.limit(1), since this is a pure existence check) makes the row
    count irrelevant."""
    token = await login(client, "admin@example.com")
    headers = auth_header(token)

    await _erstelle_configuration(client, headers, year=2026, mode="PER_PARCEL")

    doppelrolle = (await client.post(
        "/api/v1/members", json={"first_name": "Doppel", "last_name": "Rolle"}, headers=headers
    )).json()
    parcel = (await client.post(
        "/api/v1/parcels", json={"plot_number": "G101"}, headers=headers
    )).json()
    await client.post(
        f"/api/v1/parcels/{parcel['id']}/assignments",
        json={"member_id": doppelrolle["id"], "parcel_id": parcel["id"]},
        headers=headers,
    )

    chair_role = (await client.post(
        "/api/v1/work-hours/club-roles",
        json={"name": "Vorsitzender", "hours_exempt": True, "exemption_reason": "BOARD"},
        headers=headers,
    )).json()
    treasurer_role = (await client.post(
        "/api/v1/work-hours/club-roles",
        json={"name": "Kassenwart", "hours_exempt": True, "exemption_reason": "BOARD"},
        headers=headers,
    )).json()

    for role in (chair_role, treasurer_role):
        assignment = await client.post(
            "/api/v1/work-hours/club-roles/assignments",
            json={"member_id": doppelrolle["id"], "club_role_id": role["id"], "year": 2026},
            headers=headers,
        )
        assert assignment.status_code == 201

    evaluation_response = await client.get("/api/v1/work-hours/evaluation/2026", headers=headers)
    assert evaluation_response.status_code == 200
    row = next(z for z in evaluation_response.json() if z["label"] == "G101")
    assert row["exempt"] is True

    await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})
    html_response = await client.get("/work-hours/evaluation", params={"year": 2026})
    assert html_response.status_code == 200
    assert "G101" in html_response.text


async def test_former_leaser_excluded_from_annual_evaluation(client, admin_user):
    """Issue #206: evaluate_parcel() only filtered tenants by whether the
    MEMBER is still active, never whether this specific tenancy
    (MemberParcel.is_current) is still current -- so a member whose
    lease on a parcel already ended (assigned_until in the past) kept
    being counted as a tenant of that parcel. Two cases: a parcel with
    only a terminated tenant must vanish entirely (vacant of current
    tenants); a parcel with one current + one terminated tenant must
    still appear, reflecting only the current tenant."""
    token = await login(client, "admin@example.com")
    headers = auth_header(token)

    await _erstelle_configuration(client, headers, year=2026, mode="PER_PARCEL")

    former = (await client.post(
        "/api/v1/members", json={"first_name": "Peter", "last_name": "Ausgezogen"}, headers=headers
    )).json()
    current = (await client.post(
        "/api/v1/members", json={"first_name": "Sabine", "last_name": "Geblieben"}, headers=headers
    )).json()
    vacated_parcel = (await client.post(
        "/api/v1/parcels", json={"plot_number": "G206A"}, headers=headers
    )).json()
    mixed_parcel = (await client.post(
        "/api/v1/parcels", json={"plot_number": "G206B"}, headers=headers
    )).json()

    await client.post(
        f"/api/v1/parcels/{vacated_parcel['id']}/assignments",
        json={"member_id": former["id"], "parcel_id": vacated_parcel["id"], "assigned_until": "2025-12-31"},
        headers=headers,
    )
    await client.post(
        f"/api/v1/parcels/{mixed_parcel['id']}/assignments",
        json={"member_id": former["id"], "parcel_id": mixed_parcel["id"], "assigned_until": "2025-12-31"},
        headers=headers,
    )
    await client.post(
        f"/api/v1/parcels/{mixed_parcel['id']}/assignments",
        json={"member_id": current["id"], "parcel_id": mixed_parcel["id"]},
        headers=headers,
    )

    evaluation = (await client.get("/api/v1/work-hours/evaluation/2026", headers=headers)).json()
    labels = {row["label"] for row in evaluation}
    assert "G206A" not in labels, "parcel with only a terminated tenant must not appear at all"
    assert "G206B" in labels, "parcel with a current tenant must still appear"

    await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})
    html_response = await client.get("/work-hours/evaluation", params={"year": 2026})
    assert html_response.status_code == 200
    assert "G206A" not in html_response.text
    assert "G206B" in html_response.text


async def test_attended_participant_without_hours_override_counts_session_default(client, admin_user):
    """Issue #205: a participant marked ATTENDED without a manually
    entered hours_completed override was credited 0 hours in the annual
    evaluation instead of falling back to the session's
    hours_per_participant default -- the same fallback already used for
    the attendee-sheet PDF (app/routers/work_hours.py). Since attendees
    are typically added straight to ATTENDED with no hours typed in
    (participant_add's default), this meant most attendance simply
    didn't count."""
    token = await login(client, "admin@example.com")
    headers = auth_header(token)

    await _erstelle_configuration(client, headers, year=2026, mode="PER_PARCEL")

    member = (await client.post(
        "/api/v1/members", json={"first_name": "Anna", "last_name": "Fleissig"}, headers=headers
    )).json()
    parcel = (await client.post(
        "/api/v1/parcels", json={"plot_number": "G205"}, headers=headers
    )).json()
    await client.post(
        f"/api/v1/parcels/{parcel['id']}/assignments",
        json={"member_id": member["id"], "parcel_id": parcel["id"]},
        headers=headers,
    )

    session = (await client.post(
        "/api/v1/work-hours/sessions",
        json={"title": "Fruehjahrsputz", "type": "STANDARD", "date": "2026-04-01", "hours_per_participant": "4.0"},
        headers=headers,
    )).json()
    participation = await client.post(
        f"/api/v1/work-hours/sessions/{session['id']}/participations",
        json={"member_id": member["id"], "status": "ATTENDED"},
        headers=headers,
    )
    assert participation.status_code == 201

    evaluation = (await client.get("/api/v1/work-hours/evaluation/2026", headers=headers)).json()
    row = next(z for z in evaluation if z["label"] == "G205")
    assert float(row["hours_completed"]) == 4.0
    assert float(row["hours_open"]) == 1.0

    await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})
    html_response = await client.get("/work-hours/evaluation", params={"year": 2026})
    assert html_response.status_code == 200
    assert "G205" in html_response.text


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


async def test_configuration_and_evaluation_pages_show_fractional_hours_required(client, admin_user):
    """Same |int truncation bug as hours_per_participant (see
    test_session_detail_shows_fractional_hours_per_participant), but for
    WorkHoursConfiguration.hours_required -- also Numeric(*, 1) and thus
    also fractional. Hit every page that displays or edits it."""
    await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})

    async with AsyncSessionLocal() as db:
        config = WorkHoursConfiguration(
            year=2027, hours_required=4.5, rate_per_hour_eur=20.0, mode=WorkHoursMode.PER_PARCEL,
        )
        db.add(config)
        await db.commit()
        config_id = config.id

    overview = await client.get("/work-hours/", params={"year": 2027})
    assert overview.status_code == 200
    assert "4.5" in overview.text or "4,5" in overview.text

    configuration_list = await client.get("/work-hours/configuration")
    assert configuration_list.status_code == 200
    assert "4.5" in configuration_list.text or "4,5" in configuration_list.text

    configuration_edit = await client.get(f"/work-hours/configuration/{config_id}/edit")
    assert configuration_edit.status_code == 200
    assert 'value="4.5"' in configuration_edit.text

    evaluation = await client.get("/work-hours/evaluation", params={"year": 2027})
    assert evaluation.status_code == 200
    assert "4.5" in evaluation.text or "4,5" in evaluation.text


async def test_sponsorship_page_and_edit_form_show_fractional_hours(client, admin_user):
    """Same truncation bug for Sponsorship.credited_hours, plus the
    create-form's prefilled-from-config hint text."""
    await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})

    async with AsyncSessionLocal() as db:
        config = WorkHoursConfiguration(
            year=2027, hours_required=4.5, rate_per_hour_eur=20.0, mode=WorkHoursMode.PER_PARCEL,
        )
        sponsorship = Sponsorship(
            area="Hedge north side", credited_hours=3.5, valid_from=date(2027, 1, 1),
        )
        db.add_all([config, sponsorship])
        await db.commit()
        sponsorship_id = sponsorship.id

    sponsorships_page = await client.get("/work-hours/sponsorships", params={"year": 2027})
    assert sponsorships_page.status_code == 200
    assert "3.5" in sponsorships_page.text or "3,5" in sponsorships_page.text
    assert "4.5" in sponsorships_page.text or "4,5" in sponsorships_page.text

    sponsorship_edit = await client.get(f"/work-hours/sponsorships/{sponsorship_id}/edit")
    assert sponsorship_edit.status_code == 200
    assert 'value="3.5"' in sponsorship_edit.text


async def test_sponsorship_can_be_created_unclaimed_and_shows_regardless_of_year(client, admin_user):
    """Issue #213: a sponsorship area can be advertised before anyone
    has committed to it -- no member and no valid_from. Such a row has
    no year of its own, so it must show up in the active table no
    matter which year is selected."""
    await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})

    create = await client.post(
        "/work-hours/sponsorships/new",
        data={"area": "Compost area", "credited_hours": "4.0"},
    )
    assert create.status_code == 302

    for year in (2020, 2099):
        page = await client.get("/work-hours/sponsorships", params={"year": year})
        assert page.status_code == 200
        assert "Compost area" in page.text


async def test_former_sponsorship_listed_in_history_table(client, admin_user):
    """A sponsorship whose valid_until has already passed used to
    simply disappear once its year fell out of view. It must now show
    up permanently in the 'Former Sponsorships' table (issue #213)."""
    async with AsyncSessionLocal() as db:
        db.add(Sponsorship(
            area="Old playground fence", credited_hours=2.0,
            valid_from=date(2020, 1, 1), valid_until=date(2020, 12, 31),
        ))
        await db.commit()

    await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})
    page = await client.get("/work-hours/sponsorships", params={"year": 2026})
    assert page.status_code == 200
    # The area name also legitimately appears in the create card's
    # autocomplete <datalist> (all known areas, any year) -- only check
    # that it shows up in the dedicated former-sponsorships section.
    former_section = page.text.split("Former Sponsorships", 1)[1]
    assert "Old playground fence" in former_section


async def test_sponsorship_ended_this_year_only_shows_as_former_not_active(client, admin_user):
    """A sponsorship that ended earlier in the *current* calendar year
    used to satisfy the active table's year-overlap check and so showed
    up there too, at the same time as in the Former table below -- filed
    the same day issue #213 shipped. Ended-as-of-today must exclude a
    row from the active table regardless of the selected year."""
    today = date.today()
    async with AsyncSessionLocal() as db:
        db.add(Sponsorship(
            area="Already ended this year", credited_hours=2.0,
            valid_from=date(today.year, 1, 1), valid_until=today - timedelta(days=1),
        ))
        await db.commit()

    await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})
    page = await client.get("/work-hours/sponsorships", params={"year": today.year})
    assert page.status_code == 200

    # Isolate the active table's own body -- the create card's area
    # <datalist> (all areas ever used, for autocomplete) sits above the
    # "Active Sponsorships" heading and legitimately contains every area
    # name, ended ones included.
    active_table_section, former_section = page.text.split("Active Sponsorships", 1)[1].split(
        "Former Sponsorships", 1
    )
    assert "Already ended this year" not in active_table_section
    assert "Already ended this year" in former_section


async def test_sponsorship_member_select_sorted_by_plot_number(client, admin_user):
    """Kermie asked for the sponsorship member picker to be labeled and
    sorted by plot number first (e.g. "G001 - Peter Ahnert"), not
    alphabetically by name -- a large club gets scanned by garden plot
    far more often than by surname. Members without any current plot
    sort last, after every plot-holder (issue #213 follow-up)."""
    token = await login(client, "admin@example.com")
    headers = auth_header(token)

    async def _member_with_plot(first, last, plot_number):
        member = (await client.post(
            "/api/v1/members", json={"first_name": first, "last_name": last}, headers=headers
        )).json()
        parcel = (await client.post(
            "/api/v1/parcels", json={"plot_number": plot_number}, headers=headers
        )).json()
        await client.post(
            f"/api/v1/parcels/{parcel['id']}/assignments",
            json={"member_id": member["id"], "parcel_id": parcel["id"]},
            headers=headers,
        )

    await _member_with_plot("Petra", "Picker", "T042")
    await _member_with_plot("Peter", "Ahnert", "G001")
    await client.post(
        "/api/v1/members", json={"first_name": "Aaron", "last_name": "Aaronson"}, headers=headers
    )

    await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})
    page = await client.get("/work-hours/sponsorships")
    assert page.status_code == 200

    assert "G001 - Peter Ahnert" in page.text
    assert "T042 - Petra Picker" in page.text
    assert "Aaron Aaronson" in page.text
    assert (
        page.text.index("G001 - Peter Ahnert")
        < page.text.index("T042 - Petra Picker")
        < page.text.index("Aaron Aaronson")
    )


async def test_session_detail_signup_search_includes_name_and_plot_number(client, admin_user):
    """The "add participant" control used to be a plain <select> of
    member names only -- unusable for a large club and impossible to
    search by garden plot number. It's now a JS-driven search box fed
    by a JSON payload of {id, name, plots}; confirm that payload
    actually carries the plot number, and that the old <select> is gone."""
    token = await login(client, "admin@example.com")
    headers = auth_header(token)

    member = (await client.post(
        "/api/v1/members", json={"first_name": "Petra", "last_name": "Picker"}, headers=headers
    )).json()
    parcel = (await client.post(
        "/api/v1/parcels", json={"plot_number": "T001"}, headers=headers
    )).json()
    await client.post(
        f"/api/v1/parcels/{parcel['id']}/assignments",
        json={"member_id": member["id"], "parcel_id": parcel["id"]},
        headers=headers,
    )
    session = (await client.post(
        "/api/v1/work-hours/sessions",
        json={"title": "Picker test session", "type": "STANDARD", "date": "2026-06-01"},
        headers=headers,
    )).json()

    await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})
    detail = await client.get(f"/work-hours/sessions/{session['id']}")
    assert detail.status_code == 200
    assert '"name": "Petra Picker"' in detail.text
    assert '"plots": "T001"' in detail.text
    assert 'id="add-participant-search"' in detail.text
    assert '<select name="member_id"' not in detail.text


async def test_lease_cancelled_during_the_year_still_counts_in_evaluation(client, admin_user):
    """Issue #239: cancelling a lease doesn't cancel that year's work
    hours. A tenancy that ended in June 2026 must still appear in the
    2026 evaluation with the full requirement (pooled on the parcel in
    PER_PARCEL mode), marked "lease ended". Leases that ended before the
    year (issue #206) or start after it stay out."""
    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _erstelle_configuration(client, headers, year=2026, mode="PER_PARCEL")

    async def member(last_name):
        return (await client.post(
            "/api/v1/members", json={"first_name": "Test", "last_name": last_name}, headers=headers
        )).json()

    async def parcel_with(plot_number, *tenancies):
        parcel = (await client.post("/api/v1/parcels", json={"plot_number": plot_number}, headers=headers)).json()
        for m, extra in tenancies:
            response = await client.post(
                f"/api/v1/parcels/{parcel['id']}/assignments",
                json={"member_id": m["id"], "parcel_id": parcel["id"], **extra}, headers=headers,
            )
            assert response.status_code in (200, 201), response.text
        return parcel

    leaver = await member("Gekuendigt")
    successor = await member("Nachfolger")
    future = await member("Zukunft")
    await parcel_with("G239A", (leaver, {"assigned_until": "2026-06-30"}))
    await parcel_with(
        "G239B",
        (await member("Vorgaenger"), {"assigned_until": "2026-07-01"}),
        (successor, {"assigned_from": "2026-07-01"}),
    )
    await parcel_with("G239C", (future, {"assigned_from": "2027-01-01"}))

    rows = {row["label"]: row for row in (await client.get("/api/v1/work-hours/evaluation/2026", headers=headers)).json()}
    assert "G239A" in rows, "a lease cancelled during the year still owes that year's hours"
    assert float(rows["G239A"]["hours_required"]) == 5.0 and float(rows["G239A"]["hours_open"]) == 5.0
    assert "G239B" in rows
    assert "G239C" not in rows, "a lease starting next year owes nothing this year"

    await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})
    page = await client.get("/work-hours/evaluation", params={"year": 2026})
    assert page.status_code == 200
    assert "Gekuendigt" in page.text and "30.06.2026" in page.text
    assert "Vorgaenger" in page.text and "Nachfolger" in page.text


async def test_lease_cancelled_during_the_year_counts_per_member_and_is_billed(client, admin_user):
    """Issue #239 in PER_MEMBER mode: the ex-tenant gets their own row,
    and invoicing (which reads the same evaluation) bills their
    shortfall. For the year before they left they are an ordinary
    full-year tenant -- no "lease ended" mark there."""
    from app.work_hours_evaluation import compute_work_hours_shortfalls

    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _erstelle_configuration(client, headers, year=2026, mode="PER_MEMBER")
    await _erstelle_configuration(client, headers, year=2025, mode="PER_MEMBER")

    leaver = (await client.post(
        "/api/v1/members", json={"first_name": "Test", "last_name": "Weggezogen"}, headers=headers
    )).json()
    parcel = (await client.post("/api/v1/parcels", json={"plot_number": "G239M"}, headers=headers)).json()
    await client.post(
        f"/api/v1/parcels/{parcel['id']}/assignments",
        json={"member_id": leaver["id"], "parcel_id": parcel["id"], "assigned_until": "2026-05-15"},
        headers=headers,
    )

    labels = {row["label"] for row in (await client.get("/api/v1/work-hours/evaluation/2026", headers=headers)).json()}
    assert "Test Weggezogen" in labels

    async with AsyncSessionLocal() as db:
        mode, _, by_member = await compute_work_hours_shortfalls(db, 2026)
    assert mode == WorkHoursMode.PER_MEMBER
    assert by_member[leaver["id"]] == 5.0 * 25.0

    await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})
    page_2026 = await client.get("/work-hours/evaluation", params={"year": 2026})
    assert "15.05.2026" in page_2026.text
    page_2025 = await client.get("/work-hours/evaluation", params={"year": 2025})
    assert "Weggezogen" in page_2025.text and "15.05.2026" not in page_2025.text


async def test_member_who_moved_plots_mid_year_counts_once(client, admin_user):
    """Review finding on issue #239: a member who moves from plot A to
    plot B within the club during the year is a tenant of both for that
    year, but their hours (and an exemption) are per member -- they must
    count on B only, not fulfil both plots with one person-year."""
    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _erstelle_configuration(client, headers, year=2026, mode="PER_PARCEL")

    mover = (await client.post(
        "/api/v1/members", json={"first_name": "Test", "last_name": "Umzug"}, headers=headers
    )).json()
    old_plot = (await client.post("/api/v1/parcels", json={"plot_number": "G239X"}, headers=headers)).json()
    new_plot = (await client.post("/api/v1/parcels", json={"plot_number": "G239Y"}, headers=headers)).json()
    await client.post(
        f"/api/v1/parcels/{old_plot['id']}/assignments",
        json={"member_id": mover["id"], "parcel_id": old_plot["id"], "assigned_until": "2026-06-30"},
        headers=headers,
    )
    await client.post(
        f"/api/v1/parcels/{new_plot['id']}/assignments",
        json={"member_id": mover["id"], "parcel_id": new_plot["id"], "assigned_from": "2026-07-01"},
        headers=headers,
    )

    labels = {row["label"] for row in (await client.get("/api/v1/work-hours/evaluation/2026", headers=headers)).json()}
    assert "G239Y" in labels
    assert "G239X" not in labels, "the plot they left has no other tenant in the year"


async def test_sponsorship_ended_mid_year_still_counts_its_full_hours(client, admin_user):
    """Issue #245: a sponsorship cancelled during the year still counts
    with its full credited hours for that year."""
    from app.models import Member
    from app.services.work_hours import calculate_hours_for_member

    async with AsyncSessionLocal() as db:
        member = Member(first_name="Detlef", last_name="Hedge")
        db.add(member)
        await db.flush()
        db.add(Sponsorship(
            member_id=member.id, area="Hedge at the BBQ area", credited_hours=2.5,
            valid_from=date(2026, 3, 21), valid_until=date(2026, 5, 20),
        ))
        await db.commit()
        hours = await calculate_hours_for_member(db, member.id, 2026)
    assert hours["sponsorship_hours"] == 2.5


async def test_sponsorship_end_before_start_is_rejected(client, admin_user):
    """Issue #245: a sponsorship entered as 21.03.2026 - 20.05.2025 (a
    typo in the year) overlaps no year at all, so the evaluation silently
    credited the member nothing. The web forms and the API must refuse
    it, and the web forms must keep what was typed."""
    from sqlalchemy import select

    await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})
    bad_dates = {"valid_from": "2026-03-21", "valid_until": "2025-05-20"}

    create = await client.post(
        "/work-hours/sponsorships/new",
        data={"area": "Hedge at the BBQ area", "credited_hours": "2.5", **bad_dates},
    )
    assert create.status_code == 400
    assert "The end date is before the start date" in create.text
    assert 'value="Hedge at the BBQ area"' in create.text
    assert 'value="2025-05-20"' in create.text

    async with AsyncSessionLocal() as db:
        assert (await db.execute(select(Sponsorship))).scalars().all() == []

    ok = await client.post(
        "/work-hours/sponsorships/new",
        data={"area": "Hedge at the BBQ area", "credited_hours": "2.5", "valid_from": "2026-03-21"},
    )
    assert ok.status_code == 302
    async with AsyncSessionLocal() as db:
        sponsorship_id = (await db.execute(select(Sponsorship.id))).scalar_one()

    edit = await client.post(
        f"/work-hours/sponsorships/{sponsorship_id}/edit",
        data={"area": "Renamed hedge", "credited_hours": "2.5", **bad_dates},
    )
    assert edit.status_code == 400
    assert "The end date is before the start date" in edit.text
    assert 'value="Renamed hedge"' in edit.text

    headers = auth_header(await login(client, "admin@example.com"))
    api_create = await client.post(
        "/api/v1/work-hours/sponsorships",
        json={"area": "API hedge", "credited_hours": "2.5", **bad_dates},
        headers=headers,
    )
    assert api_create.status_code == 422
    # A partial update is checked against the stored start date.
    api_update = await client.put(
        f"/api/v1/work-hours/sponsorships/{sponsorship_id}",
        json={"valid_until": "2025-05-20"},
        headers=headers,
    )
    assert api_update.status_code == 422

    async with AsyncSessionLocal() as db:
        stored = await db.get(Sponsorship, sponsorship_id)
        assert stored.area == "Hedge at the BBQ area"
        assert stored.valid_until is None


async def test_existing_sponsorship_with_end_before_start_is_flagged(client, admin_user):
    """Rows saved before the check (issue #245) get a badge so they can
    be found and corrected."""
    async with AsyncSessionLocal() as db:
        db.add(Sponsorship(
            area="Typo hedge", credited_hours=2.5,
            valid_from=date(2026, 3, 21), valid_until=date(2025, 5, 20),
        ))
        await db.commit()

    await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})
    page = await client.get("/work-hours/sponsorships", params={"year": 2026})
    assert page.status_code == 200
    former_section = page.text.split("Former Sponsorships", 1)[1]
    assert "Typo hedge" in former_section
    assert "End before start" in former_section


async def test_evaluation_lists_attended_sessions_per_member(client, admin_user):
    """Issue #258: each evaluation row expands into the member's attended
    work sessions of that year -- in both modes, only ATTENDED ones (the
    same rule the session-hours column counts), and only that year's."""
    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _erstelle_configuration(client, headers, year=2026, mode="PER_PARCEL")

    member = (await client.post(
        "/api/v1/members", json={"first_name": "Erna", "last_name": "Emsig"}, headers=headers
    )).json()
    idle = (await client.post(
        "/api/v1/members", json={"first_name": "Otto", "last_name": "Ohnefleiss"}, headers=headers
    )).json()
    for plot_number, tenant in (("G258A", member), ("G258B", idle)):
        parcel = (await client.post("/api/v1/parcels", json={"plot_number": plot_number}, headers=headers)).json()
        await client.post(
            f"/api/v1/parcels/{parcel['id']}/assignments",
            json={"member_id": tenant["id"], "parcel_id": parcel["id"]}, headers=headers,
        )

    async def session_with(title, day, status):
        session = (await client.post(
            "/api/v1/work-hours/sessions",
            json={"title": title, "type": "STANDARD", "date": day, "hours_per_participant": "2.5"},
            headers=headers,
        )).json()
        response = await client.post(
            f"/api/v1/work-hours/sessions/{session['id']}/participations",
            json={"member_id": member["id"], "status": status}, headers=headers,
        )
        assert response.status_code == 201, response.text
        return session

    attended = await session_with("Hecke schneiden", "2026-05-02", "ATTENDED")
    await session_with("Nur angemeldet", "2026-06-06", "REGISTERED")
    await session_with("Letztes Jahr", "2025-09-13", "ATTENDED")

    await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})
    page = await client.get("/work-hours/evaluation", params={"year": 2026})
    assert page.status_code == 200
    assert f'href="/work-hours/sessions/{attended["id"]}"' in page.text
    assert "02.05.2026" in page.text
    assert "2.5 h" in page.text or "2,5 h" in page.text
    assert "Nur angemeldet" not in page.text
    assert "Letztes Jahr" not in page.text
    assert "No attended work sessions this year." in page.text  # Otto's row
    assert page.text.count('class="collapse evaluation-detail"') == 2

    await _erstelle_configuration(client, headers, year=2026, mode="PER_MEMBER")
    page = await client.get("/work-hours/evaluation", params={"year": 2026})
    assert f'href="/work-hours/sessions/{attended["id"]}"' in page.text


async def test_member_with_two_plots_owes_the_hours_for_each_plot(client, admin_user):
    """Under PER_PARCEL a member holding two plots owes the requirement
    for each of them, but their hours are per member and used to count
    in full on both plots: 7.5 h fulfilled two 5 h plots at once. They
    are now shared out in plot-number order -- the first plot gets what
    it needs, the next one the rest."""
    from tests.test_hours_transfers import _worked

    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _erstelle_configuration(client, headers, year=2026, mode="PER_PARCEL")

    schmidt = (await client.post(
        "/api/v1/members", json={"first_name": "Test", "last_name": "Schmidt"}, headers=headers
    )).json()
    for plot in ("G047", "G048"):
        parcel = (await client.post("/api/v1/parcels", json={"plot_number": plot}, headers=headers)).json()
        await client.post(
            f"/api/v1/parcels/{parcel['id']}/assignments",
            json={"member_id": schmidt["id"], "parcel_id": parcel["id"]}, headers=headers,
        )
    await _worked(client, headers, schmidt, 7.5)

    rows = {r["label"]: r for r in (await client.get("/api/v1/work-hours/evaluation/2026", headers=headers)).json()}
    assert float(rows["G047"]["hours_completed"]) == 5.0 and rows["G047"]["fulfilled"] is True
    assert float(rows["G048"]["hours_completed"]) == 2.5 and rows["G048"]["fulfilled"] is False
    assert float(rows["G048"]["hours_open"]) == 2.5
    assert float(rows["G048"]["amount_due_eur"]) == 62.5

    await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})
    html = (await client.get("/work-hours/evaluation", params={"year": 2026})).text
    assert "5,0 of 7,5 h" in html and "2,5 of 7,5 h" in html  # de-DE number format

    csv_text = (await client.get("/work-hours/evaluation/csv", params={"year": 2026})).text
    csv_rows = {line.split(";")[0]: line.split(";") for line in csv_text.splitlines()[1:]}
    assert csv_rows["G047"][6] == "5.0" and csv_rows["G048"][6] == "2.5"


async def test_member_with_two_plots_fills_what_a_cotenant_left_open(client, admin_user):
    """The share-out counts single-plot co-tenants first: a plot already
    fulfilled by its co-tenant needs nothing from the multi-plot member,
    so all of their hours go to their other plot."""
    from tests.test_hours_transfers import _worked

    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _erstelle_configuration(client, headers, year=2026, mode="PER_PARCEL")

    def member(last_name):
        return client.post("/api/v1/members", json={"first_name": "Test", "last_name": last_name}, headers=headers)

    owner = (await member("Zweigarten")).json()
    cotenant = (await member("Mitpaechter")).json()
    first = (await client.post("/api/v1/parcels", json={"plot_number": "M1"}, headers=headers)).json()
    second = (await client.post("/api/v1/parcels", json={"plot_number": "M2"}, headers=headers)).json()
    for m, parcel in ((owner, first), (cotenant, first), (owner, second)):
        await client.post(
            f"/api/v1/parcels/{parcel['id']}/assignments",
            json={"member_id": m["id"], "parcel_id": parcel["id"]}, headers=headers,
        )
    await _worked(client, headers, cotenant, 5)
    await _worked(client, headers, owner, 6)

    rows = {r["label"]: r for r in (await client.get("/api/v1/work-hours/evaluation/2026", headers=headers)).json()}
    assert float(rows["M1"]["hours_completed"]) == 5.0 and rows["M1"]["fulfilled"] is True
    assert float(rows["M2"]["hours_completed"]) == 6.0 and rows["M2"]["fulfilled"] is True
