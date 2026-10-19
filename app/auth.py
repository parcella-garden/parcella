"""
Authentication: password hashing, sessions, invitation tokens.
"""
import secrets
import bcrypt
from datetime import datetime, timedelta, timezone
from typing import Optional

from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from fastapi import Request, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.models import User

serializer = URLSafeTimedSerializer(settings.secret_key)

INVITATION_VALID_DAYS = 7


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


# Checked instead when there is no hash to check against (unknown email,
# account without a password), so a failed login takes as long either way
# and its timing doesn't reveal which addresses have an account.
_DUMMY_HASH = bcrypt.hashpw(b"no-such-account", bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: Optional[str]) -> bool:
    if not hashed:
        bcrypt.checkpw(password.encode(), _DUMMY_HASH.encode())
        return False
    return bcrypt.checkpw(password.encode(), hashed.encode())


def create_invitation_token(email: str) -> str:
    # secrets.token_urlsafe guarantees two invitations to the same address
    # within the same second get different tokens (itsdangerous' own
    # timestamp only has second precision, so a plain email+timestamp
    # would otherwise be deterministically identical).
    nonce = secrets.token_urlsafe(8)
    return serializer.dumps(f"{email}:{nonce}", salt="einladung")


def verify_invitation_token(token: str, max_age: int = INVITATION_VALID_DAYS * 86400) -> Optional[str]:
    try:
        payload = serializer.loads(token, salt="einladung", max_age=max_age)
        email, _, _nonce = payload.rpartition(":")
        return email or payload  # backwards-compatible with older tokens without a nonce
    except (BadSignature, SignatureExpired):
        return None


def create_session_token(user_id: str, session_version: int = 0) -> str:
    return serializer.dumps(f"{user_id}:{session_version}", salt="session")


def verify_session_token(token: str) -> Optional[tuple[str, int]]:
    """(user_id, session_version), or None. A cookie from before session
    versions existed holds the bare user id and counts as version 0, so
    deploying this didn't log everyone out."""
    try:
        payload = serializer.loads(
            token, salt="session", max_age=settings.session_max_age
        )
    except (BadSignature, SignatureExpired):
        return None
    user_id, _, version = payload.partition(":")
    try:
        return user_id, int(version or 0)
    except ValueError:
        return None


async def get_current_user(request: Request, db: AsyncSession) -> Optional[User]:
    token = request.cookies.get("session")
    if not token:
        return None
    verified = verify_session_token(token)
    if not verified:
        return None
    user_id, session_version = verified
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user and (not user.is_active or user.session_version != session_version):
        return None
    return user


async def require_user(request: Request, db: AsyncSession) -> User:
    user = await get_current_user(request, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            headers={"Location": "/auth/login"}
        )
    return user


async def require_admin(request: Request, db: AsyncSession) -> User:
    """ADMIN/BOARD role, or membership in a grants_full_access group
    (ADR 0041): full read/write/delete on every club module (see
    app/permissions.py), but NOT the administration panel itself -- see
    require_system_admin for that. Reads the per-request cache
    permissions_middleware computed, falling back to a fresh check."""
    from app.permissions import is_full_access_user
    user = await require_user(request, db)
    is_full_access = getattr(request.state, "is_full_access", None)
    if is_full_access is None:
        is_full_access = await is_full_access_user(db, user)
    if not is_full_access:
        from app.i18n import t_for
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=t_for(request, "errors.no_permission"))
    return user


async def require_system_admin(request: Request, db: AsyncSession) -> User:
    """ADMIN role, or membership in a grants_system_admin group (ADR
    0041): the administration panel (users, groups, club settings,
    integrations, sample data) -- these are the people who administer
    the installation itself, not necessarily council members. BOARD
    (or an equivalent grants_full_access group) gets full access to
    every club module (require_admin above) but not this."""
    from app.permissions import is_system_admin_user
    user = await require_user(request, db)
    is_system_admin = getattr(request.state, "is_system_admin", None)
    if is_system_admin is None:
        is_system_admin = await is_system_admin_user(db, user)
    if not is_system_admin:
        from app.i18n import t_for
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=t_for(request, "errors.no_permission"))
    return user
