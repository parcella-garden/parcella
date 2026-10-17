"""Announcements to filtered members, by email and letter (issue #242)

Revision ID: 0096_announcement_audience
Revises: 0095_hours_transfers
Create Date: 2026-10-17

- announcements.audience_filter (JSON, NULL = classic announcement to
  all members) and announcements.letters_for_all.
- LETTER value for the announcementchannel enum -- the uppercase member
  name, like every enum label here (see CLAUDE.md), and outside a
  transaction since ALTER TYPE ... ADD VALUE can't run inside one (same
  pattern as 0030).

See docs/module-announcements.md and ADR 0095.
"""
from typing import Union

from alembic import op
import sqlalchemy as sa

revision: str = "0096_announcement_audience"
down_revision: Union[str, None] = "0095_hours_transfers"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("announcements", sa.Column("audience_filter", sa.JSON(), nullable=True))
    op.add_column(
        "announcements",
        sa.Column("letters_for_all", sa.Boolean(), server_default=sa.false(), nullable=False),
    )
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE announcementchannel ADD VALUE IF NOT EXISTS 'LETTER'")


def downgrade() -> None:
    # The LETTER enum value stays (Postgres has no ALTER TYPE ... DROP
    # VALUE, see 0030); its delivery rows are removed so nothing uses it.
    op.execute("DELETE FROM announcement_deliveries WHERE channel = 'LETTER'")
    op.drop_column("announcements", "letters_for_all")
    op.drop_column("announcements", "audience_filter")
