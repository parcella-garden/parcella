"""
Zendesk Support (https://www.zendesk.com): commercial helpdesk with a
complete REST API -- every Parcella feature is available. Authenticated
with an agent's email address plus an API token (Admin Center -> Apps
and integrations -> Zendesk API).
"""
from datetime import datetime, timezone
from typing import Dict, List, Optional

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.helpdesk.base import (
    ALL_CAPABILITIES, ConfigField, HelpdeskConversation, HelpdeskError, HelpdeskMessage, HttpHelpdeskProvider,
    STATUS_ACTIVE, STATUS_CLOSED, STATUS_DELETED, STATUS_PENDING, parse_iso,
)

_STATUS_MAP = {
    "new": STATUS_ACTIVE, "open": STATUS_ACTIVE,
    "pending": STATUS_PENDING, "hold": STATUS_PENDING,
    "solved": STATUS_CLOSED, "closed": STATUS_CLOSED,
    "deleted": STATUS_DELETED,
}


class ZendeskProvider(HttpHelpdeskProvider):
    type = "zendesk"
    label = "Zendesk"
    capabilities = ALL_CAPABILITIES
    config_fields = [
        ConfigField("base_url", kind="url", required=True, placeholder="https://yourclub.zendesk.com"),
        ConfigField("agent_email", required=True, hint=True),
        ConfigField("api_token", kind="secret", required=True, hint=True),
    ]

    def __init__(self, base_url: str, agent_email: str, api_token: str, client: Optional[httpx.AsyncClient] = None):
        super().__init__(base_url, client)
        self.agent_email = agent_email
        self.api_token = api_token

    @classmethod
    async def build(cls, config: dict, db: AsyncSession) -> "ZendeskProvider":
        return cls(base_url=config["base_url"], agent_email=config["agent_email"], api_token=config["api_token"])

    def _auth_kwargs(self) -> dict:
        return {"auth": (f"{self.agent_email}/token", self.api_token)}

    def conversation_url(self, external_id: str) -> Optional[str]:
        return f"{self.base_url}/agent/tickets/{external_id}"

    async def test_connection(self) -> None:
        user = self._json(await self._request("GET", "/api/v2/users/me.json")).get("user") or {}
        # Zendesk answers wrong credentials with an anonymous user, not 401.
        if not user.get("id"):
            raise HelpdeskError("Zendesk didn't accept the email address and API token.")

    @staticmethod
    def _to_conversation(raw: dict, users: Dict[int, dict]) -> HelpdeskConversation:
        requester = users.get(raw.get("requester_id")) or {}
        status = raw.get("status") or "open"
        return HelpdeskConversation(
            external_id=str(raw["id"]),
            subject=raw.get("subject") or "",
            customer_email=requester.get("email"),
            customer_name=requester.get("name"),
            customer_id=str(raw["requester_id"]) if raw.get("requester_id") else None,
            status=_STATUS_MAP.get(status, STATUS_ACTIVE),
            raw_status=status,
            updated_at=parse_iso(raw.get("updated_at")) or datetime.now(timezone.utc),
            mailbox_id=str(raw["group_id"]) if raw.get("group_id") else None,
        )

    async def list_conversations(self, updated_since: Optional[datetime]) -> List[HelpdeskConversation]:
        """Zendesk's cursor-based incremental export, which also returns
        deleted tickets (status "deleted") and side-loads the requesters."""
        start = int(updated_since.timestamp()) if updated_since else 0
        params: Dict[str, object] = {"start_time": start, "include": "users"}
        conversations: List[HelpdeskConversation] = []
        while True:
            data = self._json(await self._request("GET", "/api/v2/incremental/tickets/cursor.json", params=params))
            users = {u["id"]: u for u in data.get("users") or [] if "id" in u}
            conversations.extend(self._to_conversation(raw, users) for raw in data.get("tickets") or [])
            if data.get("end_of_stream") or not data.get("after_cursor"):
                break
            params = {"cursor": data["after_cursor"], "include": "users"}
        return conversations

    async def get_status(self, external_id: str) -> Optional[str]:
        response = await self._raw("GET", f"/api/v2/tickets/{external_id}.json")
        if response.status_code == 404:
            return None
        status = _STATUS_MAP.get((self._json(self._check(response)).get("ticket") or {}).get("status"), STATUS_ACTIVE)
        return None if status == STATUS_DELETED else status

    async def get_messages(self, external_id: str) -> List[HelpdeskMessage]:
        """Public comments only -- internal notes stay in Zendesk."""
        data = self._json(await self._request(
            "GET", f"/api/v2/tickets/{external_id}/comments.json", params={"include": "users"},
        ))
        users = {u["id"]: u for u in data.get("users") or [] if "id" in u}
        messages = []
        for comment in data.get("comments") or []:
            if not comment.get("public", True):
                continue
            author = users.get(comment.get("author_id")) or {}
            messages.append(HelpdeskMessage(
                author=author.get("name") or author.get("email") or "",
                created_at=parse_iso(comment.get("created_at")),
                body_html=comment.get("html_body"), body_text=comment.get("plain_body") or comment.get("body"),
                from_customer=author.get("role") == "end-user",
            ))
        return messages

    async def reply(self, external_id: str, text: str) -> None:
        await self._request("PUT", f"/api/v2/tickets/{external_id}.json", json={
            "ticket": {"comment": {"body": text, "public": True}},
        })

    async def create_conversation(
        self, subject: str, customer_email: str, message: str, customer_name: Optional[str] = None,
    ) -> str:
        response = await self._request("POST", "/api/v2/tickets.json", json={"ticket": {
            "subject": subject,
            "comment": {"body": message},
            "requester": {"email": customer_email, "name": customer_name or customer_email},
        }})
        return str((self._json(response).get("ticket") or {}).get("id", ""))

    async def update_customer(
        self, customer_id: str, first_name: Optional[str] = None, last_name: Optional[str] = None,
    ) -> None:
        name = " ".join(p for p in (first_name, last_name) if p)
        if name:
            await self._request("PUT", f"/api/v2/users/{customer_id}.json", json={"user": {"name": name}})
