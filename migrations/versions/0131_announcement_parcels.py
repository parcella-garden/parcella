"""Announcement to the leaseholders of picked parcels

Revision ID: 0131_announcement_parcels
Revises: 0130_meter_factor
Create Date: 2026-11-20

Issue #397: a notice to the leaseholders of parcels picked on /parcels/
stores the parcel ids (leasehold law, ADR 0142), not a member filter.
"""
from typing import Union

from alembic import op
import sqlalchemy as sa

revision: str = "0131_announcement_parcels"
down_revision: Union[str, None] = "0130_meter_factor"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("announcements", sa.Column("audience_parcel_ids", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("announcements", "audience_parcel_ids")
