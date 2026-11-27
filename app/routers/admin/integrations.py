"""Integrations: API/ICS tokens, public forms, website, cloud storage and its folders, helpdesk, Deck."""
import urllib.parse
from fastapi import APIRouter
from fastapi import Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from app.database import get_db
from app.models import ClubSetting, ExternalTaskLink
from app.auth import require_system_admin
from app.crypto_utils import encrypt
from app.provider_registry import InvalidConnectorConfig, ProviderRegistry
from app.website_connectors import BlogPublishError
from app.website_connectors.registry import WEBSITE
from app.helpdesk import HELPDESK, HelpdeskError
from app.cloud_storage import CLOUD_STORAGE, CloudStorageError
from app.task_sync import (
    DeckError,
    DeckTaskProvider,
    load_deck_configuration,
    normalize_deck_board_id,
)
from app.deck_sync import sync_deck_tasks
from app.i18n import t_for
from app.public_api_auth import (
    PUBLIC_FORM_ORIGINS_SETTING_KEY,
    allowed_form_origins,
    get_or_create_public_api_token,
    normalize_origin,
    regenerate_public_api_token,
)
from app.form_altcha import REQUIRE_ALTCHA_SETTING_KEY, altcha_required
from app.parcel_cloud_folders import (
    InvalidCloudPathError,
    browse_folder_picker,
    sanitize_relative_path,
)
from app.print_publisher import PRINT_CLOUD_FOLDER_SETTING, load_print_cloud_folder
from app.ics_utils import regenerate_ics_token
from app.contact_documents import (
    EXTERNAL_CONTACTS_FOLDER_SETTING,
    load_base_folder as load_contacts_base_folder,
)
from app.services.notes import NOTES_FOLDER_SETTING, load_notes_folder, reset_sync_throttle
from app.services.processes import CLOUD_FOLDER_SETTING as PROCESSES_FOLDER_SETTING
from app.templating import templates
from app.services.admin import upsert_club_setting

router = APIRouter()


