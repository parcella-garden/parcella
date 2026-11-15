"""Announcement print QR switch

Revision ID: 0127_announcement_print_qr
Revises: 0126_api_token_mcp_only
Create Date: 2026-11-15

ADR 0133: an announcement can ask for the QR code to the website post on
its printed notice even when the text fits -- for a print text that's
only a teaser. Defaults to off, so existing announcements print as
before; the PRINT fingerprint only includes it when it's on, so
existing deliveries keep matching.

Also public_link_token: the random part of the announcement's short link
(/a/<token>) that the printed QR code points to. NULL until the first
print with a website connector.
"""
from typing import Union

from alembic import op
import sqlalchemy as sa

revision: str = "0127_announcement_print_qr"
down_revision: Union[str, None] = "0126_api_token_mcp_only"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "announcements",
        sa.Column("print_qr_code", sa.Boolean(), server_default="false", nullable=False),
    )
    op.add_column("announcements", sa.Column("public_link_token", sa.String(length=43), nullable=True))
    op.create_unique_constraint(
        "uq_announcements_public_link_token", "announcements", ["public_link_token"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_announcements_public_link_token", "announcements", type_="unique")
    op.drop_column("announcements", "public_link_token")
    op.drop_column("announcements", "print_qr_code")
