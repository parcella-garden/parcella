"""
API router: authentication (JWT token issuance).
"""
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api_auth import authenticate_user, create_access_token, ACCESS_TOKEN_VALID_MINUTES, get_current_api_user
from app.login_throttle import (
    login_is_throttled, record_failed_login, clear_login_failures,
)
from app.schemas import TokenResponse, LoginRequest, UserOut
from app.models import User

router = APIRouter(prefix="/api/v1/auth", tags=["API: Auth"])

_THROTTLED = HTTPException(
    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
    detail="Too many failed login attempts, please try again later.",
)
_BAD_CREDENTIALS = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Incorrect email or password, or account deactivated.",
)
# A user still on the bootstrap password has to change it in the web UI
# before the account is usable at all -- otherwise the forced change
# (app/main.py's request_context_middleware) would be a web-only gate
# that any API client could walk straight past.
_PASSWORD_CHANGE_REQUIRED = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="This account must set a new password in the web interface before the API can be used.",
)


async def _issue_token(request: Request, db: AsyncSession, email: str, password: str) -> TokenResponse:
    """Shared body of /token and /login: same throttling, same checks,
    same responses -- the two endpoints differ only in how the client
    encodes the credentials (form vs. JSON)."""
    if login_is_throttled(request, email):
        raise _THROTTLED

    user = await authenticate_user(db, email, password)
    if not user:
        record_failed_login(request, email)
        raise _BAD_CREDENTIALS

    if user.must_change_password:
        raise _PASSWORD_CHANGE_REQUIRED

    clear_login_failures(request, email)
    token = create_access_token(user.id, user.email)
    return TokenResponse(access_token=token, expires_in_minutes=ACCESS_TOKEN_VALID_MINUTES)


@router.post(
    "/token",
    response_model=TokenResponse,
    summary="Request access token",
    description=(
        "Authenticates with email and password and returns a JWT bearer token. "
        "Compatible with the OAuth2 password flow (for the Swagger UI \"Authorize\" button) AND "
        "with a JSON body (for programmatic clients, see /api/v1/auth/login)."
    ),
)
async def request_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    return await _issue_token(request, db, form_data.username, form_data.password)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Request access token (JSON)",
    description="Like /token, but with a JSON body instead of form data -- more convenient for most HTTP clients.",
)
async def login_json(
    daten: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    return await _issue_token(request, db, daten.email, daten.password)


@router.get(
    "/me",
    response_model=UserOut,
    summary="Retrieve own user profile",
)
async def get_own_profile(user: User = Depends(get_current_api_user)):
    return user
