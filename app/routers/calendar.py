"""
Calendar module router.

Four calendars, each with a simple upcoming-items list (no full
month-grid view -- deliberately kept simple per the feature request)
and an ICS export:

- Community calendar: member meetings + parcel inspections (entered
  here) merged with work sessions (read directly from WorkSession, not
  duplicated). Its ICS feed is fully public -- meant to be embedded on
  the club's public WordPress site, which can't authenticate with this
  app's session cookies.
- Birthdays: derived entirely from Member.date_of_birth, nothing stored.
- Council presence: scheduled on-site slots for board/council members.
- Council absence: self-reported absence periods for any user account.

The latter three ICS feeds require a secret token (see app/ics_utils.py)
rather than a login, since calendar apps subscribing to a feed URL
can't do session-cookie authentication either -- the token is the
practical equivalent of a login for a subscription URL.
"""
import re
import secrets
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Literal, Optional

from fastapi import APIRouter, Request, Form, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import (
    CalendarEvent, CalendarEventType, WorkSession, SessionType,
    CouncilPresence, CouncilAbsence, User, CustomCalendar,
    InventoryItem, InventoryOwnerType, ItemLoan,
)
from app.auth import require_admin
from app.permissions import is_full_access_user, get_user_permissions, has_permission
from app.auth import require_user
from app.permissions import require_permission
from app.module_flags import require_module
from app.i18n import t_for, load_current_language
from app.l10n import load_current_region
from app.branding import load_branding
from app.pdf_chrome import load_org_footer_context
from app.birthdays import (
    upcoming_birthdays, all_birthdays_for_calendar, birthday_rows, sort_birthdays, birthday_range_end,
    BIRTHDAY_RANGES, BIRTHDAY_SORTS, DEFAULT_BIRTHDAY_RANGE, DEFAULT_BIRTHDAY_SORT, ROUND_BIRTHDAY_INTERVAL,
)
from app.birthday_calendar_pdf import render_birthday_calendar_pdf
from app.ics_utils import (
    get_or_create_ics_token, verify_ics_token,
    build_community_calendar, build_birthday_calendar,
    build_council_presence_calendar, build_council_absence_calendar, build_custom_calendar,
)
from app.templating import templates

router = APIRouter(
    prefix="/calendar",
    tags=["calendar"],
    dependencies=[Depends(require_module("calendar"))],
)


def _ics_response(ical_bytes: bytes, filename: str) -> Response:
    return Response(
        content=ical_bytes,
        media_type="text/calendar; charset=utf-8",
        headers={"Content-Disposition": f'inline; filename="{filename}"'},
    )


# ---------------------------------------------------------------------------
# Hub -- removed as a standalone overview page (redundant once every
# sub-calendar links its own ICS feed directly, see below); kept as a
# redirect so old bookmarks/links to /calendar/ still land somewhere
# useful rather than 404ing.
# ---------------------------------------------------------------------------

@router.get("/", response_class=HTMLResponse)
async def calendar_hub(request: Request, db: AsyncSession = Depends(get_db)):
    await require_permission(request, db, "calendar", "read")
    return RedirectResponse("/calendar/community", status_code=302)


# ---------------------------------------------------------------------------
# Community calendar (member meetings, parcel inspections, work sessions)
# ---------------------------------------------------------------------------

