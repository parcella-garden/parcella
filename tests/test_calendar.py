"""
Tests for the calendar module: community calendar entries (merged with
work sessions), the public ICS feed and its JSON twin, token protection
on the private feeds, and council-absence permissions (anyone can log
absence for themselves or another registered user, but deleting someone
else's entry still requires Admin/Board).

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


async def test_community_ics_keeps_event_times(client, admin_user):
    """Regression: up to 3.18.0 the ICS feed dropped an event's start and
    end time, so "Board office hours, 10:00-12:00" showed up as an
    all-day event in subscribers' calendar apps (the JSON twin had the
    times all along). Timed events carry the club's zone (region de_DE
    -> Europe/Berlin) plus its VTIMEZONE; events without a time stay
    all-day with the exclusive DTEND = day + 1."""
    await web_login(client, "admin@example.com")
    day = date.today() + timedelta(days=12)
    await client.post("/calendar/community/new", data={
        "title": "Board Office Hours", "event_type": "OTHER",
        "start_date": day.isoformat(), "start_time": "10:00", "end_time": "12:00",
    })
    await client.post("/calendar/community/new", data={
        "title": "Allotment Inspection", "event_type": "OTHER", "start_date": day.isoformat(),
    })

    from icalendar import Calendar

    ics = (await client.get("/calendar/community.ics")).text
    stamp = day.strftime("%Y%m%d")
    assert f"DTSTART;TZID=Europe/Berlin:{stamp}T100000" in ics
    assert f"DTEND;TZID=Europe/Berlin:{stamp}T120000" in ics
    assert "BEGIN:VTIMEZONE" in ics and "TZID:Europe/Berlin" in ics

    events = {str(e["summary"]): e for e in Calendar.from_ical(ics).walk("VEVENT")}
    all_day = events["Allotment Inspection"]
    assert all_day.decoded("dtstart") == day
    assert all_day.decoded("dtend") == day + timedelta(days=1)


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


async def test_council_presence_grouped_by_date(client, admin_user, board_user):
    """Issue #218: entries are grouped under one date heading per day
    rather than repeating the date on every row -- two people on the
    same slot (issue #197's multi-select) share one heading, a second
    date gets its own."""
    await web_login(client, "admin@example.com")

    first_date = (date.today() + timedelta(days=5)).isoformat()
    second_date = (date.today() + timedelta(days=6)).isoformat()

    await client.post(
        "/calendar/council-presence/new",
        data={
            "user_ids": [admin_user.id, board_user.id],
            "presence_date": first_date,
            "note": "Joint office hours",
        },
    )
    await client.post(
        "/calendar/council-presence/new",
        data={"user_ids": [admin_user.id], "presence_date": second_date, "note": "Solo shift"},
    )

    overview = await client.get("/calendar/council-presence")
    assert overview.status_code == 200
    # The first date appears exactly once as a group heading, even
    # though two people are listed under it.
    first_date_formatted = date.fromisoformat(first_date).strftime("%d.%m.%Y")
    second_date_formatted = date.fromisoformat(second_date).strftime("%d.%m.%Y")
    assert overview.text.count(first_date_formatted) == 1
    assert overview.text.count(second_date_formatted) == 1
    assert overview.text.count("Joint office hours") == 2


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


async def test_council_absence_for_another_user(client, admin_user, board_user):
    """Issue #216: logging absence isn't self-only anymore -- any
    logged-in user can also log it on behalf of another registered user
    via the user_ids checkbox list (same shape as council-presence's
    multi-select, see docs/module-calendar.md)."""
    await web_login(client, "admin@example.com")

    create = await client.post(
        "/calendar/council-absence/new",
        data={
            "user_ids": [board_user.id],
            "start_date": (date.today() + timedelta(days=20)).isoformat(),
            "end_date": (date.today() + timedelta(days=25)).isoformat(),
            "note": "Conference",
        },
    )
    assert create.status_code in (302, 303)

    overview = await client.get("/calendar/council-absence")
    assert overview.status_code == 200
    assert "Conference" in overview.text
    assert "Test-Vorstand" in overview.text

    # Selecting both self and another user in one submission creates one
    # row per person, same as council-presence.
    both = await client.post(
        "/calendar/council-absence/new",
        data={
            "user_ids": [admin_user.id, board_user.id],
            "start_date": (date.today() + timedelta(days=30)).isoformat(),
            "end_date": (date.today() + timedelta(days=31)).isoformat(),
            "note": "Joint trip",
        },
    )
    assert both.status_code in (302, 303)
    overview2 = await client.get("/calendar/council-absence")
    assert overview2.text.count("Joint trip") == 2


async def test_council_presence_and_work_session_ics_are_timed(client, admin_user, board_user):
    """Regression for issue #268: a council presence slot (and a work
    session) with a time used to be written as an all-day event, its
    time only in DESCRIPTION. Both must now carry the time in DTSTART/
    DTEND in the club's zone, with a VTIMEZONE; one without a time stays
    all-day."""
    import re

    from icalendar import Calendar

    from app.database import AsyncSessionLocal
    from app.models import SessionType, WorkSession

    await web_login(client, "admin@example.com")
    day = date.today() + timedelta(days=6)
    stamp = day.strftime("%Y%m%d")
    await client.post("/calendar/council-presence/new", data={
        "user_ids": [admin_user.id], "presence_date": day.isoformat(),
        "time_from": "09:00", "time_until": "11:30", "note": "Office hours",
    })
    await client.post("/calendar/council-presence/new", data={
        "user_ids": [board_user.id], "presence_date": day.isoformat(),
    })
    async with AsyncSessionLocal() as session:
        session.add(WorkSession(
            title="Hedge Trimming", type=SessionType.STANDARD, date=day,
            time_from="08:00", time_until="12:00",
        ))
        await session.commit()

    page = await client.get("/calendar/council-presence")
    token = re.search(r"council-presence\.ics\?token=([\w-]+)", page.text).group(1)
    ics = (await client.get(f"/calendar/council-presence.ics?token={token}")).text
    assert f"DTSTART;TZID=Europe/Berlin:{stamp}T090000" in ics
    assert f"DTEND;TZID=Europe/Berlin:{stamp}T113000" in ics
    assert "BEGIN:VTIMEZONE" in ics

    events = {str(e["summary"]): e for e in Calendar.from_ical(ics).walk("VEVENT")}
    timed = events["Test-Admin on-site"]
    assert str(timed["description"]) == "Office hours"  # no time text left in it
    all_day = events["Test-Vorstand on-site"]
    assert all_day.decoded("dtstart") == day
    assert all_day.decoded("dtend") == day + timedelta(days=1)

    community = (await client.get("/calendar/community.ics")).text
    assert f"DTSTART;TZID=Europe/Berlin:{stamp}T080000" in community
    assert f"DTEND;TZID=Europe/Berlin:{stamp}T120000" in community


# ---------------------------------------------------------------------------
# Custom calendars and the resource view (issue #314, ADR 0131)
# ---------------------------------------------------------------------------

async def _create_custom_calendar(client, name="Vereinsheim", **extra):
    data = {"name": name, "color": "#1e40af", **extra}
    assert (await client.post("/calendar/custom/new", data=data)).status_code == 303
    from sqlalchemy import select
    from app.database import AsyncSessionLocal
    from app.models import CustomCalendar
    async with AsyncSessionLocal() as session:
        return (await session.execute(select(CustomCalendar).where(CustomCalendar.name == name))).scalar_one()


async def _calendar_reader_client(module_perms=("calendar",)):
    """A logged-in non-board user whose group grants read on the given
    modules -- the case "board only" and the inventory check are about."""
    from app.database import AsyncSessionLocal
    from app.models import Group, GroupMembership, GroupModulePermission, User, UserRole
    from app.auth import hash_password
    async with AsyncSessionLocal() as session:
        user = User(email="reader@example.com", name="Reader", password_hash=hash_password("testpasswort123"),
                    role=UserRole.READONLY)
        group = Group(name="Calendar readers")
        session.add_all([user, group])
        await session.flush()
        session.add(GroupMembership(user_id=user.id, group_id=group.id))
        for module in module_perms:
            session.add(GroupModulePermission(group_id=group.id, module=module, can_read=True, can_write=False, can_delete=False))
        await session.commit()
    from httpx import ASGITransport
    from app.main import app as fastapi_app
    from tests.conftest import CsrfAwareClient
    other = CsrfAwareClient(transport=ASGITransport(app=fastapi_app), base_url="http://testserver")
    await web_login(other, "reader@example.com")
    return other


async def test_custom_calendar_events_never_reach_the_public_community_feed(client, admin_user):
    await web_login(client, "admin@example.com")
    calendar = await _create_custom_calendar(client)
    day = (date.today() + timedelta(days=5)).isoformat()
    created = await client.post(f"/calendar/custom/{calendar.id}/new", data={
        "title": "Kinderfest-Vorbereitung", "start_date": day, "start_time": "18:00", "end_time": "20:00",
    })
    assert created.status_code == 303

    page = await client.get(f"/calendar/custom/{calendar.id}")
    assert "Kinderfest-Vorbereitung" in page.text and "18:00-20:00" in page.text

    for url in ("/calendar/community", "/calendar/community.json", "/calendar/community.ics"):
        assert "Kinderfest" not in (await client.get(url)).text, url

    # The community delete route can't reach it either.
    import re
    event_id = re.search(rf"/calendar/custom/{calendar.id}/([a-f0-9-]{{36}})/delete", page.text).group(1)
    assert (await client.post(f"/calendar/community/{event_id}/delete")).status_code == 404


async def test_custom_calendar_ics_needs_the_token(client, admin_user):
    await web_login(client, "admin@example.com")
    calendar = await _create_custom_calendar(client)
    await client.post(f"/calendar/custom/{calendar.id}/new", data={
        "title": "Schlüsselübergabe", "start_date": (date.today() + timedelta(days=2)).isoformat(),
    })
    assert (await client.get(f"/calendar/custom/{calendar.id}/feed.ics")).status_code == 404
    assert (await client.get(f"/calendar/custom/{calendar.id}/feed.ics?token=wrong")).status_code == 404

    import re
    page = await client.get(f"/calendar/custom/{calendar.id}")
    token = re.search(r"feed\.ics\?token=([\w-]+)", page.text).group(1)
    feed = await client.get(f"/calendar/custom/{calendar.id}/feed.ics?token={token}")
    assert feed.status_code == 200 and "Schlüsselübergabe" in feed.text and "X-WR-CALNAME:Vereinsheim" in feed.text


async def test_board_only_calendar_is_invisible_to_other_users(client, admin_user):
    await web_login(client, "admin@example.com")
    secret = await _create_custom_calendar(client, name="Vorstandsklausur", full_access_only="true")
    open_cal = await _create_custom_calendar(client, name="Vereinsheim")

    reader = await _calendar_reader_client()
    try:
        index = await reader.get("/calendar/custom")
        assert index.status_code == 200
        assert "Vereinsheim" in index.text and "Vorstandsklausur" not in index.text
        assert "/calendar/custom/new" not in index.text  # no management form
        assert (await reader.get(f"/calendar/custom/{secret.id}")).status_code == 404
        assert (await reader.get(f"/calendar/custom/{open_cal.id}")).status_code == 200
        # Read-only: may not add entries or create calendars.
        assert (await reader.post(f"/calendar/custom/{open_cal.id}/new", data={
            "title": "x", "start_date": date.today().isoformat()})).status_code == 403
        assert (await reader.post("/calendar/custom/new", data={"name": "Mine"})).status_code == 403
    finally:
        await reader.aclose()


async def test_archived_calendar_keeps_entries_but_takes_no_new_ones(client, admin_user):
    await web_login(client, "admin@example.com")
    calendar = await _create_custom_calendar(client)
    await client.post(f"/calendar/custom/{calendar.id}/new", data={
        "title": "Altes Treffen", "start_date": (date.today() + timedelta(days=1)).isoformat(),
    })
    archived = await client.post(f"/calendar/custom/{calendar.id}/edit", data={
        "name": "Vereinsheim", "color": "javascript:alert(1)",  # not a colour -> default
    })
    assert archived.status_code == 303
    from app.database import AsyncSessionLocal
    from app.models import CustomCalendar
    async with AsyncSessionLocal() as session:
        stored = await session.get(CustomCalendar, calendar.id)
        assert stored.is_active is False and stored.color == "#2e7d32"

    assert "Altes Treffen" in (await client.get(f"/calendar/custom/{calendar.id}")).text
    refused = await client.post(f"/calendar/custom/{calendar.id}/new", data={
        "title": "Neu", "start_date": date.today().isoformat(),
    })
    assert refused.status_code == 409


async def test_resources_view_shows_current_loans_and_needs_inventory_read(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    member = (await client.post("/api/v1/members", json={"first_name": "Petra", "last_name": "Leiherin"}, headers=headers)).json()
    item = (await client.post("/api/v1/inventory/items", json={
        "name": "Vereinsanhänger", "is_borrowable": True, "quantity_total": 1}, headers=headers)).json()
    await client.post("/api/v1/inventory/items", json={"name": "Not lendable", "is_borrowable": False}, headers=headers)
    loan = await client.post(f"/api/v1/inventory/items/{item['id']}/loans", json={
        "member_id": member["id"], "quantity": 1, "borrowed_date": "2026-11-01"}, headers=headers)
    assert loan.status_code in (200, 201), loan.text

    await web_login(client, "admin@example.com")
    page = await client.get("/calendar/resources")
    assert page.status_code == 200
    assert "Vereinsanhänger" in page.text and "Petra Leiherin" in page.text and "01.11.2026" in page.text
    assert "Not lendable" not in page.text

    # Calendar read alone isn't enough: who borrowed what is inventory data.
    reader = await _calendar_reader_client()
    try:
        assert (await reader.get("/calendar/resources")).status_code == 403
        assert "/calendar/resources" not in (await reader.get("/calendar/custom")).text
    finally:
        await reader.aclose()
