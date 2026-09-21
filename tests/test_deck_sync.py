"""
Tests for Nextcloud Deck sync (app/task_sync.py's DeckTaskProvider,
app/deck_sync.py's sync_deck_tasks, the admin Integrations routes, and
the task board's locked-fields/badge/Adopt behavior for a linked task).

DeckTaskProvider is exercised against an httpx.MockTransport, the same
approach tests/test_cloud_storage.py uses for NextcloudProvider -- no
real Nextcloud/Deck instance is reachable from this test environment.
"""
import httpx as httpx_module

from app.database import AsyncSessionLocal
from app.crypto_utils import encrypt
from app.models import ClubSetting, ExternalTaskLink, Task, TaskList
from tests.conftest import login, auth_header


def _card(id, title, stack_order=0, order=0, due=None, archived=False, description=None, last_modified=1_700_000_000):
    return {
        "id": id, "title": title, "description": description, "duedate": due,
        "archived": archived, "order": order, "lastModified": last_modified,
    }


def _deck_mock_transport(stacks_by_board, boards_status=200):
    def handler(request: httpx_module.Request) -> httpx_module.Response:
        assert request.headers.get("OCS-APIRequest") == "true"
        path = request.url.path
        if path.endswith("/boards"):
            return httpx_module.Response(boards_status, json=[{"id": 1, "title": "Board"}])
        for board_id, stacks in stacks_by_board.items():
            if path.endswith(f"/boards/{board_id}/stacks"):
                return httpx_module.Response(200, json=stacks)
        return httpx_module.Response(404)
    return httpx_module.MockTransport(handler)


async def _enable_deck_sync(client, headers):
    response = await client.put(
        "/api/v1/club-settings/modul_deck_sync", json={"value": "true"}, headers=headers,
    )
    assert response.status_code == 200, response.text


async def _seed_deck_credentials(board_id="1"):
    async with AsyncSessionLocal() as session:
        session.add(ClubSetting(key="deck_base_url", value="https://cloud.example.org"))
        session.add(ClubSetting(key="deck_username", value="board"))
        session.add(ClubSetting(key="deck_app_password", value=encrypt("secret")))
        session.add(ClubSetting(key="deck_board_id", value=board_id))
        await session.commit()


# ---------------------------------------------------------------------------
# DeckTaskProvider (app/task_sync.py) unit tests
# ---------------------------------------------------------------------------

async def test_deck_provider_fetch_board_parses_stacks_and_cards():
    from app.task_sync import DeckTaskProvider

    stacks = [
        {"id": 10, "title": "To Do", "order": 0, "cards": [
            _card(101, "Water the trees", due="2026-10-01T00:00:00+00:00"),
        ]},
        {"id": 11, "title": "Done", "order": 1, "cards": [
            _card(102, "Repair the gate", archived=True),
        ]},
    ]
    mock_client = httpx_module.AsyncClient(transport=_deck_mock_transport({"1": stacks}))
    provider = DeckTaskProvider(base_url="https://cloud.example.org", username="board", app_password="secret", client=mock_client)

    result = await provider.fetch_board("1")
    await provider.aclose()

    assert [s.title for s in result] == ["To Do", "Done"]
    todo = result[0]
    assert len(todo.cards) == 1
    assert todo.cards[0].id == "101"
    assert todo.cards[0].title == "Water the trees"
    assert todo.cards[0].due_date.isoformat() == "2026-10-01"
    assert result[1].cards[0].archived is True


async def test_deck_provider_test_connection_reports_bad_credentials():
    from app.task_sync import DeckTaskProvider, DeckError

    mock_client = httpx_module.AsyncClient(transport=_deck_mock_transport({}, boards_status=401))
    provider = DeckTaskProvider(base_url="https://cloud.example.org", username="board", app_password="wrong", client=mock_client)

    try:
        await provider.test_connection()
        assert False, "expected DeckError"
    except DeckError as e:
        assert "401" in str(e) or "credentials" in str(e).lower()
    finally:
        await provider.aclose()


# ---------------------------------------------------------------------------
# sync_deck_tasks() (app/deck_sync.py)
# ---------------------------------------------------------------------------

async def _patch_deck_client(monkeypatch, stacks_by_board):
    from app.task_sync import DeckTaskProvider as RealDeckTaskProvider

    mock_client = httpx_module.AsyncClient(transport=_deck_mock_transport(stacks_by_board))

    async def fake_get_deck_client(db, client=None):
        return RealDeckTaskProvider(
            base_url="https://cloud.example.org", username="board", app_password="secret", client=mock_client,
        )

    monkeypatch.setattr("app.deck_sync.get_deck_client", fake_get_deck_client)
    return mock_client


