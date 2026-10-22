"""
Tests for the support module with FreeScout as the active helpdesk:
matching hierarchy (app/helpdesk/sync.py), idempotent upserts, deletion
reconciliation, task-board linking, and reply-to-customer. External
calls are always faked (a HelpdeskProvider exposing just what's used) --
no real helpdesk is reachable from this test environment. See
tests/test_freescout_client.py for the HTTP layer and
tests/test_helpdesk_providers.py for the other helpdesks.
"""
from datetime import date, datetime, timezone

from sqlalchemy import select

from tests.conftest import login, auth_header
from app.database import AsyncSessionLocal
from app.auth import hash_password
from app.helpdesk.base import ALL_CAPABILITIES, HelpdeskProvider
from app.helpdesk.freescout import FreeScoutProvider
from app.helpdesk.sync import sync_helpdesk_conversations
from app.models import (
    ClubSetting, HelpdeskConversationLink, HelpdeskCustomerId, Member, MemberEmail, MemberParcel, Parcel,
    Task, TaskList, TaskComment, User, UserRole,
)


class _FakeFreeScoutClient(HelpdeskProvider):
    type = "freescout"
    label = "FreeScout"
    capabilities = ALL_CAPABILITIES

    def __init__(self, conversations, states=None):
        self._conversations = conversations
        # {conversation id: status_or_None} -- None means "gone
        # (deleted)"; a ROW not present in this dict is treated as still
        # existing as "active".
        self._states = states or {}
        self.reply_calls = []

    async def list_conversations(self, updated_since):
        return [FreeScoutProvider._to_conversation(raw) for raw in self._conversations]

    async def get_status(self, external_id):
        return self._states.get(int(external_id), "active")

    async def reply(self, external_id, text):
        self.reply_calls.append((external_id, text))


async def sync_freescout_conversations(db, client):
    return await sync_helpdesk_conversations(db, client)


async def _choose_freescout():
    """The lists only show the active helpdesk's conversations."""
    async with AsyncSessionLocal() as db:
        db.add(ClubSetting(key="helpdesk_provider", value="freescout"))
        await db.commit()


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
        db.add(HelpdeskCustomerId(member_id=member.id, provider="freescout", customer_id="183"))
        await db.commit()

    client = _FakeFreeScoutClient([_conversation(1, email="anna-changed-her-email@example.com", customer_id=183)])
    async with AsyncSessionLocal() as db:
        count = await sync_freescout_conversations(db, client)
        assert count == 1

        result = await db.execute(select(HelpdeskConversationLink))
        link = result.scalar_one()
        assert link.member_id == member.id


async def test_sync_exact_single_email_match_backfills_customer_id():
    member = await _make_member("sofia@example.com", "Sofia", "Keller")
    client = _FakeFreeScoutClient([_conversation(2, email="sofia@example.com", name="Sofia Keller", customer_id=555)])

    async with AsyncSessionLocal() as db:
        await sync_freescout_conversations(db, client)

    async with AsyncSessionLocal() as db:
        link = (await db.execute(select(HelpdeskConversationLink))).scalar_one()
        assert link.member_id == member.id

        stored = (await db.execute(select(HelpdeskCustomerId))).scalar_one()
        assert (stored.member_id, stored.provider, stored.customer_id) == (member.id, "freescout", "555")


async def test_sync_ambiguous_email_leaves_unassociated():
    await _make_member("shared@example.com", "Klara", "Hoffmann")
    await _make_member("shared@example.com", "Peter", "Hoffmann")
    client = _FakeFreeScoutClient([_conversation(3, email="shared@example.com", customer_id=700)])

    async with AsyncSessionLocal() as db:
        await sync_freescout_conversations(db, client)

    async with AsyncSessionLocal() as db:
        link = (await db.execute(select(HelpdeskConversationLink))).scalar_one()
        assert link.member_id is None


