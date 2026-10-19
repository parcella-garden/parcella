"""Tags: per-language names

Revision ID: 0100_tag_translations
Revises: 0099_contact_cloud_folder
Create Date: 2026-10-19

member_tags.translations and external_contact_tags.translations --
{language code: name}, shown instead of the typed name while the club
runs in that language. See app/tag_translations.py and ADR 0098.
"""
from typing import Union

from alembic import op
import sqlalchemy as sa

revision: str = "0100_tag_translations"
down_revision: Union[str, None] = "0099_contact_cloud_folder"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("member_tags", sa.Column("translations", sa.JSON(), nullable=True))
    op.add_column("external_contact_tags", sa.Column("translations", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("external_contact_tags", "translations")
    op.drop_column("member_tags", "translations")
