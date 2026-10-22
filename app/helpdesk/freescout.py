"""
FreeScout (https://freescout.net): open-source helpdesk with a full REST
API module -- every Parcella feature is available. Moved here from
app/freescout_client.py when the helpdesk became pluggable (ADR 0107);
the HTTP calls are unchanged.
"""
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.helpdesk.base import (
    ALL_CAPABILITIES, ConfigField, HelpdeskConversation, HelpdeskError, HelpdeskMessage, HttpHelpdeskProvider,
    STATUS_ACTIVE, STATUS_CLOSED, STATUS_PENDING, STATUS_SPAM, parse_iso,
)

DEFAULT_MAILBOX_ID = 1

# Every status FreeScout's own UI can put a conversation in. FreeScout's
# GET /api/conversations defaults `status` to "active" when the param is
# omitted -- list_conversations() iterates all four explicitly so
# pending/closed/spam conversations are never silently excluded.
CONVERSATION_STATUSES = ("active", "pending", "closed", "spam")
_STATUS_MAP = {"active": STATUS_ACTIVE, "pending": STATUS_PENDING, "closed": STATUS_CLOSED, "spam": STATUS_SPAM}


def extract_customer(conversation: dict) -> dict:
    """FreeScout embeds the customer either directly under "customer" or
    under "_embedded.customer" depending on endpoint/version -- accept
    either shape rather than assuming one."""
    customer = conversation.get("customer") or conversation.get("_embedded", {}).get("customer") or {}
    email = customer.get("email")
    if not email:
        emails = customer.get("emails") or []
        email = emails[0]["value"] if emails and isinstance(emails[0], dict) else (emails[0] if emails else None)
    name_parts = [customer.get("firstName"), customer.get("lastName")]
    name = " ".join(p for p in name_parts if p) or None
    return {"id": customer.get("id"), "email": email, "name": name}


