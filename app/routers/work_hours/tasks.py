"""Work tasks: create, schedule, assign, done, delete."""
from fastapi import APIRouter
from datetime import date
from fastapi import Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models import SessionParticipation, TaskWorkload, WorkSession, WorkTask
from app.permissions import require_permission
from app.i18n import t_for
from app.services.errors import ServiceError
from app.services.work_hours import (
    assign_task_to_participant,
    create_task,
    schedule_task,
    toggle_task_done,
    load_task,
)
from app.templating import templates

router = APIRouter()


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

    return templates.TemplateResponse(request, "work_hours/tasks.html", {
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
    task = await load_task(db, task_id)
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
    task = await load_task(db, task_id)
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
    task = await load_task(db, task_id)
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
    task = await load_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail=t_for(request, "work_hours.errors.task_not_found"))

    await db.delete(task)
    await db.commit()
    referer = request.headers.get("referer", "/work-hours/tasks")
    return RedirectResponse(referer, status_code=302)
