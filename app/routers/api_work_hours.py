"""
API router: Work Hours -- configuration, club roles, work sessions,
sponsorships, evaluation.

Business logic shared with app/routers/work_hours.py (HTML) lives in
app/services/work_hours.py (ADR 0070) -- this router owns bearer-token
authentication, the fine-grained permission check (require_api_permission,
Group-based like the HTML side), Pydantic body parsing, and JSON
response serialization.
"""
from datetime import date
from decimal import Decimal
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_

from app.database import get_db
from app.models import (
    WorkHoursConfiguration, WorkHoursMode,
    ClubRole, MemberClubRole,
    WorkSession, SessionParticipation, SessionType, ParticipationStatus,
    Sponsorship, User,
    WorkTask, TaskWorkload,
)
from app.api_auth import require_api_permission
from app.i18n import t_for
from app.module_flags import require_module
from app.services.errors import ServiceError
from app.services.work_hours import (
    get_config_for_year, save_configuration_for_year, evaluate_year,
    create_club_role, update_club_role, assign_member_to_club_role,
    create_session, update_session, add_participation, update_participation,
    create_sponsorship, update_sponsorship,
    create_task, schedule_task, assign_task_to_participant,
)
from app.schemas import (
    WorkHoursConfigurationOut, WorkHoursConfigurationCreate,
    ClubRoleOut, ClubRoleCreate,
    MemberClubRoleOut, MemberClubRoleCreate,
    WorkSessionOut, WorkSessionCreate, WorkSessionUpdate,
    SessionParticipationOut, SessionParticipationCreate, SessionParticipationUpdate,
    SponsorshipOut, SponsorshipCreate, SponsorshipUpdate,
    TaskOut, TaskCreate, TaskUpdate,
    EvaluationRowOut,
)

router = APIRouter(
    prefix="/api/v1/work-hours",
    tags=["API: Work Hours"],
    dependencies=[Depends(require_module("work_hours"))],
)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

@router.get("/configuration", response_model=List[WorkHoursConfigurationOut], summary="List configurations")
async def configurations_list(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission("work_hours", "read")),
):
    result = await db.execute(
        select(WorkHoursConfiguration).order_by(WorkHoursConfiguration.year.desc())
    )
    return result.scalars().all()


@router.get("/configuration/{year}", response_model=WorkHoursConfigurationOut, summary="Retrieve configuration for a year")
async def configuration_get(
    year: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission("work_hours", "read")),
):
    config = await get_config_for_year(db, year)
    if not config:
        raise HTTPException(status_code=404, detail=f"No configuration for {year}")
    return config


@router.put(
    "/configuration/{year}", response_model=WorkHoursConfigurationOut,
    summary="Set configuration (upsert)",
    description="Creates the configuration for a year or updates it if one already exists.",
)
async def configuration_set(
    year: int,
    data: WorkHoursConfigurationCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission("work_hours", "write")),
):
    config = await save_configuration_for_year(
        db, year, hours_required=data.hours_required, rate_per_hour_eur=data.rate_per_hour_eur,
        mode=data.mode, note=data.note,
    )
    await db.commit()
    await db.refresh(config)
    return config


# ---------------------------------------------------------------------------
# Club Roles
# ---------------------------------------------------------------------------

@router.get("/club-roles", response_model=List[ClubRoleOut], summary="List club roles")
async def club_roles_list(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission("work_hours", "read")),
):
    result = await db.execute(select(ClubRole).order_by(ClubRole.name))
    return result.scalars().all()


@router.post(
    "/club-roles", response_model=ClubRoleOut, status_code=status.HTTP_201_CREATED,
    summary="Create club role",
)
async def club_role_create(
    data: ClubRoleCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission("work_hours", "write")),
):
    role = await create_club_role(
        db, name=data.name, description=data.description, hours_exempt=data.hours_exempt,
        exemption_reason=data.exemption_reason,
    )
    await db.commit()
    await db.refresh(role)
    return role


@router.put("/club-roles/{role_id}", response_model=ClubRoleOut, summary="Update club role")
async def club_role_update(
    role_id: str,
    data: ClubRoleCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission("work_hours", "write")),
):
    result = await db.execute(select(ClubRole).where(ClubRole.id == role_id))
    role = result.scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=404, detail="Club role not found")

    await update_club_role(
        db, role, name=data.name, description=data.description, hours_exempt=data.hours_exempt,
        exemption_reason=data.exemption_reason,
    )
    await db.commit()
    await db.refresh(role)
    return role


