"""Users and invitations: list, invite, edit, reset password, avatar, deactivate, delete."""
import urllib.parse
from fastapi import APIRouter
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models import (
    Group,
    GroupMembership,
    Invitation,
    InvitationGroupTarget,
    InvitationStatus,
    User,
    UserRole,
)
from app.auth import (
    create_invitation_token,
    generate_temporary_password,
    hash_password,
    require_system_admin,
)
from app.permissions import is_last_admin
from app.email_service import send_email
from app.i18n import t_for
from app.avatars import remove_avatar_file, save_avatar_upload
from app.config import settings
from app.templating import templates
from app.services.admin import user_has_history

router = APIRouter()


INVITATION_DAYS = 7


@router.get("/")
async def admin_root_redirect():
    """Issue #145: the user-management page moved from the bare /admin/
    to /admin/users/, matching every other admin sub-page's own path
    (Groups, Settings, Integrations, ...). Kept as a redirect so old
    bookmarks/links still land somewhere sensible."""
    return RedirectResponse("/admin/users/", status_code=302)


@router.get("/users/", response_class=HTMLResponse)
async def admin_dashboard(request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_system_admin(request, db)

    user_result = await db.execute(select(User).order_by(User.name))
    all_users = user_result.scalars().all()

    invitation_result = await db.execute(
        select(Invitation)
        .where(Invitation.status == InvitationStatus.PENDING)
        .options(selectinload(Invitation.target_groups).selectinload(InvitationGroupTarget.group))
        .order_by(Invitation.created_at.desc())
    )
    open_invitations = invitation_result.scalars().all()

    groups_result = await db.execute(select(Group).order_by(Group.name))
    all_groups = groups_result.scalars().all()

    membership_result = await db.execute(
        select(GroupMembership).options(selectinload(GroupMembership.group))
    )
    # Groups shown in the user list (issue #129: group membership is the
    # real access mechanism for non-legacy accounts, per ADR 0041, so it
    # replaces the "role" column there rather than sitting alongside it).
    user_group_names: dict[str, list[str]] = {}
    for membership in membership_result.scalars().all():
        user_group_names.setdefault(membership.user_id, []).append(membership.group.name)

    return templates.TemplateResponse(
        request, "admin/dashboard.html",
        {
            "request": request,
            "user": user,
            "all_users": all_users,
            "open_invitations": open_invitations,
            "all_groups": all_groups,
            "user_group_names": user_group_names,
            "UserRole": UserRole,
        },
    )


async def _send_invitation_email(request: Request, admin: User, invitation: Invitation, db: AsyncSession) -> bool:
    """Sends (or re-sends) the invitation email for an existing Invitation
    row. Returns whether an email was actually sent (see the dev-mode
    fallback in user_invite/invitation_resend, which show the link
    directly instead when SMTP isn't configured)."""
    base_url = str(request.base_url).rstrip("/")
    invitation_link = f"{base_url}/auth/invitation/{invitation.token}"

    subject = t_for(request, "email.invitation.subject", app_name=settings.app_name)
    html = f"""
    <html><body style="font-family: sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
    <h2>{t_for(request, "email.invitation.heading", app_name=settings.app_name)}</h2>
    <p>{t_for(request, "email.invitation.intro", admin_name=f"<strong>{admin.name}</strong>")}</p>
    <p>{t_for(request, "email.invitation.instruction")}</p>
    <p style="margin: 20px 0;">
        <a href="{invitation_link}" style="background: #2d6a4f; color: white; padding: 10px 20px;
           text-decoration: none; border-radius: 4px;">{t_for(request, "email.invitation.button")}</a>
    </p>
    <p style="color: #666; font-size: 0.9em;">
        {t_for(request, "email.invitation.validity", days=INVITATION_DAYS)}<br>
        {t_for(request, "email.invitation.fallback", link=invitation_link)}
    </p>
    </body></html>
    """
    return await send_email(invitation.email, subject, html, db=db)


def _invitation_send_failed(request: Request, email: str) -> RedirectResponse:
    """The invitation row is saved either way (its link works); only the
    email didn't go out. Say so, and where to look (issue #359)."""
    message = t_for(request, "errors.invitation_send_failed", email=email)
    return RedirectResponse(f"/admin/users/?error={urllib.parse.quote(message)}", status_code=302)


@router.post("/invite")
async def user_invite(
    request: Request,
    email: str = Form(...),
    group_ids: list[str] = Form([]),
    db: AsyncSession = Depends(get_db),
):
    """ADR 0041: invites assign group(s), not a role -- the new User is
    always created with role=READONLY (inert, real access comes from
    whichever groups were selected here, applied on acceptance in
    routers/auth.py)."""
    admin = await require_system_admin(request, db)

    email = email.strip().lower()

    # Already registered?
    existing = await db.execute(select(User).where(User.email == email))
    if existing.scalar_one_or_none():
        return RedirectResponse(
            f"/admin/users/?error={urllib.parse.quote(t_for(request, 'errors.email_already_registered'))}",
            status_code=302,
        )

    # Already a pending invitation for this address? Then invalidate the
    # old one instead of letting a second one exist in parallel
    # (otherwise the new token can, in rare cases, collide with the old
    # one if both are generated within the same second, and the insert
    # fails with a hard database error instead of an understandable message).
    pending = await db.execute(
        select(Invitation).where(
            Invitation.email == email,
            Invitation.status == InvitationStatus.PENDING,
        )
    )
    for old_invitation in pending.scalars().all():
        old_invitation.status = InvitationStatus.EXPIRED

    valid_group_ids = set()
    if group_ids:
        existing_groups = await db.execute(select(Group.id).where(Group.id.in_(group_ids)))
        valid_group_ids = {row[0] for row in existing_groups.all()}

    token = create_invitation_token(email)
    expires_at = datetime.now(timezone.utc) + timedelta(days=INVITATION_DAYS)

    invitation = Invitation(
        email=email,
        token=token,
        role=UserRole.READONLY,
        invited_by_id=admin.id,
        expires_at=expires_at,
    )
    db.add(invitation)
    await db.flush()
    for group_id in valid_group_ids:
        db.add(InvitationGroupTarget(invitation_id=invitation.id, group_id=group_id))
    await db.commit()

    email_sent = await _send_invitation_email(request, admin, invitation, db)

    # In development mode: return the link in the URL
    if settings.is_development and not email_sent:
        base_url = str(request.base_url).rstrip("/")
        invitation_link = f"{base_url}/auth/invitation/{token}"
        return RedirectResponse(
            f"/admin/users/?info=Invitation+link+%28Dev%29%3A+{invitation_link}", status_code=302
        )

    if not email_sent:
        # Issue #359: this used to say "Invitation sent" even when SMTP refused it.
        return _invitation_send_failed(request, invitation.email)
    return RedirectResponse(
        f"/admin/users/?success={urllib.parse.quote(t_for(request, 'errors.invitation_sent'))}",
        status_code=302,
    )


@router.post("/invitations/{invitation_id}/resend")
async def invitation_resend(
    invitation_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Re-sends a pending invitation's email and extends its expiry --
    reuses the existing token (never cryptographically re-checked, see
    app/auth.py's verify_invitation_token; only Invitation.expires_at
    is actually enforced in routers/auth.py), so the old link keeps
    working rather than silently breaking once a new one is sent."""
    admin = await require_system_admin(request, db)

    result = await db.execute(
        select(Invitation).where(
            Invitation.id == invitation_id,
            Invitation.status == InvitationStatus.PENDING,
        )
    )
    invitation = result.scalar_one_or_none()
    if not invitation:
        return RedirectResponse(
            f"/admin/users/?error={urllib.parse.quote(t_for(request, 'errors.invitation_not_found'))}",
            status_code=302,
        )

    invitation.expires_at = datetime.now(timezone.utc) + timedelta(days=INVITATION_DAYS)
    await db.commit()

    email_sent = await _send_invitation_email(request, admin, invitation, db)

    if settings.is_development and not email_sent:
        base_url = str(request.base_url).rstrip("/")
        invitation_link = f"{base_url}/auth/invitation/{invitation.token}"
        return RedirectResponse(
            f"/admin/users/?info=Invitation+link+%28Dev%29%3A+{invitation_link}", status_code=302
        )

    if not email_sent:
        return _invitation_send_failed(request, invitation.email)
    return RedirectResponse(
        f"/admin/users/?success={urllib.parse.quote(t_for(request, 'errors.invitation_resent'))}",
        status_code=302,
    )


@router.post("/invitations/{invitation_id}/delete")
async def invitation_delete(
    invitation_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    await require_system_admin(request, db)

    result = await db.execute(select(Invitation).where(Invitation.id == invitation_id))
    invitation = result.scalar_one_or_none()
    if invitation:
        await db.delete(invitation)
        await db.commit()

    return RedirectResponse(
        f"/admin/users/?success={urllib.parse.quote(t_for(request, 'errors.invitation_deleted'))}",
        status_code=302,
    )


@router.post("/users/{user_id}/deactivate")
async def user_deactivate(
    user_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    admin = await require_system_admin(request, db)

    if user_id == admin.id:
        return RedirectResponse(
            f"/admin/users/?error={urllib.parse.quote(t_for(request, 'errors.own_account_cannot_deactivate'))}",
            status_code=302,
        )

    result = await db.execute(select(User).where(User.id == user_id))
    target = result.scalar_one_or_none()
    if target:
        if (
            target.is_active
            and target.role == UserRole.ADMIN
            and await is_last_admin(db, target.id)
        ):
            return RedirectResponse(
                f"/admin/users/?error={urllib.parse.quote(t_for(request, 'errors.cannot_remove_last_admin'))}",
                status_code=302,
            )
        target.is_active = not target.is_active
        await db.commit()

    return RedirectResponse("/admin/users/", status_code=302)


@router.get("/users/{user_id}/edit", response_class=HTMLResponse)
async def user_edit_page(
    user_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    admin = await require_system_admin(request, db)

    result = await db.execute(select(User).where(User.id == user_id))
    target = result.scalar_one_or_none()
    if not target:
        raise HTTPException(status_code=404, detail=t_for(request, "errors.user_not_found"))

    return templates.TemplateResponse(
        request, "admin/user_edit.html", await _user_edit_context(request, db, admin, target),
    )


async def _user_edit_context(request: Request, db: AsyncSession, admin: User, target: User) -> dict:
    can_delete = False
    if target.id != admin.id:
        is_last_admin_lock = (
            target.role == UserRole.ADMIN
            and target.is_active
            and await is_last_admin(db, target.id)
        )
        can_delete = not is_last_admin_lock and not await user_has_history(db, target.id)

    groups_result = await db.execute(select(Group).order_by(Group.name))
    all_groups = groups_result.scalars().all()

    memberships_result = await db.execute(
        select(GroupMembership).where(GroupMembership.user_id == target.id)
    )
    # group_id -> membership_id, so the template can render a Remove
    # button (needs the membership id) or an Add button per group.
    target_memberships = {m.group_id: m.id for m in memberships_result.scalars().all()}

    return {
        "request": request, "user": admin, "target": target, "UserRole": UserRole,
        "can_delete": can_delete, "all_groups": all_groups, "target_memberships": target_memberships,
    }


@router.post("/users/{user_id}/reset-password", response_class=HTMLResponse)
async def user_reset_password(
    user_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Issue #244, ADR 0109: there's no self-service "forgot password" by
    design, so an admin resets it. Parcella generates a temporary
    password, shows it once, and the user must change it at the next
    login (the same must_change_password flow as the bootstrap admin).
    The page is rendered directly rather than redirected to, so the
    password never ends up in a URL, the browser history or a log."""
    admin = await require_system_admin(request, db)

    if user_id == admin.id:
        return RedirectResponse(
            f"/admin/users/{user_id}/edit?error={urllib.parse.quote(t_for(request, 'errors.own_password_reset_use_change_password'))}",
            status_code=302,
        )

    result = await db.execute(select(User).where(User.id == user_id))
    target = result.scalar_one_or_none()
    if not target:
        raise HTTPException(status_code=404, detail=t_for(request, "errors.user_not_found"))

    temp_password = generate_temporary_password()
    target.password_hash = hash_password(temp_password)
    target.must_change_password = True
    # Logs out every open session of that account.
    target.session_version += 1
    await db.commit()

    context = await _user_edit_context(request, db, admin, target)
    response = templates.TemplateResponse(
        request, "admin/user_edit.html", {**context, "temp_password": temp_password},
    )
    response.headers["Cache-Control"] = "no-store"
    return response


@router.post("/users/{user_id}/edit")
async def user_edit(
    user_id: str,
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    role: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
):
    """ADR 0041: role is no longer offered as a promotable dropdown --
    the only way `role` is submitted here is the "remove legacy role"
    action on an existing ADMIN/BOARD account, always sending READONLY.
    Every other user's real access comes from group membership, edited
    via the /admin/groups/{id}/members/add|remove endpoints from this
    same page."""
    await require_system_admin(request, db)

    result = await db.execute(select(User).where(User.id == user_id))
    target = result.scalar_one_or_none()
    if not target:
        raise HTTPException(status_code=404, detail=t_for(request, "errors.user_not_found"))

    name = name.strip()
    email = email.strip().lower()

    if not name:
        return RedirectResponse(
            f"/admin/users/{user_id}/edit?error={urllib.parse.quote(t_for(request, 'errors.name_required'))}",
            status_code=302,
        )

    existing = await db.execute(select(User).where(User.email == email, User.id != user_id))
    if existing.scalar_one_or_none():
        return RedirectResponse(
            f"/admin/users/{user_id}/edit?error={urllib.parse.quote(t_for(request, 'errors.email_already_registered'))}",
            status_code=302,
        )

    if role is not None and role in [r.value for r in UserRole]:
        new_role = UserRole(role)
        if (
            target.role == UserRole.ADMIN
            and new_role != UserRole.ADMIN
            and target.is_active
            and await is_last_admin(db, target.id)
        ):
            return RedirectResponse(
                f"/admin/users/{user_id}/edit?error={urllib.parse.quote(t_for(request, 'errors.cannot_remove_last_admin'))}",
                status_code=302,
            )
        target.role = new_role

    target.name = name
    target.email = email
    await db.commit()

    return RedirectResponse(
        f"/admin/users/?success={urllib.parse.quote(t_for(request, 'errors.user_updated'))}",
        status_code=302,
    )


# ---------------------------------------------------------------------------
# Avatar upload/removal for another user (issue #150) -- an admin can set
# this from the edit page, alongside the self-service /auth/avatar upload
# every user has for their own account. Shares app/avatars.py's storage/
# validation core with that self-service route.
# ---------------------------------------------------------------------------

@router.post("/users/{user_id}/avatar")
async def user_avatar_upload(
    user_id: str,
    request: Request,
    avatar: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    await require_system_admin(request, db)

    result = await db.execute(select(User).where(User.id == user_id))
    target = result.scalar_one_or_none()
    if not target:
        raise HTTPException(status_code=404, detail=t_for(request, "errors.user_not_found"))

    try:
        target.avatar_filename = await save_avatar_upload(target.id, avatar)
    except ValueError as e:
        return RedirectResponse(
            f"/admin/users/{user_id}/edit?avatar_error={str(e)}", status_code=302,
        )

    await db.commit()
    return RedirectResponse(f"/admin/users/{user_id}/edit", status_code=302)


@router.post("/users/{user_id}/avatar/remove")
async def user_avatar_remove(
    user_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    await require_system_admin(request, db)

    result = await db.execute(select(User).where(User.id == user_id))
    target = result.scalar_one_or_none()
    if not target:
        raise HTTPException(status_code=404, detail=t_for(request, "errors.user_not_found"))

    remove_avatar_file(target.id)
    target.avatar_filename = None
    await db.commit()
    return RedirectResponse(f"/admin/users/{user_id}/edit", status_code=302)


@router.post("/users/{user_id}/delete")
async def user_delete(
    user_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    admin = await require_system_admin(request, db)

    if user_id == admin.id:
        return RedirectResponse(
            f"/admin/users/?error={urllib.parse.quote(t_for(request, 'errors.own_account_cannot_deactivate'))}",
            status_code=302,
        )

    result = await db.execute(select(User).where(User.id == user_id))
    target = result.scalar_one_or_none()
    if not target:
        return RedirectResponse("/admin/users/", status_code=302)

    if (
        target.role == UserRole.ADMIN
        and target.is_active
        and await is_last_admin(db, target.id)
    ):
        return RedirectResponse(
            f"/admin/users/?error={urllib.parse.quote(t_for(request, 'errors.cannot_remove_last_admin'))}",
            status_code=302,
        )

    if await user_has_history(db, target.id):
        return RedirectResponse(
            f"/admin/users/{user_id}/edit?error={urllib.parse.quote(t_for(request, 'errors.user_has_history_cannot_delete'))}",
            status_code=302,
        )

    await db.delete(target)
    await db.commit()

    return RedirectResponse(
        f"/admin/users/?success={urllib.parse.quote(t_for(request, 'errors.user_deleted'))}",
        status_code=302,
    )
