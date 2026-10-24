"""
Freshdesk (https://www.freshworks.com/freshdesk/): commercial helpdesk
with a complete REST API -- every Parcella feature is available.
Authenticated with an agent's API key (Profile settings -> View API key).
"""
from datetime import datetime, timezone
from typing import Dict, List, Optional

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.helpdesk.base import (
    ALL_CAPABILITIES, ConfigField, HelpdeskConversation, HelpdeskError, HelpdeskMessage, HttpHelpdeskProvider,
    STATUS_ACTIVE, STATUS_CLOSED, STATUS_PENDING, STATUS_SPAM, parse_iso,
)

PER_PAGE = 100
# Freshdesk's built-in numeric statuses; custom ones count as active.
_STATUS_MAP = {2: STATUS_ACTIVE, 3: STATUS_PENDING, 4: STATUS_CLOSED, 5: STATUS_CLOSED}
_STATUS_NAMES = {2: "open", 3: "pending", 4: "resolved", 5: "closed"}


class FreshdeskProvider(HttpHelpdeskProvider):
    type = "freshdesk"
    label = "Freshdesk"
    capabilities = ALL_CAPABILITIES
    config_fields = [
        ConfigField("base_url", kind="url", required=True, placeholder="https://yourclub.freshdesk.com"),
        ConfigField("api_key", kind="secret", required=True, hint=True),
    ]

    def __init__(self, base_url: str, api_key: str, client: Optional[httpx.AsyncClient] = None):
        super().__init__(base_url, client)
        self.api_key = api_key

    @classmethod
    async def build(cls, config: dict, db: AsyncSession) -> "FreshdeskProvider":
        return cls(base_url=config["base_url"], api_key=config["api_key"])

    def _auth_kwargs(self) -> dict:
        # Freshdesk's documented scheme: the API key as user, any password.
        return {"auth": (self.api_key, "X")}

    def conversation_url(self, external_id: str) -> Optional[str]:
        return f"{self.base_url}/a/tickets/{external_id}"

    async def test_connection(self) -> None:
        await self._request("GET", "/api/v2/agents/me")

    @staticmethod
    def _status(raw: dict) -> str:
        if raw.get("spam"):
            return STATUS_SPAM
        return _STATUS_MAP.get(raw.get("status"), STATUS_ACTIVE)

    def _to_conversation(self, raw: dict) -> HelpdeskConversation:
        requester = raw.get("requester") or {}
        return HelpdeskConversation(
            external_id=str(raw["id"]),
            subject=raw.get("subject") or "",
            customer_email=requester.get("email"),
            customer_name=requester.get("name"),
            customer_id=str(raw["requester_id"]) if raw.get("requester_id") else None,
            status=self._status(raw),
            raw_status=_STATUS_NAMES.get(raw.get("status"), str(raw.get("status"))),
            updated_at=parse_iso(raw.get("updated_at")) or datetime.now(timezone.utc),
            mailbox_id=str(raw["group_id"]) if raw.get("group_id") else None,
        )

    async def list_conversations(self, updated_since: Optional[datetime]) -> List[HelpdeskConversation]:
        """Without `updated_since`, Freshdesk's list only covers the last
        30 days -- so the first sync asks from 2000 onwards."""
        since = (updated_since or datetime(2000, 1, 1, tzinfo=timezone.utc)).strftime("%Y-%m-%dT%H:%M:%SZ")
        conversations: List[HelpdeskConversation] = []
        page = 1
        while True:
            response = await self._request("GET", "/api/v2/tickets", params={
                "updated_since": since, "include": "requester", "per_page": PER_PAGE, "page": page,
                "order_by": "updated_at", "order_type": "asc",
            })
            batch = self._json(response)
            if not isinstance(batch, list) or not batch:
                break
            conversations.extend(self._to_conversation(raw) for raw in batch)
            if len(batch) < PER_PAGE:
                break
            page += 1
        return conversations

    async def get_status(self, external_id: str) -> Optional[str]:
        response = await self._raw("GET", f"/api/v2/tickets/{external_id}")
        if response.status_code == 404:
            return None
        data = self._json(self._check(response))
        if data.get("deleted"):
            return None
        return self._status(data)

    async def get_messages(self, external_id: str) -> List[HelpdeskMessage]:
        """The ticket's description is its first message; private notes
        stay in Freshdesk."""
        data = self._json(await self._request(
            "GET", f"/api/v2/tickets/{external_id}", params={"include": "conversations,requester"},
        ))
        requester = data.get("requester") or {}
        messages = [HelpdeskMessage(
            author=requester.get("name") or requester.get("email") or "",
            created_at=parse_iso(data.get("created_at")),
            body_html=data.get("description"), body_text=data.get("description_text"), from_customer=True,
        )]
        for entry in data.get("conversations") or []:
            if entry.get("private"):
                continue
            messages.append(HelpdeskMessage(
                author=entry.get("from_email") or "",
                created_at=parse_iso(entry.get("created_at")),
                body_html=entry.get("body"), body_text=entry.get("body_text"),
                from_customer=bool(entry.get("incoming")),
            ))
        return messages

    async def create_conversation(
        self, subject: str, customer_email: str, message: str, customer_name: Optional[str] = None,
    ) -> str:
        payload: Dict[str, object] = {
            "email": customer_email, "subject": subject, "description": message,
            "status": 2, "priority": 1, "source": 2,
        }
        if customer_name:
            payload["name"] = customer_name
        response = await self._request("POST", "/api/v2/tickets", json=payload)
        return str(self._json(response).get("id", ""))

    async def update_customer(
        self, customer_id: str, first_name: Optional[str] = None, last_name: Optional[str] = None,
    ) -> None:
        name = " ".join(p for p in (first_name, last_name) if p)
        if name:
            await self._request("PUT", f"/api/v2/contacts/{customer_id}", json={"name": name})