@router.get("/community", response_class=HTMLResponse)
async def community_overview(request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_permission(request, db, "calendar", "read")

    events_result = await db.execute(
        select(CalendarEvent)
        .where(CalendarEvent.start_date >= date.today(), CalendarEvent.calendar_id.is_(None))
        .order_by(CalendarEvent.start_date)
    )
    events = events_result.scalars().all()

    # STANDARD only -- SPECIAL sessions are spontaneous/unplanned (e.g.
    # "paint the garden bench today") and deliberately don't show up
    # here, since they aren't something members plan their week around.
    # Same filter as the ICS feed (app/ics_utils.py's
    # build_community_calendar) -- keep both in sync if this changes.
    sessions_result = await db.execute(
        select(WorkSession)
        .where(WorkSession.date >= date.today(), WorkSession.type == SessionType.STANDARD)
        .order_by(WorkSession.date)
    )
    sessions = sessions_result.scalars().all()

    # Merge into one date-sorted list for display: (date, kind, item)
    combined = [("event", e.start_date, e) for e in events] + [("session", s.date, s) for s in sessions]
    combined.sort(key=lambda row: row[1])

    return templates.TemplateResponse(request, "calendar/community.html", {
        "request": request, "user": user, "combined": combined,
        "CalendarEventType": CalendarEventType,
    })


@router.post("/community/new")
async def community_event_create(
    request: Request,
    title: str = Form(...),
    event_type: str = Form("OTHER"),
    description: str = Form(""),
    location: str = Form(""),
    start_date: str = Form(...),
    start_time: str = Form(""),
    end_date: str = Form(""),
    end_time: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    user = await require_permission(request, db, "calendar", "write")

    event = CalendarEvent(
        title=title.strip(),
        event_type=CalendarEventType(event_type),
        description=description.strip() or None,
        location=location.strip() or None,
        start_date=date.fromisoformat(start_date),
        start_time=start_time or None,
        end_date=date.fromisoformat(end_date) if end_date else None,
        end_time=end_time or None,
        created_by_id=user.id,
    )
    db.add(event)
    await db.commit()
    return RedirectResponse("/calendar/community", status_code=302)


@router.post("/community/{event_id}/delete")
async def community_event_delete(event_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    await require_permission(request, db, "calendar", "delete")
    result = await db.execute(
        select(CalendarEvent).where(CalendarEvent.id == event_id, CalendarEvent.calendar_id.is_(None))
    )
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=404, detail=t_for(request, "calendar.errors.event_not_found"))
    await db.delete(event)
    await db.commit()
    return RedirectResponse("/calendar/community", status_code=302)


@router.get("/community.ics")
async def community_ics(request: Request, db: AsyncSession = Depends(get_db)):
    """Public, unauthenticated -- meant for embedding on the club's
    public WordPress site. Contains only already-public information
    (meeting/inspection announcements and work session schedules)."""
    cal = await build_community_calendar(db, base_url=request.url.hostname or "parcella.local")
    return _ics_response(cal.to_ical(), "community.ics")


@router.get("/community.json")
async def community_json(db: AsyncSession = Depends(get_db)):
    """JSON twin of community.ics above, for driving a styled widget
    (e.g. the parcella-connector WordPress plugin's [parcella_calendar]
    shortcode) instead of a calendar-app subscription. Same public,
    unauthenticated posture and same underlying data -- CalendarEvent
    rows plus STANDARD work sessions, SPECIAL sessions excluded -- kept
    in sync with community_overview() and build_community_calendar()
    above; update all three together if this merge logic ever changes."""
    events_result = await db.execute(
        select(CalendarEvent)
        .where(CalendarEvent.start_date >= date.today(), CalendarEvent.calendar_id.is_(None))
        .order_by(CalendarEvent.start_date)
    )
    items = [
        {
            "kind": "event",
            "title": e.title,
            "date": e.start_date.isoformat(),
            "end_date": e.end_date.isoformat() if e.end_date else None,
            "time_from": e.start_time,
            "time_until": e.end_time,
            "location": e.location,
            "description": e.description,
        }
        for e in events_result.scalars().all()
    ]

    sessions_result = await db.execute(
        select(WorkSession)
        .where(WorkSession.date >= date.today(), WorkSession.type == SessionType.STANDARD)
        .order_by(WorkSession.date)
    )
    items += [
        {
            "kind": "session",
            "title": f"Work session: {s.title}",
            "date": s.date.isoformat(),
            "end_date": None,
            "time_from": s.time_from,
            "time_until": s.time_until,
            "location": None,
            "description": s.description,
        }
        for s in sessions_result.scalars().all()
    ]

    items.sort(key=lambda item: item["date"])
    return items


# ---------------------------------------------------------------------------
# Custom calendars (issue #314, ADR 0131): admin-defined, never public
# ---------------------------------------------------------------------------

_HEX_COLOR_RE = re.compile(r"^#[0-9a-fA-F]{6}$")


def _clean_color(value: str) -> str:
    value = (value or "").strip()
    return value.lower() if _HEX_COLOR_RE.match(value) else "#2e7d32"


async def _visible_calendars(db: AsyncSession, user: User, include_archived: bool = False) -> list[CustomCalendar]:
    query = select(CustomCalendar).order_by(CustomCalendar.name)
    if not include_archived:
        query = query.where(CustomCalendar.is_active.is_(True))
    calendars = (await db.execute(query)).scalars().all()
    if await is_full_access_user(db, user):
        return list(calendars)
    return [c for c in calendars if not c.full_access_only]


async def _get_visible_calendar_or_404(request: Request, db: AsyncSession, user: User, calendar_id: str) -> CustomCalendar:
    """404 -- not 403 -- for a calendar this user may not see, so its
    existence doesn't leak."""
    calendar = await db.get(CustomCalendar, calendar_id)
    if calendar is None or (calendar.full_access_only and not await is_full_access_user(db, user)):
        raise HTTPException(status_code=404, detail=t_for(request, "calendar.errors.calendar_not_found"))
    return calendar


@router.get("/custom", response_class=HTMLResponse)
async def custom_calendars_index(request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_permission(request, db, "calendar", "read")
    is_admin = await is_full_access_user(db, user)
    calendars = await _visible_calendars(db, user, include_archived=is_admin)
    perms = await get_user_permissions(db, user)
    return templates.TemplateResponse(request, "calendar/custom_index.html", {
        "request": request, "user": user, "calendars": calendars, "can_manage": is_admin,
        "show_resources": bool(request.state.module_flags.get("inventory")) and has_permission(perms, "inventory", "read"),
    })


@router.post("/custom/new")
async def custom_calendar_create(request: Request, db: AsyncSession = Depends(get_db)):
    await require_admin(request, db)
    form = await request.form()
    name = (form.get("name") or "").strip()[:100]
    if not name:
        return RedirectResponse("/calendar/custom", status_code=303)
    db.add(CustomCalendar(
        name=name, description=(form.get("description") or "").strip() or None,
        color=_clean_color(form.get("color")), full_access_only=form.get("full_access_only") == "true",
    ))
    await db.commit()
    return RedirectResponse("/calendar/custom", status_code=303)


@router.post("/custom/{calendar_id}/edit")
async def custom_calendar_update(calendar_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    """Rename/recolour, change visibility, archive or reactivate. There's
    no delete: archiving keeps the calendar's past events (ADR 0005)."""
    await require_admin(request, db)
    calendar = await db.get(CustomCalendar, calendar_id)
    if calendar is None:
        raise HTTPException(status_code=404, detail=t_for(request, "calendar.errors.calendar_not_found"))
    form = await request.form()
    name = (form.get("name") or "").strip()[:100]
    if name:
        calendar.name = name
    calendar.description = (form.get("description") or "").strip() or None
    calendar.color = _clean_color(form.get("color"))
    full_access_only = form.get("full_access_only") == "true"
    # A new feed secret whenever the audience changes (old subscribers of
    # a now board-only calendar must lose access) or on request (e.g.
    # someone left the board).
    if full_access_only != calendar.full_access_only or form.get("new_feed_link") == "true":
        calendar.feed_token = secrets.token_urlsafe(32)
    calendar.full_access_only = full_access_only
    calendar.is_active = form.get("is_active") == "true"
    await db.commit()
    return RedirectResponse("/calendar/custom", status_code=303)


@router.get("/custom/{calendar_id}", response_class=HTMLResponse)
async def custom_calendar_overview(calendar_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_permission(request, db, "calendar", "read")
    calendar = await _get_visible_calendar_or_404(request, db, user, calendar_id)
    events = (await db.execute(
        select(CalendarEvent)
        .where(CalendarEvent.calendar_id == calendar.id, CalendarEvent.start_date >= date.today())
        .order_by(CalendarEvent.start_date, CalendarEvent.start_time)
    )).scalars().all()
    return templates.TemplateResponse(request, "calendar/custom.html", {
        "request": request, "user": user, "calendar": calendar, "events": events,
    })


@router.post("/custom/{calendar_id}/new")
async def custom_calendar_event_create(
    calendar_id: str,
    request: Request,
    title: str = Form(...),
    description: str = Form(""),
    location: str = Form(""),
    start_date: str = Form(...),
    start_time: str = Form(""),
    end_date: str = Form(""),
    end_time: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    user = await require_permission(request, db, "calendar", "write")
    calendar = await _get_visible_calendar_or_404(request, db, user, calendar_id)
    if not calendar.is_active:
        raise HTTPException(status_code=409, detail=t_for(request, "calendar.errors.calendar_archived"))
    try:
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date) if end_date else None
    except ValueError:
        raise HTTPException(status_code=400, detail=t_for(request, "calendar.errors.invalid_date"))
    db.add(CalendarEvent(
        calendar_id=calendar.id, event_type=CalendarEventType.OTHER,
        title=title.strip()[:255], description=description.strip() or None,
        location=location.strip()[:255] or None, start_date=start, start_time=_clean_time(start_time),
        end_date=end, end_time=_clean_time(end_time), created_by_id=user.id,
    ))
    await db.commit()
    return RedirectResponse(f"/calendar/custom/{calendar.id}", status_code=303)


@router.post("/custom/{calendar_id}/{event_id}/delete")
async def custom_calendar_event_delete(
    calendar_id: str, event_id: str, request: Request, db: AsyncSession = Depends(get_db),
):
    user = await require_permission(request, db, "calendar", "delete")
    calendar = await _get_visible_calendar_or_404(request, db, user, calendar_id)
    event = (await db.execute(
        select(CalendarEvent).where(CalendarEvent.id == event_id, CalendarEvent.calendar_id == calendar.id)
    )).scalar_one_or_none()
    if event is None:
        raise HTTPException(status_code=404, detail=t_for(request, "calendar.errors.event_not_found"))
    await db.delete(event)
    await db.commit()
    return RedirectResponse(f"/calendar/custom/{calendar.id}", status_code=303)


@router.get("/custom/{calendar_id}/feed.ics")
async def custom_calendar_ics(
    calendar_id: str, request: Request, token: Optional[str] = Query(None), db: AsyncSession = Depends(get_db),
):
    """Private feed with the calendar's OWN secret (feed_token), never
    the installation-wide ICS token: that one is shown to every calendar
    reader, so it would open board-only calendars to everyone (ADR 0131)."""
    calendar = await db.get(CustomCalendar, calendar_id)
    if calendar is None or not calendar.is_active or not verify_ics_token(token, calendar.feed_token):
        raise HTTPException(status_code=404)
    cal = await build_custom_calendar(db, calendar, base_url=request.url.hostname or "parcella.local")
    return _ics_response(cal.to_ical(), "calendar.ics")


def _clean_time(value: str) -> Optional[str]:
    value = (value or "").strip()
    return value if re.fullmatch(r"([01]\d|2[0-3]):[0-5]\d", value) else None


# ---------------------------------------------------------------------------
# Resources (issue #314): club-owned borrowable items and who has them
# right now. Read-only; loans have no planned period yet, so this shows
# current loans only (kermie's call, 2026-11-15).
# ---------------------------------------------------------------------------

@router.get("/resources", response_class=HTMLResponse)
async def resources_overview(request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_permission(request, db, "calendar", "read")
    # Who borrowed what is member data from the inventory module: its own
    # permission and module switch apply, not just the calendar's.
    if not request.state.module_flags.get("inventory"):
        raise HTTPException(status_code=404)
    await require_permission(request, db, "inventory", "read")

    items = (await db.execute(
        select(InventoryItem)
        .where(
            InventoryItem.owner_type == InventoryOwnerType.CLUB,
            InventoryItem.is_borrowable.is_(True),
            InventoryItem.retired_at.is_(None),
        )
        .options(selectinload(InventoryItem.category), selectinload(InventoryItem.loans).selectinload(ItemLoan.member))
        .order_by(InventoryItem.name)
    )).scalars().all()
    rows = []
    for item in items:
        current = sorted((l for l in item.loans if l.returned_date is None), key=lambda l: l.borrowed_date)
        rows.append({"item": item, "loans": current})
    return templates.TemplateResponse(request, "calendar/resources.html", {
        "request": request, "user": user, "rows": rows,
    })


# ---------------------------------------------------------------------------
# Birthdays
# ---------------------------------------------------------------------------

BirthdayRange = Literal["month", "quarter", "year"]
BirthdaySort = Literal["date", "name", "plot"]


@router.get("/birthdays", response_class=HTMLResponse)
async def birthdays_overview(
    request: Request,
    range_key: BirthdayRange = Query(DEFAULT_BIRTHDAY_RANGE, alias="range"),
    sort: BirthdaySort = Query(DEFAULT_BIRTHDAY_SORT),
    db: AsyncSession = Depends(get_db),
):
    """Upcoming birthdays, with the window (next month/quarter/year,
    counted from today) and order (date/name/plot) picked on the page
    (issue #272). The PDF button passes the same choices on."""
    user = await require_permission(request, db, "calendar", "read")
    today = date.today()
    end = birthday_range_end(today, range_key)
    upcoming = await upcoming_birthdays(db, today=today, within_days=(end - today).days, with_plots=(sort == "plot"))
    ics_token = await get_or_create_ics_token(db)
    return templates.TemplateResponse(request, "calendar/birthdays.html", {
        "request": request, "user": user, "upcoming": sort_birthdays(upcoming, sort),
        "ROUND_BIRTHDAY_INTERVAL": ROUND_BIRTHDAY_INTERVAL,
        "ics_token": ics_token,
        "range_key": range_key, "sort_key": sort,
        "range_keys": list(BIRTHDAY_RANGES), "sort_keys": BIRTHDAY_SORTS,
        "range_start": today, "range_end": end,
    })


@router.get("/birthdays/pdf")
async def birthdays_pdf(
    request: Request,
    range_key: BirthdayRange = Query(DEFAULT_BIRTHDAY_RANGE, alias="range"),
    sort: BirthdaySort = Query(DEFAULT_BIRTHDAY_SORT),
    db: AsyncSession = Depends(get_db),
):
    """Printable birthday list (issue #272): the window and order chosen
    on the web view above, with plots and contact details for whoever
    hands out presents. Replaced the whole-year calendar of issue #99.
    Behind the normal app login/permission check like the web view, not
    the ICS feeds' separate secret-token scheme, since this is reached
    from within the logged-in UI, not a calendar-app subscription URL."""
    await require_permission(request, db, "calendar", "read")
    today = date.today()
    end = birthday_range_end(today, range_key)
    upcoming = await upcoming_birthdays(db, today=today, within_days=(end - today).days, with_contact_details=True)
    rows = birthday_rows(upcoming, sort)

    branding = await load_branding(db)
    logo_path = Path("app" + branding["logo_url"]) if branding["logo_url"] else None
    language = await load_current_language(db)
    region = await load_current_region(db)
    footer_context = await load_org_footer_context(db, branding["club_name"])

    pdf_bytes = render_birthday_calendar_pdf(
        today, end, footer_context, logo_path, rows, language, region, group_by_plot=(sort == "plot"),
    )

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="birthdays-{today.isoformat()}.pdf"'},
    )


@router.get("/birthdays.ics")
async def birthdays_ics(request: Request, token: Optional[str] = Query(None), db: AsyncSession = Depends(get_db)):
    """Token-protected -- member birth dates are personal data and must
    never be reachable without the installation's secret token."""
    actual_token = await get_or_create_ics_token(db)
    if not verify_ics_token(token, actual_token):
        raise HTTPException(status_code=403, detail=t_for(request, "calendar.errors.invalid_token"))
    cal = await build_birthday_calendar(db, base_url=request.url.hostname or "parcella.local")
    return _ics_response(cal.to_ical(), "birthdays.ics")


# ---------------------------------------------------------------------------
# Council presence
# ---------------------------------------------------------------------------

@router.get("/council-presence", response_class=HTMLResponse)
async def council_presence_overview(request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_permission(request, db, "calendar", "read")

    result = await db.execute(
        select(CouncilPresence)
        .options(selectinload(CouncilPresence.user))
        .where(CouncilPresence.date >= date.today())
        .order_by(CouncilPresence.date)
    )
    entries = result.scalars().all()

    users_result = await db.execute(select(User).where(User.is_active == True).order_by(User.name))
    all_users = users_result.scalars().all()

    ics_token = await get_or_create_ics_token(db)
    return templates.TemplateResponse(request, "calendar/council_presence.html", {
        "request": request, "user": user, "entries": entries, "all_users": all_users,
        "ics_token": ics_token,
    })


@router.post("/council-presence/new")
async def council_presence_create(
    request: Request,
    user_ids: list[str] = Form([]),
    presence_date: str = Form(...),
    time_from: str = Form(""),
    time_until: str = Form(""),
    note: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    await require_permission(request, db, "calendar", "write")
    if not user_ids:
        raise HTTPException(status_code=400, detail=t_for(request, "calendar.errors.no_member_selected"))
    # One CouncilPresence row per selected person, all sharing the same
    # slot (date/time/note) -- matches the model's "one row per person
    # per slot" shape (docs/module-calendar.md), so two board members
    # covering the same slot together is just two rows, not a new
    # many-to-many table.
    parsed_date = date.fromisoformat(presence_date)
    for user_id in dict.fromkeys(user_ids):
        db.add(CouncilPresence(
            user_id=user_id,
            date=parsed_date,
            time_from=time_from or None,
            time_until=time_until or None,
            note=note.strip() or None,
        ))
    await db.commit()
    return RedirectResponse("/calendar/council-presence", status_code=302)


@router.post("/council-presence/{entry_id}/delete")
async def council_presence_delete(entry_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    await require_permission(request, db, "calendar", "delete")
    result = await db.execute(select(CouncilPresence).where(CouncilPresence.id == entry_id))
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail=t_for(request, "calendar.errors.entry_not_found"))
    await db.delete(entry)
    await db.commit()
    return RedirectResponse("/calendar/council-presence", status_code=302)


@router.get("/council-presence.ics")
async def council_presence_ics(request: Request, token: Optional[str] = Query(None), db: AsyncSession = Depends(get_db)):
    actual_token = await get_or_create_ics_token(db)
    if not verify_ics_token(token, actual_token):
        raise HTTPException(status_code=403, detail=t_for(request, "calendar.errors.invalid_token"))
    cal = await build_council_presence_calendar(db, base_url=request.url.hostname or "parcella.local")
    return _ics_response(cal.to_ical(), "council-presence.ics")


# ---------------------------------------------------------------------------
# Council absence
# ---------------------------------------------------------------------------

@router.get("/council-absence", response_class=HTMLResponse)
async def council_absence_overview(request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_permission(request, db, "calendar", "read")

    result = await db.execute(
        select(CouncilAbsence)
        .options(selectinload(CouncilAbsence.user))
        .where(CouncilAbsence.end_date >= date.today())
        .order_by(CouncilAbsence.start_date)
    )
    entries = result.scalars().all()

    users_result = await db.execute(select(User).where(User.is_active == True).order_by(User.name))
    all_users = users_result.scalars().all()

    ics_token = await get_or_create_ics_token(db)
    return templates.TemplateResponse(request, "calendar/council_absence.html", {
        "request": request, "user": user, "entries": entries, "all_users": all_users,
        "ics_token": ics_token,
    })


@router.post("/council-absence/new")
async def council_absence_create(
    request: Request,
    user_ids: list[str] = Form([]),
    start_date: str = Form(...),
    end_date: str = Form(...),
    note: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    """Anyone with a system account can log absence -- originally
    self-only (see git history), reopened by issue #216 to also allow
    logging it for other registered users, still gated only on being
    logged in at all (no elevated permission, matching the module's
    existing "everybody can do this" posture for self-logging). Callers
    pick one or more people via `user_ids`, one CouncilAbsence row per
    person, same shape as council-presence's multi-select. An empty/
    missing `user_ids` (the original single-user form shape, still used
    by the "just me" default in the template) falls back to the
    logged-in user themselves, so the original one-click self-log flow
    keeps working unchanged."""
    user = await require_user(request, db)
    parsed_start = date.fromisoformat(start_date)
    parsed_end = date.fromisoformat(end_date)
    target_ids = list(dict.fromkeys(user_ids)) or [user.id]
    for target_id in target_ids:
        db.add(CouncilAbsence(
            user_id=target_id,
            start_date=parsed_start,
            end_date=parsed_end,
            note=note.strip() or None,
        ))
    await db.commit()
    return RedirectResponse("/calendar/council-absence", status_code=302)


@router.post("/council-absence/{entry_id}/delete")
async def council_absence_delete(entry_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    """Anyone can delete their OWN absence entry; admin/board can delete
    anyone's (e.g. to clean up an entry someone else got wrong for them)."""
    user = await require_user(request, db)
    result = await db.execute(select(CouncilAbsence).where(CouncilAbsence.id == entry_id))
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail=t_for(request, "calendar.errors.entry_not_found"))
    if entry.user_id != user.id and not getattr(request.state, "is_full_access", False):
        raise HTTPException(status_code=403, detail=t_for(request, "calendar.errors.not_your_entry"))
    await db.delete(entry)
    await db.commit()
    return RedirectResponse("/calendar/council-absence", status_code=302)


@router.get("/council-absence.ics")
async def council_absence_ics(request: Request, token: Optional[str] = Query(None), db: AsyncSession = Depends(get_db)):
    actual_token = await get_or_create_ics_token(db)
    if not verify_ics_token(token, actual_token):
        raise HTTPException(status_code=403, detail=t_for(request, "calendar.errors.invalid_token"))
    cal = await build_council_absence_calendar(db, base_url=request.url.hostname or "parcella.local")
    return _ics_response(cal.to_ical(), "council-absence.ics")
