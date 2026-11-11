"""Notes: strip the front-matter header from every cloud file once

Revision ID: 0122_notes_strip_headers
Revises: 0121_api_tokens
Create Date: 2026-11-11

Issue #311, ADR 0127: a note's title, date, category, tags and source
now live in Parcella only; the .md file in the cloud holds just the
note's text. Changing the metadata no longer rewrites the file, so a
file that's locked in a cloud editor (WebDAV 423) can't block it.

Data-only: sets the ClubSetting `notes_strip_headers_pending`. While it
exists, the next notes sync reads every file (not only changed ones),
takes over any header edits made in the cloud since the last sync, and
rewrites each file that still has a header as text only. The sync
removes the setting once it went through without an error, so a file
that's locked at that moment is retried on the next sync. Without a
notes folder configured, the setting just waits.
"""
from typing import Union

from alembic import op

revision: str = "0122_notes_strip_headers"
down_revision: Union[str, None] = "0121_api_tokens"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "INSERT INTO club_settings (key, value, description) VALUES "
        "('notes_strip_headers_pending', 'true', "
        "'One-time: next notes sync rewrites cloud note files as text only (issue #311)') "
        "ON CONFLICT (key) DO NOTHING"
    )


def downgrade() -> None:
    # Files already rewritten stay text only: the metadata is in the
    # notes table either way.
    op.execute("DELETE FROM club_settings WHERE key = 'notes_strip_headers_pending'")
