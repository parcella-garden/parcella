"""
Reporting module (issue #264, docs/module-reporting.md, ADR 0118): club
figures over time, computed live from the existing tables each time the
page or API is asked -- no snapshot table, so nothing to keep in sync,
but also only what the data can still tell (see the module doc for the
gaps, e.g. members without a join date).

One function per figure, each returning a Report. SECTIONS lists them
in page order together with the module flag a section needs; adding a
KPI is one function plus one SECTIONS entry (and its translations under
reporting.<key>.*).

Labels: years and quarters are plain strings ("2025", "2025 Q1");
categories are stable ids ("boomers", "owes_fee") that the HTML page
translates as reporting.<report key>.<id> and the API returns as-is.
"""
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from typing import Awaitable, Callable, Dict, List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import active_member_filter
from app.models import (
    Applicant, HoursTransfer, Member, MemberParcel, MeteringMedium, MeteringPoint, MeteringPointType, Parcel,
    ParcelStatus, WorkHoursConfiguration, WorkHoursMode,
)
from app.services.work_hours import evaluate_year

# Time series show at most this many years, ending with the current
# one -- a single 1995 join date shouldn't stretch the axis over 30 years.
MAX_YEARS = 10

# Birth-year ranges per generation (Pew Research's common cut-offs),
# oldest first. None = open-ended.
GENERATIONS: List[Tuple[str, Optional[int], Optional[int]]] = [
    ("silent", None, 1945),
    ("boomers", 1946, 1964),
    ("gen_x", 1965, 1980),
    ("millennials", 1981, 1996),
    ("gen_z", 1997, 2012),
    ("alpha", 2013, None),
]

# Work-hours outcome per evaluated row, in the order they're checked --
# each row lands in exactly one, so the shares add up to 100%.
WORK_HOURS_CATEGORIES = ["exempt", "owes_fee", "sponsorship", "sessions"]


@dataclass
class ReportSeries:
    key: str  # stable id, translated as reporting.<report key>.series_<key>
    values: List[float]


@dataclass
class Report:
    key: str
    chart: str  # "pie", "bar", "stacked_bar" or "line"
    labels: List[str]
    categorical: bool  # labels are ids to translate (not years/quarters)
    series: List[ReportSeries]
    # Translation key + params for a sentence under the chart, e.g. how
    # many members a figure couldn't place.
    note_key: Optional[str] = None
    note_params: Dict[str, object] = field(default_factory=dict)


def generation_of(birth_year: int) -> str:
    for key, start, end in GENERATIONS:
        if (start is None or birth_year >= start) and (end is None or birth_year <= end):
            return key
    raise ValueError(birth_year)  # unreachable: the ranges are open at both ends


def _year_window(first_year_with_data: Optional[int], today: date) -> List[int]:
    start = max(today.year - MAX_YEARS + 1, first_year_with_data or today.year)
    return list(range(start, today.year + 1))


def _year_end(year: int, today: date) -> date:
    """The day a year's figure is measured on: 31 Dec, or today for the
    year still running."""
    return today if year == today.year else date(year, 12, 31)


async def generations_report(db: AsyncSession, today: date) -> Report:
    birth_dates = (await db.scalars(
        select(Member.date_of_birth).where(active_member_filter())
    )).all()
    counts = {key: 0 for key, _, _ in GENERATIONS}
    missing = 0
    for birth_date in birth_dates:
        if birth_date is None:
            missing += 1
        else:
            counts[generation_of(birth_date.year)] += 1
    return Report(
        key="generations", chart="pie", labels=list(counts), categorical=True,
        series=[ReportSeries("members", list(counts.values()))],
        note_key="reporting.generations.note_missing" if missing else None,
        note_params={"count": missing},
    )


async def members_per_year_report(db: AsyncSession, today: date) -> Report:
    """Members on the last day of each year. A blank member_since counts
    as "since before the first year shown", the same way
    active_member_filter() treats it; soft-deleted members are left out
    entirely, since nothing records when they were deleted."""
    rows = (await db.execute(
        select(Member.member_since, Member.member_until).where(Member.deleted_at.is_(None))
    )).all()
    years = _year_window(min((s.year for s, _ in rows if s), default=None), today)
    values = []
    for year in years:
        day = _year_end(year, today)
        values.append(sum(
            1 for since, until in rows
            if (since is None or since <= day) and (until is None or until >= day)
        ))
    blank_since = sum(1 for since, _ in rows if since is None)
    return Report(
        key="members_per_year", chart="line", labels=[str(y) for y in years], categorical=False,
        series=[ReportSeries("members", values)],
        note_key="reporting.members_per_year.note_blank_since" if blank_since else None,
        note_params={"count": blank_since},
    )


async def cancelled_plots_report(db: AsyncSession, today: date) -> Report:
    """Leases (member <-> plot assignments) ending in each year, past or
    already scheduled for the current year (kermie's definition of a
    cancelled plot)."""
    end_dates = (await db.scalars(
        select(MemberParcel.assigned_until).where(
            MemberParcel.assigned_until.is_not(None),
            MemberParcel.assigned_until <= date(today.year, 12, 31),
        )
    )).all()
    years = _year_window(min((d.year for d in end_dates), default=None), today)
    values = [sum(1 for d in end_dates if d.year == year) for year in years]
    return Report(
        key="cancelled_plots", chart="bar", labels=[str(y) for y in years], categorical=False,
        series=[ReportSeries("leases_ended", values)],
    )


async def _applied_dates(db: AsyncSession) -> List[date]:
    return [a.astimezone(timezone.utc).date() if isinstance(a, datetime) else a
            for a in (await db.scalars(select(Applicant.applied_at))).all()]


