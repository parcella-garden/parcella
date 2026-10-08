"""
Authentication for the public signup API (see app/routers/api_public.py).

This is a THIRD auth mechanism alongside the web UI's cookie sessions
(app/auth.py) and the member-facing REST API's JWT bearer tokens
(app/api_auth.py). Neither of those fit here: an external CMS plugin
(WordPress, TYPO3, Contao, ...) is a server-side script with no user to
log in as, so it needs a long-lived, installation-wide credential it can
send with every request -- the same shape as the ICS feed tokens in
app/ics_utils.py, and deliberately reusing that shape rather than
inventing a new one.

One shared token per installation, not per-plugin or per-CMS: simple,
matches the project's existing "one shared secret for a small trusted
club" stance (see get_or_create_ics_token), and is easy to document in
a single admin settings screen. Read endpoints (session/parcel listing)
stay unauthenticated -- see docs/module-public-api.md for why that split
is safe here, the same reasoning as the public community ICS feed.
"""
import secrets
from typing import Optional
from urllib.parse import urlsplit

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import ClubSetting

PUBLIC_API_TOKEN_SETTING_KEY = "public_signup_api_token"


async def get_or_create_public_api_token(db: AsyncSession) -> str:
    """Returns the installation's shared secret for the public signup API,
    generating one on first use."""
    result = await db.execute(select(ClubSetting).where(ClubSetting.key == PUBLIC_API_TOKEN_SETTING_KEY))
    entry = result.scalar_one_or_none()
    if entry and entry.value:
        return entry.value

    token = secrets.token_urlsafe(32)
    if entry:
        entry.value = token
    else:
        db.add(ClubSetting(
            key=PUBLIC_API_TOKEN_SETTING_KEY, value=token,
            description="Shared secret for the public signup API (CMS connectors)",
        ))
    await db.commit()
    return token


async def regenerate_public_api_token(db: AsyncSession) -> str:
    """Invalidates the current token and issues a new one. Any connector
    still using the old token starts failing immediately -- intentional,
    this is the way to cut off a leaked or retired integration."""
    token = secrets.token_urlsafe(32)
    result = await db.execute(select(ClubSetting).where(ClubSetting.key == PUBLIC_API_TOKEN_SETTING_KEY))
    entry = result.scalar_one_or_none()
    if entry:
        entry.value = token
    else:
        db.add(ClubSetting(
            key=PUBLIC_API_TOKEN_SETTING_KEY, value=token,
            description="Shared secret for the public signup API (CMS connectors)",
        ))
    await db.commit()
    return token


def verify_public_api_token(provided: Optional[str], actual: str) -> bool:
    if not provided:
        return False
    return secrets.compare_digest(provided, actual)


async def require_public_api_token(
    db: AsyncSession = Depends(get_db),
    x_parcella_api_token: Optional[str] = Header(None, alias="X-Parcella-API-Token"),
) -> None:
    """FastAPI dependency for the public write endpoint. Deliberately a
    custom header rather than the Authorization/Bearer scheme used by the
    member API -- this is a different, coarser-grained credential (one
    shared secret, not a per-user session) and keeping the header name
    distinct avoids any confusion between the two in logs or docs."""
    actual = await get_or_create_public_api_token(db)
    if not verify_public_api_token(x_parcella_api_token, actual):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid API token",
        )


# ---------------------------------------------------------------------------
# Website-origin allowlist for the plain-HTML-form endpoints
# (app/routers/api_public.py, ADR 0088) -- their stand-in for the token
# above, which a static website has nowhere secret to keep.
# ---------------------------------------------------------------------------

PUBLIC_FORM_ORIGINS_SETTING_KEY = "public_form_allowed_origins"


def normalize_origin(value: str) -> Optional[str]:
    """Reduces a URL to its origin -- https://Example.org/some/page becomes
    https://example.org -- or None for anything that isn't an absolute
    http(s) URL."""
    try:
        parts = urlsplit((value or "").strip())
    except ValueError:
        return None
    if parts.scheme not in ("http", "https") or not parts.hostname:
        return None
    return f"{parts.scheme}://{parts.netloc.lower()}"


async def allowed_form_origins(db: AsyncSession) -> set[str]:
    result = await db.execute(select(ClubSetting).where(ClubSetting.key == PUBLIC_FORM_ORIGINS_SETTING_KEY))
    entry = result.scalar_one_or_none()
    lines = (entry.value or "").split() if entry else []
    return {origin for origin in map(normalize_origin, lines) if origin}
