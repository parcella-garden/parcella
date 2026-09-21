"""
Task board router (web UI): a general-purpose kanban board for club
business that isn't tied to a work session (see app/models.py for the
distinction from WorkTask). Admin/board only for both viewing and
editing, per explicit product decision. Columns are user-configurable
`TaskList` rows (issue #100, see ADR 0043) -- both cards and lists are
managed here.
"""
from datetime import date, timedelta
from typing import Optional
from urllib.parse import quote as urlquote

from babel.dates import get_month_names
from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import ChangeHistory, Task, TaskAssignee, TaskComment, TaskList, TaskPriority, User
from app.auth import require_admin
from app.change_tracker import ChangeTracker
from app.i18n import t_for, DEFAULT_LANGUAGE
from app.module_flags import require_module
from app.task_board import (
    next_position, move_task, close_gap_after_delete,
    next_list_position, move_list, delete_list, create_task,
)
from app.task_report import build_report_markdown

EXPORT_DEFAULT_WINDOW_DAYS = 30
# Scalar fields tracked in the change-history table (app/models.py's
# ChangeHistory, see docs/ADR/0085) -- list_id is tracked separately,
# directly inside app/task_board.py's move_task(), since that's the
# single funnel every list change (web + API, drag-and-drop + form)
# goes through. assigned_to_ids is deliberately excluded -- see ADR 0085.
TASK_TRACKED_FIELDS = ["title", "description", "due_date", "priority", "tags"]

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    dependencies=[Depends(require_module("tasks"))],
)
from app.templating import templates

# Maps task_board.delete_list()'s short ValueError codes to translation keys.
_LIST_DELETE_ERROR_KEYS = {
    "last_list": "tasks.errors.delete_list_last_list",
    "missing_target": "tasks.errors.delete_list_missing_target",
    "target_not_found": "tasks.errors.delete_list_target_not_found",
}


