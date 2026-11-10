"""Personal API tokens

Revision ID: 0121_api_tokens
Revises: 0120_note_source_url
Create Date: 2026-11-09

Issue #306 (ADR 0126): long-lived, revocable API tokens per user, stored
only as a SHA-256 hash. Prerequisite for the MCP connector (#307).
"""
from typing import Union

from alembic import op
import sqlalchemy as sa

revision: str = "0121_api_tokens"
down_revision: Union[str, None] = "0120_note_source_url"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "api_tokens",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("token_prefix", sa.String(length=16), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("session_version", sa.Integer(), nullable=False),
        sa.Column("created_by_id", sa.String(length=36), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("token_hash", name="uq_api_tokens_token_hash"),
    )
    op.create_index("ix_api_tokens_user_id", "api_tokens", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_api_tokens_user_id", table_name="api_tokens")
    op.drop_table("api_tokens")
