"""
Issue #364: wording and i18n fixes found while writing the user docs --
hard-coded German shown whatever the club's language, swapped or wrong
labels, a button shown without the permission its route needs.
"""
import json
import re
from pathlib import Path

from app.auth import hash_password
from app.database import AsyncSessionLocal
from app.models import ClubSetting, Group, GroupMembership, GroupModulePermission, User, UserRole

GERMAN = re.compile(r"Sachversicherung|Pächter|Pflicht \(h\)|Zählpunkt|Hauptzähler|\bJa\b|\bNein\b|Funktionsbereich")


async def _login(client, email="admin@example.com"):
    response = await client.post("/auth/login", data={"email": email, "password": "testpasswort123"})
    assert response.status_code in (302, 303)


async def _module(name, on=True):
    async with AsyncSessionLocal() as db:
        db.add(ClubSetting(key=f"modul_{name}", value="true" if on else "false", description="test"))
        await db.commit()


def test_settings_help_names_the_real_fallback_language():
    for path in Path("app/translations").glob("*.json"):
        help_text = json.loads(path.read_text(encoding="utf-8"))["admin"]["settings"]["language_help"]
        assert "German" not in help_text and "deutsch" not in help_text.lower(), path.name
    assert "English" in json.loads(Path("app/translations/en.json").read_text())["admin"]["settings"]["language_help"]


async def test_switched_off_module_page_speaks_the_club_language(client, admin_user):
    await _module("inventory", on=False)
    await _login(client)
    response = await client.get("/inventory/")
    assert response.status_code == 404
    assert "This feature is switched off for this club." in response.text
    assert "Funktionsbereich" not in response.text


async def test_csv_exports_have_no_hard_coded_german(client, admin_user):
    await _module("insurance")
    await _login(client)
    for url in ("/insurance/evaluation/csv", "/water/evaluation/csv"):
        response = await client.get(url)
        assert response.status_code == 200, url
        header = response.text.splitlines()[0]
        assert not GERMAN.search(header), (url, header)
    assert "Parcel;Property insurance;Package;" in (await client.get("/insurance/evaluation/csv")).text
    assert (await client.get("/water/evaluation/csv")).text.startswith("Type;Metering point;Meter no.;")


def test_calendar_resources_headers_match_their_columns():
    en = json.loads(Path("app/translations/en.json").read_text())["calendar"]["resources"]
    assert (en["col_status"], en["col_loans"]) == ("Status", "Currently lent out")


def test_metering_import_field_names_are_translated():
    de = json.loads(Path("app/translations/de.json").read_text())["metering"]
    assert de["points_list"]["map_field_meter_number"] == "Zählernummer"
    assert de["readings_list"]["map_field_reading"] == "Zählerstand"
    for section in ("points_list", "readings_list"):
        assert "Type is required" not in json.loads(Path("app/translations/en.json").read_text())["metering"][section]["import_preview_help"]


async def test_inventory_category_delete_button_needs_delete_permission(client, admin_user):
    await _module("inventory")
    async with AsyncSessionLocal() as db:
        user = User(email="lager@example.com", name="Lager", password_hash=hash_password("testpasswort123"), role=UserRole.READONLY)
        group = Group(name="Inventory writers")
        db.add_all([user, group])
        await db.flush()
        db.add(GroupModulePermission(group_id=group.id, module="inventory", can_read=True, can_write=True))
        db.add(GroupMembership(user_id=user.id, group_id=group.id))
        await db.commit()
    await _login(client)
    await client.post("/inventory/categories/new", data={"name": "Werkzeug", "description": ""})
    assert "/delete" in (await client.get("/inventory/categories/")).text

    await _login(client, "lager@example.com")
    page = await client.get("/inventory/categories/")
    assert page.status_code == 200 and "Werkzeug" in page.text
    assert "/delete" not in page.text