@router.delete(
    "/club-roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete club role",
    description="Also deletes the role's member assignments (cascade).",
)
async def club_role_delete(
    role_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission("work_hours", "delete")),
):
    result = await db.execute(select(ClubRole).where(ClubRole.id == role_id))
    role = result.scalar_one_or_none()
    if role:
        await db.delete(role)
        await db.commit()


@router.get(
    "/club-roles/assignments", response_model=List[MemberClubRoleOut],
    summary="List member club-role assignments",
)
async def assignments_list(
    year: Optional[int] = Query(None),
    member_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission("work_hours", "read")),
):
    query = select(MemberClubRole)
    if year:
        query = query.where(MemberClubRole.year == year)
    if member_id:
        query = query.where(MemberClubRole.member_id == member_id)
    result = await db.execute(query)
    return result.scalars().all()


@router.post(
    "/club-roles/assignments", response_model=MemberClubRoleOut,
    status_code=status.HTTP_201_CREATED, summary="Assign member to a club role",
    description="Returns 409 if this member/role/year combination is already assigned.",
)
async def assignment_create(
    data: MemberClubRoleCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission("work_hours", "write")),
):
    assignment = await assign_member_to_club_role(
        db, member_id=data.member_id, club_role_id=data.club_role_id, year=data.year,
        valid_from=data.valid_from, valid_until=data.valid_until, note=data.note,
    )
    if assignment is None:
        raise HTTPException(status_code=409, detail="This member/role/year combination is already assigned")
    await db.commit()
    await db.refresh(assignment)
    return assignment


@router.delete(
    "/club-roles/assignments/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove assignment",
)
async def assignment_delete(
    assignment_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission("work_hours", "write")),
):
    result = await db.execute(select(MemberClubRole).where(MemberClubRole.id == assignment_id))
    assignment = result.scalar_one_or_none()
    if assignment:
        await db.delete(assignment)
        await db.commit()


# ---------------------------------------------------------------------------
# Work Sessions
# ---------------------------------------------------------------------------

@router.get("/sessions", response_model=List[WorkSessionOut], summary="List work sessions")
async def sessions_list(
    year: Optional[int] = Query(None, description="Filter by year"),
    type: Optional[str] = Query(None, description="STANDARD or SPECIAL"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission("work_hours", "read")),
):
    query = select(WorkSession).order_by(WorkSession.date.desc())
    if year:
        from sqlalchemy import extract
        query = query.where(extract("year", WorkSession.date) == year)
    if type:
        query = query.where(WorkSession.type == SessionType(type))
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/sessions/{session_id}", response_model=WorkSessionOut, summary="Retrieve session")
async def session_get(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission("work_hours", "read")),
):
    result = await db.execute(select(WorkSession).where(WorkSession.id == session_id))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Work session not found")
    return session


@router.post(
    "/sessions", response_model=WorkSessionOut, status_code=status.HTTP_201_CREATED,
    summary="Create work session",
)
async def session_create(
    data: WorkSessionCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission("work_hours", "write")),
):
    session = await create_session(
        db, title=data.title, description=data.description, type=data.type, date_value=data.date,
        time_from=data.time_from, time_until=data.time_until,
        max_participants=data.max_participants, hours_per_participant=data.hours_per_participant,
        created_by_id=user.id,
    )
    await db.commit()
    await db.refresh(session)
    return session


@router.put("/sessions/{session_id}", response_model=WorkSessionOut, summary="Update session")
async def session_update(
    session_id: str,
    data: WorkSessionUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission("work_hours", "write")),
):
    result = await db.execute(select(WorkSession).where(WorkSession.id == session_id))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Work session not found")

    await update_session(db, session, **data.model_dump(exclude_unset=True))
    await db.commit()
    await db.refresh(session)
    return session


@router.delete(
    "/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete session", description="Also deletes all participations (cascade).",
)
async def session_delete(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission("work_hours", "delete")),
):
    result = await db.execute(select(WorkSession).where(WorkSession.id == session_id))
    session = result.scalar_one_or_none()
    if session:
        await db.delete(session)
        await db.commit()


# ---------------------------------------------------------------------------
# Participations (sub-resource of sessions)
# ---------------------------------------------------------------------------

