"""
Allotment garden association management -- main application.
"""
from contextlib import asynccontextmanager
from datetime import date
import asyncio
import logging
import posixpath
import re

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.gzip import GZipMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.config import settings
from app.database import get_db, AsyncSessionLocal, active_member_filter, current_or_upcoming_tenant_filter
from app.models import User, UserRole, Member, Parcel, ParcelStatus, MemberParcel, Group, GroupMembership
from app.birthdays import average_age, upcoming_birthdays
from app.auth import hash_password, get_current_user
from app.module_flags import load_module_flags
from app import settings_cache
from app.nav_order import load_nav_order
from app.i18n import load_translations, load_current_language, translate, t_for
from app import csrf
from app.security_headers import security_headers
from app.l10n import load_current_region, load_current_currency
from app.branding import load_branding
from app.update_check import refresh_update_check_cache
from app.cloud_backup import get_cloud_backup_settings, is_backup_due, run_cloud_backup_now
from app.area_utils import compute_area_a_sqm
from app.permissions import get_user_permissions, is_full_access_user, is_system_admin_user
from app.services.work_hours import count_new_participations
from app.nav_counts import NAV_COUNT_KEYS, load_nav_counts
from app.services.applicants import maybe_purge_expired_applicants
from app.services.processes import count_open as count_open_processes
from app.email_log import maybe_purge_expired_email_logs

# Loaded at module import time (not only in the lifespan startup
# event), since ASGI test clients (e.g. httpx with ASGITransport) don't
# necessarily trigger lifespan events. load_translations() is a pure,
# fast file-read operation with no DB access -- unproblematic at import.
load_translations()
from app.templating import templates
from app.helpdesk import get_helpdesk, load_helpdesk_web_url
from app.helpdesk.sync import sync_helpdesk_conversations
from app.deck_sync import sync_deck_tasks
from app.parcel_cloud_folders import apply_scheduled_folder_switches
from app.routers import auth, members, parcels, admin as admin_router, admin_groups as admin_groups_router, work_hours, insurance, support as support_router, purchase_requests, calendar as calendar_router, announcements as announcements_router, inventory as inventory_router, tasks as tasks_router, finances as finances_router
from app.routers.metering import create_metering_router
from app.models import MeteringMedium
from app.routers import api_auth, api_members, api_parcels, api_club_settings, api_stats, api_custom_fields
from app.routers import api_email_log
from app.routers import api_work_hours, api_insurance, api_helpdesk, api_purchase_requests, api_inventory, api_tasks
from app.routers import applicants as applicants_router, api_applicants
from app.routers import external_contacts as external_contacts_router, api_external_contacts
from app.routers import reporting as reporting_router, api_reporting
from app.routers import notes as notes_router, api_notes
from app.routers import processes as processes_router, api_processes
from app.routers import mcp as mcp_router
from app.routers import api_public
from app.routers import api_website, api_cloud_storage
from app.routers.api_metering import create_metering_api_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def _helpdesk_polling_loop():
    """
    Polls the active helpdesk for new/updated conversations every 5
    minutes, upserting app/models/'s HelpdeskConversationLink rows (see
    app/helpdesk/sync.py). Runs permanently in the background; errors are
    caught so a single failed poll doesn't end the loop. A no-op whenever
    no helpdesk is set up, or the active one can't list conversations
    (osTicket) -- see get_helpdesk() and the INBOX capability.
    """
    while True:
        try:
            async with AsyncSessionLocal() as db:
                provider = await get_helpdesk(db)
                if provider is not None:
                    try:
                        synced = await sync_helpdesk_conversations(db, provider)
                    finally:
                        await provider.aclose()
                    if synced:
                        logger.info(f"{provider.label}: {synced} conversation(s) synced.")
        except Exception as e:
            logger.error(f"Helpdesk polling failed: {e}")

        await asyncio.sleep(5 * 60)  # 5 minutes


async def _update_check_polling_loop():
    """
    Periodically checks GitHub releases for a newer Parcella version
    than the one currently running, caching the result (see
    app/update_check.py) so the admin dashboard can show it without an
    outbound call on every page load. Skipped when disabled in
    Admin -> Settings.
    """
    while True:
        try:
            async with AsyncSessionLocal() as db:
                await refresh_update_check_cache(db)
        except Exception as e:
            logger.error(f"Update check failed: {e}")

        await asyncio.sleep(6 * 60 * 60)  # 6 hours