async def test_sync_no_match_leaves_unassociated():
    client = _FakeFreeScoutClient([_conversation(4, email="stranger@example.com", customer_id=1)])

    async with AsyncSessionLocal() as db:
        await sync_freescout_conversations(db, client)

    async with AsyncSessionLocal() as db:
        link = (await db.execute(select(HelpdeskConversationLink))).scalar_one()
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
        link = (await db.execute(select(HelpdeskConversationLink))).scalar_one()
        assert link.parcel_id == parcel_id


# ---------------------------------------------------------------------------
# Deletion reconciliation
# ---------------------------------------------------------------------------

async def test_reconciliation_marks_a_conversation_deleted_on_404():
    """FreeScout represents deletion via a separate `state` field (or a
    404 on refetch), never via `status` -- the incremental updatedSince
    sync alone can never observe it, since a deleted conversation simply
    stops appearing rather than being reported as changed. Regression
    test for a real bug: a conversation deleted directly in FreeScout
    stayed stuck at its last-known status ("active") in Parcella forever."""
    client = _FakeFreeScoutClient([_conversation(8001, email="gone@example.com", customer_id=1)])
    async with AsyncSessionLocal() as db:
        await sync_freescout_conversations(db, client)

    async with AsyncSessionLocal() as db:
        link = (await db.execute(select(HelpdeskConversationLink).where(
            HelpdeskConversationLink.external_id == "8001"
        ))).scalar_one()
        assert link.status == "active"

    # Conversation #8001 is now gone in FreeScout -- the next poll's
    # reconciliation pass must catch it even though list_conversations()
    # no longer returns it at all.
    client2 = _FakeFreeScoutClient([], states={8001: None})
    async with AsyncSessionLocal() as db:
        await sync_freescout_conversations(db, client2)

    async with AsyncSessionLocal() as db:
        link = (await db.execute(select(HelpdeskConversationLink).where(
            HelpdeskConversationLink.external_id == "8001"
        ))).scalar_one()
        assert link.status == "deleted"


async def test_reconciliation_does_not_recheck_already_hidden_rows():
    """Once a row is closed/deleted, reconciliation stops spending an
    API call on it every cycle -- it's not actionable anymore."""
    client = _FakeFreeScoutClient([_conversation(8002, email="x@example.com", status="closed")])
    async with AsyncSessionLocal() as db:
        await sync_freescout_conversations(db, client)

    checked_ids = []

    class _TrackingClient(_FakeFreeScoutClient):
        async def get_status(self, external_id):
            checked_ids.append(external_id)
            return await super().get_status(external_id)

    client2 = _TrackingClient([])
    async with AsyncSessionLocal() as db:
        await sync_freescout_conversations(db, client2)

    assert "8002" not in checked_ids


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
            select(HelpdeskConversationLink).where(HelpdeskConversationLink.external_id == "6")
        )
        assert len(result.scalars().all()) == 1


async def test_sync_persists_pending_conversations():
    """The sync poller must fetch pending conversations, not just active
    ones -- FreeScout's own list endpoint would otherwise silently drop
    them (issue #222). This exercises app/helpdesk/sync.py's use of
    the provider's list_conversations(), not the provider's HTTP layer
    itself (see tests/test_freescout_client.py for that)."""
    client = _FakeFreeScoutClient(
        [_conversation(8, email="pending@example.com", customer_id=None, status="pending")],
        states={8: "pending"},
    )

    async with AsyncSessionLocal() as db:
        count = await sync_freescout_conversations(db, client)
        assert count == 1

        link = (await db.execute(
            select(HelpdeskConversationLink).where(HelpdeskConversationLink.external_id == "8")
        )).scalar_one()
        assert link.status == "pending"


