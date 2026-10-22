"""Website connectors: move the WordPress settings into the new scheme

Revision ID: 0105_website_connectors
Revises: 0104_drop_imap_settings
Create Date: 2026-10-22

The blog channel became CMS-agnostic (ADR 0104): one active connector,
named in the ClubSetting `website_connector`, with its fields stored as
`website_<type>_<field>`. The three `wordpress_*` settings are renamed
to `website_wordpress_*` -- values untouched, so the encrypted
Application Password keeps working -- and a fully configured WordPress
becomes the active connector, so nothing changes for clubs using it.
"""
from typing import Union

from alembic import op
import sqlalchemy as sa

revision: str = "0105_website_connectors"
down_revision: Union[str, None] = "0104_drop_imap_settings"
branch_labels = None
depends_on = None

RENAMES = (
    ("wordpress_site_url", "website_wordpress_site_url"),
    ("wordpress_username", "website_wordpress_username"),
    ("wordpress_app_password", "website_wordpress_app_password"),
)


def upgrade() -> None:
    bind = op.get_bind()
    for old, new in RENAMES:
        bind.execute(sa.text("UPDATE club_settings SET key = :new WHERE key = :old"), {"old": old, "new": new})

    configured = bind.execute(
        sa.text(
            "SELECT count(*) FROM club_settings WHERE key IN :keys AND value IS NOT NULL AND value <> ''"
        ).bindparams(sa.bindparam("keys", expanding=True)),
        {"keys": [new for _old, new in RENAMES]},
    ).scalar()
    if configured == len(RENAMES):
        bind.execute(sa.text(
            "INSERT INTO club_settings (key, value, description, updated_at) "
            "VALUES ('website_connector', 'wordpress', 'Active website connector', now()) "
            "ON CONFLICT (key) DO NOTHING"
        ))


def downgrade() -> None:
    bind = op.get_bind()
    bind.execute(sa.text("DELETE FROM club_settings WHERE key = 'website_connector'"))
    for old, new in RENAMES:
        bind.execute(sa.text("UPDATE club_settings SET key = :old WHERE key = :new"), {"old": old, "new": new})
