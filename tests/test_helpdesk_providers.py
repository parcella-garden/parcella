"""
Helpdesk providers other than FreeScout (ADR 0107): Zammad, Znuny,
osTicket, Zendesk and Freshdesk against httpx.MockTransport (request
shape, authentication, state mapping, pagination), plus the capability
gating on the support pages and the one-helpdesk-at-a-time admin card.
"""
import json
from datetime import datetime, timezone

import httpx
import pytest

from app.helpdesk import ALL_CAPABILITIES, CREATE, HelpdeskError
from app.helpdesk.freshdesk import FreshdeskProvider
from app.helpdesk.osticket import OsTicketProvider
from app.helpdesk.zammad import ZammadProvider
from app.helpdesk.zendesk import ZendeskProvider
from app.helpdesk.znuny import ZnunyProvider
from tests.conftest import auth_header, login


def _mock(handler):
    return httpx.AsyncClient(transport=httpx.MockTransport(handler))


# ---------------------------------------------------------------------------
# Zammad
# ---------------------------------------------------------------------------

async def test_zammad_lists_tickets_with_customer_and_state_mapping():
    def handler(request):
        assert request.headers["Authorization"] == "Token token=tok"
        if request.url.path == "/api/v1/tickets":
            if request.url.params["page"] == "1":
                return httpx.Response(200, json=[
                    {"id": 5, "title": "Wasser", "state": "pending reminder", "customer_id": 9, "group": "Users",
                     "updated_at": "2026-10-01T10:00:00Z", "article_count": 3},
                    {"id": 6, "title": "Alt", "state": "closed", "customer_id": 9, "updated_at": "2025-01-01T10:00:00Z"},
                ])
            return httpx.Response(200, json=[])
        if request.url.path == "/api/v1/users/9":
            return httpx.Response(200, json={"id": 9, "email": "anna@example.com", "firstname": "Anna", "lastname": "B"})
        return httpx.Response(404)

    provider = ZammadProvider("https://z.example.org", "tok", client=_mock(handler))
    conversations = await provider.list_conversations(datetime(2026, 9, 1, tzinfo=timezone.utc))
    assert [(c.external_id, c.status, c.raw_status) for c in conversations] == [("5", "pending", "pending reminder")]
    assert conversations[0].customer_email == "anna@example.com"
    assert conversations[0].customer_id == "9"
    assert conversations[0].message_count == 3
    assert provider.conversation_url("5") == "https://z.example.org/#ticket/zoom/5"
    await provider.aclose()


async def test_zammad_reply_goes_to_the_customer_and_create_names_the_customer():
    posted = []

    def handler(request):
        if request.method == "GET" and request.url.path == "/api/v1/tickets/5":
            return httpx.Response(200, json={"id": 5, "title": "Wasser", "customer_id": 9})
        if request.url.path == "/api/v1/users/9":
            return httpx.Response(200, json={"email": "anna@example.com"})
        if request.url.path == "/api/v1/users/search":
            # Plain address, not the email:"..." syntax that needs Elasticsearch.
            assert request.url.params["query"] == "gast@example.com"
            return httpx.Response(200, json=[{"id": 3, "email": "gast.other@example.com"}])  # no exact match
        posted.append((request.url.path, json.loads(request.content)))
        if request.url.path == "/api/v1/users":
            return httpx.Response(201, json={"id": 42})
        return httpx.Response(201, json={"id": 77})

    provider = ZammadProvider("https://z.example.org", "tok", group="Verein", client=_mock(handler))
    await provider.reply("5", "Wir kümmern uns.")
    new_id = await provider.create_conversation("Frage", "gast@example.com", "Hallo", customer_name="Gerd Gast")

    article = posted[0][1]
    assert posted[0][0] == "/api/v1/ticket_articles"
    assert (article["ticket_id"], article["to"], article["internal"], article["type"]) == (5, "anna@example.com", False, "email")
    assert posted[1] == ("/api/v1/users", {
        "email": "gast@example.com", "firstname": "Gerd", "lastname": "Gast", "roles": ["Customer"],
    })
    ticket = posted[2][1]
    assert (ticket["group"], ticket["customer_id"]) == ("Verein", 42)
    assert new_id == "77"
    await provider.aclose()


