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
