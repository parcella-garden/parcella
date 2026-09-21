"""
Task board activity report (Markdown export) -- lets a board member pull
"what happened on the task board" for a date range into a file they can
paste into an LLM to draft meeting minutes. See app/routers/tasks.py for
the route and app/templates/tasks/board.html for the export button/modal.

The task board keeps no move-history log (see docs/module-tasks.md) --
only a card's *current* list_id plus created_at/updated_at, and an
append-only comment thread. So this report can only say a card was
"touched" (created or updated) in the window, never "moved to list X on
date Y". That limitation is stated in the generated file itself (not
just in code comments), since the file is meant to be read standalone.
"""
from datetime import date, datetime, time, timedelta, timezone
from typing import List

from fastapi import Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.i18n import t_for
from app.models import Task, TaskAssignee, TaskComment, TaskList


def _period_bounds(date_from: date, date_to: date) -> tuple[datetime, datetime]:
    """Inclusive [date_from, date_to] as UTC datetime bounds, upper bound
    exclusive, for comparing against the DateTime(timezone=True) columns
    (Task.created_at/updated_at, TaskComment.created_at)."""
    start = datetime.combine(date_from, time.min, tzinfo=timezone.utc)
    end = datetime.combine(date_to + timedelta(days=1), time.min, tzinfo=timezone.utc)
    return start, end


def _md_cell(value: str) -> str:
    """Flattens a free-text value onto one line and escapes '|' so it
    can't break a Markdown table row."""
    return value.replace("\n", " ").replace("|", "\\|").strip()


def _md_table(headers: List[str], rows: List[List[str]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "|" + "|".join("---" for _ in headers) + "|",
    ]
    for row in rows:
        lines.append("| " + " | ".join(_md_cell(cell) for cell in row) + " |")
    return "\n".join(lines)


def _priority_label(request: Request, task: Task) -> str:
    if not task.priority:
        return "—"
    return t_for(request, "tasks.form.priority_" + task.priority.value.lower())


def _assignee_names(task: Task) -> str:
    names = [assignee.user.name for assignee in task.assignees]
    return ", ".join(names) if names else "—"


async def build_report_markdown(
    db: AsyncSession, request: Request, date_from: date, date_to: date,
) -> str:
    period_start, period_end = _period_bounds(date_from, date_to)

    lists_result = await db.execute(select(TaskList).order_by(TaskList.position))
    lists_by_id = {task_list.id: task_list for task_list in lists_result.scalars().all()}

    tasks_result = await db.execute(
        select(Task)
        .options(
            selectinload(Task.assignees).selectinload(TaskAssignee.user),
            selectinload(Task.created_by),
        )
        .order_by(Task.list_id, Task.position)
    )
    all_tasks = tasks_result.scalars().all()

    touched_tasks = [
        task for task in all_tasks
        if (period_start <= task.created_at < period_end)
        or (period_start <= task.updated_at < period_end)
    ]

    comments_result = await db.execute(
        select(TaskComment)
        .options(selectinload(TaskComment.created_by), selectinload(TaskComment.task))
        .where(TaskComment.created_at >= period_start, TaskComment.created_at < period_end)
        .order_by(TaskComment.created_at)
    )
    comments = comments_result.scalars().all()

    today = date.today()

    touched_table = _md_table(
        [
            t_for(request, "tasks.export.col_list"), t_for(request, "tasks.export.col_title"),
            t_for(request, "tasks.export.col_priority"), t_for(request, "tasks.export.col_tags"),
            t_for(request, "tasks.export.col_due"), t_for(request, "tasks.export.col_created"),
            t_for(request, "tasks.export.col_updated"), t_for(request, "tasks.export.col_assignees"),
            t_for(request, "tasks.export.col_created_by"),
        ],
        [
            [
                lists_by_id[task.list_id].name, task.title, _priority_label(request, task),
                ", ".join(task.tags) if task.tags else "—",
                task.due_date.isoformat() if task.due_date else "—",
                task.created_at.date().isoformat(), task.updated_at.date().isoformat(),
                _assignee_names(task), task.created_by.name if task.created_by else "—",
            ]
            for task in touched_tasks
        ],
    )

    comments_table = _md_table(
        [
            t_for(request, "tasks.export.col_date"), t_for(request, "tasks.export.col_list"),
            t_for(request, "tasks.export.col_card"), t_for(request, "tasks.export.col_author"),
            t_for(request, "tasks.export.col_comment"),
        ],
        [
            [
                comment.created_at.date().isoformat(), lists_by_id[comment.task.list_id].name,
                comment.task.title, comment.created_by.name if comment.created_by else "—",
                comment.content,
            ]
            for comment in comments
        ],
    )

    snapshot_table = _md_table(
        [
            t_for(request, "tasks.export.col_list"), t_for(request, "tasks.export.col_title"),
            t_for(request, "tasks.export.col_priority"), t_for(request, "tasks.export.col_due"),
            t_for(request, "tasks.export.col_overdue"), t_for(request, "tasks.export.col_assignees"),
        ],
        [
            [
                lists_by_id[task.list_id].name, task.title, _priority_label(request, task),
                task.due_date.isoformat() if task.due_date else "—",
                t_for(request, "tasks.export.overdue_yes") if task.due_date and task.due_date < today else "",
                _assignee_names(task),
            ]
            for task in all_tasks
        ],
    )

    club_name = getattr(request.state, "club_name", "Parcella")
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    return (
        f"# {t_for(request, 'tasks.export.report_title', club_name=club_name)}\n\n"
        f"{t_for(request, 'tasks.export.period_label', date_from=date_from.isoformat(), date_to=date_to.isoformat())}\n"
        f"{t_for(request, 'tasks.export.generated_label', generated_at=generated_at)}\n\n"
        f"> {t_for(request, 'tasks.export.caveat_note')}\n\n"
        f"## {t_for(request, 'tasks.export.section_touched')}\n\n{touched_table}\n\n"
        f"## {t_for(request, 'tasks.export.section_comments')}\n\n{comments_table}\n\n"
        f"## {t_for(request, 'tasks.export.section_snapshot')}\n\n{snapshot_table}\n"
    )
