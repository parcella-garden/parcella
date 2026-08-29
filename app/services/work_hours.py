"""
Shared work-hours business logic, called by both
app/routers/work_hours.py (HTML) and app/routers/api_work_hours.py
(API) -- see ADR 0070.

Headline fix: the evaluation/exemption engine
(get_config_for_year/calculate_hours_for_member/is_exempt/evaluate_year)
was reimplemented independently 3x -- the HTML evaluation page, the
HTML CSV export, and the API's evaluation_get (which imported the HTML
router's private helpers directly, a fragile shape ADR 0070 replaces
with a real shared module). This exact duplication already caused a
real shipped bug once: an inverted `all()`-copy of the "at least one
exempt tenant exempts the whole parcel" rule (`any()`, never `all()` --
see docs/ADR/README.md). All three call sites now compute a row's
standing through the one path here, so that mistake is now structurally
impossible to reintroduce independently in a fourth place.

No audit trail or notifications anywhere in this module, either side,
before or after this extraction.
"""
from datetime import date
from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import (
    ClubRole, ExemptionReason, Member, MemberClubRole, MemberParcel, Parcel, ParcelStatus,
    ParticipationStatus, SessionParticipation, SessionType, Sponsorship, TaskWorkload,
    WorkHoursConfiguration, WorkHoursMode, WorkSession, WorkTask,
)
from app.services.errors import ServiceError

# ---------------------------------------------------------------------------
# Evaluation / exemption engine
# ---------------------------------------------------------------------------


async def get_config_for_year(db: AsyncSession, year: int) -> Optional[WorkHoursConfiguration]:
    result = await db.execute(select(WorkHoursConfiguration).where(WorkHoursConfiguration.year == year))
    return result.scalar_one_or_none()


async def calculate_hours_for_member(db: AsyncSession, member_id: str, year: int) -> dict:
    """Calculates a member's required-work-hours standing for a year."""
    session_hours = await db.scalar(
        select(func.coalesce(func.sum(
            func.coalesce(SessionParticipation.hours_completed, WorkSession.hours_per_participant, 0)
        ), 0))
        .join(WorkSession)
        .where(
            SessionParticipation.member_id == member_id,
            SessionParticipation.status == ParticipationStatus.ATTENDED,
            func.extract("year", WorkSession.date) == year,
        )
    ) or 0

    sponsorship_hours = await db.scalar(
        select(func.coalesce(func.sum(Sponsorship.credited_hours), 0))
        .where(
            Sponsorship.member_id == member_id,
            Sponsorship.valid_from <= date(year, 12, 31),
            (Sponsorship.valid_until.is_(None)) | (Sponsorship.valid_until >= date(year, 1, 1)),
        )
    ) or 0

    return {
        "session_hours": float(session_hours),
        "sponsorship_hours": float(sponsorship_hours),
        "total": float(session_hours) + float(sponsorship_hours),
    }


async def is_exempt(db: AsyncSession, member_id: str, year: int) -> bool:
    """Checks whether a member is exempt from required work hours for a year."""
    result = await db.execute(
        select(MemberClubRole)
        .join(ClubRole, MemberClubRole.club_role_id == ClubRole.id)
        .where(
            MemberClubRole.member_id == member_id,
            MemberClubRole.year == year,
            ClubRole.hours_exempt == True,
        )
    )
    return result.scalar_one_or_none() is not None


async def evaluate_parcel(db: AsyncSession, parcel: Parcel, year: int, *, config: WorkHoursConfiguration) -> Optional[dict]:
    """Evaluates one parcel's standing for PER_PARCEL mode. Returns None
    if the parcel has no active tenants (vacant, or every tenant
    inactive) -- skip it, same as every caller always did."""
    tenants = [
        z.member for z in parcel.member_assignments
        if z.member.deleted_at is None
        and (z.member.member_until is None or z.member.member_until >= date.today())
    ]
    if not tenants:
        return None

    total_hours = 0.0
    tenant_details = []
    for m in tenants:
        hours = await calculate_hours_for_member(db, m.id, year)
        exempt = await is_exempt(db, m.id, year)
        total_hours += hours["total"]
        tenant_details.append({"member": m, "hours": hours, "exempt": exempt})

    required = float(config.hours_required)
    # Exempt if AT LEAST ONE tenant is exempt (any(), not all() -- see
    # this module's docstring: this exact rule already caused a real
    # shipped bug from an inverted all()-copy in the CSV export and API.
    exempt_flag = any(t["exempt"] for t in tenant_details)
    outstanding = max(0.0, required - total_hours) if not exempt_flag else 0.0
    amount_due = outstanding * float(config.rate_per_hour_eur)

    return {
        "parcel": parcel,
        "tenant_details": tenant_details,
        "total_hours": total_hours,
        "required_hours": required,
        "outstanding_hours": outstanding,
        "amount_due": amount_due,
        "fulfilled": exempt_flag or total_hours >= required,
        "all_exempt": exempt_flag,  # unified key kept for the template, see original comment
        "exempt": exempt_flag,
    }


