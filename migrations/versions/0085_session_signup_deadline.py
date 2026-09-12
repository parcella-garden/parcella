"""Add work_sessions.signup_deadline_days

Revision ID: 0085_session_signup_deadline
Revises: 0084_sponsorship_optional_dates
Create Date: 2026-09-12

Public self-service signup (app/routers/api_public.py) had no notion
of a session's date having already passed -- a session that took place
that same morning still accepted signups that afternoon. Optional,
per-session lead-time requirement: when set, public signup closes N
days before the session's date; NULL means only the baseline "date
hasn't passed yet" rule applies. See docs/module-public-api.md.
"""
from typing import Union

from alembic import op
import sqlalchemy as sa

revision: str = "0085_session_signup_deadline"
down_revision: Union[str, None] = "0084_sponsorship_optional_dates"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("work_sessions", sa.Column("signup_deadline_days", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("work_sessions", "signup_deadline_days")