async def test_zammad_reply_failure_names_the_likely_cause():
    def handler(request):
        if request.method == "GET":
            return httpx.Response(200, json={"id": 5, "title": "x", "customer_id": None})
        return httpx.Response(500, json={"error": "Please contact your administrator."})

    provider = ZammadProvider("https://z.example.org", "tok", client=_mock(handler))
    with pytest.raises(HelpdeskError, match="email address"):
        await provider.reply("5", "Hallo")
    await provider.aclose()


async def test_zammad_messages_leave_out_internal_notes():
    def handler(request):
        return httpx.Response(200, json=[
            {"from": "Anna", "body": "Hilfe", "content_type": "text/plain", "sender": "Customer", "internal": False},
            {"from": "Vorstand", "body": "intern", "content_type": "text/plain", "sender": "Agent", "internal": True},
        ])

    provider = ZammadProvider("https://z.example.org", "tok", client=_mock(handler))
    messages = await provider.get_messages("5")
    assert [(m.author, m.body_text, m.from_customer) for m in messages] == [("Anna", "Hilfe", True)]
    await provider.aclose()


# ---------------------------------------------------------------------------
# Znuny
# ---------------------------------------------------------------------------

def _znuny_handler(seen, *, error=None):
    def handler(request):
        seen.append(request)
        if request.url.path.endswith("/Session"):
            body = json.loads(request.content)
            if body["Password"] != "pw":
                return httpx.Response(200, json={"Error": {"ErrorCode": "SessionCreate.AuthFail", "ErrorMessage": "x"}})
            return httpx.Response(200, json={"SessionID": "sess-1"})
        if error:
            return httpx.Response(200, json={"Error": error})
        if request.url.path.endswith("/Ticket") and request.method == "GET":
            return httpx.Response(200, json={"TicketID": ["11", "12"]})
        if "/Ticket/" in request.url.path and request.method == "GET":
            return httpx.Response(200, json={"Ticket": [
                {"TicketID": "11", "Title": "Zaun", "StateType": "open", "State": "open",
                 "CustomerUserID": "anna@example.com", "Queue": "Raw", "Changed": "2026-10-01 10:00:00"},
                {"TicketID": "12", "Title": "Spam", "StateType": "closed", "State": "closed successful",
                 "CustomerUserID": "x", "Queue": "Raw", "Changed": "2026-10-01 11:00:00"},
            ]})
        return httpx.Response(200, json={"TicketID": "99"})
    return handler


async def test_znuny_logs_in_once_and_never_puts_the_password_in_a_url():
    seen = []
    provider = ZnunyProvider("https://h.example.org/otrs/nph-genericinterface.pl/Webservice/P", "agent", "pw",
                             client=_mock(_znuny_handler(seen)))
    conversations = await provider.list_conversations(datetime.now(timezone.utc))

    assert [(c.external_id, c.status) for c in conversations] == [("11", "active"), ("12", "closed")]
    assert conversations[0].customer_email == "anna@example.com"
    assert conversations[1].customer_email is None
    assert sum(1 for r in seen if r.url.path.endswith("/Session")) == 1
    assert all("pw" not in str(r.url) for r in seen)
    assert seen[1].url.params["SessionID"] == "sess-1"
    assert int(seen[1].url.params["TicketChangeTimeNewerMinutes"]) >= 24 * 60  # safety margin
    await provider.aclose()


async def test_znuny_error_objects_in_200_answers_are_errors():
    seen = []
    bad = ZnunyProvider("https://h.example.org/ws", "agent", "wrong", client=_mock(_znuny_handler(seen)))
    with pytest.raises(HelpdeskError, match="credentials"):
        await bad.test_connection()
    await bad.aclose()

    other = ZnunyProvider("https://h.example.org/ws", "agent", "pw",
                          client=_mock(_znuny_handler([], error={"ErrorCode": "TicketSearch.NotAuthorized"})))
    with pytest.raises(HelpdeskError, match="NotAuthorized"):
        await other.test_connection()
    await other.aclose()


