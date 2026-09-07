"""Sponsorship: valid_from made optional (nullable)

Revision ID: 0084_sponsorship_optional_dates
Revises: 0082_household_members
Create Date: 2026-09-07

A sponsorship area can now be advertised before anyone has committed to
it at all -- no member *and* no start date yet (issue #213). Same shape
as 0004_patenschaft_optional, which made member_id optional for the
same reason a year earlier.

Chains onto 0082_household_members (the last *committed* migration at
the time this was written), not the local 0083_freescout_bridge file
that happened to sit on top of it in this working tree -- that file was
still-uncommitted, unrelated WIP, and chaining onto an uncommitted
revision breaks `alembic upgrade head` for anyone (including CI) who
doesn't have it, with a `KeyError` on the missing down_revision.
"""
from typing import Union
from alembic import op
import sqlalchemy as sa

revision: str = "0084_sponsorship_optional_dates"
down_revision: Union[str, None] = "0082_household_members"
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
