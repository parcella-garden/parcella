"""Task board: predefined, coloured tags

Revision ID: 0115_task_tags
Revises: 0114_task_done_list
Create Date: 2026-10-27

Issue #259: cards may only carry tags from a list that admin/board
manage, each with a colour from a fixed palette -- see docs/ADR/0116.
Replaces the free-text `tasks.tags` text array (migration 0056).

Existing tags are kept: every distinct tag already on a card becomes a
`task_tags` row in the default colour (grey) and is linked to its cards.
Spellings that differ only in case or surrounding spaces ("Garten",
"garten ") become one tag; the alphabetically first spelling wins.
Names longer than the new 100-character limit are cut.

The downgrade writes the tag names back into a text array and drops the
new tables; colours are lost.
"""
from typing import Union

import sqlalchemy as sa
from alembic import op

revision: str = "0115_task_tags"
down_revision: Union[str, None] = "0114_task_done_list"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "task_tags",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("color", sa.String(20), nullable=False, server_default="grey"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "task_tag_links",
        sa.Column("task_id", sa.String(36), sa.ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("tag_id", sa.String(36), sa.ForeignKey("task_tags.id", ondelete="CASCADE"), primary_key=True),
    )
    op.create_index("ix_task_tag_links_tag_id", "task_tag_links", ["tag_id"])

    op.execute("""
        INSERT INTO task_tags (id, name)
        SELECT gen_random_uuid()::text, min(name)
        FROM (
            SELECT left(trim(raw), 100) AS name
            FROM tasks, unnest(tasks.tags) AS raw
        ) existing
        WHERE name <> ''
        GROUP BY lower(name)
    """)
    op.execute("""
        INSERT INTO task_tag_links (task_id, tag_id)
        SELECT DISTINCT tasks.id, task_tags.id
        FROM tasks, unnest(tasks.tags) AS raw
        JOIN task_tags ON lower(task_tags.name) = lower(left(trim(raw), 100))
    """)

    op.drop_column("tasks", "tags")


def downgrade() -> None:
    op.add_column(
        "tasks",
        sa.Column("tags", sa.ARRAY(sa.String()), nullable=False, server_default="{}"),
    )
    op.execute("""
        UPDATE tasks SET tags = sub.names
        FROM (
            SELECT task_tag_links.task_id, array_agg(task_tags.name ORDER BY task_tags.name) AS names
            FROM task_tag_links JOIN task_tags ON task_tags.id = task_tag_links.tag_id
            GROUP BY task_tag_links.task_id
        ) sub
        WHERE tasks.id = sub.task_id
    """)
    op.drop_index("ix_task_tag_links_tag_id", table_name="task_tag_links")
    op.drop_table("task_tag_links")
    op.drop_table("task_tags")
