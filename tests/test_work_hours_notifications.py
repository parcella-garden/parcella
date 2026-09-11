"""
Tests for issue #217's work-hours half: informing about newly created
SessionParticipation rows via the dashboard tile, the second
/work-hours/ nav badge, the session-detail "New" badge, and an email
to active Admin/Board users. See app/services/work_hours.py
(count_new_participations, notify_new_participation,
notify_new_participations_digest) and docs/ADR/0079 for the design --
staff-initiated sign-ups get a per-row email (actor excluded), the
actorless public self-service signup path gets one digest email per
call instead of one per row.
"""
from datetime import date, datetime, timedelta, timezone

from app.database import AsyncSessionLocal
from app.models import Member, SessionParticipation, WorkSession, SessionType, ParticipationStatus
from tests.conftest import login, auth_header


async def web_login(client, email: str, password: str = "testpasswort123") -> None:
    response = await client.post("/auth/login", data={"email": email, "password": password})
    assert response.status_code in (302, 303)


async def _create_session_and_member(session_local, *, title="Frühjahrsputz"):
    async with session_local() as db:
        wsession = WorkSession(title=title, type=SessionType.STANDARD, date=date.today() + timedelta(days=10))
        member = Member(first_name="Klaus", last_name="Fleissig")
        db.add_all([wsession, member])
        await db.commit()
        await db.refresh(wsession)
        await db.refresh(member)
        return wsession.id, member.id


async def test_staff_participant_add_sends_email_excluding_actor(client, admin_user, board_user, monkeypatch):
    sent_to = []

    async def fake_send_email(recipient, subject, html_body, text_body=None, db=None):
        sent_to.append(recipient)
        return True

    monkeypatch.setattr("app.services.work_hours.send_email", fake_send_email)

    session_id, member_id = await _create_session_and_member(AsyncSessionLocal)

    # board_user performs the add -- must not receive their own
    # notification; admin_user must.
    await web_login(client, "vorstand@example.com")
    add = await client.post(
        f"/work-hours/sessions/{session_id}/participants/add",
        data={"member_id": member_id, "status": "ATTENDED"},
    )
    assert add.status_code in (302, 303)

    assert sent_to == ["admin@example.com"]

    # Re-adding the same member is a no-op (add_participation returns
    # None) and must NOT send a second email.
    again = await client.post(
        f"/work-hours/sessions/{session_id}/participants/add",
        data={"member_id": member_id, "status": "ATTENDED"},
    )
    assert again.status_code in (302, 303)
    assert sent_to == ["admin@example.com"]


async def test_api_participation_create_sends_email_excluding_actor(client, admin_user, board_user, monkeypatch):
    sent_to = []

    async def fake_send_email(recipient, subject, html_body, text_body=None, db=None):
        sent_to.append(recipient)
        return True

    monkeypatch.setattr("app.services.work_hours.send_email", fake_send_email)

    token = await login(client, "vorstand@example.com")
    headers = auth_header(token)

    member = (await client.post(
        "/api/v1/members", json={"first_name": "API", "last_name": "Newcomer"}, headers=headers,
    )).json()
    session = (await client.post(
        "/api/v1/work-hours/sessions",
        json={"title": "API Session", "type": "STANDARD", "date": (date.today() + timedelta(days=10)).isoformat()},
        headers=headers,
    )).json()

    participation = await client.post(
        f"/api/v1/work-hours/sessions/{session['id']}/participations",
        json={"member_id": member["id"], "status": "REGISTERED"},
        headers=headers,
    )
    assert participation.status_code == 201

    assert sent_to == ["admin@example.com"]


