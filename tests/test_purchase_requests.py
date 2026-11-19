"""
Tests for the Purchase Requests module. Focus: the four-eyes principle
itself -- exactly the control this module exists for in the first
place. A regression here would be especially serious (a security hole,
not a mere comfort bug).
"""
from tests.conftest import login, auth_header


async def test_two_different_approvals_lead_to_approved(
    client, admin_user, board_user, second_board_user
):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)

    pr = (await client.post(
        "/api/v1/purchase-requests",
        json={"title": "Neuer Rasenmäher", "justification": "Alter ist kaputt"},
        headers=headers,
    )).json()
    assert pr["status"] == "OPEN"

    token_v1 = await login(client, "vorstand@example.com")
    r1 = await client.post(
        f"/api/v1/purchase-requests/{pr['id']}/approve", headers=auth_header(token_v1)
    )
    assert r1.status_code == 200
    assert r1.json()["status"] == "OPEN"  # only 1 of 2 so far

    token_v2 = await login(client, "vorstand2@example.com")
    r2 = await client.post(
        f"/api/v1/purchase-requests/{pr['id']}/approve", headers=auth_header(token_v2)
    )
    assert r2.status_code == 200
    assert r2.json()["status"] == "APPROVED"  # now 2 of 2


async def test_requester_may_not_approve_own_request(client, admin_user, board_user):
    """Core protection of the four-eyes principle: whoever requests may not also approve."""
    token = await login(client, "vorstand@example.com")
    headers = auth_header(token)

    pr = (await client.post(
        "/api/v1/purchase-requests",
        json={"title": "Selbst beantragt", "justification": "Test"},
        headers=headers,
    )).json()

    # The requester themselves tries to approve -- must be rejected
    response = await client.post(f"/api/v1/purchase-requests/{pr['id']}/approve", headers=headers)
    assert response.status_code == 403


async def test_same_person_cannot_approve_twice(
    client, admin_user, board_user, second_board_user
):
    """Two approvals must come from TWO DIFFERENT people."""
    token = await login(client, "admin@example.com")
    headers = auth_header(token)

    pr = (await client.post(
        "/api/v1/purchase-requests",
        json={"title": "Test", "justification": "Test"},
        headers=headers,
    )).json()

    token_v1 = await login(client, "vorstand@example.com")
    await client.post(f"/api/v1/purchase-requests/{pr['id']}/approve", headers=auth_header(token_v1))

    # The same person tries to approve a second time
    zweiter_versuch = await client.post(
        f"/api/v1/purchase-requests/{pr['id']}/approve", headers=auth_header(token_v1)
    )
    assert zweiter_versuch.status_code == 409

    # Status must still be OPEN, not incorrectly APPROVED
    aktuell = (await client.get(f"/api/v1/purchase-requests/{pr['id']}", headers=headers)).json()
    assert aktuell["status"] == "OPEN"


async def test_rejection_by_one_person_is_enough(client, admin_user, board_user):
    """Veto principle: a single rejection stops the request immediately."""
    token = await login(client, "admin@example.com")
    headers = auth_header(token)

    pr = (await client.post(
        "/api/v1/purchase-requests",
        json={"title": "Fragwürdige Anschaffung", "justification": "Test"},
        headers=headers,
    )).json()

    token_v1 = await login(client, "vorstand@example.com")
    r = await client.post(
        f"/api/v1/purchase-requests/{pr['id']}/reject",
        json={"rejection_reason": "Nicht notwendig"},
        headers=auth_header(token_v1),
    )
    assert r.status_code == 200
    assert r.json()["status"] == "REJECTED"
    assert r.json()["rejection_reason"] == "Nicht notwendig"


async def test_group_granted_full_access_can_approve_via_api(client, admin_user, board_user):
    """ADR 0070/0071: approve/reject used to require require_vorstand_api
    (role-only ADMIN/BOARD) -- a non-admin/board user granted full
    access via a Group (the exact mechanism ADR 0041 introduced so
    installations don't have to use the legacy roles) could already
    approve through the HTML UI (require_admin is Group-aware) but was
    blocked via the API. The reverse-direction version of ADR 0071's
    TREASURER bug: here the API was stricter than HTML, not looser."""
    from app.database import AsyncSessionLocal
    from app.models import User, UserRole, Group, GroupMembership
    from app.auth import hash_password

    async with AsyncSessionLocal() as db:
        user = User(
            email="full-access-via-group@example.com", name="Full Access Via Group",
            password_hash=hash_password("testpasswort123"), role=UserRole.READONLY,
        )
        db.add(user)
        await db.flush()

        group = Group(name="Honorary Board", grants_full_access=True)
        db.add(group)
        await db.flush()
        db.add(GroupMembership(user_id=user.id, group_id=group.id))
        await db.commit()

    token_admin = await login(client, "admin@example.com")
    pr = (await client.post(
        "/api/v1/purchase-requests",
        json={"title": "Test", "justification": "Test"},
        headers=auth_header(token_admin),
    )).json()

    token_group = await login(client, "full-access-via-group@example.com")
    response = await client.post(
        f"/api/v1/purchase-requests/{pr['id']}/approve", headers=auth_header(token_group)
    )
    assert response.status_code == 200, response.text


