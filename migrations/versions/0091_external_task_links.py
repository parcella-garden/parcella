"""Add external task source links (Nextcloud Deck sync)

Revision ID: 0091_external_task_links
Revises: 0090_meter_number_not_unique
Create Date: 2026-09-22

One new table, app.models.ExternalTaskLink: a cross-reference from a
Task to a card in an external task source (Nextcloud Deck is the only
one today, see app/task_sync.py). ON DELETE CASCADE from tasks.id --
the reverse of most FKs in this app, since a link row has no meaning
without the Task it points at. No other schema changes.
"""
from typing import Union

from alembic import op
import sqlalchemy as sa

revision: str = "0091_external_task_links"
down_revision: Union[str, None] = "0090_meter_number_not_unique"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "external_task_links",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("task_id", sa.String(36), sa.ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source", sa.String(50), nullable=False),
        sa.Column("external_board_id", sa.String(100), nullable=False),
        sa.Column("external_stack_id", sa.String(100), nullable=False),
        sa.Column("external_card_id", sa.String(100), nullable=False),
        sa.Column("external_updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "last_synced_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()"),
        ),
    )
    op.create_index(
        "ix_external_task_links_task_id", "external_task_links", ["task_id"], unique=True,
    )
    op.create_unique_constraint(
        "uq_external_task_link_source_card", "external_task_links", ["source", "external_card_id"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_external_task_link_source_card", "external_task_links", type_="unique")
    op.drop_index("ix_external_task_links_task_id", table_name="external_task_links")
    op.drop_table("external_task_links")
