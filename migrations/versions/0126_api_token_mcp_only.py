"""API tokens: MCP-only flag

Revision ID: 0126_api_token_mcp_only
Revises: 0125_custom_calendars
Create Date: 2026-11-15

Issue #307 (ADR 0132): a token marked mcp_only works only on the MCP
endpoint (notes released for AI) and is rejected by the REST API.
Existing tokens stay ordinary tokens.
"""
from typing import Union

from alembic import op
import sqlalchemy as sa

revision: str = "0126_api_token_mcp_only"
down_revision: Union[str, None] = "0125_custom_calendars"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("api_tokens", sa.Column("mcp_only", sa.Boolean(), nullable=False, server_default="false"))


def downgrade() -> None:
    op.drop_column("api_tokens", "mcp_only")
