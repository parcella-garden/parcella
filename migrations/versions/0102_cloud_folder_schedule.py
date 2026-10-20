"""Parcel cloud folders: scheduled switch dates

Revision ID: 0102_cloud_folder_schedule
Revises: 0101_user_session_version
Create Date: 2026-10-21

parcel_cloud_folders.active_until (the active folder retires on that
day) and active_from (a not-yet-active folder takes over on that day)
-- a parcel handed over on a future date switches folders on the
handover date itself, not when the handover is recorded (ADR 0102).
Both NULL for every existing row: nothing scheduled.
"""
from typing import Union

from alembic import op
import sqlalchemy as sa

revision: str = "0102_cloud_folder_schedule"
down_revision: Union[str, None] = "0101_user_session_version"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("parcel_cloud_folders", sa.Column("active_from", sa.Date(), nullable=True))
    op.add_column("parcel_cloud_folders", sa.Column("active_until", sa.Date(), nullable=True))


def downgrade() -> None:
    op.drop_column("parcel_cloud_folders", "active_until")
    op.drop_column("parcel_cloud_folders", "active_from")
