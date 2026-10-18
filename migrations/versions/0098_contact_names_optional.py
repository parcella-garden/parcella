"""External contacts: first and last name optional

Revision ID: 0098_contact_names_optional
Revises: 0097_external_contacts
Create Date: 2026-10-18

- external_contacts.first_name / last_name become nullable.
- uq_external_contacts_person now covers any given person name (first
  and/or last), ignoring case; a contact without a person is unique by
  company name instead (uq_external_contacts_company).

See docs/module-external-contacts.md and ADR 0096.
"""
from typing import Union

from alembic import op
import sqlalchemy as sa

revision: str = "0098_contact_names_optional"
down_revision: Union[str, None] = "0097_external_contacts"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("external_contacts", "first_name", existing_type=sa.String(100), nullable=True)
    op.alter_column("external_contacts", "last_name", existing_type=sa.String(100), nullable=True)
    op.drop_index("uq_external_contacts_person", table_name="external_contacts")
    op.create_index(
        "uq_external_contacts_person", "external_contacts",
        [sa.text("lower(coalesce(first_name, ''))"), sa.text("lower(coalesce(last_name, ''))")],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL AND (first_name IS NOT NULL OR last_name IS NOT NULL)"),
    )
    op.create_index(
        "uq_external_contacts_company", "external_contacts",
        [sa.text("lower(company_name)")],
        unique=True,
        postgresql_where=sa.text(
            "deleted_at IS NULL AND first_name IS NULL AND last_name IS NULL AND company_name IS NOT NULL"
        ),
    )


def downgrade() -> None:
    # Contacts without a name can't go back under NOT NULL -- give them
    # a placeholder rather than failing the downgrade. The id suffix
    # keeps two nameless contacts apart under the old unique index.
    op.execute("UPDATE external_contacts SET first_name = '' WHERE first_name IS NULL")
    op.execute(
        "UPDATE external_contacts SET last_name = '#' || left(id, 8) WHERE last_name IS NULL"
    )
    op.drop_index("uq_external_contacts_company", table_name="external_contacts")
    op.drop_index("uq_external_contacts_person", table_name="external_contacts")
    op.create_index(
        "uq_external_contacts_person", "external_contacts",
        [sa.text("lower(first_name)"), sa.text("lower(last_name)")],
        unique=True, postgresql_where=sa.text("deleted_at IS NULL"),
    )
    op.alter_column("external_contacts", "first_name", existing_type=sa.String(100), nullable=False)
    op.alter_column("external_contacts", "last_name", existing_type=sa.String(100), nullable=False)
