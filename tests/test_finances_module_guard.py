"""
Issue #416: the finances routes live in sub-routers under one /finances
router that carries the module guard. Every route must still be locked
while the module is off (its default) -- a sub-router included
somewhere else, or given its own APIRouter with a prefix, would slip
past the guard.
"""
import re

from app.main import app
from tests.test_announcements import web_login

_PARAM = re.compile(r"\{[^}]+\}")
_DUMMY_ID = "00000000-0000-0000-0000-000000000000"


def _finances_routes():
    for path, ops in app.openapi()["paths"].items():
        if path.startswith("/finances"):
            for method in ops:
                yield method.upper(), _PARAM.sub(_DUMMY_ID, path)


async def test_every_finances_route_is_locked_while_the_module_is_off(client, admin_user):
    await web_login(client, "admin@example.com")
    routes = list(_finances_routes())
    assert len(routes) > 50  # the whole module, not a stray subset
    for method, path in routes:
        response = await client.request(method, path)
        assert response.status_code == 404, (method, path, response.status_code)
