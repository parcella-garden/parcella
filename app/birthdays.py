"""
Birthday calculations shared between the dashboard widget and the
calendar module's birthday list/ICS feed.

Deliberately not a stored table -- a member's birthday calendar entry is
entirely derived from Member.date_of_birth each time it's needed, so
there's nothing to keep in sync when a member's birth date is corrected.
"""
import re
from dataclasses import dataclass
from datetime import date
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import active_member_filter
from app.models import Member, MemberParcel

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


async def upcoming_birthdays(
    db: AsyncSession, today: Optional[date] = None, within_days: int = 7, *, with_contact_details: bool = False,
) -> List[UpcomingBirthday]:
    """Active members whose next birthday falls within the given window
    (inclusive of today), sorted by how soon it is. Tags are loaded for
    the birthday list (issue #271); `with_contact_details` also loads
    current plots, emails and phone numbers for the print PDF (#272)."""
    today = today or date.today()
    options = [selectinload(Member.tags)]
    if with_contact_details:
        options += [
            selectinload(Member.parcel_assignments).selectinload(MemberParcel.parcel),
            selectinload(Member.email_addresses),
            selectinload(Member.phone_numbers),
        ]
    result = await db.execute(
        select(Member).where(active_member_filter(), Member.date_of_birth.is_not(None)).options(*options)
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


# The birthday list's window (web page and print PDF, issue #272).
BIRTHDAY_LIST_DAYS = 90


@dataclass
class ParcelBirthdayRow:
    plot_number: Optional[str]  # None: the member has no current plot
    birthday: UpcomingBirthday


def _plot_sort_key(plot_number: Optional[str]):
    """Natural order ("2" before "10", "3a" after "3"); members without
    a plot go last."""
    if plot_number is None:
        return (1, [])
    parts = re.split(r"(\d+)", plot_number.strip().lower())
    return (0, [(0, int(p), "") if p.isdigit() else (1, 0, p) for p in parts if p])


def birthdays_by_parcel(upcoming: List[UpcomingBirthday]) -> List[ParcelBirthdayRow]:
    """The upcoming birthdays (loaded with_contact_details) as one row
    per member and current plot, sorted by plot number, then date, then
    name (issue #272). A member holding several plots is listed under
    each; one without a current plot gets a single row at the end."""
    rows = []
    for b in upcoming:
        plots = sorted({a.parcel.plot_number for a in b.member.parcel_assignments if a.is_current and a.parcel})
        for plot_number in plots or [None]:
            rows.append(ParcelBirthdayRow(plot_number=plot_number, birthday=b))
    rows.sort(key=lambda r: (
        _plot_sort_key(r.plot_number), r.birthday.next_occurrence,
        r.birthday.member.last_name, r.birthday.member.first_name,
    ))
    return rows


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
