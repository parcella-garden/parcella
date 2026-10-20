"""
ADR 0102: a parcel handover is a turnover the vacancy check can't see
(the parcel is never empty), so the handover itself retires the old
tenants' cloud folder -- right away, or on a future handover date --
and optionally switches to a folder picked for the new tenants.
"""
from datetime import date, timedelta

from sqlalchemy import select, update

from tests.conftest import login, auth_header
from tests.test_applicant_parcel_handover import _setup, web_login
from app.database import AsyncSessionLocal
from app.models import ClubSetting, ParcelCloudFolder
from app.parcel_cloud_folders import apply_scheduled_folder_switches


async def _with_old_folder(ids: dict) -> str:
    async with AsyncSessionLocal() as db:
        db.add(ClubSetting(key="modul_cloud_storage", value="true"))
        folder = ParcelCloudFolder(parcel_id=ids["parcel"], relative_path="Parzellen/7 Alt")
        db.add(folder)
        await db.commit()
        return folder.id


async def _folders(parcel_id: str) -> dict[str, ParcelCloudFolder]:
    async with AsyncSessionLocal() as db:
        rows = (await db.execute(
            select(ParcelCloudFolder).where(ParcelCloudFolder.parcel_id == parcel_id)
        )).scalars().all()
        return {f.relative_path: f for f in rows}


async def test_handover_today_switches_folder(client, admin_user):
    ids = await _setup()
    await _with_old_folder(ids)
    await web_login(client, "admin@example.com")
    response = await client.post(
        f"/applicants/{ids['xaver']}/assign-parcel",
        data={"parcel_id": ids["parcel"], "handover_date": date.today().isoformat(),
              "new_folder_path": "/Parzellen/7 Neu/"},
    )
    assert response.status_code == 303

    folders = await _folders(ids["parcel"])
    assert folders["Parzellen/7 Alt"].is_active is False
    assert folders["Parzellen/7 Alt"].deactivated_at is not None
    assert folders["Parzellen/7 Neu"].is_active is True


async def test_handover_without_new_folder_still_retires_old_one(client, admin_user):
    """The bug this closes: the new tenants inherited the old folder."""
    ids = await _setup()
    await _with_old_folder(ids)
    await web_login(client, "admin@example.com")
    await client.post(f"/applicants/{ids['xaver']}/assign-parcel", data={"parcel_id": ids["parcel"]})

    folders = await _folders(ids["parcel"])
    assert [f.is_active for f in folders.values()] == [False]


async def test_future_handover_switches_folder_on_the_date(client, admin_user):
    ids = await _setup()
    await _with_old_folder(ids)
    token = await login(client, "admin@example.com")
    day = date.today() + timedelta(days=14)
    response = await client.post(
        f"/api/v1/applicants/{ids['xaver']}/assign-parcel",
        json={"parcel_id": ids["parcel"], "handover_date": day.isoformat(), "new_folder_path": "Parzellen/7 Neu"},
        headers=auth_header(token),
    )
    assert response.status_code == 200, response.text

    folders = await _folders(ids["parcel"])
    assert folders["Parzellen/7 Alt"].is_active and folders["Parzellen/7 Alt"].active_until == day
    assert not folders["Parzellen/7 Neu"].is_active and folders["Parzellen/7 Neu"].active_from == day

    async with AsyncSessionLocal() as db:
        assert await apply_scheduled_folder_switches(db) == 0  # not yet
        # The handover date arrives.
        await db.execute(update(ParcelCloudFolder).where(ParcelCloudFolder.parcel_id == ids["parcel"])
                         .values(active_until=None))
        await db.execute(update(ParcelCloudFolder).where(ParcelCloudFolder.relative_path == "Parzellen/7 Alt")
                         .values(active_until=date.today()))
        await db.execute(update(ParcelCloudFolder).where(ParcelCloudFolder.relative_path == "Parzellen/7 Neu")
                         .values(active_from=date.today()))
        await db.commit()
        assert await apply_scheduled_folder_switches(db) == 2

    folders = await _folders(ids["parcel"])
    assert folders["Parzellen/7 Alt"].is_active is False
    assert folders["Parzellen/7 Neu"].is_active is True


async def test_api_folder_needs_cloud_storage_module(client, admin_user):
    ids = await _setup()  # cloud_storage module left off
    token = await login(client, "admin@example.com")
    response = await client.post(
        f"/api/v1/applicants/{ids['xaver']}/assign-parcel",
        json={"parcel_id": ids["parcel"], "new_folder_path": "Parzellen/7 Neu"},
        headers=auth_header(token),
    )
    assert response.status_code == 403
