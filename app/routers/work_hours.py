"""
Work hours router: work sessions, sponsorships, club roles, configuration.
"""
import csv
import io
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Optional, List

from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.database import get_db, active_member_filter
from app.csv_utils import csv_safe
from app.models import (
    WorkSession, SessionParticipation, SessionType, ParticipationStatus,
    Sponsorship, ClubRole, MemberClubRole, ExemptionReason,
    WorkHoursConfiguration, WorkHoursMode,
    Member, MemberParcel,
    WorkTask, TaskWorkload,
)
from app.permissions import require_permission
from app.i18n import t_for, load_current_language
from app.branding import load_branding
from app.pdf_chrome import load_org_footer_context
from app.l10n import load_current_region, format_number
from app.session_attendee_sheet import render_session_attendee_sheet_pdf, AttendeeRow

from app.module_flags import require_module
from app.services.errors import ServiceError
from app.services.work_hours import (
    get_config_for_year, evaluate_year, save_configuration_for_year,
    create_club_role, update_club_role, assign_member_to_club_role,
    create_session, update_session, add_participation, update_participation,
    create_sponsorship, update_sponsorship,
    create_task, schedule_task, assign_task_to_participant, toggle_task_done,
)

router = APIRouter(
    prefix="/work-hours",
    tags=["work-hours"],
    dependencies=[Depends(require_module("work_hours"))],
)
from app.templating import templates


# ---------------------------------------------------------------------------
# Dashboard / Overview
# ---------------------------------------------------------------------------

@router.get("/", response_class=HTMLResponse)
async def work_hours_overview(
    request: Request,
    year: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
):
    user = await require_permission(request, db, "work_hours", "read")

    if not year:
        year = date.today().year

    config = await get_config_for_year(db, year)

    # All available years, for the dropdown
    years_result = await db.execute(
        select(WorkHoursConfiguration.year).order_by(WorkHoursConfiguration.year.desc())
    )
    available_years = [r[0] for r in years_result.all()]

    # Sessions of the year
    sessions_result = await db.execute(
        select(WorkSession)
        .options(selectinload(WorkSession.participations))
        .where(func.extract("year", WorkSession.date) == year)
        .order_by(WorkSession.date.desc())
    )
    sessions = sessions_result.scalars().all()

    return templates.TemplateResponse(
        "work_hours/overview.html",
        {
            "request": request,
            "user": user,
            "year": year,
            "config": config,
            "sessions": sessions,
            "available_years": available_years,
            "SessionType": SessionType,
            "ParticipationStatus": ParticipationStatus,
        },
    )


# ---------------------------------------------------------------------------
# Work hours configuration
# ---------------------------------------------------------------------------