# Must match app/routers/finances.py's INCOMING_INVOICES_FOLDER_SETTING
# (issue #191: folder configuration moved here, but the setting is
# still read from app/routers/finances.py at upload/download time).
INCOMING_INVOICES_FOLDER_SETTING = "incoming_invoices_cloud_folder"


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
    external_contacts_folder_path = await load_contacts_base_folder(db)
    print_folder_path = await load_print_cloud_folder(db)
    # Issue #262: "Browse" opens the same folder picker as the parcel
    # page, inline in the cloud storage card (?print_pick=1&pick_path=...).
    print_picker = None
    if cloud_storage_active and request.query_params.get("print_pick") == "1":
        print_picker = await browse_folder_picker(
            db, request.query_params.get("pick_path", ""),
            root_label=t_for(request, "parcels.detail.cloud_picker_root_label"),
            not_configured_message=t_for(request, "parcels.cloud_storage.not_configured"),
        )


    deck_result = await db.execute(
        select(ClubSetting).where(
            ClubSetting.key.in_(["deck_base_url", "deck_username", "deck_app_password", "deck_board_id"])
        )
    )
    deck_stored = {e.key: e.value for e in deck_result.scalars().all()}
    deck_link_stats = (await db.execute(
        select(func.count(ExternalTaskLink.id), func.max(ExternalTaskLink.last_synced_at))
        .where(ExternalTaskLink.source == "deck")
    )).one()
    deck_synced_count, deck_last_synced_at = deck_link_stats

    form_origins_result = await db.execute(
        select(ClubSetting).where(ClubSetting.key == PUBLIC_FORM_ORIGINS_SETTING_KEY)
    )
    form_origins_entry = form_origins_result.scalar_one_or_none()

    return templates.TemplateResponse(request, "admin/integrations.html", {
        "request": request, "user": user,
        "api_token": token,
        "public_form_origins": "\n".join(sorted(await allowed_form_origins(db))) if form_origins_entry else "",
        "public_form_require_altcha": await altcha_required(db),
        "public_forms_saved": request.query_params.get("public_forms_saved"),
        "public_forms_ignored": request.query_params.get("public_forms_ignored"),
        "module_active": module_active,
        "contact_module_active": contact_module_active,
        "base_url": str(request.base_url).rstrip("/"),
        "website": await WEBSITE.admin_context(db),
        "website_saved": request.query_params.get("website_saved"),
        "website_error": request.query_params.get("website_error"),
        "website_test_result": request.query_params.get("website_test"),
        "website_test_message": request.query_params.get("website_test_message"),
        "cloud_storage": await CLOUD_STORAGE.admin_context(db),
        "cloud_storage_saved": request.query_params.get("cloud_storage_saved"),
        "cloud_storage_error": request.query_params.get("cloud_storage_error"),
        "cloud_storage_test_result": request.query_params.get("cloud_storage_test"),
        "cloud_storage_test_message": request.query_params.get("cloud_storage_test_message"),
        "cloud_storage_active": cloud_storage_active,
        "incoming_invoices_folder_path": incoming_invoices_folder_path,
        "incoming_invoices_folder_saved": request.query_params.get("incoming_invoices_folder_saved"),
        "incoming_invoices_folder_error": request.query_params.get("incoming_invoices_folder_error"),
        "external_contacts_folder_path": external_contacts_folder_path,
        "external_contacts_folder_saved": request.query_params.get("external_contacts_folder_saved"),
        "external_contacts_folder_error": request.query_params.get("external_contacts_folder_error"),
        "print_folder_path": print_folder_path,
        "print_picker": print_picker,
        "print_folder_saved": request.query_params.get("print_folder_saved"),
        "print_folder_error": request.query_params.get("print_folder_error"),
        "notes_folder_path": await load_notes_folder(db),
        "notes_folder_saved": request.query_params.get("notes_folder_saved"),
        "notes_folder_error": request.query_params.get("notes_folder_error"),
        "processes_folder_path": await db.scalar(
            select(ClubSetting.value).where(ClubSetting.key == PROCESSES_FOLDER_SETTING)
        ),
        "processes_folder_saved": request.query_params.get("processes_folder_saved"),
        "processes_folder_error": request.query_params.get("processes_folder_error"),
        "helpdesk": await HELPDESK.admin_context(db),
        "helpdesk_saved": request.query_params.get("helpdesk_saved"),
        "helpdesk_error": request.query_params.get("helpdesk_error"),
        "helpdesk_test_result": request.query_params.get("helpdesk_test"),
        "helpdesk_test_message": request.query_params.get("helpdesk_test_message"),
        "deck_base_url": deck_stored.get("deck_base_url", ""),
        "deck_username": deck_stored.get("deck_username", ""),
        "deck_app_password_set": bool(deck_stored.get("deck_app_password")),
        "deck_board_id": deck_stored.get("deck_board_id", ""),
        "deck_saved": request.query_params.get("deck_saved"),
        "deck_test_result": request.query_params.get("deck_test"),
        "deck_test_message": request.query_params.get("deck_test_message"),
        "deck_synced_now": request.query_params.get("deck_synced"),
        "deck_synced_count": deck_synced_count,
        "deck_last_synced_at": deck_last_synced_at,
    })


@router.post("/integrations/regenerate-token")
async def integrations_token_regenerate(request: Request, db: AsyncSession = Depends(get_db)):
    await require_system_admin(request, db)
    await regenerate_public_api_token(db)
    return RedirectResponse("/admin/integrations?success=1", status_code=302)


@router.post("/integrations/regenerate-ics-token")
async def integrations_ics_token_regenerate(request: Request, db: AsyncSession = Depends(get_db)):
    await require_system_admin(request, db)
    await regenerate_ics_token(db)
    return RedirectResponse("/admin/integrations?ics_rotated=1", status_code=302)


@router.post("/integrations/public-forms")
async def integrations_public_forms_save(request: Request, db: AsyncSession = Depends(get_db)):
    """Saves the website origins allowed to post the plain-HTML-form
    endpoints (app/routers/api_public.py, ADR 0088) and whether those
    forms must carry an ALTCHA solution (ADR 0089). Entries are reduced
    to scheme://host[:port]; anything that isn't an http(s) URL is
    dropped and reported back rather than stored."""
    await require_system_admin(request, db)
    form = await request.form()
    entries = (form.get("public_form_origins") or "").split()
    origins = sorted({o for o in map(normalize_origin, entries) if o})
    ignored = [e for e in entries if not normalize_origin(e)]

    await upsert_club_setting(
        db, PUBLIC_FORM_ORIGINS_SETTING_KEY, "\n".join(origins) or None,
        "Website origins allowed to post the public plain-HTML forms",
    )
    await upsert_club_setting(
        db, REQUIRE_ALTCHA_SETTING_KEY, "1" if form.get("require_altcha") else "0",
        "Plain-HTML forms must carry an ALTCHA proof-of-work solution",
    )
    await db.commit()
    query = "public_forms_saved=1"
    if ignored:
        query += f"&public_forms_ignored={urllib.parse.quote(', '.join(ignored))}"
    return RedirectResponse(f"/admin/integrations?{query}", status_code=303)


