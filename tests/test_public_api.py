"""
Tests for the public signup API (see app/routers/api_public.py).

The public form only ever collects a parcel number, never a member
picked from a list (the club's public website must not expose which
members live on which parcel) -- so these tests focus on the
resulting matching behaviour: a confidently-matched name registers
just that member, anything ambiguous registers every current resident
of the parcel, capacity is enforced against however many that turns
out to be, and duplicate participations are avoided across repeated
submissions.
"""
from datetime import date, timedelta

from tests.conftest import login, auth_header

_FUTURE_SESSION_DATE = (date.today() + timedelta(days=30)).isoformat()


async def _enable_module(client, headers):
    response = await client.put(
        "/api/v1/club-settings/modul_public_signup_api",
        json={"value": "true"},
        headers=headers,
    )
    assert response.status_code == 200, response.text


async def _enable_contact_module(client, headers):
    response = await client.put(
        "/api/v1/club-settings/modul_public_contact_api",
        json={"value": "true"},
        headers=headers,
    )
    assert response.status_code == 200, response.text


async def _set_api_token(client, headers) -> str:
    response = await client.put(
        "/api/v1/club-settings/public_signup_api_token",
        json={"value": "test-public-api-token"},
        headers=headers,
    )
    assert response.status_code == 200, response.text
    return "test-public-api-token"


async def _create_member(client, headers, first_name="Gerd", last_name="Mustergärtner"):
    response = await client.post(
        "/api/v1/members", json={"first_name": first_name, "last_name": last_name}, headers=headers
    )
    assert response.status_code == 201, response.text
    return response.json()


async def _create_parcel(client, headers, plot_number="G042"):
    response = await client.post(
        "/api/v1/parcels", json={"plot_number": plot_number}, headers=headers
    )
    assert response.status_code == 201, response.text
    return response.json()


