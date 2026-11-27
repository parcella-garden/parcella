"""System information, update check, e-mail log, backup and restore, sample data."""
import urllib.parse
from fastapi import APIRouter
from zoneinfo import ZoneInfo
from fastapi import Depends, File, Form, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from starlette.background import BackgroundTask
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import EmailLogStatus
from app.auth import require_system_admin
from app.cloud_storage import CloudStorageError, get_cloud_storage_provider
from app.i18n import t_for
from app.l10n import DEFAULT_REGION, REGION_TIMEZONES, load_current_region
from app.email_log import (
    load_retention_days as load_email_log_retention_days,
    parse_status as parse_email_log_status,
    query_email_logs,
)
from app.update_check import get_update_status, refresh_update_check_cache
from app.sample_data import (
    MODULES,
    SampleDataBlockedError,
    add_sample_data,
    has_real_core_data,
    has_sample_data,
    remove_sample_data,
    sample_data_counts,
)
from app.backup import (
    BackupError,
    MAX_RESTORE_UPLOAD_BYTES,
    RESTORE_CONFIRM_PHRASE,
    RestoreZipError,
    build_backup_zip_file,
    restore_from_zip_bytes,
)
from app.parcel_cloud_folders import InvalidCloudPathError, sanitize_relative_path
from app.cloud_backup import (
    FREQUENCY_CHOICES,
    get_cloud_backup_settings,
    is_backup_filename,
    run_cloud_backup_now,
    save_cloud_backup_settings,
)
from app.templating import templates
from app.services.admin import list_cloud_backups

router = APIRouter()


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
    return templates.TemplateResponse(request, "admin/system.html", {
        "request": request, "user": user, "update_status": update_status,
    })


EMAIL_LOG_PAGE_SIZE = 50


@router.get("/email-log", response_class=HTMLResponse)
async def admin_email_log(
    request: Request, status: str = "", q: str = "", page: int = 1, db: AsyncSession = Depends(get_db),
):
    """Outgoing emails with their SMTP result (issue #270, ADR 0120),
    newest first, 50 per page, filterable by status and recipient."""
    user = await require_system_admin(request, db)
    status_filter = parse_email_log_status(status)
    page = max(page, 1)
    rows, total = await query_email_logs(
        db, status=status_filter, recipient=q[:320],
        limit=EMAIL_LOG_PAGE_SIZE, offset=(page - 1) * EMAIL_LOG_PAGE_SIZE,
    )
    region = await load_current_region(db)
    tz = ZoneInfo(REGION_TIMEZONES.get(region, REGION_TIMEZONES[DEFAULT_REGION]))
    return templates.TemplateResponse(request, "admin/email_log.html", {
        "request": request, "user": user, "rows": rows, "total": total, "tz": tz,
        "status": status_filter.name if status_filter else "", "q": q[:320], "page": page,
        "page_count": max((total + EMAIL_LOG_PAGE_SIZE - 1) // EMAIL_LOG_PAGE_SIZE, 1),
        "statuses": list(EmailLogStatus),
        "retention_days": await load_email_log_retention_days(db),
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
        filename, path = await build_backup_zip_file()
    except BackupError as e:
        return RedirectResponse(
            f"/admin/system?error={urllib.parse.quote(t_for(request, 'admin.dashboard.backup_error', detail=str(e)))}",
            status_code=302,
        )

    # Streamed from the temporary file, which is deleted once sent.
    return FileResponse(
        path, media_type="application/zip", filename=filename,
        background=BackgroundTask(path.unlink, missing_ok=True),
    )


@router.get("/backup/restore", response_class=HTMLResponse)
async def backup_restore_page(request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_system_admin(request, db)
    return templates.TemplateResponse(request, "admin/backup_restore.html", {
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


@router.get("/backup/cloud", response_class=HTMLResponse)
async def backup_cloud_page(request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_system_admin(request, db)
    module_enabled = request.state.module_flags.get("cloud_storage", False)
    cfg = await get_cloud_backup_settings(db)

    provider = await get_cloud_storage_provider(db) if module_enabled else None
    backups = []
    if provider is not None:
        backups = await list_cloud_backups(provider, cfg.folder)
        await provider.aclose()

    return templates.TemplateResponse(request, "admin/backup_cloud.html", {
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
    provider = await get_cloud_storage_provider(db)
    if provider is None:
        return _err("admin.cloud_backup.error_not_configured")

    try:
        zip_bytes = await provider.download_file(cfg.folder, filename)
    except CloudStorageError as e:
        return _err("admin.restore.error_restore_failed", detail=str(e)[:500])
    finally:
        await provider.aclose()

    # Same self-deadlock guard as the manual-upload restore -- this
    # handler holds the session (needed it above for get_cloud_storage_provider),
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

    return templates.TemplateResponse(request, "admin/sample_data.html", {
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
