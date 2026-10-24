"""
Znuny / OTRS (https://www.znuny.org): open-source helpdesk, through its
GenericInterface "TicketConnector" web service. That web service has to
be imported once in Znuny (Admin -> Web Services -> Add -> Import) from
integrations/znuny/ParcellaTicketConnector.yml -- see the README there.

Znuny has no web-service operation for editing customer users, so name
sync isn't available.
"""
from datetime import datetime, timedelta, timezone
from typing import List, Optional

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.helpdesk.base import (
    CREATE, INBOX, READ, ConfigField, HelpdeskConversation, HelpdeskError, HelpdeskMessage,
    HttpHelpdeskProvider, STATUS_ACTIVE, STATUS_CLOSED, STATUS_DELETED, STATUS_PENDING,
)

# Znuny's state *types* -- stable across installations, unlike state names.
_STATE_TYPE_MAP = {
    "new": STATUS_ACTIVE, "open": STATUS_ACTIVE,
    "pending reminder": STATUS_PENDING, "pending auto": STATUS_PENDING,
    "closed": STATUS_CLOSED, "merged": STATUS_CLOSED,
    "removed": STATUS_DELETED,
}
# Znuny reports times in the server's local time zone without saying
# which; the incremental sync looks back this much further so a time-zone
# offset can never make it miss a change (upserts are idempotent).
SYNC_MARGIN = timedelta(days=1)
_BATCH = 50