async def _cloud_backup_polling_loop():
    """
    Ticks every 15 minutes and checks whether a scheduled cloud backup
    is due (see Admin -> System -> Cloud backups, app/cloud_backup.py),
    rather than sleeping for the full configured duration like the two
    loops above -- the backup frequency is user-configurable at
    runtime, so a single long asyncio.sleep couldn't react to a changed
    setting without an app restart. See docs/ADR/0055-scheduled-cloud-backups.md.
    run_cloud_backup_now() never raises on its own (it records
    success/failure in ClubSettings) -- the try/except here is pure
    defense in depth against something truly unexpected.
    """
    while True:
        try:
            async with AsyncSessionLocal() as db:
                cfg = await get_cloud_backup_settings(db)
                if is_backup_due(cfg):
                    await run_cloud_backup_now(db)
        except Exception as e:
            logger.error(f"Cloud backup polling failed: {e}")

        await asyncio.sleep(15 * 60)  # 15 minutes


async def _deck_sync_polling_loop():
    """
    Polls the configured Nextcloud Deck board for new/updated cards
    every 15 minutes, upserting app/models/'s ExternalTaskLink + Task
    rows (see app/deck_sync.py). A no-op whenever Deck sync isn't both
    enabled (Admin -> Settings) and configured (Admin -> Integrations)
    -- unlike the FreeScout loop above, this one also checks the module
    flag itself (not just whether credentials are present), so pausing
    an already-configured sync doesn't require clearing the credentials
    -- see docs/ADR/0086.
    """
    while True:
        try:
            async with AsyncSessionLocal() as db:
                flags = await load_module_flags(db)
                if flags.get("deck_sync"):
                    synced = await sync_deck_tasks(db)
                    if synced:
                        logger.info(f"Deck sync: {synced} card(s) synced.")
        except Exception as e:
            logger.error(f"Deck sync polling failed: {e}")

        await asyncio.sleep(15 * 60)  # 15 minutes


