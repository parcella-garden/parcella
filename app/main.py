"""
Allotment garden association management -- main application.
"""
from contextlib import asynccontextmanager
from datetime import date
import asyncio
import logging

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.config import settings
from app.database import get_db, AsyncSessionLocal, active_member_filter
from app.models import User, UserRole, Member, Parcel, ParcelStatus, MemberParcel, Group, GroupMembership
from app.models import PurchaseRequest, PurchaseRequestStatus
from app.models import Ticket, TicketStatus
from app.models import Task
from app.birthdays import upcoming_birthdays
from app.auth import hash_password, get_current_user
from app.module_flags import load_module_flags
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

# Loaded at module import time (not only in the lifespan startup
# event), since ASGI test clients (e.g. httpx with ASGITransport) don't
# necessarily trigger lifespan events. load_translations() is a pure,
# fast file-read operation with no DB access -- unproblematic at import.
load_translations()
from app.templating import templates
from app.ticket_mailer import process_incoming_mails
from app.routers import auth, members, parcels, admin as admin_router, admin_groups as admin_groups_router, work_hours, insurance, tickets, purchase_requests, calendar as calendar_router, announcements as announcements_router, inventory as inventory_router, tasks as tasks_router, finances as finances_router
from app.routers.metering import create_metering_router
from app.models import MeteringMedium
from app.routers import api_auth, api_members, api_parcels, api_club_settings, api_stats
from app.routers import api_work_hours, api_insurance, api_tickets, api_purchase_requests, api_inventory, api_tasks
from app.routers import api_public
from app.routers.api_metering import create_metering_api_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def _ticket_inbox_polling_loop():
    """
    Polls the configured ticket mailbox for new emails every 2 minutes.
    Runs permanently in the background; errors are caught so a single
    failed poll doesn't end the loop.
    """
    while True:
        try:
            async with AsyncSessionLocal() as db:
                anzahl = await process_incoming_mails(db)
                if anzahl:
                    logger.info(f"Ticket mailbox: {anzahl} new email(s) processed.")
        except Exception as e:
            logger.error(f"Ticket mailbox polling failed: {e}")

        await asyncio.sleep(120)  # 2 minutes


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
                # until it's changed -- see password_change_middleware.
                must_change_password=True,
            )
            db.add(erster_admin)
            await db.commit()
            logger.warning(
                "First admin user created: admin@parcella.local / admin1234 "
                "-- you will be asked to set a new password on first login."
            )

    polling_task = asyncio.create_task(_ticket_inbox_polling_loop())
    update_check_task = asyncio.create_task(_update_check_polling_loop())
    cloud_backup_task = asyncio.create_task(_cloud_backup_polling_loop())
    yield
    polling_task.cancel()
    update_check_task.cancel()
    cloud_backup_task.cancel()


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
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.middleware("http")
async def modul_flags_middleware(request: Request, call_next):
    """
    Loads the module flags once per request (e.g. whether work hours is
    active) and stores them under request.state.module_flags. Templates
    and router dependencies (require_module) read from there without
    querying the DB again.
    """
    async with AsyncSessionLocal() as db:
        request.state.module_flags = await load_module_flags(db)
    response = await call_next(request)
    return response


@app.middleware("http")
async def nav_order_middleware(request: Request, call_next):
    """
    Loads the club's configured sidebar nav order once per request (see
    app/nav_order.py, issue #60) and stores it under
    request.state.nav_order. base.html sorts its nav-item macros by
    this instead of a fixed source order.
    """
    async with AsyncSessionLocal() as db:
        request.state.nav_order = await load_nav_order(db)
    response = await call_next(request)
    return response


@app.middleware("http")
async def sprache_middleware(request: Request, call_next):
    """
    Loads the currently configured language once per request (see
    app/i18n.py) and stores it under request.state.language. Templates
    (via the Jinja function `t`) and routers (via t_for(request, ...))
    read from there.
    """
    async with AsyncSessionLocal() as db:
        request.state.language = await load_current_language(db)
    response = await call_next(request)
    return response


@app.middleware("http")
async def l10n_middleware(request: Request, call_next):
    """
    Loads region and currency once per request (see app/l10n.py) and
    stores them under request.state.region / request.state.currency.
    Deliberately separate from language (sprache_middleware above) --
    region/currency are independent settings, see the app/l10n.py
    module docstring. Templates use the `money`, `number`, `address`
    filters/function.
    """
    async with AsyncSessionLocal() as db:
        request.state.region = await load_current_region(db)
        request.state.currency = await load_current_currency(db)
    response = await call_next(request)
    return response


