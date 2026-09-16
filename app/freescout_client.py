"""
FreeScout API client: the only place in the codebase that talks HTTP to
FreeScout. Parcella no longer implements its own ticket/helpdesk system
(removed -- see docs/module-freescout-bridge.md and the ADR on this
decision); FreeScout is the sole, canonical system for support
conversations and email communication. This client is used by:

- app/freescout_sync.py (the poll loop, app/main.py) -- lists/fetches
  conversations and customers to build the local cross-reference
  (app.models.FreescoutConversationLink).
- app/services/members.py -- pushes member create/update as a FreeScout
  customer create/update (lazy: only once a member has actually been
  matched to a conversation, see docs/module-freescout-bridge.md).
- app/routers/freescout.py -- fetches a conversation's full thread live
  for the detail view, and posts replies/new conversations.
- app/routers/api_public.py's contact-form bridge -- creates a new
  FreeScout conversation directly from an external contact form.

Same connector shape as app/blog_publisher.py's WordPressPublisher and
app/cloud_storage.py's NextcloudProvider: an injectable httpx.AsyncClient
(tests use httpx.MockTransport), a domain-specific error type, and a
load_configuration()/get_client() factory pair. Credentials (base URL,
API key, mailbox ID) are stored per club in ClubSettings, configured on
the Admin -> Integrations page -- same place every other outbound
connector's credentials live -- with the API key Fernet-encrypted via
app.crypto_utils, and "empty field on save = leave unchanged."
"""
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ClubSetting
from app.crypto_utils import decrypt, DecryptionError

logger = logging.getLogger(__name__)

DEFAULT_MAILBOX_ID = 1


class FreeScoutError(Exception):
    """Raised for any failure talking to FreeScout -- network, auth, or
    an unexpected response shape. Callers turn this into a user-facing
    message without leaking the underlying detail (never log/return the
    API key itself -- it never appears in these messages to begin with,
    since it's sent as a header, not embedded in any URL/body we'd echo)."""


@dataclass
class FreeScoutCustomer:
    id: int
    email: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]


class FreeScoutClient:
    def __init__(
        self, base_url: str, api_key: str, mailbox_id: int = DEFAULT_MAILBOX_ID,
        client: Optional[httpx.AsyncClient] = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.mailbox_id = mailbox_id
        # Injectable for tests (httpx.MockTransport) -- no real FreeScout
        # instance is reachable from Parcella's own test/CI environment.
        self._client = client
        self._owns_client = client is None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=15.0)
        return self._client

    async def aclose(self) -> None:
        if self._owns_client and self._client is not None:
            await self._client.aclose()

    def _headers(self) -> dict:
        return {"X-FreeScout-API-Key": self.api_key}

    async def _request(self, method: str, path: str, **kwargs) -> httpx.Response:
        client = await self._get_client()
        try:
            response = await client.request(method, f"{self.base_url}{path}", headers=self._headers(), **kwargs)
        except httpx.HTTPError as e:
            raise FreeScoutError(f"Could not reach FreeScout: {e}") from e

        if response.status_code == 401:
            raise FreeScoutError("FreeScout rejected the API key (401 Unauthorized).")
        if response.status_code >= 400:
            raise FreeScoutError(f"FreeScout returned HTTP {response.status_code}: {response.text[:200]}")
        return response

    # -- Customers ----------------------------------------------------

    async def find_customer_by_email(self, email: str) -> Optional[FreeScoutCustomer]:
        response = await self._request("GET", "/api/customers", params={"email": email})
        items = response.json().get("_embedded", {}).get("customers", [])
        if not items:
            return None
        first = items[0]
        return FreeScoutCustomer(
            id=first["id"], email=email,
            first_name=first.get("firstName"), last_name=first.get("lastName"),
        )

    async def create_customer(
        self, email: str, first_name: Optional[str] = None, last_name: Optional[str] = None,
    ) -> FreeScoutCustomer:
        payload: Dict[str, Any] = {"emails": [email]}
        if first_name:
            payload["firstName"] = first_name
        if last_name:
            payload["lastName"] = last_name
        response = await self._request("POST", "/api/customers", json=payload)
        data = response.json()
        return FreeScoutCustomer(id=data["id"], email=email, first_name=first_name, last_name=last_name)

    async def update_customer(
        self, customer_id: int, first_name: Optional[str] = None, last_name: Optional[str] = None,
    ) -> None:
        payload: Dict[str, Any] = {}
        if first_name:
            payload["firstName"] = first_name
        if last_name:
            payload["lastName"] = last_name
        if not payload:
            return
        await self._request("PUT", f"/api/customers/{customer_id}", json=payload)

    # -- Conversations --------------------------------------------------

    async def list_conversations(
        self, mailbox_id: Optional[int] = None, updated_since: Optional[str] = None, page: int = 1,
    ) -> List[dict]:
        """`updated_since` is an ISO-8601 UTC string
        ("YYYY-MM-DDThh:mm:ssZ"), FreeScout's own required format."""
        params: Dict[str, Any] = {"mailboxId": mailbox_id or self.mailbox_id, "page": page}
        if updated_since:
            params["updatedSince"] = updated_since
        response = await self._request("GET", "/api/conversations", params=params)
        return response.json().get("_embedded", {}).get("conversations", [])

    async def get_conversation(self, conversation_id: int, embed: str = "threads") -> dict:
        response = await self._request("GET", f"/api/conversations/{conversation_id}", params={"embed": embed})
        return response.json()

    async def create_conversation(
        self, subject: str, customer_email: str, message: str,
        customer_name: Optional[str] = None, mailbox_id: Optional[int] = None,
    ) -> dict:
        customer: Dict[str, Any] = {"email": customer_email}
        if customer_name:
            customer["firstName"] = customer_name
        payload = {
            "type": "email",
            "mailboxId": mailbox_id or self.mailbox_id,
            "subject": subject,
            "customer": customer,
            "threads": [{"type": "customer", "text": message, "customer": customer}],
            "status": "active",
        }
        response = await self._request("POST", "/api/conversations", json=payload)
        return response.json()

    async def create_thread(self, conversation_id: int, text: str, by_user_id: Optional[str] = None) -> dict:
        """Posts a customer-facing reply (type="message") into an
        existing conversation -- FreeScout emails it out from there.
        `by_user_id` isn't sent to FreeScout (it has no concept of
        Parcella's users); it's accepted here only so callers can log
        who triggered the reply without a second lookup."""
        payload = {"type": "message", "text": text}
        response = await self._request("POST", f"/api/conversations/{conversation_id}/threads", json=payload)
        return response.json()


