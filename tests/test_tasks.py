"""
Tests for the task board module. Focus: the card-ordering algorithm
(app/task_board.py) -- cross-list moves, same-list reordering, and that
deleting a card doesn't leave a gap in `position` -- list (column)
management (create/rename/reorder/delete-with-reassignment, issue #100)
-- and the admin/board-only permission boundary on both the web UI and
the API.
"""
from app.database import AsyncSessionLocal
from app.models import TaskList
from tests.conftest import login, auth_header


async def _enable_module(client, headers):
    response = await client.put(
        "/api/v1/club-settings/modul_tasks", json={"value": "true"}, headers=headers,
    )
    assert response.status_code == 200, response.text


async def _seed_lists(names=("To Do", "In Progress", "Done")):
    """Mirrors migration 0054_task_lists's seed data -- the test DB is
    built straight from models via create_all (see conftest.py), not
    Alembic, so tests seed their own lists. Returns {name: id}."""
    ids = {}
    async with AsyncSessionLocal() as session:
        for position, name in enumerate(names):
            task_list = TaskList(name=name, position=position)
            session.add(task_list)
            await session.flush()
            ids[name] = task_list.id
        await session.commit()
    return ids


async def web_login(client, email: str, password: str = "testpasswort123") -> None:
    response = await client.post("/auth/login", data={"email": email, "password": password})
    assert response.status_code in (302, 303)


