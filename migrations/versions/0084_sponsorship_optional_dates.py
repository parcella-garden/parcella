"""Sponsorship: valid_from made optional (nullable)

Revision ID: 0084_sponsorship_optional_dates
Revises: 0083_freescout_bridge
Create Date: 2026-09-07

A sponsorship area can now be advertised before anyone has committed to
it at all -- no member *and* no start date yet (issue #213). Same shape
as 0004_patenschaft_optional, which made member_id optional for the
same reason a year earlier.
"""
from typing import Union
from alembic import op
import sqlalchemy as sa

revision: str = "0084_sponsorship_optional_dates"
down_revision: Union[str, None] = "0083_freescout_bridge"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "sponsorships", "valid_from",
        existing_type=sa.Date(),
        nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "sponsorships", "valid_from",
        existing_type=sa.Date(),
        nullable=False,
    )