async def _cloud_folder_schedule_loop():
    """
    Hourly: carries out parcel cloud-folder switches whose date has come
    -- a parcel handed over on a future date retires the old tenants'
    folder and activates the new tenants' one on the handover date
    itself (app/parcel_cloud_folders.py, ADR 0102). A no-op when
    nothing is scheduled, so no module-flag check needed.
    """
    while True:
        try:
            async with AsyncSessionLocal() as db:
                switched = await apply_scheduled_folder_switches(db)
                if switched:
                    logger.info(f"Cloud folders: {switched} scheduled switch(es) applied.")
        except Exception as e:
            logger.error(f"Cloud folder schedule failed: {e}")

        await asyncio.sleep(60 * 60)  # 1 hour


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: create the first admin if the users table is empty."""
    async with AsyncSessionLocal() as db:
        user_count = await db.scalar(select(func.count()).select_from(User))
        if not user_count:
            erster_admin = User(
                email="admin@parcella.local",
                name="Administrator",
                password_hash=hash_password("admin1234"),
                role=UserRole.ADMIN,
                # This password is documented in the README and identical
                # on every fresh installation, so the account is unusable
                # until it's changed -- see request_context_middleware.
                must_change_password=True,
            )
            db.add(erster_admin)
            await db.commit()
            logger.warning(
                "First admin user created: admin@parcella.local / admin1234 "
                "-- you will be asked to set a new password on first login."
            )

    polling_task = asyncio.create_task(_helpdesk_polling_loop())
    update_check_task = asyncio.create_task(_update_check_polling_loop())
    cloud_backup_task = asyncio.create_task(_cloud_backup_polling_loop())
    deck_sync_task = asyncio.create_task(_deck_sync_polling_loop())
    folder_schedule_task = asyncio.create_task(_cloud_folder_schedule_loop())
    yield
    polling_task.cancel()
    update_check_task.cancel()
    cloud_backup_task.cancel()
    deck_sync_task.cancel()
    folder_schedule_task.cancel()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "REST API for managing an allotment garden association: members, parcels, "
        "assignments, and club settings. Authentication via JWT bearer token "
        "(see `/api/v1/auth/token` or `/api/v1/auth/login`).\n\n"
        "The interactive web UI (Jinja2 templates) runs in parallel at `/`, "
        "`/members/`, `/parcels/`, etc., and uses separate, cookie-based "
        "session authentication."
    ),
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# Static files
class _CachedStaticFiles(StaticFiles):
    """Vendor files live in versioned folders (vendor/<package>@<version>/),
    so browsers may keep them for good; everything else (uploads, the
    logo, favicons) can change under the same name and is revalidated by
    ETag on every use (issue #413)."""

    async def get_response(self, path, scope):
        response = await super().get_response(path, scope)
        if response.status_code in (200, 304):
            response.headers["Cache-Control"] = (
                "public, max-age=31536000, immutable" if path.startswith("vendor/") else "no-cache"
            )
        return response


# gzip for static files only: HTML pages carry the CSRF token next to
# reflected input (search boxes), the shape BREACH needs.
app.mount("/static", GZipMiddleware(_CachedStaticFiles(directory="app/static"), minimum_size=1000), name="static")


CHANGE_PASSWORD_PATH = "/auth/change-password"
# Reachable while a forced password change is pending: the change form
# itself, logging out, and static assets (the page needs its CSS).
_PASSWORD_CHANGE_EXEMPT_PREFIXES = (CHANGE_PASSWORD_PATH, "/auth/logout", "/static/")

# Static files read nothing from request.state (issue #412); their 404
# is plain text for the same reason (see not_found_handler).
_STATIC_PREFIX = "/static/"


async def _load_club_settings(db: AsyncSession) -> dict:
    return {
        # e.g. whether work hours is active; require_module() and the
        # templates read request.state.module_flags.
        "module_flags": await load_module_flags(db),
        # Only the active helpdesk's web address (no credentials), for
        # base.html's "Support" link for members without freescout_bridge.
        "helpdesk_web_url": await load_helpdesk_web_url(db),
        # t()/t_for() read request.state.language (app/i18n.py).
        "language": await load_current_language(db),
        # Independent of language (app/l10n.py): money/number/address.
        "region": await load_current_region(db),
        "currency": await load_current_currency(db),
        # Sidebar order (app/nav_order.py, issue #60).
        "nav_order": await load_nav_order(db),
    }


@app.middleware("http")
async def request_context_middleware(request: Request, call_next):
    """
    Loads everything the templates and permission checks read from
    request.state, in ONE session with ONE user lookup (issue #412; this
    was eight middlewares, three of them looking up the user).

    - Club settings (app/settings_cache.py caches them per process).
    - Branding: club name and logo URL with its cache-busting ?v= (see
      load_branding() for why the version is the file's mtime).
    - Web UI only: the user's permissions, the two ADR 0041 group flags
      and group names (the sidebar footer shows those, not the raw
      UserRole -- issue #129), and the nav badge counts (issue #217,
      ADR 0079/0100), which also run the throttled retention purges
      (issues #255, #270). /api/v1 authenticates by token instead.
    - A user flagged must_change_password (the bootstrap admin) is sent
      to the change-password form, whatever page they asked for; the
      API side of that rule is where tokens are issued.

    scope["path"], not request.url.path: the latter is rebuilt and
    re-parsed and can disagree with the path routing actually used.
    """
    path = request.scope.get("path", "")
    if path.startswith(_STATIC_PREFIX):
        return await call_next(request)
    is_api = path.startswith("/api/")

    state = request.state
    state.new_participations_count = 0
    state.nav_counts = dict.fromkeys(NAV_COUNT_KEYS, 0)
    must_change = False
    async with AsyncSessionLocal() as db:
        club_settings = settings_cache.get()
        if club_settings is None:
            generation = settings_cache.generation()
            club_settings = await _load_club_settings(db)
            settings_cache.put(club_settings, generation)
        for key, value in club_settings.items():
            setattr(state, key, value)

        branding = await load_branding(db)
        state.club_name = branding["club_name"]
        state.logo_url = (
            f"{branding['logo_url']}?v={branding['logo_version']}" if branding["logo_url"] else None
        )

        if not is_api:
            user = await get_current_user(request, db)
            must_change = bool(user and user.must_change_password) and not path.startswith(_PASSWORD_CHANGE_EXEMPT_PREFIXES)
            state.permissions = await get_user_permissions(db, user)
            state.is_full_access = await is_full_access_user(db, user)
            state.is_system_admin = await is_system_admin_user(db, user)
            state.user_group_names = []
            if user is not None:
                state.user_group_names = list((await db.execute(
                    select(Group.name)
                    .join(GroupMembership, GroupMembership.group_id == Group.id)
                    .where(GroupMembership.user_id == user.id)
                )).scalars().all())
                if not must_change:
                    state.new_participations_count = await count_new_participations(db)
                    state.nav_counts = await load_nav_counts(db)
                    await maybe_purge_expired_applicants(db)
                    await maybe_purge_expired_email_logs(db)

    if must_change:
        return RedirectResponse(CHANGE_PASSWORD_PATH, status_code=302)
    return await call_next(request)


# NOTE ON ORDERING: Starlette runs the LAST-REGISTERED middleware
# FIRST. The two below are therefore deliberately the last ones in this
# file -- CSRF has to reject a forged request before any of the
# per-request loaders above do their DB work, and the security headers
# have to be attached to every response, including that rejection and
# anything else short-circuited further in.

@app.middleware("http")
async def csrf_middleware(request: Request, call_next):
    """Double-submit CSRF protection for the cookie-authenticated web UI
    -- see app/csrf.py for the mechanism and why /api/** is exempt.

    Rejecting here rather than in a per-route dependency means no
    handler can forget the check. Minting the token here for every
    request that doesn't have one is what makes it available to
    `csrf_field()` in the very first form a visitor sees -- the login
    form, whose POST is protected like any other.
    """
    cookie_token = request.cookies.get(csrf.COOKIE_NAME)
    token = cookie_token or csrf.new_token()
    request.state.csrf_token = token

    # scope["path"] rather than request.url.path -- see the note in
    # request_context_middleware below. Here it decides whether the
    # exemption applies, so a disagreement would mean skipping the
    # check on a route that needs it.
    path = request.scope.get("path", "")
    if request.method in csrf.UNSAFE_METHODS and not csrf.is_exempt(path):
        submitted = await csrf.submitted_token(request)
        if not csrf.tokens_match(submitted, cookie_token or ""):
            logger.warning(
                "Rejected %s %s: missing or invalid CSRF token",
                request.method, path,
            )
            # request.state.language isn't loaded yet at this point (that
            # middleware runs further in), so the club's language is
            # fetched here -- only on the rejection path, which is rare.
            async with AsyncSessionLocal() as db:
                language = await load_current_language(db)
            return PlainTextResponse(
                translate("errors.csrf_invalid", language), status_code=403,
            )

    response = await call_next(request)
    if cookie_token != token:
        response.set_cookie(
            csrf.COOKIE_NAME, token,
            max_age=csrf.COOKIE_MAX_AGE,
            httponly=True,  # compared server-side, so JS never needs to read it
            samesite="lax",
            secure=not settings.is_development,
        )
    return response


# Private uploads (process files, ADR 0136) live on the persisted uploads
# volume next to the public ones, but are never served from /static --
# only through their permission-checked download routes. The path is
# normalized first: a literal prefix check alone is sidestepped with
# "/static/uploads//private/..." or "/static/uploads/./private/...",
# which StaticFiles would still resolve to the same file.
_PRIVATE_UPLOADS_PREFIX = "/static/uploads/private"


@app.middleware("http")
async def private_uploads_blocked(request: Request, call_next):
    # scope["path"] is the decoded path StaticFiles itself resolves.
    # request.url.path is not: it is re-parsed with urlsplit, so a decoded
    # "%23" or "%3F" ("/static/uploads/%23/../private/...") would cut it
    # short and slip past the check (security review).
    candidates = {request.scope.get("path") or "", request.url.path}
    for raw in candidates:
        path = posixpath.normpath(re.sub(r"/+", "/", raw))
        if path == _PRIVATE_UPLOADS_PREFIX or path.startswith(_PRIVATE_UPLOADS_PREFIX + "/"):
            return PlainTextResponse("Not Found", status_code=404)
    return await call_next(request)


@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    """Attaches the security response headers (CSP, nosniff, frame
    options, referrer policy, HSTS outside development) to every
    response, static files and error pages included. See
    app/security_headers.py for what the policy does and does not
    promise."""
    response = await call_next(request)
    for header, value in security_headers().items():
        response.headers.setdefault(header, value)
    return response


# Register routers -- Web UI (Jinja2)
app.include_router(auth.router)
app.include_router(members.router)
app.include_router(parcels.router)
app.include_router(admin_router.router)
app.include_router(admin_groups_router.router)
app.include_router(work_hours.router)
app.include_router(insurance.router)
app.include_router(support_router.router)
app.include_router(support_router.legacy_router)
app.include_router(purchase_requests.router)
app.include_router(calendar_router.router)
app.include_router(announcements_router.router)
app.include_router(announcements_router.link_router)
app.include_router(inventory_router.router)
app.include_router(tasks_router.router)
app.include_router(finances_router.router)
app.include_router(applicants_router.router)
app.include_router(external_contacts_router.router)
app.include_router(reporting_router.router)
app.include_router(notes_router.router)
app.include_router(processes_router.router)

# Metering: ONE codebase (app/routers/metering.py), instantiated twice
# for water and electricity -- see create_metering_router().
water_router = create_metering_router(
    medium=MeteringMedium.WATER, url_prefix="/water", modul_name="water",
    medium_label_key="metering.medium.water", unit="m³", icon="bi-droplet", decimal_places=1,
)
electricity_router = create_metering_router(
    medium=MeteringMedium.ELECTRICITY, url_prefix="/electricity", modul_name="electricity",
    medium_label_key="metering.medium.electricity", unit="kWh", icon="bi-lightning-charge", decimal_places=0,
)
app.include_router(water_router)
app.include_router(electricity_router)

# Register routers -- REST API (JSON, JWT auth)
app.include_router(api_auth.router)
app.include_router(api_members.router)
app.include_router(api_parcels.router)
app.include_router(api_custom_fields.router)
app.include_router(api_club_settings.router)
app.include_router(api_email_log.router)
app.include_router(api_stats.router)
app.include_router(api_work_hours.router)
app.include_router(api_insurance.router)
app.include_router(api_inventory.router)
app.include_router(api_tasks.router)
app.include_router(api_applicants.router)
app.include_router(api_external_contacts.router)
app.include_router(api_reporting.router)
app.include_router(api_notes.router)
app.include_router(api_processes.router)
app.include_router(api_processes.template_router)
app.include_router(mcp_router.router)
app.include_router(api_helpdesk.router)
app.include_router(api_helpdesk.legacy_router)
app.include_router(api_helpdesk.settings_router)
app.include_router(api_purchase_requests.router)
app.include_router(api_public.router)
app.include_router(api_website.router)
app.include_router(api_website.announcement_router)
app.include_router(api_cloud_storage.router)

api_water_router = create_metering_api_router(MeteringMedium.WATER, "/water", "water")
api_electricity_router = create_metering_api_router(MeteringMedium.ELECTRICITY, "/electricity", "electricity")
app.include_router(api_water_router)
app.include_router(api_electricity_router)


@app.get("/", response_class=HTMLResponse)
async def startseite(request: Request):
    async with AsyncSessionLocal() as db:
        user = await get_current_user(request, db)

        if not user:
            return RedirectResponse("/auth/login", status_code=302)

        members_total = await db.scalar(
            select(func.count()).where(active_member_filter())
        )
        # Issue #200: members_total (above) still counts a blank
        # member_since as active, same as active_member_filter() itself
        # (deliberate, issue #167). members_active is the stricter set
        # that also backs the dashboard card's "Show" link -- only
        # members with a confirmed member_since, i.e. exactly the rows
        # /members/?active_only=true returns and the "active" (not
        # "pending") badge shows. Keep this in sync with the
        # active_only branch of MemberListFilter.apply() (app/member_filters.py).
        members_active = await db.scalar(
            select(func.count()).where(active_member_filter(), Member.member_since.is_not(None))
        )
        parcels_active = await db.scalar(
            select(func.count()).select_from(Parcel).where(
                Parcel.status == ParcelStatus.ACTIVE
            )
        )
        parcels_terminated = await db.scalar(
            select(func.count()).select_from(Parcel).where(
                Parcel.status == ParcelStatus.TERMINATED
            )
        )
        # Issue #360: tenancies are historized (ADR 0005), so "has ever had
        # a MemberParcel row" made a parcel occupied forever. Only a
        # tenancy that hasn't ended (current or upcoming) occupies it now.
        besetzte_ids = select(MemberParcel.parcel_id).where(current_or_upcoming_tenant_filter()).distinct()
        parcels_vacant = await db.scalar(
            select(func.count()).select_from(Parcel).where(
                Parcel.status == ParcelStatus.ACTIVE,
                Parcel.id.not_in(besetzte_ids)
            )
        )
        # Every parcel that's ever been leased (active or terminated) --
        # not just currently-active ones (issue #80) -- same figure as
        # app/area_utils.py's Area A, reused directly rather than
        # duplicating the query so this stat and the settings page's
        # Area A can never drift apart (issue #168 added the COMMUNAL
        # exclusion there; duplicating it here would have been an easy
        # spot to miss).
        area_total = await compute_area_a_sqm(db)
        neueste_result = await db.execute(
            select(Member)
            .where(active_member_filter())
            .order_by(Member.created_at.desc())
            .limit(5)
        )
        recent_members = neueste_result.scalars().all()

        # Dashboard tile "Birthdays this week" -- independent of the Calendar
        # module flag, since birthdays are shown here purely for information
        # (no link/dependency on the calendar routes). Must stay inside the
        # session block: run after it, the closed session silently opened a
        # new transaction that nobody ended, leaking a connection "idle in
        # transaction" on every dashboard load -- enough to block a backup
        # restore's DROP TABLE until it timed out.
        birthdays_this_week = await upcoming_birthdays(db, within_days=7)
        members_average_age = await average_age(db)
        processes_open = await count_open_processes(db)

    stats = {
        "members_total": members_total or 0,
        "members_active": members_active or 0,
        "members_average_age": members_average_age,
        "parcels_active": parcels_active or 0,
        "parcels_terminated": parcels_terminated or 0,
        "parcels_vacant": parcels_vacant or 0,
        "area_total_sqm": float(area_total or 0),
        # The "needs attention" tiles reuse the counts request_context_middleware
        # already computed for this request (nav badges) instead of querying
        # again -- one source, so badge and tile can't disagree (ADR 0100).
        **request.state.nav_counts,
        "new_participations": getattr(request.state, "new_participations_count", 0),
        "processes_open": processes_open,
    }

    return templates.TemplateResponse(
        request, "dashboard.html",
        {
            "request": request,
            "user": user,
            "stats": stats,
            "recent_members": recent_members,
            "birthdays_this_week": birthdays_this_week,
            "today_date": date.today(),
        },
    )


@app.exception_handler(403)
async def forbidden_handler(request: Request, exc):
    async with AsyncSessionLocal() as db:
        user = await get_current_user(request, db)
    # exc.detail often carries a specific, helpful reason (e.g. "the
    # requester may not also approve their own purchase request"). This
    # used to be discarded entirely in favor of a generic fallback --
    # which made a number of carefully worded (and translated) error
    # messages elsewhere effectively invisible. Now: show the specific
    # message if present. Important: FastAPI auto-fills "detail" with
    # the generic English HTTP status phrase ("Forbidden") when no
    # custom text was given at raise time -- detect exactly that case
    # and fall back to the translated generic message instead.
    detail = getattr(exc, "detail", None)
    meldung = detail if detail and detail != "Forbidden" else t_for(request, "errors.no_permission")
    return templates.TemplateResponse(
        request, "fehler.html",
        {"request": request, "user": user, "code": 403, "meldung": meldung},
        status_code=403,
    )


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    if request.scope.get("path", "").startswith(_STATIC_PREFIX):
        return PlainTextResponse("Not Found", status_code=404)
    async with AsyncSessionLocal() as db:
        user = await get_current_user(request, db)
    detail = getattr(exc, "detail", None)
    meldung = detail if detail and detail != "Not Found" else t_for(request, "errors.page_not_found")
    return templates.TemplateResponse(
        request, "fehler.html",
        {"request": request, "user": user, "code": 404, "meldung": meldung},
        status_code=404,
    )