async def test_sync_never_reguesses_once_staff_has_associated_a_conversation():
    member = await _make_member("real@example.com", "Real", "Member")
    other_member = await _make_member("real2@example.com", "Other", "Member")

    client = _FakeFreeScoutClient([_conversation(7, email="unmatched@example.com", customer_id=None)])
    async with AsyncSessionLocal() as db:
        await sync_freescout_conversations(db, client)

    # Staff manually associates the (unmatched-by-email) conversation with a member.
    async with AsyncSessionLocal() as db:
        link = (await db.execute(select(HelpdeskConversationLink))).scalar_one()
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
        link = (await db.execute(select(HelpdeskConversationLink))).scalar_one()
        assert link.member_id == other_member.id


# ---------------------------------------------------------------------------
# Task board bridge + reply-to-customer (via the REST API)
# ---------------------------------------------------------------------------

async def _enable_module(client, headers):
    response = await client.put(
        "/api/v1/club-settings/modul_freescout_bridge", json={"value": "true"}, headers=headers,
    )
    assert response.status_code == 200, response.text
    await _choose_freescout()


async def _make_link(freescout_conversation_id=100, subject="Leaking tap") -> str:
    async with AsyncSessionLocal() as db:
        link = HelpdeskConversationLink(
            provider="freescout", external_id=str(freescout_conversation_id), mailbox_id="1",
            subject=subject, customer_email="x@example.com", status="active",
            external_updated_at=datetime.now(timezone.utc),
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
    import app.routers.api_helpdesk as api_helpdesk

    async def _fake_get_helpdesk(db):
        return fake_client

    monkeypatch.setattr(api_helpdesk, "get_helpdesk", _fake_get_helpdesk)

    response = await client.post(
        f"/api/v1/freescout/conversations/{link_id}/reply", json={"text": "We'll look into it."}, headers=headers,
    )
    assert response.status_code == 204, response.text
    assert fake_client.reply_calls == [("847", "We'll look into it.")]

    async with AsyncSessionLocal() as db:
        assert (await db.execute(select(TaskComment))).scalars().all() == []


# ---------------------------------------------------------------------------
# Permission gating
# ---------------------------------------------------------------------------

async def test_closed_deleted_and_spam_conversations_are_hidden_from_the_list(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _enable_module(client, headers)

    await _make_link(freescout_conversation_id=201)  # active, default in _make_link
    async with AsyncSessionLocal() as db:
        db.add(HelpdeskConversationLink(
            provider="freescout", external_id="202", mailbox_id="1", subject="Old, resolved",
            customer_email="x@example.com", status="closed",
            external_updated_at=datetime.now(timezone.utc),
        ))
        db.add(HelpdeskConversationLink(
            provider="freescout", external_id="203", mailbox_id="1", subject="Removed in FreeScout",
            customer_email="x@example.com", status="deleted",
            external_updated_at=datetime.now(timezone.utc),
        ))
        db.add(HelpdeskConversationLink(
            provider="freescout", external_id="204", mailbox_id="1", subject="Buy cheap watches",
            customer_email="spammer@example.com", status="spam",
            external_updated_at=datetime.now(timezone.utc),
        ))
        await db.commit()

    response = await client.get("/api/v1/freescout/conversations", headers=headers)
    assert response.status_code == 200, response.text
    conversation_ids = {c["freescout_conversation_id"] for c in response.json()}
    assert conversation_ids == {201}


async def test_unmatched_conversation_shows_no_action_badge_in_list(client, admin_user):
    """Issue #231: an unmatched conversation (no member_id) is normal and
    expected -- a lot of inbound mail is from non-members -- so the list
    must not flag it as something staff needs to act on."""
    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _enable_module(client, headers)
    await _make_link(freescout_conversation_id=301)  # unassociated by default

    await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})
    response = await client.get("/support/")
    assert response.status_code == 200
    assert "Needs association" not in response.text


