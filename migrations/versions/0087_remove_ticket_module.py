"""Remove the built-in ticket module

Revision ID: 0087_remove_ticket_module
Revises: 0086_session_signups_reviewed
Create Date: 2026-09-16

Parcella no longer implements its own ticket/helpdesk system. FreeScout
(https://service.kgv-goldene-hoehe.de/) is now the sole, canonical
system for support conversations -- see the ADR on this decision and
docs/module-freescout-bridge.md (migration 0088, right after this one,
adds the replacement schema).

THIS IS A DELIBERATE, DESTRUCTIVE CHANGE, CONFIRMED BY THE PROJECT OWNER
-- not an oversight, and not the project's usual "historization over
deletion" default. Upgrading to this revision PERMANENTLY DELETES every
existing ticket, ticket message, and ticket-attachment row (and, for a
club that had ticket_attachments_cloud_folder configured, orphans the
files themselves in that Nextcloud folder -- this migration does not
touch external storage, and local-disk attachments under
app/private_uploads/ticket_attachments/ are likewise left in place for
manual cleanup, since a migration shouldn't do filesystem/network I/O).
BACK UP THE DATABASE BEFORE RUNNING THIS.

downgrade() recreates the tables (empty) for consistency with every
other migration in this repo's history -- it cannot, of course, restore
deleted data.
"""
from typing import Union

from alembic import op
import sqlalchemy as sa

revision: str = "0087_remove_ticket_module"
down_revision: Union[str, None] = "0086_session_signups_reviewed"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_table("ticket_attachments")
    op.drop_index("ix_ticket_messages_message_id", table_name="ticket_messages")
    op.drop_index("ix_ticket_messages_ticket_id", table_name="ticket_messages")
    op.drop_table("ticket_messages")
    op.drop_index("ix_tickets_status", table_name="tickets")
    op.drop_index("ix_tickets_assigned_to_id", table_name="tickets")
    op.drop_index("ix_tickets_member_id", table_name="tickets")
    op.drop_index("ix_tickets_sender_email", table_name="tickets")
    op.drop_index("ix_tickets_spam_reviewed_by_id", table_name="tickets")
    op.drop_table("tickets")

    ticket_status = sa.Enum(name="ticketstatus")
    ticket_status.drop(op.get_bind(), checkfirst=True)
    message_direction = sa.Enum(name="messagedirection")
    message_direction.drop(op.get_bind(), checkfirst=True)
    attachment_storage_backend = sa.Enum(name="attachmentstoragebackend")
    attachment_storage_backend.drop(op.get_bind(), checkfirst=True)


def downgrade() -> None:
    ticket_status = sa.Enum(
        "ACTIVE", "ASSIGNED", "WAITING", "POSTPONED", "CLOSED", "DELETED", name="ticketstatus",
    )
    message_direction = sa.Enum("INCOMING", "OUTGOING", "INTERNAL", name="messagedirection")
    attachment_storage_backend = sa.Enum("CLOUD", "LOCAL", name="attachmentstoragebackend")
    bind = op.get_bind()
    ticket_status.create(bind, checkfirst=True)
    message_direction.create(bind, checkfirst=True)
    attachment_storage_backend.create(bind, checkfirst=True)

    op.create_table(
        "tickets",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("subject", sa.String(255), nullable=False),
        sa.Column("status", ticket_status, nullable=False, server_default="ACTIVE"),
        sa.Column("assigned_to_id", sa.String(36), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("postponed_until", sa.Date(), nullable=True),
        sa.Column("member_id", sa.String(36), sa.ForeignKey("members.id", ondelete="SET NULL"), nullable=True),
        sa.Column("sender_email", sa.String(255), nullable=False),
        sa.Column("sender_name", sa.String(255), nullable=True),
        sa.Column("spam_suspected", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("spam_score", sa.Numeric(5, 2), nullable=True),
        sa.Column("spam_reasoning", sa.Text(), nullable=True),
        sa.Column("spam_reviewed_by_id", sa.String(36), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("spam_reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_tickets_status", "tickets", ["status"])
    op.create_index("ix_tickets_assigned_to_id", "tickets", ["assigned_to_id"])
    op.create_index("ix_tickets_member_id", "tickets", ["member_id"])
    op.create_index("ix_tickets_sender_email", "tickets", ["sender_email"])
    op.create_index("ix_tickets_spam_reviewed_by_id", "tickets", ["spam_reviewed_by_id"])

    op.create_table(
        "ticket_messages",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("ticket_id", sa.String(36), sa.ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("direction", message_direction, nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("content_html", sa.Text(), nullable=True),
        sa.Column("authored_by_id", sa.String(36), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("message_id", sa.String(255), nullable=True),
        sa.Column("in_reply_to", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_ticket_messages_ticket_id", "ticket_messages", ["ticket_id"])
    op.create_index("ix_ticket_messages_message_id", "ticket_messages", ["message_id"])

    op.create_table(
        "ticket_attachments",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("ticket_message_id", sa.String(36), sa.ForeignKey("ticket_messages.id", ondelete="CASCADE"), nullable=False),
        sa.Column("original_filename", sa.String(500), nullable=False),
        sa.Column("storage_backend", attachment_storage_backend, nullable=False, server_default="CLOUD"),
        sa.Column("cloud_filename", sa.String(500), nullable=True),
        sa.Column("local_filename", sa.String(500), nullable=True),
        sa.Column("content_type", sa.String(255), nullable=True),
        sa.Column("size_bytes", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_ticket_attachments_ticket_message_id", "ticket_attachments", ["ticket_message_id"])
