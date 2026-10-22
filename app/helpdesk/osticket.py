"""
osTicket (https://osticket.com): open-source helpdesk whose official API
can only create tickets (POST /api/tickets.json) -- there is no endpoint
for listing, reading or answering them. With osTicket, the website
contact form creates tickets in it, and staff work in osTicket itself;
Parcella's Support page says so and links there (ADR 0107).

osTicket binds every API key to one client IP address (Admin Panel ->
Manage -> API Keys): it must be the address Parcella's server connects
from.
"""
from typing import Optional

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.helpdesk.base import CREATE, ConfigField, HelpdeskError, HttpHelpdeskProvider


class OsTicketProvider(HttpHelpdeskProvider):
    type = "osticket"
    label = "osTicket"
    capabilities = frozenset({CREATE})
    config_fields = [
        ConfigField("base_url", kind="url", required=True, placeholder="https://support.example.org", hint=True),
        ConfigField("api_key", kind="secret", required=True, hint=True),
    ]

    def __init__(self, base_url: str, api_key: str, client: Optional[httpx.AsyncClient] = None):
        super().__init__(base_url, client)
        self.api_key = api_key

    @classmethod
    async def build(cls, config: dict, db: AsyncSession) -> "OsTicketProvider":
        return cls(base_url=config["base_url"], api_key=config["api_key"])

    def _auth(self) -> dict:
        return {"X-API-Key": self.api_key}

    def conversation_url(self, external_id: str) -> Optional[str]:
        return f"{self.base_url}/scp/tickets.php?number={external_id}"

    async def test_connection(self) -> None:
        """osTicket has no read-only endpoint, so this posts an empty
        ticket: a valid key gets "400 missing fields" (nothing is
        created), an invalid key or wrong IP gets 401."""
        response = await self._raw("POST", "/api/tickets.json", json={})
        if response.status_code == 401:
            raise HelpdeskError(
                "osTicket rejected the API key. Check the key and that it's bound to this server's IP address."
            )
        if response.status_code == 404:
            raise HelpdeskError("No osTicket API at this address. Check the URL (without /api).")
        if response.status_code not in (400, 422):
            raise HelpdeskError(f"Unexpected answer from osTicket (HTTP {response.status_code}).")

    async def create_conversation(
        self, subject: str, customer_email: str, message: str, customer_name: Optional[str] = None,
    ) -> str:
        response = await self._raw("POST", "/api/tickets.json", json={
            "name": customer_name or customer_email,
            "email": customer_email,
            "subject": subject,
            "message": message,
            "source": "API",
        })
        if response.status_code == 401:
            raise HelpdeskError("osTicket rejected the API key.")
        if response.status_code != 201:
            raise HelpdeskError(f"osTicket didn't create the ticket (HTTP {response.status_code}): {response.text[:200]}")
        # osTicket answers with the new ticket's number as plain text.
        return response.text.strip()[:100]