@router.get(
    "/sessions/{session_id}/participations", response_model=List[SessionParticipationOut],
    summary="List participations of a session",
)
async def participations_list(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission("work_hours", "read")),
):
    result = await db.execute(
        select(SessionParticipation).where(SessionParticipation.session_id == session_id)
    )
    return result.scalars().all()


@router.post(
    "/sessions/{session_id}/participations", response_model=SessionParticipationOut,
    status_code=status.HTTP_201_CREATED, summary="Register participation",
)
async def participation_create(
    session_id: str,
    data: SessionParticipationCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission("work_hours", "write")),
):
    participation = await add_participation(
        db, session_id, member_id=data.member_id, status=data.status,
        hours_completed=data.hours_completed, note=data.note,
    )
    if participation is None:
        raise HTTPException(status_code=409, detail="Member is already registered")
    await db.commit()
    await db.refresh(participation)
    return participation


@router.put(
    "/sessions/{session_id}/participations/{participation_id}", response_model=SessionParticipationOut,
    summary="Update participation",
)
async def participation_update(
    session_id: str,
    participation_id: str,
    data: SessionParticipationUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission("work_hours", "write")),
):
    result = await db.execute(
        select(SessionParticipation).where(
            SessionParticipation.id == participation_id, SessionParticipation.session_id == session_id
        )
    )
    participation = result.scalar_one_or_none()
    if not participation:
        raise HTTPException(status_code=404, detail="Participation not found")

    await update_participation(db, participation, **data.model_dump(exclude_unset=True))
    await db.commit()
    await db.refresh(participation)
    return participation


@router.delete(
    "/sessions/{session_id}/participations/{participation_id}", status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove participation",
)
async def participation_delete(
    session_id: str,
    participation_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission("work_hours", "delete")),
):
    result = await db.execute(
        select(SessionParticipation).where(
            SessionParticipation.id == participation_id, SessionParticipation.session_id == session_id
        )
    )
    participation = result.scalar_one_or_none()
    if participation:
        await db.delete(participation)
        await db.commit()


# ---------------------------------------------------------------------------
# Sponsorships
# ---------------------------------------------------------------------------

@router.get("/sponsorships", response_model=List[SponsorshipOut], summary="List sponsorships")
async def sponsorships_list(
    year: Optional[int] = Query(None, description="Only sponsorships active in this year"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission("work_hours", "read")),
):
    query = select(Sponsorship).order_by(Sponsorship.area)
    if year:
        query = query.where(
            or_(
                Sponsorship.valid_from.is_(None),
                and_(
                    Sponsorship.valid_from <= date(year, 12, 31),
                    or_(Sponsorship.valid_until.is_(None), Sponsorship.valid_until >= date(year, 1, 1)),
                ),
            )
        )
    result = await db.execute(query)
    return result.scalars().all()


@router.post(
    "/sponsorships", response_model=SponsorshipOut, status_code=status.HTTP_201_CREATED,
    summary="Create sponsorship",
    description="member_id is optional -- a sponsorship can be created before it's assigned to anyone.",
)
async def sponsorship_create(
    data: SponsorshipCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission("work_hours", "write")),
):
    sponsorship = await create_sponsorship(
        db, member_id=data.member_id, area=data.area, description=data.description,
        credited_hours=data.credited_hours, valid_from=data.valid_from, valid_until=data.valid_until,
    )
    await db.commit()
    await db.refresh(sponsorship)
    return sponsorship


@router.put("/sponsorships/{sponsorship_id}", response_model=SponsorshipOut, summary="Update sponsorship")
async def sponsorship_update(
    sponsorship_id: str,
    data: SponsorshipUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission("work_hours", "write")),
):
    result = await db.execute(select(Sponsorship).where(Sponsorship.id == sponsorship_id))
    sponsorship = result.scalar_one_or_none()
    if not sponsorship:
        raise HTTPException(status_code=404, detail="Sponsorship not found")

    await update_sponsorship(db, sponsorship, **data.model_dump(exclude_unset=True))
    await db.commit()
    await db.refresh(sponsorship)
    return sponsorship


@router.delete(
    "/sponsorships/{sponsorship_id}", status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete sponsorship",
)
async def sponsorship_delete(
    sponsorship_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission("work_hours", "delete")),
):
    result = await db.execute(select(Sponsorship).where(Sponsorship.id == sponsorship_id))
    sponsorship = result.scalar_one_or_none()
    if sponsorship:
        await db.delete(sponsorship)
        await db.commit()


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------

