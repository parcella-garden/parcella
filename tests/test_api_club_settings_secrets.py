"""
GET /api/v1/club-settings must never hand out credentials or tokens:
any API account could read the list, and the plaintext ICS feed token
alone exposes every member's birthday (security audit 2026-10-19).
"""
from app.auth import hash_password
from app.database import AsyncSessionLocal
from app.models import ClubSetting, User, UserRole
from tests.conftest import auth_header, login

SECRETS = {
    "ics_secret_token": "ics-plaintext-token",
    "public_signup_api_token": "form-plaintext-token",
    "smtp_password": "gAAAAencrypted",
    "freescout_api_key": "gAAAAencrypted",
}


async def _readonly_token(client):
    async with AsyncSessionLocal() as db:
        db.add(User(email="readonly@example.com", name="Read Only",
                    password_hash=hash_password("testpasswort123"), role=UserRole.READONLY))
        db.add_all([ClubSetting(key=k, value=v, description="test") for k, v in SECRETS.items()])
        db.add(ClubSetting(key="club_name", value="KGV Test", description="test"))
        await db.commit()
    return auth_header(await login(client, "readonly@example.com"))


async def test_list_and_get_hide_secrets(client, admin_user):
    headers = await _readonly_token(client)

    listed = await client.get("/api/v1/club-settings", headers=headers)
    assert listed.status_code == 200
    keys = {entry["key"] for entry in listed.json()}
    assert "club_name" in keys
    assert not keys & set(SECRETS)
    for value in SECRETS.values():
        assert value not in listed.text

    for key in SECRETS:
        assert (await client.get(f"/api/v1/club-settings/{key}", headers=headers)).status_code == 404
    assert (await client.get("/api/v1/club-settings/club_name", headers=headers)).json()["value"] == "KGV Test"


async def test_admin_cannot_overwrite_secrets_through_the_api(client, admin_user):
    await _readonly_token(client)
    headers = auth_header(await login(client, "admin@example.com"))

    response = await client.put("/api/v1/club-settings/smtp_password", json={"value": "plain"}, headers=headers)
    assert response.status_code == 403
    assert (await client.put("/api/v1/club-settings/club_name", json={"value": "Neu"}, headers=headers)).status_code == 200
