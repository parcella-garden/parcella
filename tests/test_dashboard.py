"""
Issue #196: the dashboard's "quick access" card exposed admin-only
functionality to every logged-in user. "Manage users" was already
gated to `is_system_admin`, but the API docs (Swagger) link had no
gate at all, so a plain board member saw a shortcut to internals that
belong in the administration area. Both links were removed from the
quick access card; the API docs link was added to the admin sidebar's
"Administration" nav group instead (also `is_system_admin`-gated).
"""


async def web_login(client, email: str, password: str = "testpasswort123") -> None:
    response = await client.post("/auth/login", data={"email": email, "password": password})
    assert response.status_code in (302, 303)


async def test_dashboard_quick_access_hides_admin_links_from_board_member(client, board_user):
    await web_login(client, "vorstand@example.com")

    page = await client.get("/")
    assert page.status_code == 200
    assert "/admin/users/" not in page.text
    assert "/api/docs" not in page.text


async def test_admin_sidebar_has_api_docs_link_instead_of_dashboard_card(client, admin_user):
    await web_login(client, "admin@example.com")

    page = await client.get("/")
    assert page.status_code == 200
    assert 'href="/api/docs"' in page.text
    # only the sidebar's admin nav link remains -- the quick access card's copy was removed
    assert page.text.count('href="/api/docs"') == 1


async def test_dashboard_returns_its_db_connection(client, admin_user):
    """Regression: the dashboard (app/main.py, startseite -- it manages
    its own session instead of using get_db) queried the birthdays tile
    after its `async with` block had closed the session, which silently
    began a new transaction nobody ended. Every dashboard load leaked a
    connection "idle in transaction" holding a lock on members, and a
    later backup restore hung on DROP TABLE until it timed out (broke
    the v3.21.0 release run)."""
    from app.database import engine

    await web_login(client, "admin@example.com")
    page = await client.get("/")
    assert page.status_code == 200
    assert engine.pool.checkedout() == 0


async def test_tiles_only_show_for_users_who_may_open_them(client, admin_user):
    """Issue #361: the purchase requests, overdue tasks and sign-ups tiles
    only checked the module flag; "Show all" then led to a 403."""
    from app.auth import hash_password
    from app.database import AsyncSessionLocal
    from app.models import ClubSetting, User, UserRole
    async with AsyncSessionLocal() as db:
        for module in ("purchase_requests", "tasks", "work_hours"):
            db.add(ClubSetting(key=f"modul_{module}", value="true", description="test"))
        db.add(User(email="reader@example.com", name="Reader", password_hash=hash_password("testpasswort123"),
                    role=UserRole.READONLY))
        await db.commit()
    tiles = ("Open Purchase Requests", "Overdue Tasks", "New Sign-ups")

    await web_login(client, "reader@example.com")
    page = (await client.get("/")).text
    assert not [tile for tile in tiles if tile in page]
    assert "/tasks/?overdue=1" not in page

    await web_login(client, "admin@example.com")
    page = (await client.get("/")).text
    assert all(tile in page for tile in tiles)


async def test_vacant_count_ignores_ended_tenancies(client, admin_user):
    """Issue #360: tenancies are historized, so a parcel whose last
    tenancy has ended was never counted as vacant again."""
    import re
    from datetime import date, timedelta
    from app.database import AsyncSessionLocal
    from app.models import Member, MemberParcel, Parcel, ParcelStatus
    today = date.today()
    async with AsyncSessionLocal() as db:
        member = Member(first_name="Vera", last_name="Vacant")
        never, ended, current, notice, upcoming = parcels = [
            Parcel(plot_number=f"V{i}", area_sqm=100, status=ParcelStatus.ACTIVE) for i in range(5)
        ]
        db.add_all([member, *parcels])
        await db.flush()
        db.add_all([
            MemberParcel(member_id=member.id, parcel_id=ended.id, assigned_until=today - timedelta(days=30)),
            MemberParcel(member_id=member.id, parcel_id=current.id),
            MemberParcel(member_id=member.id, parcel_id=notice.id, assigned_until=today + timedelta(days=60)),
            MemberParcel(member_id=member.id, parcel_id=upcoming.id, assigned_from=today + timedelta(days=7)),
        ])
        await db.commit()

    await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})
    page = (await client.get("/")).text
    assert re.search(r">\s*2 vacant\s*<", page), "never let + tenancy ended = 2; notice and upcoming still count as let"