@app.middleware("http")
async def permissions_middleware(request: Request, call_next):
    """
    Loads the current user's effective per-module permissions once per
    request and stores them under request.state.permissions, plus the
    two ADR 0041 group-derived flags (is_full_access/is_system_admin)
    -- see app/permissions.py. require_permission()/require_admin()/
    require_system_admin() and the has_perm/is_full_access/is_system_admin
    Jinja globals all read from here instead of re-querying. Anonymous
    requests get all-False permissions, same as get_user_permissions(None).

    Also loads the current user's group names into
    request.state.user_group_names -- the sidebar footer (base.html)
    shows these instead of the raw UserRole for the same reason the
    admin user list does (issue #129/ADR 0041): a non-legacy account's
    real access comes from group membership, not role, so showing e.g.
    "Read-only" for a full-access group member is actively misleading.
    """
    async with AsyncSessionLocal() as db:
        user = await get_current_user(request, db)
        request.state.permissions = await get_user_permissions(db, user)
        request.state.is_full_access = await is_full_access_user(db, user)
        request.state.is_system_admin = await is_system_admin_user(db, user)
        request.state.user_group_names = []
        if user is not None:
            result = await db.execute(
                select(Group.name)
                .join(GroupMembership, GroupMembership.group_id == Group.id)
                .where(GroupMembership.user_id == user.id)
            )
            request.state.user_group_names = list(result.scalars().all())
    response = await call_next(request)
    return response


@app.middleware("http")
async def new_participations_count_middleware(request: Request, call_next):
    """
    Issue #217: loads the "N work-session sign-ups in the last
    NEW_PARTICIPATION_WINDOW_DAYS days" count once per request and
    stores it under request.state.new_participations_count, driving the
    /work-hours/ nav badge (base.html) and the dashboard tile. Only
    queried for a logged-in user -- anonymous requests (public ICS
    feeds, login page) get 0 without a DB round-trip, since nothing
    anonymous-facing reads this. See docs/ADR/0079.
    """
    request.state.new_participations_count = 0
    async with AsyncSessionLocal() as db:
        user = await get_current_user(request, db)
        if user is not None:
            request.state.new_participations_count = await count_new_participations(db)
    response = await call_next(request)
    return response


CHANGE_PASSWORD_PATH = "/auth/change-password"
# Reachable while a forced password change is pending: the change form
# itself, logging out, and static assets (the page needs its CSS).
_PASSWORD_CHANGE_EXEMPT_PREFIXES = (CHANGE_PASSWORD_PATH, "/auth/logout", "/static/")


@app.middleware("http")
async def password_change_middleware(request: Request, call_next):
    """
    Sends a logged-in user whose account is flagged must_change_password
    (today: the bootstrap admin, whose password is the same documented
    default on every installation) to the change-password form, whatever
    page they asked for.

    Web UI only -- /api/v1 uses its own JWT auth, and the API side of the
    same rule lives where tokens are issued (app/routers/api_auth.py):
    an account in this state simply doesn't get a token, which is a
    clearer answer to an API client than a redirect to an HTML form.
    """
    # scope["path"], not request.url.path: the latter is rebuilt by
    # concatenating scheme/host/path and re-parsing, which known
    # Starlette issues can make disagree with the path that routing
    # actually used. Anything that decides whether a check applies must
    # read the same value the router does.
    path = request.scope.get("path", "")
    if path.startswith("/api/") or path.startswith(_PASSWORD_CHANGE_EXEMPT_PREFIXES):
        return await call_next(request)

    async with AsyncSessionLocal() as db:
        user = await get_current_user(request, db)
        must_change = bool(user and user.must_change_password)

    if must_change:
        return RedirectResponse(CHANGE_PASSWORD_PATH, status_code=302)
    return await call_next(request)


