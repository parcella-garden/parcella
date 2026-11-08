"""Notes and club taxonomy

Revision ID: 0118_notes_and_taxonomy
Revises: 0117_email_log
Create Date: 2026-11-08

- taxonomy_categories / taxonomy_tags (issue #286, ADR 0122): one
  club-wide taxonomy, shared by notes now and the knowledge base (#285)
  later. Seeds the four categories the issue names, with names in all
  seven UI languages (app/tag_translations.py shows the club language's).
- notes + note_tag_links (issue #286, ADR 0123): Markdown notes, with
  the bookkeeping columns for the cloud file that is their master when
  a notes folder is configured.
"""
import uuid
from typing import Union

from alembic import op
import sqlalchemy as sa

revision: str = "0118_notes_and_taxonomy"
down_revision: Union[str, None] = "0117_email_log"
branch_labels = None
depends_on = None


_DEFAULT_CATEGORIES = [
    ("General meeting", {
        "de": "Mitgliederversammlung", "pl": "Walne zebranie", "cs": "Členská schůze",
        "sk": "Členská schôdza", "fr": "Assemblée générale", "nl": "Algemene ledenvergadering",
    }),
    ("Board meeting", {
        "de": "Vorstandssitzung", "pl": "Posiedzenie zarządu", "cs": "Schůze výboru",
        "sk": "Zasadnutie výboru", "fr": "Réunion du bureau", "nl": "Bestuursvergadering",
    }),
    ("Meeting with externals", {
        "de": "Termin mit Externen", "pl": "Spotkanie z podmiotami zewnętrznymi", "cs": "Schůzka s externisty",
        "sk": "Stretnutie s externistami", "fr": "Rendez-vous externe", "nl": "Overleg met externen",
    }),
    ("Other", {
        "de": "Sonstiges", "pl": "Inne", "cs": "Ostatní", "sk": "Ostatné", "fr": "Autre", "nl": "Overig",
    }),
]


def upgrade() -> None:
    categories = op.create_table(
        "taxonomy_categories",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("translations", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "taxonomy_tags",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("translations", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "notes",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("note_date", sa.Date(), nullable=False),
        sa.Column("category_id", sa.String(36),
                  sa.ForeignKey("taxonomy_categories.id", ondelete="SET NULL"), nullable=True),
        sa.Column("body_markdown", sa.Text(), nullable=False),
        sa.Column("created_by_user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("updated_by_user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cloud_filename", sa.String(255), nullable=True),
        sa.Column("cloud_fingerprint", sa.String(255), nullable=True),
        sa.Column("cloud_hash", sa.String(64), nullable=True),
        sa.Column("cloud_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cloud_dirty", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("cloud_delete_pending", sa.Boolean(), server_default="false", nullable=False),
    )
    op.create_index("ix_notes_note_date", "notes", ["note_date"])
    op.create_index("ix_notes_category_id", "notes", ["category_id"])
    op.create_index(
        "uq_notes_cloud_filename", "notes", ["cloud_filename"], unique=True,
        postgresql_where=sa.text("deleted_at IS NULL AND cloud_filename IS NOT NULL"),
    )
    op.create_table(
        "note_tag_links",
        sa.Column("note_id", sa.String(36), sa.ForeignKey("notes.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("tag_id", sa.String(36), sa.ForeignKey("taxonomy_tags.id", ondelete="CASCADE"), primary_key=True),
    )
    op.create_index("ix_note_tag_links_tag_id", "note_tag_links", ["tag_id"])

    op.bulk_insert(categories, [
        {"id": str(uuid.uuid4()), "name": name, "translations": translations}
        for name, translations in _DEFAULT_CATEGORIES
    ])


def downgrade() -> None:
    op.drop_table("note_tag_links")
    op.drop_table("notes")
    op.drop_table("taxonomy_tags")
    op.drop_table("taxonomy_categories")
