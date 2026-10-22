"""
Tests for the FreeScout helpdesk provider's HTTP layer
(app/helpdesk/freescout.py). Exercised against an httpx.MockTransport --
no real FreeScout instance is reachable from this test environment. The
sync and the support pages are tested in tests/test_freescout_bridge.py.
"""
import json
from datetime import datetime, timezone

import httpx
import pytest

from app.helpdesk import HelpdeskError
from app.helpdesk.freescout import FreeScoutProvider


def _client(handler) -> FreeScoutProvider:
    mock_client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    return FreeScoutProvider(base_url="https://service.example.org", api_key="secret", mailbox_id=1, client=mock_client)


def _page(conversations):
    return {"_embedded": {"conversations": conversations}}


async def test_list_conversations_passes_mailbox_and_updated_since():
    captured = []

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["X-FreeScout-API-Key"] == "secret"
        captured.append(dict(request.url.params))
        if request.url.params["page"] == "1" and request.url.params["status"] == "active":
            return httpx.Response(200, json=_page([
                {"id": 1, "subject": "A", "status": "active", "mailboxId": 1, "updatedAt": "2026-09-02T10:00:00Z",
                 "customer": {"id": 183, "email": "anna@example.com", "firstName": "Anna", "lastName": "Bergmann"}},
            ]))
        return httpx.Response(200, json=_page([]))

    client = _client(handler)
    conversations = await client.list_conversations(datetime(2026, 9, 1, tzinfo=timezone.utc))
    await client.aclose()

    assert [c.external_id for c in conversations] == ["1"]
    assert conversations[0].customer_id == "183"
    assert conversations[0].customer_name == "Anna Bergmann"
    assert conversations[0].mailbox_id == "1"
    assert captured[0]["mailboxId"] == "1"
    assert captured[0]["updatedSince"] == "2026-09-01T00:00:00Z"


async def test_list_conversations_covers_every_status_not_just_active():
    requested_statuses = []

    def handler(request: httpx.Request) -> httpx.Response:
        status = request.url.params["status"]
        if request.url.params["page"] == "1":
            requested_statuses.append(status)
        if status == "pending" and request.url.params["page"] == "1":
            return httpx.Response(200, json=_page([{"id": 99, "status": "pending", "updatedAt": "2026-09-01T00:00:00Z"}]))
        return httpx.Response(200, json=_page([]))

    client = _client(handler)
    conversations = await client.list_conversations(None)
    await client.aclose()

    assert {c.external_id for c in conversations} == {"99"}
    assert conversations[0].status == "pending"
    assert set(requested_statuses) == {"active", "pending", "closed", "spam"}


async def test_list_conversations_pages_past_the_first_page():
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.params["status"] != "active":
            return httpx.Response(200, json=_page([]))
        page = int(request.url.params["page"])
        pages = {1: [{"id": 1}, {"id": 2}], 2: [{"id": 3}]}
        return httpx.Response(200, json=_page(pages.get(page, [])))

    client = _client(handler)
    conversations = await client.list_conversations(None)
    await client.aclose()

    assert {c.external_id for c in conversations} == {"1", "2", "3"}


async def test_get_messages_embeds_threads_oldest_first():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.params["embed"] == "threads"
        return httpx.Response(200, json={"_embedded": {"threads": [
            {"type": "message", "body": "<p>reply</p>", "createdAt": "2026-09-02T10:00:00Z",
             "createdBy": {"firstName": "Vor", "lastName": "Stand"}},
            {"type": "customer", "text": "hi", "createdAt": "2026-09-01T10:00:00Z",
             "customer": {"email": "anna@example.com"}},
        ]}})

    client = _client(handler)
    messages = await client.get_messages("847")
    await client.aclose()

    assert [m.author for m in messages] == ["anna@example.com", "Vor Stand"]
    assert messages[0].from_customer and messages[0].body_text == "hi"
    assert messages[1].body_html == "<p>reply</p>"


async def test_create_conversation_posts_expected_shape():
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["body"] = json.loads(request.content)
        return httpx.Response(201, json={"id": 900})

    client = _client(handler)
    result = await client.create_conversation(
        subject="Hello from the website", customer_email="visitor@example.com",
        message="Hello", customer_name="Visitor",
    )
    await client.aclose()

    assert result == "900"
    body = captured["body"]
    assert body["mailboxId"] == 1
    assert body["customer"]["email"] == "visitor@example.com"
    assert body["threads"][0]["text"] == "Hello"


async def test_reply_posts_message_type():
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["path"] = request.url.path
        captured["body"] = json.loads(request.content)
        return httpx.Response(201, json={"id": 1})

    client = _client(handler)
    await client.reply("847", "We'll look into it.")
    await client.aclose()

    assert captured["path"] == "/api/conversations/847/threads"
    assert captured["body"] == {"type": "message", "text": "We'll look into it."}


async def test_update_customer_sends_only_given_names():
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["path"] = request.url.path
        captured["body"] = json.loads(request.content)
        return httpx.Response(200, json={})

    client = _client(handler)
    await client.update_customer("183", first_name="Anna")
    await client.aclose()

    assert captured == {"path": "/api/customers/183", "body": {"firstName": "Anna"}}


async def test_get_status_returns_status_when_present():
    client = _client(lambda r: httpx.Response(200, json={"id": 7346, "status": "active"}))
    assert await client.get_status("7346") == "active"
    await client.aclose()


async def test_get_status_returns_none_on_404():
    client = _client(lambda r: httpx.Response(404))
    assert await client.get_status("7346") is None
    await client.aclose()


async def test_get_status_returns_none_when_state_field_says_deleted():
    """FreeScout can also report a deleted conversation as a normal 200
    response whose `status` field still reads the pre-deletion value
    (e.g. "active") -- the separate `state: "deleted"` field is what
    actually signals it's gone."""
    client = _client(lambda r: httpx.Response(200, json={"id": 7346, "status": "active", "state": "deleted"}))
    assert await client.get_status("7346") is None
    await client.aclose()


async def test_unauthorized_raises_helpdesk_error():
    client = _client(lambda r: httpx.Response(401))
    with pytest.raises(HelpdeskError, match="API key"):
        await client.list_conversations(None)
    await client.aclose()


async def test_network_error_raises_helpdesk_error():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectTimeout("timed out", request=request)

    client = _client(handler)
    with pytest.raises(HelpdeskError):
        await client.list_conversations(None)
    await client.aclose()


async def test_server_error_raises_helpdesk_error_with_truncated_body():
    client = _client(lambda r: httpx.Response(500, text="x" * 500))
    with pytest.raises(HelpdeskError) as exc_info:
        await client.list_conversations(None)
    await client.aclose()

    assert len(str(exc_info.value)) < 400
