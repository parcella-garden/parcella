"""Drop the announcement-level status; track delivered content per channel

Revision ID: 0092_announcement_no_status
Revises: 0091_external_task_links
Create Date: 2026-09-30

See docs/ADR/0087. announcements.status (DRAFT/PUBLISHED/ARCHIVED) is
dropped along with its enum type: PUBLISHED was never set by any code
path and ARCHIVED had no UI, so every announcement stayed "Draft"
forever regardless of what had gone out.

Four new columns on announcement_deliveries:
- content_fingerprint / image_filename: what this channel last
  delivered, so the UI only offers a channel's action again once the
  content actually changed.
- pdf_filename: stored copy of the last print PDF (download again).
- qr_pending: print PDF was shortened without a QR code because the
  blog post wasn't public yet.

Existing SENT deliveries are backfilled with the announcement's
*current* content -- the best available assumption, and it means
nothing already delivered suddenly shows up as "changed" after the
upgrade.
"""
import hashlib
from typing import Union

from alembic import op
import sqlalchemy as sa

revision: str = "0092_announcement_no_status"
down_revision: Union[str, None] = "0091_external_task_links"
branch_labels = None
depends_on = None


def _channel_fingerprint(channel, title, body_markdown, print_text_override):
    # Frozen copy of app.announcement_utils.channel_fingerprint.
    parts = [channel, title, body_markdown]
    if channel == "PRINT":
        parts.append(print_text_override or "")
    return hashlib.sha256("\x1f".join(parts).encode("utf-8")).hexdigest()


def upgrade() -> None:
    op.add_column("announcement_deliveries", sa.Column("content_fingerprint", sa.String(64), nullable=True))
    op.add_column("announcement_deliveries", sa.Column("image_filename", sa.String(255), nullable=True))
    op.add_column("announcement_deliveries", sa.Column("pdf_filename", sa.String(255), nullable=True))
    op.add_column(
        "announcement_deliveries",
        sa.Column("qr_pending", sa.Boolean(), nullable=False, server_default=sa.false()),
    )

    conn = op.get_bind()
    rows = conn.execute(sa.text(
        "SELECT d.id, d.channel, a.title, a.body_markdown, a.print_text_override, a.image_filename "
        "FROM announcement_deliveries d JOIN announcements a ON a.id = d.announcement_id "
        "WHERE d.status = 'SENT'"
    )).fetchall()
    for delivery_id, channel, title, body_markdown, print_text_override, image_filename in rows:
        conn.execute(
            sa.text(
                "UPDATE announcement_deliveries SET content_fingerprint = :fp, image_filename = :img WHERE id = :id"
            ),
            {
                "fp": _channel_fingerprint(channel, title, body_markdown, print_text_override),
                "img": image_filename, "id": delivery_id,
            },
        )

    op.drop_column("announcements", "status")
    op.execute("DROP TYPE announcementstatus")


def downgrade() -> None:
    announcement_status = sa.Enum("DRAFT", "PUBLISHED", "ARCHIVED", name="announcementstatus")
    announcement_status.create(op.get_bind())
    op.add_column(
        "announcements",
        sa.Column("status", announcement_status, nullable=False, server_default="DRAFT"),
    )
    op.drop_column("announcement_deliveries", "qr_pending")
    op.drop_column("announcement_deliveries", "pdf_filename")
    op.drop_column("announcement_deliveries", "image_filename")
    op.drop_column("announcement_deliveries", "content_fingerprint")
