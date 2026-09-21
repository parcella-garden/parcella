"""
External task source connectors: lets a club pull cards from an
external kanban tool it already uses into Parcella's own task board
(app/deck_sync.py does the actual upsert-into-Task work; this module is
only the API client). Nextcloud Deck is the only source today; a future
second source (e.g. Trello) would be a new class implementing the same
TaskSyncProvider interface, not a change to this one -- see
docs/ADR/0086.

Structured the same way as app/cloud_storage.py's CloudStorageProvider/
NextcloudProvider: an injectable httpx.AsyncClient (tests use
httpx.MockTransport), a domain-specific error type, and a
load_configuration()/get_client() factory pair. Credentials (base URL,
username, app password) are stored per club in ClubSettings, configured
on Admin -> Integrations -- same place every other outbound connector's
credentials live -- with the app password Fernet-encrypted via
app.crypto_utils, and "empty field on save = leave unchanged".

Deliberately a SEPARATE set of ClubSetting keys from cloud storage's
(deck_base_url/deck_username/deck_app_password, not
nextcloud_base_url/nextcloud_username/nextcloud_app_password) even
though a club's Deck board and their cloud storage usually live on the
very same Nextcloud instance -- reusing cloud storage's credentials
here would quietly couple its deliberately backend-agnostic abstraction
(docs/module-cloud-storage.md) to a Nextcloud-specific feature. See
docs/ADR/0086 for the full reasoning.
"""
import logging
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from typing import List, Optional

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ClubSetting
from app.crypto_utils import decrypt, DecryptionError

logger = logging.getLogger(__name__)

DECK_API_PATH = "/index.php/apps/deck/api/v1.0"


class DeckError(Exception):
    """Raised for any failure talking to Nextcloud Deck -- network,
    auth, or an unexpected response shape. Callers turn this into a
    user-facing message (admin flash message, or a logged warning from
    the background poller)."""


@dataclass
class ExternalCard:
    id: str
    title: str
    description: Optional[str]
    due_date: Optional[date]
    archived: bool
    updated_at: datetime
    order: int = 0


@dataclass
class ExternalStack:
    id: str
    title: str
    order: int = 0
    cards: List[ExternalCard] = field(default_factory=list)


class TaskSyncProvider:
    """Interface every external task source connector implements.
    DeckTaskProvider is the only implementation today; a future second
    source would be a new class implementing the same methods, not a
    change to this one (same shape as app/cloud_storage.py's
    CloudStorageProvider)."""

    async def test_connection(self) -> None:
        """Raises the provider's own error type if the credentials or
        server aren't reachable/valid. Returns None on success."""
        raise NotImplementedError

    async def fetch_board(self, board_id: str) -> List[ExternalStack]:
        """Returns every stack on the given board, each with its cards
        already attached -- the normalized shape app/deck_sync.py syncs
        from, regardless of how a given provider's own API happens to
        nest boards/stacks/cards."""
        raise NotImplementedError


def _parse_deck_date(value) -> Optional[date]:
    """Deck's documented format for `duedate` is ISO-8601
    ("YYYY-MM-DDTHH:MM:SS+00:00" or with a trailing "Z"). Returns just
    the date -- Task.due_date is a plain Date column, this app has never
    tracked a due *time* for a task (app/models.py's Task)."""
    if not value:
        return None
    try:
        text = value[:-1] + "+00:00" if isinstance(value, str) and value.endswith("Z") else value
        return datetime.fromisoformat(text).date()
    except (ValueError, TypeError):
        logger.warning(f"Could not parse Deck due date {value!r}, leaving it unset.")
        return None


def _parse_deck_updated_at(raw: dict) -> datetime:
    """Deck's own "last modified" field for a card -- accepted in
    whichever shape the API actually returns it in (a Unix timestamp
    integer, or an ISO-8601 string; both are documented as having been
    used across Deck API versions), since this hasn't been verified
    against a live instance yet. Falls back to now() if neither parses,
    same defensive convention as app/freescout_sync.py's
    _parse_datetime -- a card that can't be timestamped is still synced,
    just without a useful incremental-sync high-water-mark for itself
    until its next real change."""
    value = raw.get("lastModified")
    if isinstance(value, (int, float)):
        try:
            return datetime.fromtimestamp(value, tz=timezone.utc)
        except (ValueError, OSError):
            pass
    elif isinstance(value, str) and value:
        try:
            text = value[:-1] + "+00:00" if value.endswith("Z") else value
            return datetime.fromisoformat(text)
        except ValueError:
            pass
    return datetime.now(timezone.utc)