async def _get_task_or_404(db: AsyncSession, task_id: str, request: Request) -> Task:
    result = await db.execute(
        select(Task)
        .options(
            selectinload(Task.assignees),
            selectinload(Task.comments).selectinload(TaskComment.created_by),
            selectinload(Task.external_link),
        )
        .where(Task.id == task_id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail=t_for(request, "tasks.errors.task_not_found"))
    return task


async def _get_comment_or_404(db: AsyncSession, task_id: str, comment_id: str, request: Request) -> TaskComment:
    result = await db.execute(
        select(TaskComment).where(TaskComment.id == comment_id, TaskComment.task_id == task_id)
    )
    comment = result.scalar_one_or_none()
    if not comment:
        raise HTTPException(status_code=404, detail=t_for(request, "tasks.errors.comment_not_found"))
    return comment


async def _get_list_or_404(db: AsyncSession, list_id: str, request: Request) -> TaskList:
    result = await db.execute(select(TaskList).where(TaskList.id == list_id))
    task_list = result.scalar_one_or_none()
    if not task_list:
        raise HTTPException(status_code=404, detail=t_for(request, "tasks.errors.list_not_found"))
    return task_list


async def _all_lists(db: AsyncSession):
    result = await db.execute(select(TaskList).order_by(TaskList.position))
    return result.scalars().all()


async def _active_users(db: AsyncSession):
    result = await db.execute(select(User).where(User.is_active == True).order_by(User.name))
    return result.scalars().all()


async def _change_history(db: AsyncSession, task_id: str):
    result = await db.execute(
        select(ChangeHistory)
        .options(selectinload(ChangeHistory.changed_by))
        .where(ChangeHistory.entity_type == "Task", ChangeHistory.entity_id == task_id)
        .order_by(ChangeHistory.changed_at.desc())
    )
    return result.scalars().all()


def _parse_tags(raw: str) -> list[str]:
    """Comma-separated free text -> a deduped, order-preserving tag list."""
    seen: dict[str, None] = {}
    for part in raw.split(","):
        tag = part.strip()
        if tag:
            seen.setdefault(tag, None)
    return list(seen)


async def _render_board(
    request: Request, db: AsyncSession, *,
    open_task: Optional[Task] = None, is_new: bool = False,
):
    """Shared render path for the board itself and for "opening" a card
    (create or edit): both a plain `/tasks/` view and `/tasks/new` /
    `/tasks/{id}/edit` render this same template -- the latter two just
    also render the #taskModal pre-opened on top of it. This gives every
    task a real, unique, bookmarkable/refreshable URL while presenting
    as a modal rather than a separate page -- see docs/ADR/0084."""
    user = await require_admin(request, db)

    result = await db.execute(
        select(TaskList)
        .options(
            selectinload(TaskList.tasks).selectinload(Task.assignees).selectinload(TaskAssignee.user),
            selectinload(TaskList.tasks).selectinload(Task.comments),
            selectinload(TaskList.tasks).selectinload(Task.external_link),
        )
        .order_by(TaskList.position)
    )
    lists = result.scalars().all()

    # Search/filter (issue #119): filtering happens client-side (see
    # board.html) over data attributes rendered on each card, so drag-
    # and-drop keeps working without a round trip -- these two option
    # lists just populate the tag/assignee dropdowns with what's
    # actually on the board right now, not every tag/user that's ever
    # existed.
    assignee_options: dict[str, str] = {}
    tag_options: set[str] = set()
    due_year_months: set[tuple[int, int]] = set()
    for task_list in lists:
        for task in task_list.tasks:
            for assignee in task.assignees:
                assignee_options[assignee.user_id] = assignee.user.name
            tag_options.update(task.tags)
            if task.due_date:
                due_year_months.add((task.due_date.year, task.due_date.month))

    # Due month/year filter (issue #119): a dropdown of only the
    # year/month combinations actually present among current due dates
    # ("July 2026", not a raw month/year picker), localized to the
    # viewer's language the same way the birthday calendar PDF names
    # months (app/birthday_calendar_pdf.py).
    language = getattr(request.state, "language", DEFAULT_LANGUAGE)
    month_names = get_month_names("wide", context="stand-alone", locale=language)
    due_month_options = [
        (f"{year:04d}-{month:02d}", f"{month_names[month]} {year}")
        for year, month in sorted(due_year_months)
    ]

    context = {
        "request": request, "user": user,
        "lists": lists,
        "today": date.today(),
        "list_error": request.query_params.get("list_error"),
        "assignee_options": sorted(assignee_options.items(), key=lambda kv: kv[1].lower()),
        "tag_options": sorted(tag_options, key=str.lower),
        "due_month_options": due_month_options,
        # Dashboard "Overdue Tasks" card (issue #127) links here with
        # ?overdue=1 -- pre-checks the board's own "Overdue only" filter
        # checkbox rather than being a separate one-off code path, so
        # the dashboard count and what you land on are the same filter
        # (see docs/ADR/0019's "stat query must match the list page's
        # own default filter" rule).
        "overdue_prefilter": request.query_params.get("overdue") == "1",
        "export_default_date_from": date.today() - timedelta(days=EXPORT_DEFAULT_WINDOW_DAYS),
        "open_task": open_task,
        "is_new_task_open": is_new,
    }
    if open_task or is_new:
        context["active_users"] = await _active_users(db)
        context["priorities"] = list(TaskPriority)
    if open_task:
        context["task_history"] = await _change_history(db, open_task.id)

    return templates.TemplateResponse("tasks/board.html", context)


@router.get("/", response_class=HTMLResponse)
async def board(request: Request, db: AsyncSession = Depends(get_db)):
    return await _render_board(request, db)


@router.get("/export")
async def export_report(request: Request, db: AsyncSession = Depends(get_db)):
    """Downloadable Markdown activity report for a date range -- see
    app/task_report.py. Registered before the "/{task_id}/..." routes
    below (same reasoning as "/new" and "/lists/..." above) so this
    literal path segment isn't swallowed by a {task_id} path param."""
    await require_admin(request, db)

    q = request.query_params
    today = date.today()
    date_from_str = q.get("date_from", "").strip()
    date_to_str = q.get("date_to", "").strip()
    date_from = date.fromisoformat(date_from_str) if date_from_str else today - timedelta(days=EXPORT_DEFAULT_WINDOW_DAYS)
    date_to = date.fromisoformat(date_to_str) if date_to_str else today

    markdown = await build_report_markdown(db, request, date_from, date_to)
    return Response(
        content=markdown,
        media_type="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="tasks_report_{date_from}_{date_to}.md"'},
    )


@router.get("/new", response_class=HTMLResponse)
async def task_new_page(request: Request, db: AsyncSession = Depends(get_db)):
    await require_admin(request, db)
    return await _render_board(request, db, is_new=True)


@router.post("/new")
async def task_create(
    request: Request,
    title: str = Form(...),
    description: str = Form(""),
    due_date: str = Form(""),
    priority: str = Form(""),
    tags: str = Form(""),
    assigned_to_ids: list[str] = Form([]),
    list_id: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    await require_admin(request, db)

    lists = await _all_lists(db)
    target_list_id = list_id.strip() or lists[0].id

    await create_task(
        db,
        title=title.strip(),
        description=description.strip() or None,
        due_date=date.fromisoformat(due_date) if due_date.strip() else None,
        priority=TaskPriority(priority.strip()) if priority.strip() else None,
        tags=_parse_tags(tags),
        list_id=target_list_id,
        assigned_to_ids=assigned_to_ids,
    )
    await db.commit()
    return RedirectResponse("/tasks/", status_code=302)


@router.post("/lists/new")
async def list_create(request: Request, name: str = Form(...), db: AsyncSession = Depends(get_db)):
    await require_admin(request, db)

    task_list = TaskList(name=name.strip(), position=await next_list_position(db))
    db.add(task_list)
    await db.commit()
    return RedirectResponse("/tasks/", status_code=302)


@router.post("/lists/{list_id}/move")
async def list_move(list_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    await require_admin(request, db)
    task_list = await _get_list_or_404(db, list_id, request)

    body = await request.json()
    try:
        new_position = int(body["position"])
    except (KeyError, ValueError):
        raise HTTPException(status_code=400, detail=t_for(request, "tasks.errors.invalid_move"))

    await move_list(db, task_list, new_position)
    return JSONResponse({"ok": True})


@router.post("/lists/{list_id}/edit")
async def list_rename(list_id: str, request: Request, name: str = Form(...), db: AsyncSession = Depends(get_db)):
    await require_admin(request, db)
    task_list = await _get_list_or_404(db, list_id, request)

    task_list.name = name.strip()
    await db.commit()
    return RedirectResponse("/tasks/", status_code=302)


@router.post("/lists/{list_id}/delete")
async def list_delete(
    list_id: str, request: Request,
    move_to_list_id: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    await require_admin(request, db)
    task_list = await _get_list_or_404(db, list_id, request)

    try:
        await delete_list(db, task_list, move_to_list_id.strip() or None)
    except ValueError as e:
        message = urlquote(t_for(request, _LIST_DELETE_ERROR_KEYS[str(e)]))
        return RedirectResponse(f"/tasks/?list_error={message}", status_code=303)

    return RedirectResponse("/tasks/", status_code=302)


@router.get("/{task_id}/edit", response_class=HTMLResponse)
async def task_edit_page(task_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    await require_admin(request, db)
    task = await _get_task_or_404(db, task_id, request)
    return await _render_board(request, db, open_task=task)


@router.post("/{task_id}/edit")
async def task_update(
    task_id: str,
    request: Request,
    title: str = Form(...),
    description: str = Form(""),
    due_date: str = Form(""),
    priority: str = Form(""),
    tags: str = Form(""),
    assigned_to_ids: list[str] = Form([]),
    list_id: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    user = await require_admin(request, db)
    task = await _get_task_or_404(db, task_id, request)

    tracker = ChangeTracker(task, "Task", TASK_TRACKED_FIELDS)

    task.title = title.strip()
    task.description = description.strip() or None
    task.due_date = date.fromisoformat(due_date) if due_date.strip() else None
    task.priority = TaskPriority(priority.strip()) if priority.strip() else None
    task.tags = _parse_tags(tags)
    if list_id.strip() and list_id.strip() != task.list_id:
        await move_task(
            db, task, list_id.strip(), await next_position(db, list_id.strip()),
            changed_by_id=user.id,
        )

    # Always resync assignees to what was actually submitted, same as
    # finances.py's parcel_scopes/member_scopes resync. Unlike those scope
    # tables, task_assignees has a uq_task_assignee unique constraint, so
    # the deletes must flush before re-adding -- otherwise re-selecting an
    # already-assigned user inserts before the matching delete lands and
    # trips the constraint.
    for assignee in list(task.assignees):
        await db.delete(assignee)
    await db.flush()
    for user_id in assigned_to_ids:
        db.add(TaskAssignee(task_id=task.id, user_id=user_id))

    await tracker.commit(db, user.id)
    await db.commit()
    return RedirectResponse("/tasks/", status_code=302)


@router.post("/{task_id}/move")
async def task_move(task_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_admin(request, db)
    task = await _get_task_or_404(db, task_id, request)

    body = await request.json()
    try:
        new_list_id = str(body["list_id"])
        new_position = int(body["position"])
    except (KeyError, ValueError):
        raise HTTPException(status_code=400, detail=t_for(request, "tasks.errors.invalid_move"))

    await move_task(db, task, new_list_id, new_position, changed_by_id=user.id)
    return JSONResponse({"ok": True})


@router.post("/{task_id}/delete")
async def task_delete(task_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    await require_admin(request, db)
    task = await _get_task_or_404(db, task_id, request)

    list_id, position = task.list_id, task.position
    await db.delete(task)
    await db.commit()
    await close_gap_after_delete(db, list_id, position)

    return RedirectResponse("/tasks/", status_code=302)


@router.post("/{task_id}/adopt")
async def task_adopt(task_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    """Detaches a card synced from an external task source (see
    app/deck_sync.py, docs/ADR/0086) -- deletes its ExternalTaskLink row
    only, never the Task itself. From then on it's a normal task,
    editable like any other, and untouched by future syncs (unless it
    happens to get re-linked, which nothing does automatically -- a
    detached task is not re-matched against Deck cards)."""
    await require_admin(request, db)
    task = await _get_task_or_404(db, task_id, request)

    if task.external_link is not None:
        await db.delete(task.external_link)
        await db.commit()

    return RedirectResponse(f"/tasks/{task_id}/edit", status_code=302)


@router.post("/{task_id}/comments")
async def comment_create(
    task_id: str, request: Request, content: str = Form(...), db: AsyncSession = Depends(get_db),
):
    user = await require_admin(request, db)
    task = await _get_task_or_404(db, task_id, request)

    stripped = content.strip()
    if stripped:
        comment = TaskComment(task_id=task.id, content=stripped, created_by_id=user.id)
        db.add(comment)
        await db.commit()
    return RedirectResponse(f"/tasks/{task_id}/edit", status_code=302)


@router.post("/{task_id}/comments/{comment_id}/delete")
async def comment_delete(
    task_id: str, comment_id: str, request: Request, db: AsyncSession = Depends(get_db),
):
    await require_admin(request, db)
    await _get_task_or_404(db, task_id, request)
    comment = await _get_comment_or_404(db, task_id, comment_id, request)

    await db.delete(comment)
    await db.commit()
    return RedirectResponse(f"/tasks/{task_id}/edit", status_code=302)
