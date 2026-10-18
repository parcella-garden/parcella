"""External contacts: suppliers, craftsmen, authorities

Revision ID: 0097_external_contacts
Revises: 0096_announcement_audience
Create Date: 2026-10-18

- external_contacts (company + contact person, soft delete) with phone,
  email and its own tag tables -- separate from the member ones.
- uq_external_contacts_person: contact person's name unique ignoring
  case among non-deleted contacts; the company name may repeat.
- external_contact_id on incoming_invoices and purchase_requests.

See docs/module-external-contacts.md and ADR 0096.
"""
from typing import Union

from alembic import op
import sqlalchemy as sa

revision: str = "0097_external_contacts"
down_revision: Union[str, None] = "0096_announcement_audience"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "external_contacts",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("company_name", sa.String(255), nullable=True),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("street", sa.String(255), nullable=True),
        sa.Column("postal_code", sa.String(10), nullable=True),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("iban", sa.String(34), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_external_contacts_company_name", "external_contacts", ["company_name"])
    op.create_index(
        "uq_external_contacts_person", "external_contacts",
        [sa.text("lower(first_name)"), sa.text("lower(last_name)")],
        unique=True, postgresql_where=sa.text("deleted_at IS NULL"),
    )

    op.create_table(
        "external_contact_phones",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("contact_id", sa.String(36), sa.ForeignKey("external_contacts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("number", sa.String(50), nullable=False),
        sa.Column("label", sa.String(50), nullable=True),
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_index("ix_external_contact_phones_contact_id", "external_contact_phones", ["contact_id"])

    op.create_table(
        "external_contact_emails",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("contact_id", sa.String(36), sa.ForeignKey("external_contacts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("address", sa.String(255), nullable=False),
        sa.Column("label", sa.String(50), nullable=True),
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_index("ix_external_contact_emails_contact_id", "external_contact_emails", ["contact_id"])

    op.create_table(
        "external_contact_tags",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "external_contact_tag_links",
        sa.Column("contact_id", sa.String(36), sa.ForeignKey("external_contacts.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("tag_id", sa.String(36), sa.ForeignKey("external_contact_tags.id", ondelete="CASCADE"), primary_key=True),
    )
    op.create_index("ix_external_contact_tag_links_tag_id", "external_contact_tag_links", ["tag_id"])

    for table in ("incoming_invoices", "purchase_requests"):
        op.add_column(table, sa.Column(
            "external_contact_id", sa.String(36),
            sa.ForeignKey("external_contacts.id", ondelete="SET NULL"), nullable=True,
        ))
        op.create_index(f"ix_{table}_external_contact_id", table, ["external_contact_id"])


def downgrade() -> None:
    for table in ("purchase_requests", "incoming_invoices"):
        op.drop_index(f"ix_{table}_external_contact_id", table_name=table)
        op.drop_column(table, "external_contact_id")
    op.drop_index("ix_external_contact_tag_links_tag_id", table_name="external_contact_tag_links")
    op.drop_table("external_contact_tag_links")
    op.drop_table("external_contact_tags")
    op.drop_index("ix_external_contact_emails_contact_id", table_name="external_contact_emails")
    op.drop_table("external_contact_emails")
    op.drop_index("ix_external_contact_phones_contact_id", table_name="external_contact_phones")
    op.drop_table("external_contact_phones")
    op.drop_index("uq_external_contacts_person", table_name="external_contacts")
    op.drop_index("ix_external_contacts_company_name", table_name="external_contacts")
    op.drop_table("external_contacts")
