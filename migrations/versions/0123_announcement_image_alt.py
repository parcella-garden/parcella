"""Announcement banner alt text

Revision ID: 0123_announcement_image_alt
Revises: 0122_notes_strip_headers
Create Date: 2026-11-15

Issue #318 (ADR 0128): an alt text for the announcement's banner image,
plus the alt text as delivered per channel (compared like image_filename
so an alt-only edit marks the channel as changed). Both nullable; no
backfill -- NULL on both sides means "unchanged".
"""
from typing import Union

from alembic import op
import sqlalchemy as sa

revision: str = "0123_announcement_image_alt"
down_revision: Union[str, None] = "0122_notes_strip_headers"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("announcements", sa.Column("image_alt", sa.String(length=255), nullable=True))
    op.add_column("announcement_deliveries", sa.Column("image_alt", sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column("announcement_deliveries", "image_alt")
    op.drop_column("announcements", "image_alt")