async def evaluate_member(db: AsyncSession, member: Member, year: int, *, config: WorkHoursConfiguration) -> dict:
    """Evaluates one member's standing for PER_MEMBER mode."""
    hours = await calculate_hours_for_member(db, member.id, year)
    exempt_flag = await is_exempt(db, member.id, year)
    required = float(config.hours_required)
    outstanding = max(0.0, required - hours["total"]) if not exempt_flag else 0.0
    amount_due = outstanding * float(config.rate_per_hour_eur)

    return {
        "member": member,
        "hours": hours,
        "exempt": exempt_flag,
        "required_hours": required,
        "outstanding_hours": outstanding,
        "amount_due": amount_due,
        "fulfilled": exempt_flag or hours["total"] >= required,
    }


async def evaluate_year(db: AsyncSession, year: int) -> tuple:
    """Full evaluation for a year: (config, rows). rows is [] if no
    configuration exists for the year yet. Dispatches to
    evaluate_parcel/evaluate_member per the configuration's mode --
    same shape every one of the three former independent
    implementations used."""
    config = await get_config_for_year(db, year)
    if not config:
        return None, []

    rows: List[dict] = []
    if config.mode == WorkHoursMode.PER_PARCEL:
        result = await db.execute(
            select(Parcel)
            .options(selectinload(Parcel.member_assignments).selectinload(MemberParcel.member))
            .where(Parcel.status == ParcelStatus.ACTIVE)
            .order_by(Parcel.plot_number)
        )
        for parcel in result.scalars().all():
            row = await evaluate_parcel(db, parcel, year, config=config)
            if row:
                rows.append(row)
    else:
        result = await db.execute(
            select(Member)
            .options(selectinload(Member.parcel_assignments))
            .where(Member.deleted_at.is_(None), Member.parcel_assignments.any())
            .order_by(Member.last_name, Member.first_name)
        )
        for m in result.scalars().all():
            rows.append(await evaluate_member(db, m, year, config=config))

    return config, rows


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


async def save_configuration_for_year(
    db: AsyncSession, year: int, *, hours_required: float, rate_per_hour_eur: float, mode: str, note: Optional[str],
) -> WorkHoursConfiguration:
    """Upsert by year -- both HTML's configuration_create and the API's
    configuration_set key on year directly (configuration_update,
    HTML-only editing-by-id-with-year-change, has no API equivalent --
    same shape as metering's price_configuration_update)."""
    config = await get_config_for_year(db, year)
    if config:
        config.hours_required = hours_required
        config.rate_per_hour_eur = rate_per_hour_eur
        config.mode = WorkHoursMode(mode)
        config.note = note
    else:
        config = WorkHoursConfiguration(
            year=year, hours_required=hours_required, rate_per_hour_eur=rate_per_hour_eur,
            mode=WorkHoursMode(mode), note=note,
        )
        db.add(config)
    await db.flush()
    return config


# ---------------------------------------------------------------------------
# Club roles + member assignments
# ---------------------------------------------------------------------------


async def create_club_role(
    db: AsyncSession, *, name: str, description: Optional[str], hours_exempt: bool, exemption_reason: Optional[str],
) -> ClubRole:
    role = ClubRole(
        name=name.strip(), description=(description or "").strip() or None,
        hours_exempt=hours_exempt, exemption_reason=(ExemptionReason(exemption_reason) if exemption_reason else None),
    )
    db.add(role)
    await db.flush()
    return role


async def update_club_role(
    db: AsyncSession, role: ClubRole, *, name: str, description: Optional[str], hours_exempt: bool, exemption_reason: Optional[str],
) -> ClubRole:
    role.name = name.strip()
    role.description = (description or "").strip() or None
    role.hours_exempt = hours_exempt
    role.exemption_reason = ExemptionReason(exemption_reason) if exemption_reason else None
    await db.flush()
    return role


async def assign_member_to_club_role(
    db: AsyncSession, *, member_id: str, club_role_id: str, year: int,
    valid_from: Optional[date] = None, valid_until: Optional[date] = None, note: Optional[str] = None,
) -> Optional[MemberClubRole]:
    """Returns None (no-op) if this exact (member, role, year) combo is
    already assigned -- there's no DB uniqueness constraint, so without
    this check the API could silently create duplicate assignments."""
    existing = await db.execute(
        select(MemberClubRole).where(
            MemberClubRole.member_id == member_id,
            MemberClubRole.club_role_id == club_role_id,
            MemberClubRole.year == year,
        )
    )
    if existing.scalar_one_or_none():
        return None

    assignment = MemberClubRole(
        member_id=member_id, club_role_id=club_role_id, year=year,
        valid_from=valid_from, valid_until=valid_until, note=(note or "").strip() or None,
    )
    db.add(assignment)
    await db.flush()
    return assignment


# ---------------------------------------------------------------------------
# Work sessions
# ---------------------------------------------------------------------------


