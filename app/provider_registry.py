"""
The "one dropdown, one provider at a time" pattern shared by every
pluggable integration: the website (ADR 0104), cloud storage (ADR 0106)
and, later, the helpdesk.

A ProviderRegistry knows the available provider classes of one kind,
which one is active (a single ClubSetting), and how each provider's
fields are stored (`<prefix>_<type>_<field>` ClubSettings). Switching
the active provider keeps every other provider's stored settings, so
switching back needs no retyping. Secrets are Fernet-encrypted
(app.crypto_utils); a blank secret on save means "keep the stored one",
the same convention as SMTP.

A provider class only needs:
- `type`: its key in the registry, e.g. "nextcloud";
- `config_fields`: a list of ConfigField;
- `async classmethod build(config, db)`: an instance from its decrypted
  configuration.
"""
import logging
from dataclasses import dataclass
from typing import Dict, Iterable, Optional, Type
from urllib.parse import urlsplit

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crypto_utils import DecryptionError, decrypt, encrypt
from app.models import ClubSetting

logger = logging.getLogger(__name__)


@dataclass
class ConfigField:
    """One setting a provider needs, rendered generically on Admin ->
    Integrations and in the REST API. `kind` is one of text, url, path,
    secret, list (comma-separated). Secrets are encrypted at rest and
    never shown or returned again. Labels come from the translation key
    `<i18n_prefix>.<type>.fields.<key>`; with `hint=True` also
    `<i18n_prefix>.<type>.hints.<key>`."""
    key: str
    kind: str = "text"
    required: bool = False
    default: str = ""
    placeholder: str = ""
    hint: bool = False


class InvalidConnectorConfig(ValueError):
    """A submitted value doesn't pass validation (bad URL, '..' in a path,
    unknown type). The message is shown to the admin."""


def _clean_path(value: str) -> str:
    # Imported here: app.parcel_cloud_folders imports app.cloud_storage,
    # which itself builds a ProviderRegistry.
    from app.parcel_cloud_folders import InvalidCloudPathError, sanitize_relative_path
    try:
        return sanitize_relative_path(value)
    except InvalidCloudPathError as e:
        raise InvalidConnectorConfig(str(e)) from e


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
        return _clean_path(value)
    if field.kind == "list":
        return ", ".join(part.strip() for part in value.split(",") if part.strip())
    if "\n" in value or "\r" in value:
        raise InvalidConnectorConfig("Line breaks aren't allowed here.")
    return value


