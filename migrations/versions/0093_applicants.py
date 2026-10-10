"""Applicants module: people applying for a free garden plot

Revision ID: 0093_applicants
Revises: 0092_announcement_no_status
Create Date: 2026-10-11

New table `applicants` with two new enum types. Enum labels are the
uppercase member names, same as every other enum here (see CLAUDE.md).
See docs/module-applicants.md and ADR 0091.
"""
from typing import Union

from alembic import op
import sqlalchemy as sa

revision: str = "0093_applicants"
down_revision: Union[str, None] = "0092_announcement_no_status"
branch_labels = None
depends_on = None

APPLICANT_STATUS = ("NEW", "CONTACTED", "OFFERED", "ACCEPTED", "WITHDRAWN", "REJECTED")
APPLICANT_SOURCE = ("WEBSITE", "MANUAL")


def upgrade() -> None:
    op.create_table(
        "applicants",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("first_name", sa.String(100), nullable=True),
        sa.Column("last_name", sa.String(100), nullable=True),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("status", sa.Enum(*APPLICANT_STATUS, name="applicantstatus"), nullable=False),
        sa.Column("source", sa.Enum(*APPLICANT_SOURCE, name="applicantsource"), nullable=False),
        sa.Column("board_note", sa.Text(), nullable=True),
        sa.Column("consent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("applied_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("status_changed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by_id", sa.String(36), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
    )
    op.create_index("ix_applicants_email", "applicants", ["email"])
    op.create_index("ix_applicants_status", "applicants", ["status"])
    op.create_index("ix_applicants_applied_at", "applicants", ["applied_at"])


def downgrade() -> None:
    op.drop_index("ix_applicants_applied_at", table_name="applicants")
    op.drop_index("ix_applicants_status", table_name="applicants")
    op.drop_index("ix_applicants_email", table_name="applicants")
    op.drop_table("applicants")
    sa.Enum(name="applicantsource").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="applicantstatus").drop(op.get_bind(), checkfirst=True)
