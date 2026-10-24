"""Finances: budget plan

Revision ID: 0112_finance_budget_lines
Revises: 0111_purchase_request_comments
Create Date: 2026-10-24

- finance_budget_lines: the planned amount per category and year
  (issue #248). Actuals aren't stored, see ADR 0113.
"""
from typing import Union

from alembic import op
import sqlalchemy as sa

revision: str = "0112_finance_budget_lines"
down_revision: Union[str, None] = "0111_purchase_request_comments"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "finance_budget_lines",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column(
            "category_id", sa.String(36), sa.ForeignKey("finance_categories.id", ondelete="CASCADE"), nullable=False,
        ),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("year", "category_id", name="uq_finance_budget_line_year_category"),
    )
    op.create_index("ix_finance_budget_lines_year", "finance_budget_lines", ["year"])


def downgrade() -> None:
    op.drop_index("ix_finance_budget_lines_year", table_name="finance_budget_lines")
    op.drop_table("finance_budget_lines")
