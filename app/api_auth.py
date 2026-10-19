"""
JWT authentication for the REST API.

Separate from the web UI's cookie-based session authentication (see
app/auth.py). The API uses classic bearer tokens in the Authorization
header.

Authorization is a separate concern from authentication: require_api_role
and its ready-made combinations (require_write_access, require_admin_api)
are a coarse, role-only check, still used by most API routers today.
require_api_permission is the fine-grained, Group-based alternative
(same rules app/permissions.py's require_permission() applies to the
HTML side) -- ADR 0070 starts migrating routers to it module by module,
tickets first; the two coexist until that migration is done.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from jwt import PyJWTError
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.database import get_db
from app.models import User, UserRole
from app.auth import verify_password
from app.i18n import t_for
from app.permissions import get_user_permissions, has_permission, is_full_access_user

JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_VALID_MINUTES = 60 * 24  # 24 Stunden

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token", auto_error=False)


def create_access_token(user_id: str, email: str) -> str:
    expiry = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_VALID_MINUTES)
    payload = {
        "sub": user_id,
        "email": email,
        "exp": expiry,
        "iat": datetime.now(timezone.utc),
        "type": "access",
    }
    return jwt.encode(payload, settings.secret_key, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "access":
            return None
        return payload
    except PyJWTError:
        return None


async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.email == email.lower()))
    user = result.scalar_one_or_none()
    if not verify_password(password, user.password_hash if user else None) or not user:
        return None
    if not user.is_active:
        return None
    return user


async def get_current_api_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Dependency for protected API endpoints. Requires a valid bearer token."""
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing authentication",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not token:
        raise unauthorized

    payload = decode_access_token(token)
    if not payload:
        raise unauthorized

    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise unauthorized

    return user


def require_api_role(*allowed_roles: UserRole):
    """Dependency factory: restricts endpoints to specific roles."""

    async def checker(user: User = Depends(get_current_api_user)) -> User:
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This action requires one of these roles: {', '.join(r.value for r in allowed_roles)}",
            )
        return user

    return checker


# Common combinations as ready-made dependencies
#
# TREASURER is deliberately NOT in this list (see ADR 0071, amending
# ADR 0041): the role itself grants nothing beyond the READONLY baseline
# anywhere else in the app (HTML side, app/permissions.py) -- write
# access for a treasurer-type user comes from Group membership
# (e.g. a grants_full_access group), same as any other non-admin/board
# user. Role alone no longer bypasses that.
require_write_access = require_api_role(UserRole.ADMIN, UserRole.BOARD)
require_admin_api = require_api_role(UserRole.ADMIN, UserRole.BOARD)


def require_api_permission(module: str, level: str):
    """
    API counterpart to app.permissions.require_permission() -- consults
    the same Group-derived get_user_permissions() the HTML side uses,
    instead of the coarser role-only require_api_role (ADR 0070).

    Can't reuse request.state.permissions: it's populated by
    permissions_middleware (app/main.py) from get_current_user(), which
    only reads the session cookie -- always the anonymous baseline for
    a JWT-authenticated API request. Computes it directly per request
    instead.
    """
    async def checker(
        request: Request,
        user: User = Depends(get_current_api_user),
        db: AsyncSession = Depends(get_db),
    ) -> User:
        permissions = await get_user_permissions(db, user)
        if not has_permission(permissions, module, level):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=t_for(request, "errors.no_permission"))
        return user

    return checker


async def require_api_full_access(
    request: Request,
    user: User = Depends(get_current_api_user),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    API counterpart to app.auth.require_admin -- Group-aware full-access
    check (ADMIN/BOARD role, or membership in a grants_full_access/
    grants_system_admin group, ADR 0041), NOT the coarser role-only
    require_admin_api. First use: purchase_requests' approve/reject
    (ADR 0070/0071 rollout), where HTML's require_admin already let a
    grants_full_access group member act but the API's role-only
    require_vorstand_api did not -- the reverse-direction version of
    TREASURER's blanket-API-write bug (ADR 0071): here the API was
    *stricter* than HTML, not looser.
    """
    if not await is_full_access_user(db, user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=t_for(request, "errors.no_permission"))
    return user