async def test_dashboard_freescout_stat_counts_open_conversations_regardless_of_match(client, admin_user):
    """Issue #231: the dashboard tile counts active/pending conversations,
    not unmatched ones -- a member match no longer factors in, and closed
    conversations stay excluded (existing HIDDEN_STATUSES behavior)."""
    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _enable_module(client, headers)

    member = await _make_member("matched@example.com")
    async with AsyncSessionLocal() as db:
        db.add(HelpdeskConversationLink(
            provider="freescout", external_id="401", mailbox_id="1", subject="Matched, active",
            customer_email="matched@example.com", status="active", member_id=member.id,
            external_updated_at=datetime.now(timezone.utc),
        ))
        db.add(HelpdeskConversationLink(
            provider="freescout", external_id="402", mailbox_id="1", subject="Unmatched, active",
            customer_email="neighbor@example.com", status="active",
            external_updated_at=datetime.now(timezone.utc),
        ))
        db.add(HelpdeskConversationLink(
            provider="freescout", external_id="403", mailbox_id="1", subject="Unmatched, pending",
            customer_email="vendor@example.com", status="pending",
            external_updated_at=datetime.now(timezone.utc),
        ))
        db.add(HelpdeskConversationLink(
            provider="freescout", external_id="404", mailbox_id="1", subject="Old, resolved",
            customer_email="x@example.com", status="closed",
            external_updated_at=datetime.now(timezone.utc),
        ))
        await db.commit()

    await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})
    response = await client.get("/")
    assert response.status_code == 200
    assert "Needs association" not in response.text
    assert ">3<" in response.text


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


# ---------------------------------------------------------------------------
# ADR 0107: new addresses, the old ones still work, other helpdesks' rows
# stay out of the lists
# ---------------------------------------------------------------------------

async def test_new_api_uses_neutral_field_names_and_old_api_keeps_the_old_ones(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _enable_module(client, headers)
    await _make_link(freescout_conversation_id=501)

    new = await client.get("/api/v1/helpdesk/conversations", headers=headers)
    assert new.status_code == 200, new.text
    assert new.json()[0]["provider"] == "freescout"
    assert new.json()[0]["external_id"] == "501"
    assert new.json()[0]["status"] == "active"

    old = await client.get("/api/v1/freescout/conversations", headers=headers)
    assert old.status_code == 200, old.text
    assert old.json()[0]["freescout_conversation_id"] == 501
    assert old.json()[0]["freescout_status"] == "active"


async def test_old_freescout_addresses_redirect_to_support(client, admin_user):
    response = await client.get("/freescout/abc", follow_redirects=False)
    assert response.status_code == 301
    assert response.headers["location"] == "/support/abc"


async def test_conversations_of_another_helpdesk_are_hidden_not_deleted(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _enable_module(client, headers)
    await _make_link(freescout_conversation_id=601)
    async with AsyncSessionLocal() as db:
        db.add(HelpdeskConversationLink(
            provider="zammad", external_id="601", subject="From the old Zammad",
            customer_email="x@example.com", status="active", external_updated_at=datetime.now(timezone.utc),
        ))
        await db.commit()

    response = await client.get("/api/v1/helpdesk/conversations", headers=headers)
    assert [(c["provider"], c["external_id"]) for c in response.json()] == [("freescout", "601")]
    async with AsyncSessionLocal() as db:
        assert len((await db.execute(select(HelpdeskConversationLink))).scalars().all()) == 2


async def test_member_rename_updates_the_helpdesk_customer(client, admin_user, monkeypatch):
    member = await _make_member("rename@example.com", "Old", "Name")
    async with AsyncSessionLocal() as db:
        db.add(HelpdeskCustomerId(member_id=member.id, provider="freescout", customer_id="77"))
        await db.commit()

    calls = []

    class _Renaming(_FakeFreeScoutClient):
        async def update_customer(self, customer_id, first_name=None, last_name=None):
            calls.append((customer_id, first_name, last_name))

    async def _fake_get_helpdesk(db):
        return _Renaming([])

    monkeypatch.setattr("app.services.members.get_helpdesk", _fake_get_helpdesk)
    from app.services.members import update_member
    async with AsyncSessionLocal() as db:
        loaded = await db.get(Member, member.id)
        await update_member(db, loaded, first_name="New")
        await db.commit()

    assert calls == [("77", "New", "Name")]
