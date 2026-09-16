"""
Tests for the FreeScout conversation bridge: matching hierarchy
(app/freescout_sync.py), idempotent upserts, task-board linking, and
reply-to-customer. External FreeScout calls are always faked (a plain
object exposing just the methods used) -- no real FreeScout instance is
reachable from this test environment. See tests/test_freescout_client.py
for the httpx.MockTransport-backed tests of the real client's HTTP layer.
"""
from datetime import date, datetime, timezone

from sqlalchemy import select

from tests.conftest import login, auth_header
from app.database import AsyncSessionLocal
from app.auth import hash_password
from app.models import (
    FreescoutConversationLink, Member, MemberEmail, MemberParcel, Parcel,
    Task, TaskList, TaskComment, User, UserRole,
)
from app.freescout_sync import sync_freescout_conversations


class _FakeFreeScoutClient:
    def __init__(self, conversations):
        self._conversations = conversations
        self.reply_calls = []

    async def list_conversations(self, mailbox_id=None, updated_since=None, page=1):
        return self._conversations

    async def create_thread(self, conversation_id, text, by_user_id=None):
        self.reply_calls.append((conversation_id, text, by_user_id))
        return {"id": 1}


def _conversation(conv_id, subject="Question", email="anna@example.com", name="Anna Bergmann",
                   customer_id=None, status="active"):
    return {
        "id": conv_id, "subject": subject, "mailboxId": 1, "status": status,
        "updatedAt": "2026-09-16T10:00:00Z",
        "customer": {"id": customer_id, "email": email, "firstName": name.split()[0], "lastName": name.split()[-1]},
    }


async def _make_member(email: str, first_name="Anna", last_name="Bergmann") -> Member:
    async with AsyncSessionLocal() as db:
        member = Member(first_name=first_name, last_name=last_name)
        db.add(member)
        await db.flush()
        db.add(MemberEmail(member_id=member.id, address=email, is_primary=True))
        await db.commit()
        await db.refresh(member)
        return member


# ---------------------------------------------------------------------------
# Matching hierarchy
# ---------------------------------------------------------------------------

async def test_sync_matches_by_stored_freescout_customer_id():
    member = await _make_member("anna@example.com")
    async with AsyncSessionLocal() as db:
        member = await db.get(Member, member.id)
        member.freescout_customer_id = 183
        await db.commit()

    client = _FakeFreeScoutClient([_conversation(1, email="anna-changed-her-email@example.com", customer_id=183)])
    async with AsyncSessionLocal() as db:
        count = await sync_freescout_conversations(db, client)
        assert count == 1

        result = await db.execute(select(FreescoutConversationLink))
        link = result.scalar_one()
        assert link.member_id == member.id


async def test_sync_exact_single_email_match_backfills_customer_id():
    member = await _make_member("sofia@example.com", "Sofia", "Keller")
    client = _FakeFreeScoutClient([_conversation(2, email="sofia@example.com", name="Sofia Keller", customer_id=555)])

    async with AsyncSessionLocal() as db:
        await sync_freescout_conversations(db, client)

    async with AsyncSessionLocal() as db:
        link = (await db.execute(select(FreescoutConversationLink))).scalar_one()
        assert link.member_id == member.id

        refreshed_member = await db.get(Member, member.id)
        assert refreshed_member.freescout_customer_id == 555


async def test_sync_ambiguous_email_leaves_unassociated():
    await _make_member("shared@example.com", "Klara", "Hoffmann")
    await _make_member("shared@example.com", "Peter", "Hoffmann")
    client = _FakeFreeScoutClient([_conversation(3, email="shared@example.com", customer_id=700)])

    async with AsyncSessionLocal() as db:
        await sync_freescout_conversations(db, client)

    async with AsyncSessionLocal() as db:
        link = (await db.execute(select(FreescoutConversationLink))).scalar_one()
        assert link.member_id is None


async def test_sync_no_match_leaves_unassociated():
    client = _FakeFreeScoutClient([_conversation(4, email="stranger@example.com", customer_id=1)])

    async with AsyncSessionLocal() as db:
        await sync_freescout_conversations(db, client)

    async with AsyncSessionLocal() as db:
        link = (await db.execute(select(FreescoutConversationLink))).scalar_one()
        assert link.member_id is None


async def test_sync_sets_parcel_when_member_has_exactly_one_current_parcel():
    member = await _make_member("tom@example.com", "Tom", "Fischer")
    async with AsyncSessionLocal() as db:
        parcel = Parcel(plot_number="G001")
        db.add(parcel)
        await db.flush()
        db.add(MemberParcel(member_id=member.id, parcel_id=parcel.id))
        await db.commit()
        parcel_id = parcel.id

    client = _FakeFreeScoutClient([_conversation(5, email="tom@example.com", name="Tom Fischer", customer_id=42)])
    async with AsyncSessionLocal() as db:
        await sync_freescout_conversations(db, client)

    async with AsyncSessionLocal() as db:
        link = (await db.execute(select(FreescoutConversationLink))).scalar_one()
        assert link.parcel_id == parcel_id


