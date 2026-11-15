"""Custom calendars

Revision ID: 0125_custom_calendars
Revises: 0124_announcement_summary
Create Date: 2026-11-15

Issue #314 (ADR 0131): admin-defined calendars besides the built-in
ones. Their entries are calendar_events rows with calendar_id set;
NULL keeps meaning "the community calendar", so every existing event
stays exactly where it was.
"""
from typing import Union

from alembic import op
import sqlalchemy as sa

revision: str = "0125_custom_calendars"
down_revision: Union[str, None] = "0124_announcement_summary"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "custom_calendars",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("color", sa.String(length=7), nullable=False, server_default="#2e7d32"),
        sa.Column("full_access_only", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.add_column("calendar_events", sa.Column("calendar_id", sa.String(length=36), nullable=True))
    op.create_foreign_key(
        "fk_calendar_events_calendar_id", "calendar_events", "custom_calendars",
        ["calendar_id"], ["id"], ondelete="RESTRICT",
    )
    op.create_index("ix_calendar_events_calendar_id", "calendar_events", ["calendar_id"])


def downgrade() -> None:
    op.drop_index("ix_calendar_events_calendar_id", table_name="calendar_events")
    op.drop_constraint("fk_calendar_events_calendar_id", "calendar_events", type_="foreignkey")
    op.drop_column("calendar_events", "calendar_id")
    op.drop_table("custom_calendars")
