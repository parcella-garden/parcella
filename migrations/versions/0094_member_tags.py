"""Member tags: free-form labels on members, filterable (issue #241)

Revision ID: 0094_member_tags
Revises: 0093_applicants
Create Date: 2026-10-17

Two new tables: `member_tags` (the labels) and `member_tag_links`
(member <-> tag). See docs/module-members-parcels.md and ADR 0093.
"""
from typing import Union

from alembic import op
import sqlalchemy as sa

revision: str = "0094_member_tags"
down_revision: Union[str, None] = "0093_applicants"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "member_tags",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "member_tag_links",
        sa.Column("member_id", sa.String(36), sa.ForeignKey("members.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("tag_id", sa.String(36), sa.ForeignKey("member_tags.id", ondelete="CASCADE"), primary_key=True),
    )
    op.create_index("ix_member_tag_links_tag_id", "member_tag_links", ["tag_id"])


def downgrade() -> None:
    op.drop_index("ix_member_tag_links_tag_id", table_name="member_tag_links")
    op.drop_table("member_tag_links")
    op.drop_table("member_tags")
