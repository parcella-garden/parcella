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

Issue #217 added one notification concern: emailing active Admin/Board
about newly created SessionParticipation rows (see
notify_new_participation/notify_new_participations_digest below) --
otherwise still no audit trail here.
"""
import math
from datetime import date, datetime, timedelta, timezone
from typing import List, Optional

from sqlalchemy import case, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.database import tenant_in_year_filter
from app.email_service import send_email
from app.i18n import translate
from app.models import (
    ClubRole, ExemptionReason, HoursTransfer, Member, MemberClubRole, MemberParcel, Parcel, ParcelStatus,
    ParticipationStatus, SessionParticipation, SessionType, Sponsorship, TaskWorkload,
    User, UserRole, WorkHoursConfiguration, WorkHoursMode, WorkSession, WorkTask,
)
from app.services.errors import ServiceError

# Issue #217: how many days a SessionParticipation counts as "new" for
# the dashboard tile / nav badge / session-detail "New" badge -- a
# plain constant, not a ClubSetting, matching the convention of every
# other day-count threshold in this codebase (e.g.
# app/birthdays.py's ROUND_BIRTHDAY_INTERVAL). See docs/ADR/0079.
NEW_PARTICIPATION_WINDOW_DAYS = 14

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

    # Issue #243: hours given to / received from other members, one query.
    transferred_in, transferred_out = (await db.execute(
        select(
            func.coalesce(func.sum(case((HoursTransfer.receiver_member_id == member_id, HoursTransfer.hours))), 0),
            func.coalesce(func.sum(case((HoursTransfer.giver_member_id == member_id, HoursTransfer.hours))), 0),
        ).where(
            HoursTransfer.year == year,
            or_(HoursTransfer.receiver_member_id == member_id, HoursTransfer.giver_member_id == member_id),
        )
    )).one()

    return {
        "session_hours": float(session_hours),
        "sponsorship_hours": float(sponsorship_hours),
        "transferred_in": float(transferred_in),
        "transferred_out": float(transferred_out),
        "transferred_net": float(transferred_in) - float(transferred_out),
        "total": float(session_hours) + float(sponsorship_hours) + float(transferred_in) - float(transferred_out),
    }


async def attended_sessions_by_member(db: AsyncSession, year: int) -> dict:
    """Issue #258: every attended work session of `year`, grouped by
    member -- {member_id: [{"session": WorkSession, "hours": float}, ...]},
    oldest first. Same filter and hours rule as calculate_hours_for_member
    above, so a member's list always adds up to their session hours on
    the evaluation page."""
    hours = func.coalesce(SessionParticipation.hours_completed, WorkSession.hours_per_participant, 0)
    result = await db.execute(
        select(SessionParticipation.member_id, WorkSession, hours)
        .join(WorkSession, WorkSession.id == SessionParticipation.session_id)
        .where(
            SessionParticipation.status == ParticipationStatus.ATTENDED,
            func.extract("year", WorkSession.date) == year,
        )
        .order_by(WorkSession.date, WorkSession.title)
    )
    sessions: dict = {}
    for member_id, session, session_hours in result.all():
        sessions.setdefault(member_id, []).append({"session": session, "hours": float(session_hours)})
    return sessions


async def is_exempt(db: AsyncSession, member_id: str, year: int) -> bool:
    """Checks whether a member is exempt from required work hours for a
    year. A member can hold more than one ClubRole in the same year
    (e.g. chair + treasurer) -- .limit(1) makes this a pure existence
    check regardless of how many exempt roles match, rather than
    assuming at most one row (MultipleResultsFound in production on a
    member holding two exempt roles in the same year)."""
    result = await db.execute(
        select(MemberClubRole.id)
        .join(ClubRole, MemberClubRole.club_role_id == ClubRole.id)
        .where(
            MemberClubRole.member_id == member_id,
            MemberClubRole.year == year,
            ClubRole.hours_exempt == True,
        )
        .limit(1)
    )
    return result.scalar_one_or_none() is not None


# Parcel statuses the evaluation looks at. TERMINATED is included so a
# plot given up during the year still shows (and owes) that year's hours
# (issue #239) -- a parcel with no tenancy in the year is skipped anyway.
EVALUATED_PARCEL_STATUSES = (ParcelStatus.ACTIVE, ParcelStatus.TERMINATED)


def _member_in_year(member: Member, year: int) -> bool:
    """Not soft-deleted, membership not over before the year began."""
    return member.deleted_at is None and (
        member.member_until is None or member.member_until >= date(year, 1, 1)
    )


def _moved_on(assignment: MemberParcel, year: int) -> bool:
    """Whether this tenancy ended because its member moved to another
    plot of the club: a later tenancy of theirs on a different parcel
    also falls in `year`. They owe the year once, on the plot they moved
    to -- otherwise PER_PARCEL would credit their (per-member) hours and
    exemption to both plots (review finding on issue #239). Needs the
    member's parcel_assignments loaded."""
    if assignment.assigned_until is None:
        return False
    return any(
        other.parcel_id != assignment.parcel_id
        and other.overlaps_year(year)
        and (other.assigned_until is None or other.assigned_until > assignment.assigned_until)
        for other in assignment.member.parcel_assignments
    )


def _lease_ended_on(assignments, year: int) -> Optional[date]:
    """The day a tenant's lease ended, if it ended within `year` and by
    today -- the evaluation page marks them "lease ended" (issue #239).
    None while any of their tenancies in that year is still current or
    ran past the end of the year (a full-year tenant for that year)."""
    in_year = [a for a in assignments if a.overlaps_year(year)]
    cutoff = min(date.today(), date(year, 12, 31))
    if not in_year or any(a.assigned_until is None or a.assigned_until > cutoff for a in in_year):
        return None
    return max(a.assigned_until for a in in_year)


async def evaluate_parcel(db: AsyncSession, parcel: Parcel, year: int, *, config: WorkHoursConfiguration) -> Optional[dict]:
    """Evaluates one parcel's standing for PER_PARCEL mode. Returns None
    if the parcel had no tenants in `year` -- skip it, same as every
    caller always did.

    "Tenant" means the tenancy overlaps the evaluated year
    (MemberParcel.overlaps_year), not "current today" (issue #239): a
    lease cancelled in June still owes the full year, pooled on the
    parcel with whoever took it over. A lease that ended before the
    year began doesn't count (issue #206), nor one its member left for
    another plot of the club during the year (_moved_on)."""
    assignments = [
        z for z in parcel.member_assignments
        if z.overlaps_year(year) and _member_in_year(z.member, year) and not _moved_on(z, year)
    ]
    if not assignments:
        return None

    total_hours = 0.0
    tenant_details = []
    for z in assignments:
        m = z.member
        hours = await calculate_hours_for_member(db, m.id, year)
        exempt = await is_exempt(db, m.id, year)
        total_hours += hours["total"]
        tenant_details.append({
            "member": m, "hours": hours, "exempt": exempt,
            "lease_ended_on": _lease_ended_on([z], year),
        })

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
        "lease_ended_on": _lease_ended_on(member.parcel_assignments, year),
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
            .options(
                selectinload(Parcel.member_assignments)
                .selectinload(MemberParcel.member)
                .selectinload(Member.parcel_assignments)
            )
            .where(Parcel.status.in_(EVALUATED_PARCEL_STATUSES))
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
            .where(
                Member.deleted_at.is_(None),
                (Member.member_until.is_(None)) | (Member.member_until >= date(year, 1, 1)),
                Member.parcel_assignments.any(tenant_in_year_filter(year)),
            )
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
    signup_deadline_days: Optional[int] = None,
) -> WorkSession:
    session = WorkSession(
        title=title.strip(), description=(description or "").strip() or None, type=SessionType(type),
        date=date_value, time_from=(time_from or "").strip() or None, time_until=(time_until or "").strip() or None,
        max_participants=max_participants, hours_per_participant=hours_per_participant,
        created_by_id=created_by_id, signup_deadline_days=signup_deadline_days,
    )
    db.add(session)
    await db.flush()
    return session