async def _assign_member_to_parcel(client, headers, member_id, parcel_id):
    response = await client.post(
        f"/api/v1/parcels/{parcel_id}/assignments",
        json={"member_id": member_id, "parcel_id": parcel_id},
        headers=headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


async def _create_session(client, headers, title="Standardarbeitseinsatz", max_participants=None, date=None):
    payload = {"title": title, "type": "STANDARD", "date": date or _FUTURE_SESSION_DATE}
    if max_participants is not None:
        payload["max_participants"] = max_participants
    response = await client.post("/api/v1/work-hours/sessions", json=payload, headers=headers)
    assert response.status_code == 201, response.text
    return response.json()


async def _get_session_participations(client, headers, session_id):
    response = await client.get(f"/api/v1/work-hours/sessions/{session_id}/participations", headers=headers)
    assert response.status_code == 200, response.text
    return response.json()


async def test_public_endpoints_require_module_flag_enabled(client, admin_user):
    response = await client.get("/api/v1/public/work-sessions/upcoming")
    assert response.status_code == 404


async def test_upcoming_sessions_and_parcels_are_unauthenticated(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _enable_module(client, headers)
    await _create_parcel(client, headers)
    await _create_session(client, headers)

    sessions_response = await client.get("/api/v1/public/work-sessions/upcoming")
    assert sessions_response.status_code == 200
    assert len(sessions_response.json()) == 1

    parcels_response = await client.get("/api/v1/public/parcels")
    assert parcels_response.status_code == 200
    assert parcels_response.json()[0]["plot_number"] == "G042"
    # No internal UUID for an unauthenticated caller -- the reference
    # WordPress connector matches by plot_number alone, so handing out
    # the id is pure IDOR reconnaissance value with no legitimate use
    # (flagged by an external pentest).
    assert "id" not in parcels_response.json()[0]


async def test_signup_requires_valid_api_token(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _enable_module(client, headers)
    await _set_api_token(client, headers)
    parcel = await _create_parcel(client, headers)
    member = await _create_member(client, headers)
    await _assign_member_to_parcel(client, headers, member["id"], parcel["id"])
    session = await _create_session(client, headers)

    no_token_response = await client.post(
        "/api/v1/public/work-sessions/signup",
        json={"parcel_number": "G042", "session_ids": [session["id"]]},
    )
    assert no_token_response.status_code == 401

    wrong_token_response = await client.post(
        "/api/v1/public/work-sessions/signup",
        json={"parcel_number": "G042", "session_ids": [session["id"]]},
        headers={"X-Parcella-API-Token": "not-the-real-token"},
    )
    assert wrong_token_response.status_code == 401

    ok_response = await client.post(
        "/api/v1/public/work-sessions/signup",
        json={"parcel_number": "G042", "name": "Gerd Mustergärtner", "session_ids": [session["id"]]},
        headers={"X-Parcella-API-Token": "test-public-api-token"},
    )
    assert ok_response.status_code == 200, ok_response.text
    assert ok_response.json()["results"] == [{"session_id": session["id"], "accepted": True, "reason": None}]


async def test_signup_with_matching_name_registers_only_that_member(client, admin_user):
    """The core privacy-preserving path: a submitted name that matches
    exactly one current resident registers only that member, with
    status REGISTERED."""
    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _enable_module(client, headers)
    await _set_api_token(client, headers)
    parcel = await _create_parcel(client, headers)
    matched = await _create_member(client, headers, "Gerd", "Mustergärtner")
    other = await _create_member(client, headers, "Erika", "Musterfrau")
    await _assign_member_to_parcel(client, headers, matched["id"], parcel["id"])
    await _assign_member_to_parcel(client, headers, other["id"], parcel["id"])
    session = await _create_session(client, headers)

    response = await client.post(
        "/api/v1/public/work-sessions/signup",
        json={"parcel_number": "G042", "name": "Gerd Mustergärtner", "session_ids": [session["id"]]},
        headers={"X-Parcella-API-Token": "test-public-api-token"},
    )
    assert response.status_code == 200, response.text
    assert response.json()["results"][0]["accepted"] is True

    participations = await _get_session_participations(client, headers, session["id"])
    member_ids = {p["member_id"] for p in participations}
    assert member_ids == {matched["id"]}
    assert participations[0]["status"] == "REGISTERED"


async def test_signup_with_no_match_registers_all_current_residents(client, admin_user):
    """No name given (or one that doesn't match anybody) falls back to
    registering every current resident of the parcel -- overregistering
    is the deliberately safer default; the board can remove the wrong
    ones from the normal participants table."""
    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _enable_module(client, headers)
    await _set_api_token(client, headers)
    parcel = await _create_parcel(client, headers)
    resident_a = await _create_member(client, headers, "Gerd", "Mustergärtner")
    resident_b = await _create_member(client, headers, "Erika", "Musterfrau")
    await _assign_member_to_parcel(client, headers, resident_a["id"], parcel["id"])
    await _assign_member_to_parcel(client, headers, resident_b["id"], parcel["id"])
    session = await _create_session(client, headers)

    # No name at all.
    response = await client.post(
        "/api/v1/public/work-sessions/signup",
        json={"parcel_number": "G042", "session_ids": [session["id"]]},
        headers={"X-Parcella-API-Token": "test-public-api-token"},
    )
    assert response.status_code == 200
    assert response.json()["results"][0]["accepted"] is True

    participations = await _get_session_participations(client, headers, session["id"])
    member_ids = {p["member_id"] for p in participations}
    assert member_ids == {resident_a["id"], resident_b["id"]}


async def test_signup_with_unmatched_name_falls_back_to_all_residents(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _enable_module(client, headers)
    await _set_api_token(client, headers)
    parcel = await _create_parcel(client, headers)
    resident_a = await _create_member(client, headers, "Gerd", "Mustergärtner")
    resident_b = await _create_member(client, headers, "Erika", "Musterfrau")
    await _assign_member_to_parcel(client, headers, resident_a["id"], parcel["id"])
    await _assign_member_to_parcel(client, headers, resident_b["id"], parcel["id"])
    session = await _create_session(client, headers)

    response = await client.post(
        "/api/v1/public/work-sessions/signup",
        json={"parcel_number": "G042", "name": "Someone Else Entirely", "session_ids": [session["id"]]},
        headers={"X-Parcella-API-Token": "test-public-api-token"},
    )
    assert response.status_code == 200
    assert response.json()["results"][0]["accepted"] is True

    participations = await _get_session_participations(client, headers, session["id"])
    member_ids = {p["member_id"] for p in participations}
    assert member_ids == {resident_a["id"], resident_b["id"]}


async def test_signup_with_no_current_residents_is_rejected(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _enable_module(client, headers)
    await _set_api_token(client, headers)
    await _create_parcel(client, headers)  # no member assigned
    session = await _create_session(client, headers)

    response = await client.post(
        "/api/v1/public/work-sessions/signup",
        json={"parcel_number": "G042", "session_ids": [session["id"]]},
        headers={"X-Parcella-API-Token": "test-public-api-token"},
    )
    assert response.status_code == 200
    result = response.json()["results"][0]
    assert result["accepted"] is False
    assert result["reason"] == "No members are currently assigned to this parcel"


async def test_signup_respects_capacity_for_the_whole_group(client, admin_user):
    """A session with room for only 1 must reject a 2-resident parcel's
    signup entirely (not partially register one of them)."""
    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _enable_module(client, headers)
    await _set_api_token(client, headers)
    parcel = await _create_parcel(client, headers)
    resident_a = await _create_member(client, headers, "Gerd", "Mustergärtner")
    resident_b = await _create_member(client, headers, "Erika", "Musterfrau")
    await _assign_member_to_parcel(client, headers, resident_a["id"], parcel["id"])
    await _assign_member_to_parcel(client, headers, resident_b["id"], parcel["id"])
    session = await _create_session(client, headers, max_participants=1)

    response = await client.post(
        "/api/v1/public/work-sessions/signup",
        json={"parcel_number": "G042", "session_ids": [session["id"]]},
        headers={"X-Parcella-API-Token": "test-public-api-token"},
    )
    assert response.status_code == 200
    result = response.json()["results"][0]
    assert result["accepted"] is False
    assert result["reason"] == "Session is full"

    participations = await _get_session_participations(client, headers, session["id"])
    assert participations == []


async def test_signup_does_not_duplicate_existing_participation(client, admin_user):
    """Submitting twice for the same parcel/session shouldn't create two
    participations for the same member (would violate the DB's unique
    constraint and shouldn't happen anyway)."""
    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _enable_module(client, headers)
    await _set_api_token(client, headers)
    parcel = await _create_parcel(client, headers)
    member = await _create_member(client, headers, "Gerd", "Mustergärtner")
    await _assign_member_to_parcel(client, headers, member["id"], parcel["id"])
    session = await _create_session(client, headers)

    for _ in range(2):
        response = await client.post(
            "/api/v1/public/work-sessions/signup",
            json={"parcel_number": "G042", "name": "Gerd Mustergärtner", "session_ids": [session["id"]]},
            headers={"X-Parcella-API-Token": "test-public-api-token"},
        )
        assert response.status_code == 200
        assert response.json()["results"][0]["accepted"] is True

    participations = await _get_session_participations(client, headers, session["id"])
    assert len(participations) == 1


async def test_signup_accepts_blank_phone_and_email(client, admin_user):
    """Regression test: HTML forms send untouched optional fields as ""
    rather than omitting them, and EmailStr used to reject "" outright
    (422), breaking every submission that left email blank."""
    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _enable_module(client, headers)
    await _set_api_token(client, headers)
    parcel = await _create_parcel(client, headers)
    member = await _create_member(client, headers)
    await _assign_member_to_parcel(client, headers, member["id"], parcel["id"])
    session = await _create_session(client, headers)

    response = await client.post(
        "/api/v1/public/work-sessions/signup",
        json={
            "parcel_number": "G042", "name": "", "phone": "", "email": "",
            "remarks": "", "session_ids": [session["id"]],
        },
        headers={"X-Parcella-API-Token": "test-public-api-token"},
    )
    assert response.status_code == 200, response.text
    assert response.json()["results"][0]["accepted"] is True


async def test_signup_rejects_unknown_parcel_number(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _enable_module(client, headers)
    await _set_api_token(client, headers)
    session = await _create_session(client, headers)

    response = await client.post(
        "/api/v1/public/work-sessions/signup",
        json={"parcel_number": "DOES-NOT-EXIST", "session_ids": [session["id"]]},
        headers={"X-Parcella-API-Token": "test-public-api-token"},
    )
    assert response.status_code == 404


async def test_signup_honeypot_field_silently_ignored(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _enable_module(client, headers)
    await _set_api_token(client, headers)
    parcel = await _create_parcel(client, headers)
    member = await _create_member(client, headers)
    await _assign_member_to_parcel(client, headers, member["id"], parcel["id"])
    session = await _create_session(client, headers, max_participants=1)

    response = await client.post(
        "/api/v1/public/work-sessions/signup",
        json={"parcel_number": "G042", "session_ids": [session["id"]], "website": "http://spam.example"},
        headers={"X-Parcella-API-Token": "test-public-api-token"},
    )
    assert response.status_code == 200
    assert response.json()["results"][0]["accepted"] is True

    # Honeypot submissions must not actually create anything.
    participations = await _get_session_participations(client, headers, session["id"])
    assert participations == []


# ---------------------------------------------------------------------------
# Public contact-form API (POST /api/v1/public/contact) -- creates a
# Parcella ticket directly, replacing a plain-email contact form. Its own
# module flag (public_contact_api), independent of public_signup_api;
# see ADR 0074.
# ---------------------------------------------------------------------------

_CONTACT_PAYLOAD = {
    "name": "Gerd Mustergärtner",
    "email": "gerd@example.com",
    "message": "Could you please check the water tap near G042?",
    "consent": True,
}


async def test_contact_endpoint_requires_module_flag_enabled(client, admin_user):
    response = await client.post(
        "/api/v1/public/contact", json=_CONTACT_PAYLOAD,
        headers={"X-Parcella-API-Token": "irrelevant"},
    )
    assert response.status_code == 404


async def test_contact_requires_valid_api_token(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _enable_contact_module(client, headers)
    await _set_api_token(client, headers)

    no_token_response = await client.post("/api/v1/public/contact", json=_CONTACT_PAYLOAD)
    assert no_token_response.status_code == 401

    wrong_token_response = await client.post(
        "/api/v1/public/contact", json=_CONTACT_PAYLOAD,
        headers={"X-Parcella-API-Token": "not-the-real-token"},
    )
    assert wrong_token_response.status_code == 401


async def test_contact_creates_a_ticket(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _enable_contact_module(client, headers)
    await _set_api_token(client, headers)

    response = await client.post(
        "/api/v1/public/contact", json=_CONTACT_PAYLOAD,
        headers={"X-Parcella-API-Token": "test-public-api-token"},
    )
    assert response.status_code == 200, response.text
    assert response.json() == {"accepted": True, "reason": None}

    from app.database import AsyncSessionLocal
    from sqlalchemy import select
    from app.models import Ticket, TicketMessage

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Ticket).where(Ticket.sender_email == "gerd@example.com"))
        ticket = result.scalar_one()
        assert ticket.sender_name == "Gerd Mustergärtner"
        assert ticket.spam_score is not None

        message_result = await db.execute(select(TicketMessage).where(TicketMessage.ticket_id == ticket.id))
        message = message_result.scalar_one()
        assert "Could you please check the water tap near G042?" in message.content
        assert "consent" in message.content.lower()


async def test_contact_without_consent_is_rejected(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _enable_contact_module(client, headers)
    await _set_api_token(client, headers)

    payload = {**_CONTACT_PAYLOAD, "consent": False}
    response = await client.post(
        "/api/v1/public/contact", json=payload,
        headers={"X-Parcella-API-Token": "test-public-api-token"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["accepted"] is False
    assert body["reason"]

    from app.database import AsyncSessionLocal
    from sqlalchemy import select
    from app.models import Ticket

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Ticket).where(Ticket.sender_email == "gerd@example.com"))
        assert result.scalar_one_or_none() is None


async def test_contact_honeypot_field_silently_ignored(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _enable_contact_module(client, headers)
    await _set_api_token(client, headers)

    payload = {**_CONTACT_PAYLOAD, "website": "http://spam.example"}
    response = await client.post(
        "/api/v1/public/contact", json=payload,
        headers={"X-Parcella-API-Token": "test-public-api-token"},
    )
    assert response.status_code == 200
    assert response.json() == {"accepted": True, "reason": None}

    from app.database import AsyncSessionLocal
    from sqlalchemy import select
    from app.models import Ticket

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Ticket).where(Ticket.sender_email == "gerd@example.com"))
        assert result.scalar_one_or_none() is None