@router.get("/configuration", response_class=HTMLResponse)
async def configuration_page(request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_permission(request, db, "work_hours", "read")

    result = await db.execute(
        select(WorkHoursConfiguration).order_by(WorkHoursConfiguration.year.desc())
    )
    configurations = result.scalars().all()

    return templates.TemplateResponse(
        "work_hours/configuration.html",
        {
            "request": request,
            "user": user,
            "configurations": configurations,
            "WorkHoursMode": WorkHoursMode,
            "current_year": date.today().year,
        },
    )


@router.get("/configuration/{configuration_id}/edit", response_class=HTMLResponse)
async def configuration_edit_page(
    configuration_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user = await require_permission(request, db, "work_hours", "write")

    result = await db.execute(
        select(WorkHoursConfiguration).where(WorkHoursConfiguration.id == configuration_id)
    )
    configuration = result.scalar_one_or_none()
    if not configuration:
        raise HTTPException(status_code=404, detail=t_for(request, "work_hours.errors.configuration_not_found"))

    return templates.TemplateResponse(
        "work_hours/configuration_form.html",
        {
            "request": request,
            "user": user,
            "configuration": configuration,
            "WorkHoursMode": WorkHoursMode,
        },
    )


@router.post("/configuration/{configuration_id}/edit")
async def configuration_update(
    configuration_id: str,
    request: Request,
    year: int = Form(...),
    hours_required: str = Form(...),
    rate_per_hour_eur: str = Form(...),
    mode: str = Form("PER_PARCEL"),
    note: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    await require_permission(request, db, "work_hours", "write")

    result = await db.execute(
        select(WorkHoursConfiguration).where(WorkHoursConfiguration.id == configuration_id)
    )
    configuration = result.scalar_one_or_none()
    if not configuration:
        raise HTTPException(status_code=404, detail=t_for(request, "work_hours.errors.configuration_not_found"))

    # If the year is being changed: check for a collision with another entry
    if year != configuration.year:
        kollision = await get_config_for_year(db, year)
        if kollision and kollision.id != configuration_id:
            raise HTTPException(
                status_code=400,
                detail=t_for(request, "work_hours.errors.configuration_year_exists", year=year)
            )

    configuration.year = year
    configuration.hours_required = float(hours_required.replace(",", "."))
    configuration.rate_per_hour_eur = float(rate_per_hour_eur.replace(",", "."))
    configuration.mode = WorkHoursMode(mode)
    configuration.note = note.strip() or None

    await db.commit()
    return RedirectResponse("/work-hours/configuration", status_code=302)


@router.post("/configuration/{configuration_id}/delete")
async def configuration_delete(
    configuration_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    await require_permission(request, db, "work_hours", "delete")

    result = await db.execute(
        select(WorkHoursConfiguration).where(WorkHoursConfiguration.id == configuration_id)
    )
    configuration = result.scalar_one_or_none()
    if configuration:
        await db.delete(configuration)
        await db.commit()

    return RedirectResponse("/work-hours/configuration", status_code=302)


@router.post("/configuration/new")
async def configuration_create(
    request: Request,
    year: int = Form(...),
    hours_required: str = Form(...),
    rate_per_hour_eur: str = Form(...),
    mode: str = Form("PER_PARCEL"),
    note: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    await require_permission(request, db, "work_hours", "write")

    await save_configuration_for_year(
        db, year,
        hours_required=float(hours_required.replace(",", ".")),
        rate_per_hour_eur=float(rate_per_hour_eur.replace(",", ".")),
        mode=mode, note=(note.strip() or None),
    )
    await db.commit()
    return RedirectResponse("/work-hours/configuration", status_code=302)


# ---------------------------------------------------------------------------
# Work Sessions
# ---------------------------------------------------------------------------

@router.get("/sessions/new", response_class=HTMLResponse)
async def session_new_page(request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_permission(request, db, "work_hours", "write")
    return templates.TemplateResponse(
        "work_hours/session_form.html",
        {
            "request": request,
            "user": user,
            "session": None,
            "SessionType": SessionType,
        },
    )


@router.post("/sessions/new")
async def session_create(
    request: Request,
    title: str = Form(...),
    description: str = Form(""),
    type: str = Form("STANDARD"),
    date_value: str = Form(..., alias="date"),
    time_from: str = Form(""),
    time_until: str = Form(""),
    max_participants: str = Form(""),
    hours_per_participant: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    user = await require_permission(request, db, "work_hours", "write")

    session = await create_session(
        db,
        title=title, description=description, type=type, date_value=date.fromisoformat(date_value),
        time_from=time_from, time_until=time_until,
        max_participants=(int(max_participants) if max_participants.strip() else None),
        hours_per_participant=(float(hours_per_participant.replace(",", ".")) if hours_per_participant.strip() else None),
        created_by_id=user.id,
    )
    await db.commit()
    return RedirectResponse(f"/work-hours/sessions/{session.id}", status_code=302)


@router.get("/sessions/{session_id}/edit", response_class=HTMLResponse)
async def session_edit_page(
    session_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user = await require_permission(request, db, "work_hours", "write")

    result = await db.execute(select(WorkSession).where(WorkSession.id == session_id))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail=t_for(request, "work_hours.errors.session_not_found"))

    return templates.TemplateResponse(
        "work_hours/session_form.html",
        {
            "request": request,
            "user": user,
            "session": session,
            "SessionType": SessionType,
        },
    )


@router.post("/sessions/{session_id}/edit")
async def session_update(
    session_id: str,
    request: Request,
    title: str = Form(...),
    description: str = Form(""),
    type: str = Form("STANDARD"),
    date_value: str = Form(..., alias="date"),
    time_from: str = Form(""),
    time_until: str = Form(""),
    max_participants: str = Form(""),
    hours_per_participant: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    await require_permission(request, db, "work_hours", "write")

    result = await db.execute(select(WorkSession).where(WorkSession.id == session_id))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail=t_for(request, "work_hours.errors.session_not_found"))

    await update_session(
        db, session,
        title=title, description=description, type=type, date=date.fromisoformat(date_value),
        time_from=time_from, time_until=time_until,
        max_participants=(int(max_participants) if max_participants.strip() else None),
        hours_per_participant=(float(hours_per_participant.replace(",", ".")) if hours_per_participant.strip() else None),
    )
    await db.commit()
    return RedirectResponse(f"/work-hours/sessions/{session_id}", status_code=302)


@router.post("/sessions/{session_id}/delete")
async def session_delete(
    session_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    await require_permission(request, db, "work_hours", "delete")

    result = await db.execute(select(WorkSession).where(WorkSession.id == session_id))
    session = result.scalar_one_or_none()
    if session:
        year = session.date.year
        await db.delete(session)
        await db.commit()
        return RedirectResponse(f"/work-hours/?year={year}", status_code=302)

    return RedirectResponse("/work-hours/", status_code=302)


@router.get("/sessions/{session_id}", response_class=HTMLResponse)
async def session_detail(
    session_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user = await require_permission(request, db, "work_hours", "read")

    result = await db.execute(
        select(WorkSession)
        .options(
            selectinload(WorkSession.participations)
            .selectinload(SessionParticipation.member)
            .selectinload(Member.parcel_assignments)
            .selectinload(MemberParcel.parcel)
        )
        .where(WorkSession.id == session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail=t_for(request, "work_hours.errors.session_not_found"))

    # All active members, for the signup search box (name or plot number)
    members_result = await db.execute(
        select(Member)
        .options(
            selectinload(Member.parcel_assignments).selectinload(MemberParcel.parcel)
        )
        .where(active_member_filter())
        .order_by(Member.last_name, Member.first_name)
    )
    all_members = members_result.scalars().all()
    already_registered = {t.member_id for t in session.participations}
    signup_members_json = [
        {
            "id": m.id,
            "name": m.full_name,
            "plots": ", ".join(pa.parcel.plot_number for pa in m.parcel_assignments if pa.is_current),
        }
        for m in all_members
        if m.id not in already_registered
    ]

    tasks_result = await db.execute(
        select(WorkTask)
        .options(selectinload(WorkTask.assigned_participation).selectinload(SessionParticipation.member))
        .where(WorkTask.session_id == session_id)
        .order_by(WorkTask.is_done, WorkTask.created_at)
    )
    session_tasks = tasks_result.scalars().all()

    return templates.TemplateResponse(
        "work_hours/session_detail.html",
        {
            "request": request,
            "user": user,
            "session": session,
            "signup_members_json": signup_members_json,
            "ParticipationStatus": ParticipationStatus,
            "SessionType": SessionType,
            "session_tasks": session_tasks,
            "TaskWorkload": TaskWorkload,
        },
    )


@router.get("/sessions/{session_id}/attendee-sheet")
async def session_attendee_sheet_pdf(
    session_id: str, request: Request, db: AsyncSession = Depends(get_db),
):
    """Generates the attendee sheet PDF for this session: registered
    participants with parcel, expected hours, any task assigned to
    them for this session, and a blank signature line -- meant for
    printing and bringing to the actual session so the coordinator can
    confirm attendance/hours on paper. Multi-page, like the general-
    meeting sign-in sheet (app/meeting_signin_sheet.py) -- a big
    session can have more attendees than fit on one page."""
    await require_permission(request, db, "work_hours", "read")

    result = await db.execute(
        select(WorkSession)
        .options(
            selectinload(WorkSession.participations)
            .selectinload(SessionParticipation.member)
            .selectinload(Member.parcel_assignments)
            .selectinload(MemberParcel.parcel)
        )
        .where(WorkSession.id == session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail=t_for(request, "work_hours.errors.session_not_found"))

    # One task can be assigned to a participation; a participant could
    # in principle have more than one (e.g. two small tasks) -- collect
    # all of them per participation rather than assuming exactly one.
    tasks_result = await db.execute(
        select(WorkTask).where(WorkTask.session_id == session_id, WorkTask.assigned_participation_id.isnot(None))
    )
    tasks_by_participation = {}
    for task in tasks_result.scalars().all():
        tasks_by_participation.setdefault(task.assigned_participation_id, []).append(task.title)

    region = await load_current_region(db)

    def current_parcel_numbers(member: Member) -> str:
        current = [pa.parcel.plot_number for pa in member.parcel_assignments if pa.is_current]
        return "; ".join(current)

    def sort_key(participation: SessionParticipation):
        parcels = current_parcel_numbers(participation.member)
        return (parcels, participation.member.last_name, participation.member.first_name)

    rows = []
    for participation in sorted(session.participations, key=sort_key):
        hours_value = participation.hours_completed
        if hours_value is None:
            hours_value = session.hours_per_participant
        hours_text = format_number(hours_value, region, decimals=1) if hours_value is not None else ""

        task_titles = tasks_by_participation.get(participation.id, [])

        rows.append(AttendeeRow(
            parcel=current_parcel_numbers(participation.member),
            member_name=participation.member.full_name,
            hours=hours_text,
            tasks="; ".join(task_titles),  # left blank if none assigned yet, per request
        ))

    subtitle_parts = [session.date.isoformat()]
    if session.time_from:
        time_range = session.time_from + (f" - {session.time_until}" if session.time_until else "")
        subtitle_parts.append(time_range)
    subtitle = ", ".join(subtitle_parts)

    branding = await load_branding(db)
    logo_path = Path("app" + branding["logo_url"]) if branding["logo_url"] else None
    language = await load_current_language(db)
    footer_context = await load_org_footer_context(db, branding["club_name"])

    pdf_bytes = render_session_attendee_sheet_pdf(
        session.title, subtitle, footer_context, logo_path, rows, language,
    )

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="attendee-sheet.pdf"'},
    )


@router.post("/sessions/{session_id}/participants/add")
async def participant_add(
    session_id: str,
    request: Request,
    member_id: str = Form(...),
    status: str = Form("ATTENDED"),
    hours_completed: str = Form(""),
    note: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    await require_permission(request, db, "work_hours", "write")

    participation = await add_participation(
        db, session_id, member_id=member_id, status=status,
        hours_completed=(float(hours_completed.replace(",", ".")) if hours_completed.strip() else None),
        note=note,
    )
    if participation is not None:
        await db.commit()
    return RedirectResponse(f"/work-hours/sessions/{session_id}", status_code=302)


@router.post("/sessions/{session_id}/participants/{participation_id}/status")
async def participation_status_change(
    session_id: str,
    participation_id: str,
    request: Request,
    status: str = Form(...),
    hours_completed: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    await require_permission(request, db, "work_hours", "write")

    result = await db.execute(
        select(SessionParticipation).where(SessionParticipation.id == participation_id)
    )
    participation = result.scalar_one_or_none()
    if participation:
        fields = {"status": status}
        if hours_completed.strip():
            fields["hours_completed"] = float(hours_completed.replace(",", "."))
        await update_participation(db, participation, **fields)
        await db.commit()

    return RedirectResponse(f"/work-hours/sessions/{session_id}", status_code=302)


@router.post("/sessions/{session_id}/participants/{participation_id}/remove")
async def participation_remove(
    session_id: str,
    participation_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    await require_permission(request, db, "work_hours", "delete")

    result = await db.execute(
        select(SessionParticipation).where(SessionParticipation.id == participation_id)
    )
    participation = result.scalar_one_or_none()
    if participation:
        await db.delete(participation)
        await db.commit()

    return RedirectResponse(f"/work-hours/sessions/{session_id}", status_code=302)


# ---------------------------------------------------------------------------
# Club Roles
# ---------------------------------------------------------------------------

@router.get("/club-roles", response_class=HTMLResponse)
async def club_roles_page(
    request: Request,
    year: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
):
    user = await require_permission(request, db, "work_hours", "read")

    if not year:
        year = date.today().year

    roles_result = await db.execute(
        select(ClubRole).order_by(ClubRole.name)
    )
    roles = roles_result.scalars().all()

    assignments_result = await db.execute(
        select(MemberClubRole)
        .options(
            selectinload(MemberClubRole.member),
            selectinload(MemberClubRole.club_role),
        )
        .where(MemberClubRole.year == year)
        .order_by(MemberClubRole.club_role_id)
    )
    assignments = assignments_result.scalars().all()

    members_result = await db.execute(
        select(Member)
        .where(active_member_filter())
        .order_by(Member.last_name, Member.first_name)
    )
    all_members = members_result.scalars().all()

    return templates.TemplateResponse(
        "work_hours/club-roles.html",
        {
            "request": request,
            "user": user,
            "roles": roles,
            "assignments": assignments,
            "all_members": all_members,
            "year": year,
            "ExemptionReason": ExemptionReason,
            "current_year": date.today().year,
        },
    )


@router.post("/club-roles/assign-member")
async def member_club_role_assign(
    request: Request,
    member_id: str = Form(...),
    club_role_id: str = Form(...),
    year: int = Form(...),
    valid_from: str = Form(""),
    valid_until: str = Form(""),
    note: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    await require_permission(request, db, "work_hours", "write")

    assignment = await assign_member_to_club_role(
        db, member_id=member_id, club_role_id=club_role_id, year=year,
        valid_from=(date.fromisoformat(valid_from) if valid_from.strip() else None),
        valid_until=(date.fromisoformat(valid_until) if valid_until.strip() else None),
        note=note,
    )
    if assignment is not None:
        await db.commit()

    return RedirectResponse(f"/work-hours/club-roles?year={year}", status_code=302)


@router.get("/club-roles/assignment/{assignment_id}/edit", response_class=HTMLResponse)
async def member_club_role_edit_page(
    assignment_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user = await require_permission(request, db, "work_hours", "write")

    result = await db.execute(
        select(MemberClubRole)
        .options(
            selectinload(MemberClubRole.member),
            selectinload(MemberClubRole.club_role),
        )
        .where(MemberClubRole.id == assignment_id)
    )
    assignment = result.scalar_one_or_none()
    if not assignment:
        raise HTTPException(status_code=404, detail=t_for(request, "work_hours.errors.assignment_not_found"))

    members_result = await db.execute(
        select(Member)
        .where(active_member_filter())
        .order_by(Member.last_name, Member.first_name)
    )
    all_members = members_result.scalars().all()

    roles_result = await db.execute(select(ClubRole).order_by(ClubRole.name))
    all_roles = roles_result.scalars().all()

    return templates.TemplateResponse(
        "work_hours/member_club_role_form.html",
        {
            "request": request,
            "user": user,
            "assignment": assignment,
            "all_members": all_members,
            "all_roles": all_roles,
        },
    )


@router.post("/club-roles/assignment/{assignment_id}/edit")
async def member_club_role_update(
    assignment_id: str,
    request: Request,
    member_id: str = Form(...),
    club_role_id: str = Form(...),
    year: int = Form(...),
    valid_from: str = Form(""),
    valid_until: str = Form(""),
    note: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    await require_permission(request, db, "work_hours", "write")

    result = await db.execute(
        select(MemberClubRole).where(MemberClubRole.id == assignment_id)
    )
    assignment = result.scalar_one_or_none()
    if not assignment:
        raise HTTPException(status_code=404, detail=t_for(request, "work_hours.errors.assignment_not_found"))

    assignment.member_id = member_id
    assignment.club_role_id = club_role_id
    assignment.year = year
    assignment.valid_from = date.fromisoformat(valid_from) if valid_from.strip() else None
    assignment.valid_until = date.fromisoformat(valid_until) if valid_until.strip() else None
    assignment.note = note.strip() or None

    await db.commit()
    return RedirectResponse(f"/work-hours/club-roles?year={year}", status_code=302)


@router.post("/club-roles/assignment/{assignment_id}/remove")
async def member_club_role_remove(
    assignment_id: str,
    request: Request,
    year: int = Form(0),
    db: AsyncSession = Depends(get_db),
):
    await require_permission(request, db, "work_hours", "delete")

    result = await db.execute(
        select(MemberClubRole).where(MemberClubRole.id == assignment_id)
    )
    assignment = result.scalar_one_or_none()
    return_year = assignment.year if assignment else date.today().year
    if assignment:
        await db.delete(assignment)
        await db.commit()

    return RedirectResponse(f"/work-hours/club-roles?year={return_year}", status_code=302)


@router.post("/club-roles/new")
async def club_role_create(
    request: Request,
    name: str = Form(...),
    description: str = Form(""),
    hours_exempt: bool = Form(False),
    exemption_reason: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    await require_permission(request, db, "work_hours", "write")

    await create_club_role(
        db, name=name, description=description, hours_exempt=hours_exempt, exemption_reason=(exemption_reason or None),
    )
    await db.commit()
    return RedirectResponse("/work-hours/club-roles", status_code=302)


@router.get("/club-roles/{role_id}/edit", response_class=HTMLResponse)
async def club_role_edit_page(
    role_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user = await require_permission(request, db, "work_hours", "write")

    result = await db.execute(select(ClubRole).where(ClubRole.id == role_id))
    role = result.scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=404, detail=t_for(request, "work_hours.errors.club_role_not_found"))

    return templates.TemplateResponse(
        "work_hours/club_role_form.html",
        {
            "request": request,
            "user": user,
            "role": role,
        },
    )


@router.post("/club-roles/{role_id}/edit")
async def club_role_update(
    role_id: str,
    request: Request,
    name: str = Form(...),
    description: str = Form(""),
    hours_exempt: bool = Form(False),
    exemption_reason: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    await require_permission(request, db, "work_hours", "write")

    result = await db.execute(select(ClubRole).where(ClubRole.id == role_id))
    role = result.scalar_one_or_none()
    if role:
        await update_club_role(
            db, role, name=name, description=description, hours_exempt=hours_exempt,
            exemption_reason=(exemption_reason or None),
        )
        await db.commit()

    return RedirectResponse("/work-hours/club-roles", status_code=302)


@router.post("/club-roles/{role_id}/delete")
async def club_role_delete(
    role_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    await require_permission(request, db, "work_hours", "delete")
    result = await db.execute(select(ClubRole).where(ClubRole.id == role_id))
    role = result.scalar_one_or_none()
    if role:
        await db.delete(role)
        await db.commit()
    return RedirectResponse("/work-hours/club-roles", status_code=302)


# ---------------------------------------------------------------------------
# Sponsorships
# ---------------------------------------------------------------------------

@router.get("/sponsorships", response_class=HTMLResponse)
async def sponsorships_page(
    request: Request,
    year: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
):
    user = await require_permission(request, db, "work_hours", "read")

    if not year:
        year = date.today().year

    query = (
        select(Sponsorship)
        .options(selectinload(Sponsorship.member))
        .where(
            Sponsorship.valid_from <= date(year, 12, 31),
            (Sponsorship.valid_until.is_(None)) | (Sponsorship.valid_until >= date(year, 1, 1)),
        )
        .order_by(Sponsorship.area)
    )
    result = await db.execute(query)
    sponsorships = result.scalars().all()

    # Group by area, so multiple members per area are shown together
    grouped_areas = {}
    for p in sponsorships:
        grouped_areas.setdefault(p.area, []).append(p)

    # All known area names (for autocomplete, including past years, to
    # avoid typos when reusing one)
    alle_bereiche_result = await db.execute(
        select(Sponsorship.area).distinct().order_by(Sponsorship.area)
    )
    all_areas = [r[0] for r in alle_bereiche_result.all()]

    # Current work-hours configuration, for pre-filling
    config = await get_config_for_year(db, year)

    members_result = await db.execute(
        select(Member)
        .where(active_member_filter())
        .order_by(Member.last_name, Member.first_name)
    )
    all_members = members_result.scalars().all()

    return templates.TemplateResponse(
        "work_hours/sponsorships.html",
        {
            "request": request,
            "user": user,
            "sponsorships": sponsorships,
            "grouped_areas": grouped_areas,
            "all_areas": all_areas,
            "config": config,
            "all_members": all_members,
            "year": year,
        },
    )


@router.post("/sponsorships/new")
async def sponsorship_create(
    request: Request,
    member_id: str = Form(""),
    area: str = Form(...),
    description: str = Form(""),
    credited_hours: str = Form(...),
    valid_from: str = Form(...),
    valid_until: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    await require_permission(request, db, "work_hours", "write")

    await create_sponsorship(
        db, member_id=member_id, area=area, description=description,
        credited_hours=float(credited_hours.replace(",", ".")),
        valid_from=date.fromisoformat(valid_from),
        valid_until=(date.fromisoformat(valid_until) if valid_until.strip() else None),
    )
    await db.commit()
    return RedirectResponse("/work-hours/sponsorships", status_code=302)


@router.get("/sponsorships/{sponsorship_id}/edit", response_class=HTMLResponse)
async def sponsorship_edit_page(
    sponsorship_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user = await require_permission(request, db, "work_hours", "write")

    result = await db.execute(
        select(Sponsorship)
        .options(selectinload(Sponsorship.member))
        .where(Sponsorship.id == sponsorship_id)
    )
    sponsorship = result.scalar_one_or_none()
    if not sponsorship:
        raise HTTPException(status_code=404, detail=t_for(request, "work_hours.errors.sponsorship_not_found"))

    members_result = await db.execute(
        select(Member)
        .where(active_member_filter())
        .order_by(Member.last_name, Member.first_name)
    )
    all_members = members_result.scalars().all()

    alle_bereiche_result = await db.execute(
        select(Sponsorship.area).distinct().order_by(Sponsorship.area)
    )
    all_areas = [r[0] for r in alle_bereiche_result.all()]

    return templates.TemplateResponse(
        "work_hours/sponsorship_form.html",
        {
            "request": request,
            "user": user,
            "sponsorship": sponsorship,
            "all_members": all_members,
            "all_areas": all_areas,
        },
    )


@router.post("/sponsorships/{sponsorship_id}/edit")
async def sponsorship_update(
    sponsorship_id: str,
    request: Request,
    member_id: str = Form(""),
    area: str = Form(...),
    description: str = Form(""),
    credited_hours: str = Form(...),
    valid_from: str = Form(...),
    valid_until: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    await require_permission(request, db, "work_hours", "write")

    result = await db.execute(select(Sponsorship).where(Sponsorship.id == sponsorship_id))
    sponsorship = result.scalar_one_or_none()
    if not sponsorship:
        raise HTTPException(status_code=404, detail=t_for(request, "work_hours.errors.sponsorship_not_found"))

    await update_sponsorship(
        db, sponsorship,
        member_id=member_id, area=area, description=description,
        credited_hours=float(credited_hours.replace(",", ".")),
        valid_from=date.fromisoformat(valid_from),
        valid_until=(date.fromisoformat(valid_until) if valid_until.strip() else None),
    )

    await db.commit()

    year = sponsorship.valid_from.year
    return RedirectResponse(f"/work-hours/sponsorships?year={year}", status_code=302)


@router.post("/sponsorships/{sponsorship_id}/delete")
async def sponsorship_delete(
    sponsorship_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    await require_permission(request, db, "work_hours", "delete")
    result = await db.execute(select(Sponsorship).where(Sponsorship.id == sponsorship_id))
    sponsorship = result.scalar_one_or_none()
    if sponsorship:
        await db.delete(sponsorship)
        await db.commit()
    return RedirectResponse("/work-hours/sponsorships", status_code=302)


# ---------------------------------------------------------------------------
# Evaluation: annual standing per member/parcel
# ---------------------------------------------------------------------------

@router.get("/evaluation", response_class=HTMLResponse)
async def evaluation(
    request: Request,
    year: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
):
    user = await require_permission(request, db, "work_hours", "read")

    if not year:
        year = date.today().year

    years_result = await db.execute(
        select(WorkHoursConfiguration.year).order_by(WorkHoursConfiguration.year.desc())
    )
    available_years = [r[0] for r in years_result.all()]

    config, rows = await evaluate_year(db, year)

    return templates.TemplateResponse(
        "work_hours/evaluation.html",
        {
            "request": request,
            "user": user,
            "year": year,
            "config": config,
            "rows": rows,
            "available_years": available_years,
            "WorkHoursMode": WorkHoursMode,
        },
    )


@router.get("/evaluation/csv")
async def evaluation_export_csv(
    request: Request,
    year: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
):
    await require_permission(request, db, "work_hours", "read")

    if not year:
        year = date.today().year

    config, rows = await evaluate_year(db, year)
    if not config:
        raise HTTPException(status_code=404, detail=t_for(request, "work_hours.errors.no_configuration_for_year", year=year))

    output = io.StringIO()
    writer = csv.writer(output, delimiter=";")
    writer.writerow([
        "Parcel", "Pächter", "Pflicht (h)", "Geleistet (h)",
        "Sponsorship (h)", "Gesamt (h)", "Offen (h)",
        "Schuldbetrag (EUR)", "Befreit", "Erfüllt"
    ])

    # Same rule as the evaluation page for what counts as "exempt": ONE
    # exempt tenant is enough to exempt the whole parcel (any(), not
    # all() -- see docs/ADR/README.md). Computed once, in
    # app.services.work_hours.evaluate_parcel(), not re-derived here.
    if config.mode == WorkHoursMode.PER_PARCEL:
        for row in rows:
            session_hours = sum(t["hours"]["session_hours"] for t in row["tenant_details"])
            sponsorship_hours = sum(t["hours"]["sponsorship_hours"] for t in row["tenant_details"])
            names = [t["member"].full_name for t in row["tenant_details"]]
            writer.writerow([
                row["parcel"].plot_number,
                csv_safe("; ".join(names)),
                f"{row['required_hours']:.1f}",
                f"{session_hours:.1f}",
                f"{sponsorship_hours:.1f}",
                f"{row['total_hours']:.1f}",
                f"{row['outstanding_hours']:.1f}",
                f"{row['amount_due']:.2f}".replace(".", ","),
                "Ja" if row["exempt"] else "Nein",
                "Ja" if row["fulfilled"] else "Nein",
            ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=work_hours_{year}.csv"},
    )


# ---------------------------------------------------------------------------
# Tasks: a backlog of upcoming work, optionally scheduled to a session and
# assigned to one of that session's signed-up participants. Lets whoever
# coordinates a session match tasks to people appropriately (e.g. lighter
# tasks for someone who can't do heavy physical work) -- the app only
# stores a workload label per task; the actual matching judgment stays
# entirely with the human coordinator.
# ---------------------------------------------------------------------------

async def _load_task(db: AsyncSession, task_id: str) -> Optional[WorkTask]:
    result = await db.execute(
        select(WorkTask)
        .options(
            selectinload(WorkTask.session),
            selectinload(WorkTask.assigned_participation).selectinload(SessionParticipation.member),
        )
        .where(WorkTask.id == task_id)
    )
    return result.scalar_one_or_none()


@router.get("/tasks", response_class=HTMLResponse)
async def tasks_overview(request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_permission(request, db, "work_hours", "read")

    backlog_result = await db.execute(
        select(WorkTask)
        .where(WorkTask.session_id.is_(None))
        .order_by(WorkTask.created_at.desc())
    )
    backlog = backlog_result.scalars().all()

    scheduled_result = await db.execute(
        select(WorkTask)
        .options(
            selectinload(WorkTask.session),
            selectinload(WorkTask.assigned_participation).selectinload(SessionParticipation.member),
        )
        .where(WorkTask.session_id.is_not(None))
        .order_by(WorkTask.is_done, WorkTask.created_at.desc())
    )
    scheduled_tasks = scheduled_result.scalars().all()

    # Group scheduled tasks by session for display, most recent session first.
    by_session: dict = {}
    for task in scheduled_tasks:
        by_session.setdefault(task.session, []).append(task)
    sessions_with_tasks = sorted(by_session.items(), key=lambda pair: pair[0].date, reverse=True)

    upcoming_sessions_result = await db.execute(
        select(WorkSession).where(WorkSession.date >= date.today()).order_by(WorkSession.date)
    )
    upcoming_sessions = upcoming_sessions_result.scalars().all()

    return templates.TemplateResponse("work_hours/tasks.html", {
        "request": request, "user": user,
        "backlog": backlog,
        "sessions_with_tasks": sessions_with_tasks,
        "upcoming_sessions": upcoming_sessions,
        "TaskWorkload": TaskWorkload,
    })


@router.post("/tasks/new")
async def task_create(
    request: Request,
    title: str = Form(...),
    description: str = Form(""),
    workload: str = Form("MODERATE"),
    session_id: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    user = await require_permission(request, db, "work_hours", "write")

    await create_task(
        db, title=title, description=description, workload=workload,
        session_id=(session_id or None), created_by_id=user.id,
    )
    await db.commit()
    return RedirectResponse("/work-hours/tasks", status_code=302)


@router.post("/tasks/{task_id}/schedule")
async def task_assign_to_session(
    task_id: str,
    request: Request,
    session_id: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    """Schedules a task to a session, or sends it back to the backlog if
    session_id is empty. Clears any participant assignment when the
    session changes (an assignment to a specific person only makes sense
    for the session they actually signed up for)."""
    await require_permission(request, db, "work_hours", "write")
    task = await _load_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail=t_for(request, "work_hours.errors.task_not_found"))

    await schedule_task(db, task, session_id=session_id)
    await db.commit()
    return RedirectResponse("/work-hours/tasks", status_code=302)


@router.post("/tasks/{task_id}/assign")
async def task_participant_assign(
    task_id: str,
    request: Request,
    participation_id: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    """Assigns a task to one specific signed-up participant of its
    session, or clears the assignment if participation_id is empty."""
    await require_permission(request, db, "work_hours", "write")
    task = await _load_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail=t_for(request, "work_hours.errors.task_not_found"))

    try:
        await assign_task_to_participant(db, task, participation_id=participation_id)
    except ServiceError as e:
        raise HTTPException(status_code=e.http_status, detail=t_for(request, e.key, **e.params))

    await db.commit()
    referer = request.headers.get("referer", "/work-hours/tasks")
    return RedirectResponse(referer, status_code=302)


@router.post("/tasks/{task_id}/toggle-done")
async def task_toggle_done(
    task_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    await require_permission(request, db, "work_hours", "write")
    task = await _load_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail=t_for(request, "work_hours.errors.task_not_found"))

    await toggle_task_done(db, task)
    await db.commit()
    referer = request.headers.get("referer", "/work-hours/tasks")
    return RedirectResponse(referer, status_code=302)


@router.post("/tasks/{task_id}/delete")
async def task_delete(
    task_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    await require_permission(request, db, "work_hours", "delete")
    task = await _load_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail=t_for(request, "work_hours.errors.task_not_found"))

    await db.delete(task)
    await db.commit()
    referer = request.headers.get("referer", "/work-hours/tasks")
    return RedirectResponse(referer, status_code=302)
