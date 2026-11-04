"""Email log

Revision ID: 0117_email_log
Revises: 0116_birthday_present_declined
Create Date: 2026-11-04

- email_logs (issue #270, ADR 0120): one row per outgoing email with
  date/time, recipient, subject, SMTP result (SENT/FAILED) and error.
  New enum type emaillogstatus, member names as values (CLAUDE.md).
"""
from typing import Union

from alembic import op
import sqlalchemy as sa

revision: str = "0117_email_log"
down_revision: Union[str, None] = "0116_birthday_present_declined"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "email_logs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("recipient", sa.String(320), nullable=False),
        sa.Column("subject", sa.String(500), nullable=False),
        sa.Column("status", sa.Enum("SENT", "FAILED", name="emaillogstatus"), nullable=False),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("attachment_count", sa.Integer(), server_default="0", nullable=False),
    )
    op.create_index("ix_email_logs_sent_at", "email_logs", ["sent_at"])
    op.create_index("ix_email_logs_recipient", "email_logs", ["recipient"])
    op.create_index("ix_email_logs_status", "email_logs", ["status"])


def downgrade() -> None:
    op.drop_table("email_logs")
    sa.Enum(name="emaillogstatus").drop(op.get_bind(), checkfirst=True)
