"""
Tests for the FreeScout API client (app/freescout_client.py). Exercised
against an httpx.MockTransport, same approach as NextcloudProvider/
WordPressPublisher (tests/test_cloud_storage.py) -- no real FreeScout
instance is reachable from this test environment.
"""
import json

import httpx
import pytest

from app.freescout_client import FreeScoutClient, FreeScoutError


def _mock_transport(handler):
    return httpx.MockTransport(handler)


def _client(handler) -> FreeScoutClient:
    mock_client = httpx.AsyncClient(transport=_mock_transport(handler))
    return FreeScoutClient(base_url="https://service.example.org", api_key="secret", mailbox_id=1, client=mock_client)


async def test_find_customer_by_email_found():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["X-FreeScout-API-Key"] == "secret"
        assert request.url.params["email"] == "anna@example.com"
        return httpx.Response(200, json={
            "_embedded": {"customers": [{"id": 183, "firstName": "Anna", "lastName": "Bergmann"}]}
        })

    client = _client(handler)
    customer = await client.find_customer_by_email("anna@example.com")
    await client.aclose()

    assert customer.id == 183
    assert customer.first_name == "Anna"


async def test_find_customer_by_email_not_found():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"_embedded": {"customers": []}})

    client = _client(handler)
    customer = await client.find_customer_by_email("nobody@example.com")
    await client.aclose()

    assert customer is None


async def test_create_customer_posts_email():
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["body"] = json.loads(request.content)
        return httpx.Response(201, json={"id": 42})

    client = _client(handler)
    customer = await client.create_customer("new@example.com", first_name="New", last_name="Person")
    await client.aclose()

    assert customer.id == 42
    assert captured["body"]["emails"] == ["new@example.com"]
    assert captured["body"]["firstName"] == "New"


async def test_list_conversations_passes_mailbox_and_updated_since():
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["params"] = dict(request.url.params)
        return httpx.Response(200, json={"_embedded": {"conversations": [{"id": 1}, {"id": 2}]}})

    client = _client(handler)
    conversations = await client.list_conversations(updated_since="2026-09-01T00:00:00Z")
    await client.aclose()

    assert len(conversations) == 2
    assert captured["params"]["mailboxId"] == "1"
    assert captured["params"]["updatedSince"] == "2026-09-01T00:00:00Z"


async def test_get_conversation_embeds_threads():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.params["embed"] == "threads"
        return httpx.Response(200, json={"id": 847, "_embedded": {"threads": [{"id": 1, "text": "hi"}]}})

    client = _client(handler)
    conversation = await client.get_conversation(847)
    await client.aclose()

    assert conversation["_embedded"]["threads"][0]["text"] == "hi"


async def test_create_conversation_posts_expected_shape():
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["body"] = json.loads(request.content)
        return httpx.Response(201, json={"id": 900})

    client = _client(handler)
    result = await client.create_conversation(
        subject="Contact form inquiry", customer_email="visitor@example.com",
        customer_name="Visitor", message="Hello",
    )
    await client.aclose()

    assert result["id"] == 900
    body = captured["body"]
    assert body["mailboxId"] == 1
    assert body["customer"]["email"] == "visitor@example.com"
    assert body["threads"][0]["text"] == "Hello"


async def test_create_thread_posts_message_type():
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["body"] = json.loads(request.content)
        return httpx.Response(201, json={"id": 5})

    client = _client(handler)
    await client.create_thread(847, "We'll look into it.")
    await client.aclose()

    assert captured["body"] == {"type": "message", "text": "We'll look into it."}


async def test_get_conversation_state_returns_status_when_present():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"id": 7346, "status": "active"})

    client = _client(handler)
    state = await client.get_conversation_state(7346)
    await client.aclose()

    assert state == "active"


async def test_get_conversation_state_returns_none_on_404():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404)

    client = _client(handler)
    state = await client.get_conversation_state(7346)
    await client.aclose()

    assert state is None


async def test_get_conversation_state_returns_none_when_state_field_says_deleted():
    """FreeScout can also report a deleted conversation as a normal 200
    response whose `status` field still reads the pre-deletion value
    (e.g. "active") -- the separate `state: "deleted"` field is what
    actually signals it's gone."""
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"id": 7346, "status": "active", "state": "deleted"})

    client = _client(handler)
    state = await client.get_conversation_state(7346)
    await client.aclose()

    assert state is None


async def test_unauthorized_raises_freescout_error():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401)

    client = _client(handler)
    with pytest.raises(FreeScoutError):
        await client.list_conversations()
    await client.aclose()


async def test_network_error_raises_freescout_error():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectTimeout("timed out", request=request)

    client = _client(handler)
    with pytest.raises(FreeScoutError):
        await client.list_conversations()
    await client.aclose()


async def test_server_error_raises_freescout_error_with_truncated_body():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, text="x" * 500)

    client = _client(handler)
    with pytest.raises(FreeScoutError) as exc_info:
        await client.list_conversations()
    await client.aclose()

    assert len(str(exc_info.value)) < 400
