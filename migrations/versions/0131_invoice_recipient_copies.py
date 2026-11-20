"""Invoice recipient copies

Revision ID: 0131_invoice_recipient_copies
Revises: 0130_meter_factor
Create Date: 2026-11-20

Issue #396: a parcel invoice goes to every address its invoice-address
tenants live at, one copy per address. Existing invoices keep NULL and
stay single-copy (their recipient_names/recipient_address snapshot).
"""
from typing import Union

from alembic import op
import sqlalchemy as sa

revision: str = "0131_invoice_recipient_copies"
down_revision: Union[str, None] = "0130_meter_factor"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("invoices", sa.Column("recipient_copies", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("invoices", "recipient_copies")
