"""
ICS (iCalendar, RFC 5545) feed generation for the calendar module.

Four feeds, with two different privacy postures:
- Community calendar (member meetings, parcel inspections, work
  sessions): fully public, no authentication -- this is the one meant
  to be embedded on the club's public WordPress site, so it can't
  require a login (an external site can't send this app's session
  cookie).
- Birthdays, council presence, council absence: all personal/internal
  data, never served without a valid secret token (see
  get_or_create_ics_token below) -- calendar apps generally can't do
  session-cookie auth either, so a long random token in the URL is the
  practical equivalent of a login for a subscription feed. Never
  reachable without it.
"""
import secrets
from datetime import date, datetime, time, timezone, timedelta
from typing import Optional
from zoneinfo import ZoneInfo

from icalendar import Calendar, Event
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models import ClubSetting, CalendarEvent, CalendarEventType, WorkSession, SessionType, CouncilPresence, CouncilAbsence
from app.birthdays import all_birthdays_for_calendar
from app.l10n import DEFAULT_REGION, REGION_TIMEZONES, load_current_region

ICS_TOKEN_SETTING_KEY = "ics_secret_token"


async def get_or_create_ics_token(db: AsyncSession) -> str:
    """Returns the installation's shared secret for the private ICS
    feeds, generating one on first use. One shared secret for the whole
    installation (not per-user) -- deliberately simple for a small,
    trusted club; see docs/module-calendar.md if per-user tokens are
    ever needed."""
    result = await db.execute(select(ClubSetting).where(ClubSetting.key == ICS_TOKEN_SETTING_KEY))
    entry = result.scalar_one_or_none()
    if entry and entry.value:
        return entry.value

    token = secrets.token_urlsafe(32)
    if entry:
        entry.value = token
    else:
        db.add(ClubSetting(key=ICS_TOKEN_SETTING_KEY, value=token, description="Secret token for private ICS calendar feeds"))
    await db.commit()
    return token


async def regenerate_ics_token(db: AsyncSession) -> str:
    """Invalidates every subscribed private feed URL at once -- the way to
    cut off a leaked link or a board member who left (the token never
    expires on its own). Subscribers re-copy the URL from the calendar
    pages afterwards."""
    token = secrets.token_urlsafe(32)
    result = await db.execute(select(ClubSetting).where(ClubSetting.key == ICS_TOKEN_SETTING_KEY))
    entry = result.scalar_one_or_none()
    if entry:
        entry.value = token
    else:
        db.add(ClubSetting(key=ICS_TOKEN_SETTING_KEY, value=token, description="Secret token for private ICS calendar feeds"))
    await db.commit()
    return token


def verify_ics_token(provided: Optional[str], actual: str) -> bool:
    if not provided:
        return False
    return secrets.compare_digest(provided, actual)


def _new_calendar(name: str) -> Calendar:
    cal = Calendar()
    cal.add("prodid", f"-//Parcella//{name}//EN")
    cal.add("version", "2.0")
    cal.add("x-wr-calname", name)
    return cal


def _add_event(cal: Calendar, uid: str, summary: str, start, end=None, description: Optional[str] = None,
                location: Optional[str] = None, rrule_yearly: bool = False,
                start_time: Optional[str] = None, end_time: Optional[str] = None,
                tz: Optional[ZoneInfo] = None) -> None:
    """Adds an all-day VEVENT. Per RFC 5545, DTEND for a DATE-value event
    is EXCLUSIVE (the day itself is not part of the event) -- a single-day
    event needs DTEND = start + 1 day, not DTEND = start, or most calendar
    apps will render it as zero-length / one day short. `end` here is the
    LAST DAY the event should visibly cover (inclusive), matching how a
    human reads a date range; this function does the +1 day conversion.

    With `start_time` ("HH:MM") and `tz` it's a timed event instead:
    DTSTART/DTEND carry the time in the club's zone, and DTEND is the
    actual end (no +1 day). Without an `end_time` there's no DTEND, which
    RFC 5545 reads as "starts then". The caller adds the VTIMEZONE
    (cal.add_missing_timezones()) once all events are in."""
    event = Event()
    event.add("uid", uid)
    event.add("summary", summary)
    inclusive_end = end or start
    timed_start = _at(start, start_time, tz)
    if timed_start:
        event.add("dtstart", timed_start)
        timed_end = _at(inclusive_end, end_time, tz)
        if timed_end and timed_end > timed_start:
            event.add("dtend", timed_end)
    else:
        event.add("dtstart", start)
        event.add("dtend", inclusive_end + timedelta(days=1))
    event.add("dtstamp", datetime.now(timezone.utc))
    if description:
        event.add("description", description)
    if location:
        event.add("location", location)
    if rrule_yearly:
        event.add("rrule", {"freq": "yearly"})
    cal.add_component(event)


