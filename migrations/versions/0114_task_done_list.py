"""Task board: done lists and Task.completed_at

Revision ID: 0114_task_done_list
Revises: 0113_applicant_status_closed
Create Date: 2026-10-26

Issue #257: a card moved into a list flagged `is_done_list` is marked
done (`completed_at`), and done cards no longer count as overdue -- see
docs/ADR/0115.

Existing boards: any list named "Done" -- ignoring case, spaces and
punctuation, so "DONE!" or " done. " count too (migration 0054 seeded
"Done", and clubs decorate it) -- becomes a done list, and the cards already in it
are marked done as of their last update -- the closest timestamp we
have for "when it got there".
"""
from typing import Union

import sqlalchemy as sa
from alembic import op

revision: str = "0114_task_done_list"
down_revision: Union[str, None] = "0113_applicant_status_closed"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "task_lists",
        sa.Column("is_done_list", sa.Boolean(), server_default="false", nullable=False),
    )
    op.add_column("tasks", sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True))

    op.execute(
        "UPDATE task_lists SET is_done_list = true "
        "WHERE regexp_replace(lower(name), '[^a-z0-9]', '', 'g') = 'done'"
    )
    op.execute(
        "UPDATE tasks SET completed_at = updated_at "
        "WHERE list_id IN (SELECT id FROM task_lists WHERE is_done_list)"
    )


def downgrade() -> None:
    op.drop_column("tasks", "completed_at")
    op.drop_column("task_lists", "is_done_list")
