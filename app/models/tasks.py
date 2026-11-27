"""Task board: lists, tasks, tags, assignees, comments, external links."""

import enum
from datetime import datetime, date
from typing import Optional, List
from sqlalchemy import String, Integer, Boolean, Date, DateTime, Text, ForeignKey, Enum as SAEnum, UniqueConstraint, Column, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func, text

from app.database import Base
from app.models._common import new_uuid


# ---------------------------------------------------------------------------
# Task board: general-purpose kanban for club business (not tied to a work
# session -- see WorkTask above for that). Admin/board only, per explicit
# product decision -- this is internal club-business tracking, not
# something every member needs visibility into. Columns are user-configurable
# `TaskList` rows (issue #100) -- v1 had a fixed TODO/IN_PROGRESS/DONE enum
# (see ADR 0034), superseded by ADR 0043 once configurable columns were
# actually requested.
# ---------------------------------------------------------------------------

class TaskPriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class TaskList(Base):
    """
    A kanban column. `position` orders columns on the board (0-based, no
    gaps), same scheme as `Task.position` below. `name` is free text, like
    `InventoryCategory.name` -- not translated per viewer once an admin can
    rename/add columns (see docs/module-tasks.md).
    """
    __tablename__ = "task_lists"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    position: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    # Issue #257: a card moved into a "done list" gets Task.completed_at
    # set (and cleared again when moved out) -- see app/task_board.py's
    # apply_done_state() and docs/ADR/0115. List names are free text, so
    # this flag is the only reliable way to know which list means "done".
    is_done_list: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    tasks: Mapped[List["Task"]] = relationship(
        "Task", back_populates="list", order_by="Task.position"
    )

    def __repr__(self) -> str:
        return f"<TaskList {self.name!r}>"


class Task(Base):
    """
    A single kanban card. `position` orders cards within their list
    (0-based, no gaps) and is fully rewritten for the affected list(s)
    on every create/move/delete -- simple and correct at the card counts
    a club's task board will ever realistically have, avoids the
    fractional-position bookkeeping a high-write-volume board would need.

    A card can have any number of assignees (issue #109) via the
    `TaskAssignee` join table below -- replaced the original single
    `assigned_to_id` FK, see ADR 0046.
    """
    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    list_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("task_lists.id"), nullable=False, index=True
    )
    position: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    due_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    priority: Mapped[Optional[TaskPriority]] = mapped_column(SAEnum(TaskPriority), nullable=True)
    # Issue #259: predefined, coloured tags only (TaskTag) -- replaced the
    # free-text ARRAY(String) column from issue #107, see docs/ADR/0116.
    # Not lazy-loadable under asyncio: selectinload(Task.tags) wherever
    # it's read. passive_deletes: the link rows go by ON DELETE CASCADE,
    # so deleting a card never has to load its tags first.
    tags: Mapped[List["TaskTag"]] = relationship(
        "TaskTag", secondary="task_tag_links", back_populates="tasks", order_by="TaskTag.name",
        passive_deletes=True,
    )
    # Issue #257: set = done. Done cards never count as overdue. Set by a
    # move into a done list or by the "Done" checkbox on any list.
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    created_by_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    list: Mapped["TaskList"] = relationship("TaskList", back_populates="tasks", foreign_keys=[list_id])
    assignees: Mapped[List["TaskAssignee"]] = relationship(
        "TaskAssignee", back_populates="task", cascade="all, delete-orphan"
    )
    created_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[created_by_id])
    comments: Mapped[List["TaskComment"]] = relationship(
        "TaskComment", back_populates="task", order_by="TaskComment.created_at",
        cascade="all, delete-orphan",
    )
    external_link: Mapped[Optional["ExternalTaskLink"]] = relationship(
        "ExternalTaskLink", back_populates="task", uselist=False, cascade="all, delete-orphan",
    )

    @property
    def assigned_to_ids(self) -> List[str]:
        return [assignee.user_id for assignee in self.assignees]

    def __repr__(self) -> str:
        return f"<Task {self.title!r} (list={self.list_id})>"


# Issue #259: the fixed palette a TaskTag's colour comes from. A plain
# string column validated against this list, not a Postgres enum, so a
# colour can be added later without an ALTER TYPE migration. Each key
# has a .task-tag-<key> CSS class in app/templates/tasks/.
TASK_TAG_COLORS = ("grey", "red", "orange", "yellow", "green", "teal", "blue", "purple")
TASK_TAG_DEFAULT_COLOR = "grey"


