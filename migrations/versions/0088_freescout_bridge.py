"""Add FreeScout conversation bridge

Revision ID: 0088_freescout_bridge
Revises: 0087_remove_ticket_module
Create Date: 2026-09-16

Replacement for the ticket module removed in 0087: a lightweight
cross-reference to FreeScout conversations (app.models.FreescoutConversationLink)
-- NOT a mirror of FreeScout's messages/attachments, see that model's
docstring and docs/module-freescout-bridge.md -- plus a persistent
Member -> FreeScout-customer identity mapping
(members.freescout_customer_id), so repeated conversations from the same
customer resolve without re-matching by email every time.

This migration only creates the one new table and adds the one new
column -- no other schema changes, per this project's convention of
keeping each migration to a single concern (autogenerate can pick up
unrelated noise; this was written by hand).
"""
from typing import Union

from alembic import op
import sqlalchemy as sa

revision: str = "0088_freescout_bridge"
down_revision: Union[str, None] = "0087_remove_ticket_module"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("members", sa.Column("freescout_customer_id", sa.Integer(), nullable=True))
    op.create_index(
        "ix_members_freescout_customer_id", "members", ["freescout_customer_id"], unique=True,
    )

    op.create_table(
        "freescout_conversation_links",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("freescout_conversation_id", sa.Integer(), nullable=False),
        sa.Column("freescout_mailbox_id", sa.Integer(), nullable=False),
        sa.Column("subject", sa.String(255), nullable=False),
        sa.Column("customer_email", sa.String(255), nullable=False),
        sa.Column("customer_name", sa.String(255), nullable=True),
        sa.Column("freescout_status", sa.String(50), nullable=False),
        sa.Column("message_count", sa.Integer(), nullable=True),
        sa.Column("member_id", sa.String(36), sa.ForeignKey("members.id", ondelete="SET NULL"), nullable=True),
        sa.Column("parcel_id", sa.String(36), sa.ForeignKey("parcels.id", ondelete="SET NULL"), nullable=True),
        sa.Column("task_id", sa.String(36), sa.ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True),
        sa.Column("freescout_updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "last_synced_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()"),
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index(
        "ix_freescout_conversation_links_freescout_conversation_id",
        "freescout_conversation_links", ["freescout_conversation_id"], unique=True,
    )
    op.create_index(
        "ix_freescout_conversation_links_freescout_mailbox_id",
        "freescout_conversation_links", ["freescout_mailbox_id"],
    )
    op.create_index(
        "ix_freescout_conversation_links_customer_email", "freescout_conversation_links", ["customer_email"],
    )
    op.create_index(
        "ix_freescout_conversation_links_freescout_status", "freescout_conversation_links", ["freescout_status"],
    )
    op.create_index(
        "ix_freescout_conversation_links_member_id", "freescout_conversation_links", ["member_id"],
    )
    op.create_index(
        "ix_freescout_conversation_links_parcel_id", "freescout_conversation_links", ["parcel_id"],
    )
    op.create_index(
        "ix_freescout_conversation_links_task_id", "freescout_conversation_links", ["task_id"],
    )
    op.create_index(
        "ix_freescout_conversation_links_freescout_updated_at",
        "freescout_conversation_links", ["freescout_updated_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_freescout_conversation_links_freescout_updated_at", table_name="freescout_conversation_links")
    op.drop_index("ix_freescout_conversation_links_task_id", table_name="freescout_conversation_links")
    op.drop_index("ix_freescout_conversation_links_parcel_id", table_name="freescout_conversation_links")
    op.drop_index("ix_freescout_conversation_links_member_id", table_name="freescout_conversation_links")
    op.drop_index("ix_freescout_conversation_links_freescout_status", table_name="freescout_conversation_links")
    op.drop_index("ix_freescout_conversation_links_customer_email", table_name="freescout_conversation_links")
    op.drop_index("ix_freescout_conversation_links_freescout_mailbox_id", table_name="freescout_conversation_links")
    op.drop_index(
        "ix_freescout_conversation_links_freescout_conversation_id", table_name="freescout_conversation_links",
    )
    op.drop_table("freescout_conversation_links")

    op.drop_index("ix_members_freescout_customer_id", table_name="members")
    op.drop_column("members", "freescout_customer_id")
