"""
Tests for issue #217: informing about newly registered members via the
dashboard tile, the /work-hours/ nav badge, and an email to active
Admin/Board users (excluding whoever performed the creation). See
app/services/members.py (count_new_members, notify_new_member) and
docs/ADR for the design (stateless rolling window, no email on CSV
bulk import).
"""
from datetime import datetime, timedelta, timezone

from app.database import AsyncSessionLocal
from app.models import Member, User, UserRole
from app.auth import hash_password


async def web_login(client, email: str, password: str = "testpasswort123") -> None:
    response = await client.post("/auth/login", data={"email": email, "password": password})
    assert response.status_code in (302, 303)


async def test_dashboard_tile_and_nav_badge_count_new_members(client, admin_user):
    """A member created just now counts as "new"; one created well
    outside the rolling window (app/services/members.py's
    NEW_MEMBER_WINDOW_DAYS) does not."""
    await web_login(client, "admin@example.com")

    async with AsyncSessionLocal() as session:
        session.add(Member(
            first_name="Old", last_name="Timer",
            created_at=datetime.now(timezone.utc) - timedelta(days=100),
        ))
        await session.commit()

    create = await client.post(
        "/members/new",
        data={"first_name": "Brand", "last_name": "Newcomer"},
    )
    assert create.status_code in (302, 303)

    dashboard = await client.get("/")
    assert dashboard.status_code == 200
    # Exactly one "New" badge in the recent-members card -- the 100-day-old
    # member must not be counted.
    assert dashboard.text.count(">New</span>") == 1
    # The /work-hours/ nav badge (rendered on every page) carries the
    # same count in its title attribute.
    assert "1 new member(s) registered recently" in dashboard.text


async def test_new_member_email_sent_to_admin_board_excluding_actor(client, admin_user, board_user, monkeypatch):
    """Issue #217: active Admin/Board users get an email about a newly
    created member -- except the person who created it, and except
    inactive or non-Admin/Board accounts."""
    sent_to = []

    async def fake_send_email(recipient, subject, html_body, text_body=None, db=None):
        sent_to.append(recipient)
        return True

    monkeypatch.setattr("app.services.members.send_email", fake_send_email)

    async with AsyncSessionLocal() as session:
        session.add(User(
            email="inactive-board@example.com", name="Inactive Board",
            password_hash=hash_password("testpasswort123"),
            role=UserRole.BOARD, is_active=False,
        ))
        session.add(User(
            email="readonly@example.com", name="Readonly",
            password_hash=hash_password("testpasswort123"),
            role=UserRole.READONLY,
        ))
        await session.commit()

    # board_user performs the creation -- must not receive their own
    # notification; admin_user (a different active Admin/Board account)
    # must.
    await web_login(client, "vorstand@example.com")
    create = await client.post(
        "/members/new",
        data={"first_name": "Brand", "last_name": "Newcomer"},
    )
    assert create.status_code in (302, 303)

    assert sent_to == ["admin@example.com"]


async def test_new_member_email_sent_via_api(client, admin_user, board_user, monkeypatch):
    """The REST API creation path (app/routers/api_members.py) triggers
    the same notification as the HTML form, via the shared
    notify_new_member() helper."""
    from tests.conftest import login, auth_header

    sent_to = []

    async def fake_send_email(recipient, subject, html_body, text_body=None, db=None):
        sent_to.append(recipient)
        return True

    monkeypatch.setattr("app.services.members.send_email", fake_send_email)

    token = await login(client, "vorstand@example.com")
    create = await client.post(
        "/api/v1/members",
        json={"first_name": "API", "last_name": "Newcomer"},
        headers=auth_header(token),
    )
    assert create.status_code == 201

    assert sent_to == ["admin@example.com"]


async def test_csv_import_sends_no_email(client, admin_user, board_user, monkeypatch):
    """CSV bulk import (app/routers/members.py::members_import_csv) is
    a distinct, separate creation path from the single-member form/API
    and deliberately does NOT call notify_new_member() -- one email per
    imported member would spam Admin/Board on a large import."""
    sent_to = []

    async def fake_send_email(recipient, subject, html_body, text_body=None, db=None):
        sent_to.append(recipient)
        return True

    monkeypatch.setattr("app.services.members.send_email", fake_send_email)

    await web_login(client, "admin@example.com")
    csv_content = "Vorname;Nachname\nImported;One\nImported;Two\n"
    import_response = await client.post(
        "/members/import/csv",
        files={"datei": ("members.csv", csv_content.encode("utf-8"), "text/csv")},
        follow_redirects=False,
    )
    assert import_response.status_code in (302, 303)

    async with AsyncSessionLocal() as session:
        from sqlalchemy import select
        result = await session.execute(select(Member).where(Member.last_name.in_(["One", "Two"])))
        assert len(result.scalars().all()) == 2

    assert sent_to == []
