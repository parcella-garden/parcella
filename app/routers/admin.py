"""
Admin router: user management, invitations, club settings.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional
import urllib.parse

from fastapi import APIRouter, Request, Form, Depends, HTTPException, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db, active_member_filter
from app.models import (
    User, Invitation, InvitationStatus, UserRole, ClubSetting,
    Group, InvitationGroupTarget,
    GroupMembership, ParcelCloudFolder, WorkSession, WorkTask, ChangeHistory,
    MeterReading, Ticket, TicketMessage, PurchaseRequest, PurchaseRequestApproval,
    CalendarEvent, CouncilPresence, CouncilAbsence, Announcement, InventoryItem,
    ItemLoan, Task, TaskAssignee, Member, ClubBoardMember,
)
from app.auth import require_system_admin, create_invitation_token, hash_password
from app.permissions import is_last_admin
from app.email_service import send_email
from app.crypto_utils import encrypt
from app.blog_publisher import load_wordpress_configuration, WordPressPublisher, BlogPublishError
from app.cloud_storage import load_nextcloud_configuration, get_nextcloud_provider, NextcloudProvider, CloudStorageError
from app.i18n import AVAILABLE_LANGUAGES, t_for
from app.l10n import AVAILABLE_REGIONS, AVAILABLE_CURRENCIES
from app.branding import save_logo_upload, remove_logo_file
from app.avatars import save_avatar_upload, remove_avatar_file
from app.nav_order import NAV_ORDER_DEFAULTS
from app.area_utils import compute_area_a_sqm, compute_area_b_sqm
from app.invoice_generation import (
    INVOICE_NUMBER_FORMAT_EXAMPLES, DEFAULT_INVOICE_NUMBER_FORMAT, is_valid_invoice_number_format,
)
from app.config import settings
from app.public_api_auth import get_or_create_public_api_token, regenerate_public_api_token
from app.update_check import get_update_status, refresh_update_check_cache
from app.sample_data import (
    add_sample_data, remove_sample_data, sample_data_counts,
    has_real_core_data, has_sample_data, SampleDataBlockedError, MODULES,
)
from app.backup import (
    build_backup_zip, restore_from_zip_bytes, BackupError, RestoreZipError,
    RESTORE_CONFIRM_PHRASE, MAX_RESTORE_UPLOAD_BYTES,
)
from app.parcel_cloud_folders import sanitize_relative_path, InvalidCloudPathError
from app.cloud_backup import (
    get_cloud_backup_settings, save_cloud_backup_settings, run_cloud_backup_now,
    is_backup_filename, FREQUENCY_CHOICES,
)

router = APIRouter(prefix="/admin", tags=["admin"])
from app.templating import templates

INVITATION_DAYS = 7
# Must match app/routers/finances.py's INCOMING_INVOICES_FOLDER_SETTING
# (issue #191: folder configuration moved here, but the setting is
# still read from app/routers/finances.py at upload/download time).
INCOMING_INVOICES_FOLDER_SETTING = "incoming_invoices_cloud_folder"
# Must match app/ticket_mailer.py's TICKET_ATTACHMENTS_FOLDER_SETTING --
# same "configured here, read from the owning module" split as above.
TICKET_ATTACHMENTS_FOLDER_SETTING = "ticket_attachments_cloud_folder"


# Every FK-to-users.id in the schema (see ADR 0040/audit) -- a user can
# only be permanently deleted if none of these reference them; anyone
# with a real footprint has to be deactivated instead (ADR 0005).
_USER_REFERENCE_CHECKS = [
    (Invitation, Invitation.invited_by_id),
    (GroupMembership, GroupMembership.user_id),
    (ParcelCloudFolder, ParcelCloudFolder.set_by_user_id),
    (WorkSession, WorkSession.created_by_id),
    (WorkTask, WorkTask.created_by_id),
    (ChangeHistory, ChangeHistory.changed_by_id),
    (MeterReading, MeterReading.recorded_by_id),
    (Ticket, Ticket.assigned_to_id),
    (TicketMessage, TicketMessage.authored_by_id),
    (PurchaseRequest, PurchaseRequest.requested_by_id),
    (PurchaseRequest, PurchaseRequest.created_by_id),
    (PurchaseRequest, PurchaseRequest.rejected_by_id),
    (PurchaseRequestApproval, PurchaseRequestApproval.user_id),
    (CalendarEvent, CalendarEvent.created_by_id),
    (CouncilPresence, CouncilPresence.user_id),
    (CouncilAbsence, CouncilAbsence.user_id),
    (Announcement, Announcement.created_by_id),
    (InventoryItem, InventoryItem.created_by_id),
    (ItemLoan, ItemLoan.created_by_id),
    (TaskAssignee, TaskAssignee.user_id),
    (Task, Task.created_by_id),
]


async def _user_has_history(db: AsyncSession, user_id: str) -> bool:
    """True if any row anywhere in the schema still references this
    user -- see _USER_REFERENCE_CHECKS. A hard delete is only offered
    when this is False."""
    for model, column in _USER_REFERENCE_CHECKS:
        result = await db.execute(select(model.id).where(column == user_id).limit(1))
        if result.scalar_one_or_none() is not None:
            return True
    return False


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
        "admin/dashboard.html",
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


# ---------------------------------------------------------------------------
# System: update check + backup/restore -- split out from user management
# (the dashboard above) since these are operational/maintenance concerns,
# not user administration. Follows the same "own page, linked from the
# Administration nav group" pattern as Groups/Settings/Integrations/
# Sample data (app/templates/base.html).
# ---------------------------------------------------------------------------

@router.get("/system", response_class=HTMLResponse)
async def admin_system_page(request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_system_admin(request, db)
    update_status = await get_update_status(db)
    return templates.TemplateResponse("admin/system.html", {
        "request": request, "user": user, "update_status": update_status,
    })


@router.post("/updates/check-now")
async def update_check_now(request: Request, db: AsyncSession = Depends(get_db)):
    """Manually triggers the same check the background loop runs every
    6 hours (see app/update_check.py), for admins who don't want to wait."""
    await require_system_admin(request, db)
    await refresh_update_check_cache(db)
    return RedirectResponse("/admin/system", status_code=302)


