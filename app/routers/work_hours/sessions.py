"""Work sessions: create, edit, detail, attendee sheet, participants."""
from fastapi import APIRouter
from datetime import date, datetime, timezone
from pathlib import Path
from fastapi import Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.database import active_member_filter, get_db
from app.models import (
    Member,
    MemberParcel,
    ParticipationStatus,
    SessionParticipation,
    SessionType,
    TaskWorkload,
    WorkSession,
    WorkTask,
)
from app.permissions import require_permission
from app.i18n import load_current_language, t_for
from app.branding import load_branding
from app.pdf_chrome import load_org_footer_context
from app.l10n import format_number, load_current_region
from app.session_attendee_sheet import AttendeeRow, render_session_attendee_sheet_pdf
from app.services.work_hours import (
    add_participation,
    create_session,
    mark_signups_reviewed,
    new_participation_cutoff,
    notify_new_participation,
    update_participation,
    update_session,
)
from app.templating import templates
from app.routers.work_hours._common import _lang

router = APIRouter()


# ---------------------------------------------------------------------------
# Work Sessions
# ---------------------------------------------------------------------------

@router.get("/sessions/new", response_class=HTMLResponse)
async def session_new_page(request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_permission(request, db, "work_hours", "write")
    return templates.TemplateResponse(
        request, "work_hours/session_form.html",
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
    signup_deadline_days: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    user = await require_permission(request, db, "work_hours", "write")

    session = await create_session(
        db,
        title=title, description=description, type=type, date_value=date.fromisoformat(date_value),
        time_from=time_from, time_until=time_until,
        max_participants=(int(max_participants) if max_participants.strip() else None),
        hours_per_participant=(float(hours_per_participant.replace(",", ".")) if hours_per_participant.strip() else None),
        signup_deadline_days=(int(signup_deadline_days) if signup_deadline_days.strip() else None),
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
        request, "work_hours/session_form.html",
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
    signup_deadline_days: str = Form(""),
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
        signup_deadline_days=(int(signup_deadline_days) if signup_deadline_days.strip() else None),
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
        request, "work_hours/session_detail.html",
        {
            "request": request,
            "user": user,
            "session": session,
            "signup_members_json": signup_members_json,
            "ParticipationStatus": ParticipationStatus,
            "SessionType": SessionType,
            "session_tasks": session_tasks,
            "TaskWorkload": TaskWorkload,
            "new_participation_cutoff": new_participation_cutoff(),
            "epoch_datetime": datetime.min.replace(tzinfo=timezone.utc),
            "today": date.today(),
        },
    )


@router.post("/sessions/{session_id}/mark-signups-reviewed")
async def session_mark_signups_reviewed(
    session_id: str, request: Request, db: AsyncSession = Depends(get_db),
):
    """Clears the "New" badges/count for this session's current
    participants (a fresh sign-up afterward still shows as new again --
    see mark_signups_reviewed() in app/services/work_hours.py)."""
    await require_permission(request, db, "work_hours", "write")

    result = await db.execute(select(WorkSession).where(WorkSession.id == session_id))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail=t_for(request, "work_hours.errors.session_not_found"))

    await mark_signups_reviewed(db, session)
    await db.commit()
    return RedirectResponse(f"/work-hours/sessions/{session_id}", status_code=302)


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
    actor = await require_permission(request, db, "work_hours", "write")

    participation = await add_participation(
        db, session_id, member_id=member_id, status=status,
        hours_completed=(float(hours_completed.replace(",", ".")) if hours_completed.strip() else None),
        note=note,
    )
    if participation is not None:
        await db.commit()
        # Issue #217: fire only after a successful commit and only for a
        # genuinely new row -- add_participation() returns None (no-op)
        # if the member was already registered, and that must not notify.
        member = await db.get(Member, member_id)
        session = await db.get(WorkSession, session_id)
        await notify_new_participation(
            db, participation, member=member, session=session, actor=actor, lang=_lang(request),
        )
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
