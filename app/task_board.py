"""
Card- and list-ordering logic for the task board module (see app/models.py
for the Task/TaskList models and the reasoning behind the position field).

Shared between the web router (app/routers/tasks.py) and the REST API
(app/routers/api_tasks.py) so both move cards/lists with identical
semantics.
"""
from datetime import date
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ChangeHistory, Task, TaskAssignee, TaskList, TaskPriority


async def next_position(db: AsyncSession, list_id: str) -> int:
    """Position for a brand-new card: appended to the end of its list."""
    result = await db.execute(select(Task).where(Task.list_id == list_id))
    return len(result.scalars().all())


async def create_task(
    db: AsyncSession,
    *,
    title: str,
    description: Optional[str],
    list_id: str,
    due_date: Optional[date],
    priority: Optional[TaskPriority],
    tags: List[str],
    assigned_to_ids: List[str],
    created_by_id: Optional[str] = None,
) -> Task:
    """
    Builds a card at the end of `list_id` (via `next_position`), flushes,
    adds a `TaskAssignee` row per assignee, and flushes again. Caller
    commits. Shared by the web (app/routers/tasks.py) and REST
    (app/routers/api_tasks.py) create handlers, and by the FreeScout
    bridge's "Create task" action (app/routers/freescout.py), so all
    three build a card the same way instead of each duplicating this
    construction.
    """
    task = Task(
        title=title,
        description=description,
        due_date=due_date,
        priority=priority,
        tags=list(tags),
        list_id=list_id,
        position=await next_position(db, list_id),
        created_by_id=created_by_id,
    )
    db.add(task)
    await db.flush()
    for user_id in assigned_to_ids:
        db.add(TaskAssignee(task_id=task.id, user_id=user_id))
    await db.flush()
    return task


async def move_task(
    db: AsyncSession, task: Task, new_list_id: str, new_position: int,
    changed_by_id: Optional[str] = None,
) -> None:
    """
    Moves a card to `new_list_id` at `new_position` (0-based index within
    that list), and fully renumbers the affected list(s) so `position`
    stays a gapless 0..n-1 sequence.

    Works for both cross-list moves and pure reordering within the same
    list: the target list's cards (excluding this one) are fetched, the
    card is reinserted at the clamped target index, and the whole list is
    renumbered in one pass.

    This is the single funnel every list change goes through (web
    drag-and-drop, the edit form's list dropdown, and the API's move
    endpoint), so it's also where a `list_id` ChangeHistory row is
    written when the card actually changes list (not for a same-list
    reorder) -- see docs/ADR/0085 for why this reuses the generic
    ChangeHistory/ChangeTracker mechanism instead of a bespoke table.
    """
    old_list_id = task.list_id

    if old_list_id != new_list_id:
        result = await db.execute(
            select(Task).where(Task.list_id == old_list_id, Task.id != task.id).order_by(Task.position)
        )
        for index, other in enumerate(result.scalars().all()):
            other.position = index

    result = await db.execute(
        select(Task).where(Task.list_id == new_list_id, Task.id != task.id).order_by(Task.position)
    )
    column = result.scalars().all()
    clamped = max(0, min(new_position, len(column)))
    column.insert(clamped, task)

    for index, card in enumerate(column):
        card.position = index
        card.list_id = new_list_id

    if old_list_id != new_list_id:
        db.add(ChangeHistory(
            entity_type="Task", entity_id=task.id, field_name="list_id",
            old_value=old_list_id, new_value=new_list_id, changed_by_id=changed_by_id,
        ))

    await db.commit()


async def close_gap_after_delete(db: AsyncSession, list_id: str, deleted_position: int) -> None:
    """Renumbers a list after a card is removed from it, so `position`
    stays gapless."""
    result = await db.execute(
        select(Task).where(Task.list_id == list_id, Task.position > deleted_position).order_by(Task.position)
    )
    for card in result.scalars().all():
        card.position -= 1
    await db.commit()


async def next_list_position(db: AsyncSession) -> int:
    """Position for a brand-new list: appended to the end of the board."""
    result = await db.execute(select(TaskList))
    return len(result.scalars().all())


async def move_list(db: AsyncSession, task_list: TaskList, new_position: int) -> None:
    """Moves `task_list` to `new_position` among all lists, renumbering
    the whole board in one pass (same reinsert-and-renumber shape as
    `move_task`, minus the cross-column case -- there's only one board)."""
    result = await db.execute(
        select(TaskList).where(TaskList.id != task_list.id).order_by(TaskList.position)
    )
    lists = result.scalars().all()
    clamped = max(0, min(new_position, len(lists)))
    lists.insert(clamped, task_list)

    for index, entry in enumerate(lists):
        entry.position = index

    await db.commit()


async def delete_list(db: AsyncSession, task_list: TaskList, move_to_list_id: Optional[str]) -> None:
    """
    Deletes `task_list`, reassigning its cards to `move_to_list_id` first
    if it has any. Raises `ValueError` with one of the short codes below
    (caught by the routers, which turn each into a localized 400 --
    see app/routers/tasks.py's `_LIST_DELETE_ERROR_KEYS`) if:

    - "last_list": this is the only remaining list -- a board must
      always have at least one column, or
    - "missing_target"/"target_not_found": the list has cards but
      `move_to_list_id` doesn't identify a *different*, existing list
      to move them to.
    """
    result = await db.execute(select(TaskList).order_by(TaskList.position))
    all_lists = result.scalars().all()
    if len(all_lists) <= 1:
        raise ValueError("last_list")

    result = await db.execute(
        select(Task).where(Task.list_id == task_list.id).order_by(Task.position)
    )
    cards = result.scalars().all()

    if cards:
        if not move_to_list_id or move_to_list_id == task_list.id:
            raise ValueError("missing_target")
        target = await db.get(TaskList, move_to_list_id)
        if target is None:
            raise ValueError("target_not_found")

        result = await db.execute(
            select(Task).where(Task.list_id == target.id).order_by(Task.position)
        )
        target_cards = result.scalars().all()
        for index, card in enumerate(target_cards + cards):
            card.position = index
            card.list_id = target.id

        # Flush the reassignment before deleting the list: otherwise
        # SQLAlchemy's unit-of-work sees `task_list` still has (or might
        # still have) associated `Task` rows via the `TaskList.tasks`
        # relationship and nulls their `list_id` FK to disassociate them
        # on parent-delete (its default one-to-many behavior, short of
        # cascade="delete") -- which violates the NOT NULL constraint,
        # even though we already reassigned those exact rows above.
        await db.flush()

    await db.delete(task_list)
    await db.flush()

    remaining = [entry for entry in all_lists if entry.id != task_list.id]
    for index, entry in enumerate(remaining):
        entry.position = index

    await db.commit()