async def test_sync_creates_lists_and_tasks_from_deck_cards(monkeypatch):
    await _seed_deck_credentials()
    stacks = [
        {"id": 10, "title": "To Do", "order": 0, "cards": [_card(101, "Water the trees")]},
        {"id": 11, "title": "Done", "order": 1, "cards": [_card(102, "Repair the gate")]},
    ]
    mock_client = await _patch_deck_client(monkeypatch, {"1": stacks})

    from app.deck_sync import sync_deck_tasks
    async with AsyncSessionLocal() as db:
        count = await sync_deck_tasks(db)
    await mock_client.aclose()

    assert count == 2
    async with AsyncSessionLocal() as db:
        from sqlalchemy import select
        list_names = {l.name for l in (await db.execute(select(TaskList))).scalars().all()}
        assert list_names == {"To Do", "Done"}

        links = (await db.execute(select(ExternalTaskLink))).scalars().all()
        assert len(links) == 2
        tasks = (await db.execute(select(Task))).scalars().all()
        titles = {t.title for t in tasks}
        assert titles == {"Water the trees", "Repair the gate"}


async def test_sync_skips_unchanged_cards_on_second_run(monkeypatch):
    await _seed_deck_credentials()
    stacks = [{"id": 10, "title": "To Do", "order": 0, "cards": [_card(101, "Water the trees")]}]
    mock_client = await _patch_deck_client(monkeypatch, {"1": stacks})

    from app.deck_sync import sync_deck_tasks
    async with AsyncSessionLocal() as db:
        first = await sync_deck_tasks(db)
    async with AsyncSessionLocal() as db:
        second = await sync_deck_tasks(db)
    await mock_client.aclose()

    assert first == 1
    assert second == 0  # unchanged lastModified -> incremental skip


async def test_sync_updates_title_and_moves_task_on_stack_change(monkeypatch):
    await _seed_deck_credentials()
    stacks_v1 = [
        {"id": 10, "title": "To Do", "order": 0, "cards": [_card(101, "Water the trees", last_modified=1)]},
        {"id": 11, "title": "In Progress", "order": 1, "cards": []},
    ]
    mock_client = await _patch_deck_client(monkeypatch, {"1": stacks_v1})
    from app.deck_sync import sync_deck_tasks
    async with AsyncSessionLocal() as db:
        await sync_deck_tasks(db)
    await mock_client.aclose()

    stacks_v2 = [
        {"id": 10, "title": "To Do", "order": 0, "cards": []},
        {"id": 11, "title": "In Progress", "order": 1, "cards": [_card(101, "Water the new trees", last_modified=2)]},
    ]
    mock_client2 = await _patch_deck_client(monkeypatch, {"1": stacks_v2})
    async with AsyncSessionLocal() as db:
        count = await sync_deck_tasks(db)
    await mock_client2.aclose()

    assert count == 1
    from sqlalchemy import select
    async with AsyncSessionLocal() as db:
        task = (await db.execute(select(Task).where(Task.title == "Water the new trees"))).scalar_one()
        target_list = (await db.execute(select(TaskList).where(TaskList.name == "In Progress"))).scalar_one()
        assert task.list_id == target_list.id


async def test_sync_reconciles_deleted_and_archived_cards(monkeypatch):
    await _seed_deck_credentials()
    stacks_v1 = [{"id": 10, "title": "To Do", "order": 0, "cards": [
        _card(101, "Stays"), _card(102, "Disappears"),
    ]}]
    mock_client = await _patch_deck_client(monkeypatch, {"1": stacks_v1})
    from app.deck_sync import sync_deck_tasks
    async with AsyncSessionLocal() as db:
        await sync_deck_tasks(db)
    await mock_client.aclose()

    # 102 is now archived (Deck may still return it, or omit it -- either
    # way it must be treated as gone from Parcella's perspective).
    stacks_v2 = [{"id": 10, "title": "To Do", "order": 0, "cards": [
        _card(101, "Stays", last_modified=1), _card(102, "Disappears", archived=True),
    ]}]
    mock_client2 = await _patch_deck_client(monkeypatch, {"1": stacks_v2})
    async with AsyncSessionLocal() as db:
        await sync_deck_tasks(db)
    await mock_client2.aclose()

    from sqlalchemy import select
    async with AsyncSessionLocal() as db:
        remaining_titles = {t.title for t in (await db.execute(select(Task))).scalars().all()}
        # Both tasks still exist (this app historizes, never hard-deletes
        # via sync) -- only the archived one's link should be gone.
        assert remaining_titles == {"Stays", "Disappears"}
        links = (await db.execute(select(ExternalTaskLink))).scalars().all()
        assert len(links) == 1
        assert links[0].external_card_id == "101"


async def test_sync_is_a_noop_without_configuration():
    from app.deck_sync import sync_deck_tasks
    async with AsyncSessionLocal() as db:
        count = await sync_deck_tasks(db)
    assert count == 0


# ---------------------------------------------------------------------------
# Admin Integrations routes
# ---------------------------------------------------------------------------

