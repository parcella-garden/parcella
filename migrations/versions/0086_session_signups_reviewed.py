"""Add work_sessions.signups_reviewed_at

Revision ID: 0086_session_signups_reviewed
Revises: 0085_session_signup_deadline
Create Date: 2026-09-13

The "new sign-up" count/badges (ADR 0079) are purely a stateless
14-day rolling window -- there was no way to say "I've seen these" and
have the badge clear before the window expires on its own, which in
practice was annoying once someone had actually reviewed a session's
participants. Optional per-session "mark reviewed" timestamp: a
participation counts as new only if it's both inside the rolling
window AND newer than this timestamp (NULL = no session has been
reviewed yet, window alone applies).
"""
from typing import Union

from alembic import op
import sqlalchemy as sa

revision: str = "0086_session_signups_reviewed"
down_revision: Union[str, None] = "0085_session_signup_deadline"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("work_sessions", sa.Column("signups_reviewed_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("work_sessions", "signups_reviewed_at")
