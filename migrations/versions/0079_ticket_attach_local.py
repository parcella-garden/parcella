"""Local-storage fallback for ticket attachments

Revision ID: 0079_ticket_attach_local
Revises: 0078_ticket_attach
Create Date: 2026-08-14

If Nextcloud isn't configured (or its credentials can't be decrypted --
see the live incident that prompted this), incoming ticket attachments
used to be silently discarded (docs/module-tickets.md, "Incoming
attachments are stored in Nextcloud, never locally"). This adds a local
disk fallback (app/ticket_attachment_storage.py) instead. `cloud_filename`
becomes nullable (LOCAL rows won't have one) and a new nullable
`local_filename` holds the local disk filename for those. `storage_backend`
says which of the two a given row actually uses; every existing row is
backfilled to CLOUD, matching its actual (and only, until now) storage.
"""
from typing import Union

from alembic import op
import sqlalchemy as sa

revision: str = "0079_ticket_attach_local"
down_revision: Union[str, None] = "0078_ticket_attach"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # CREATE TYPE explicitly first -- op.add_column() with an inline
    # sa.Enum() only auto-creates the Postgres type as a side effect of
    # op.create_table(); standalone add_column does not (see migration
    # 0055_task_priority for the same pattern).
    op.execute("CREATE TYPE attachmentstoragebackend AS ENUM ('CLOUD', 'LOCAL')")
    op.add_column(
        "ticket_attachments",
        sa.Column(
            "storage_backend",
            sa.Enum("CLOUD", "LOCAL", name="attachmentstoragebackend", create_type=False),
            nullable=False,
            server_default="CLOUD",
        ),
    )
    op.alter_column("ticket_attachments", "cloud_filename", existing_type=sa.String(500), nullable=True)
    op.add_column("ticket_attachments", sa.Column("local_filename", sa.String(500), nullable=True))


def downgrade() -> None:
    op.drop_column("ticket_attachments", "local_filename")
    op.alter_column("ticket_attachments", "cloud_filename", existing_type=sa.String(500), nullable=False)
    op.drop_column("ticket_attachments", "storage_backend")
    op.execute("DROP TYPE IF EXISTS attachmentstoragebackend")