class TaskTag(Base):
    """
    A predefined task board tag (issue #259): cards can only carry tags
    from this list, and only admin/board -- the board's own audience --
    manage it (/tasks/tags). Replaced the free-text per-card tag array
    of issue #107; see docs/ADR/0116. Removing a tag from a card deletes
    the link row, deleting the tag removes it from every card -- a label
    isn't club history, same reasoning as MemberTag (ADR 0005 doesn't
    apply).
    """
    __tablename__ = "task_tags"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    color: Mapped[str] = mapped_column(
        String(20), nullable=False, default=TASK_TAG_DEFAULT_COLOR, server_default=TASK_TAG_DEFAULT_COLOR,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    tasks: Mapped[List["Task"]] = relationship(
        "Task", secondary="task_tag_links", back_populates="tags", passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"<TaskTag {self.name}>"


task_tag_links = Table(
    "task_tag_links",
    Base.metadata,
    Column("task_id", String(36), ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", String(36), ForeignKey("task_tags.id", ondelete="CASCADE"), primary_key=True, index=True),
)


class TaskAssignee(Base):
    """A user assigned to a kanban task (m:n -- issue #109 replaced the
    original single `assigned_to_id` FK on Task). Mirrors GroupMembership's
    shape."""
    __tablename__ = "task_assignees"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    task_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    task: Mapped["Task"] = relationship("Task", back_populates="assignees")
    user: Mapped["User"] = relationship("User")

    __table_args__ = (
        UniqueConstraint("task_id", "user_id", name="uq_task_assignee"),
    )


class TaskComment(Base):
    """
    A single comment on a task board card (issue #108). Append-only --
    add/delete only, no edit, same shape as TicketMessage but without the
    email/direction/HTML-sanitization complexity that doesn't apply here.
    """
    __tablename__ = "task_comments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    task_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_by_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    task: Mapped["Task"] = relationship("Task", back_populates="comments")
    created_by: Mapped[Optional["User"]] = relationship("User")

    def __repr__(self) -> str:
        return f"<TaskComment task={self.task_id}>"


class ExternalTaskLink(Base):
    """
    Cross-reference from a Task to a card in an external task source
    (Nextcloud Deck today -- see app/task_sync.py's TaskSyncProvider
    interface and docs/ADR/0086). One row per synced Task, one-to-one
    (ON DELETE CASCADE -- deleting the Task also drops its link, the
    reverse of every other FK in this app, since the link has no
    meaning without the Task it points at).

    Presence of this row is what makes a card "synced": the task board
    (app/templates/tasks/board.html) shows a badge and locks the fields
    the external source owns (title/description/due_date/list_id, see
    app/deck_sync.py) whenever a Task has one. Removing the row --
    whether via the admin "Adopt into Parcella" action
    (POST /tasks/{id}/adopt) or automatically when the card disappears
    from Deck (app/deck_sync.py's reconciliation pass) -- turns the Task
    into a normal, fully-independent, fully-editable one from then on;
    the Task row itself is never touched by either path.
    """
    __tablename__ = "external_task_links"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    task_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, unique=True, index=True
    )

    # "deck" is the only source today -- kept as a column (not hardcoded
    # into the table name) so a second provider never needs a schema
    # change, only a new value here.
    source: Mapped[str] = mapped_column(String(50), nullable=False)
    external_board_id: Mapped[str] = mapped_column(String(100), nullable=False)
    external_stack_id: Mapped[str] = mapped_column(String(100), nullable=False)
    external_card_id: Mapped[str] = mapped_column(String(100), nullable=False)

    # The external source's own last-modified timestamp for this card --
    # the incremental-sync high-water-mark (app/deck_sync.py skips
    # re-writing a card whose external_updated_at hasn't advanced).
    # Deliberately NOT this row's own updated_at: that would conflate
    # "Deck changed this card" with "Parcella last polled it".
    external_updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_synced_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    task: Mapped["Task"] = relationship("Task", back_populates="external_link")

    __table_args__ = (
        UniqueConstraint("source", "external_card_id", name="uq_external_task_link_source_card"),
    )

    def __repr__(self) -> str:
        return f"<ExternalTaskLink {self.source}:{self.external_card_id} task={self.task_id}>"
