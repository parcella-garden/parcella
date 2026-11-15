"""
MCP endpoint for the notes knowledge base (issue #307, ADR 0132).

The hard rule (kermie, 2026-11-08): no personal data goes to any AI. So
most of these tests are about what the AI must NOT see: unreleased notes
(by search, by id, through the category/tag lists), author fields, cloud
file names -- and that its MCP-only token opens nothing else in the API.
"""
from datetime import date

from app.database import AsyncSessionLocal
from app.main import app
from app.models import Group, GroupMembership, GroupModulePermission, User, UserRole
from app.auth import hash_password
from app.services import api_tokens
from tests.conftest import login, auth_header

MCP = "/api/v1/mcp"


async def _enable(client, headers, module="mcp", value="true"):
    response = await client.put(f"/api/v1/club-settings/modul_{module}", json={"value": value}, headers=headers)
    assert response.status_code == 200, response.text


async def _ai_user(can_write=True) -> User:
    """The dedicated AI account: a group with notes access only."""
    async with AsyncSessionLocal() as db:
        user = User(email="ki@example.com", name="KI-Assistent", password_hash=hash_password("testpasswort123"),
                    role=UserRole.READONLY)
        group = Group(name="KI")
        db.add_all([user, group])
        await db.flush()
        db.add(GroupMembership(user_id=user.id, group_id=group.id))
        db.add(GroupModulePermission(group_id=group.id, module="notes", can_read=True, can_write=can_write, can_delete=False))
        await db.commit()
        return user


async def _token(user: User, mcp_only=True) -> str:
    async with AsyncSessionLocal() as db:
        db_user = await db.get(User, user.id)
        _, raw = await api_tokens.create_token(db, db_user, "Claude", 30, created_by=db_user, mcp_only=mcp_only)
        return raw


async def _note(client, headers, title, body, tags=(), category_id=None):
    payload = {"title": title, "body_markdown": body, "note_date": "2026-11-01", "new_tags": list(tags)}
    if category_id:
        payload["category_id"] = category_id
    response = await client.post("/api/v1/notes", json=payload, headers=headers)
    assert response.status_code == 201, response.text
    return response.json()


async def _rpc(client, token, method, params=None, request_id=1, headers=None):
    body = {"jsonrpc": "2.0", "id": request_id, "method": method}
    if params is not None:
        body["params"] = params
    return await client.post(MCP, json=body, headers={"Authorization": f"Bearer {token}", **(headers or {})})


async def _tool(client, token, name, **arguments):
    response = await _rpc(client, token, "tools/call", {"name": name, "arguments": arguments})
    assert response.status_code == 200, response.text
    return response.json()["result"]


async def _setup(client):
    admin_token = await login(client, "admin@example.com")
    headers = auth_header(admin_token)
    await _enable(client, headers)
    category = (await client.post("/api/v1/notes/categories", json={"name": "Vorstand"}, headers=headers)).json()
    released = await _note(client, headers, "Wasser im Frühjahr", "Das Wasser wird am 11. April angestellt.",
                           tags=["ki-freigegeben", "wasser"])
    secret = await _note(client, headers, "Sprechstunde Erika Muster (Parzelle 42)", "Geheimwort Zebrafink.",
                         tags=["erika-muster"], category_id=category["id"])
    token = await _token(await _ai_user())
    return headers, token, released, secret


