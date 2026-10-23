"""
Issue #244 / ADR 0109: an admin resets another user's password.
Parcella generates a temporary password, shows it once, ends the user's
open sessions, and the user must change it at the next login (the
must_change_password flow, app/main.py's password_change_middleware).
"""
import re

import pytest
from httpx import ASGITransport
from sqlalchemy import select

from app.auth import hash_password
from app.database import AsyncSessionLocal
from app.main import app
from app.models import User, UserRole
from tests.conftest import CsrfAwareClient


@pytest.fixture
async def member_user():
    async with AsyncSessionLocal() as session:
        user = User(
            email="member@example.com",
            name="Forgetful Member",
            password_hash=hash_password("oldpassword123"),
            role=UserRole.READONLY,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


def _new_client():
    return CsrfAwareClient(transport=ASGITransport(app=app), base_url="http://testserver")


async def _web_login(client, email, password):
    return await client.post("/auth/login", data={"email": email, "password": password})


async def _reset(admin_client, user_id):
    return await admin_client.post(f"/admin/users/{user_id}/reset-password")


def _temp_password(html: str) -> str:
    match = re.search(r'<code id="temp_password"[^>]*>([^<]+)</code>', html)
    assert match, "temporary password not shown"
    return match.group(1).strip()


async def test_reset_shows_temp_password_and_forces_change(client, admin_user, member_user):
    assert (await _web_login(client, "admin@example.com", "testpasswort123")).status_code in (302, 303)

    async with _new_client() as member:
        assert (await _web_login(member, "member@example.com", "oldpassword123")).status_code in (302, 303)
        assert (await member.get("/")).status_code == 200

        response = await _reset(client, member_user.id)
        assert response.status_code == 200
        assert response.headers["cache-control"] == "no-store"
        temp = _temp_password(response.text)
        assert re.fullmatch(r"[A-Za-z0-9]{4}(-[A-Za-z0-9]{4}){3}", temp)

        # The open session ended with the reset.
        assert (await member.get("/", follow_redirects=False)).status_code in (302, 303, 401)

    async with _new_client() as member:
        assert (await _web_login(member, "member@example.com", "oldpassword123")).status_code == 401
        assert (await _web_login(member, "member@example.com", temp)).status_code in (302, 303)

        forced = await member.get("/", follow_redirects=False)
        assert forced.status_code == 302
        assert forced.headers["location"] == "/auth/change-password"

        changed = await member.post("/auth/change-password", data={
            "current_password": temp,
            "new_password": "brandnew12345",
            "new_password_confirm": "brandnew12345",
        })
        assert changed.status_code == 200
        assert (await member.get("/", follow_redirects=False)).status_code == 200

    async with AsyncSessionLocal() as session:
        user = (await session.execute(select(User).where(User.id == member_user.id))).scalar_one()
        assert user.must_change_password is False


async def test_api_token_refused_until_password_changed(client, admin_user, member_user):
    await _web_login(client, "admin@example.com", "testpasswort123")
    temp = _temp_password((await _reset(client, member_user.id)).text)

    response = await client.post("/api/v1/auth/login", json={"email": "member@example.com", "password": temp})
    assert response.status_code != 200


async def test_admin_cannot_reset_own_password_here(client, admin_user):
    await _web_login(client, "admin@example.com", "testpasswort123")

    response = await _reset(client, admin_user.id)
    assert response.status_code == 302
    assert "error=" in response.headers["location"]

    async with AsyncSessionLocal() as session:
        user = (await session.execute(select(User).where(User.id == admin_user.id))).scalar_one()
        assert user.must_change_password is False


async def test_non_admin_cannot_reset_passwords(client, admin_user, member_user):
    await _web_login(client, "member@example.com", "oldpassword123")

    response = await _reset(client, admin_user.id)
    assert response.status_code in (302, 303, 403)
    assert "temp_password" not in response.text

    async with AsyncSessionLocal() as session:
        user = (await session.execute(select(User).where(User.id == admin_user.id))).scalar_one()
        assert user.must_change_password is False
    async with _new_client() as fresh:
        assert (await _web_login(fresh, "admin@example.com", "testpasswort123")).status_code in (302, 303)
