"""
Tests for the calendar module: community calendar entries (merged with
work sessions), the public ICS feed and its JSON twin, token protection
on the private feeds, and the council-absence self-service permission
rule (anyone can log their own absence, nobody can delete someone
else's).

Uses the web UI's cookie-based session login (not the JWT API), since
the calendar module is web-UI-only -- httpx's AsyncClient keeps cookies
across requests within a test automatically.
"""
from datetime import date, timedelta

from tests.conftest import login, auth_header


async def web_login(client, email: str, password: str = "testpasswort123") -> None:
    """Logs in via the web UI's cookie-based session (not the JWT API) --
    the calendar module's routes are traditional web forms, so this is
    the login flow that actually applies to them."""
    response = await client.post("/auth/login", data={"email": email, "password": password})
    assert response.status_code in (302, 303)


async def test_community_calendar_and_public_ics(client, admin_user):
    await web_login(client, "admin@example.com")

    create = await client.post(
        "/calendar/community/new",
        data={
            "title": "Annual General Meeting",
            "event_type": "MEMBER_MEETING",
            "start_date": (date.today() + timedelta(days=30)).isoformat(),
        },
    )
    assert create.status_code in (302, 303)

    overview = await client.get("/calendar/community")
    assert overview.status_code == 200
    assert "Annual General Meeting" in overview.text

    # The ICS feed must be reachable with NO authentication at all --
    # it's meant to be embedded on the club's public website, which
    # can't send this app's session cookie.
    from httpx import AsyncClient, ASGITransport
    from app.main import app as fastapi_app

    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as anon_client:
        ics_response = await anon_client.get("/calendar/community.ics")
        assert ics_response.status_code == 200
        assert "Annual General Meeting" in ics_response.text
        assert "BEGIN:VCALENDAR" in ics_response.text

        # JSON twin of the same feed (ADR 0073) -- same data, same
        # unauthenticated posture, used by the WordPress connector's
        # [parcella_calendar] shortcode instead of an ICS subscription.
        json_response = await anon_client.get("/calendar/community.json")
        assert json_response.status_code == 200
        items = json_response.json()
        assert any(item["kind"] == "event" and item["title"] == "Annual General Meeting" for item in items)


async def test_community_calendar_excludes_special_sessions(client, admin_user):
    """Only STANDARD work sessions belong on the community calendar --
    SPECIAL (spontaneous/unplanned) ones shouldn't appear in the list
    view or the public ICS feed."""
    await web_login(client, "admin@example.com")

    from app.database import AsyncSessionLocal
    from app.models import WorkSession, SessionType

    async with AsyncSessionLocal() as session:
        session.add(WorkSession(
            title="Planned Leaf Raking", type=SessionType.STANDARD,
            date=date.today() + timedelta(days=10),
        ))
        session.add(WorkSession(
            title="Spontaneous Bench Painting", type=SessionType.SPECIAL,
            date=date.today() + timedelta(days=5),
        ))
        await session.commit()

    overview = await client.get("/calendar/community")
    assert overview.status_code == 200
    assert "Planned Leaf Raking" in overview.text
    assert "Spontaneous Bench Painting" not in overview.text

    from httpx import AsyncClient, ASGITransport
    from app.main import app as fastapi_app

    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as anon_client:
        ics_response = await anon_client.get("/calendar/community.ics")
        assert ics_response.status_code == 200
        assert "Planned Leaf Raking" in ics_response.text
        assert "Spontaneous Bench Painting" not in ics_response.text

        json_response = await anon_client.get("/calendar/community.json")
        assert json_response.status_code == 200
        titles = [item["title"] for item in json_response.json()]
        assert any("Planned Leaf Raking" in t for t in titles)
        assert not any("Spontaneous Bench Painting" in t for t in titles)


async def test_private_ics_feeds_require_correct_token(client, admin_user):
    await web_login(client, "admin@example.com")

    # No token, and a wrong token, must both be rejected.
    no_token = await client.get("/calendar/birthdays.ics")
    assert no_token.status_code == 403

    wrong_token = await client.get("/calendar/birthdays.ics?token=not-the-real-token")
    assert wrong_token.status_code == 403

    # The token is now shown inline on each calendar page's own ICS
    # subscribe dropdown (the hub page was removed -- see
    # docs/module-calendar.md -- and is now just a redirect).
    birthdays_page = await client.get("/calendar/birthdays")
    assert birthdays_page.status_code == 200
    import re
    match = re.search(r"birthdays\.ics\?token=([\w-]+)", birthdays_page.text)
    assert match, "Expected the birthday ICS URL with a token on the birthdays page itself"
    real_token = match.group(1)

    correct = await client.get(f"/calendar/birthdays.ics?token={real_token}")
    assert correct.status_code == 200
    assert "BEGIN:VCALENDAR" in correct.text