def _at(day: date, hhmm: Optional[str], tz: Optional[ZoneInfo]) -> Optional[datetime]:
    """day + "HH:MM" in tz, or None (no time, no zone, or not a valid
    time -- the event then stays all-day rather than failing the feed)."""
    if not hhmm or tz is None:
        return None
    try:
        return datetime.combine(day, time.fromisoformat(hhmm), tzinfo=tz)
    except ValueError:
        return None


async def _club_timezone(db: AsyncSession) -> ZoneInfo:
    region = await load_current_region(db)
    return ZoneInfo(REGION_TIMEZONES.get(region, REGION_TIMEZONES[DEFAULT_REGION]))


async def build_community_calendar(db: AsyncSession, base_url: str) -> Calendar:
    """Member meetings, parcel inspections, and work sessions, merged
    into one public feed. Only present/future entries -- a feed that
    accumulates every past meeting forever would just get noisier every
    year, and nobody subscribing wants history, they want what's next."""
    cal = _new_calendar("Community Calendar")
    tz = await _club_timezone(db)

    events_result = await db.execute(
        select(CalendarEvent).where(CalendarEvent.start_date >= date.today()).order_by(CalendarEvent.start_date)
    )
    for e in events_result.scalars().all():
        # Times entered for an event (e.g. 10:00-12:00) make it a timed
        # event; up to 3.18.0 they were dropped and every event showed up
        # as all-day in subscribers' calendar apps.
        _add_event(
            cal, uid=f"calendar-event-{e.id}@{base_url}",
            summary=e.title, start=e.start_date, end=e.end_date or e.start_date,
            description=e.description, location=e.location,
            start_time=e.start_time, end_time=e.end_time, tz=tz,
        )

    # STANDARD only -- SPECIAL sessions are spontaneous/unplanned work
    # (e.g. "paint the garden bench today") and deliberately don't
    # appear on the community calendar or its public feed, since they
    # aren't something members plan around in advance. See
    # docs/module-calendar.md for the reasoning.
    sessions_result = await db.execute(
        select(WorkSession)
        .where(WorkSession.date >= date.today(), WorkSession.type == SessionType.STANDARD)
        .order_by(WorkSession.date)
    )
    for s in sessions_result.scalars().all():
        summary = f"Work session: {s.title}"
        description = s.description
        if s.time_from:
            description = f"{s.time_from}" + (f" - {s.time_until}" if s.time_until else "") + (f"\n{description}" if description else "")
        _add_event(
            cal, uid=f"work-session-{s.id}@{base_url}",
            summary=summary, start=s.date, description=description,
        )

    cal.add_missing_timezones()  # VTIMEZONE for the timed events' TZID
    return cal


async def build_birthday_calendar(db: AsyncSession, base_url: str) -> Calendar:
    """Yearly-recurring all-day events for every active member with a
    birth date on file."""
    cal = _new_calendar("Member Birthdays")
    members = await all_birthdays_for_calendar(db)
    for m in members:
        _add_event(
            cal, uid=f"birthday-{m.id}@{base_url}",
            summary=f"{m.full_name}'s birthday",
            start=m.date_of_birth, rrule_yearly=True,
        )
    return cal


async def build_council_presence_calendar(db: AsyncSession, base_url: str) -> Calendar:
    cal = _new_calendar("Council Presence")
    result = await db.execute(
        select(CouncilPresence)
        .options(selectinload(CouncilPresence.user))
        .where(CouncilPresence.date >= date.today())
        .order_by(CouncilPresence.date)
    )
    for p in result.scalars().all():
        time_note = None
        if p.time_from:
            time_note = p.time_from + (f" - {p.time_until}" if p.time_until else "")
        summary = f"{p.user.name} on-site" if p.user else "Council on-site"
        description = "\n".join(filter(None, [time_note, p.note]))
        _add_event(
            cal, uid=f"council-presence-{p.id}@{base_url}",
            summary=summary, start=p.date, description=description or None,
        )
    return cal


async def build_council_absence_calendar(db: AsyncSession, base_url: str) -> Calendar:
    cal = _new_calendar("Council Absence")
    result = await db.execute(
        select(CouncilAbsence)
        .options(selectinload(CouncilAbsence.user))
        .where(CouncilAbsence.end_date >= date.today())
        .order_by(CouncilAbsence.start_date)
    )
    for a in result.scalars().all():
        summary = f"{a.user.name} absent" if a.user else "Absent"
        _add_event(
            cal, uid=f"council-absence-{a.id}@{base_url}",
            summary=summary, start=a.start_date, end=a.end_date,
            description=a.note,
        )
    return cal
