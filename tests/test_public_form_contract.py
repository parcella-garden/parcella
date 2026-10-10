"""
Tests for the one form contract shared by every way of submitting a
public form (ADR 0090): the token-authenticated JSON endpoints used by
server-side connectors behave like the plain-HTML-form endpoints --
same ALTCHA switch, same reason codes -- and a connector can forward its
visitor's IP so the rate limit counts visitors, not the connector's own
server.
"""
import pytest

from app.rate_limit import reset_all
from tests.conftest import login, auth_header
from tests.test_public_api import (
    _CONTACT_PAYLOAD, _FakeFreeScoutClient, _assign_member_to_parcel, _create_member,
    _create_parcel, _create_session, _enable_contact_module, _enable_module,
    _get_session_participations, _patch_freescout_client, _set_api_token,
)
from tests.test_public_forms import _allow_origins, _cheap_altcha, _require_altcha, _solved  # noqa: F401

TOKEN = {"X-Parcella-API-Token": "test-public-api-token"}


@pytest.fixture(autouse=True)
def _fresh_rate_limits():
    reset_all()
    yield
    reset_all()


async def _contact_setup(client, monkeypatch):
    headers = auth_header(await login(client, "admin@example.com"))
    await _enable_contact_module(client, headers)
    await _set_api_token(client, headers)
    fake_client = _FakeFreeScoutClient()
    _patch_freescout_client(monkeypatch, fake_client)
    return headers, fake_client


async def _post_contact(client, payload=None, headers=None):
    return await client.post(
        "/api/v1/public/contact", json=payload or _CONTACT_PAYLOAD, headers={**TOKEN, **(headers or {})},
    )


# ---------------------------------------------------------------------------
# Rate limit per visitor, not per connector server
# ---------------------------------------------------------------------------

async def test_forwarded_client_ip_gives_each_visitor_its_own_rate_limit(client, admin_user, monkeypatch):
    """Regression: a server-side connector (the WordPress plugin up to
    2.x) posts every visitor's submission from its own server, so all
    of a website's visitors shared one 10-per-hour contact budget."""
    await _contact_setup(client, monkeypatch)
    visitor_a = {"X-Parcella-Client-IP": "203.0.113.5"}

    for _ in range(10):
        assert (await _post_contact(client, headers=visitor_a)).status_code == 200
    assert (await _post_contact(client, headers=visitor_a)).status_code == 429

    visitor_b = {"X-Parcella-Client-IP": "2001:db8::7"}
    assert (await _post_contact(client, headers=visitor_b)).status_code == 200


async def test_malformed_forwarded_ip_falls_back_to_the_connection(client, admin_user, monkeypatch):
    await _contact_setup(client, monkeypatch)

    for _ in range(10):
        assert (await _post_contact(client, headers={"X-Parcella-Client-IP": "not-an-ip"})).status_code == 200
    # Same bucket as a submission without the header at all.
    assert (await _post_contact(client)).status_code == 429


# ---------------------------------------------------------------------------
# One ALTCHA switch for every path
# ---------------------------------------------------------------------------

async def test_json_contact_requires_altcha_while_switched_on(client, admin_user, monkeypatch, _cheap_altcha):
    headers, fake_client = await _contact_setup(client, monkeypatch)
    await _allow_origins(client, headers)  # the widget fetches its challenge from an allowed site
    await _require_altcha(client, headers)

    missing = (await _post_contact(client)).json()
    assert missing["accepted"] is False and missing["code"] == "captcha" and missing["reason"]
    assert fake_client.calls == []

    solution = await _solved(client)
    accepted = (await _post_contact(client, {**_CONTACT_PAYLOAD, "altcha": solution})).json()
    assert accepted == {"accepted": True, "reason": None, "code": None}
    assert len(fake_client.calls) == 1

    replayed = (await _post_contact(client, {**_CONTACT_PAYLOAD, "altcha": solution})).json()
    assert replayed["code"] == "captcha"


async def test_json_signup_requires_altcha_while_switched_on(client, admin_user, _cheap_altcha):
    headers = auth_header(await login(client, "admin@example.com"))
    await _enable_module(client, headers)
    await _set_api_token(client, headers)
    await _allow_origins(client, headers)
    member = await _create_member(client, headers)
    parcel = await _create_parcel(client, headers)
    await _assign_member_to_parcel(client, headers, member["id"], parcel["id"])
    session = await _create_session(client, headers)
    await _require_altcha(client, headers)

    payload = {"parcel_number": "G042", "session_ids": [session["id"]]}
    missing = await client.post("/api/v1/public/work-sessions/signup", json=payload, headers=TOKEN)
    assert missing.status_code == 200
    [result] = missing.json()["results"]
    assert result["accepted"] is False and result["code"] == "captcha"
    assert await _get_session_participations(client, headers, session["id"]) == []

    payload["altcha"] = await _solved(client)
    accepted = await client.post("/api/v1/public/work-sessions/signup", json=payload, headers=TOKEN)
    assert accepted.json()["results"][0]["accepted"] is True
    assert len(await _get_session_participations(client, headers, session["id"])) == 1


async def test_json_endpoints_ignore_altcha_while_switched_off(client, admin_user, monkeypatch):
    await _contact_setup(client, monkeypatch)
    response = (await _post_contact(client, {**_CONTACT_PAYLOAD, "altcha": "garbage"})).json()
    assert response["accepted"] is True


# ---------------------------------------------------------------------------
# Reason codes and localized reasons
# ---------------------------------------------------------------------------

async def test_signup_rejections_carry_a_code(client, admin_user):
    headers = auth_header(await login(client, "admin@example.com"))
    await _enable_module(client, headers)
    await _set_api_token(client, headers)
    await _create_parcel(client, headers)  # no residents
    session = await _create_session(client, headers)

    response = await client.post(
        "/api/v1/public/work-sessions/signup",
        json={"parcel_number": "G042", "session_ids": [session["id"]]}, headers=TOKEN,
    )
    [result] = response.json()["results"]
    assert result["accepted"] is False and result["code"] == "no_members_for_parcel"


async def test_contact_rejection_reason_follows_the_club_language(client, admin_user, monkeypatch):
    headers, _fake = await _contact_setup(client, monkeypatch)
    response = await client.put("/api/v1/club-settings/language", json={"value": "de"}, headers=headers)
    assert response.status_code == 200, response.text

    body = (await _post_contact(client, {**_CONTACT_PAYLOAD, "consent": False})).json()
    assert body["code"] == "consent_missing"
    assert body["reason"] == "Für das Absenden dieses Formulars ist die Einwilligung in die Datenverarbeitung erforderlich"
