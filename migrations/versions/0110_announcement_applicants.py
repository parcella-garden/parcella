"""Announcements: messages to picked applicants

Revision ID: 0110_announcement_applicants
Revises: 0109_contact_companies
Create Date: 2026-10-24

- announcements.audience_applicant_ids: the applicant ids a message to
  applicants (issue #247) goes to, NULL for every other announcement.
  See ADR 0112.
"""
from typing import Union

from alembic import op
import sqlalchemy as sa

revision: str = "0110_announcement_applicants"
down_revision: Union[str, None] = "0109_contact_companies"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("announcements", sa.Column("audience_applicant_ids", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("announcements", "audience_applicant_ids")
