"""
Which website connectors exist, which one is active, and how their
settings are stored (ADR 0104).

One CMS at a time: the ClubSetting `website_connector` holds the active
connector's type, or nothing. Each connector's fields live in
`website_<type>_<field>` ClubSettings and stay stored when another
connector is chosen, so switching back needs no retyping. Secrets are
Fernet-encrypted (app.crypto_utils) and a blank secret on save means
"keep the stored one", the same convention as SMTP.

Adding a CMS: write a WebsiteConnector subclass and add it to
CONNECTORS below, plus its `website.connectors.<type>.*` translations.
"""
import logging
from typing import Dict, Optional, Type
from urllib.parse import urlsplit

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crypto_utils import DecryptionError, decrypt, encrypt
from app.models import ClubSetting
from app.website_connectors.base import BlogPublishError, ConfigField, WebsiteConnector
from app.website_connectors.markdown_folder import MarkdownFolderPublisher, validate_path
from app.website_connectors.parcella_plugin import ParcellaPluginPublisher
from app.website_connectors.wordpress import WordPressPublisher

logger = logging.getLogger(__name__)

ACTIVE_CONNECTOR_KEY = "website_connector"

CONNECTORS: Dict[str, Type[WebsiteConnector]] = {
    connector.type: connector
    for connector in (WordPressPublisher, MarkdownFolderPublisher, ParcellaPluginPublisher)
}


class InvalidConnectorConfig(ValueError):
    """A submitted value doesn't pass validation (bad URL, '..' in a path,
    missing required field). The message is shown to the admin."""


def setting_key(connector_type: str, field_key: str) -> str:
    return f"website_{connector_type}_{field_key}"


def get_connector_class(connector_type: Optional[str]) -> Optional[Type[WebsiteConnector]]:
    return CONNECTORS.get(connector_type or "")


async def _settings(db: AsyncSession, keys) -> Dict[str, Optional[str]]:
    result = await db.execute(select(ClubSetting).where(ClubSetting.key.in_(list(keys))))
    return {e.key: e.value for e in result.scalars().all()}


async def get_active_type(db: AsyncSession) -> Optional[str]:
    stored = (await _settings(db, [ACTIVE_CONNECTOR_KEY])).get(ACTIVE_CONNECTOR_KEY)
    return stored if stored in CONNECTORS else None


async def load_stored_values(db: AsyncSession, connector_type: str) -> Dict[str, Optional[str]]:
    """Raw stored values per field key (secrets still encrypted)."""
    cls = CONNECTORS[connector_type]
    stored = await _settings(db, [setting_key(connector_type, f.key) for f in cls.config_fields])
    return {f.key: stored.get(setting_key(connector_type, f.key)) for f in cls.config_fields}


async def load_config(db: AsyncSession, connector_type: str) -> Optional[dict]:
    """Decrypted configuration with defaults applied, or None if a
    required field is missing or a secret can't be decrypted -- a
    half-configured connector counts as "not configured" rather than
    being attempted and failing confusingly."""
    cls = CONNECTORS[connector_type]
    stored = await load_stored_values(db, connector_type)
    config = {}
    for f in cls.config_fields:
        value = stored.get(f.key) or ""
        if f.kind == "secret" and value:
            try:
                value = decrypt(value) or ""
            except DecryptionError:
                logger.error(
                    "Could not decrypt the stored %s secret %r -- did SECRET_KEY change? "
                    "Treating the website connector as not configured until it's re-entered.",
                    connector_type, f.key,
                )
                return None
        value = value or f.default
        if f.required and not value:
            return None
        config[f.key] = value
    return config


async def build_connector(db: AsyncSession, connector_type: str, config: dict) -> WebsiteConnector:
    return await CONNECTORS[connector_type].build(config, db)


async def get_active_connector(db: AsyncSession) -> Optional[WebsiteConnector]:
    """The active, fully configured connector, ready to use -- or None.
    Raises BlogPublishError if it's configured but a dependency (e.g.
    cloud storage for the Markdown folder) is missing."""
    connector_type = await get_active_type(db)
    if connector_type is None:
        return None
    config = await load_config(db, connector_type)
    if config is None:
        return None
    return await build_connector(db, connector_type, config)


def clean_value(field: ConfigField, raw: Optional[str]) -> str:
    """Normalizes and validates one submitted value."""
    value = (raw or "").strip()
    if not value:
        return ""
    if field.kind == "url":
        parts = urlsplit(value)
        if parts.scheme not in ("http", "https") or not parts.netloc:
            raise InvalidConnectorConfig(f"{value!r} isn't a valid http(s) address.")
        return value.rstrip("/")
    if field.kind == "path":
        try:
            return validate_path(value)
        except BlogPublishError as e:
            raise InvalidConnectorConfig(str(e)) from e
    if field.kind == "list":
        return ", ".join(part.strip() for part in value.split(",") if part.strip())
    if "\n" in value or "\r" in value:
        raise InvalidConnectorConfig("Line breaks aren't allowed here.")
    return value


async def merged_config(db: AsyncSession, connector_type: str, submitted: Dict[str, Optional[str]]) -> dict:
    """Submitted values with blanks filled from the stored configuration
    -- what "Test connection" checks before anything is saved."""
    cls = CONNECTORS[connector_type]
    stored = await load_config(db, connector_type) or {}
    config = {}
    for f in cls.config_fields:
        value = clean_value(f, submitted.get(f.key))
        config[f.key] = value or stored.get(f.key) or f.default
    missing = [f.key for f in cls.config_fields if f.required and not config[f.key]]
    if missing:
        raise InvalidConnectorConfig("Please fill in all required fields first.")
    return config


async def save_config(
    db: AsyncSession, connector_type: Optional[str], submitted: Dict[str, Optional[str]],
    allow_secrets: bool = True,
) -> None:
    """Makes `connector_type` the active connector (None = no website)
    and stores its submitted fields. Other connectors' stored settings
    are left alone. A blank secret keeps the stored one; with
    allow_secrets=False (the REST API) secrets are never written."""
    if connector_type is not None and connector_type not in CONNECTORS:
        raise InvalidConnectorConfig(f"Unknown website type {connector_type!r}.")

    updates = {ACTIVE_CONNECTOR_KEY: connector_type}
    if connector_type is not None:
        for f in CONNECTORS[connector_type].config_fields:
            if f.key not in submitted:
                continue
            value = clean_value(f, submitted.get(f.key))
            if f.kind == "secret":
                if not value or not allow_secrets:
                    continue
                value = encrypt(value)
            updates[setting_key(connector_type, f.key)] = value or None

    result = await db.execute(select(ClubSetting).where(ClubSetting.key.in_(list(updates))))
    entries = {e.key: e for e in result.scalars().all()}
    for key, value in updates.items():
        if key in entries:
            entries[key].value = value
        else:
            db.add(ClubSetting(key=key, value=value, description="Website connector setting"))
