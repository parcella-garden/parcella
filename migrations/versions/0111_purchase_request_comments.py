"""Purchase requests: comments

Revision ID: 0111_purchase_request_comments
Revises: 0110_announcement_applicants
Create Date: 2026-10-24

- purchase_request_comments: the discussion on a purchase request
  (issue #249), append-only like task_comments.
"""
from typing import Union

from alembic import op
import sqlalchemy as sa

revision: str = "0111_purchase_request_comments"
down_revision: Union[str, None] = "0110_announcement_applicants"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "purchase_request_comments",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "purchase_request_id", sa.String(36),
            sa.ForeignKey("purchase_requests.id", ondelete="CASCADE"), nullable=False,
        ),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_by_id", sa.String(36), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index(
        "ix_purchase_request_comments_purchase_request_id", "purchase_request_comments", ["purchase_request_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_purchase_request_comments_purchase_request_id", table_name="purchase_request_comments")
    op.drop_table("purchase_request_comments")
