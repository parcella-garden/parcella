"""Metering point active switch

Revision ID: 0129_metering_point_active
Revises: 0128_processes
Create Date: 2026-11-17

Issue #336: a metering point can be switched off for a while (no water
or power at that connection) instead of being deleted. Existing points
stay active.
"""
from typing import Union

from alembic import op
import sqlalchemy as sa

revision: str = "0129_metering_point_active"
down_revision: Union[str, None] = "0128_processes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "metering_points",
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
    )
    op.add_column("metering_points", sa.Column("inactive_since", sa.Date(), nullable=True))


def downgrade() -> None:
    op.drop_column("metering_points", "inactive_since")
    op.drop_column("metering_points", "is_active")