@app.middleware("http")
async def branding_middleware(request: Request, call_next):
    """Loads the club's display name and custom logo once per request
    (same pattern as module flags, language, and l10n above) and stores
    them under request.state.club_name / request.state.logo_url. See
    app/branding.py."""
    async with AsyncSessionLocal() as db:
        branding = await load_branding(db)
        request.state.club_name = branding["club_name"]
        # Cache-busting suffix so a re-uploaded logo is never served
        # stale from a browser's cache of the old image at this same
        # fixed URL -- see load_branding()'s docstring for why this is
        # appended here rather than baked into logo_url itself.
        request.state.logo_url = (
            f"{branding['logo_url']}?v={branding['logo_version']}" if branding["logo_url"] else None
        )
    response = await call_next(request)
    return response


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
    # password_change_middleware below. Here it decides whether the
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
app.include_router(tickets.router)
app.include_router(purchase_requests.router)
app.include_router(calendar_router.router)
app.include_router(announcements_router.router)
app.include_router(inventory_router.router)
app.include_router(tasks_router.router)
app.include_router(finances_router.router)

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
app.include_router(api_club_settings.router)
app.include_router(api_stats.router)
app.include_router(api_work_hours.router)
app.include_router(api_insurance.router)
app.include_router(api_inventory.router)
app.include_router(api_tasks.router)
app.include_router(api_tickets.router)
app.include_router(api_purchase_requests.router)
app.include_router(api_public.router)

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
        # active_only branch of _filtered_members_query().
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
        besetzte_ids = select(MemberParcel.parcel_id).distinct()
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

        # For the dashboard tile "Open purchase requests" -- only relevant
        # when the module is active (see request.state.module_flags in
        # the template), but the query costs nothing when empty/disabled.
        purchase_requests_open_count = await db.scalar(
            select(func.count()).select_from(PurchaseRequest).where(
                PurchaseRequest.status == PurchaseRequestStatus.OPEN
            )
        )

        # For the dashboard tile "Tickets" -- "open" here counts exactly
        # like the "Active" filter on /tickets/ (ACTIVE/ASSIGNED/WAITING,
        # see app/routers/tickets.py), NOT postponed/closed/deleted.
        tickets_open_count = await db.scalar(
            select(func.count()).select_from(Ticket).where(
                Ticket.status.in_([TicketStatus.ACTIVE, TicketStatus.ASSIGNED, TicketStatus.WAITING])
            )
        )
        tickets_spam_count = await db.scalar(
            select(func.count()).select_from(Ticket).where(
                Ticket.spam_suspected == True, Ticket.status != TicketStatus.DELETED
            )
        )

        # For the dashboard tile "Overdue tasks" (issue #127) -- "overdue"
        # here means exactly what the board already shows in red
        # (app/templates/tasks/board.html's kanban-card-overdue class):
        # a due_date in the past, regardless of which list the card is
        # currently in (there's no separate "done" flag to exclude by,
        # see docs/module-tasks.md -- lists are just free-text columns).
        tasks_overdue_count = await db.scalar(
            select(func.count()).select_from(Task).where(Task.due_date < date.today())
        )

    # Dashboard tile "Birthdays this week" -- independent of the Calendar
    # module flag, since birthdays are shown here purely for information
    # (no link/dependency on the calendar routes).
    birthdays_this_week = await upcoming_birthdays(db, within_days=7)

    stats = {
        "members_total": members_total or 0,
        "members_active": members_active or 0,
        "parcels_active": parcels_active or 0,
        "parcels_terminated": parcels_terminated or 0,
        "parcels_vacant": parcels_vacant or 0,
        "area_total_sqm": float(area_total or 0),
        "purchase_requests_open": purchase_requests_open_count or 0,
        "tickets_open": tickets_open_count or 0,
        "tickets_spam": tickets_spam_count or 0,
        "tasks_overdue": tasks_overdue_count or 0,
        # Reuses the count new_participations_count_middleware already
        # computed for this request (nav badge) instead of querying again.
        "new_participations": getattr(request.state, "new_participations_count", 0),
    }

    return templates.TemplateResponse(
        "dashboard.html",
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
        "fehler.html",
        {"request": request, "user": user, "code": 403, "meldung": meldung},
        status_code=403,
    )


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    async with AsyncSessionLocal() as db:
        user = await get_current_user(request, db)
    detail = getattr(exc, "detail", None)
    meldung = detail if detail and detail != "Not Found" else t_for(request, "errors.page_not_found")
    return templates.TemplateResponse(
        "fehler.html",
        {"request": request, "user": user, "code": 404, "meldung": meldung},
        status_code=404,
    )