async def test_public_signup_sends_one_digest_email_not_per_row(client, admin_user, monkeypatch):
    """Issue #217: the public self-service signup path is actorless and
    can create several rows in one call -- must send exactly ONE digest
    email per API call, never one per created participation."""
    sent_to = []
    subjects = []

    async def fake_send_email(recipient, subject, html_body, text_body=None, db=None):
        sent_to.append(recipient)
        subjects.append(subject)
        return True

    monkeypatch.setattr("app.services.work_hours.send_email", fake_send_email)

    token = await login(client, "admin@example.com")
    headers = auth_header(token)

    await client.put(
        "/api/v1/club-settings/modul_public_signup_api", json={"value": "true"}, headers=headers,
    )
    await client.put(
        "/api/v1/club-settings/public_signup_api_token",
        json={"value": "test-public-api-token"}, headers=headers,
    )
    parcel = (await client.post("/api/v1/parcels", json={"plot_number": "G042"}, headers=headers)).json()
    resident_a = (await client.post(
        "/api/v1/members", json={"first_name": "Gerd", "last_name": "Mustergaertner"}, headers=headers,
    )).json()
    resident_b = (await client.post(
        "/api/v1/members", json={"first_name": "Erika", "last_name": "Musterfrau"}, headers=headers,
    )).json()
    await client.post(
        f"/api/v1/parcels/{parcel['id']}/assignments",
        json={"member_id": resident_a["id"], "parcel_id": parcel["id"]}, headers=headers,
    )
    await client.post(
        f"/api/v1/parcels/{parcel['id']}/assignments",
        json={"member_id": resident_b["id"], "parcel_id": parcel["id"]}, headers=headers,
    )
    session = (await client.post(
        "/api/v1/work-hours/sessions",
        json={"title": "Public Session", "type": "STANDARD", "date": (date.today() + timedelta(days=10)).isoformat()},
        headers=headers,
    )).json()

    sent_to.clear()  # drop notifications from the member/parcel setup above

    # No name given -> falls back to registering both current residents,
    # i.e. TWO SessionParticipation rows in this one call.
    signup = await client.post(
        "/api/v1/public/work-sessions/signup",
        json={"parcel_number": "G042", "session_ids": [session["id"]]},
        headers={"X-Parcella-API-Token": "test-public-api-token"},
    )
    assert signup.status_code == 200, signup.text

    assert sent_to == ["admin@example.com"]
    assert "2" in subjects[0]


async def test_dashboard_tile_nav_badge_and_session_new_badge(client, admin_user):
    session_id, member_id = await _create_session_and_member(AsyncSessionLocal)

    async with AsyncSessionLocal() as db:
        old_member = Member(first_name="Old", last_name="Hand")
        db.add(old_member)
        await db.flush()
        db.add(SessionParticipation(
            session_id=session_id, member_id=old_member.id, status=ParticipationStatus.REGISTERED,
            created_at=datetime.now(timezone.utc) - timedelta(days=100),
        ))
        await db.commit()

    await web_login(client, "admin@example.com")
    add = await client.post(
        f"/work-hours/sessions/{session_id}/participants/add",
        data={"member_id": member_id, "status": "ATTENDED"},
    )
    assert add.status_code in (302, 303)

    dashboard = await client.get("/")
    assert dashboard.status_code == 200
    # Dashboard tile: the backdated participation must not count.
    assert "New Sign-ups" in dashboard.text
    # Nav badge title attribute (rendered on every page, including this one).
    assert "1 new work-session sign-up(s) recently" in dashboard.text

    detail = await client.get(f"/work-hours/sessions/{session_id}")
    assert detail.status_code == 200
    # Exactly one "New" badge on the participant table -- the 100-day-old
    # backdated row must not be flagged.
    assert detail.text.count('badge bg-info text-dark ms-1">New</span>') == 1

    # The /work-hours/ overview list also flags the session itself with
    # its count of new sign-ups (issue #217 follow-up) -- distinct from
    # the two nav badges (group toggle + /work-hours/ link) that also
    # render on this same page.
    overview = await client.get(f"/work-hours/?year={date.today().year}")
    assert overview.status_code == 200
    assert overview.text.count("rounded-pill bg-info text-dark ms-1") == 3
    assert "1 new sign-up(s) for this session" in overview.text
