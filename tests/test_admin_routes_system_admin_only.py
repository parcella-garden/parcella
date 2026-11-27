"""
Issue #416: the admin routes live in sub-routers (users, system,
settings, integrations, API tokens); each route checks
require_system_admin itself (ADR 0039). A board member -- full access to
every club module, but no system admin -- must not get through any of
them. 422 counts as refused too: the form never reached the route.
"""
import re

from app.main import app
from tests.test_announcements import web_login

_PARAM = re.compile(r"\{[^}]+\}")
_DUMMY_ID = "00000000-0000-0000-0000-000000000000"


async def test_no_admin_route_lets_a_board_member_through(client, board_user):
    await web_login(client, "vorstand@example.com")
    routes = [(m.upper(), _PARAM.sub(_DUMMY_ID, p))
              for p, ops in app.openapi()["paths"].items()
              if p.startswith("/admin/") and not p.startswith("/admin/groups") for m in ops]
    assert len(routes) > 40  # the whole admin router, not a stray subset
    for method, path in routes:
        if path == "/admin/":
            continue  # a plain redirect to /admin/users/, which is checked itself
        response = await client.request(method, path)
        assert response.status_code in (403, 422), (method, path, response.status_code)