def test_znuny_cannot_rename_customers():
    assert "customer_sync" not in ZnunyProvider.capabilities
    assert ZnunyProvider("https://h/ws", "a", "p", agent_url="https://h/otrs/index.pl").conversation_url("11") == \
        "https://h/otrs/index.pl?Action=AgentTicketZoom;TicketID=11"


# ---------------------------------------------------------------------------
# osTicket: create only
# ---------------------------------------------------------------------------

async def test_osticket_creates_tickets_and_nothing_else():
    posted = []

    def handler(request):
        assert request.headers["X-API-Key"] == "key"
        body = json.loads(request.content)
        posted.append(body)
        if not body:
            return httpx.Response(400, text="Required field missing")
        return httpx.Response(201, text="123456")

    provider = OsTicketProvider("https://o.example.org", "key", client=_mock(handler))
    await provider.test_connection()  # an empty post: 400 means the key works
    number = await provider.create_conversation("Frage", "gast@example.com", "Hallo", customer_name="Gast")
    assert number == "123456"
    assert posted[1] == {"name": "Gast", "email": "gast@example.com", "subject": "Frage", "message": "Hallo", "source": "API"}
    assert provider.capabilities == frozenset({CREATE})
    with pytest.raises(HelpdeskError):
        await provider.get_messages("1")
    await provider.aclose()


async def test_osticket_wrong_key_or_ip_is_reported():
    provider = OsTicketProvider("https://o.example.org", "key", client=_mock(lambda r: httpx.Response(401)))
    with pytest.raises(HelpdeskError, match="IP address"):
        await provider.test_connection()
    await provider.aclose()


# ---------------------------------------------------------------------------
# Zendesk and Freshdesk
# ---------------------------------------------------------------------------

async def test_zendesk_incremental_export_follows_the_cursor():
    calls = []

    def handler(request):
        calls.append(dict(request.url.params))
        assert request.headers["Authorization"].startswith("Basic ")
        if "cursor" not in request.url.params:
            return httpx.Response(200, json={
                "tickets": [{"id": 1, "subject": "A", "status": "hold", "requester_id": 7, "updated_at": "2026-10-01T10:00:00Z"}],
                "users": [{"id": 7, "email": "anna@example.com", "name": "Anna"}],
                "after_cursor": "c2", "end_of_stream": False,
            })
        return httpx.Response(200, json={
            "tickets": [{"id": 2, "subject": "B", "status": "deleted", "requester_id": 8, "updated_at": "2026-10-02T10:00:00Z"}],
            "users": [], "after_cursor": None, "end_of_stream": True,
        })

    provider = ZendeskProvider("https://club.zendesk.com", "agent@club.org", "tok", client=_mock(handler))
    conversations = await provider.list_conversations(None)
    assert [(c.external_id, c.status, c.customer_email) for c in conversations] == [
        ("1", "pending", "anna@example.com"), ("2", "deleted", None),
    ]
    assert calls[0]["start_time"] == "0" and calls[1]["cursor"] == "c2"
    await provider.aclose()


async def test_zendesk_anonymous_user_means_bad_credentials():
    provider = ZendeskProvider("https://club.zendesk.com", "a@b.c", "wrong",
                               client=_mock(lambda r: httpx.Response(200, json={"user": {"id": None}})))
    with pytest.raises(HelpdeskError, match="didn't accept"):
        await provider.test_connection()
    await provider.aclose()


async def test_freshdesk_maps_numeric_states_and_spam_and_pages():
    def handler(request):
        assert request.url.params["updated_since"] == "2000-01-01T00:00:00Z"
        if request.url.params["page"] == "1":
            return httpx.Response(200, json=[
                {"id": 1, "status": 3, "requester_id": 5, "requester": {"email": "a@example.com", "name": "A"},
                 "updated_at": "2026-10-01T10:00:00Z"},
                {"id": 2, "status": 2, "spam": True, "updated_at": "2026-10-01T10:00:00Z"},
            ])
        return httpx.Response(200, json=[])

    provider = FreshdeskProvider("https://club.freshdesk.com", "key", client=_mock(handler))
    conversations = await provider.list_conversations(None)
    assert [(c.external_id, c.status, c.raw_status) for c in conversations] == [
        ("1", "pending", "pending"), ("2", "spam", "open"),
    ]
    await provider.aclose()