# ---------------------------------------------------------------------------
# Backup/restore: thin HTTP wrappers around app/backup.py's shared core
# (also used by the scheduled cloud-backup feature, app/cloud_backup.py --
# see ADR 0053/0054/0055). Nothing is ever written to server disk.
# ---------------------------------------------------------------------------


@router.post("/backup/download")
async def backup_download(request: Request, db: AsyncSession = Depends(get_db)):
    """One-click pg_dump of the whole database, bundled together with
    app/static/uploads/ into a single zip, returned straight to the
    browser as a download. See ADR 0053."""
    await require_system_admin(request, db)

    try:
        filename, content = await build_backup_zip()
    except BackupError as e:
        return RedirectResponse(
            f"/admin/system?error={urllib.parse.quote(t_for(request, 'admin.dashboard.backup_error', detail=str(e)))}",
            status_code=302,
        )

    return Response(
        content=content,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/backup/restore", response_class=HTMLResponse)
async def backup_restore_page(request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_system_admin(request, db)
    return templates.TemplateResponse("admin/backup_restore.html", {
        "request": request, "user": user, "confirm_phrase": RESTORE_CONFIRM_PHRASE,
    })


@router.post("/backup/restore")
async def backup_restore(
    request: Request, db: AsyncSession = Depends(get_db),
    confirm_phrase: str = Form(...), backup_zip: UploadFile = File(...),
):
    """Restores both the database and app/static/uploads/ from an
    uploaded backup zip -- the same shape backup_download produces.
    See ADR 0054."""
    await require_system_admin(request, db)

    def _err(key: str, **kwargs) -> RedirectResponse:
        msg = t_for(request, key, **kwargs)
        return RedirectResponse(f"/admin/backup/restore?error={urllib.parse.quote(msg)}", status_code=302)

    if confirm_phrase.strip() != RESTORE_CONFIRM_PHRASE:
        return _err("admin.restore.error_wrong_phrase")

    contents = await backup_zip.read(MAX_RESTORE_UPLOAD_BYTES + 1)
    if len(contents) > MAX_RESTORE_UPLOAD_BYTES:
        return _err("admin.restore.error_too_large")

    # Release our own session's open transaction before the destructive
    # DDL restore_from_zip_bytes runs -- otherwise DROP TABLE deadlocks
    # against the ACCESS SHARE lock require_system_admin's own SELECT
    # is still holding.
    await db.close()

    try:
        await restore_from_zip_bytes(contents)
    except RestoreZipError as e:
        return _err("admin.restore.error_invalid_zip", detail=str(e))
    except BackupError as e:
        return _err("admin.restore.error_restore_failed", detail=str(e))
    except OSError as e:
        return _err("admin.restore.error_uploads_failed", detail=str(e)[:500])

    return RedirectResponse("/admin/backup/restore?success=1", status_code=302)


# ---------------------------------------------------------------------------
# Cloud backups: scheduled uploads of backup_download's zip to the club's
# connected Nextcloud folder, with retention pruning and a restore-from-
# cloud picker. See app/cloud_backup.py and docs/ADR/0055-scheduled-cloud-backups.md.
# ---------------------------------------------------------------------------

async def _list_cloud_backups(provider, folder: str):
    """Returns cloud backup entries (name/size/last_modified), newest
    first, or an empty list if the folder doesn't exist yet or a
    transient error occurs -- a listing failure here shouldn't block
    rendering the settings page itself."""
    if not folder:
        return []
    try:
        entries = await provider.list_files(folder)
    except CloudStorageError:
        return []
    return sorted(
        (e for e in entries if not e.is_directory and is_backup_filename(e.name)),
        key=lambda e: e.name, reverse=True,
    )


@router.get("/backup/cloud", response_class=HTMLResponse)
async def backup_cloud_page(request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_system_admin(request, db)
    module_enabled = request.state.module_flags.get("cloud_storage", False)
    cfg = await get_cloud_backup_settings(db)

    provider = await get_nextcloud_provider(db) if module_enabled else None
    backups = []
    if provider is not None:
        backups = await _list_cloud_backups(provider, cfg.folder)
        await provider.aclose()

    return templates.TemplateResponse("admin/backup_cloud.html", {
        "request": request, "user": user,
        "module_enabled": module_enabled, "nextcloud_configured": provider is not None,
        "cfg": cfg, "backups": backups,
        "frequency_choices": FREQUENCY_CHOICES,
        "confirm_phrase": RESTORE_CONFIRM_PHRASE,
    })


@router.post("/backup/cloud/settings")
async def backup_cloud_save_settings(request: Request, db: AsyncSession = Depends(get_db)):
    await require_system_admin(request, db)
    form = await request.form()

    def _err(key: str, **kwargs) -> RedirectResponse:
        return RedirectResponse(
            f"/admin/backup/cloud?error={urllib.parse.quote(t_for(request, key, **kwargs))}", status_code=302,
        )

    try:
        folder = sanitize_relative_path(form.get("folder", ""))
    except InvalidCloudPathError as e:
        return _err("admin.cloud_backup.error_invalid_folder", detail=str(e))

    frequency = form.get("frequency", "")
    if frequency not in FREQUENCY_CHOICES:
        return _err("admin.cloud_backup.error_invalid_frequency")

    try:
        retention_count = int(form.get("retention_count", ""))
        if retention_count < 1:
            raise ValueError
    except ValueError:
        return _err("admin.cloud_backup.error_invalid_retention")

    # Unchecked checkbox sends no value at all, same convention as
    # MODULE_FIELDS above.
    enabled = "enabled" in form

    await save_cloud_backup_settings(
        db, enabled=enabled, folder=folder, frequency=frequency, retention_count=retention_count,
    )
    return RedirectResponse("/admin/backup/cloud?success=1", status_code=302)


@router.post("/backup/cloud/run-now")
async def backup_cloud_run_now(request: Request, db: AsyncSession = Depends(get_db)):
    await require_system_admin(request, db)
    await run_cloud_backup_now(db)
    cfg = await get_cloud_backup_settings(db)
    if cfg.last_run_status == "error":
        return RedirectResponse(
            f"/admin/backup/cloud?error={urllib.parse.quote(cfg.last_run_error or '')}", status_code=302,
        )
    return RedirectResponse("/admin/backup/cloud?success=1", status_code=302)


@router.post("/backup/restore-from-cloud")
async def backup_restore_from_cloud(
    request: Request, db: AsyncSession = Depends(get_db),
    confirm_phrase: str = Form(...), filename: str = Form(...),
):
    """Downloads a chosen backup from the connected cloud storage and
    restores it -- same destructive-restore safeguards as the manual-
    upload restore (type-to-confirm, restore_from_zip_bytes). See ADR 0055."""
    await require_system_admin(request, db)

    def _err(key: str, **kwargs) -> RedirectResponse:
        return RedirectResponse(
            f"/admin/backup/cloud?error={urllib.parse.quote(t_for(request, key, **kwargs))}", status_code=302,
        )

    if confirm_phrase.strip() != RESTORE_CONFIRM_PHRASE:
        return _err("admin.restore.error_wrong_phrase")
    if not is_backup_filename(filename):
        return _err("admin.cloud_backup.error_invalid_filename")

    cfg = await get_cloud_backup_settings(db)
    provider = await get_nextcloud_provider(db)
    if provider is None:
        return _err("admin.cloud_backup.error_not_configured")

    try:
        zip_bytes = await provider.download_file(cfg.folder, filename)
    except CloudStorageError as e:
        return _err("admin.restore.error_restore_failed", detail=str(e)[:500])
    finally:
        await provider.aclose()

    # Same self-deadlock guard as the manual-upload restore -- this
    # handler holds the session (needed it above for get_nextcloud_provider),
    # restore_from_zip_bytes doesn't take one at all.
    await db.close()

    try:
        await restore_from_zip_bytes(zip_bytes)
    except RestoreZipError as e:
        return _err("admin.restore.error_invalid_zip", detail=str(e))
    except BackupError as e:
        return _err("admin.restore.error_restore_failed", detail=str(e))
    except OSError as e:
        return _err("admin.restore.error_uploads_failed", detail=str(e)[:500])

    return RedirectResponse("/admin/backup/cloud?success=1", status_code=302)


# ---------------------------------------------------------------------------
# Sample data: one-click demo data for a fresh setup, and one-click removal.
# See app/sample_data.py and ADR 0037.
# ---------------------------------------------------------------------------

@router.get("/sample-data", response_class=HTMLResponse)
async def sample_data_page(request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_system_admin(request, db)

    return templates.TemplateResponse("admin/sample_data.html", {
        "request": request,
        "user": user,
        "has_sample": await has_sample_data(db),
        "has_real_core_data": await has_real_core_data(db),
        "counts": await sample_data_counts(db),
        "modules": MODULES,
    })


@router.post("/sample-data/add")
async def sample_data_add(request: Request, db: AsyncSession = Depends(get_db)):
    await require_system_admin(request, db)
    try:
        await add_sample_data(db)
    except SampleDataBlockedError as e:
        return RedirectResponse(f"/admin/sample-data?error={urllib.parse.quote(str(e))}", status_code=302)
    return RedirectResponse("/admin/sample-data?success=1", status_code=302)


@router.post("/sample-data/remove")
async def sample_data_remove(request: Request, db: AsyncSession = Depends(get_db)):
    await require_system_admin(request, db)
    await remove_sample_data(db)
    return RedirectResponse("/admin/sample-data?removed=1", status_code=302)


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

    can_delete = False
    if target.id != admin.id:
        is_last_admin_lock = (
            target.role == UserRole.ADMIN
            and target.is_active
            and await is_last_admin(db, target.id)
        )
        can_delete = not is_last_admin_lock and not await _user_has_history(db, target.id)

    groups_result = await db.execute(select(Group).order_by(Group.name))
    all_groups = groups_result.scalars().all()

    memberships_result = await db.execute(
        select(GroupMembership).where(GroupMembership.user_id == target.id)
    )
    # group_id -> membership_id, so the template can render a Remove
    # button (needs the membership id) or an Add button per group.
    target_memberships = {m.group_id: m.id for m in memberships_result.scalars().all()}

    return templates.TemplateResponse(
        "admin/user_edit.html",
        {
            "request": request, "user": admin, "target": target, "UserRole": UserRole,
            "can_delete": can_delete, "all_groups": all_groups, "target_memberships": target_memberships,
        },
    )


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

    if await _user_has_history(db, target.id):
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


# ---------------------------------------------------------------------------
# Club settings
# ---------------------------------------------------------------------------

SETTINGS_FIELDS = [
    ("verein_name", "admin.settings.fields.club_name"),
    ("verein_strasse", "admin.settings.fields.street"),
    ("verein_plz", "admin.settings.fields.postal_code"),
    ("verein_ort", "admin.settings.fields.city"),
    ("vereinsnummer", "admin.settings.fields.club_number"),
    ("registergericht", "admin.settings.fields.register_court"),
    ("flaeche_gesamt_qm", "admin.settings.fields.total_area"),
    ("flaeche_c_qm", "admin.settings.fields.area_c"),
    ("smtp_host", "admin.settings.fields.smtp_host"),
    ("smtp_port", "admin.settings.fields.smtp_port"),
    ("smtp_user", "admin.settings.fields.smtp_user"),
    ("smtp_password", "admin.settings.fields.smtp_password"),
    ("smtp_from", "admin.settings.fields.sender_email"),
    ("imap_host", "admin.settings.fields.imap_host"),
    ("imap_port", "admin.settings.fields.imap_port"),
    ("imap_ssl", "admin.settings.fields.imap_ssl"),
    ("spam_domain_blocklist", "admin.settings.fields.spam_domain_blocklist"),
    ("spam_keyword_blocklist", "admin.settings.fields.spam_keyword_blocklist"),
    ("spam_schwellenwert", "admin.settings.fields.spam_threshold"),
    ("spam_api_url", "admin.settings.fields.spam_api_url"),
    ("spam_api_key", "admin.settings.fields.spam_api_key"),
]

# Optional feature areas that each club can toggle on/off.
# Keys follow the convention "modul_<name>" (see app/module_flags.py).
# Name/description are resolved via translation keys (see below).
MODULE_FIELDS = [
    ("modul_work_hours", "admin.settings.modules.work_hours_name", "admin.settings.modules.work_hours_desc"),
    ("modul_water", "admin.settings.modules.water_name", "admin.settings.modules.water_desc"),
    ("modul_electricity", "admin.settings.modules.electricity_name", "admin.settings.modules.electricity_desc"),
    ("modul_insurance", "admin.settings.modules.insurance_name", "admin.settings.modules.insurance_desc"),
    ("modul_tickets", "admin.settings.modules.tickets_name", "admin.settings.modules.tickets_desc"),
    ("modul_purchase_requests", "admin.settings.modules.purchase_requests_name", "admin.settings.modules.purchase_requests_desc"),
    ("modul_calendar", "admin.settings.modules.calendar_name", "admin.settings.modules.calendar_desc"),
    ("modul_inventory", "admin.settings.modules.inventory_name", "admin.settings.modules.inventory_desc"),
    ("modul_tasks", "admin.settings.modules.tasks_name", "admin.settings.modules.tasks_desc"),
    ("modul_public_signup_api", "admin.settings.modules.public_signup_api_name", "admin.settings.modules.public_signup_api_desc"),
    ("modul_public_contact_api", "admin.settings.modules.public_contact_api_name", "admin.settings.modules.public_contact_api_desc"),
    ("modul_announcements", "admin.settings.modules.announcements_name", "admin.settings.modules.announcements_desc"),
    ("modul_cloud_storage", "admin.settings.modules.cloud_storage_name", "admin.settings.modules.cloud_storage_desc"),
    ("modul_finances", "admin.settings.modules.finances_name", "admin.settings.modules.finances_desc"),
]

# Finances module (annual invoices, issue #55): bank details for the
# invoice footer, and the starting sequence number + display format
# for invoice numbers (issue #65 -- see app/invoice_generation.py's
# is_valid_invoice_number_format/DEFAULT_INVOICE_NUMBER_FORMAT; the
# format only affects NEW invoices, past ones keep whatever they were
# assigned since invoice numbers are permanent once finalized).
# Rendered as their own card on the settings page, same pattern as
# SETTINGS_FIELDS above -- invoice_number_format is special-cased to a
# free-text input with a datalist of examples in admin/settings.html.
FINANCE_SETTINGS_FIELDS = [
    ("bank_name", "admin.settings.fields.bank_name"),
    ("bank_iban", "admin.settings.fields.bank_iban"),
    ("bank_bic", "admin.settings.fields.bank_bic"),
    ("bank_account_owner", "admin.settings.fields.bank_account_owner"),
    ("invoice_number_start", "admin.settings.fields.invoice_number_start"),
    ("invoice_number_format", "admin.settings.fields.invoice_number_format"),
]

# Issue #60: lets a club reorder its own sidebar. Keys follow the
# convention "nav_order_<name>" (see app/nav_order.py); names/order
# come from NAV_ORDER_DEFAULTS there, labels reuse the existing nav.*
# translation keys the sidebar itself uses.
NAV_ORDER_FIELDS = [
    ("dashboard", "nav.dashboard"),
    ("members", "nav.members"),
    ("parcels", "nav.parcels"),
    ("tickets", "nav.tickets"),
    ("purchase_requests", "nav.purchase_requests"),
    ("work_hours", "nav.work_hours_group"),
    ("water", "nav.water"),
    ("electricity", "nav.electricity"),
    ("insurance", "nav.insurance"),
    ("calendar", "nav.calendar_group"),
    ("announcements", "nav.announcements"),
    ("inventory", "nav.inventory"),
    ("tasks", "nav.tasks"),
    ("finances", "nav.finances_group"),
]


@router.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_system_admin(request, db)

    result = await db.execute(select(ClubSetting))
    settings_map = {e.key: e.value for e in result.scalars().all()}

    resolved_fields = [(key, t_for(request, label_key)) for key, label_key in SETTINGS_FIELDS]
    resolved_finance_fields = [(key, t_for(request, label_key)) for key, label_key in FINANCE_SETTINGS_FIELDS]
    resolved_module_fields = [
        (key, t_for(request, name_key), t_for(request, desc_key))
        for key, name_key, desc_key in MODULE_FIELDS
    ]
    resolved_nav_order_fields = [
        (f"nav_order_{name}", t_for(request, label_key), NAV_ORDER_DEFAULTS[name])
        for name, label_key in NAV_ORDER_FIELDS
    ]

    # Issue #72: the format field can be legitimately blank (falls back
    # to DEFAULT_INVOICE_NUMBER_FORMAT, see app/invoice_generation.py),
    # but a blank input looks identical to "nothing saved" -- show what's
    # actually in effect either way, computed the same way finalize_run()
    # would resolve it.
    effective_invoice_number_format = settings_map.get("invoice_number_format") or DEFAULT_INVOICE_NUMBER_FORMAT
    effective_invoice_number_example = effective_invoice_number_format.replace("{year}", "2026").replace("{number}", "1")

    # Issue #81: Area A (parcels) and Area B (communal) are no longer
    # manually entered -- Area A was drifting out of sync with reality
    # (and was mislabeled "municipal" while Area C was mislabeled
    # "parcels", the opposite of what they should mean) whenever a
    # parcel was added/resized/removed. Area A is now always the live
    # sum of every parcel's area regardless of lease status (same
    # query as the dashboard's "Total area" card, see issue #80), and
    # Area B is derived from it, so only Total area and Area C
    # (municipal) remain things a board member actually has to type in.
    # Shared with the "communal area share" invoice pricing mode
    # (issue #82, app/invoice_generation.py) via app/area_utils.py so
    # both agree on exactly the same numbers.
    area_a_sqm = await compute_area_a_sqm(db)
    area_b_sqm = await compute_area_b_sqm(db, area_a_sqm)

    # Board members (issue #111): picked from active members via a
    # searchable multi-select, same scope_picker pattern as finances'
    # parcel/member scoping (ADR 0042).
    result = await db.execute(
        select(Member).where(active_member_filter()).order_by(Member.last_name, Member.first_name)
    )
    board_member_candidates = result.scalars().all()
    result = await db.execute(select(ClubBoardMember))
    board_member_ids = {bm.member_id for bm in result.scalars().all()}

    return templates.TemplateResponse(
        "admin/settings.html",
        {
            "request": request,
            "user": user,
            "settings_map": settings_map,
            "fields": resolved_fields,
            "finance_fields": resolved_finance_fields,
            "invoice_number_format_examples": INVOICE_NUMBER_FORMAT_EXAMPLES,
            "effective_invoice_number_format": effective_invoice_number_format,
            "effective_invoice_number_example": effective_invoice_number_example,
            "module_fields": resolved_module_fields,
            "nav_order_fields": resolved_nav_order_fields,
            "available_languages": AVAILABLE_LANGUAGES,
            "available_regions": AVAILABLE_REGIONS,
            "available_currencies": AVAILABLE_CURRENCIES,
            "area_a_sqm": area_a_sqm,
            "area_b_sqm": area_b_sqm,
            "board_member_candidates": board_member_candidates,
            "board_member_ids": board_member_ids,
        },
    )


@router.post("/settings")
async def settings_save(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    await require_system_admin(request, db)
    form = await request.form()

    # Logo: upload, remove, or leave unchanged (not a field in
    # SETTINGS_FIELDS, since UploadFile is a file rather than a text value).
    logo_error = None
    remove_logo = form.get("remove_logo", "") == "true"
    logo_upload = form.get("logo")

    if remove_logo:
        remove_logo_file()
        result = await db.execute(select(ClubSetting).where(ClubSetting.key == "logo_filename"))
        entry = result.scalar_one_or_none()
        if entry:
            await db.delete(entry)
    elif logo_upload is not None and getattr(logo_upload, "filename", ""):
        try:
            filename = await save_logo_upload(logo_upload)
            result = await db.execute(select(ClubSetting).where(ClubSetting.key == "logo_filename"))
            entry = result.scalar_one_or_none()
            if entry:
                entry.value = filename
            else:
                db.add(ClubSetting(key="logo_filename", value=filename, description="Uploaded club logo filename"))
        except ValueError as e:
            logo_error = str(e)

    for key, description in SETTINGS_FIELDS + FINANCE_SETTINGS_FIELDS:
        if key == "invoice_number_format":
            continue  # validated separately below, same reasoning as language/region/currency

        value = form.get(key, "").strip() or None

        result = await db.execute(
            select(ClubSetting).where(ClubSetting.key == key)
        )
        entry = result.scalar_one_or_none()

        if key.endswith("_password") or key.endswith("_api_key"):
            # Empty field = "leave unchanged" (as promised by the
            # placeholder text), so the password doesn't need to be
            # retyped on every save. Only a NEW value gets encrypted
            # and stored.
            if not value:
                continue
            value = encrypt(value)

        if entry:
            entry.value = value
        else:
            db.add(ClubSetting(
                key=key,
                value=value,
                description=description,
            ))

    # Module toggles: an unchecked checkbox sends no value at all in the
    # form, hence explicit "true"/"false" instead of just form.get(...).
    for key, description, _hint in MODULE_FIELDS:
        value = "true" if key in form else "false"

        result = await db.execute(
            select(ClubSetting).where(ClubSetting.key == key)
        )
        entry = result.scalar_one_or_none()

        if entry:
            entry.value = value
        else:
            db.add(ClubSetting(
                key=key,
                value=value,
                description=description,
            ))

    # Nav order: plain integers (issue #60). An empty or non-numeric
    # field is skipped rather than stored, so a blank input falls back
    # to NAV_ORDER_DEFAULTS (see app/nav_order.py's load_nav_order)
    # instead of persisting a bad value.
    for name, _label_key in NAV_ORDER_FIELDS:
        key = f"nav_order_{name}"
        value = form.get(key, "").strip()
        if not value:
            continue
        try:
            int(value)
        except ValueError:
            continue

        result = await db.execute(select(ClubSetting).where(ClubSetting.key == key))
        entry = result.scalar_one_or_none()
        if entry:
            entry.value = value
        else:
            db.add(ClubSetting(key=key, value=value, description=f"Sidebar nav position: {name}"))

    # Language: its own field (dropdown, no free text) -- validated
    # against the list of known languages, so no invalid code can end
    # up stored for which there's no translation file.
    language_value = form.get("language", "").strip()
    if language_value in AVAILABLE_LANGUAGES:
        result = await db.execute(select(ClubSetting).where(ClubSetting.key == "language"))
        entry = result.scalar_one_or_none()
        if entry:
            entry.value = language_value
        else:
            db.add(ClubSetting(key="language", value=language_value, description="UI language"))

    # Region and currency: deliberately separate from language (see
    # app/l10n.py) -- their own fields, also validated against known
    # values.
    region_value = form.get("region", "").strip()
    if region_value in AVAILABLE_REGIONS:
        result = await db.execute(select(ClubSetting).where(ClubSetting.key == "region"))
        entry = result.scalar_one_or_none()
        if entry:
            entry.value = region_value
        else:
            db.add(ClubSetting(key="region", value=region_value, description="Region (number/address format)"))

    currency_value = form.get("currency", "").strip()
    if currency_value in AVAILABLE_CURRENCIES:
        result = await db.execute(select(ClubSetting).where(ClubSetting.key == "currency"))
        entry = result.scalar_one_or_none()
        if entry:
            entry.value = currency_value
        else:
            db.add(ClubSetting(key="currency", value=currency_value, description="Currency"))

    # Invoice number format (issue #65): freely typed, so -- unlike
    # language/region/currency's silent-skip-if-unknown above -- an
    # invalid one gets flashed back to the admin rather than quietly
    # discarded, since a typo here is easy to make and "it just didn't
    # save, no explanation" would be confusing. Only ever affects
    # invoices generated from here on, see app/invoice_generation.py.
    invoice_number_format_error = None
    invoice_number_format_value = form.get("invoice_number_format", "").strip()
    result = await db.execute(select(ClubSetting).where(ClubSetting.key == "invoice_number_format"))
    entry = result.scalar_one_or_none()
    if not invoice_number_format_value:
        # Blank = revert to DEFAULT_INVOICE_NUMBER_FORMAT, same "clear
        # the field to go back to default" convention as the plain
        # SETTINGS_FIELDS text inputs above.
        if entry:
            entry.value = None
    elif is_valid_invoice_number_format(invoice_number_format_value):
        if entry:
            entry.value = invoice_number_format_value
        else:
            db.add(ClubSetting(
                key="invoice_number_format", value=invoice_number_format_value,
                description="Invoice number display format",
            ))
    else:
        invoice_number_format_error = "1"

    # Update check: same "checkbox sends nothing when off" handling as
    # the module toggles above (see app/update_check.py).
    update_check_value = "true" if "update_check_enabled" in form else "false"
    result = await db.execute(select(ClubSetting).where(ClubSetting.key == "update_check_enabled"))
    entry = result.scalar_one_or_none()
    if entry:
        entry.value = update_check_value
    else:
        db.add(ClubSetting(
            key="update_check_enabled", value=update_check_value,
            description="Whether to periodically check GitHub for a newer Parcella release",
        ))

    # Board members (issue #111): full resync, not incremental add/remove
    # -- same convention as finances.py's parcel_scopes/member_scopes and
    # tasks.py's assignee resync (ADR 0046 point 4). Submitted ids are
    # intersected with active members rather than trusted outright, since
    # a stale form (a member deactivated between page load and submit)
    # would otherwise trip the FK constraint.
    result = await db.execute(select(Member.id).where(active_member_filter()))
    valid_member_ids = {row[0] for row in result.all()}
    submitted_board_member_ids = [
        member_id for member_id in form.getlist("board_member_ids") if member_id in valid_member_ids
    ]
    result = await db.execute(select(ClubBoardMember))
    for board_member in result.scalars().all():
        await db.delete(board_member)
    await db.flush()
    for member_id in submitted_board_member_ids:
        db.add(ClubBoardMember(member_id=member_id))

    await db.commit()
    if logo_error:
        return RedirectResponse(f"/admin/settings?logo_error={logo_error}", status_code=302)
    if invoice_number_format_error:
        return RedirectResponse("/admin/settings?invoice_number_format_error=1", status_code=302)
    return RedirectResponse("/admin/settings?success=1", status_code=302)


# ---------------------------------------------------------------------------
# Integrations: public signup API for external CMS connectors (WordPress,
# TYPO3, Contao, ...). See docs/module-public-api.md and app/routers/api_public.py.
# A dedicated page rather than a field on the settings page, matching the
# calendar module's ICS-token hub -- a shared secret is sensitive enough to
# warrant its own explicit "yes, show/regenerate this" screen.
# ---------------------------------------------------------------------------

@router.get("/integrations", response_class=HTMLResponse)
async def integrations_page(request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_system_admin(request, db)
    token = await get_or_create_public_api_token(db)

    result = await db.execute(select(ClubSetting).where(ClubSetting.key == "modul_public_signup_api"))
    entry = result.scalar_one_or_none()
    module_active = (entry.value.strip().lower() in ("true", "1", "ja", "an")) if entry else False

    contact_result = await db.execute(select(ClubSetting).where(ClubSetting.key == "modul_public_contact_api"))
    contact_entry = contact_result.scalar_one_or_none()
    contact_module_active = (contact_entry.value.strip().lower() in ("true", "1", "ja", "an")) if contact_entry else False

    wordpress_result = await db.execute(
        select(ClubSetting).where(ClubSetting.key.in_(["wordpress_site_url", "wordpress_username", "wordpress_app_password"]))
    )
    wordpress_stored = {e.key: e.value for e in wordpress_result.scalars().all()}

    nextcloud_result = await db.execute(
        select(ClubSetting).where(ClubSetting.key.in_(["nextcloud_base_url", "nextcloud_username", "nextcloud_app_password"]))
    )
    nextcloud_stored = {e.key: e.value for e in nextcloud_result.scalars().all()}

    cloud_storage_entry_result = await db.execute(select(ClubSetting).where(ClubSetting.key == "modul_cloud_storage"))
    cloud_storage_entry = cloud_storage_entry_result.scalar_one_or_none()
    cloud_storage_active = (
        cloud_storage_entry.value.strip().lower() in ("true", "1", "ja", "an")
    ) if cloud_storage_entry else False

    incoming_invoices_folder_result = await db.execute(
        select(ClubSetting).where(ClubSetting.key == INCOMING_INVOICES_FOLDER_SETTING)
    )
    incoming_invoices_folder_entry = incoming_invoices_folder_result.scalar_one_or_none()
    incoming_invoices_folder_path = incoming_invoices_folder_entry.value if incoming_invoices_folder_entry else None

    ticket_attachments_folder_result = await db.execute(
        select(ClubSetting).where(ClubSetting.key == TICKET_ATTACHMENTS_FOLDER_SETTING)
    )
    ticket_attachments_folder_entry = ticket_attachments_folder_result.scalar_one_or_none()
    ticket_attachments_folder_path = ticket_attachments_folder_entry.value if ticket_attachments_folder_entry else None

    return templates.TemplateResponse("admin/integrations.html", {
        "request": request, "user": user,
        "api_token": token,
        "module_active": module_active,
        "contact_module_active": contact_module_active,
        "base_url": str(request.base_url).rstrip("/"),
        "wordpress_site_url": wordpress_stored.get("wordpress_site_url", ""),
        "wordpress_username": wordpress_stored.get("wordpress_username", ""),
        "wordpress_app_password_set": bool(wordpress_stored.get("wordpress_app_password")),
        "wordpress_saved": request.query_params.get("wordpress_saved"),
        "wordpress_test_result": request.query_params.get("wordpress_test"),
        "wordpress_test_message": request.query_params.get("wordpress_test_message"),
        "nextcloud_base_url": nextcloud_stored.get("nextcloud_base_url", ""),
        "nextcloud_username": nextcloud_stored.get("nextcloud_username", ""),
        "nextcloud_app_password_set": bool(nextcloud_stored.get("nextcloud_app_password")),
        "nextcloud_saved": request.query_params.get("nextcloud_saved"),
        "nextcloud_test_result": request.query_params.get("nextcloud_test"),
        "nextcloud_test_message": request.query_params.get("nextcloud_test_message"),
        "cloud_storage_active": cloud_storage_active,
        "incoming_invoices_folder_path": incoming_invoices_folder_path,
        "incoming_invoices_folder_saved": request.query_params.get("incoming_invoices_folder_saved"),
        "incoming_invoices_folder_error": request.query_params.get("incoming_invoices_folder_error"),
        "ticket_attachments_folder_path": ticket_attachments_folder_path,
        "ticket_attachments_folder_saved": request.query_params.get("ticket_attachments_folder_saved"),
        "ticket_attachments_folder_error": request.query_params.get("ticket_attachments_folder_error"),
    })


@router.post("/integrations/regenerate-token")
async def integrations_token_regenerate(request: Request, db: AsyncSession = Depends(get_db)):
    await require_system_admin(request, db)
    await regenerate_public_api_token(db)
    return RedirectResponse("/admin/integrations?success=1", status_code=302)


async def _upsert_club_setting(db: AsyncSession, key: str, value: Optional[str], description: str = "") -> None:
    result = await db.execute(select(ClubSetting).where(ClubSetting.key == key))
    entry = result.scalar_one_or_none()
    if entry:
        entry.value = value
    else:
        db.add(ClubSetting(key=key, value=value, description=description))


@router.post("/integrations/wordpress")
async def integrations_wordpress_save(request: Request, db: AsyncSession = Depends(get_db)):
    """Saves the WordPress blog-draft credentials. Same "blank
    Application Password field = leave the existing one unchanged"
    convention as SMTP -- site URL and username are always overwritten
    with whatever's submitted (they're not secret, so there's no
    "leave unchanged" case worth supporting for them)."""
    await require_system_admin(request, db)
    form = await request.form()

    site_url = (form.get("wordpress_site_url") or "").strip() or None
    username = (form.get("wordpress_username") or "").strip() or None
    app_password = (form.get("wordpress_app_password") or "").strip()

    await _upsert_club_setting(db, "wordpress_site_url", site_url, "WordPress site URL for blog drafts")
    await _upsert_club_setting(db, "wordpress_username", username, "WordPress username for blog drafts")
    if app_password:
        await _upsert_club_setting(
            db, "wordpress_app_password", encrypt(app_password), "WordPress Application Password (encrypted)",
        )

    await db.commit()
    return RedirectResponse("/admin/integrations?wordpress_saved=1", status_code=303)


@router.post("/integrations/wordpress/test")
async def integrations_wordpress_test(request: Request, db: AsyncSession = Depends(get_db)):
    """Tests WordPress connectivity using whatever is currently in the
    form -- freshly typed values if provided, falling back to the
    already-saved configuration for any field left blank (same
    convention as saving). Doesn't persist anything; this is purely a
    connectivity check, usable before committing to save."""
    await require_system_admin(request, db)
    form = await request.form()

    saved_config = await load_wordpress_configuration(db)

    site_url = (form.get("wordpress_site_url") or "").strip() or (saved_config["site_url"] if saved_config else None)
    username = (form.get("wordpress_username") or "").strip() or (saved_config["username"] if saved_config else None)
    app_password = (form.get("wordpress_app_password") or "").strip() or (saved_config["app_password"] if saved_config else None)

    from urllib.parse import quote

    if not site_url or not username or not app_password:
        message = quote("Please fill in all three fields first.")
        return RedirectResponse(f"/admin/integrations?wordpress_test=failed&wordpress_test_message={message}", status_code=303)

    publisher = WordPressPublisher(site_url=site_url, username=username, application_password=app_password)
    try:
        await publisher.test_connection()
        result = "success"
        message = ""
    except BlogPublishError as e:
        result = "failed"
        message = str(e)
    finally:
        await publisher.aclose()

    return RedirectResponse(
        f"/admin/integrations?wordpress_test={result}&wordpress_test_message={quote(message)}", status_code=303,
    )


@router.post("/integrations/nextcloud")
async def integrations_nextcloud_save(request: Request, db: AsyncSession = Depends(get_db)):
    """Saves the Nextcloud cloud-storage credentials. Same "blank
    Application Password field = leave the existing one unchanged"
    convention as SMTP and WordPress -- base URL and username are
    always overwritten with whatever's submitted (they're not secret,
    so there's no "leave unchanged" case worth supporting for them)."""
    await require_system_admin(request, db)
    form = await request.form()

    base_url = (form.get("nextcloud_base_url") or "").strip() or None
    username = (form.get("nextcloud_username") or "").strip() or None
    app_password = (form.get("nextcloud_app_password") or "").strip()

    await _upsert_club_setting(db, "nextcloud_base_url", base_url, "Nextcloud server URL for cloud storage")
    await _upsert_club_setting(db, "nextcloud_username", username, "Nextcloud username for cloud storage")
    if app_password:
        await _upsert_club_setting(
            db, "nextcloud_app_password", encrypt(app_password), "Nextcloud Application Password (encrypted)",
        )

    await db.commit()
    return RedirectResponse("/admin/integrations?nextcloud_saved=1", status_code=303)


@router.post("/integrations/nextcloud/test")
async def integrations_nextcloud_test(request: Request, db: AsyncSession = Depends(get_db)):
    """Tests Nextcloud connectivity using whatever is currently in the
    form -- freshly typed values if provided, falling back to the
    already-saved configuration for any field left blank (same
    convention as saving). Doesn't persist anything; this is purely a
    connectivity check, usable before committing to save."""
    await require_system_admin(request, db)
    form = await request.form()

    saved_config = await load_nextcloud_configuration(db)

    base_url = (form.get("nextcloud_base_url") or "").strip() or (saved_config["base_url"] if saved_config else None)
    username = (form.get("nextcloud_username") or "").strip() or (saved_config["username"] if saved_config else None)
    app_password = (form.get("nextcloud_app_password") or "").strip() or (saved_config["app_password"] if saved_config else None)

    from urllib.parse import quote

    if not base_url or not username or not app_password:
        message = quote("Please fill in all three fields first.")
        return RedirectResponse(f"/admin/integrations?nextcloud_test=failed&nextcloud_test_message={message}", status_code=303)

    provider = NextcloudProvider(base_url=base_url, username=username, app_password=app_password)
    try:
        await provider.test_connection()
        result = "success"
        message = ""
    except CloudStorageError as e:
        result = "failed"
        message = str(e)
    finally:
        await provider.aclose()

    return RedirectResponse(
        f"/admin/integrations?nextcloud_test={result}&nextcloud_test_message={quote(message)}", status_code=303,
    )


@router.post("/integrations/nextcloud/incoming-invoices-folder")
async def integrations_incoming_invoices_folder_save(
    request: Request, relative_path: str = Form(...), db: AsyncSession = Depends(get_db),
):
    """Issue #191: moved here from /finances/incoming-invoices, which
    had its own folder-path form -- now every Nextcloud-backed folder
    setting (parcel documents' per-parcel paths stay on each parcel's
    own page, but this shared one) lives on the admin integrations
    page. The value itself is unchanged (ClubSetting
    INCOMING_INVOICES_FOLDER_SETTING) and still read from
    app/routers/finances.py at upload/download time."""
    await require_system_admin(request, db)

    try:
        sanitized = sanitize_relative_path(relative_path)
    except InvalidCloudPathError as e:
        from urllib.parse import quote
        return RedirectResponse(
            f"/admin/integrations?incoming_invoices_folder_error={quote(str(e))}", status_code=303,
        )

    result = await db.execute(select(ClubSetting).where(ClubSetting.key == INCOMING_INVOICES_FOLDER_SETTING))
    entry = result.scalar_one_or_none()
    if entry:
        entry.value = sanitized
    else:
        db.add(ClubSetting(
            key=INCOMING_INVOICES_FOLDER_SETTING, value=sanitized,
            description="Shared cloud folder for incoming invoice attachments",
        ))
    await db.commit()
    return RedirectResponse("/admin/integrations?incoming_invoices_folder_saved=1", status_code=303)


@router.post("/integrations/nextcloud/ticket-attachments-folder")
async def integrations_ticket_attachments_folder_save(
    request: Request, relative_path: str = Form(...), db: AsyncSession = Depends(get_db),
):
    """Same shared-folder pattern as incoming invoices above (ClubSetting
    TICKET_ATTACHMENTS_FOLDER_SETTING), one folder for all tickets --
    read from app/ticket_mailer.py at ingestion time and
    app/routers/tickets.py at download time."""
    await require_system_admin(request, db)

    try:
        sanitized = sanitize_relative_path(relative_path)
    except InvalidCloudPathError as e:
        from urllib.parse import quote
        return RedirectResponse(
            f"/admin/integrations?ticket_attachments_folder_error={quote(str(e))}", status_code=303,
        )

    result = await db.execute(select(ClubSetting).where(ClubSetting.key == TICKET_ATTACHMENTS_FOLDER_SETTING))
    entry = result.scalar_one_or_none()
    if entry:
        entry.value = sanitized
    else:
        db.add(ClubSetting(
            key=TICKET_ATTACHMENTS_FOLDER_SETTING, value=sanitized,
            description="Shared cloud folder for incoming ticket attachments",
        ))
    await db.commit()
    return RedirectResponse("/admin/integrations?ticket_attachments_folder_saved=1", status_code=303)
