"""Revert meter number uniqueness entirely (superseded 0089)

Revision ID: 0090_meter_number_not_unique
Revises: 0089_meter_number_scope
Create Date: 2026-09-17

0089 replaced a global unique constraint on meters.number with one
scoped to (medium, number), reasoning that water and electricity meter
numbers shouldn't collide with each other but should still be unique
within one medium. Wrong call, per kermie: meter number is not
something this software should enforce uniqueness on at all -- a
meter's real identity is its row id, not this free-text field (see
ADR 0082, which supersedes ADR 0081). This drops the (medium, number)
constraint and the denormalized medium column added for it, restoring
`number` to a plain, non-unique field (the pre-existing lookup index
on `number` alone -- "ix_wasseruhren_nummer", never touched by 0089 --
is untouched by this migration either).
"""
from typing import Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0090_meter_number_not_unique"
down_revision: Union[str, None] = "0089_meter_number_scope"
branch_labels = None
depends_on = None

_medium_enum = postgresql.ENUM("WATER", "ELECTRICITY", name="meteringmedium", create_type=False)


def upgrade() -> None:
    op.drop_constraint("uq_meter_medium_number", "meters", type_="unique")
    op.drop_column("meters", "medium")


def downgrade() -> None:
    op.add_column("meters", sa.Column("medium", _medium_enum, nullable=True))
    op.execute(
        "UPDATE meters SET medium = mp.medium "
        "FROM metering_points mp WHERE mp.id = meters.metering_point_id"
    )
    op.alter_column("meters", "medium", nullable=False)
    op.create_unique_constraint("uq_meter_medium_number", "meters", ["medium", "number"])
