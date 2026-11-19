"""
Issue #359: inviting a user (and resending an invitation) said
"Invitation sent" in production even when the mail server refused the
email -- the result of send_email was only looked at in development mode.
"""
import urllib.parse

from sqlalchemy import select

from app.config import Settings
from app.database import AsyncSessionLocal
from app.models import Invitation


async def _login(client):
    response = await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})
    assert response.status_code in (302, 303)


def _mail(monkeypatch, ok: bool, production: bool = True):
    """Call after logging in: production mode changes how the login
    cookie works over the test client's plain http."""
    sent = []

    async def fake_send_email(to, subject, html_body, text_body=None, db=None):
        sent.append(to)
        return ok

    monkeypatch.setattr("app.routers.admin.send_email", fake_send_email)
    if production:
        monkeypatch.setattr(Settings, "is_development", property(lambda self: False))
    return sent


async def test_failed_invitation_email_is_reported_not_called_sent(client, admin_user, monkeypatch):
    await _login(client)
    sent = _mail(monkeypatch, ok=False)
    response = await client.post("/admin/invite", data={"email": "neu@example.org"})
    location = urllib.parse.unquote(response.headers["location"])
    assert sent == ["neu@example.org"]
    assert "success=" not in location
    assert "error=The invitation for neu@example.org is saved, but the email could not be sent." in location
    async with AsyncSessionLocal() as db:  # the invitation itself is kept, so it can be resent
        assert (await db.execute(select(Invitation).where(Invitation.email == "neu@example.org"))).scalar_one()


async def test_failed_resend_is_reported_too(client, admin_user, monkeypatch):
    await _login(client)
    _mail(monkeypatch, ok=True)
    await client.post("/admin/invite", data={"email": "zwei@example.org"})
    async with AsyncSessionLocal() as db:
        invitation = (await db.execute(select(Invitation).where(Invitation.email == "zwei@example.org"))).scalar_one()

    _mail(monkeypatch, ok=False)
    response = await client.post(f"/admin/invitations/{invitation.id}/resend")
    assert "is saved, but the email could not be sent" in urllib.parse.unquote(response.headers["location"])


async def test_successful_invitation_still_says_sent(client, admin_user, monkeypatch):
    await _login(client)
    _mail(monkeypatch, ok=True)
    response = await client.post("/admin/invite", data={"email": "ok@example.org"})
    assert "success=Invitation%20sent" in response.headers["location"]


async def test_development_mode_still_shows_the_link(client, admin_user, monkeypatch):
    _mail(monkeypatch, ok=False, production=False)
    await _login(client)
    response = await client.post("/admin/invite", data={"email": "dev@example.org"})
    assert "/auth/invitation/" in urllib.parse.unquote(response.headers["location"])
