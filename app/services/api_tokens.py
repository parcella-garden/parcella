"""
Personal API tokens (issue #306, ADR 0126).

A token is `pct_` + 43 random URL-safe characters (256 bits). Only its
SHA-256 is stored. A fast hash is enough here, unlike for passwords:
the input is random, not something a person chose, so there's nothing
to guess from a leaked hash. It also allows an indexed lookup by hash.

A token acts with exactly its user's permissions. It stops working when
it's revoked or expired, when its user is deactivated or has to set a
new password, and when the user's password changes (session_version,
same mechanism as the session cookie).
"""
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Tuple

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import ApiToken, User
from app.services.errors import ServiceError

TOKEN_PREFIX = "pct_"
NAME_MAX_LENGTH = 100
# Offered in the form; None = never expires.
EXPIRY_CHOICES_DAYS = (30, 90, 365, None)
DEFAULT_EXPIRY_DAYS = 365
# last_used_at is written at most this often per token, so a busy
# integration doesn't turn every API read into a database write.
LAST_USED_RESOLUTION = timedelta(minutes=5)

STATUS_ACTIVE = "active"
STATUS_EXPIRED = "expired"
STATUS_REVOKED = "revoked"
STATUS_INVALIDATED = "invalidated"  # password changed since


def looks_like_api_token(raw: Optional[str]) -> bool:
    return bool(raw) and raw.startswith(TOKEN_PREFIX)


def hash_token(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _now() -> datetime:
    return datetime.now(timezone.utc)


def parse_expiry_days(raw: Optional[str]) -> Optional[int]:
    """The form's select value: a number of days from EXPIRY_CHOICES_DAYS,
    or "never"."""
    value = (raw or "").strip()
    if value == "never":
        return None
    try:
        days = int(value)
    except ValueError:
        raise ServiceError("api_tokens.errors.invalid_expiry")
    if days not in EXPIRY_CHOICES_DAYS:
        raise ServiceError("api_tokens.errors.invalid_expiry")
    return days


async def create_token(
    db: AsyncSession, user: User, name: str, expires_in_days: Optional[int], created_by: User,
) -> Tuple[ApiToken, str]:
    """Creates a token for `user` and returns it with its plain value,
    which is never stored and can't be shown again. Commits."""
    clean_name = " ".join((name or "").split())
    if not clean_name:
        raise ServiceError("api_tokens.errors.name_required")
    if len(clean_name) > NAME_MAX_LENGTH:
        raise ServiceError("api_tokens.errors.name_too_long", max=NAME_MAX_LENGTH)
    if not user.is_active:
        raise ServiceError("api_tokens.errors.user_inactive")
    raw = TOKEN_PREFIX + secrets.token_urlsafe(32)
    token = ApiToken(
        user_id=user.id,
        name=clean_name,
        token_prefix=raw[: len(TOKEN_PREFIX) + 6],
        token_hash=hash_token(raw),
        session_version=user.session_version,
        created_by_id=created_by.id,
        expires_at=(_now() + timedelta(days=expires_in_days)) if expires_in_days else None,
    )
    db.add(token)
    await db.commit()
    return token, raw


def token_status(token: ApiToken, user: User, now: Optional[datetime] = None) -> str:
    now = now or _now()
    if token.revoked_at is not None:
        return STATUS_REVOKED
    if token.expires_at is not None and token.expires_at <= now:
        return STATUS_EXPIRED
    if token.session_version != user.session_version:
        return STATUS_INVALIDATED
    return STATUS_ACTIVE


async def authenticate(db: AsyncSession, raw: str) -> Optional[User]:
    """The user a token belongs to, or None if it's unknown or no longer
    valid. Updates last_used_at (coarsely) and commits that alone."""
    if not looks_like_api_token(raw):
        return None
    result = await db.execute(
        select(ApiToken).where(ApiToken.token_hash == hash_token(raw)).options(selectinload(ApiToken.user))
    )
    token = result.scalar_one_or_none()
    if token is None:
        return None
    user = token.user
    now = _now()
    if not user or not user.is_active or user.must_change_password:
        return None
    if token_status(token, user, now) != STATUS_ACTIVE:
        return None
    if token.last_used_at is None or now - token.last_used_at >= LAST_USED_RESOLUTION:
        await db.execute(update(ApiToken).where(ApiToken.id == token.id).values(last_used_at=now))
        await db.commit()
    return user


async def list_tokens(db: AsyncSession, user: Optional[User] = None) -> List[ApiToken]:
    """One user's tokens, or everyone's (user=None, admin view); newest first."""
    query = select(ApiToken).options(selectinload(ApiToken.user)).order_by(ApiToken.created_at.desc())
    if user is not None:
        query = query.where(ApiToken.user_id == user.id)
    return list((await db.execute(query)).scalars().all())


async def get_token(db: AsyncSession, token_id: str, owner: Optional[User] = None) -> ApiToken:
    """With `owner`, only that user's token: someone else's id is a 404,
    the same as an unknown one."""
    query = select(ApiToken).where(ApiToken.id == token_id).options(selectinload(ApiToken.user))
    if owner is not None:
        query = query.where(ApiToken.user_id == owner.id)
    token = (await db.execute(query)).scalar_one_or_none()
    if token is None:
        raise ServiceError("api_tokens.errors.not_found", http_status=404)
    return token


async def revoke_token(db: AsyncSession, token: ApiToken) -> None:
    """Ends the token at once. The row stays, marked revoked. Commits."""
    if token.revoked_at is None:
        token.revoked_at = _now()
        await db.commit()


# ---------------------------------------------------------------------------
# Showing a new token exactly once, across a redirect (Post/Redirect/Get).
# Answering the create POST with the page directly made F5 re-submit the
# form and silently mint another token. So the POST redirects, and the raw
# token rides along in a short-lived cookie: HttpOnly, SameSite=Strict,
# scoped to the tokens page, deleted on the first read. It never goes into
# a URL (history, logs, Referer). The page only shows a value whose hash
# matches a token in its own list, so a forged cookie displays nothing.
# ---------------------------------------------------------------------------

NEW_TOKEN_COOKIE = "new_api_token"
NEW_TOKEN_COOKIE_MAX_AGE = 120  # seconds; just long enough for the redirect


def set_new_token_cookie(response, raw: str, path: str, secure: bool) -> None:
    response.set_cookie(
        NEW_TOKEN_COOKIE, raw, max_age=NEW_TOKEN_COOKIE_MAX_AGE, path=path,
        httponly=True, samesite="strict", secure=secure,
    )


def read_new_token(request, tokens: List[ApiToken]) -> Tuple[Optional[str], Optional[ApiToken]]:
    """Return (raw, token) from the one-time cookie, only if the raw value
    belongs to one of `tokens`. The caller deletes the cookie on its
    response with clear_new_token_cookie()."""
    raw = request.cookies.get(NEW_TOKEN_COOKIE)
    if not looks_like_api_token(raw):
        return None, None
    digest = hash_token(raw)
    for token in tokens:
        if token.token_hash == digest:
            return raw, token
    return None, None


def clear_new_token_cookie(request, response, path: str) -> None:
    if NEW_TOKEN_COOKIE in request.cookies:
        response.delete_cookie(NEW_TOKEN_COOKIE, path=path, httponly=True, samesite="strict")
