"""
Auth router: login, logout, invitations.
"""
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Request, Form, Depends, HTTPException, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import User, Invitation, InvitationStatus, UserRole, GroupMembership
from app.auth import (
    verify_password, hash_password, create_session_token,
    verify_invitation_token, create_invitation_token, get_current_user, require_admin, require_user
)
from app.avatars import save_avatar_upload, remove_avatar_file
from app.config import settings
from app.i18n import t_for
from app.login_throttle import (
    login_is_throttled, record_failed_login, clear_login_failures,
)

router = APIRouter(prefix="/auth", tags=["auth"])
from app.templating import templates


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, db: AsyncSession = Depends(get_db)):
    user = await get_current_user(request, db)
    if user:
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse("auth/login.html", {"request": request})


@router.post("/login")
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    # Throttling comes first: an attempt that's already over the limit
    # must not even reach the password check (see app/login_throttle.py).
    if login_is_throttled(request, email):
        return templates.TemplateResponse(
            "auth/login.html",
            {"request": request, "error": t_for(request, "errors.too_many_login_attempts")},
            status_code=429,
        )

    result = await db.execute(select(User).where(User.email == email.lower()))
    user = result.scalar_one_or_none()

    if not verify_password(password, user.password_hash if user else None) or not user:
        record_failed_login(request, email)
        return templates.TemplateResponse(
            "auth/login.html",
            {"request": request, "error": t_for(request, "errors.invalid_credentials")},
            status_code=401,
        )

    if not user.is_active:
        return templates.TemplateResponse(
            "auth/login.html",
            {"request": request, "error": t_for(request, "errors.account_deactivated")},
            status_code=403,
        )

    clear_login_failures(request, email)

    # Update last login timestamp
    user.last_login = datetime.now(timezone.utc)
    await db.commit()

    token = create_session_token(user.id, user.session_version)
    response = RedirectResponse("/", status_code=302)
    response.set_cookie(
        "session",
        token,
        max_age=settings.session_max_age,
        httponly=True,
        samesite="lax",
        secure=not settings.is_development,
    )
    return response


@router.get("/logout")
async def logout():
    response = RedirectResponse("/auth/login", status_code=302)
    response.delete_cookie("session")
    return response


# ---------------------------------------------------------------------------
# Self-service password change (issue #149) -- any logged-in user, not
# just admins; gated by require_user, not require_admin/require_system_admin.
# ---------------------------------------------------------------------------

@router.get("/change-password", response_class=HTMLResponse)
async def change_password_page(request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_user(request, db)
    return templates.TemplateResponse("auth/change_password.html", {"request": request, "user": user})


@router.post("/change-password")
async def change_password(
    request: Request,
    current_password: str = Form(...),
    new_password: str = Form(...),
    new_password_confirm: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    user = await require_user(request, db)

    def _error(message: str):
        return templates.TemplateResponse(
            "auth/change_password.html",
            {"request": request, "user": user, "error": message},
            status_code=400,
        )

    if not user.password_hash or not verify_password(current_password, user.password_hash):
        return _error(t_for(request, "errors.current_password_incorrect"))

    if new_password != new_password_confirm:
        return _error(t_for(request, "errors.passwords_do_not_match"))

    if len(new_password) < 8:
        return _error(t_for(request, "errors.password_too_short"))

    if new_password == current_password:
        return _error(t_for(request, "errors.password_must_differ"))

    user.password_hash = hash_password(new_password)
    # Whatever forced the change (today: the bootstrap admin's default
    # password) is now resolved -- see app/main.py's
    # password_change_middleware.
    user.must_change_password = False
    # Ends every other session of this account (a stolen cookie included);
    # this browser gets a fresh cookie below so it stays logged in.
    user.session_version += 1
    await db.commit()

    response = templates.TemplateResponse(
        "auth/change_password.html",
        {"request": request, "user": user, "success": True},
    )
    response.set_cookie(
        "session",
        create_session_token(user.id, user.session_version),
        max_age=settings.session_max_age,
        httponly=True,
        samesite="lax",
        secure=not settings.is_development,
    )
    return response


# ---------------------------------------------------------------------------
# Self-service avatar upload (issue #150) -- any logged-in user, not just
# admins; same require_user gate as change-password above. Shares the
# storage/validation core in app/avatars.py with the admin-side upload on
# /admin/users/{id}/edit (app/routers/admin.py).
# ---------------------------------------------------------------------------

@router.post("/avatar")
async def upload_own_avatar(
    request: Request,
    avatar: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    user = await require_user(request, db)

    try:
        user.avatar_filename = await save_avatar_upload(user.id, avatar)
    except ValueError as e:
        return templates.TemplateResponse(
            "auth/change_password.html",
            {"request": request, "user": user, "avatar_error": str(e)},
            status_code=400,
        )

    await db.commit()
    return templates.TemplateResponse(
        "auth/change_password.html",
        {"request": request, "user": user, "avatar_success": True},
    )


@router.post("/avatar/remove")
async def remove_own_avatar(request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_user(request, db)
    remove_avatar_file(user.id)
    user.avatar_filename = None
    await db.commit()
    return RedirectResponse("/auth/change-password", status_code=302)


# ---------------------------------------------------------------------------
# Invitation system
# ---------------------------------------------------------------------------

@router.get("/invitation/{token}", response_class=HTMLResponse)
async def invitation_page(token: str, request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Invitation).where(
            Invitation.token == token,
            Invitation.status == InvitationStatus.PENDING,
        )
    )
    invitation = result.scalar_one_or_none()

    if not invitation or invitation.expires_at < datetime.now(timezone.utc):
        return templates.TemplateResponse(
            "auth/invitation_expired.html", {"request": request}
        )

    return templates.TemplateResponse(
        "auth/invitation.html",
        {"request": request, "token": token, "email": invitation.email},
    )


@router.post("/invitation/{token}")
async def invitation_accept(
    token: str,
    request: Request,
    name: str = Form(...),
    password: str = Form(...),
    password_confirm: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Invitation)
        .where(
            Invitation.token == token,
            Invitation.status == InvitationStatus.PENDING,
        )
        .options(selectinload(Invitation.target_groups))
    )
    invitation = result.scalar_one_or_none()

    if not invitation or invitation.expires_at < datetime.now(timezone.utc):
        return templates.TemplateResponse(
            "auth/invitation_expired.html", {"request": request}
        )

    if password != password_confirm:
        return templates.TemplateResponse(
            "auth/invitation.html",
            {
                "request": request,
                "token": token,
                "email": invitation.email,
                "error": t_for(request, "errors.passwords_do_not_match"),
            },
        )

    if len(password) < 8:
        return templates.TemplateResponse(
            "auth/invitation.html",
            {
                "request": request,
                "token": token,
                "email": invitation.email,
                "error": t_for(request, "errors.password_too_short"),
            },
        )

    # Create user
    user = User(
        email=invitation.email.lower(),
        name=name,
        password_hash=hash_password(password),
        role=invitation.role,
    )
    db.add(user)
    await db.flush()

    # ADR 0041: real access comes from whichever groups the invite targeted,
    # not from invitation.role (kept only as an inert default, see admin.py).
    for target in invitation.target_groups:
        db.add(GroupMembership(user_id=user.id, group_id=target.group_id))

    invitation.status = InvitationStatus.ACCEPTED
    await db.commit()

    session_token = create_session_token(user.id, user.session_version)
    response = RedirectResponse("/", status_code=302)
    response.set_cookie(
        "session",
        session_token,
        max_age=settings.session_max_age,
        httponly=True,
        samesite="lax",
        secure=not settings.is_development,
    )
    return response