class DeckTaskProvider(TaskSyncProvider):
    def __init__(
        self, base_url: str, username: str, app_password: str,
        client: Optional[httpx.AsyncClient] = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.app_password = app_password
        # Injectable for tests (httpx.MockTransport) -- no real
        # Nextcloud/Deck instance is reachable from Parcella's own
        # test/CI environment.
        self._client = client
        self._owns_client = client is None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=20.0, auth=(self.username, self.app_password))
        return self._client

    async def aclose(self) -> None:
        if self._owns_client and self._client is not None:
            await self._client.aclose()

    async def _request(self, method: str, path: str, **kwargs) -> httpx.Response:
        client = await self._get_client()
        # OCS-APIRequest is required on every Deck API call (Nextcloud's
        # own CSRF-bypass convention for non-browser clients), not just
        # OCS-namespaced endpoints -- see deck.readthedocs.io/en/latest/API/.
        headers = {"OCS-APIRequest": "true", "Content-Type": "application/json"}
        try:
            response = await client.request(
                method, f"{self.base_url}{DECK_API_PATH}{path}", headers=headers, **kwargs,
            )
        except httpx.HTTPError as e:
            raise DeckError(f"Could not reach {self.base_url}: {e}") from e

        if response.status_code == 401:
            raise DeckError(
                "Nextcloud rejected the credentials (401 Unauthorized). "
                "Check the username and app password."
            )
        if response.status_code == 404:
            raise DeckError(
                f"Not found (HTTP 404) on {self.base_url} -- check the base URL and "
                "that the Deck app is enabled for this user."
            )
        if response.status_code >= 400:
            raise DeckError(f"Deck returned HTTP {response.status_code}.")
        return response

    async def test_connection(self) -> None:
        await self._request("GET", "/boards")

    async def fetch_board(self, board_id: str) -> List[ExternalStack]:
        response = await self._request("GET", f"/boards/{board_id}/stacks")
        try:
            raw_stacks = response.json()
        except ValueError as e:
            raise DeckError(f"Could not parse Deck's response: {e}") from e
        if not isinstance(raw_stacks, list):
            raise DeckError("Unexpected response shape from Deck (expected a list of stacks).")
        return [self._parse_stack(s) for s in raw_stacks]

    def _parse_stack(self, raw: dict) -> ExternalStack:
        cards = [self._parse_card(c) for c in (raw.get("cards") or [])]
        return ExternalStack(
            id=str(raw["id"]), title=raw.get("title", ""), order=raw.get("order", 0), cards=cards,
        )

    def _parse_card(self, raw: dict) -> ExternalCard:
        return ExternalCard(
            id=str(raw["id"]),
            title=raw.get("title", ""),
            description=raw.get("description") or None,
            due_date=_parse_deck_date(raw.get("duedate")),
            archived=bool(raw.get("archived", False)),
            updated_at=_parse_deck_updated_at(raw),
            order=raw.get("order", 0),
        )


async def load_deck_configuration(db: AsyncSession) -> Optional[dict]:
    """Loads {base_url, username, app_password} from ClubSettings, or
    None if not (fully) configured yet. All three are required -- a
    partially-filled-in configuration is treated as "not configured"
    rather than attempted and failing confusingly (same convention as
    load_nextcloud_configuration)."""
    result = await db.execute(
        select(ClubSetting).where(
            ClubSetting.key.in_(["deck_base_url", "deck_username", "deck_app_password"])
        )
    )
    stored = {e.key: e.value for e in result.scalars().all() if e.value}

    base_url = stored.get("deck_base_url")
    username = stored.get("deck_username")
    try:
        app_password = decrypt(stored.get("deck_app_password"))
    except DecryptionError:
        logger.error(
            "Could not decrypt the stored Deck app password -- did SECRET_KEY change? "
            "Treating Deck sync as not configured until it's re-entered."
        )
        return None

    if not base_url or not username or not app_password:
        return None
    return {"base_url": base_url, "username": username, "app_password": app_password}


async def load_deck_board_id(db: AsyncSession) -> Optional[str]:
    """The single Deck board configured to sync from -- separate from
    load_deck_configuration() since a board can only be chosen after
    the connection itself works, and "credentials set but no board
    chosen yet" is a real, valid intermediate admin state."""
    return await db.scalar(select(ClubSetting.value).where(ClubSetting.key == "deck_board_id")) or None


async def get_deck_client(
    db: AsyncSession, client: Optional[httpx.AsyncClient] = None,
) -> Optional[DeckTaskProvider]:
    """Returns a configured DeckTaskProvider, or None if the club hasn't
    set up Deck credentials yet -- callers check for None rather than
    catching an exception for "not set up" (same convention as
    get_nextcloud_provider/get_freescout_client)."""
    config = await load_deck_configuration(db)
    if config is None:
        return None
    return DeckTaskProvider(
        base_url=config["base_url"], username=config["username"],
        app_password=config["app_password"], client=client,
    )