async def test_create_defaults_to_first_list_at_end(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _enable_module(client, headers)
    lists = await _seed_lists()

    first = (await client.post("/api/v1/tasks", json={"title": "First"}, headers=headers)).json()
    second = (await client.post("/api/v1/tasks", json={"title": "Second"}, headers=headers)).json()

    assert first["list_id"] == lists["To Do"]
    assert first["position"] == 0
    assert second["list_id"] == lists["To Do"]
    assert second["position"] == 1


async def test_move_to_different_list_appends_and_compacts_old_list(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _enable_module(client, headers)
    lists = await _seed_lists()

    a = (await client.post("/api/v1/tasks", json={"title": "A"}, headers=headers)).json()
    b = (await client.post("/api/v1/tasks", json={"title": "B"}, headers=headers)).json()
    c = (await client.post("/api/v1/tasks", json={"title": "C"}, headers=headers)).json()

    moved = (await client.post(
        f"/api/v1/tasks/{a['id']}/move",
        json={"list_id": lists["In Progress"], "position": 0}, headers=headers,
    )).json()
    assert moved["list_id"] == lists["In Progress"]
    assert moved["position"] == 0

    todo = (await client.get("/api/v1/tasks", params={"list_id": lists["To Do"]}, headers=headers)).json()
    todo_ids_in_order = [t["id"] for t in sorted(todo, key=lambda t: t["position"])]
    assert todo_ids_in_order == [b["id"], c["id"]]
    assert [t["position"] for t in sorted(todo, key=lambda t: t["position"])] == [0, 1]


async def test_reorder_within_same_list(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _enable_module(client, headers)
    lists = await _seed_lists()

    a = (await client.post("/api/v1/tasks", json={"title": "A"}, headers=headers)).json()
    b = (await client.post("/api/v1/tasks", json={"title": "B"}, headers=headers)).json()
    c = (await client.post("/api/v1/tasks", json={"title": "C"}, headers=headers)).json()

    # Move C (currently position 2) to the front of "To Do"
    await client.post(
        f"/api/v1/tasks/{c['id']}/move", json={"list_id": lists["To Do"], "position": 0}, headers=headers,
    )

    todo = (await client.get("/api/v1/tasks", params={"list_id": lists["To Do"]}, headers=headers)).json()
    ordered = [t["id"] for t in sorted(todo, key=lambda t: t["position"])]
    assert ordered == [c["id"], a["id"], b["id"]]


async def test_delete_closes_gap_in_remaining_list(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _enable_module(client, headers)
    lists = await _seed_lists()

    a = (await client.post("/api/v1/tasks", json={"title": "A"}, headers=headers)).json()
    b = (await client.post("/api/v1/tasks", json={"title": "B"}, headers=headers)).json()
    c = (await client.post("/api/v1/tasks", json={"title": "C"}, headers=headers)).json()

    delete_response = await client.delete(f"/api/v1/tasks/{b['id']}", headers=headers)
    assert delete_response.status_code == 204

    todo = (await client.get("/api/v1/tasks", params={"list_id": lists["To Do"]}, headers=headers)).json()
    ordered = sorted(todo, key=lambda t: t["position"])
    assert [t["id"] for t in ordered] == [a["id"], c["id"]]
    assert [t["position"] for t in ordered] == [0, 1]


async def test_update_task_fields(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _enable_module(client, headers)
    await _seed_lists()

    task = (await client.post("/api/v1/tasks", json={"title": "Original"}, headers=headers)).json()

    updated = (await client.put(
        f"/api/v1/tasks/{task['id']}",
        json={"title": "Renamed", "description": "Details", "due_date": "2026-12-01"},
        headers=headers,
    )).json()

    assert updated["title"] == "Renamed"
    assert updated["description"] == "Details"
    assert updated["due_date"] == "2026-12-01"


async def test_task_priority_set_update_and_clear_via_api(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _enable_module(client, headers)
    await _seed_lists()

    no_priority = (await client.post("/api/v1/tasks", json={"title": "Unprioritized"}, headers=headers)).json()
    assert no_priority["priority"] is None

    created = (await client.post(
        "/api/v1/tasks", json={"title": "Fix the roof", "priority": "HIGH"}, headers=headers,
    )).json()
    assert created["priority"] == "HIGH"

    updated = (await client.put(
        f"/api/v1/tasks/{created['id']}", json={"priority": "LOW"}, headers=headers,
    )).json()
    assert updated["priority"] == "LOW"

    cleared = (await client.put(
        f"/api/v1/tasks/{created['id']}", json={"priority": None}, headers=headers,
    )).json()
    assert cleared["priority"] is None


async def test_task_tags_set_update_and_clear_via_api(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _enable_module(client, headers)
    await _seed_lists()

    untagged = (await client.post("/api/v1/tasks", json={"title": "Untagged"}, headers=headers)).json()
    assert untagged["tags"] == []

    created = (await client.post(
        "/api/v1/tasks", json={"title": "Fix the roof", "tags": ["urgent", "outdoor"]}, headers=headers,
    )).json()
    assert created["tags"] == ["urgent", "outdoor"]

    updated = (await client.put(
        f"/api/v1/tasks/{created['id']}", json={"tags": ["outdoor"]}, headers=headers,
    )).json()
    assert updated["tags"] == ["outdoor"]

    cleared = (await client.put(
        f"/api/v1/tasks/{created['id']}", json={"tags": []}, headers=headers,
    )).json()
    assert cleared["tags"] == []


async def test_create_task_with_multiple_assignees(client, admin_user):
    from app.models import User, UserRole
    from app.auth import hash_password

    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _enable_module(client, headers)
    await _seed_lists()

    async with AsyncSessionLocal() as session:
        alice = User(
            email="alice@example.com", name="Alice",
            password_hash=hash_password("testpasswort123"), role=UserRole.BOARD,
        )
        bob = User(
            email="bob@example.com", name="Bob",
            password_hash=hash_password("testpasswort123"), role=UserRole.BOARD,
        )
        session.add_all([alice, bob])
        await session.commit()
        await session.refresh(alice)
        await session.refresh(bob)

    created = (await client.post(
        "/api/v1/tasks",
        json={"title": "Repaint the fence", "assigned_to_ids": [alice.id, bob.id]},
        headers=headers,
    )).json()
    assert sorted(created["assigned_to_ids"]) == sorted([alice.id, bob.id])

    fetched = (await client.get(f"/api/v1/tasks/{created['id']}", headers=headers)).json()
    assert sorted(fetched["assigned_to_ids"]) == sorted([alice.id, bob.id])


async def test_update_task_resyncs_assignees(client, admin_user):
    from app.models import User, UserRole
    from app.auth import hash_password

    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _enable_module(client, headers)
    await _seed_lists()

    async with AsyncSessionLocal() as session:
        alice = User(
            email="alice2@example.com", name="Alice Two",
            password_hash=hash_password("testpasswort123"), role=UserRole.BOARD,
        )
        bob = User(
            email="bob2@example.com", name="Bob Two",
            password_hash=hash_password("testpasswort123"), role=UserRole.BOARD,
        )
        session.add_all([alice, bob])
        await session.commit()
        await session.refresh(alice)
        await session.refresh(bob)

    created = (await client.post(
        "/api/v1/tasks", json={"title": "Order supplies", "assigned_to_ids": [alice.id]}, headers=headers,
    )).json()
    assert created["assigned_to_ids"] == [alice.id]

    updated = (await client.put(
        f"/api/v1/tasks/{created['id']}", json={"assigned_to_ids": [bob.id]}, headers=headers,
    )).json()
    assert updated["assigned_to_ids"] == [bob.id]

    # Omitting assigned_to_ids entirely from the PUT body leaves the
    # existing assignees untouched (exclude_unset semantics, same as
    # every other partial-update field on this endpoint).
    untouched = (await client.put(
        f"/api/v1/tasks/{created['id']}", json={"description": "Restocked"}, headers=headers,
    )).json()
    assert untouched["assigned_to_ids"] == [bob.id]

    cleared = (await client.put(
        f"/api/v1/tasks/{created['id']}", json={"assigned_to_ids": []}, headers=headers,
    )).json()
    assert cleared["assigned_to_ids"] == []


async def test_readonly_member_cannot_access_api(client, admin_user):
    from app.models import User, UserRole
    from app.auth import hash_password

    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _enable_module(client, headers)

    async with AsyncSessionLocal() as session:
        session.add(User(
            email="readonly@example.com", name="Readonly",
            password_hash=hash_password("testpasswort123"), role=UserRole.READONLY,
        ))
        await session.commit()

    readonly_token = await login(client, "readonly@example.com")
    response = await client.get("/api/v1/tasks", headers=auth_header(readonly_token))
    assert response.status_code == 403


async def test_readonly_member_gets_403_on_web_board(client, admin_user):
    from app.models import User, UserRole
    from app.auth import hash_password

    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _enable_module(client, headers)

    async with AsyncSessionLocal() as session:
        session.add(User(
            email="readonly2@example.com", name="Readonly Two",
            password_hash=hash_password("testpasswort123"), role=UserRole.READONLY,
        ))
        await session.commit()

    await web_login(client, "readonly2@example.com")
    response = await client.get("/tasks/")
    assert response.status_code == 403


async def test_web_board_renders_and_create_edit_delete_flow(client, admin_user):
    from app.models import User, UserRole
    from app.auth import hash_password

    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _enable_module(client, headers)
    lists = await _seed_lists()

    # Assigned to a *different* user than the logged-in one on purpose: if
    # it were the same user, SQLAlchemy could resolve the relationship from
    # the session's identity map without a real lazy-load query, masking a
    # missing selectinload() on the board query (this happened once -- see
    # docs/module-tasks.md).
    async with AsyncSessionLocal() as session:
        board_member = User(
            email="board-member@example.com", name="Board Member",
            password_hash=hash_password("testpasswort123"), role=UserRole.BOARD,
        )
        session.add(board_member)
        await session.commit()
        await session.refresh(board_member)

    await web_login(client, "admin@example.com")

    create_response = await client.post(
        "/tasks/new",
        data={
            "title": "Fix the gate lock", "description": "Squeaky hinge", "due_date": "2026-08-01",
            "priority": "HIGH", "tags": "urgent, outdoor, urgent, ",
            "assigned_to_ids": [board_member.id],
        },
    )
    assert create_response.status_code in (302, 303)

    board_response = await client.get("/tasks/")
    assert board_response.status_code == 200
    assert "Fix the gate lock" in board_response.text
    assert "UndefinedError" not in board_response.text
    assert board_member.name in board_response.text
    # The exact rendered badge markup, not a bare "kanban-card-priority-high"
    # substring check -- that also matches board.html's <style> block CSS
    # selector, which is always present regardless of any card's priority.
    assert 'class="kanban-card-priority kanban-card-priority-high"' in board_response.text
    # "urgent" typed twice (with stray whitespace) collapses to one badge.
    assert board_response.text.count('class="kanban-card-tag"') == 2
    assert '<span class="kanban-card-tag">urgent</span>' in board_response.text
    assert '<span class="kanban-card-tag">outdoor</span>' in board_response.text

    import re
    m = re.search(r'/tasks/([a-f0-9-]+)/edit', board_response.text)
    assert m, "no edit link found on board"
    task_id = m.group(1)

    edit_page = await client.get(f"/tasks/{task_id}/edit")
    assert edit_page.status_code == 200
    assert "Fix the gate lock" in edit_page.text
    assert 'value="urgent, outdoor"' in edit_page.text

    edit_response = await client.post(
        f"/tasks/{task_id}/edit",
        data={"title": "Fix the gate lock (urgent)", "description": "Squeaky hinge", "due_date": ""},
    )
    assert edit_response.status_code in (302, 303)

    board_response2 = await client.get("/tasks/")
    assert "Fix the gate lock (urgent)" in board_response2.text
    # Priority and tags form fields were both omitted on the edit POST --
    # same "" default as an explicit clear, so both should be gone.
    assert 'class="kanban-card-priority kanban-card-priority-high"' not in board_response2.text
    assert 'class="kanban-card-tag"' not in board_response2.text
    # assigned_to_ids was also omitted -- the web form always resyncs to
    # exactly what was submitted, so the assignee is cleared too.
    assert board_member.name not in board_response2.text

    move_response = await client.post(
        f"/tasks/{task_id}/move",
        json={"list_id": lists["Done"], "position": 0},
    )
    assert move_response.status_code == 200
    assert move_response.json()["ok"] is True

    delete_response = await client.post(f"/tasks/{task_id}/delete")
    assert delete_response.status_code in (302, 303)

    board_response3 = await client.get("/tasks/")
    assert "Fix the gate lock" not in board_response3.text


async def test_web_form_supports_multiple_assignees(client, admin_user):
    from app.models import User, UserRole
    from app.auth import hash_password

    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _enable_module(client, headers)
    await _seed_lists()

    async with AsyncSessionLocal() as session:
        alice = User(
            email="alice3@example.com", name="Alice Three",
            password_hash=hash_password("testpasswort123"), role=UserRole.BOARD,
        )
        bob = User(
            email="bob3@example.com", name="Bob Three",
            password_hash=hash_password("testpasswort123"), role=UserRole.BOARD,
        )
        session.add_all([alice, bob])
        await session.commit()
        await session.refresh(alice)
        await session.refresh(bob)

    await web_login(client, "admin@example.com")

    create_response = await client.post(
        "/tasks/new",
        data={"title": "Water the new trees", "assigned_to_ids": [alice.id, bob.id]},
    )
    assert create_response.status_code in (302, 303)

    board_response = await client.get("/tasks/")
    assert alice.name in board_response.text
    assert bob.name in board_response.text

    import re
    m = re.search(r'/tasks/([a-f0-9-]+)/edit', board_response.text)
    assert m, "no edit link found on board"
    task_id = m.group(1)

    edit_page = await client.get(f"/tasks/{task_id}/edit")
    assert edit_page.status_code == 200
    assert f'id="assignee-{alice.id}"' in edit_page.text
    assert f'id="assignee-{bob.id}"' in edit_page.text

    # Resync down to a single assignee on edit.
    edit_response = await client.post(
        f"/tasks/{task_id}/edit",
        data={"title": "Water the new trees", "due_date": "", "assigned_to_ids": [bob.id]},
    )
    assert edit_response.status_code in (302, 303)

    board_response2 = await client.get("/tasks/")
    assert alice.name not in board_response2.text
    assert bob.name in board_response2.text


async def test_module_disabled_returns_404(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    response = await client.put(
        "/api/v1/club-settings/modul_tasks", json={"value": "false"}, headers=headers,
    )
    assert response.status_code == 200, response.text

    await web_login(client, "admin@example.com")

    response = await client.get("/tasks/")
    assert response.status_code == 404

    api_response = await client.get("/api/v1/tasks", headers=headers)
    assert api_response.status_code == 404


# ---------------------------------------------------------------------------
# Export report -- Markdown activity export (app/task_report.py)
# ---------------------------------------------------------------------------

async def test_export_report_includes_touched_and_full_snapshot(client, admin_user):
    from datetime import datetime, timedelta, timezone
    from app.models import Task, TaskComment

    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _enable_module(client, headers)
    lists = await _seed_lists()

    now = datetime.now(timezone.utc)
    old = now - timedelta(days=90)

    async with AsyncSessionLocal() as session:
        touched = Task(
            title="Touched Card", list_id=lists["To Do"], position=0,
            created_at=now, updated_at=now,
        )
        untouched = Task(
            title="Old Untouched Card", list_id=lists["Done"], position=0,
            created_at=old, updated_at=old,
        )
        session.add_all([touched, untouched])
        await session.flush()
        session.add(TaskComment(task_id=touched.id, content="Discussed in the window", created_at=now))
        await session.commit()

    await web_login(client, "admin@example.com")
    date_from = (now - timedelta(days=7)).date().isoformat()
    date_to = now.date().isoformat()
    response = await client.get("/tasks/export", params={"date_from": date_from, "date_to": date_to})

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/markdown")
    assert f'tasks_report_{date_from}_{date_to}.md' in response.headers["content-disposition"]

    body = response.text
    touched_section, _, remainder = body.partition("## Comments in this period")
    assert "Touched Card" in touched_section
    assert "Old Untouched Card" not in touched_section
    assert "Discussed in the window" in remainder
    # The full-board snapshot section lists every card regardless of window.
    assert "Old Untouched Card" in body


async def test_export_report_defaults_to_30_day_window_without_params(client, admin_user):
    from datetime import date, timedelta

    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _enable_module(client, headers)
    await _seed_lists()

    await web_login(client, "admin@example.com")
    response = await client.get("/tasks/export")

    assert response.status_code == 200
    expected_from = date.today() - timedelta(days=30)
    assert f'tasks_report_{expected_from}_{date.today()}.md' in response.headers["content-disposition"]


async def test_readonly_member_gets_403_on_export_report(client, admin_user):
    from app.models import User, UserRole
    from app.auth import hash_password

    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _enable_module(client, headers)

    async with AsyncSessionLocal() as session:
        session.add(User(
            email="readonly3@example.com", name="Readonly Three",
            password_hash=hash_password("testpasswort123"), role=UserRole.READONLY,
        ))
        await session.commit()

    await web_login(client, "readonly3@example.com")
    response = await client.get("/tasks/export")
    assert response.status_code == 403


# ---------------------------------------------------------------------------
# List (column) management -- issue #100
# ---------------------------------------------------------------------------

async def test_create_list_appends_at_end(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _enable_module(client, headers)
    await _seed_lists()

    created = (await client.post("/api/v1/tasks/lists", json={"name": "Blocked"}, headers=headers)).json()
    assert created["name"] == "Blocked"
    assert created["position"] == 3

    all_lists = (await client.get("/api/v1/tasks/lists", headers=headers)).json()
    assert [l["name"] for l in sorted(all_lists, key=lambda l: l["position"])] == \
        ["To Do", "In Progress", "Done", "Blocked"]


async def test_rename_list(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _enable_module(client, headers)
    lists = await _seed_lists()

    renamed = (await client.put(
        f"/api/v1/tasks/lists/{lists['To Do']}", json={"name": "Backlog"}, headers=headers,
    )).json()
    assert renamed["name"] == "Backlog"


async def test_reorder_lists(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _enable_module(client, headers)
    lists = await _seed_lists()

    await client.post(
        f"/api/v1/tasks/lists/{lists['Done']}/move", json={"position": 0}, headers=headers,
    )

    all_lists = (await client.get("/api/v1/tasks/lists", headers=headers)).json()
    ordered_names = [l["name"] for l in sorted(all_lists, key=lambda l: l["position"])]
    assert ordered_names == ["Done", "To Do", "In Progress"]


async def test_delete_empty_list(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _enable_module(client, headers)
    lists = await _seed_lists()

    response = await client.delete(
        f"/api/v1/tasks/lists/{lists['Done']}", headers=headers,
    )
    assert response.status_code == 204

    all_lists = (await client.get("/api/v1/tasks/lists", headers=headers)).json()
    assert sorted(l["name"] for l in all_lists) == ["In Progress", "To Do"]


async def test_delete_list_with_cards_reassigns_them(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _enable_module(client, headers)
    lists = await _seed_lists()

    existing = (await client.post(
        "/api/v1/tasks", json={"title": "Already in progress", "list_id": lists["In Progress"]}, headers=headers,
    )).json()
    a = (await client.post(
        "/api/v1/tasks", json={"title": "A", "list_id": lists["To Do"]}, headers=headers,
    )).json()
    b = (await client.post(
        "/api/v1/tasks", json={"title": "B", "list_id": lists["To Do"]}, headers=headers,
    )).json()

    response = await client.delete(
        f"/api/v1/tasks/lists/{lists['To Do']}",
        params={"move_to_list_id": lists["In Progress"]}, headers=headers,
    )
    assert response.status_code == 204

    remaining = (await client.get(
        "/api/v1/tasks", params={"list_id": lists["In Progress"]}, headers=headers,
    )).json()
    ordered = sorted(remaining, key=lambda t: t["position"])
    assert [t["id"] for t in ordered] == [existing["id"], a["id"], b["id"]]
    assert [t["position"] for t in ordered] == [0, 1, 2]
    assert all(t["list_id"] == lists["In Progress"] for t in ordered)


async def test_delete_only_remaining_list_is_rejected(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _enable_module(client, headers)

    only_list = (await client.post("/api/v1/tasks/lists", json={"name": "Solo"}, headers=headers)).json()

    response = await client.delete(f"/api/v1/tasks/lists/{only_list['id']}", headers=headers)
    assert response.status_code == 400


async def test_delete_nonempty_list_without_target_is_rejected(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _enable_module(client, headers)
    lists = await _seed_lists()

    await client.post("/api/v1/tasks", json={"title": "A", "list_id": lists["To Do"]}, headers=headers)

    response = await client.delete(f"/api/v1/tasks/lists/{lists['To Do']}", headers=headers)
    assert response.status_code == 400


async def test_readonly_member_cannot_manage_lists_via_api(client, admin_user):
    from app.models import User, UserRole
    from app.auth import hash_password

    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _enable_module(client, headers)
    await _seed_lists()

    async with AsyncSessionLocal() as session:
        session.add(User(
            email="readonly3@example.com", name="Readonly Three",
            password_hash=hash_password("testpasswort123"), role=UserRole.READONLY,
        ))
        await session.commit()

    readonly_token = await login(client, "readonly3@example.com")
    response = await client.get("/api/v1/tasks/lists", headers=auth_header(readonly_token))
    assert response.status_code == 403


async def test_web_add_rename_delete_list_flow(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _enable_module(client, headers)
    lists = await _seed_lists()

    await web_login(client, "admin@example.com")

    add_response = await client.post("/tasks/lists/new", data={"name": "Blocked"})
    assert add_response.status_code in (302, 303)

    board_response = await client.get("/tasks/")
    assert "Blocked" in board_response.text
    # The rename/delete URLs are assembled by JS from data-list-id on the
    # dropdown items (one shared modal per action), not rendered as a
    # literal href/action per list -- see app/templates/tasks/board.html.
    assert f'data-list-id="{lists["Done"]}"' in board_response.text

    rename_response = await client.post(
        f"/tasks/lists/{lists['Done']}/edit", data={"name": "Finished"},
    )
    assert rename_response.status_code in (302, 303)

    board_response2 = await client.get("/tasks/")
    assert "Finished" in board_response2.text
    assert ">Done<" not in board_response2.text

    delete_response = await client.post(f"/tasks/lists/{lists['In Progress']}/delete")
    assert delete_response.status_code in (302, 303)

    board_response3 = await client.get("/tasks/")
    assert "In Progress" not in board_response3.text


async def test_add_and_list_comment(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _enable_module(client, headers)
    await _seed_lists()

    task = (await client.post("/api/v1/tasks", json={"title": "Task"}, headers=headers)).json()

    created = await client.post(
        f"/api/v1/tasks/{task['id']}/comments", json={"content": "Looking into it"}, headers=headers,
    )
    assert created.status_code == 201
    comment = created.json()
    assert comment["content"] == "Looking into it"
    assert comment["task_id"] == task["id"]

    listed = await client.get(f"/api/v1/tasks/{task['id']}/comments", headers=headers)
    assert listed.status_code == 200
    assert [c["id"] for c in listed.json()] == [comment["id"]]


async def test_delete_comment(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _enable_module(client, headers)
    await _seed_lists()

    task = (await client.post("/api/v1/tasks", json={"title": "Task"}, headers=headers)).json()
    comment = (await client.post(
        f"/api/v1/tasks/{task['id']}/comments", json={"content": "Temporary"}, headers=headers,
    )).json()

    delete_response = await client.delete(
        f"/api/v1/tasks/{task['id']}/comments/{comment['id']}", headers=headers,
    )
    assert delete_response.status_code == 204

    listed = await client.get(f"/api/v1/tasks/{task['id']}/comments", headers=headers)
    assert listed.json() == []


async def test_comment_on_nonexistent_task_is_404(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _enable_module(client, headers)

    response = await client.post(
        "/api/v1/tasks/does-not-exist/comments", json={"content": "Hi"}, headers=headers,
    )
    assert response.status_code == 404


async def test_delete_nonexistent_comment_is_404(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _enable_module(client, headers)
    await _seed_lists()

    task = (await client.post("/api/v1/tasks", json={"title": "Task"}, headers=headers)).json()

    response = await client.delete(
        f"/api/v1/tasks/{task['id']}/comments/does-not-exist", headers=headers,
    )
    assert response.status_code == 404


async def test_readonly_member_cannot_manage_comments_via_api(client, admin_user):
    from app.models import User, UserRole
    from app.auth import hash_password

    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _enable_module(client, headers)
    await _seed_lists()

    task = (await client.post("/api/v1/tasks", json={"title": "Task"}, headers=headers)).json()

    async with AsyncSessionLocal() as session:
        session.add(User(
            email="readonly4@example.com", name="Readonly Four",
            password_hash=hash_password("testpasswort123"), role=UserRole.READONLY,
        ))
        await session.commit()

    readonly_token = await login(client, "readonly4@example.com")
    readonly_headers = auth_header(readonly_token)

    response = await client.post(
        f"/api/v1/tasks/{task['id']}/comments", json={"content": "Hi"}, headers=readonly_headers,
    )
    assert response.status_code == 403


async def test_web_add_and_delete_comment_flow(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _enable_module(client, headers)
    await _seed_lists()

    task = (await client.post("/api/v1/tasks", json={"title": "Task"}, headers=headers)).json()

    await web_login(client, "admin@example.com")

    add_response = await client.post(
        f"/tasks/{task['id']}/comments", data={"content": "Please review"},
    )
    assert add_response.status_code in (302, 303)

    edit_page = await client.get(f"/tasks/{task['id']}/edit")
    assert "Please review" in edit_page.text

    listed = await client.get(f"/api/v1/tasks/{task['id']}/comments", headers=headers)
    comment_id = listed.json()[0]["id"]

    delete_response = await client.post(f"/tasks/{task['id']}/comments/{comment_id}/delete")
    assert delete_response.status_code in (302, 303)

    edit_page2 = await client.get(f"/tasks/{task['id']}/edit")
    assert "Please review" not in edit_page2.text


async def test_board_renders_search_filter_data_attributes(client, admin_user):
    """Issue #119: the board's search/filter is client-side JS over
    data-* attributes on each card, so this only has to verify those
    attributes are actually rendered correctly -- title, description,
    tags, and comment content folded into data-search-text (lowercased),
    plus data-priority/data-tags/data-assignee-ids/data-due-month, and
    that the tag/assignee/due-month filter dropdowns are populated from
    what's actually on the board (the due-month one as a localized
    "Month YYYY" label, not a raw value). Also exercises the board query's
    selectinload(Task.comments) -- a missing eager-load here would trip
    an unawaited-lazy-load error under asyncpg (see CLAUDE.md's
    identity-map sharp edge), not just render an empty attribute."""
    from app.models import User, UserRole
    from app.auth import hash_password

    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _enable_module(client, headers)
    await _seed_lists()

    async with AsyncSessionLocal() as session:
        alice = User(
            email="alice-filter@example.com", name="Alice Filterby",
            password_hash=hash_password("testpasswort123"), role=UserRole.BOARD,
        )
        session.add(alice)
        await session.commit()
        await session.refresh(alice)

    await web_login(client, "admin@example.com")

    create_response = await client.post(
        "/tasks/new",
        data={
            "title": "Renew the insurance policy",
            "description": "Talk to the broker about the annual renewal",
            "due_date": "2026-11-15",
            "priority": "HIGH",
            "tags": "urgent, admin",
            "assigned_to_ids": [alice.id],
        },
    )
    assert create_response.status_code in (302, 303)

    await client.post(
        "/tasks/new", data={"title": "Untagged task with no extras"},
    )

    board_response = await client.get("/tasks/")
    assert board_response.status_code == 200
    html = board_response.text

    assert 'data-search-text="renew the insurance policy talk to the broker' in html
    assert 'data-priority="high"' in html
    assert 'data-tags="urgent,admin"' in html
    assert f'data-assignee-ids="{alice.id}"' in html
    assert 'data-due-month="2026-11"' in html

    # Filter dropdowns must be populated from what's actually on the
    # board (the tag/assignee added above), not every tag/user ever
    # created. The due-month dropdown shows a human-readable "Month
    # YYYY" label (localized -- English here), not a raw YYYY-MM value.
    assert '<option value="urgent">urgent</option>' in html
    assert '<option value="admin">admin</option>' in html
    assert f'<option value="{alice.id}">{alice.name}</option>' in html
    assert '<option value="2026-11">November 2026</option>' in html


async def test_board_search_text_includes_comment_content(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _enable_module(client, headers)
    await _seed_lists()
    await web_login(client, "admin@example.com")

    create_response = await client.post("/tasks/new", data={"title": "Fix the fence"})
    assert create_response.status_code in (302, 303)

    board_response = await client.get("/tasks/")
    import re
    m = re.search(r'data-task-id="([a-f0-9-]+)"', board_response.text)
    task_id = m.group(1)

    await client.post(f"/tasks/{task_id}/comments", data={"content": "Ask the neighbor about the broken post"})

    board_response2 = await client.get("/tasks/")
    assert board_response2.status_code == 200
    assert "ask the neighbor about the broken post" in board_response2.text.lower()


async def test_board_renders_sort_dropdown(client, admin_user):
    """Issue #120: sort by due date / priority is purely client-side JS
    reordering the same data-priority/data-due-month attributes the
    search/filter feature (issue #119) already renders -- nothing new
    to eager-load or compute server-side, so this just guards that the
    <select id="task-sort"> and its three options are actually present
    on the page (a template typo here would otherwise only surface as
    a silent missing control, not an error)."""
    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _enable_module(client, headers)
    await _seed_lists()
    await web_login(client, "admin@example.com")

    board_response = await client.get("/tasks/")
    assert board_response.status_code == 200
    html = board_response.text

    assert 'id="task-sort"' in html
    assert '<option value="due_date">' in html
    assert '<option value="priority">' in html


async def test_dashboard_overdue_tasks_card_and_board_prefilter(client, admin_user):
    """Issue #127: dashboard gets an "Overdue Tasks" card counting tasks
    whose due_date is in the past (across every list -- there's no
    "done" flag to exclude by, see docs/module-tasks.md), linking to
    /tasks/?overdue=1. The board pre-checks its own "Overdue only"
    filter checkbox from that query param (ADR 0019: the stat and the
    view it links to must use the exact same definition of the count)."""
    from datetime import date, timedelta

    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _enable_module(client, headers)
    await _seed_lists()
    await web_login(client, "admin@example.com")

    past = (date.today() - timedelta(days=5)).isoformat()
    future = (date.today() + timedelta(days=5)).isoformat()

    await client.post("/tasks/new", data={"title": "Overdue task", "due_date": past})
    await client.post("/tasks/new", data={"title": "Future task", "due_date": future})
    await client.post("/tasks/new", data={"title": "Undated task"})

    dashboard_response = await client.get("/")
    assert dashboard_response.status_code == 200
    assert 'href="/tasks/?overdue=1"' in dashboard_response.text

    import re
    m = re.search(r'Overdue Tasks.*?font-weight: 700; color: #b91c1c;">(\d+)<', dashboard_response.text, re.S)
    assert m, "expected an Overdue Tasks stat block on the dashboard"
    assert m.group(1) == "1"

    board_response = await client.get("/tasks/")
    assert board_response.status_code == 200
    assert board_response.text.count('data-overdue="1"') == 1

    prefiltered_response = await client.get("/tasks/?overdue=1")
    assert prefiltered_response.status_code == 200
    assert 'id="task-filter-overdue" checked' in prefiltered_response.text
