from pydantic import model_validator
from pydantic_settings import BaseSettings
from typing import Optional

from app.secret_bootstrap import DEFAULT_SECRET_KEY, read_secret_file

# DEFAULT_SECRET_KEY is the built-in development fallback. It is published
# in a public repo, so an installation still running on it has forgeable
# session cookies (app/auth.py), forgeable API tokens (app/api_auth.py) and
# readable stored SMTP/Nextcloud/WordPress passwords (app/crypto_utils.py
# derives the Fernet key from it). Anything but ENVIRONMENT=development
# refuses to start with it -- see _reject_default_secret_key below.
#
# An empty SECRET_KEY means "use the generated key file" (ADR 0121): the
# published image's entrypoint creates /app/secrets/secret_key on first
# start, see app/secret_bootstrap.py.


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://parcella:changeme@localhost:5432/parcella"

    # Security
    secret_key: str = ""
    session_max_age: int = 60 * 60 * 8  # 8 hours

    # Environment
    environment: str = "development"

    # Email
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = "noreply@parcella.local"
    smtp_tls: bool = True

    # App metadata
    app_name: str = "Parcella"
    app_version: str = "6.3.0"

    @property
    def is_development(self) -> bool:
        return self.environment == "development"

    @property
    def smtp_configured(self) -> bool:
        return bool(self.smtp_host and self.smtp_user)

    @model_validator(mode="after")
    def _resolve_secret_key(self) -> "Settings":
        """Empty SECRET_KEY: the generated key file, else the dev default
        (which _reject_default_secret_key then refuses outside development)."""
        if not self.secret_key.strip():
            self.secret_key = read_secret_file() or DEFAULT_SECRET_KEY
        return self

    @model_validator(mode="after")
    def _reject_default_secret_key(self) -> "Settings":
        """Fail fast instead of silently running a production install on
        the public default key. Documentation was previously the only
        thing standing between a `docker compose up` and forgeable admin
        sessions -- docker-compose.yml even passes this exact string as
        its SECRET_KEY fallback."""
        if not self.is_development and self.secret_key == DEFAULT_SECRET_KEY:
            raise ValueError(
                "SECRET_KEY is still the built-in development default, which is "
                f"published in Parcella's public repository. Set a real one for "
                f"ENVIRONMENT={self.environment!r}, e.g.:\n"
                "  SECRET_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(48))')\n"
                "or leave SECRET_KEY empty: the published image's entrypoint then "
                "generates one in ./data/secrets/secret_key.\n"
                "Note that changing SECRET_KEY later invalidates all sessions and "
                "makes already-encrypted settings (SMTP/Nextcloud/WordPress "
                "passwords) unreadable -- see docs/ADR/0006."
            )
        return self

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


settings = Settings()