async def test_confirmation_email_includes_the_actual_confirmation_link(client, admin_user, monkeypatch):
    """ADR 0070: the API's confirmation email for an external (no-login)
    requester used to just say "please log in" -- with no actual link,
    even though a confirmation_token and the unauthenticated /confirm/
    {token} page already existed. Now shares the same email content
    (including the link) the HTML side already built correctly."""
    captured = {}

    async def fake_send_email(recipient, subject, html_body, text_body=None, db=None):
        captured["recipient"] = recipient
        captured["html"] = html_body
        return True

    monkeypatch.setattr("app.services.purchase_requests.send_email", fake_send_email)

    token = await login(client, "admin@example.com")
    pr = (await client.post(
        "/api/v1/purchase-requests",
        json={
            "title": "Neuer Rasenmäher", "justification": "Test",
            "requester_name": "Extern Person", "requester_email": "extern@example.com",
        },
        headers=auth_header(token),
    )).json()

    assert captured["recipient"] == "extern@example.com"
    assert "/purchase-requests/confirm/" in captured["html"]
    assert pr["id"]  # sanity: the request itself was created


async def test_regular_members_cannot_approve(client, admin_user):
    """Only board/admin may approve -- regular members may not."""
    from app.models import User, UserRole
    from app.auth import hash_password
    from app.database import AsyncSessionLocal

    async with AsyncSessionLocal() as session:
        einfaches_mitglied = User(
            email="mitglied@example.com", name="Normales Member",
            password_hash=hash_password("testpasswort123"), role=UserRole.READONLY,
        )
        session.add(einfaches_mitglied)
        await session.commit()

    token_admin = await login(client, "admin@example.com")
    pr = (await client.post(
        "/api/v1/purchase-requests",
        json={"title": "Test", "justification": "Test"},
        headers=auth_header(token_admin),
    )).json()

    token_mitglied = await login(client, "mitglied@example.com")
    response = await client.post(
        f"/api/v1/purchase-requests/{pr['id']}/approve", headers=auth_header(token_mitglied)
    )
    assert response.status_code == 403


async def test_on_behalf_without_email_keeps_the_name(client, admin_user, monkeypatch):
    """Issue #363: "on behalf of" with a name but no email was saved as the
    board member's own request, and the name was gone."""
    from sqlalchemy import select
    from app.database import AsyncSessionLocal
    from app.models import PurchaseRequest
    sent = []

    async def fake_send_email(*args, **kwargs):
        sent.append(args)
        return True

    monkeypatch.setattr("app.services.purchase_requests.send_email", fake_send_email)
    await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})
    response = await client.post("/purchase-requests/new", data={
        "title": "Heckenschere", "justification": "Alte ist kaputt",
        "for_other_person": "true", "requester_name": "Gerda Gärtnerin", "requester_email": "",
    })
    assert response.status_code == 302
    async with AsyncSessionLocal() as db:
        pr = (await db.execute(select(PurchaseRequest).where(PurchaseRequest.title == "Heckenschere"))).scalar_one()
    assert pr.requester_name == "Gerda Gärtnerin" and pr.requested_by_id is None and pr.requester_email is None
    assert pr.confirmation_token is None and sent == []  # no address, no confirmation mail
    assert "Gerda Gärtnerin" in (await client.get(response.headers["location"])).text


async def test_on_behalf_ticked_without_name_or_email_is_your_own_request(client, admin_user):
    from sqlalchemy import select
    from app.database import AsyncSessionLocal
    from app.models import PurchaseRequest
    await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})
    await client.post("/purchase-requests/new", data={
        "title": "Gießkanne", "justification": "x", "for_other_person": "true", "requester_name": " ", "requester_email": "",
    })
    async with AsyncSessionLocal() as db:
        pr = (await db.execute(select(PurchaseRequest).where(PurchaseRequest.title == "Gießkanne"))).scalar_one()
    assert pr.requested_by_id == pr.created_by_id and pr.requester_name is None