@router.get(
    "/evaluation/{year}", response_model=List[EvaluationRowOut],
    summary="Retrieve annual report",
    description=(
        "Calculates the work-hours status depending on the configured mode "
        "(PER_PARCEL or PER_MEMBER): hours completed, hours outstanding, amount owed, "
        "exemption status."
    ),
)
async def evaluation_get(
    year: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission("work_hours", "read")),
):
    config, rows = await evaluate_year(db, year)
    if not config:
        raise HTTPException(status_code=404, detail=f"No configuration for {year}")

    required = Decimal(str(config.hours_required))
    rate = Decimal(str(config.rate_per_hour_eur))
    out: List[EvaluationRowOut] = []
    if config.mode == WorkHoursMode.PER_PARCEL:
        for row in rows:
            total = Decimal(str(row["total_hours"]))
            outstanding = Decimal(str(row["outstanding_hours"]))
            out.append(EvaluationRowOut(
                label=row["parcel"].plot_number,
                hours_required=required, hours_completed=total, hours_open=outstanding,
                amount_due_eur=outstanding * rate,
                exempt=row["exempt"], fulfilled=row["fulfilled"],
            ))
    else:
        for row in rows:
            total = Decimal(str(row["hours"]["total"]))
            outstanding = Decimal(str(row["outstanding_hours"]))
            out.append(EvaluationRowOut(
                label=row["member"].full_name,
                hours_required=required, hours_completed=total, hours_open=outstanding,
                amount_due_eur=outstanding * rate,
                exempt=row["exempt"], fulfilled=row["fulfilled"],
            ))
    return out


# ---------------------------------------------------------------------------
# Tasks: a backlog of upcoming work, optionally scheduled to a session and
# assigned to one signed-up participant. See app/routers/work_hours.py for
# the fuller explanation of the workload/assignment model -- summary:
# the app stores a workload label (light/moderate/demanding) per task; the
# actual matching of task to person is a manual, human judgment call.
# ---------------------------------------------------------------------------

@router.get("/tasks", response_model=List[TaskOut], summary="List tasks")
async def list_tasks(
    session_id: Optional[str] = Query(None, description="Filter by session (omit for all tasks, including the backlog)"),
    backlog_only: bool = Query(False, description="Only tasks not yet scheduled to any session"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission("work_hours", "read")),
):
    query = select(WorkTask).order_by(WorkTask.created_at.desc())
    if backlog_only:
        query = query.where(WorkTask.session_id.is_(None))
    elif session_id:
        query = query.where(WorkTask.session_id == session_id)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/tasks", response_model=TaskOut, status_code=status.HTTP_201_CREATED, summary="Create a task")
async def create_task_endpoint(
    data: TaskCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission("work_hours", "write")),
):
    task = await create_task(
        db, title=data.title, description=data.description, workload=data.workload,
        session_id=data.session_id, created_by_id=user.id,
    )
    await db.commit()
    await db.refresh(task)
    return task


@router.put("/tasks/{task_id}", response_model=TaskOut, summary="Update a task")
async def update_task(
    task_id: str,
    data: TaskUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission("work_hours", "write")),
):
    result = await db.execute(select(WorkTask).where(WorkTask.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if data.title is not None:
        task.title = data.title
    if data.description is not None:
        task.description = data.description
    if data.workload is not None:
        task.workload = TaskWorkload(data.workload)
    if data.session_id is not None:
        await schedule_task(db, task, session_id=data.session_id)
    if data.assigned_participation_id is not None:
        try:
            await assign_task_to_participant(db, task, participation_id=data.assigned_participation_id)
        except ServiceError as e:
            # This API's pre-existing convention for these two checks was
            # 400 (not the 422 tickets/metering use for their own rule
            # violations) -- kept as-is (e.http_status is 400), only the
            # previously-hard-coded English text now shares HTML's i18n key.
            raise HTTPException(status_code=e.http_status, detail=t_for(request, e.key, **e.params))
    if data.is_done is not None:
        task.is_done = data.is_done

    await db.commit()
    await db.refresh(task)
    return task


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a task")
async def delete_task(
    task_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission("work_hours", "delete")),
):
    result = await db.execute(select(WorkTask).where(WorkTask.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    await db.delete(task)
    await db.commit()