async def _save_provider_card(request: Request, db: AsyncSession, registry: ProviderRegistry, param: str):
    """Saves a "one dropdown, one provider at a time" card (Website,
    Cloud storage): which provider is active -- choosing one switches the
    others off -- and that provider's fields. Other providers' stored
    settings stay as they are, so switching back needs no retyping. A
    blank secret keeps the stored one, same convention as SMTP."""
    await require_system_admin(request, db)
    form = await request.form()

    provider_type = (form.get(registry.active_key) or "").strip() or None
    try:
        await registry.save_config(
            db, provider_type, registry.form_values(form, provider_type) if provider_type in registry.providers else {},
        )
    except InvalidConnectorConfig as e:
        await db.rollback()
        return RedirectResponse(f"/admin/integrations?{param}_error={urllib.parse.quote(str(e))}", status_code=303)

    await db.commit()
    return RedirectResponse(f"/admin/integrations?{param}_saved=1", status_code=303)


async def _test_provider_card(
    request: Request, db: AsyncSession, registry: ProviderRegistry, param: str, errors: tuple,
):
    """Tests the provider chosen in the dropdown with whatever is in the
    form -- freshly typed values, falling back to the saved ones for
    blank fields. Saves nothing: it's a check before committing."""
    await require_system_admin(request, db)
    form = await request.form()

    provider_type = (form.get(registry.active_key) or "").strip()
    if provider_type not in registry.providers:
        message = urllib.parse.quote("Choose a type first.")
        return RedirectResponse(f"/admin/integrations?{param}_test=failed&{param}_test_message={message}", status_code=303)

    provider = None
    try:
        config = await registry.merged_config(db, provider_type, registry.form_values(form, provider_type))
        provider = await registry.build(db, provider_type, config)
        await provider.test_connection()
        result, message = "success", ""
    except (InvalidConnectorConfig,) + errors as e:
        result, message = "failed", str(e)
    finally:
        if provider is not None:
            await provider.aclose()

    return RedirectResponse(
        f"/admin/integrations?{param}_test={result}&{param}_test_message={urllib.parse.quote(message)}", status_code=303,
    )


@router.post("/integrations/website")
async def integrations_website_save(request: Request, db: AsyncSession = Depends(get_db)):
    """The Website card (ADR 0104)."""
    return await _save_provider_card(request, db, WEBSITE, "website")


@router.post("/integrations/website/test")
async def integrations_website_test(request: Request, db: AsyncSession = Depends(get_db)):
    return await _test_provider_card(request, db, WEBSITE, "website", (BlogPublishError,))


@router.post("/integrations/cloud-storage")
async def integrations_cloud_storage_save(request: Request, db: AsyncSession = Depends(get_db)):
    """The Cloud storage card (ADR 0106)."""
    return await _save_provider_card(request, db, CLOUD_STORAGE, "cloud_storage")


@router.post("/integrations/cloud-storage/test")
async def integrations_cloud_storage_test(request: Request, db: AsyncSession = Depends(get_db)):
    return await _test_provider_card(request, db, CLOUD_STORAGE, "cloud_storage", (CloudStorageError,))


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


@router.post("/integrations/nextcloud/external-contacts-folder")
async def integrations_external_contacts_folder_save(
    request: Request, relative_path: str = Form(""), db: AsyncSession = Depends(get_db),
):
    """Base folder for external contacts' documents (ADR 0097): one
    subfolder per contact below it, created by hand in the cloud. Blank
    clears the setting (the documents card then disappears)."""
    await require_system_admin(request, db)
    from urllib.parse import quote

    entry = await db.scalar(select(ClubSetting).where(ClubSetting.key == EXTERNAL_CONTACTS_FOLDER_SETTING))
    if not relative_path.strip():
        if entry:
            await db.delete(entry)
            await db.commit()
        return RedirectResponse("/admin/integrations?external_contacts_folder_saved=1", status_code=303)
    try:
        sanitized = sanitize_relative_path(relative_path)
    except InvalidCloudPathError as e:
        return RedirectResponse(
            f"/admin/integrations?external_contacts_folder_error={quote(str(e))}", status_code=303,
        )
    if entry:
        entry.value = sanitized
    else:
        db.add(ClubSetting(
            key=EXTERNAL_CONTACTS_FOLDER_SETTING, value=sanitized,
            description="Cloud base folder for external contacts' documents",
        ))
    await db.commit()
    return RedirectResponse("/admin/integrations?external_contacts_folder_saved=1", status_code=303)


