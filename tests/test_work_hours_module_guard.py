"""
Issue #416: the work-hours routes live in sub-routers under one
/work-hours router that carries the module guard. Every route must be
locked while the module is switched off -- a sub-router included
somewhere else, or given its own prefix, would slip past the guard.
"""
import re

from app.database import AsyncSessionLocal
from app.main import app
from app.models import ClubSetting
from tests.test_announcements import web_login

_PARAM = re.compile(r"\{[^}]+\}")
_DUMMY_ID = "00000000-0000-0000-0000-000000000000"


async def test_every_work_hours_route_is_locked_while_the_module_is_off(client, admin_user):
    async with AsyncSessionLocal() as session:
        session.add(ClubSetting(key="modul_work_hours", value="false", description="test"))
        await session.commit()
    await web_login(client, "admin@example.com")
    routes = [(m.upper(), _PARAM.sub(_DUMMY_ID, p))
              for p, ops in app.openapi()["paths"].items() if p.startswith("/work-hours") for m in ops]
    assert len(routes) > 40  # the whole module, not a stray subset
    for method, path in routes:
        response = await client.request(method, path)
        assert response.status_code == 404, (method, path, response.status_code)
