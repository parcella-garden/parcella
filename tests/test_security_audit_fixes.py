"""
Regression tests for the security audit of 2026-10-19 (see
docs/ADR/0099-security-audit-2026-10.md): one test per fixed finding,
so none of them can quietly come back. The club-settings secret leak
has its own file, tests/test_api_club_settings_secrets.py.
"""
import re
from pathlib import Path

from httpx import ASGITransport

from app.auth import verify_password
from app.database import AsyncSessionLocal
from app.main import app
from app.models import ClubSetting
from app.pdf_utils import data_uri_only_fetcher
from app.security_headers import content_disposition
from sqlalchemy import select
from tests.conftest import CsrfAwareClient
from tests.test_detail_page_navigation import web_login

TEMPLATES = Path("app/templates")


def test_member_search_results_are_not_built_as_html_strings():
    """Member names went into innerHTML unescaped on the parcel and the
    work-session page: a stored XSS against whoever opened them."""
    for name in ("parcels/detail.html", "work_hours/session_detail.html"):
        source = (TEMPLATES / name).read_text()
        assert not re.search(r"innerHTML\s*=\s*matches\.map", source), name
        assert "btn.textContent" in source, name


async def test_ics_token_can_be_regenerated(client, admin_user):
    await web_login(client, "admin@example.com")
    page = (await client.get("/calendar/birthdays")).text
    old_token = re.search(r"birthdays\.ics\?token=([\w-]+)", page).group(1)
    assert (await client.get(f"/calendar/birthdays.ics?token={old_token}")).status_code == 200

    response = await client.post("/admin/integrations/regenerate-ics-token")
    assert response.status_code == 302

    async with AsyncSessionLocal() as db:
        new_token = await db.scalar(select(ClubSetting.value).where(ClubSetting.key == "ics_secret_token"))
    assert new_token and new_token != old_token
    assert (await client.get(f"/calendar/birthdays.ics?token={old_token}")).status_code == 403
    assert (await client.get(f"/calendar/birthdays.ics?token={new_token}")).status_code == 200


async def test_password_change_ends_other_sessions(client, admin_user):
    async with CsrfAwareClient(transport=ASGITransport(app=app), base_url="http://testserver") as other_device:
        await web_login(other_device, "admin@example.com")
        assert (await other_device.get("/members/")).status_code == 200

        await web_login(client, "admin@example.com")
        response = await client.post("/auth/change-password", data={
            "current_password": "testpasswort123",
            "new_password": "ein-neues-passwort",
            "new_password_confirm": "ein-neues-passwort",
        })
        assert response.status_code == 200

        # The other device's cookie is dead; this browser got a fresh one.
        assert (await other_device.get("/members/", follow_redirects=False)).status_code == 303
        assert (await client.get("/members/", follow_redirects=False)).status_code == 200


def test_pdf_rendering_refuses_external_urls():
    fetcher = data_uri_only_fetcher()
    try:
        fetcher.fetch("http://169.254.169.254/latest/meta-data")
    except Exception as e:  # WeasyPrint raises and then skips the resource
        assert "disallowed protocol" in str(e)
    else:
        raise AssertionError("an http:// URL was fetched during PDF rendering")


def test_content_disposition_survives_hostile_and_non_latin_names():
    header = content_disposition('Łukasiewicz "x"\r\nSet-Cookie: a=1.pdf')
    assert "\r" not in header and "\n" not in header
    header.encode("latin-1")  # what the HTTP layer requires
    assert "filename*=UTF-8''%C5%81ukasiewicz" in header


def test_unknown_account_still_costs_a_password_check():
    assert verify_password("anything", None) is False