async def load_freescout_base_url(db: AsyncSession) -> Optional[str]:
    """Just the base URL (not the API key) -- cheap enough to load on
    every request for the nav link (see app/main.py's
    modul_flags_middleware), used by members with no freescout_bridge
    permission to link straight to FreeScout instead of Parcella's
    internal /freescout/ view."""
    value = await db.scalar(select(ClubSetting.value).where(ClubSetting.key == "freescout_base_url"))
    return value or None


async def load_freescout_configuration(db: AsyncSession) -> Optional[dict]:
    """Loads {base_url, api_key, mailbox_id} from ClubSettings, or None
    if not (fully) configured yet -- base_url and api_key are both
    required; mailbox_id falls back to DEFAULT_MAILBOX_ID (1) if unset,
    matching this module's documented default scope."""
    result = await db.execute(
        select(ClubSetting).where(
            ClubSetting.key.in_(["freescout_base_url", "freescout_api_key", "freescout_mailbox_id"])
        )
    )
    stored = {e.key: e.value for e in result.scalars().all() if e.value}

    base_url = stored.get("freescout_base_url")
    try:
        api_key = decrypt(stored.get("freescout_api_key"))
    except DecryptionError:
        logger.error(
            "Could not decrypt the stored FreeScout API key -- did SECRET_KEY change? "
            "Treating the FreeScout bridge as not configured until it's re-entered."
        )
        return None

    if not base_url or not api_key:
        return None

    try:
        mailbox_id = int(stored.get("freescout_mailbox_id") or DEFAULT_MAILBOX_ID)
    except ValueError:
        mailbox_id = DEFAULT_MAILBOX_ID

    return {"base_url": base_url, "api_key": api_key, "mailbox_id": mailbox_id}


async def get_freescout_client(
    db: AsyncSession, client: Optional[httpx.AsyncClient] = None,
) -> Optional[FreeScoutClient]:
    """Returns a configured FreeScoutClient, or None if the club hasn't
    set up FreeScout credentials yet -- callers check for None rather
    than catching an exception for "not set up" (same convention as
    get_wordpress_publisher/get_nextcloud_provider)."""
    config = await load_freescout_configuration(db)
    if config is None:
        return None
    return FreeScoutClient(
        base_url=config["base_url"], api_key=config["api_key"], mailbox_id=config["mailbox_id"], client=client,
    )
