"""Drop the leftover spam-filter club settings

Revision ID: 0103_drop_spam_settings
Revises: 0102_cloud_folder_schedule
Create Date: 2026-10-22

The spam filter went away with the built-in ticket module (ADR 0080,
migration 0087), but its ClubSetting rows stayed behind -- including
an encrypted external API key. Nothing reads them anymore (ADR 0103).
"""
from typing import Union

from alembic import op
import sqlalchemy as sa

revision: str = "0103_drop_spam_settings"
down_revision: Union[str, None] = "0102_cloud_folder_schedule"
branch_labels = None
depends_on = None

SPAM_SETTING_KEYS = (
    "spam_domain_blocklist",
    "spam_keyword_blocklist",
    "spam_schwellenwert",
    "spam_threshold",
    "spam_api_url",
    "spam_api_key",
)


def upgrade() -> None:
    op.get_bind().execute(
        sa.text("DELETE FROM club_settings WHERE key IN :keys").bindparams(
            sa.bindparam("keys", expanding=True)
        ),
        {"keys": list(SPAM_SETTING_KEYS)},
    )


def downgrade() -> None:
    # Nothing to restore: no code reads these keys, and the deleted
    # values (an encrypted API key among them) aren't recoverable here.
    pass