# ---------------------------------------------------------------------------
# Idempotency
# ---------------------------------------------------------------------------

async def test_sync_is_idempotent_on_repeated_conversation():
    client = _FakeFreeScoutClient([_conversation(6, email="repeat@example.com", customer_id=9)])

    async with AsyncSessionLocal() as db:
        await sync_freescout_conversations(db, client)
    async with AsyncSessionLocal() as db:
        await sync_freescout_conversations(db, client)

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(FreescoutConversationLink).where(FreescoutConversationLink.freescout_conversation_id == 6)
        )
        assert len(result.scalars().all()) == 1


async def test_sync_never_reguesses_once_staff_has_associated_a_conversation():
    member = await _make_member("real@example.com", "Real", "Member")
    other_member = await _make_member("real2@example.com", "Other", "Member")

    client = _FakeFreeScoutClient([_conversation(7, email="unmatched@example.com", customer_id=None)])
    async with AsyncSessionLocal() as db:
        await sync_freescout_conversations(db, client)

    # Staff manually associates the (unmatched-by-email) conversation with a member.
    async with AsyncSessionLocal() as db:
        link = (await db.execute(select(FreescoutConversationLink))).scalar_one()
        link.member_id = other_member.id
        await db.commit()

    # A member with exactly that email now exists -- a naive re-poll
    # WOULD auto-match it if the "already associated" guard didn't exist.
    await _make_member("unmatched@example.com", "Newly", "Registered")

    # A re-poll of the same conversation must not override the manual choice.
    client2 = _FakeFreeScoutClient([_conversation(7, email="unmatched@example.com", customer_id=None)])
    async with AsyncSessionLocal() as db:
        await sync_freescout_conversations(db, client2)

    async with AsyncSessionLocal() as db:
        link = (await db.execute(select(FreescoutConversationLink))).scalar_one()
        assert link.member_id == other_member.id


# ---------------------------------------------------------------------------
# Task board bridge + reply-to-customer (via the REST API)
# ---------------------------------------------------------------------------

async def _enable_module(client, headers):
    response = await client.put(
        "/api/v1/club-settings/modul_freescout_bridge", json={"value": "true"}, headers=headers,
    )
    assert response.status_code == 200, response.text


async def _make_link(freescout_conversation_id=100, subject="Leaking tap") -> str:
    async with AsyncSessionLocal() as db:
        link = FreescoutConversationLink(
            freescout_conversation_id=freescout_conversation_id, freescout_mailbox_id=1,
            subject=subject, customer_email="x@example.com", freescout_status="active",
            freescout_updated_at=datetime.now(timezone.utc),
        )
        db.add(link)
        await db.commit()
        await db.refresh(link)
        return link.id


async def test_add_to_task_board_creates_a_task_and_links_it(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _enable_module(client, headers)

    async with AsyncSessionLocal() as db:
        db.add(TaskList(name="To Do", position=0))
        await db.commit()

    link_id = await _make_link()

    response = await client.post(f"/api/v1/freescout/conversations/{link_id}/task", json={}, headers=headers)
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["task_id"] is not None

    async with AsyncSessionLocal() as db:
        task = await db.get(Task, body["task_id"])
        assert task is not None
        assert task.title == "Leaking tap"


async def test_reply_to_customer_calls_client_and_never_touches_task_comments(client, admin_user, monkeypatch):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _enable_module(client, headers)

    link_id = await _make_link(freescout_conversation_id=847)

    fake_client = _FakeFreeScoutClient([])
    import app.routers.api_freescout as api_freescout

    async def _fake_get_client(db):
        return fake_client

    monkeypatch.setattr(api_freescout, "get_freescout_client", _fake_get_client)

    response = await client.post(
        f"/api/v1/freescout/conversations/{link_id}/reply", json={"text": "We'll look into it."}, headers=headers,
    )
    assert response.status_code == 204, response.text
    assert fake_client.reply_calls == [(847, "We'll look into it.", admin_user.id)]

    async with AsyncSessionLocal() as db:
        assert (await db.execute(select(TaskComment))).scalars().all() == []


# ---------------------------------------------------------------------------
# Permission gating
# ---------------------------------------------------------------------------

async def test_conversations_endpoint_404_when_module_disabled(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    response = await client.get("/api/v1/freescout/conversations", headers=headers)
    assert response.status_code == 404


async def test_conversations_endpoint_403_without_freescout_bridge_permission(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _enable_module(client, headers)

    async with AsyncSessionLocal() as db:
        readonly_user = User(
            email="readonly@example.com", name="Readonly", role=UserRole.READONLY,
            password_hash=hash_password("testpasswort123"),
        )
        db.add(readonly_user)
        await db.commit()

    readonly_token = await login(client, "readonly@example.com")
    response = await client.get("/api/v1/freescout/conversations", headers=auth_header(readonly_token))
    assert response.status_code == 403
