"""Helpdesk providers: neutral conversation links, per-helpdesk customer ids

Revision ID: 0107_helpdesk_providers
Revises: 0106_cloud_storage_providers
Create Date: 2026-10-23

The support module became pluggable (ADR 0107): FreeScout, Zammad,
Znuny, osTicket, Zendesk or Freshdesk, one at a time.

- freescout_conversation_links -> helpdesk_conversation_links, with a
  `provider` column (every existing row: "freescout"), the conversation
  id as a string (`external_id`; not every helpdesk uses integers) and
  neutral column names. Unique per (provider, external_id).
- members.freescout_customer_id -> rows in the new helpdesk_customer_ids
  table (member, provider, customer id), since every helpdesk numbers
  its customers differently.
- freescout_* settings -> helpdesk_freescout_*; a configured FreeScout
  becomes the active helpdesk (`helpdesk_provider`).
"""
from typing import Union

from alembic import op
import sqlalchemy as sa

revision: str = "0107_helpdesk_providers"
down_revision: Union[str, None] = "0106_cloud_storage_providers"
branch_labels = None
depends_on = None

OLD, NEW = "freescout_conversation_links", "helpdesk_conversation_links"

SETTING_RENAMES = (
    ("freescout_base_url", "helpdesk_freescout_base_url"),
    ("freescout_api_key", "helpdesk_freescout_api_key"),
    ("freescout_mailbox_id", "helpdesk_freescout_mailbox_id"),
)

# (old index name, new index name, column(s) after the rename, unique)
INDEXES = (
    ("ix_freescout_conversation_links_customer_email", "ix_helpdesk_conversation_links_customer_email", "customer_email"),
    ("ix_freescout_conversation_links_member_id", "ix_helpdesk_conversation_links_member_id", "member_id"),
    ("ix_freescout_conversation_links_parcel_id", "ix_helpdesk_conversation_links_parcel_id", "parcel_id"),
    ("ix_freescout_conversation_links_task_id", "ix_helpdesk_conversation_links_task_id", "task_id"),
)