class FreeScoutProvider(HttpHelpdeskProvider):
    type = "freescout"
    label = "FreeScout"
    capabilities = ALL_CAPABILITIES
    config_fields = [
        ConfigField("base_url", kind="url", required=True, placeholder="https://support.example.org"),
        ConfigField("api_key", kind="secret", required=True, hint=True),
        ConfigField("mailbox_id", default=str(DEFAULT_MAILBOX_ID), placeholder="1", hint=True),
    ]

    def __init__(
        self, base_url: str, api_key: str, mailbox_id: int = DEFAULT_MAILBOX_ID,
        client: Optional[httpx.AsyncClient] = None,
    ):
        super().__init__(base_url, client)
        self.api_key = api_key
        self.mailbox_id = mailbox_id

    @classmethod
    async def build(cls, config: dict, db: AsyncSession) -> "FreeScoutProvider":
        try:
            mailbox_id = int(config.get("mailbox_id") or DEFAULT_MAILBOX_ID)
        except ValueError:
            mailbox_id = DEFAULT_MAILBOX_ID
        return cls(base_url=config["base_url"], api_key=config["api_key"], mailbox_id=mailbox_id)

    def _auth(self) -> dict:
        return {"X-FreeScout-API-Key": self.api_key}

    def conversation_url(self, external_id: str) -> Optional[str]:
        return f"{self.base_url}/conversation/{external_id}"

    async def _request(self, method: str, path: str, **kwargs) -> httpx.Response:
        response = await self._raw(method, path, **kwargs)
        if response.status_code == 401:
            raise HelpdeskError("FreeScout rejected the API key (401 Unauthorized).")
        if response.status_code >= 400:
            raise HelpdeskError(f"FreeScout returned HTTP {response.status_code}: {response.text[:200]}")
        return response

    async def test_connection(self) -> None:
        await self._request("GET", "/api/conversations", params={"mailboxId": self.mailbox_id, "page": 1})

    # -- conversations -------------------------------------------------

    async def _list_page(self, updated_since: Optional[str], page: int, status: str) -> List[dict]:
        params: Dict[str, Any] = {"mailboxId": self.mailbox_id, "page": page, "status": status}
        if updated_since:
            params["updatedSince"] = updated_since
        response = await self._request("GET", "/api/conversations", params=params)
        return self._json(response).get("_embedded", {}).get("conversations", [])

    @staticmethod
    def _to_conversation(raw: dict) -> HelpdeskConversation:
        customer = extract_customer(raw)
        raw_status = raw.get("status", "active")
        return HelpdeskConversation(
            external_id=str(raw["id"]),
            subject=raw.get("subject", "") or "",
            customer_email=customer.get("email"),
            customer_name=customer.get("name"),
            customer_id=str(customer["id"]) if customer.get("id") is not None else None,
            status=_STATUS_MAP.get(raw_status, STATUS_ACTIVE),
            raw_status=raw_status,
            updated_at=parse_iso(raw.get("updatedAt")) or datetime.now(timezone.utc),
            mailbox_id=str(raw["mailboxId"]) if raw.get("mailboxId") is not None else None,
            message_count=raw.get("threadsCount"),
        )

    async def list_conversations(self, updated_since: Optional[datetime]) -> List[HelpdeskConversation]:
        """Every conversation in every status, across every page -- one
        page of one status alone would silently drop pending/closed/spam
        conversations and anything past page one."""
        since = updated_since.strftime("%Y-%m-%dT%H:%M:%SZ") if updated_since else None
        conversations: List[HelpdeskConversation] = []
        for status in CONVERSATION_STATUSES:
            page = 1
            while True:
                batch = await self._list_page(since, page, status)
                if not batch:
                    break
                conversations.extend(self._to_conversation(raw) for raw in batch)
                page += 1
        return conversations

    async def get_status(self, external_id: str) -> Optional[str]:
        """FreeScout represents a deleted conversation either as a 404 or
        as `state: "deleted"` on an otherwise normal response (its
        `status` is untouched by deletion) -- both mean "gone"."""
        response = await self._raw("GET", f"/api/conversations/{external_id}")
        if response.status_code == 404:
            return None
        if response.status_code == 401:
            raise HelpdeskError("FreeScout rejected the API key (401 Unauthorized).")
        if response.status_code >= 400:
            raise HelpdeskError(f"FreeScout returned HTTP {response.status_code}: {response.text[:200]}")
        data = self._json(response)
        if data.get("state") == "deleted":
            return None
        return _STATUS_MAP.get(data.get("status"), STATUS_ACTIVE)

    async def get_messages(self, external_id: str) -> List[HelpdeskMessage]:
        response = await self._request("GET", f"/api/conversations/{external_id}", params={"embed": "threads"})
        threads = self._json(response).get("_embedded", {}).get("threads", [])
        messages = []
        for thread in threads:
            created_by = thread.get("createdBy") or {}
            customer = thread.get("customer") or {}
            author = " ".join(p for p in [created_by.get("firstName"), created_by.get("lastName")] if p) \
                or created_by.get("email") or customer.get("email") or ""
            messages.append(HelpdeskMessage(
                author=author, created_at=parse_iso(thread.get("createdAt")),
                body_html=thread.get("body"), body_text=thread.get("text"),
                from_customer=thread.get("type") == "customer",
            ))
        # FreeScout lists newest first.
        messages.sort(key=lambda m: m.created_at or datetime.min.replace(tzinfo=timezone.utc))
        return messages

    async def reply(self, external_id: str, text: str) -> None:
        """A customer-facing reply (type="message"); FreeScout emails it out."""
        await self._request("POST", f"/api/conversations/{external_id}/threads", json={"type": "message", "text": text})

    async def create_conversation(
        self, subject: str, customer_email: str, message: str, customer_name: Optional[str] = None,
    ) -> str:
        customer: Dict[str, Any] = {"email": customer_email}
        if customer_name:
            customer["firstName"] = customer_name
        payload = {
            "type": "email",
            "mailboxId": self.mailbox_id,
            "subject": subject,
            "customer": customer,
            "threads": [{"type": "customer", "text": message, "customer": customer}],
            "status": "active",
        }
        response = await self._request("POST", "/api/conversations", json=payload)
        return str(self._json(response).get("id", ""))

    async def update_customer(
        self, customer_id: str, first_name: Optional[str] = None, last_name: Optional[str] = None,
    ) -> None:
        payload: Dict[str, Any] = {}
        if first_name:
            payload["firstName"] = first_name
        if last_name:
            payload["lastName"] = last_name
        if payload:
            await self._request("PUT", f"/api/customers/{customer_id}", json=payload)
