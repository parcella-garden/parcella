"""Users: session version

Revision ID: 0101_user_session_version
Revises: 0100_tag_translations
Create Date: 2026-10-20

users.session_version -- baked into the session cookie (app/auth.py);
a password change bumps it, ending every older session of that account.
Existing rows start at 0, which is also what a pre-existing cookie
counts as, so nobody is logged out by the upgrade.
"""
from typing import Union

from alembic import op
import sqlalchemy as sa

revision: str = "0101_user_session_version"
down_revision: Union[str, None] = "0100_tag_translations"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("session_version", sa.Integer(), server_default="0", nullable=False))


def downgrade() -> None:
    op.drop_column("users", "session_version")
