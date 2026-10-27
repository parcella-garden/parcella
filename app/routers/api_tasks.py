"""
API router: Task board -- full CRUD plus a dedicated move endpoint for
reordering/moving cards between lists, and a parallel set of endpoints
for managing the lists (columns) themselves. Admin/board only
(require_admin_api), matching the web UI's permission level.
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import Task, TaskAssignee, TaskComment, TaskList, TaskTag, User
from app.api_auth import require_admin_api
from app.change_tracker import ChangeTracker
from app.module_flags import require_module
from app.routers.tasks import TASK_TRACKED_FIELDS
from app.task_board import (
    next_position, move_task, close_gap_after_delete,
    next_list_position, move_list, delete_list, create_task,
    set_completed, set_done_list,
    TagError, UnknownTagsError, list_task_tags, create_tag, update_tag, tags_by_names, set_task_tags,
)
from app.schemas import (
    KanbanTaskCreate, KanbanTaskUpdate, KanbanTaskMove, KanbanTaskOut,
    KanbanTaskListCreate, KanbanTaskListUpdate, KanbanTaskListMove, KanbanTaskListOut,
    KanbanTaskCommentCreate, KanbanTaskCommentOut,
    KanbanTaskTagCreate, KanbanTaskTagUpdate, KanbanTaskTagOut,
)

router = APIRouter(
    prefix="/api/v1/tasks",
    tags=["API: Task Board"],
    dependencies=[Depends(require_module("tasks"))],
)

# Maps task_board.delete_list()'s short ValueError codes to API error messages.
_LIST_DELETE_ERROR_MESSAGES = {
    "last_list": "Cannot delete the only remaining list.",
    "missing_target": "move_to_list_id is required to delete a list that still has cards.",
    "target_not_found": "move_to_list_id does not identify an existing list.",
}

# Maps task_board.TagError's short codes to API error messages (issue #259).
_TAG_ERROR_MESSAGES = {
    "name_required": "A tag needs a name.",
    "name_taken": "A tag with this name already exists.",
    "invalid_color": "Unknown tag colour.",
}


async def _tags_or_400(db: AsyncSession, names: List[str]):
    """Predefined tags only (issue #259, ADR 0116): unknown names are a
    400 listing them, never created on the fly."""
    try:
        return await tags_by_names(db, names)
    except UnknownTagsError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown tag(s): {', '.join(e.unknown)}. Create them first via POST /api/v1/tasks/tags.",
        )


async def _get_task_or_404(db: AsyncSession, task_id: str) -> Task:
    result = await db.execute(
        select(Task).options(selectinload(Task.assignees), selectinload(Task.tags)).where(Task.id == task_id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


async def _get_list_or_404(db: AsyncSession, list_id: str) -> TaskList:
    result = await db.execute(select(TaskList).where(TaskList.id == list_id))
    task_list = result.scalar_one_or_none()
    if not task_list:
        raise HTTPException(status_code=404, detail="List not found")
    return task_list


async def _get_comment_or_404(db: AsyncSession, task_id: str, comment_id: str) -> TaskComment:
    result = await db.execute(
        select(TaskComment).where(TaskComment.id == comment_id, TaskComment.task_id == task_id)
    )
    comment = result.scalar_one_or_none()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment


# ---------------------------------------------------------------------------
# Lists (columns) -- registered before the plain "/{task_id}" routes below
# so a path like "/lists" is never captured by "/{task_id}".
# ---------------------------------------------------------------------------

@router.get("/lists", response_model=List[KanbanTaskListOut], summary="List columns")
async def lists_list(db: AsyncSession = Depends(get_db), user: User = Depends(require_admin_api)):
    result = await db.execute(select(TaskList).order_by(TaskList.position))
    return result.scalars().all()


@router.post("/lists", response_model=KanbanTaskListOut, status_code=status.HTTP_201_CREATED, summary="Create a column")
async def list_create(
    data: KanbanTaskListCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin_api),
):
    task_list = TaskList(name=data.name, position=await next_list_position(db), is_done_list=data.is_done_list)
    db.add(task_list)
    await db.commit()
    await db.refresh(task_list)
    return task_list


@router.put("/lists/{list_id}", response_model=KanbanTaskListOut, summary="Update a column")
async def list_rename(
    list_id: str, data: KanbanTaskListUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin_api),
):
    task_list = await _get_list_or_404(db, list_id)
    if data.name is not None:
        task_list.name = data.name
    if data.is_done_list is not None:
        await set_done_list(db, task_list, data.is_done_list)
    await db.commit()
    await db.refresh(task_list)
    return task_list


@router.post(
    "/lists/{list_id}/move", response_model=KanbanTaskListOut, summary="Reorder a column",
    description="Moves a column to a new position among all columns, renumbering the whole board.",
)
async def list_move(
    list_id: str, data: KanbanTaskListMove,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin_api),
):
    task_list = await _get_list_or_404(db, list_id)
    await move_list(db, task_list, data.position)
    await db.refresh(task_list)
    return task_list


@router.delete(
    "/lists/{list_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a column",
    description="Deletes a column. If it still has cards, move_to_list_id must "
                "identify another column to move them to. The last remaining "
                "column on a board cannot be deleted.",
)
async def list_delete(
    list_id: str,
    move_to_list_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin_api),
):
    task_list = await _get_list_or_404(db, list_id)
    try:
        await delete_list(db, task_list, move_to_list_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=_LIST_DELETE_ERROR_MESSAGES[str(e)])


# ---------------------------------------------------------------------------
# Predefined tags (issue #259) -- also registered before "/{task_id}".
# ---------------------------------------------------------------------------

async def _get_tag_or_404(db: AsyncSession, tag_id: str) -> TaskTag:
    tag = await db.get(TaskTag, tag_id)
    if tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag


@router.get("/tags", response_model=List[KanbanTaskTagOut], summary="List tags")
async def tags_list(db: AsyncSession = Depends(get_db), user: User = Depends(require_admin_api)):
    return await list_task_tags(db)


@router.post("/tags", response_model=KanbanTaskTagOut, status_code=status.HTTP_201_CREATED, summary="Create a tag")
async def tag_create(
    data: KanbanTaskTagCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin_api),
):
    try:
        tag = await create_tag(db, data.name, data.color)
    except TagError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=_TAG_ERROR_MESSAGES[str(e)])
    await db.commit()
    return tag


@router.put("/tags/{tag_id}", response_model=KanbanTaskTagOut, summary="Rename or recolour a tag")
async def tag_update(
    tag_id: str, data: KanbanTaskTagUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin_api),
):
    tag = await _get_tag_or_404(db, tag_id)
    try:
        await update_tag(db, tag, name=data.name, color=data.color)
    except TagError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=_TAG_ERROR_MESSAGES[str(e)])
    await db.commit()
    return tag


@router.delete(
    "/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a tag",
    description="Deletes the tag and removes it from every task carrying it.",
)
async def tag_delete(
    tag_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin_api),
):
    tag = await _get_tag_or_404(db, tag_id)
    await db.delete(tag)
    await db.commit()


# ---------------------------------------------------------------------------
# Tasks (cards)
# ---------------------------------------------------------------------------

@router.get("", response_model=List[KanbanTaskOut], summary="List tasks")
async def tasks_list(
    list_id: Optional[str] = Query(None, description="Filter by column id"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin_api),
):
    query = (
        select(Task)
        .options(selectinload(Task.assignees), selectinload(Task.tags))
        .order_by(Task.list_id, Task.position)
    )
    if list_id:
        query = query.where(Task.list_id == list_id)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{task_id}", response_model=KanbanTaskOut, summary="Retrieve a single task")
async def task_get(
    task_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin_api),
):
    return await _get_task_or_404(db, task_id)


@router.post("", response_model=KanbanTaskOut, status_code=status.HTTP_201_CREATED, summary="Create a task")
async def task_create(
    data: KanbanTaskCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin_api),
):
    target_list_id = data.list_id
    if not target_list_id:
        result = await db.execute(select(TaskList).order_by(TaskList.position).limit(1))
        first_list = result.scalar_one_or_none()
        if first_list is None:
            raise HTTPException(status_code=400, detail="No lists exist on the board yet")
        target_list_id = first_list.id
    else:
        await _get_list_or_404(db, target_list_id)
    tags = await _tags_or_400(db, data.tags)

    task = await create_task(
        db,
        title=data.title,
        description=data.description,
        due_date=data.due_date,
        priority=data.priority,
        tags=tags,
        list_id=target_list_id,
        assigned_to_ids=data.assigned_to_ids,
    )
    await db.commit()
    # created_at/updated_at are server-side defaults, and assignees was
    # populated via separately-added rows -- both need a DB round-trip
    # (see CLAUDE.md's identity-map sharp edge).
    await db.refresh(task, attribute_names=["created_at", "updated_at", "assignees"])
    return task


@router.put("/{task_id}", response_model=KanbanTaskOut, summary="Update a task")
async def task_update(
    task_id: str,
    data: KanbanTaskUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin_api),
):
    task = await _get_task_or_404(db, task_id)
    tracker = ChangeTracker(task, "Task", TASK_TRACKED_FIELDS)

    fields = data.model_dump(exclude_unset=True)
    assigned_to_ids = fields.pop("assigned_to_ids", None)
    completed = fields.pop("completed", None)
    tag_names = fields.pop("tags", None)
    tags = await _tags_or_400(db, tag_names) if tag_names is not None else None
    for field, value in fields.items():
        setattr(task, field, value)
    if tags is not None:
        set_task_tags(db, task, tags, user.id)
    if completed is not None:
        set_completed(task, completed, db, user.id)

    if assigned_to_ids is not None:
        # uq_task_assignee is a unique constraint, so the deletes must
        # flush before re-adding -- otherwise re-selecting an already-
        # assigned user inserts before the matching delete lands and
        # trips the constraint.
        for assignee in list(task.assignees):
            await db.delete(assignee)
        await db.flush()
        for user_id in assigned_to_ids:
            db.add(TaskAssignee(task_id=task.id, user_id=user_id))

    await tracker.commit(db, user.id)
    await db.commit()
    await db.refresh(task, attribute_names=["updated_at", "assignees"])
    return task


@router.post(
    "/{task_id}/move", response_model=KanbanTaskOut, summary="Move a task",
    description="Moves a task to a column (list_id) and position. Renumbers "
                "the affected column(s) so `position` stays gapless.",
)
async def task_move(
    task_id: str,
    data: KanbanTaskMove,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin_api),
):
    task = await _get_task_or_404(db, task_id)
    await _get_list_or_404(db, data.list_id)
    await move_task(db, task, data.list_id, data.position, changed_by_id=user.id)
    # Only updated_at needs a DB round-trip (server-side onupdate) --
    # list_id/position are already correct in-memory, and refreshing
    # without attribute_names would expire (and require a lazy-load of)
    # the assignees relationship already loaded by _get_task_or_404.
    await db.refresh(task, attribute_names=["updated_at"])
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a task")
async def task_delete(
    task_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin_api),
):
    task = await _get_task_or_404(db, task_id)
    list_id, position = task.list_id, task.position
    await db.delete(task)
    await db.commit()
    await close_gap_after_delete(db, list_id, position)


# ---------------------------------------------------------------------------
# Comments (issue #108)
# ---------------------------------------------------------------------------

@router.get("/{task_id}/comments", response_model=List[KanbanTaskCommentOut], summary="List a task's comments")
async def comments_list(
    task_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin_api),
):
    await _get_task_or_404(db, task_id)
    result = await db.execute(
        select(TaskComment).where(TaskComment.task_id == task_id).order_by(TaskComment.created_at)
    )
    return result.scalars().all()


@router.post(
    "/{task_id}/comments", response_model=KanbanTaskCommentOut, status_code=status.HTTP_201_CREATED,
    summary="Add a comment to a task",
)
async def comment_create(
    task_id: str,
    data: KanbanTaskCommentCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin_api),
):
    await _get_task_or_404(db, task_id)
    comment = TaskComment(task_id=task_id, content=data.content, created_by_id=user.id)
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    return comment


@router.delete("/{task_id}/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a comment")
async def comment_delete(
    task_id: str,
    comment_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin_api),
):
    await _get_task_or_404(db, task_id)
    comment = await _get_comment_or_404(db, task_id, comment_id)
    await db.delete(comment)
    await db.commit()
