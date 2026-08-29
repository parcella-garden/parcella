"""Add parcel_insurance.covers_household

Revision ID: 0081_covers_household
Revises: 0080_parcel_coords
Create Date: 2026-08-29

Issue #204: household coverage becomes an independent toggle from
has_accident_insurance, so a household can decline the flat base fee
for themselves while a named additional person stays insured.
server_default="true" keeps every existing row's billing behavior
unchanged (the whole household was always implicitly covered before).
"""
from typing import Union

from alembic import op
import sqlalchemy as sa

revision: str = "0081_covers_household"
down_revision: Union[str, None] = "0080_parcel_coords"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "parcel_insurance",
        sa.Column("covers_household", sa.Boolean(), nullable=False, server_default="true"),
    )


def downgrade() -> None:
    op.drop_column("parcel_insurance", "covers_household")
