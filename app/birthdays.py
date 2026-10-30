"""
Birthday calculations shared between the dashboard widget and the
calendar module's birthday list/ICS feed.

Deliberately not a stored table -- a member's birthday calendar entry is
entirely derived from Member.date_of_birth each time it's needed, so
there's nothing to keep in sync when a member's birth date is corrected.
"""
from dataclasses import dataclass
from datetime import date
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import active_member_filter
from app.models import Member

# A birthday is considered "round" (a milestone worth highlighting) when
# the age being turned is a multiple of this number. 10 matches the
# common convention (30th, 40th, 50th, ...); adjust here if your
# association also wants to highlight 25/75-style anniversaries.
ROUND_BIRTHDAY_INTERVAL = 10


@dataclass
class UpcomingBirthday:
    member: Member
    next_occurrence: date
    turning_age: int
    is_round: bool


def _next_occurrence(birth_date: date, today: date) -> date:
    """Returns this year's birthday if it hasn't passed yet, otherwise
    next year's. Handles Feb 29 by falling back to Feb 28 in non-leap
    years, so members born on a leap day still get a yearly entry."""
    for year in (today.year, today.year + 1):
        try:
            candidate = birth_date.replace(year=year)
        except ValueError:
            candidate = date(year, 2, 28)
        if candidate >= today:
            return candidate
    # Unreachable in practice, but keeps the return type honest.
    return birth_date.replace(year=today.year + 1)


async def upcoming_birthdays(db: AsyncSession, today: Optional[date] = None, within_days: int = 7) -> List[UpcomingBirthday]:
    """Active members whose next birthday falls within the given window
    (inclusive of today), sorted by how soon it is."""
    today = today or date.today()
    result = await db.execute(
        select(Member).where(active_member_filter(), Member.date_of_birth.is_not(None))
    )
    members = result.scalars().all()

    upcoming = []
    for member in members:
        next_occ = _next_occurrence(member.date_of_birth, today)
        if (next_occ - today).days > within_days:
            continue
        turning_age = next_occ.year - member.date_of_birth.year
        upcoming.append(UpcomingBirthday(
            member=member,
            next_occurrence=next_occ,
            turning_age=turning_age,
            is_round=(turning_age % ROUND_BIRTHDAY_INTERVAL == 0),
        ))

    upcoming.sort(key=lambda b: b.next_occurrence)
    return upcoming


# Mean Gregorian year length, so a member's exact age is the same
# fraction of a year whether or not leap days fall in between.
DAYS_PER_YEAR = 365.2425


def exact_age(birth_date: date, today: date) -> float:
    """Age in years including the fraction since the last birthday --
    an average of whole years would understate every member by ~half a
    year, visibly so at one decimal place."""
    return (today - birth_date).days / DAYS_PER_YEAR


async def average_age(db: AsyncSession, today: Optional[date] = None) -> Optional[float]:
    """Average exact age of active members (issue #263), or None when no
    active member has a date of birth on file. Same population as the
    dashboard's headline member count (active_member_filter()); members
    without a date of birth are left out rather than guessed at."""
    today = today or date.today()
    birth_dates = (await db.scalars(
        select(Member.date_of_birth).where(active_member_filter(), Member.date_of_birth.is_not(None))
    )).all()
    if not birth_dates:
        return None
    return sum(exact_age(b, today) for b in birth_dates) / len(birth_dates)


async def all_birthdays_for_calendar(db: AsyncSession) -> List[Member]:
    """All active members with a birth date on file, for the full
    birthday calendar/ICS feed (not just the next-N-days dashboard
    widget)."""
    result = await db.execute(
        select(Member).where(active_member_filter(), Member.date_of_birth.is_not(None))
        .order_by(Member.date_of_birth)
    )
    return result.scalars().all()


@dataclass
class YearBirthdayEntry:
    member: Member
    month: int
    day: int
    turning_age: int
    is_round: bool


async def birthdays_for_year(db: AsyncSession, year: Optional[int] = None) -> List[YearBirthdayEntry]:
    """Every active member with a birth date on file, one entry each,
    sorted by (month, day) -- Jan 1 through Dec 31 -- for a print/PDF
    birthday calendar covering the whole year (issue #99). Unlike
    upcoming_birthdays()'s rolling "next N days from today" window,
    this has no time-based cutoff: everyone appears exactly once,
    regardless of whether their birthday this year has already passed.
    turning_age is the age reached in `year` (defaults to the current
    year) specifically, not "next occurrence from today"."""
    year = year or date.today().year
    result = await db.execute(
        select(Member).where(active_member_filter(), Member.date_of_birth.is_not(None))
    )
    members = result.scalars().all()

    entries = []
    for m in members:
        turning_age = year - m.date_of_birth.year
        entries.append(YearBirthdayEntry(
            member=m, month=m.date_of_birth.month, day=m.date_of_birth.day,
            turning_age=turning_age, is_round=(turning_age % ROUND_BIRTHDAY_INTERVAL == 0),
        ))
    entries.sort(key=lambda e: (e.month, e.day, e.member.last_name, e.member.first_name))
    return entries