def upgrade() -> None:
    bind = op.get_bind()

    # -- conversation links -------------------------------------------
    op.rename_table(OLD, NEW)
    op.execute(f"ALTER TABLE {NEW} RENAME CONSTRAINT {OLD}_pkey TO {NEW}_pkey")
    for fk in ("member_id", "parcel_id", "task_id"):
        op.execute(f"ALTER TABLE {NEW} RENAME CONSTRAINT {OLD}_{fk}_fkey TO {NEW}_{fk}_fkey")
    for old_name, new_name, _column in INDEXES:
        op.execute(f"ALTER INDEX {old_name} RENAME TO {new_name}")

    op.drop_index("ix_freescout_conversation_links_freescout_conversation_id", table_name=NEW)
    op.drop_index("ix_freescout_conversation_links_freescout_mailbox_id", table_name=NEW)
    op.drop_index("ix_freescout_conversation_links_freescout_status", table_name=NEW)
    op.drop_index("ix_freescout_conversation_links_freescout_updated_at", table_name=NEW)

    op.add_column(NEW, sa.Column("provider", sa.String(30), nullable=False, server_default="freescout"))
    op.alter_column(NEW, "provider", server_default=None)
    op.alter_column(
        NEW, "freescout_conversation_id", new_column_name="external_id",
        type_=sa.String(100), postgresql_using="freescout_conversation_id::varchar",
    )
    op.alter_column(
        NEW, "freescout_mailbox_id", new_column_name="mailbox_id",
        type_=sa.String(100), nullable=True, postgresql_using="freescout_mailbox_id::varchar",
    )
    op.alter_column(NEW, "freescout_status", new_column_name="status")
    op.alter_column(NEW, "freescout_updated_at", new_column_name="external_updated_at")

    op.create_unique_constraint("uq_helpdesk_conversation_provider_external", NEW, ["provider", "external_id"])
    op.create_index("ix_helpdesk_conversation_links_provider", NEW, ["provider"])
    op.create_index("ix_helpdesk_conversation_links_external_id", NEW, ["external_id"])
    op.create_index("ix_helpdesk_conversation_links_mailbox_id", NEW, ["mailbox_id"])
    op.create_index("ix_helpdesk_conversation_links_status", NEW, ["status"])
    op.create_index("ix_helpdesk_conversation_links_external_updated_at", NEW, ["external_updated_at"])

    # -- customer ids -------------------------------------------------
    op.create_table(
        "helpdesk_customer_ids",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("member_id", sa.String(36), sa.ForeignKey("members.id", ondelete="CASCADE"), nullable=False),
        sa.Column("provider", sa.String(30), nullable=False),
        sa.Column("customer_id", sa.String(100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("provider", "customer_id", name="uq_helpdesk_customer_provider_customer"),
        sa.UniqueConstraint("member_id", "provider", name="uq_helpdesk_customer_member_provider"),
    )
    op.create_index("ix_helpdesk_customer_ids_member_id", "helpdesk_customer_ids", ["member_id"])
    op.execute(
        "INSERT INTO helpdesk_customer_ids (id, member_id, provider, customer_id, created_at) "
        "SELECT gen_random_uuid()::varchar, id, 'freescout', freescout_customer_id::varchar, now() "
        "FROM members WHERE freescout_customer_id IS NOT NULL"
    )
    op.drop_index("ix_members_freescout_customer_id", table_name="members")
    op.drop_column("members", "freescout_customer_id")

    # Sample data is tracked by class name (ADR 0037) -- keep already
    # generated demo conversations removable.
    op.execute(
        "UPDATE sample_data_records SET entity_type = 'HelpdeskConversationLink' "
        "WHERE entity_type = 'FreescoutConversationLink'"
    )

    # -- settings -----------------------------------------------------
    for old, new in SETTING_RENAMES:
        bind.execute(sa.text("UPDATE club_settings SET key = :new WHERE key = :old"), {"old": old, "new": new})
    configured = bind.execute(sa.text(
        "SELECT count(*) FROM club_settings WHERE key IN ('helpdesk_freescout_base_url', 'helpdesk_freescout_api_key') "
        "AND value IS NOT NULL AND value <> ''"
    )).scalar()
    if configured == 2:
        bind.execute(sa.text(
            "INSERT INTO club_settings (key, value, description, updated_at) "
            "VALUES ('helpdesk_provider', 'freescout', 'Active helpdesk', now()) ON CONFLICT (key) DO NOTHING"
        ))


def downgrade() -> None:
    """Back to the FreeScout-only shape. Conversations and customer ids of
    any other helpdesk can't be represented there and are dropped."""
    bind = op.get_bind()

    bind.execute(sa.text("DELETE FROM club_settings WHERE key = 'helpdesk_provider'"))
    for old, new in SETTING_RENAMES:
        bind.execute(sa.text("UPDATE club_settings SET key = :old WHERE key = :new"), {"old": old, "new": new})
    op.execute(
        "UPDATE sample_data_records SET entity_type = 'FreescoutConversationLink' "
        "WHERE entity_type = 'HelpdeskConversationLink'"
    )

    op.add_column("members", sa.Column("freescout_customer_id", sa.Integer(), nullable=True))
    op.execute(
        "UPDATE members m SET freescout_customer_id = h.customer_id::integer FROM helpdesk_customer_ids h "
        "WHERE h.member_id = m.id AND h.provider = 'freescout' AND h.customer_id ~ '^[0-9]+$'"
    )
    op.create_index("ix_members_freescout_customer_id", "members", ["freescout_customer_id"], unique=True)
    op.drop_index("ix_helpdesk_customer_ids_member_id", table_name="helpdesk_customer_ids")
    op.drop_table("helpdesk_customer_ids")

    op.execute(f"DELETE FROM {NEW} WHERE provider <> 'freescout' OR external_id !~ '^[0-9]+$'")
    for name in ("external_updated_at", "status", "mailbox_id", "external_id", "provider"):
        op.drop_index(f"ix_helpdesk_conversation_links_{name}", table_name=NEW)
    op.drop_constraint("uq_helpdesk_conversation_provider_external", NEW, type_="unique")
    op.alter_column(NEW, "external_updated_at", new_column_name="freescout_updated_at")
    op.alter_column(NEW, "status", new_column_name="freescout_status")
    op.execute(f"UPDATE {NEW} SET mailbox_id = '1' WHERE mailbox_id IS NULL OR mailbox_id !~ '^[0-9]+$'")
    op.alter_column(
        NEW, "mailbox_id", new_column_name="freescout_mailbox_id",
        type_=sa.Integer(), nullable=False, postgresql_using="mailbox_id::integer",
    )
    op.alter_column(
        NEW, "external_id", new_column_name="freescout_conversation_id",
        type_=sa.Integer(), postgresql_using="external_id::integer",
    )
    op.drop_column(NEW, "provider")

    op.create_index("ix_freescout_conversation_links_freescout_conversation_id", NEW, ["freescout_conversation_id"], unique=True)
    op.create_index("ix_freescout_conversation_links_freescout_mailbox_id", NEW, ["freescout_mailbox_id"])
    op.create_index("ix_freescout_conversation_links_freescout_status", NEW, ["freescout_status"])
    op.create_index("ix_freescout_conversation_links_freescout_updated_at", NEW, ["freescout_updated_at"])
    for old_name, new_name, _column in INDEXES:
        op.execute(f"ALTER INDEX {new_name} RENAME TO {old_name}")
    for fk in ("member_id", "parcel_id", "task_id"):
        op.execute(f"ALTER TABLE {NEW} RENAME CONSTRAINT {NEW}_{fk}_fkey TO {OLD}_{fk}_fkey")
    op.execute(f"ALTER TABLE {NEW} RENAME CONSTRAINT {NEW}_pkey TO {OLD}_pkey")
    op.rename_table(NEW, OLD)
