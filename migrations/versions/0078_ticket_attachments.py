"""Ticket attachments (incoming email attachments, stored in Nextcloud)

Revision ID: 0078_ticket_attach
Revises: 0077_spam_review
Create Date: 2026-08-10

Adds a `ticket_attachments` table -- one row per attachment found on an
incoming ticket email. Mirrors IncomingInvoice's cloud-storage pattern
(see docs/module-finances.md): no file bytes are ever stored in
Parcella's own database/filesystem, `cloud_filename` just names a file
inside the single shared Nextcloud folder configured for ticket
attachments (ClubSetting "ticket_attachments_cloud_folder"). Cascades
on `ticket_message_id` -- an attachment can't outlive its message,
same as `ticket_messages.ticket_id` cascading on `tickets`.
"""
from typing import Union

from alembic import op
import sqlalchemy as sa

revision: str = "0078_ticket_attach"
down_revision: Union[str, None] = "0077_spam_review"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ticket_attachments",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("ticket_message_id", sa.String(36), sa.ForeignKey("ticket_messages.id", ondelete="CASCADE"), nullable=False),
        sa.Column("original_filename", sa.String(500), nullable=False),
        sa.Column("cloud_filename", sa.String(500), nullable=False),
        sa.Column("content_type", sa.String(255), nullable=True),
        sa.Column("size_bytes", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_ticket_attachments_ticket_message_id", "ticket_attachments", ["ticket_message_id"])


def downgrade() -> None:
    op.drop_index("ix_ticket_attachments_ticket_message_id", table_name="ticket_attachments")
    op.drop_table("ticket_attachments")
