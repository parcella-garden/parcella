"""External contacts: documents folder in the cloud

Revision ID: 0099_contact_cloud_folder
Revises: 0098_contact_names_optional
Create Date: 2026-10-18

external_contacts.cloud_folder -- the name of one subfolder of the
club-wide base folder (ClubSetting external_contacts_cloud_folder).
See docs/module-external-contacts.md and ADR 0097.
"""
from typing import Union

from alembic import op
import sqlalchemy as sa

revision: str = "0099_contact_cloud_folder"
down_revision: Union[str, None] = "0098_contact_names_optional"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("external_contacts", sa.Column("cloud_folder", sa.String(255), nullable=True))


def downgrade() -> None:
    op.drop_column("external_contacts", "cloud_folder")