async def update_session(db: AsyncSession, session: WorkSession, **fields) -> WorkSession:
    optional_string_fields = {"description", "time_from", "time_until"}
    for key in (
        "title", "description", "type", "date", "time_from", "time_until",
        "max_participants", "hours_per_participant", "signup_deadline_days",
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


def new_participation_cutoff(within_days: int = NEW_PARTICIPATION_WINDOW_DAYS) -> datetime:
    """Shared cutoff for "counts as a new sign-up" -- used by
    count_new_participations() below and by the session-detail template
    to mark individual rows (app/routers/work_hours.py)."""
    return datetime.now(timezone.utc) - timedelta(days=within_days)


async def count_new_participations(db: AsyncSession, within_days: int = NEW_PARTICIPATION_WINDOW_DAYS) -> int:
    """Issue #217: how many SessionParticipation rows were created in
    the last `within_days` days, for a session that is both STANDARD
    (never SPECIAL -- same distinction the public site/community
    calendar already draw) and still upcoming (`date >= today`) --
    status-agnostic otherwise (a row counts regardless of
    REGISTERED/ATTENDED/NO_SHOW, since "newly registered" is about when
    the row was created, not its current state).

    Originally counted every new participation regardless of the
    session's own type or date -- in practice that surfaced staff
    retroactively recording attendance on long-past sessions and
    SPECIAL (spontaneous/unplanned) sessions as "new," swamping the
    count with noise nobody needed to act on. See docs/ADR/0079.

    Also excludes anything a session's "mark reviewed" button
    (`mark_signups_reviewed()` below) has already cleared -- a
    participation only counts if it's newer than
    `WorkSession.signups_reviewed_at` (NULL = never reviewed, no
    additional filtering).
    """
    result = await db.execute(
        select(func.count()).select_from(SessionParticipation)
        .join(WorkSession, WorkSession.id == SessionParticipation.session_id)
        .where(
            SessionParticipation.created_at >= new_participation_cutoff(within_days),
            WorkSession.type == SessionType.STANDARD,
            WorkSession.date >= date.today(),
            or_(
                WorkSession.signups_reviewed_at.is_(None),
                SessionParticipation.created_at > WorkSession.signups_reviewed_at,
            ),
        )
    )
    return result.scalar_one()


async def mark_signups_reviewed(db: AsyncSession, session: WorkSession) -> None:
    """Clears the "New" badges/count for whatever participants exist on
    this session right now -- a participant added after this call still
    shows as new again, until the next review or the rolling window
    (NEW_PARTICIPATION_WINDOW_DAYS) passes on its own."""
    session.signups_reviewed_at = datetime.now(timezone.utc)
    await db.flush()


def jinja_new_participations_count(request) -> int:
    """Jinja global for base.html's second nav badge -- reads the count
    new_participations_count_middleware (app/main.py) already computed
    once per request."""
    return getattr(request.state, "new_participations_count", 0)


async def _active_admin_board_recipients(db: AsyncSession, *, exclude_user_id: Optional[str] = None) -> List[User]:
    conditions = [User.role.in_([UserRole.ADMIN, UserRole.BOARD]), User.is_active == True]  # noqa: E712
    if exclude_user_id is not None:
        conditions.append(User.id != exclude_user_id)
    result = await db.execute(select(User).where(*conditions))
    return list(result.scalars().all())


async def notify_new_participation(
    db: AsyncSession, participation: SessionParticipation, *, member: Member, session: WorkSession,
    actor: User, lang: str,
) -> None:
    """Issue #217: emails active Admin/Board users (excluding `actor`)
    when a member is newly added as a participant on a work session
    through the single-row staff form/API. Deliberately NOT called for
    the already-registered no-op (add_participation() returns None
    there -- callers only reach this when a row was actually created).
    Not used by the public self-service signup path either -- see
    notify_new_participations_digest below. Caller is responsible for
    having already committed the row."""
    recipients = await _active_admin_board_recipients(db, exclude_user_id=actor.id)
    if not recipients:
        return

    subject = translate("email.new_participation_notification.subject", lang, app_name=settings.app_name)
    session_label = f"{session.title} ({session.date.strftime('%d.%m.%Y')})"
    for recipient in recipients:
        html = f"""
        <html><body>
        <p>{translate("email.new_participation_notification.greeting", lang, name=recipient.name)}</p>
        <p>{translate("email.new_participation_notification.body", lang, app_name=settings.app_name)}</p>
        <p><strong>{member.full_name}</strong> &mdash; {session_label}</p>
        <p>{translate("email.new_participation_notification.instruction", lang, app_name=settings.app_name)}</p>
        </body></html>
        """
        await send_email(recipient.email, subject, html, db=db)


async def notify_new_participations_digest(db: AsyncSession, count: int, lang: str) -> None:
    """Issue #217: one digest email for the public self-service signup
    path (app/routers/api_public.py::submit_signup) -- that endpoint is
    actorless (token-authenticated, not a logged-in user) and can create
    several SessionParticipation rows in one call (multiple sessions x
    an ambiguous-name match registering a whole household), so a
    per-row email would spam Admin/Board the same way one email per CSV-
    imported member would (see docs/ADR/0079) -- one summary email per
    call instead, to every active Admin/Board user, no exclusion since
    there's no actor to exclude."""
    if count <= 0:
        return
    recipients = await _active_admin_board_recipients(db)
    if not recipients:
        return

    subject = translate("email.new_participation_digest.subject", lang, count=count, app_name=settings.app_name)
    for recipient in recipients:
        html = f"""
        <html><body>
        <p>{translate("email.new_participation_notification.greeting", lang, name=recipient.name)}</p>
        <p>{translate("email.new_participation_digest.body", lang, count=count, app_name=settings.app_name)}</p>
        </body></html>
        """
        await send_email(recipient.email, subject, html, db=db)


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


class SponsorshipDatesError(ValueError):
    """End date before start date (issue #245). Such a sponsorship
    overlaps no year at all, so the evaluation silently credited it
    nothing -- a typo in the year (2025 for 2026) was enough."""


def _check_sponsorship_dates(valid_from: Optional[date], valid_until: Optional[date]) -> None:
    if valid_from and valid_until and valid_until < valid_from:
        raise SponsorshipDatesError("sponsorship_end_before_start")


async def create_sponsorship(
    db: AsyncSession, *, member_id: Optional[str], area: str, description: Optional[str],
    credited_hours: float, valid_from: Optional[date] = None, valid_until: Optional[date] = None,
) -> Sponsorship:
    _check_sponsorship_dates(valid_from, valid_until)
    sponsorship = Sponsorship(
        member_id=member_id or None, area=area.strip(), description=(description or "").strip() or None,
        credited_hours=credited_hours, valid_from=valid_from, valid_until=valid_until,
    )
    db.add(sponsorship)
    await db.flush()
    return sponsorship


# ---------------------------------------------------------------------------
# Hours transfers (issue #243, ADR 0094): a member gives surplus hours of
# a year to another member.
# ---------------------------------------------------------------------------

async def transferable_hours(db: AsyncSession, member_id: str, year: int) -> float:
    """How many hours `member_id` can still give away for `year`: what
    they did beyond what they owe, never more than their own hours.

    - PER_MEMBER: own total minus the requirement.
    - PER_PARCEL: the surplus of the plot(s) they're a tenant of that
      year (hours are pooled there, so giving must not push the plot
      below its requirement), capped at their own total -- a co-tenant's
      hours aren't theirs to give. With several plots, the smallest
      surplus counts.
    - Exempt, or no lease that year (a helper without a plot): nothing
      is owed, so all of their own hours.
    Their own total already nets earlier transfers in and out."""
    config = await get_config_for_year(db, year)
    if config is None:
        raise ServiceError("work_hours.errors.no_configuration_for_year", year=year)
    own = (await calculate_hours_for_member(db, member_id, year))["total"]
    if await is_exempt(db, member_id, year):
        return max(0.0, own)

    if config.mode == WorkHoursMode.PER_MEMBER:
        # Same rule as evaluate_year: only a tenant in that year owes hours.
        has_lease = await db.scalar(
            select(MemberParcel.id).where(MemberParcel.member_id == member_id, tenant_in_year_filter(year)).limit(1)
        )
        return max(0.0, own - float(config.hours_required)) if has_lease else max(0.0, own)

    parcels = (await db.scalars(
        select(Parcel)
        .join(MemberParcel, MemberParcel.parcel_id == Parcel.id)
        .where(MemberParcel.member_id == member_id, tenant_in_year_filter(year))
        .options(
            selectinload(Parcel.member_assignments)
            .selectinload(MemberParcel.member)
            .selectinload(Member.parcel_assignments)
        )
    )).unique().all()
    surpluses = []
    for parcel in parcels:
        row = await evaluate_parcel(db, parcel, year, config=config)
        if row is None or not any(t["member"].id == member_id for t in row["tenant_details"]):
            continue  # e.g. they moved off this plot during the year
        surpluses.append(own if row["exempt"] else row["total_hours"] - row["required_hours"])
    if not surpluses:
        return max(0.0, own)
    return max(0.0, min([own] + surpluses))


async def create_hours_transfer(
    db: AsyncSession, *, giver_member_id: str, receiver_member_id: str, year: int,
    hours: float, note: Optional[str] = None, created_by_id: Optional[str] = None,
) -> HoursTransfer:
    if not giver_member_id or not receiver_member_id:
        raise ServiceError("work_hours.transfers.errors.members_required")
    if giver_member_id == receiver_member_id:
        raise ServiceError("work_hours.transfers.errors.same_member")
    hours = float(hours)
    if not math.isfinite(hours) or round(hours, 1) <= 0:  # float("nan") passes every comparison
        raise ServiceError("work_hours.transfers.errors.hours_positive")
    hours = round(hours, 1)
    for member_id in (giver_member_id, receiver_member_id):
        member = await db.get(Member, member_id)
        if member is None or member.deleted_at is not None:
            raise ServiceError("work_hours.transfers.errors.member_not_found", http_status=404)

    # Lock the giver's row for this transaction: two transfers from the
    # same giver submitted at once would otherwise both see the full
    # surplus and together give more than it.
    await db.execute(select(Member.id).where(Member.id == giver_member_id).with_for_update())
    available = await transferable_hours(db, giver_member_id, year)
    if hours > available + 1e-9:
        raise ServiceError("work_hours.transfers.errors.exceeds_surplus", available=f"{available:.1f}")

    transfer = HoursTransfer(
        giver_member_id=giver_member_id, receiver_member_id=receiver_member_id, year=year,
        hours=hours, note=(note or "").strip() or None, created_by_id=created_by_id,
    )
    db.add(transfer)
    await db.flush()
    return transfer


async def list_hours_transfers(db: AsyncSession, year: int) -> List[HoursTransfer]:
    return list((await db.scalars(
        select(HoursTransfer)
        .options(
            selectinload(HoursTransfer.giver), selectinload(HoursTransfer.receiver),
            selectinload(HoursTransfer.created_by),
        )
        .where(HoursTransfer.year == year)
        .order_by(HoursTransfer.created_at.desc())
    )).all())


async def update_sponsorship(db: AsyncSession, sponsorship: Sponsorship, **fields) -> Sponsorship:
    # Checked against the stored date for a partial (API) update, and
    # before anything is changed.
    _check_sponsorship_dates(
        fields.get("valid_from", sponsorship.valid_from),
        fields.get("valid_until", sponsorship.valid_until),
    )
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
