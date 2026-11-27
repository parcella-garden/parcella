"""Club settings page (master data, modules, finance settings, navigation order)."""
from fastapi import APIRouter
from fastapi import Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import active_member_filter, get_db
from app.models import ClubBoardMember, ClubSetting, Member
from app.auth import require_system_admin
from app.crypto_utils import encrypt
from app.i18n import AVAILABLE_LANGUAGES, t_for
from app.l10n import AVAILABLE_CURRENCIES, AVAILABLE_REGIONS
from app.email_log import (
    MAX_RETENTION_DAYS as EMAIL_LOG_MAX_RETENTION_DAYS,
    RETENTION_SETTING as EMAIL_LOG_RETENTION_SETTING,
    parse_retention_days as parse_email_log_retention_days,
)
from app.branding import remove_logo_file, save_logo_upload
from app.nav_order import NAV_ORDER_DEFAULTS
from app.area_utils import compute_area_a_sqm, compute_area_b_sqm
from app.invoice_generation import (
    DEFAULT_INVOICE_NUMBER_FORMAT,
    INVOICE_NUMBER_FORMAT_EXAMPLES,
    is_valid_invoice_number_format,
)
from app.module_flags import MODULE_DEFAULTS
from app.services.applicants import (
    CONTACT_TEMPLATE_SETTING,
    RETENTION_SETTING,
    parse_retention_months,
)
from app.templating import templates
from app.services.admin import upsert_club_setting

router = APIRouter()


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
]

# Optional feature areas that each club can toggle on/off.
# Keys follow the convention "modul_<name>" (see app/module_flags.py).
# Name/description are resolved via translation keys (see below).
MODULE_FIELDS = [
    ("modul_work_hours", "admin.settings.modules.work_hours_name", "admin.settings.modules.work_hours_desc"),
    ("modul_water", "admin.settings.modules.water_name", "admin.settings.modules.water_desc"),
    ("modul_electricity", "admin.settings.modules.electricity_name", "admin.settings.modules.electricity_desc"),
    ("modul_insurance", "admin.settings.modules.insurance_name", "admin.settings.modules.insurance_desc"),
    ("modul_freescout_bridge", "admin.settings.modules.freescout_bridge_name", "admin.settings.modules.freescout_bridge_desc"),
    ("modul_purchase_requests", "admin.settings.modules.purchase_requests_name", "admin.settings.modules.purchase_requests_desc"),
    ("modul_calendar", "admin.settings.modules.calendar_name", "admin.settings.modules.calendar_desc"),
    ("modul_inventory", "admin.settings.modules.inventory_name", "admin.settings.modules.inventory_desc"),
    ("modul_tasks", "admin.settings.modules.tasks_name", "admin.settings.modules.tasks_desc"),
    ("modul_applicants", "admin.settings.modules.applicants_name", "admin.settings.modules.applicants_desc"),
    ("modul_external_contacts", "admin.settings.modules.external_contacts_name", "admin.settings.modules.external_contacts_desc"),
    ("modul_reporting", "admin.settings.modules.reporting_name", "admin.settings.modules.reporting_desc"),
    ("modul_notes", "admin.settings.modules.notes_name", "admin.settings.modules.notes_desc"),
    ("modul_processes", "admin.settings.modules.processes_name", "admin.settings.modules.processes_desc"),
    ("modul_mcp", "admin.settings.modules.mcp_name", "admin.settings.modules.mcp_desc"),
    ("modul_public_signup_api", "admin.settings.modules.public_signup_api_name", "admin.settings.modules.public_signup_api_desc"),
    ("modul_public_contact_api", "admin.settings.modules.public_contact_api_name", "admin.settings.modules.public_contact_api_desc"),
    ("modul_public_applicant_api", "admin.settings.modules.public_applicant_api_name", "admin.settings.modules.public_applicant_api_desc"),
    ("modul_announcements", "admin.settings.modules.announcements_name", "admin.settings.modules.announcements_desc"),
    ("modul_cloud_storage", "admin.settings.modules.cloud_storage_name", "admin.settings.modules.cloud_storage_desc"),
    ("modul_finances", "admin.settings.modules.finances_name", "admin.settings.modules.finances_desc"),
    ("modul_deck_sync", "admin.settings.modules.deck_sync_name", "admin.settings.modules.deck_sync_desc"),
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
    ("freescout_bridge", "nav.freescout_bridge"),
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
    ("applicants", "nav.applicants"),
    ("external_contacts", "nav.external_contacts"),
    ("reporting", "nav.reporting"),
    ("notes", "nav.notes"),
    ("processes", "nav.processes"),
]


@router.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_system_admin(request, db)

    result = await db.execute(select(ClubSetting))
    settings_map = {e.key: e.value for e in result.scalars().all()}

    resolved_fields = [(key, t_for(request, label_key)) for key, label_key in SETTINGS_FIELDS]
    resolved_finance_fields = [(key, t_for(request, label_key)) for key, label_key in FINANCE_SETTINGS_FIELDS]
    resolved_module_fields = [
        (
            key, t_for(request, name_key), t_for(request, desc_key),
            # Fallback for a module never explicitly saved yet -- must
            # match app/module_flags.py's actual MODULE_DEFAULTS, not a
            # hardcoded assumption, or a module defaulting to False
            # (e.g. one that opens a public endpoint) would render its
            # toggle as already ON before ever being saved.
            "true" if MODULE_DEFAULTS.get(key[len("modul_"):], True) else "false",
        )
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
        request, "admin/settings.html",
        {
            "request": request,
            "user": user,
            "settings_map": settings_map,
            "email_log_retention_days": parse_email_log_retention_days(settings_map.get(EMAIL_LOG_RETENTION_SETTING)),
            "email_log_max_retention_days": EMAIL_LOG_MAX_RETENTION_DAYS,
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

    # Applicant retention (issue #255): months after the last status
    # change; blank or 0 = keep forever. Only when the field was on the
    # form, so a form without it can't silently switch the purge off.
    if "applicant_retention_months" in form:
        months = parse_retention_months(form.get("applicant_retention_months"))
        await upsert_club_setting(
            db, RETENTION_SETTING, str(months) if months else "",
            "Months after the last status change before an applicant is deleted (blank = never)",
        )
    # Issue #270: email log retention in days (1-3650, otherwise the
    # 90-day default). Same "only when on the form" guard.
    if "email_log_retention_days" in form:
        await upsert_club_setting(
            db, EMAIL_LOG_RETENTION_SETTING,
            str(parse_email_log_retention_days(form.get("email_log_retention_days"))),
            "Days an email log entry is kept before it is deleted",
        )
    # Issue #267: the "Contact applicant" boilerplate; blank = the
    # translated default. Same "only when on the form" guard as above.
    if "applicant_contact_template" in form:
        await upsert_club_setting(
            db, CONTACT_TEMPLATE_SETTING, (form.get("applicant_contact_template") or "").strip()[:20000],
            "Boilerplate for the email to a new applicant (blank = built-in text)",
        )

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
