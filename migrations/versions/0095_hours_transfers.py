"""Work hours: members give surplus hours to other members (issue #243)

Revision ID: 0095_hours_transfers
Revises: 0094_member_tags
Create Date: 2026-10-17

New table `hours_transfers`. See docs/module-work-hours.md and ADR 0094.
"""
from typing import Union

from alembic import op
import sqlalchemy as sa

revision: str = "0095_hours_transfers"
down_revision: Union[str, None] = "0094_member_tags"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "hours_transfers",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("giver_member_id", sa.String(36), sa.ForeignKey("members.id", ondelete="CASCADE"), nullable=False),
        sa.Column("receiver_member_id", sa.String(36), sa.ForeignKey("members.id", ondelete="CASCADE"), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("hours", sa.Numeric(5, 1), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_by_id", sa.String(36), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("hours > 0", name="ck_hours_transfers_positive"),
        sa.CheckConstraint("giver_member_id <> receiver_member_id", name="ck_hours_transfers_not_self"),
    )
    op.create_index("ix_hours_transfers_giver_member_id", "hours_transfers", ["giver_member_id"])
    op.create_index("ix_hours_transfers_receiver_member_id", "hours_transfers", ["receiver_member_id"])
    op.create_index("ix_hours_transfers_year", "hours_transfers", ["year"])


def downgrade() -> None:
    op.drop_index("ix_hours_transfers_year", table_name="hours_transfers")
    op.drop_index("ix_hours_transfers_receiver_member_id", table_name="hours_transfers")
    op.drop_index("ix_hours_transfers_giver_member_id", table_name="hours_transfers")
    op.drop_table("hours_transfers")