async def test_handshake_and_tool_list(client, admin_user):
    _headers, token, _released, _secret = await _setup(client)

    init = await _rpc(client, token, "initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                                                    "clientInfo": {"name": "test", "version": "1"}})
    assert init.status_code == 200
    result = init.json()["result"]
    assert result["protocolVersion"] == "2025-06-18" and "tools" in result["capabilities"]

    notification = await client.post(MCP, json={"jsonrpc": "2.0", "method": "notifications/initialized"},
                                      headers={"Authorization": f"Bearer {token}"})
    assert notification.status_code == 202 and notification.content == b""

    tools = (await _rpc(client, token, "tools/list")).json()["result"]["tools"]
    assert {t["name"] for t in tools} == {"search_notes", "get_note", "list_categories", "list_tags",
                                          "create_note", "update_note"}
    assert "delete" not in str([t["name"] for t in tools])

    assert (await client.get(MCP, headers={"Authorization": f"Bearer {token}"})).status_code == 405
    assert (await _rpc(client, token, "resources/list")).json()["error"]["code"] == -32601


async def test_unreleased_notes_do_not_exist_for_the_ai(client, admin_user):
    _headers, token, released, secret = await _setup(client)

    # Search by text that only appears in the unreleased note.
    for query in ("Zebrafink", "Erika", "Parzelle 42"):
        assert (await _tool(client, token, "search_notes", query=query))["structuredContent"]["notes"] == []
    found = (await _tool(client, token, "search_notes", query="Wasser"))["structuredContent"]["notes"]
    assert [n["id"] for n in found] == [released["id"]]

    # By id: the same answer as for an id that doesn't exist.
    hidden = await _tool(client, token, "get_note", id=secret["id"])
    missing = await _tool(client, token, "get_note", id="00000000-0000-0000-0000-000000000000")
    assert hidden["isError"] and hidden["content"] == missing["content"]

    # Terms only used on the unreleased note stay invisible (a tag could be a name).
    tags = (await _tool(client, token, "list_tags"))["structuredContent"]["tags"]
    assert "erika-muster" not in tags and "wasser" in tags
    assert (await _tool(client, token, "list_categories"))["structuredContent"]["categories"] == []
    assert (await _tool(client, token, "search_notes", tag="erika-muster"))["structuredContent"]["notes"] == []


async def test_note_output_carries_no_author_or_file_fields(client, admin_user):
    _headers, token, released, _secret = await _setup(client)
    note = (await _tool(client, token, "get_note", id=released["id"]))["structuredContent"]
    assert set(note) == {"id", "title", "date", "category", "tags", "source", "body", "version"}
    assert "admin" not in str(note).lower()
    listed = (await _tool(client, token, "search_notes"))["structuredContent"]["notes"][0]
    assert set(listed) == {"id", "title", "date", "category", "tags", "source", "excerpt"}


async def test_ai_creates_and_updates_only_released_notes(client, admin_user):
    headers, token, released, secret = await _setup(client)

    created = await _tool(client, token, "create_note", title="Zusammenfassung Wasser",
                          body="Kurz: ab April Wasser.", tags=["wasser"])
    assert not created["isError"], created
    note = created["structuredContent"]
    assert {"ki-freigegeben", "ki-erstellt", "wasser"} <= set(note["tags"])

    # It can't touch the unreleased note -- "not found", nothing changed.
    refused = await _tool(client, token, "update_note", id=secret["id"], body="overwritten")
    assert refused["isError"]
    assert (await client.get(f"/api/v1/notes/{secret['id']}", headers=headers)).json()["body_markdown"] == "Geheimwort Zebrafink."

    # Updating a released note: only the passed fields change, the
    # release tag can't be dropped, the created tag is added.
    updated = await _tool(client, token, "update_note", id=released["id"], body="Neu: 12. April.", tags=["wasser"])
    assert not updated["isError"], updated
    out = updated["structuredContent"]
    assert out["body"] == "Neu: 12. April." and out["title"] == "Wasser im Frühjahr"
    assert {"ki-freigegeben", "ki-erstellt", "wasser"} <= set(out["tags"])

    # A hidden tag -- by base name or by a translation -- is refused with
    # the same message as a tag that doesn't exist, and never attached.
    async with AsyncSessionLocal() as db:
        from sqlalchemy import select
        from app.models import TaxonomyTag
        hidden_tag = (await db.execute(select(TaxonomyTag).where(TaxonomyTag.name == "erika-muster"))).scalar_one()
        hidden_tag.translations = {"en": "Erika family"}
        await db.commit()
    answers = [await _tool(client, token, "create_note", title="probe", tags=[name])
               for name in ("erika-muster", "Erika family", "does-not-exist")]
    assert all(a["isError"] for a in answers)
    assert len({a["content"][0]["text"] for a in answers}) == 1
    assert "erika-muster" not in (await _tool(client, token, "list_tags"))["structuredContent"]["tags"]

    # Naming a category it can't see doesn't confirm it exists.
    unknown = await _tool(client, token, "create_note", title="x", category="Vorstand")
    assert unknown["isError"] and "Unknown category" in unknown["content"][0]["text"]


async def test_read_only_ai_user_gets_no_write_tools(client, admin_user):
    admin_token = await login(client, "admin@example.com")
    await _enable(client, auth_header(admin_token))
    token = await _token(await _ai_user(can_write=False))
    names = {t["name"] for t in (await _rpc(client, token, "tools/list")).json()["result"]["tools"]}
    assert names == {"search_notes", "get_note", "list_categories", "list_tags"}
    assert (await _tool(client, token, "create_note", title="x"))["isError"]


async def test_mcp_token_opens_nothing_else_and_ordinary_tokens_dont_open_mcp(client, admin_user):
    """Every other API route rejects the AI's token -- otherwise
    GET /api/v1/notes would hand it every unreleased note."""
    _headers, token, _released, _secret = await _setup(client)

    checked = 0
    for route in app.routes:
        path = getattr(route, "path", "")
        if not path.startswith("/api/v1/") or path.startswith(MCP) or path.startswith("/api/v1/public") \
                or "{" in path or "GET" not in getattr(route, "methods", set()):
            continue
        response = await client.get(path, headers={"Authorization": f"Bearer {token}"})
        assert response.status_code in (401, 403, 404), (path, response.status_code)
        checked += 1
    assert checked > 20
    assert (await client.get("/api/v1/notes", headers={"Authorization": f"Bearer {token}"})).status_code == 401

    # An ordinary token of the same AI user is refused by the MCP endpoint.
    async with AsyncSessionLocal() as db:
        from sqlalchemy import select
        ai = (await db.execute(select(User).where(User.email == "ki@example.com"))).scalar_one()
    ordinary = await _token(ai, mcp_only=False)
    assert (await _rpc(client, ordinary, "tools/list")).status_code == 401
    assert (await _rpc(client, "", "tools/list")).status_code == 401


async def test_mcp_is_off_by_default_and_checks_the_origin(client, admin_user):
    admin_token = await login(client, "admin@example.com")
    token = await _token(await _ai_user())
    assert (await _rpc(client, token, "tools/list")).status_code == 404  # module off

    await _enable(client, auth_header(admin_token))
    evil = await _rpc(client, token, "tools/list", headers={"Origin": "https://evil.example"})
    assert evil.status_code == 403
    assert (await _rpc(client, token, "tools/list")).status_code == 200
