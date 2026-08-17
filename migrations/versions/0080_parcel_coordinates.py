"""Add parcels.latitude / parcels.longitude

Revision ID: 0080_parcel_coords
Revises: 0079_ticket_attach_local
Create Date: 2026-08-18

Optional GPS coordinates per parcel, filled in by hand. Numeric(9,6):
3 integer digits + 6 decimals covers longitude's full -180..180 range
at ~11cm precision. Both nullable -- most existing parcels won't have
this until someone fills it in.
"""
from typing import Union

from alembic import op
import sqlalchemy as sa

revision: str = "0080_parcel_coords"
down_revision: Union[str, None] = "0079_ticket_attach_local"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("parcels", sa.Column("latitude", sa.Numeric(9, 6), nullable=True))
    op.add_column("parcels", sa.Column("longitude", sa.Numeric(9, 6), nullable=True))


def downgrade() -> None:
    op.drop_column("parcels", "longitude")
    op.drop_column("parcels", "latitude")
