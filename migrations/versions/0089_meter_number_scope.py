"""Scope meter number uniqueness per medium

Revision ID: 0089_meter_number_scope
Revises: 0088_freescout_bridge
Create Date: 2026-09-17

`meters.number` was globally unique across water AND electricity --
a leftover from when this table only held water meters (the live
constraint is still named "wasseruhren_nummer_key", from the table's
original German name, predating the ADR 0009 rename; renaming a
Postgres table does not rename its constraints/indexes). Water and
electricity meters are physically unrelated registries, and both
commonly use the same placeholder number (e.g. "ohne"/"none") for a
parcel with no distinct physical meter -- the second medium to use a
given placeholder hit this constraint and 500'd on creation.

Adds `meters.medium` (denormalized from the parent metering_points row,
set once at creation and never changed -- see app/services/metering.py),
backfills it, then replaces the global unique constraint on `number`
alone with a composite one on (medium, number).
"""
from typing import Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0089_meter_number_scope"
down_revision: Union[str, None] = "0088_freescout_bridge"
branch_labels = None
depends_on = None

_medium_enum = postgresql.ENUM("WATER", "ELECTRICITY", name="meteringmedium", create_type=False)


def upgrade() -> None:
    op.add_column("meters", sa.Column("medium", _medium_enum, nullable=True))
    op.execute(
        "UPDATE meters SET medium = mp.medium "
        "FROM metering_points mp WHERE mp.id = meters.metering_point_id"
    )
    op.alter_column("meters", "medium", nullable=False)

    op.drop_constraint("wasseruhren_nummer_key", "meters", type_="unique")
    op.create_unique_constraint("uq_meter_medium_number", "meters", ["medium", "number"])


def downgrade() -> None:
    # Only safe if no two meters of different media share a number --
    # true before this migration ran, not guaranteed afterwards.
    op.drop_constraint("uq_meter_medium_number", "meters", type_="unique")
    op.create_unique_constraint("wasseruhren_nummer_key", "meters", ["number"])
    op.drop_column("meters", "medium")
