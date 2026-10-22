"""Drop the leftover IMAP and ticket-inbox club settings

Revision ID: 0104_drop_imap_settings
Revises: 0103_drop_spam_settings
Create Date: 2026-10-22

Parcella stopped reading any mailbox when the built-in ticket module
went away (ADR 0080, migration 0087), but the IMAP connection settings
and the old poller's state rows stayed behind. Nothing reads them
anymore (ADR 0103).
"""
from typing import Union

from alembic import op
import sqlalchemy as sa

revision: str = "0104_drop_imap_settings"
down_revision: Union[str, None] = "0103_drop_spam_settings"
branch_labels = None
depends_on = None

IMAP_SETTING_KEYS = (
    "imap_host",
    "imap_port",
    "imap_ssl",
    "ticket_imap_letzte_uid",
    "ticket_imap_letzter_abruf",
    "ticket_imap_letzter_fehler",
    "ticket_attachments_cloud_folder",
)


def upgrade() -> None:
    op.get_bind().execute(
        sa.text("DELETE FROM club_settings WHERE key IN :keys").bindparams(
            sa.bindparam("keys", expanding=True)
        ),
        {"keys": list(IMAP_SETTING_KEYS)},
    )


def downgrade() -> None:
    # Nothing to restore: no code reads these keys.
    pass
