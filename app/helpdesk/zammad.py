"""
Zammad (https://zammad.org): open-source helpdesk with a complete REST
API -- every Parcella feature is available. Authenticated with an
access token (Profile -> Token Access) of an agent who may see the
configured group.
"""
from datetime import datetime, timezone
from typing import Dict, List, Optional

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.helpdesk.base import (
    ALL_CAPABILITIES, ConfigField, HelpdeskConversation, HelpdeskError, HelpdeskMessage, HttpHelpdeskProvider,
    STATUS_ACTIVE, STATUS_CLOSED, STATUS_DELETED, STATUS_PENDING, parse_iso,
)

PER_PAGE = 100

# Zammad's built-in state names; anything custom falls back to "active".
_STATE_MAP = {
    "new": STATUS_ACTIVE, "open": STATUS_ACTIVE,
    "pending reminder": STATUS_PENDING, "pending close": STATUS_PENDING,
    "closed": STATUS_CLOSED, "merged": STATUS_CLOSED,
    "removed": STATUS_DELETED,
}


class ZammadProvider(HttpHelpdeskProvider):
    type = "zammad"
    label = "Zammad"
    capabilities = ALL_CAPABILITIES
    config_fields = [
        ConfigField("base_url", kind="url", required=True, placeholder="https://support.example.org"),
        ConfigField("api_token", kind="secret", required=True, hint=True),
        ConfigField("group", required=True, default="Users", placeholder="Users", hint=True),
    ]

    def __init__(self, base_url: str, api_token: str, group: str = "Users", client: Optional[httpx.AsyncClient] = None):
        super().__init__(base_url, client)
        self.api_token = api_token
        self.group = group
        self._user_cache: Dict[int, dict] = {}

    @classmethod
    async def build(cls, config: dict, db: AsyncSession) -> "ZammadProvider":
        return cls(base_url=config["base_url"], api_token=config["api_token"], group=config.get("group") or "Users")

    def _auth(self) -> dict:
        return {"Authorization": f"Token token={self.api_token}"}

    def conversation_url(self, external_id: str) -> Optional[str]:
        return f"{self.base_url}/#ticket/zoom/{external_id}"

    async def test_connection(self) -> None:
        await self._request("GET", "/api/v1/users/me")

    async def _user(self, user_id: Optional[int]) -> dict:
        if not user_id:
            return {}
        if user_id not in self._user_cache:
            response = await self._raw("GET", f"/api/v1/users/{user_id}")
            self._user_cache[user_id] = self._json(response) if response.status_code == 200 else {}
        return self._user_cache[user_id]

    @staticmethod
    def _name(user: dict) -> Optional[str]:
        return " ".join(p for p in [user.get("firstname"), user.get("lastname")] if p) or None

    async def _to_conversation(self, raw: dict) -> HelpdeskConversation:
        customer = await self._user(raw.get("customer_id"))
        state = (raw.get("state") or "").lower() if isinstance(raw.get("state"), str) else ""
        return HelpdeskConversation(
            external_id=str(raw["id"]),
            subject=raw.get("title") or "",
            customer_email=customer.get("email"),
            customer_name=self._name(customer),
            customer_id=str(raw["customer_id"]) if raw.get("customer_id") else None,
            status=_STATE_MAP.get(state, STATUS_ACTIVE),
            raw_status=state or "open",
            updated_at=parse_iso(raw.get("updated_at")) or datetime.now(timezone.utc),
            mailbox_id=raw.get("group") if isinstance(raw.get("group"), str) else None,
            message_count=raw.get("article_count"),
        )

    async def list_conversations(self, updated_since: Optional[datetime]) -> List[HelpdeskConversation]:
        """Pages through /api/v1/tickets (expanded, so states and groups
        come as names) and keeps what changed since `updated_since`. Uses
        the plain list rather than /tickets/search, which needs
        Elasticsearch on the Zammad side to be reliable."""
        conversations: List[HelpdeskConversation] = []
        page = 1
        while True:
            response = await self._request(
                "GET", "/api/v1/tickets", params={"expand": "true", "page": page, "per_page": PER_PAGE},
            )
            batch = self._json(response)
            if not isinstance(batch, list) or not batch:
                break
            for raw in batch:
                changed = parse_iso(raw.get("updated_at"))
                if updated_since is None or changed is None or changed >= updated_since:
                    conversations.append(await self._to_conversation(raw))
            if len(batch) < PER_PAGE:
                break
            page += 1
        return conversations

    async def get_status(self, external_id: str) -> Optional[str]:
        response = await self._raw("GET", f"/api/v1/tickets/{external_id}", params={"expand": "true"})
        if response.status_code == 404:
            return None
        state = str(self._json(self._check(response)).get("state") or "").lower()
        status = _STATE_MAP.get(state, STATUS_ACTIVE)
        return None if status == STATUS_DELETED else status

    async def get_messages(self, external_id: str) -> List[HelpdeskMessage]:
        """Internal notes are left out: the transcript in Parcella shows
        what was exchanged with the customer."""
        response = await self._request("GET", f"/api/v1/ticket_articles/by_ticket/{external_id}")
        messages = []
        for article in self._json(response) or []:
            if article.get("internal"):
                continue
            is_html = (article.get("content_type") or "").startswith("text/html")
            messages.append(HelpdeskMessage(
                author=article.get("from") or "",
                created_at=parse_iso(article.get("created_at")),
                body_html=article.get("body") if is_html else None,
                body_text=None if is_html else article.get("body"),
                from_customer=(article.get("sender") or "").lower() == "customer",
            ))
        return messages

    async def _customer_id(self, email: str, name: Optional[str]):
        """Finds the customer by email address, or creates one with the
        visitor's name -- Zammad's own `guess:<email>` shortcut would
        create a nameless customer. Searches for the plain address (the
        `email:"..."` field syntax needs Elasticsearch, which small
        installations often don't run) and keeps only an exact match."""
        found = self._json(await self._request("GET", "/api/v1/users/search", params={"query": email, "limit": 10}))
        for user in found if isinstance(found, list) else []:
            if (user.get("email") or "").lower() == email.lower():
                return user["id"]
        first, _, last = (name or "").strip().partition(" ")
        response = await self._raw("POST", "/api/v1/users", json={
            "email": email, "firstname": first or email, "lastname": last, "roles": ["Customer"],
        })
        if response.status_code == 422:
            # Exists after all (the search missed it): let Zammad match it.
            return f"guess:{email}"
        return self._json(self._check(response))["id"]

    async def create_conversation(
        self, subject: str, customer_email: str, message: str, customer_name: Optional[str] = None,
    ) -> str:
        response = await self._request("POST", "/api/v1/tickets", json={
            "title": subject,
            "group": self.group,
            "customer_id": await self._customer_id(customer_email, customer_name),
            "article": {
                "subject": subject, "body": message, "content_type": "text/plain",
                "type": "web", "internal": False, "sender": "Customer",
                "from": f"{customer_name} <{customer_email}>" if customer_name else customer_email,
            },
        })
        return str(self._json(response).get("id", ""))

    async def update_customer(
        self, customer_id: str, first_name: Optional[str] = None, last_name: Optional[str] = None,
    ) -> None:
        payload = {k: v for k, v in (("firstname", first_name), ("lastname", last_name)) if v}
        if payload:
            await self._request("PUT", f"/api/v1/users/{customer_id}", json=payload)
