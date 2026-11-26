"""Issue #412: one request-context middleware, ClubSetting values cached
per process and dropped on every committed settings change."""
from sqlalchemy import select

from app import settings_cache
from app.database import AsyncSessionLocal
from app.models import ClubSetting
from tests.test_detail_page_navigation import web_login


async def _set_flag(key: str, value: str) -> None:
    async with AsyncSessionLocal() as db:
        row = await db.scalar(select(ClubSetting).where(ClubSetting.key == key))
        if row is None:
            db.add(ClubSetting(key=key, value=value, description="test"))
        else:
            row.value = value
        await db.commit()


async def test_a_settings_change_shows_on_the_very_next_request(client, admin_user):
    await web_login(client, "admin@example.com")
    await _set_flag("modul_inventory", "true")
    assert (await client.get("/inventory/")).status_code == 200
    assert settings_cache.get() is not None  # now cached

    await _set_flag("modul_inventory", "false")  # the commit drops the cache
    assert settings_cache.get() is None
    assert (await client.get("/inventory/")).status_code == 404


def test_values_loaded_before_a_change_are_not_cached():
    settings_cache.clear()
    started = settings_cache.generation()
    settings_cache.clear()  # someone committed a change meanwhile
    settings_cache.put({"stale": True}, started)
    assert settings_cache.get() is None


async def test_static_files_skip_the_context_and_404_in_plain_text(client):
    assert (await client.get("/static/favicon.ico")).status_code == 200
    missing = await client.get("/static/nope.css")
    assert missing.status_code == 404 and missing.text == "Not Found"
