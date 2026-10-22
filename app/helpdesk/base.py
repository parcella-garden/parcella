"""
The interface every helpdesk provider implements (ADR 0107).

Parcella has no ticket system of its own (ADR 0080): support
conversations live in a helpdesk -- FreeScout, Zammad, Znuny/OTRS,
osTicket, Zendesk, Freshdesk -- chosen from a dropdown on Admin ->
Integrations, one at a time. Parcella keeps a lightweight
cross-reference (app.models.HelpdeskConversationLink) and talks to the
active helpdesk live for everything else.

Not every helpdesk's API can do everything. Each provider declares its
`capabilities`, and every caller checks before using a feature:

- INBOX: list conversations and their state (the Support list, the
  background sync, the nav badge, the dashboard card)
- READ: fetch a conversation's messages (the detail page transcript)
- REPLY: send a customer-facing reply
- CREATE: open a new conversation (the website contact form)
- CUSTOMER_SYNC: update a customer's name when a member is renamed

A missing capability means the feature is hidden or explained -- never
a broken button or a 500.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import FrozenSet, List, Optional

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.provider_registry import ConfigField  # noqa: F401  (re-exported for providers)

INBOX = "inbox"
READ = "read"
REPLY = "reply"
CREATE = "create"
CUSTOMER_SYNC = "customer_sync"
ALL_CAPABILITIES = frozenset({INBOX, READ, REPLY, CREATE, CUSTOMER_SYNC})

# Every provider maps its own states onto these. "deleted" is only ever
# set by Parcella's reconciliation (the conversation is gone).
STATUS_ACTIVE = "active"
STATUS_PENDING = "pending"
STATUS_CLOSED = "closed"
STATUS_SPAM = "spam"
STATUS_DELETED = "deleted"

# Statuses that are no longer actionable -- excluded from the staff-facing
# lists, the nav badge and the dashboard card, but still synced and kept up
# to date: a closed conversation that gets reopened must still have its
# already-matched member waiting for it (issue #230).
HIDDEN_STATUSES = (STATUS_CLOSED, STATUS_DELETED, STATUS_SPAM)


class HelpdeskError(Exception):
    """Raised for any failure talking to the helpdesk -- network, auth, or
    an unexpected response. Callers turn this into a user-facing message.
    Never contains a credential: keys and passwords travel in headers or
    bodies, never in anything echoed back."""


class CapabilityMissing(HelpdeskError):
    """The active helpdesk's API can't do this (e.g. osTicket has no
    endpoint for reading conversations)."""


@dataclass
class HelpdeskConversation:
    """One conversation as the sync stores it. `status` is one of the
    STATUS_* values; `raw_status` is the helpdesk's own word for it."""
    external_id: str
    subject: str
    customer_email: Optional[str]
    customer_name: Optional[str]
    customer_id: Optional[str]
    status: str
    raw_status: str
    updated_at: datetime
    mailbox_id: Optional[str] = None
    message_count: Optional[int] = None


@dataclass
class HelpdeskMessage:
    """One message of a conversation's transcript. `body_html` is
    untrusted (whoever emailed in) and is sanitized before rendering."""
    author: str
    created_at: Optional[datetime]
    body_html: Optional[str] = None
    body_text: Optional[str] = None
    from_customer: bool = False