class ProviderRegistry:
    def __init__(
        self, *, active_key: str, setting_prefix: str, i18n_prefix: str,
        providers: Iterable[type], label: str,
    ):
        self.active_key = active_key
        self.setting_prefix = setting_prefix
        self.i18n_prefix = i18n_prefix
        self.label = label
        self.providers: Dict[str, Type] = {p.type: p for p in providers}

    # -- lookup ------------------------------------------------------------

    def setting_key(self, provider_type: str, field_key: str) -> str:
        return f"{self.setting_prefix}_{provider_type}_{field_key}"

    def get_class(self, provider_type: Optional[str]) -> Optional[Type]:
        return self.providers.get(provider_type or "")

    async def _settings(self, db: AsyncSession, keys) -> Dict[str, Optional[str]]:
        result = await db.execute(select(ClubSetting).where(ClubSetting.key.in_(list(keys))))
        return {e.key: e.value for e in result.scalars().all()}

    async def get_active_type(self, db: AsyncSession) -> Optional[str]:
        stored = (await self._settings(db, [self.active_key])).get(self.active_key)
        return stored if stored in self.providers else None

    async def load_stored_values(self, db: AsyncSession, provider_type: str) -> Dict[str, Optional[str]]:
        """Raw stored values per field key (secrets still encrypted)."""
        cls = self.providers[provider_type]
        stored = await self._settings(db, [self.setting_key(provider_type, f.key) for f in cls.config_fields])
        return {f.key: stored.get(self.setting_key(provider_type, f.key)) for f in cls.config_fields}

    async def load_config(self, db: AsyncSession, provider_type: str) -> Optional[dict]:
        """Decrypted configuration with defaults applied, or None if a
        required field is missing or a secret can't be decrypted -- a
        half-configured provider counts as "not configured" rather than
        being attempted and failing confusingly."""
        cls = self.providers[provider_type]
        stored = await self.load_stored_values(db, provider_type)
        config = {}
        for f in cls.config_fields:
            value = stored.get(f.key) or ""
            if f.kind == "secret" and value:
                try:
                    value = decrypt(value) or ""
                except DecryptionError:
                    logger.error(
                        "Could not decrypt the stored %s %s secret %r -- did SECRET_KEY change? "
                        "Treating it as not configured until it's re-entered.",
                        self.label, provider_type, f.key,
                    )
                    return None
            value = value or f.default
            if f.required and not value:
                return None
            config[f.key] = value
        return config

    async def build(self, db: AsyncSession, provider_type: str, config: dict):
        return await self.providers[provider_type].build(config, db)

    async def get_active(self, db: AsyncSession):
        """The active, fully configured provider, ready to use -- or None."""
        provider_type = await self.get_active_type(db)
        if provider_type is None:
            return None
        config = await self.load_config(db, provider_type)
        if config is None:
            return None
        return await self.build(db, provider_type, config)

    # -- saving ------------------------------------------------------------

    def form_values(self, form, provider_type: str) -> dict:
        """The submitted fields of one provider from an admin form whose
        inputs are named like the ClubSettings."""
        return {
            f.key: form.get(self.setting_key(provider_type, f.key))
            for f in self.providers[provider_type].config_fields
            if self.setting_key(provider_type, f.key) in form
        }

    async def merged_config(self, db: AsyncSession, provider_type: str, submitted: Dict[str, Optional[str]]) -> dict:
        """Submitted values with blanks filled from the stored configuration
        -- what "Test connection" checks before anything is saved."""
        cls = self.providers[provider_type]
        stored = await self.load_config(db, provider_type) or {}
        config = {}
        for f in cls.config_fields:
            value = clean_value(f, submitted.get(f.key))
            config[f.key] = value or stored.get(f.key) or f.default
        if any(f.required and not config[f.key] for f in cls.config_fields):
            raise InvalidConnectorConfig("Please fill in all required fields first.")
        return config

    async def save_config(
        self, db: AsyncSession, provider_type: Optional[str], submitted: Dict[str, Optional[str]],
        allow_secrets: bool = True,
    ) -> None:
        """Makes `provider_type` the active provider (None = none) and
        stores its submitted fields. Other providers' stored settings are
        left alone. A blank secret keeps the stored one; with
        allow_secrets=False (the REST API) secrets are never written."""
        if provider_type is not None and provider_type not in self.providers:
            raise InvalidConnectorConfig(f"Unknown {self.label} type {provider_type!r}.")

        updates = {self.active_key: provider_type}
        if provider_type is not None:
            for f in self.providers[provider_type].config_fields:
                if f.key not in submitted:
                    continue
                value = clean_value(f, submitted.get(f.key))
                if f.kind == "secret":
                    if not value or not allow_secrets:
                        continue
                    value = encrypt(value)
                updates[self.setting_key(provider_type, f.key)] = value or None

        result = await db.execute(select(ClubSetting).where(ClubSetting.key.in_(list(updates))))
        entries = {e.key: e for e in result.scalars().all()}
        for key, value in updates.items():
            if key in entries:
                entries[key].value = value
            else:
                db.add(ClubSetting(key=key, value=value, description=f"{self.label} setting"))

    # -- admin page --------------------------------------------------------

    async def admin_context(self, db: AsyncSession) -> dict:
        """Everything the shared provider card template needs."""
        providers = []
        for provider_type, cls in self.providers.items():
            stored = await self.load_stored_values(db, provider_type)
            providers.append({
                "type": provider_type,
                "fields": [
                    {
                        "field": f,
                        "name": self.setting_key(provider_type, f.key),
                        "value": "" if f.kind == "secret" else (stored.get(f.key) or f.default),
                        "is_set": bool(stored.get(f.key)),
                    }
                    for f in cls.config_fields
                ],
            })
        return {
            "providers": providers,
            "active_type": await self.get_active_type(db),
            "i18n_prefix": self.i18n_prefix,
            "active_key": self.active_key,
        }
