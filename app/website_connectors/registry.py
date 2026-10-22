"""
Which website connectors exist, which one is active, and how their
settings are stored (ADR 0104) -- one CMS at a time, through the shared
ProviderRegistry (app/provider_registry.py).

The ClubSetting `website_connector` holds the active connector's type,
or nothing. Each connector's fields live in `website_<type>_<field>`
ClubSettings and stay stored when another connector is chosen.

Adding a CMS: write a WebsiteConnector subclass and add it to the
registry below, plus its `website.connectors.<type>.*` translations.
"""
from typing import Dict, Optional, Type

from sqlalchemy.ext.asyncio import AsyncSession

from app.provider_registry import InvalidConnectorConfig, ProviderRegistry, clean_value  # noqa: F401
from app.website_connectors.base import WebsiteConnector
from app.website_connectors.markdown_folder import MarkdownFolderPublisher
from app.website_connectors.parcella_plugin import ParcellaPluginPublisher
from app.website_connectors.wordpress import WordPressPublisher

ACTIVE_CONNECTOR_KEY = "website_connector"

WEBSITE = ProviderRegistry(
    active_key=ACTIVE_CONNECTOR_KEY, setting_prefix="website", i18n_prefix="website.connectors",
    providers=(WordPressPublisher, MarkdownFolderPublisher, ParcellaPluginPublisher), label="website",
)

CONNECTORS: Dict[str, Type[WebsiteConnector]] = WEBSITE.providers


def setting_key(connector_type: str, field_key: str) -> str:
    return WEBSITE.setting_key(connector_type, field_key)


def get_connector_class(connector_type: Optional[str]) -> Optional[Type[WebsiteConnector]]:
    return WEBSITE.get_class(connector_type)


async def get_active_type(db: AsyncSession) -> Optional[str]:
    return await WEBSITE.get_active_type(db)


async def load_stored_values(db: AsyncSession, connector_type: str) -> Dict[str, Optional[str]]:
    return await WEBSITE.load_stored_values(db, connector_type)


async def load_config(db: AsyncSession, connector_type: str) -> Optional[dict]:
    return await WEBSITE.load_config(db, connector_type)


async def build_connector(db: AsyncSession, connector_type: str, config: dict) -> WebsiteConnector:
    return await WEBSITE.build(db, connector_type, config)


async def get_active_connector(db: AsyncSession) -> Optional[WebsiteConnector]:
    """The active, fully configured connector, ready to use -- or None.
    Raises BlogPublishError if it's configured but a dependency (e.g.
    cloud storage for the Markdown folder) is missing."""
    return await WEBSITE.get_active(db)


async def merged_config(db: AsyncSession, connector_type: str, submitted: Dict[str, Optional[str]]) -> dict:
    return await WEBSITE.merged_config(db, connector_type, submitted)


async def save_config(
    db: AsyncSession, connector_type: Optional[str], submitted: Dict[str, Optional[str]],
    allow_secrets: bool = True,
) -> None:
    await WEBSITE.save_config(db, connector_type, submitted, allow_secrets=allow_secrets)
