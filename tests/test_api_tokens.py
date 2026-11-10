"""
Issue #306 / ADR 0126: personal API tokens -- long-lived, revocable,
stored only as a hash, acting with exactly their user's permissions.
"""
import re
from datetime import datetime, timedelta, timezone

import pytest
from httpx import ASGITransport
from sqlalchemy import select, update

from app.auth import hash_password
from app.database import AsyncSessionLocal
from app.main import app
from app.models import ApiToken, User, UserRole
from app.services import api_tokens
from tests.conftest import CsrfAwareClient, auth_header


@pytest.fixture
async def member_user():
    async with AsyncSessionLocal() as session:
        user = User(
            email="member@example.com",
            name="Plain Member",
            password_hash=hash_password("memberpass123"),
            role=UserRole.READONLY,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


def _new_client():
    return CsrfAwareClient(transport=ASGITransport(app=app), base_url="http://testserver")


async def _web_login(client, email, password):
    response = await client.post("/auth/login", data={"email": email, "password": password})
    assert response.status_code in (302, 303), response.text


def _shown_token(html: str) -> str:
    match = re.search(r'<code id="new_api_token"[^>]*>([^<]+)</code>', html)
    assert match, "new token not shown"
    return match.group(1).strip()


async def _create_own_token(client, name="Script", expires_in="365"):
    response = await client.post("/auth/api-tokens", data={"name": name, "expires_in": expires_in})
    # Post/Redirect/Get: the POST never renders the token itself.
    assert response.status_code == 303, response.text
    assert response.headers["location"] == "/auth/api-tokens"
    page = await client.get("/auth/api-tokens")
    assert page.status_code == 200
    assert page.headers.get("cache-control") == "no-store"
    return _shown_token(page.text)


async def test_reload_after_create_neither_mints_nor_reshows_token(client, admin_user):
    """Smoke-test bug on PR #309: the create POST answered with the page,
    so F5 re-submitted the form and minted a second token."""
    await _web_login(client, "admin@example.com", "testpasswort123")
    response = await client.post("/auth/api-tokens", data={"name": "Once", "expires_in": "30"})
    assert response.status_code == 303
    assert "pct_" not in response.text and "pct_" not in response.headers["location"]
    set_cookie = response.headers["set-cookie"].lower()
    assert "httponly" in set_cookie and "samesite=strict" in set_cookie and "path=/auth/api-tokens" in set_cookie

    raw = _shown_token((await client.get("/auth/api-tokens")).text)
    # Reloading the page the browser landed on is a GET: no new token,
    # and the raw value isn't shown a second time.
    again = await client.get("/auth/api-tokens")
    assert raw not in again.text and "new_api_token" not in again.text
    async with AsyncSessionLocal() as session:
        assert len((await session.execute(select(ApiToken))).scalars().all()) == 1


async def test_forged_new_token_cookie_shows_nothing(client, admin_user, member_user):
    """The one-time cookie is only displayed if it is one of the page's own
    tokens: someone else's token (or junk) shows nothing."""
    async with _new_client() as other:
        await _web_login(other, member_user.email, "memberpass123")
        others_raw = await _create_own_token(other)
    await _web_login(client, "admin@example.com", "testpasswort123")
    client.cookies.set(api_tokens.NEW_TOKEN_COOKIE, others_raw, path="/auth/api-tokens")
    page = await client.get("/auth/api-tokens")
    assert others_raw not in page.text and "new_api_token" not in page.text


async def test_token_created_once_stored_hashed_and_accepted_by_api(client, admin_user):
    await _web_login(client, "admin@example.com", "testpasswort123")
    raw = await _create_own_token(client, name="Knowledge base AI")
    assert raw.startswith("pct_") and len(raw) > 40

    async with AsyncSessionLocal() as session:
        token = (await session.execute(select(ApiToken))).scalar_one()
        assert token.token_hash == api_tokens.hash_token(raw)
        assert raw not in (token.token_hash, token.token_prefix)
        assert token.created_by_id == admin_user.id
        assert token.expires_at is not None and token.last_used_at is None

    # Shown once: the list afterwards only has the prefix.
    page = await client.get("/auth/api-tokens")
    assert raw not in page.text and token.token_prefix in page.text

    async with _new_client() as api:
        response = await api.get("/api/v1/members", headers=auth_header(raw))
        assert response.status_code == 200, response.text
        assert (await api.get("/api/v1/members", headers=auth_header(raw + "x"))).status_code == 401
        assert (await api.get("/api/v1/members", headers=auth_header("pct_unknown"))).status_code == 401

    async with AsyncSessionLocal() as session:
        token = (await session.execute(select(ApiToken))).scalar_one()
        assert token.last_used_at is not None


async def test_revoked_token_stops_working_immediately(client, admin_user):
    await _web_login(client, "admin@example.com", "testpasswort123")
    raw = await _create_own_token(client)
    async with _new_client() as api:
        assert (await api.get("/api/v1/members", headers=auth_header(raw))).status_code == 200

        async with AsyncSessionLocal() as session:
            token_id = (await session.execute(select(ApiToken.id))).scalar_one()
        response = await client.post(f"/auth/api-tokens/{token_id}/revoke")
        assert response.status_code == 302

        assert (await api.get("/api/v1/members", headers=auth_header(raw))).status_code == 401
    page = await client.get("/auth/api-tokens")
    assert "revoked" in page.text


async def test_token_cannot_do_more_than_its_user(client, admin_user, member_user):
    """A READONLY user's token reads what the user may read and gets the
    same 403 the user's JWT gets for a write."""
    await _web_login(client, "member@example.com", "memberpass123")
    raw = await _create_own_token(client)
    async with _new_client() as api:
        assert (await api.get("/api/v1/members", headers=auth_header(raw))).status_code == 200
        response = await api.post(
            "/api/v1/members", headers=auth_header(raw),
            json={"first_name": "Eve", "last_name": "Intruder"},
        )
        assert response.status_code == 403, response.text


async def test_expired_password_changed_and_deactivated_end_tokens(client, admin_user, member_user):
    await _web_login(client, "member@example.com", "memberpass123")
    expiring = await _create_own_token(client, name="expiring")
    survives_nothing = await _create_own_token(client, name="password", expires_in="never")

    async with _new_client() as api:
        async def status(raw):
            return (await api.get("/api/v1/members", headers=auth_header(raw))).status_code

        assert await status(expiring) == 200
        async with AsyncSessionLocal() as session:
            await session.execute(
                update(ApiToken).where(ApiToken.name == "expiring")
                .values(expires_at=datetime.now(timezone.utc) - timedelta(minutes=1))
            )
            await session.commit()
        assert await status(expiring) == 401

        assert await status(survives_nothing) == 200
        response = await client.post("/auth/change-password", data={
            "current_password": "memberpass123", "new_password": "newmemberpass456",
            "new_password_confirm": "newmemberpass456",
        })
        assert response.status_code == 200
        assert await status(survives_nothing) == 401
        page = await client.get("/auth/api-tokens")
        assert "ended" in page.text

        # A token made after the change works -- until the user is deactivated.
        fresh = await _create_own_token(client, name="fresh")
        assert await status(fresh) == 200
        async with AsyncSessionLocal() as session:
            await session.execute(update(User).where(User.id == member_user.id).values(is_active=False))
            await session.commit()
        assert await status(fresh) == 401


async def test_user_cannot_see_or_revoke_someone_elses_token(client, admin_user, member_user):
    await _web_login(client, "admin@example.com", "testpasswort123")
    raw = await _create_own_token(client, name="Admin secret integration")
    async with AsyncSessionLocal() as session:
        token_id = (await session.execute(select(ApiToken.id))).scalar_one()

    async with _new_client() as other:
        await _web_login(other, "member@example.com", "memberpass123")
        page = await other.get("/auth/api-tokens")
        assert "Admin secret integration" not in page.text
        assert (await other.post(f"/auth/api-tokens/{token_id}/revoke")).status_code == 404
        assert (await other.get("/admin/api-tokens")).status_code in (302, 303, 403)
        assert (await other.post(f"/admin/api-tokens/{token_id}/revoke")).status_code in (302, 303, 403)

    async with _new_client() as api:
        assert (await api.get("/api/v1/members", headers=auth_header(raw))).status_code == 200


async def test_admin_creates_token_for_integration_user_and_revokes_any(client, admin_user, board_user, member_user):
    await _web_login(client, "admin@example.com", "testpasswort123")
    page = await client.get("/admin/api-tokens")
    assert page.status_code == 200
    # Another full-access account isn't offered, and is refused if posted anyway.
    assert member_user.email in page.text and board_user.email not in page.text
    refused = await client.post("/admin/api-tokens", data={
        "user_id": board_user.id, "name": "impersonate", "expires_in": "30",
    })
    assert refused.status_code == 403
    assert "new_api_token" not in refused.text

    response = await client.post("/admin/api-tokens", data={
        "user_id": member_user.id, "name": "KI-Assistent", "expires_in": "90",
    })
    assert response.status_code == 303, response.text
    assert response.headers["location"] == "/admin/api-tokens"
    page = await client.get("/admin/api-tokens")
    raw = _shown_token(page.text)
    assert member_user.name in page.text
    assert raw not in (await client.get("/admin/api-tokens")).text
    async with AsyncSessionLocal() as session:
        token = (await session.execute(select(ApiToken))).scalar_one()
        assert token.user_id == member_user.id and token.created_by_id == admin_user.id

    async with _new_client() as api:
        me = await api.get("/api/v1/members", headers=auth_header(raw))
        assert me.status_code == 200
        assert (await client.post(f"/admin/api-tokens/{token.id}/revoke")).status_code == 302
        assert (await api.get("/api/v1/members", headers=auth_header(raw))).status_code == 401


async def test_token_form_validation(client, admin_user):
    await _web_login(client, "admin@example.com", "testpasswort123")
    assert (await client.post("/auth/api-tokens", data={"name": "  ", "expires_in": "30"})).status_code == 400
    assert (await client.post("/auth/api-tokens", data={"name": "x", "expires_in": "7"})).status_code == 400
    assert (await client.post("/auth/api-tokens", data={"name": "x" * 101, "expires_in": "30"})).status_code == 400
    async with AsyncSessionLocal() as session:
        assert (await session.execute(select(ApiToken))).first() is None