def _parse_local(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
    except ValueError:
        return None


class ZnunyProvider(HttpHelpdeskProvider):
    type = "znuny"
    label = "Znuny"
    capabilities = frozenset({INBOX, READ, CREATE})
    web_url_field = "agent_url"
    config_fields = [
        ConfigField(
            "webservice_url", kind="url", required=True, hint=True,
            placeholder="https://helpdesk.example.org/otrs/nph-genericinterface.pl/Webservice/ParcellaTicketConnector",
        ),
        ConfigField("username", required=True, hint=True),
        ConfigField("password", kind="secret", required=True),
        ConfigField("queue", required=True, default="Raw", placeholder="Raw", hint=True),
        ConfigField("agent_url", kind="url", placeholder="https://helpdesk.example.org/otrs/index.pl", hint=True),
    ]

    def __init__(
        self, webservice_url: str, username: str, password: str, queue: str = "Raw",
        agent_url: str = "", client: Optional[httpx.AsyncClient] = None,
    ):
        super().__init__(webservice_url, client)
        self.username = username
        self.password = password
        self.queue = queue
        self.agent_url = (agent_url or "").rstrip("/")
        self._session_id: Optional[str] = None

    @classmethod
    async def build(cls, config: dict, db: AsyncSession) -> "ZnunyProvider":
        return cls(
            webservice_url=config["webservice_url"], username=config["username"], password=config["password"],
            queue=config.get("queue") or "Raw", agent_url=config.get("agent_url") or "",
        )

    @property
    def web_url(self) -> Optional[str]:
        return self.agent_url or None

    def conversation_url(self, external_id: str) -> Optional[str]:
        if not self.agent_url:
            return None
        return f"{self.agent_url}?Action=AgentTicketZoom;TicketID={external_id}"

    async def _credentials(self) -> dict:
        """A session id from SessionCreate -- the password itself is only
        ever sent once, in a POST body, never in a URL (GET requests carry
        their parameters in the query string, which web servers log)."""
        if self._session_id is None:
            data = self._unwrap(await self._raw(
                "POST", "/Session", json={"UserLogin": self.username, "Password": self.password},
            ))
            if not data.get("SessionID"):
                raise HelpdeskError("Znuny didn't return a session -- check the username and password.")
            self._session_id = data["SessionID"]
        return {"SessionID": self._session_id}

    def _unwrap(self, response: httpx.Response) -> dict:
        """The GenericInterface often answers errors with HTTP 200 and an
        `Error` object; treat both as failures."""
        data = self._json(self._check(response))
        error = data.get("Error") if isinstance(data, dict) else None
        if error:
            code = error.get("ErrorCode", "")
            # Only a failed login means wrong credentials; "NotAuthorized"
            # means the agent lacks rights (e.g. on the queue).
            if code.startswith("SessionCreate") or code.endswith("AuthFail"):
                raise HelpdeskError("Znuny rejected the credentials.")
            raise HelpdeskError(f"Znuny reported an error: {code} {error.get('ErrorMessage', '')}".strip())
        return data

    async def _get(self, path: str, **params) -> dict:
        return self._unwrap(await self._raw("GET", path, params={**(await self._credentials()), **params}))

    async def test_connection(self) -> None:
        await self._get("/Ticket", Limit=1)

    async def _tickets(self, ids: List[str], articles: bool) -> List[dict]:
        tickets: List[dict] = []
        for start in range(0, len(ids), _BATCH):
            data = await self._get(
                f"/Ticket/{','.join(ids[start:start + _BATCH])}",
                AllArticles=1 if articles else 0, DynamicFields=0,
            )
            tickets.extend(data.get("Ticket") or [])
        return tickets

    @staticmethod
    def _to_conversation(raw: dict) -> HelpdeskConversation:
        state_type = (raw.get("StateType") or "").lower()
        customer = raw.get("CustomerUserID") or ""
        return HelpdeskConversation(
            external_id=str(raw["TicketID"]),
            subject=raw.get("Title") or "",
            customer_email=customer if "@" in customer else None,
            customer_name=None,
            customer_id=customer or None,
            status=_STATE_TYPE_MAP.get(state_type, STATUS_ACTIVE),
            raw_status=raw.get("State") or state_type,
            updated_at=_parse_local(raw.get("Changed")) or datetime.now(timezone.utc),
            mailbox_id=raw.get("Queue"),
        )

    async def list_conversations(self, updated_since: Optional[datetime]) -> List[HelpdeskConversation]:
        params = {"Limit": 100000}
        if updated_since is not None:
            minutes = int((datetime.now(timezone.utc) - updated_since + SYNC_MARGIN).total_seconds() // 60) + 1
            params["TicketChangeTimeNewerMinutes"] = max(minutes, 1)
        ids = [str(i) for i in (await self._get("/Ticket", **params)).get("TicketID") or []]
        return [self._to_conversation(raw) for raw in await self._tickets(ids, articles=False)]

    async def get_status(self, external_id: str) -> Optional[str]:
        try:
            tickets = await self._tickets([external_id], articles=False)
        except HelpdeskError as e:
            if "TicketGet.AccessDenied" in str(e) or "NotValid" in str(e) or "TicketID" in str(e):
                return None
            raise
        if not tickets:
            return None
        status = _STATE_TYPE_MAP.get((tickets[0].get("StateType") or "").lower(), STATUS_ACTIVE)
        return None if status == STATUS_DELETED else status

    async def _ticket_with_articles(self, external_id: str) -> dict:
        tickets = await self._tickets([external_id], articles=True)
        if not tickets:
            raise HelpdeskError(f"Ticket {external_id} wasn't found in Znuny.")
        return tickets[0]

    async def get_messages(self, external_id: str) -> List[HelpdeskMessage]:
        """Only articles visible to the customer -- internal notes stay
        in Znuny."""
        ticket = await self._ticket_with_articles(external_id)
        messages = []
        for article in ticket.get("Article") or []:
            if str(article.get("IsVisibleForCustomer", "1")) != "1":
                continue
            is_html = (article.get("ContentType") or article.get("MimeType") or "").startswith("text/html")
            messages.append(HelpdeskMessage(
                author=article.get("From") or "",
                created_at=_parse_local(article.get("CreateTime")),
                body_html=article.get("Body") if is_html else None,
                body_text=None if is_html else article.get("Body"),
                from_customer=(article.get("SenderType") or "") == "customer",
            ))
        return messages

    async def create_conversation(
        self, subject: str, customer_email: str, message: str, customer_name: Optional[str] = None,
    ) -> str:
        data = self._unwrap(await self._raw("POST", "/Ticket", json={
            **(await self._credentials()),
            "Ticket": {
                "Title": subject, "Queue": self.queue, "State": "new", "PriorityID": 3,
                "CustomerUser": customer_email,
            },
            "Article": {
                "CommunicationChannel": "Internal", "SenderType": "customer", "IsVisibleForCustomer": 1,
                "Subject": subject, "Body": message, "ContentType": "text/plain; charset=utf8",
                "From": f"{customer_name} <{customer_email}>" if customer_name else customer_email,
            },
        }))
        return str(data.get("TicketID", ""))