async def applicants_per_quarter_report(db: AsyncSession, today: date) -> Report:
    """The previous and the current year, quarter by quarter."""
    applied = await _applied_dates(db)
    labels, values = [], []
    for year in (today.year - 1, today.year):
        for quarter in range(1, 5):
            labels.append(f"{year} Q{quarter}")
            values.append(sum(1 for d in applied if d.year == year and (d.month - 1) // 3 + 1 == quarter))
    return Report(
        key="applicants_per_quarter", chart="bar", labels=labels, categorical=False,
        series=[ReportSeries("applicants", values)],
    )


async def applicants_per_year_report(db: AsyncSession, today: date) -> Report:
    applied = await _applied_dates(db)
    years = _year_window(min((d.year for d in applied), default=None), today)
    return Report(
        key="applicants_per_year", chart="bar", labels=[str(y) for y in years], categorical=False,
        series=[ReportSeries("applicants", [sum(1 for d in applied if d.year == y) for y in years])],
    )


def work_hours_category(row: dict) -> str:
    """Exactly one outcome per evaluation row: exempt, else short of
    hours (pays the fee), else fulfilled with the help of sponsorship
    hours, else fulfilled by sessions (and transfers) alone. Works for
    both row shapes of evaluate_year(): PER_PARCEL rows carry their
    tenants' hours in tenant_details, PER_MEMBER rows their own."""
    if row["exempt"]:
        return "exempt"
    if row["outstanding_hours"] > 0:
        return "owes_fee"
    hours = [t["hours"] for t in row["tenant_details"]] if "tenant_details" in row else [row["hours"]]
    if any(h["sponsorship_hours"] > 0 for h in hours):
        return "sponsorship"
    return "sessions"


async def work_hours_report(db: AsyncSession, today: date) -> Report:
    """Configured years only (evaluate_year() has nothing to say about
    the others), counted per plot -- or per member in a year set to
    PER_MEMBER, which the note then mentions."""
    configs = (await db.execute(
        select(WorkHoursConfiguration.year, WorkHoursConfiguration.mode)
        .where(WorkHoursConfiguration.year <= today.year)
        .order_by(WorkHoursConfiguration.year)
    )).all()[-MAX_YEARS:]
    counts = {category: [] for category in WORK_HOURS_CATEGORIES}
    for year, _ in configs:
        _, rows = await evaluate_year(db, year)
        per_year = {category: 0 for category in WORK_HOURS_CATEGORIES}
        for row in rows:
            per_year[work_hours_category(row)] += 1
        for category in WORK_HOURS_CATEGORIES:
            counts[category].append(per_year[category])
    per_member_years = [str(year) for year, mode in configs if mode == WorkHoursMode.PER_MEMBER]
    return Report(
        key="work_hours", chart="stacked_bar", labels=[str(year) for year, _ in configs], categorical=False,
        series=[ReportSeries(category, counts[category]) for category in WORK_HOURS_CATEGORIES],
        note_key="reporting.work_hours.note_per_member" if per_member_years else None,
        note_params={"years": ", ".join(per_member_years)},
    )


async def hours_transfers_report(db: AsyncSession, today: date) -> Report:
    rows = (await db.execute(
        select(HoursTransfer.year, func.count(HoursTransfer.id), func.coalesce(func.sum(HoursTransfer.hours), 0))
        .where(HoursTransfer.year <= today.year)
        .group_by(HoursTransfer.year)
    )).all()
    by_year = {year: (count, float(hours)) for year, count, hours in rows}
    years = _year_window(min(by_year, default=None), today)
    return Report(
        key="hours_transfers", chart="bar", labels=[str(y) for y in years], categorical=False,
        series=[
            ReportSeries("transfers", [by_year.get(y, (0, 0.0))[0] for y in years]),
            ReportSeries("hours", [by_year.get(y, (0, 0.0))[1] for y in years]),
        ],
    )


async def electricity_report(db: AsyncSession, today: date) -> Report:
    """Active plots with at least one electricity connection point of
    their own (MeteringPoint type PARCEL) vs. without."""
    total = await db.scalar(select(func.count()).select_from(Parcel).where(Parcel.status == ParcelStatus.ACTIVE)) or 0
    with_power = await db.scalar(
        select(func.count(func.distinct(Parcel.id)))
        .join(MeteringPoint, MeteringPoint.parcel_id == Parcel.id)
        .where(
            Parcel.status == ParcelStatus.ACTIVE,
            MeteringPoint.medium == MeteringMedium.ELECTRICITY,
            MeteringPoint.type == MeteringPointType.PARCEL,
        )
    ) or 0
    return Report(
        key="electricity", chart="pie", labels=["with", "without"], categorical=True,
        series=[ReportSeries("plots", [with_power, total - with_power])],
    )


ReportBuilder = Callable[[AsyncSession, date], Awaitable[Report]]

# Page order. The second item is the module flag a section needs, or
# None for core data (members, parcels).
SECTIONS: List[Tuple[ReportBuilder, Optional[str]]] = [
    (generations_report, None),
    (members_per_year_report, None),
    (cancelled_plots_report, None),
    (applicants_per_quarter_report, "applicants"),
    (applicants_per_year_report, "applicants"),
    (work_hours_report, "work_hours"),
    (hours_transfers_report, "work_hours"),
    (electricity_report, "electricity"),
]


async def build_reports(db: AsyncSession, module_flags: Dict[str, bool], today: Optional[date] = None) -> List[Report]:
    """Every section whose module is switched on, in page order."""
    today = today or date.today()
    return [
        await builder(db, today)
        for builder, module in SECTIONS
        if module is None or module_flags.get(module, False)
    ]