async def test_calendar_hub_redirects_to_community(client, admin_user):
    """The old /calendar/ overview page was removed in favor of putting
    each calendar's ICS link on its own page -- but the URL still
    redirects rather than 404ing, for anyone with an old bookmark."""
    await web_login(client, "admin@example.com")
    response = await client.get("/calendar/", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["location"] == "/calendar/community"


async def test_each_calendar_page_shows_its_own_ics_link(client, admin_user):
    """Every sub-calendar carries its own ICS subscribe link now,
    rather than all four being listed on a separate hub page."""
    await web_login(client, "admin@example.com")

    community = await client.get("/calendar/community")
    assert "calendar/community.ics" in community.text

    birthdays = await client.get("/calendar/birthdays")
    assert "calendar/birthdays.ics?token=" in birthdays.text

    presence = await client.get("/calendar/council-presence")
    assert "calendar/council-presence.ics?token=" in presence.text

    absence = await client.get("/calendar/council-absence")
    assert "calendar/council-absence.ics?token=" in absence.text


async def test_council_presence_multiple_members_one_slot(client, admin_user, board_user):
    """Issue #197: selecting more than one board member for the same
    slot must create one CouncilPresence row per person (the model is
    already "one row per person per slot", see docs/module-calendar.md)
    rather than requiring a separate form submission per person."""
    await web_login(client, "admin@example.com")

    slot_date = (date.today() + timedelta(days=5)).isoformat()
    create = await client.post(
        "/calendar/council-presence/new",
        data={
            "user_ids": [admin_user.id, board_user.id],
            "presence_date": slot_date,
            "time_from": "09:00",
            "time_until": "11:00",
            "note": "Joint office hours",
        },
    )
    assert create.status_code in (302, 303)

    overview = await client.get("/calendar/council-presence")
    assert overview.status_code == 200
    assert overview.text.count("Joint office hours") == 2
    assert "Test-Admin" in overview.text
    assert "Test-Vorstand" in overview.text

    # Submitting with no member selected at all must be rejected rather
    # than silently creating nothing.
    rejected = await client.post(
        "/calendar/council-presence/new",
        data={"presence_date": slot_date},
    )
    assert rejected.status_code == 400


async def test_council_absence_self_service_permissions(client, admin_user):
    await web_login(client, "admin@example.com")

    create = await client.post(
        "/calendar/council-absence/new",
        data={
            "start_date": (date.today() + timedelta(days=10)).isoformat(),
            "end_date": (date.today() + timedelta(days=15)).isoformat(),
            "note": "Vacation",
        },
    )
    assert create.status_code in (302, 303)

    overview = await client.get("/calendar/council-absence")
    assert "Vacation" in overview.text

    import re
    match = re.search(r"council-absence/([a-f0-9-]{36})/delete", overview.text)
    assert match
    entry_id = match.group(1)

    # A regular (non-admin/board) user must NOT be able to delete
    # someone else's entry -- admin/board CAN, for cleanup purposes,
    # which is why this needs a genuinely restricted role, not just a
    # different account.
    from app.database import AsyncSessionLocal
    from app.models import User, UserRole
    from app.auth import hash_password

    async with AsyncSessionLocal() as session:
        other_user = User(
            email="member@example.com",
            name="Test Member",
            password_hash=hash_password("testpasswort123"),
            role=UserRole.READONLY,
        )
        session.add(other_user)
        await session.commit()

    from httpx import ASGITransport
    from app.main import app as fastapi_app
    from tests.conftest import CsrfAwareClient

    # CsrfAwareClient, not a bare AsyncClient: this second user posts a
    # form, so it needs the same CSRF token any browser would carry
    # (app/csrf.py). The point of the assertion below is the 403 from the
    # permission check -- a 403 from a missing token would look identical
    # and prove nothing.
    transport = ASGITransport(app=fastapi_app)
    async with CsrfAwareClient(transport=transport, base_url="http://testserver") as other_client:
        await web_login(other_client, "member@example.com")
        forbidden = await other_client.post(f"/calendar/council-absence/{entry_id}/delete")
        assert forbidden.status_code == 403

    # The original user deleting their own entry must succeed.
    own_delete = await client.post(f"/calendar/council-absence/{entry_id}/delete")
    assert own_delete.status_code in (302, 303)