async def test_freshdesk_transcript_starts_with_the_description_and_skips_private_notes():
    def handler(request):
        return httpx.Response(200, json={
            "description": "<p>Hilfe</p>", "created_at": "2026-10-01T10:00:00Z",
            "requester": {"name": "Anna"},
            "conversations": [
                {"body": "<p>Antwort</p>", "from_email": "vorstand@club.org", "incoming": False, "private": False},
                {"body": "<p>intern</p>", "private": True},
            ],
        })

    provider = FreshdeskProvider("https://club.freshdesk.com", "key", client=_mock(handler))
    messages = await provider.get_messages("1")
    assert [(m.author, m.body_html, m.from_customer) for m in messages] == [
        ("Anna", "<p>Hilfe</p>", True), ("vorstand@club.org", "<p>Antwort</p>", False),
    ]
    await provider.aclose()


def test_full_providers_declare_every_capability():
    for cls in (ZammadProvider, ZendeskProvider, FreshdeskProvider):
        assert cls.capabilities == ALL_CAPABILITIES


# ---------------------------------------------------------------------------
# Pages and admin card
# ---------------------------------------------------------------------------

async def web_login(client, email: str, password: str = "testpasswort123") -> None:
    response = await client.post("/auth/login", data={"email": email, "password": password})
    assert response.status_code in (302, 303)


async def test_support_page_explains_a_helpdesk_without_inbox(client, admin_user):
    token = await login(client, "admin@example.com")
    await client.put("/api/v1/club-settings/modul_freescout_bridge", json={"value": "true"}, headers=auth_header(token))
    await web_login(client, "admin@example.com")
    await client.post("/admin/integrations/helpdesk", data={
        "helpdesk_provider": "osticket",
        "helpdesk_osticket_base_url": "https://o.example.org",
        "helpdesk_osticket_api_key": "key",
    })

    page = await client.get("/support/")
    assert page.status_code == 200
    assert "osTicket can&#39;t list conversations" in page.text or "osTicket can't list conversations" in page.text
    assert 'href="https://o.example.org"' in page.text


async def test_switching_helpdesk_keeps_the_other_settings(client, admin_user):
    await web_login(client, "admin@example.com")
    await client.post("/admin/integrations/helpdesk", data={
        "helpdesk_provider": "freescout",
        "helpdesk_freescout_base_url": "https://fs.example.org",
        "helpdesk_freescout_api_key": "fs-secret",
    })
    response = await client.post("/admin/integrations/helpdesk", data={
        "helpdesk_provider": "zammad",
        "helpdesk_zammad_base_url": "https://z.example.org",
        "helpdesk_zammad_api_token": "z-secret",
    })
    assert "helpdesk_saved=1" in response.headers["location"]

    from app.database import AsyncSessionLocal
    from app.helpdesk import HELPDESK, get_helpdesk
    async with AsyncSessionLocal() as session:
        active = await get_helpdesk(session)
        assert isinstance(active, ZammadProvider) and active.group == "Users"
        assert (await HELPDESK.load_config(session, "freescout"))["api_key"] == "fs-secret"
        await active.aclose()

    page = await client.get("/admin/integrations")
    assert 'value="zammad" selected' in page.text
    assert "z-secret" not in page.text and "fs-secret" not in page.text


async def test_helpdesk_settings_api_lists_all_six_and_hides_secrets(client, admin_user):
    await web_login(client, "admin@example.com")
    await client.post("/admin/integrations/helpdesk", data={
        "helpdesk_provider": "freshdesk",
        "helpdesk_freshdesk_base_url": "https://club.freshdesk.com",
        "helpdesk_freshdesk_api_key": "fd-secret",
    })
    token = await login(client, "admin@example.com")
    types = await client.get("/api/v1/helpdesk/providers", headers=auth_header(token))
    assert {t["type"] for t in types.json()} == {"freescout", "zammad", "znuny", "osticket", "zendesk", "freshdesk"}
    current = await client.get("/api/v1/helpdesk", headers=auth_header(token))
    assert current.json()["active"] == "freshdesk"
    assert "fd-secret" not in current.text
