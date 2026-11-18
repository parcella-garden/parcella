"""Metering point factor

Revision ID: 0130_meter_factor
Revises: 0129_metering_point_active
Create Date: 2026-11-18

Issue #341: a metering point can carry a multiplier (e.g. x20 on a
current-transformer main meter). Existing points get 1, so every
consumption stays exactly what it was.
"""
from typing import Union

from alembic import op
import sqlalchemy as sa

revision: str = "0130_meter_factor"
down_revision: Union[str, None] = "0129_metering_point_active"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "metering_points",
        sa.Column("factor", sa.Numeric(10, 4), server_default="1", nullable=False),
    )


def downgrade() -> None:
    op.drop_column("metering_points", "factor")
