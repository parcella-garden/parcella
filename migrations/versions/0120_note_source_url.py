"""Notes: source URL (a bookmark is a note with a source)

Revision ID: 0120_note_source_url
Revises: 0119_notes_reread_dates
Create Date: 2026-11-08

Issue #305 (ADR 0125): `notes.source_url`, the web page a note is
about. It's written to and read from the note file's `source:` header
like every other field (ADR 0123). Indexed, because the bookmark import
skips URLs that already have a note.
"""
from typing import Union

from alembic import op
import sqlalchemy as sa

revision: str = "0120_note_source_url"
down_revision: Union[str, None] = "0119_notes_reread_dates"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("notes", sa.Column("source_url", sa.String(length=2048), nullable=True))
    op.create_index("ix_notes_source_url", "notes", ["source_url"])


def downgrade() -> None:
    op.drop_index("ix_notes_source_url", table_name="notes")
    op.drop_column("notes", "source_url")