async def test_integrations_page_saves_deck_credentials(client, admin_user):
    await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})

    response = await client.post(
        "/admin/integrations/deck",
        data={
            "deck_base_url": "https://cloud.example.com", "deck_username": "board",
            "deck_app_password": "app-password-1", "deck_board_id": "7",
        },
    )
    assert response.status_code == 303
    assert "deck_saved=1" in response.headers["location"]

    async with AsyncSessionLocal() as db:
        from app.task_sync import load_deck_configuration, load_deck_board_id
        cfg = await load_deck_configuration(db)
        assert cfg["base_url"] == "https://cloud.example.com"
        assert cfg["app_password"] == "app-password-1"
        assert await load_deck_board_id(db) == "7"


async def test_deck_test_connection_reports_success(client, admin_user, monkeypatch):
    await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})

    mock_client = httpx_module.AsyncClient(transport=_deck_mock_transport({}))
    from app.task_sync import DeckTaskProvider as RealDeckTaskProvider

    class MockedDeckTaskProvider(RealDeckTaskProvider):
        def __init__(self, base_url, username, app_password, client=None):
            super().__init__(base_url, username, app_password, client=mock_client)

    monkeypatch.setattr("app.routers.admin.DeckTaskProvider", MockedDeckTaskProvider)

    response = await client.post(
        "/admin/integrations/deck/test",
        data={"deck_base_url": "https://cloud.example.com", "deck_username": "board", "deck_app_password": "secret"},
    )
    assert response.status_code == 303
    assert "deck_test=success" in response.headers["location"]
    await mock_client.aclose()


async def test_deck_sync_now_reports_count(client, admin_user, monkeypatch):
    await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})

    async def fake_sync_deck_tasks(db):
        return 3

    monkeypatch.setattr("app.routers.admin.sync_deck_tasks", fake_sync_deck_tasks)

    response = await client.post("/admin/integrations/deck/sync-now")
    assert response.status_code == 303
    assert "deck_synced=success" in response.headers["location"]


async def test_readonly_user_cannot_save_deck_credentials(client, admin_user):
    from app.models import User, UserRole
    from app.auth import hash_password

    async with AsyncSessionLocal() as session:
        session.add(User(
            email="readonly-deck@example.com", name="Readonly Deck",
            password_hash=hash_password("testpasswort123"), role=UserRole.READONLY,
        ))
        await session.commit()

    await client.post("/auth/login", data={"email": "readonly-deck@example.com", "password": "testpasswort123"})
    response = await client.post(
        "/admin/integrations/deck",
        data={"deck_base_url": "https://cloud.example.com", "deck_username": "board", "deck_app_password": "x", "deck_board_id": "1"},
    )
    assert response.status_code == 403


# ---------------------------------------------------------------------------
# Task board: linked-task locked fields, badge, and Adopt action
# ---------------------------------------------------------------------------

async def _seed_lists(names=("To Do", "In Progress", "Done")):
    ids = {}
    async with AsyncSessionLocal() as session:
        for position, name in enumerate(names):
            task_list = TaskList(name=name, position=position)
            session.add(task_list)
            await session.flush()
            ids[name] = task_list.id
        await session.commit()
    return ids


async def test_linked_task_renders_locked_fields_and_badge(client, admin_user):
    from datetime import datetime, timezone

    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    response = await client.put("/api/v1/club-settings/modul_tasks", json={"value": "true"}, headers=headers)
    assert response.status_code == 200
    lists = await _seed_lists()

    task_resp = (await client.post("/api/v1/tasks", json={"title": "Synced card"}, headers=headers)).json()

    async with AsyncSessionLocal() as session:
        session.add(ExternalTaskLink(
            task_id=task_resp["id"], source="deck",
            external_board_id="1", external_stack_id="10", external_card_id="999",
            external_updated_at=datetime.now(timezone.utc),
        ))
        await session.commit()

    await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})
    response = await client.get(f"/tasks/{task_resp['id']}/edit")
    assert response.status_code == 200
    assert "readonly" in response.text
    assert 'name="list_id" class="form-select" disabled' in response.text
    assert f'action="/tasks/{task_resp["id"]}/adopt"' in response.text


async def test_adopt_action_removes_link_and_unlocks_fields(client, admin_user):
    from datetime import datetime, timezone

    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await client.put("/api/v1/club-settings/modul_tasks", json={"value": "true"}, headers=headers)
    await _seed_lists()

    task_resp = (await client.post("/api/v1/tasks", json={"title": "Synced card"}, headers=headers)).json()
    async with AsyncSessionLocal() as session:
        session.add(ExternalTaskLink(
            task_id=task_resp["id"], source="deck",
            external_board_id="1", external_stack_id="10", external_card_id="999",
            external_updated_at=datetime.now(timezone.utc),
        ))
        await session.commit()

    await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})
    adopt_response = await client.post(f"/tasks/{task_resp['id']}/adopt")
    assert adopt_response.status_code in (302, 303)

    async with AsyncSessionLocal() as db:
        from sqlalchemy import select
        links = (await db.execute(select(ExternalTaskLink))).scalars().all()
        assert links == []

    edit_page = await client.get(f"/tasks/{task_resp['id']}/edit")
    assert 'name="list_id" class="form-select" disabled' not in edit_page.text
