"""Notes: re-read every cloud file once for file-name dates

Revision ID: 0119_notes_reread_dates
Revises: 0118_notes_and_taxonomy
Create Date: 2026-11-08

Issue #302: file names starting with "20261108 ..." or "202506_..." are
now read as the note's date (before, only "2026-11-08-..." was), when the
file's header has no `date:`. Notes already imported got the file's
last-modified date instead, so a Nextcloud copy of a template landed
on the template's date.

Data-only: forgetting the stored hash and fingerprint makes the next
sync download and re-parse each file once (step 3 of _sync() in
app/services/notes.py). The cloud file is the master (ADR 0123), so
re-reading is safe. Rows with an unpushed local edit (cloud_dirty) are
left alone: clearing their hash would make that sync treat the file as
changed underneath them and create a conflict copy. Nothing is written
to the cloud.
"""
from typing import Union

from alembic import op

revision: str = "0119_notes_reread_dates"
down_revision: Union[str, None] = "0118_notes_and_taxonomy"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "UPDATE notes SET cloud_hash = NULL, cloud_fingerprint = NULL "
        "WHERE cloud_filename IS NOT NULL AND deleted_at IS NULL AND NOT cloud_dirty"
    )


def downgrade() -> None:
    # Nothing to undo: the next sync recomputes hash and fingerprint.
    pass