async def create_session(
    db: AsyncSession, *, title: str, description: Optional[str], type: str, date_value: date,
    time_from: Optional[str], time_until: Optional[str], max_participants: Optional[int],
    hours_per_participant: Optional[float], created_by_id: str,
) -> WorkSession:
    session = WorkSession(
        title=title.strip(), description=(description or "").strip() or None, type=SessionType(type),
        date=date_value, time_from=(time_from or "").strip() or None, time_until=(time_until or "").strip() or None,
        max_participants=max_participants, hours_per_participant=hours_per_participant,
        created_by_id=created_by_id,
    )
    db.add(session)
    await db.flush()
    return session


async def update_session(db: AsyncSession, session: WorkSession, **fields) -> WorkSession:
    optional_string_fields = {"description", "time_from", "time_until"}
    for key in (
        "title", "description", "type", "date", "time_from", "time_until",
        "max_participants", "hours_per_participant",
    ):
        if key not in fields:
            continue
        value = fields[key]
        if key == "title" and value is not None:
            value = value.strip()
        elif key in optional_string_fields and value is not None:
            value = value.strip() or None
        elif key == "type" and value is not None:
            value = SessionType(value)
        setattr(session, key, value)
    await db.flush()
    return session


async def add_participation(
    db: AsyncSession, session_id: str, *, member_id: str, status: str,
    hours_completed: Optional[float] = None, note: Optional[str] = None,
) -> Optional[SessionParticipation]:
    """Returns None (no-op) if the member is already registered for
    this session."""
    existing = await db.execute(
        select(SessionParticipation).where(
            SessionParticipation.session_id == session_id, SessionParticipation.member_id == member_id,
        )
    )
    if existing.scalar_one_or_none():
        return None

    participation = SessionParticipation(
        session_id=session_id, member_id=member_id, status=ParticipationStatus(status),
        hours_completed=hours_completed, note=(note or "").strip() or None,
    )
    db.add(participation)
    await db.flush()
    return participation


async def update_participation(db: AsyncSession, participation: SessionParticipation, **fields) -> SessionParticipation:
    for key in ("status", "hours_completed", "note"):
        if key not in fields:
            continue
        value = fields[key]
        if key == "status" and value is not None:
            value = ParticipationStatus(value)
        setattr(participation, key, value)
    await db.flush()
    return participation


# ---------------------------------------------------------------------------
# Sponsorships
# ---------------------------------------------------------------------------


async def create_sponsorship(
    db: AsyncSession, *, member_id: Optional[str], area: str, description: Optional[str],
    credited_hours: float, valid_from: date, valid_until: Optional[date] = None,
) -> Sponsorship:
    sponsorship = Sponsorship(
        member_id=member_id or None, area=area.strip(), description=(description or "").strip() or None,
        credited_hours=credited_hours, valid_from=valid_from, valid_until=valid_until,
    )
    db.add(sponsorship)
    await db.flush()
    return sponsorship


async def update_sponsorship(db: AsyncSession, sponsorship: Sponsorship, **fields) -> Sponsorship:
    for key in ("member_id", "area", "description", "credited_hours", "valid_from", "valid_until"):
        if key not in fields:
            continue
        value = fields[key]
        if key == "member_id" and value is not None:
            value = value.strip() or None
        elif key == "area" and value is not None:
            value = value.strip()
        elif key == "description" and value is not None:
            value = value.strip() or None
        setattr(sponsorship, key, value)
    await db.flush()
    return sponsorship


# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------


async def create_task(
    db: AsyncSession, *, title: str, description: Optional[str], workload: str,
    session_id: Optional[str], created_by_id: str,
) -> WorkTask:
    task = WorkTask(
        title=title.strip(), description=(description or "").strip() or None,
        workload=TaskWorkload(workload), session_id=session_id or None, created_by_id=created_by_id,
    )
    db.add(task)
    await db.flush()
    return task


async def schedule_task(db: AsyncSession, task: WorkTask, *, session_id: Optional[str]) -> WorkTask:
    """Schedules a task to a session, or sends it back to the backlog
    if session_id is empty/None. Clears any participant assignment when
    the session changes -- an assignment to a specific person only
    makes sense for the session they actually signed up for."""
    new_session_id = session_id or None
    if new_session_id != task.session_id:
        task.assigned_participation_id = None
    task.session_id = new_session_id
    await db.flush()
    return task


async def assign_task_to_participant(db: AsyncSession, task: WorkTask, *, participation_id: Optional[str]) -> WorkTask:
    """Assigns a task to one signed-up participant of its session, or
    clears the assignment if participation_id is empty/None."""
    if not task.session_id:
        raise ServiceError("work_hours.errors.task_not_scheduled", http_status=400)

    participation_id = participation_id or None
    if participation_id:
        result = await db.execute(
            select(SessionParticipation).where(
                SessionParticipation.id == participation_id,
                SessionParticipation.session_id == task.session_id,
            )
        )
        if not result.scalar_one_or_none():
            raise ServiceError("work_hours.errors.participant_not_in_session", http_status=400)

    task.assigned_participation_id = participation_id
    await db.flush()
    return task


async def toggle_task_done(db: AsyncSession, task: WorkTask) -> WorkTask:
    task.is_done = not task.is_done
    await db.flush()
    return task
