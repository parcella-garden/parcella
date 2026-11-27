"""Personal API tokens of all users."""
from fastapi import APIRouter
from fastapi import Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import User
from app.auth import require_system_admin
from app.permissions import is_full_access_user
from app.services import api_tokens
from app.services.errors import ServiceError
from app.i18n import t_for
from app.config import settings
from app.templating import templates

router = APIRouter()


# ---------------------------------------------------------------------------
# Personal API tokens, admin view (issue #306, ADR 0126): every user's
# tokens, revocable here; and creating one for another account, e.g. a
# dedicated integration user ("KI-Assistent", #307) that never logs in
# itself. Not for another full-access account: a token is silent, so it
# would let one admin act as another unnoticed.
# ---------------------------------------------------------------------------

async def _admin_api_tokens_page(request, db, admin, *, error=None, status_code=200):
    tokens = await api_tokens.list_tokens(db)
    new_token, new_token_row = api_tokens.read_new_token(request, tokens)
    new_token_user = new_token_row.user if new_token_row is not None else None
    users = (await db.execute(select(User).where(User.is_active.is_(True)).order_by(User.name))).scalars().all()
    eligible = [u for u in users if u.id == admin.id or not await is_full_access_user(db, u)]
    response = templates.TemplateResponse(
        request, "auth/api_tokens.html",
        {
            "request": request, "user": admin, "admin_view": True,
            "rows": [(tok, api_tokens.token_status(tok, tok.user)) for tok in tokens],
            "new_token": new_token, "new_token_user": new_token_user, "error": error,
            "expiry_choices": api_tokens.EXPIRY_CHOICES_DAYS,
            "default_expiry": api_tokens.DEFAULT_EXPIRY_DAYS,
            "form_action": "/admin/api-tokens",
            "eligible_users": eligible,
        },
        status_code=status_code,
    )
    response.headers["Cache-Control"] = "no-store"
    api_tokens.clear_new_token_cookie(request, response, "/admin/api-tokens")
    return response


@router.get("/api-tokens", response_class=HTMLResponse)
async def admin_api_tokens(request: Request, db: AsyncSession = Depends(get_db)):
    admin = await require_system_admin(request, db)
    return await _admin_api_tokens_page(request, db, admin)


@router.post("/api-tokens", response_class=HTMLResponse)
async def admin_api_token_create(
    request: Request,
    user_id: str = Form(""),
    name: str = Form(""),
    expires_in: str = Form(""),
    mcp_only: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    admin = await require_system_admin(request, db)
    target = (await db.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
    try:
        if target is None:
            raise ServiceError("errors.user_not_found", http_status=404)
        if target.id != admin.id and await is_full_access_user(db, target):
            raise ServiceError("api_tokens.errors.not_for_full_access_user", http_status=403)
        days = api_tokens.parse_expiry_days(expires_in)
        _, raw = await api_tokens.create_token(db, target, name, days, created_by=admin, mcp_only=mcp_only == "true")
    except ServiceError as e:
        return await _admin_api_tokens_page(
            request, db, admin, error=t_for(request, e.key, **e.params), status_code=e.http_status,
        )
    # Post/Redirect/Get, see the user-side handler in app/routers/auth.py.
    response = RedirectResponse("/admin/api-tokens", status_code=303)
    api_tokens.set_new_token_cookie(response, raw, "/admin/api-tokens", secure=not settings.is_development)
    return response


@router.post("/api-tokens/{token_id}/revoke")
async def admin_api_token_revoke(token_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    await require_system_admin(request, db)
    try:
        token = await api_tokens.get_token(db, token_id)
    except ServiceError:
        raise HTTPException(status_code=404, detail=t_for(request, "api_tokens.errors.not_found"))
    await api_tokens.revoke_token(db, token)
    return RedirectResponse("/admin/api-tokens", status_code=302)
