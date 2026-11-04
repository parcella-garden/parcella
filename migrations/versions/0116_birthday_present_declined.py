"""Members: declines birthday presents

Revision ID: 0116_birthday_present_declined
Revises: 0115_task_tags
Create Date: 2026-11-04

- members.birthday_present_declined (issue #269): the member doesn't
  want birthday presents; shown on the birthday list. Existing members
  get false.
"""
from typing import Union

from alembic import op
import sqlalchemy as sa

revision: str = "0116_birthday_present_declined"
down_revision: Union[str, None] = "0115_task_tags"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "members",
        sa.Column("birthday_present_declined", sa.Boolean(), server_default=sa.false(), nullable=False),
    )


def downgrade() -> None:
    op.drop_column("members", "birthday_present_declined")