@router.post("/integrations/nextcloud/notes-folder")
async def integrations_notes_folder_save(
    request: Request, relative_path: str = Form(""), db: AsyncSession = Depends(get_db),
):
    """Issue #286: the cloud folder holding the notes as .md files, the
    notes' master copy once set (ADR 0123). Blank clears it (notes then
    live in the database only). Changing it re-syncs against the new
    folder: notes whose file isn't there are hidden, and come back if
    the folder is switched back."""
    await require_system_admin(request, db)
    from urllib.parse import quote

    entry = await db.scalar(select(ClubSetting).where(ClubSetting.key == NOTES_FOLDER_SETTING))
    if not relative_path.strip():
        if entry:
            await db.delete(entry)
            await db.commit()
        return RedirectResponse("/admin/integrations?notes_folder_saved=1#integration-card-nextcloud", status_code=303)
    try:
        sanitized = sanitize_relative_path(relative_path)
    except InvalidCloudPathError as e:
        return RedirectResponse(
            f"/admin/integrations?notes_folder_error={quote(str(e))}#integration-card-nextcloud", status_code=303,
        )
    if entry:
        entry.value = sanitized
    else:
        db.add(ClubSetting(key=NOTES_FOLDER_SETTING, value=sanitized, description="Cloud folder for notes (.md files)"))
    await db.commit()
    reset_sync_throttle()
    return RedirectResponse("/admin/integrations?notes_folder_saved=1#integration-card-nextcloud", status_code=303)


@router.post("/integrations/nextcloud/processes-folder")
async def integrations_processes_folder_save(
    request: Request, relative_path: str = Form(""), db: AsyncSession = Depends(get_db),
):
    """Issue #331: the cloud folder for process files (ADR 0136), one
    subfolder per process. Blank clears it -- files then go to the
    private local directory. Files already uploaded stay where they are."""
    await require_system_admin(request, db)
    from urllib.parse import quote

    anchor = "#integration-card-nextcloud"
    entry = await db.scalar(select(ClubSetting).where(ClubSetting.key == PROCESSES_FOLDER_SETTING))
    if not relative_path.strip():
        if entry:
            await db.delete(entry)
            await db.commit()
        return RedirectResponse(f"/admin/integrations?processes_folder_saved=1{anchor}", status_code=303)
    try:
        sanitized = sanitize_relative_path(relative_path)
    except InvalidCloudPathError as e:
        return RedirectResponse(f"/admin/integrations?processes_folder_error={quote(str(e))}{anchor}", status_code=303)
    if entry:
        entry.value = sanitized
    else:
        db.add(ClubSetting(key=PROCESSES_FOLDER_SETTING, value=sanitized, description="Cloud folder for process files"))
    await db.commit()
    return RedirectResponse(f"/admin/integrations?processes_folder_saved=1{anchor}", status_code=303)


@router.post("/integrations/nextcloud/announcements-print-folder")
async def integrations_print_folder_save(
    request: Request, relative_path: str = Form(""), db: AsyncSession = Depends(get_db),
):
    """Issue #262: cloud folder every generated announcement print PDF
    is also saved to. Blank clears it (download only, as before)."""
    await require_system_admin(request, db)
    from urllib.parse import quote

    entry = await db.scalar(select(ClubSetting).where(ClubSetting.key == PRINT_CLOUD_FOLDER_SETTING))
    if not relative_path.strip():
        if entry:
            await db.delete(entry)
            await db.commit()
        return RedirectResponse("/admin/integrations?print_folder_saved=1#integration-card-nextcloud", status_code=303)
    try:
        sanitized = sanitize_relative_path(relative_path)
    except InvalidCloudPathError as e:
        return RedirectResponse(
            f"/admin/integrations?print_folder_error={quote(str(e))}#integration-card-nextcloud", status_code=303,
        )
    if entry:
        entry.value = sanitized
    else:
        db.add(ClubSetting(
            key=PRINT_CLOUD_FOLDER_SETTING, value=sanitized,
            description="Cloud folder for generated announcement print PDFs",
        ))
    await db.commit()
    return RedirectResponse("/admin/integrations?print_folder_saved=1#integration-card-nextcloud", status_code=303)