class HelpdeskProvider:
    """Base class. A new helpdesk is one subclass plus one entry in
    app/helpdesk/registry.py -- no change to the routers or templates."""

    type: str = ""
    label: str = ""
    config_fields: List[ConfigField] = []
    capabilities: FrozenSet[str] = frozenset()
    # Which config field holds the address staff open in their browser
    # (the "Support" nav link and "Open in ..." buttons).
    web_url_field: str = "base_url"

    @classmethod
    async def build(cls, config: dict, db: AsyncSession) -> "HelpdeskProvider":
        raise NotImplementedError

    def can(self, capability: str) -> bool:
        return capability in self.capabilities

    @property
    def web_url(self) -> Optional[str]:
        return None

    def conversation_url(self, external_id: str) -> Optional[str]:
        """Where a human opens this conversation in the helpdesk itself."""
        return None

    async def test_connection(self) -> None:
        raise NotImplementedError

    async def list_conversations(self, updated_since: Optional[datetime]) -> List[HelpdeskConversation]:
        """INBOX: every conversation changed since `updated_since` (all, if
        None), across all states and pages."""
        raise CapabilityMissing(f"{self.label} can't list conversations through its API.")

    async def get_status(self, external_id: str) -> Optional[str]:
        """INBOX: the conversation's current STATUS_* value, or None if it
        no longer exists."""
        raise CapabilityMissing(f"{self.label} can't report a conversation's state through its API.")

    async def get_messages(self, external_id: str) -> List[HelpdeskMessage]:
        """READ: the conversation's transcript, oldest first."""
        raise CapabilityMissing(f"{self.label} can't show conversations through its API.")

    async def reply(self, external_id: str, text: str) -> None:
        """REPLY: a customer-facing reply, sent by the helpdesk."""
        raise CapabilityMissing(f"{self.label} can't send replies through its API.")

    async def create_conversation(
        self, subject: str, customer_email: str, message: str, customer_name: Optional[str] = None,
    ) -> str:
        """CREATE: opens a new conversation from a customer; returns its id."""
        raise CapabilityMissing(f"{self.label} can't create conversations through its API.")

    async def update_customer(
        self, customer_id: str, first_name: Optional[str] = None, last_name: Optional[str] = None,
    ) -> None:
        """CUSTOMER_SYNC: renames an existing customer record."""
        raise CapabilityMissing(f"{self.label} can't update customers through its API.")

    async def aclose(self) -> None:
        """Releases network clients. Safe to call more than once."""


def parse_iso(value: Optional[str]) -> Optional[datetime]:
    """ISO-8601 with a "Z" or an offset, as most helpdesk APIs send it."""
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


class HttpHelpdeskProvider(HelpdeskProvider):
    """Shared plumbing for REST-based helpdesks: one httpx client
    (injectable, so tests can use httpx.MockTransport), uniform error
    messages, and no credential ever ending up in one."""

    def __init__(self, base_url: str, client: Optional[httpx.AsyncClient] = None):
        self.base_url = base_url.rstrip("/")
        self._client = client
        self._owns_client = client is None

    @property
    def web_url(self) -> Optional[str]:
        return self.base_url

    def _auth(self) -> dict:
        """Headers (and, via `_auth_kwargs`, httpx auth) for every request."""
        return {}

    def _auth_kwargs(self) -> dict:
        return {}

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=20.0)
        return self._client

    async def aclose(self) -> None:
        if self._owns_client and self._client is not None:
            await self._client.aclose()
            self._client = None

    async def _raw(self, method: str, path: str, **kwargs) -> httpx.Response:
        client = await self._get_client()
        headers = {**self._auth(), **kwargs.pop("headers", {})}
        url = path if path.startswith(("http://", "https://")) else f"{self.base_url}{path}"
        try:
            return await client.request(method, url, headers=headers, **self._auth_kwargs(), **kwargs)
        except httpx.HTTPError as e:
            raise HelpdeskError(f"Could not reach {self.label}: {e}") from e

    def _check(self, response: httpx.Response) -> httpx.Response:
        if response.status_code in (401, 403):
            raise HelpdeskError(f"{self.label} rejected the credentials (HTTP {response.status_code}).")
        if response.status_code >= 400:
            raise HelpdeskError(f"{self.label} returned HTTP {response.status_code}: {response.text[:200]}")
        return response

    async def _request(self, method: str, path: str, **kwargs) -> httpx.Response:
        return self._check(await self._raw(method, path, **kwargs))

    @staticmethod
    def _json(response: httpx.Response):
        try:
            return response.json()
        except ValueError as e:
            raise HelpdeskError("The helpdesk's answer isn't valid JSON.") from e
