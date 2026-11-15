"""Announcement summary

Revision ID: 0124_announcement_summary
Revises: 0123_announcement_image_alt
Create Date: 2026-11-15

Issue #317 (ADR 0129): an optional one-line summary per announcement,
used as the email preheader and the website excerpt. Nullable, no
backfill; channel fingerprints only include it when it's set, so
existing deliveries keep matching.
"""
from typing import Union

from alembic import op
import sqlalchemy as sa

revision: str = "0124_announcement_summary"
down_revision: Union[str, None] = "0123_announcement_image_alt"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("announcements", sa.Column("summary", sa.String(length=300), nullable=True))


def downgrade() -> None:
    op.drop_column("announcements", "summary")