@router.post("/integrations/helpdesk")
async def integrations_helpdesk_save(request: Request, db: AsyncSession = Depends(get_db)):
    """The Support / helpdesk card (ADR 0107)."""
    return await _save_provider_card(request, db, HELPDESK, "helpdesk")


@router.post("/integrations/helpdesk/test")
async def integrations_helpdesk_test(request: Request, db: AsyncSession = Depends(get_db)):
    return await _test_provider_card(request, db, HELPDESK, "helpdesk", (HelpdeskError,))


@router.post("/integrations/deck")
async def integrations_deck_save(request: Request, db: AsyncSession = Depends(get_db)):
    """Saves the Nextcloud Deck credentials plus the single board id to
    sync from -- same "blank app password field = leave the existing
    one unchanged" convention as WordPress/Nextcloud/FreeScout above.
    Deliberately its own set of ClubSetting keys, not shared with
    cloud storage's nextcloud_* ones -- see app/task_sync.py's
    module docstring and docs/ADR/0086."""
    await require_system_admin(request, db)
    form = await request.form()

    base_url = (form.get("deck_base_url") or "").strip() or None
    username = (form.get("deck_username") or "").strip() or None
    board_id = normalize_deck_board_id(form.get("deck_board_id") or "") or None
    app_password = (form.get("deck_app_password") or "").strip()

    await upsert_club_setting(db, "deck_base_url", base_url, "Nextcloud server URL for Deck task sync")
    await upsert_club_setting(db, "deck_username", username, "Nextcloud username for Deck task sync")
    await upsert_club_setting(db, "deck_board_id", board_id, "Deck board id to sync tasks from")
    if app_password:
        await upsert_club_setting(
            db, "deck_app_password", encrypt(app_password), "Nextcloud Application Password for Deck sync (encrypted)",
        )

    await db.commit()
    return RedirectResponse("/admin/integrations?deck_saved=1", status_code=303)


@router.post("/integrations/deck/test")
async def integrations_deck_test(request: Request, db: AsyncSession = Depends(get_db)):
    """Tests Deck connectivity using whatever is currently in the form,
    falling back to the already-saved configuration for any field left
    blank -- doesn't persist anything. Only checks the connection/
    credentials, not the board id (test_connection() just lists
    boards -- it doesn't need a specific board to succeed)."""
    await require_system_admin(request, db)
    form = await request.form()
    from urllib.parse import quote

    saved_config = await load_deck_configuration(db)
    base_url = (form.get("deck_base_url") or "").strip() or (saved_config["base_url"] if saved_config else None)
    username = (form.get("deck_username") or "").strip() or (saved_config["username"] if saved_config else None)
    app_password = (form.get("deck_app_password") or "").strip() or (saved_config["app_password"] if saved_config else None)

    if not base_url or not username or not app_password:
        message = quote(t_for(request, "admin.integrations.deck_not_configured"))
        return RedirectResponse(f"/admin/integrations?deck_test=failed&deck_test_message={message}", status_code=303)

    provider = DeckTaskProvider(base_url=base_url, username=username, app_password=app_password)
    try:
        await provider.test_connection()
        result, message = "success", t_for(request, "admin.integrations.deck_test_success")
    except DeckError as e:
        result, message = "failed", str(e)
    finally:
        await provider.aclose()

    return RedirectResponse(
        f"/admin/integrations?deck_test={result}&deck_test_message={quote(message)}", status_code=303,
    )


@router.post("/integrations/deck/sync-now")
async def integrations_deck_sync_now(request: Request, db: AsyncSession = Depends(get_db)):
    """Manual on-demand sync, same precedent as
    POST /admin/backup/cloud/run-now -- calls the exact same function
    the background poller calls (app/deck_sync.py's sync_deck_tasks)."""
    await require_system_admin(request, db)
    from urllib.parse import quote

    try:
        count = await sync_deck_tasks(db)
        message = t_for(request, "admin.integrations.deck_sync_now_success", count=count)
        return RedirectResponse(f"/admin/integrations?deck_synced=success&deck_test_message={quote(message)}", status_code=303)
    except DeckError as e:
        return RedirectResponse(f"/admin/integrations?deck_synced=failed&deck_test_message={quote(str(e))}", status_code=303)
