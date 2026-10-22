"""Cloud storage providers: move the Nextcloud settings into the new scheme

Revision ID: 0106_cloud_storage_providers
Revises: 0105_website_connectors
Create Date: 2026-10-22

Cloud storage became pluggable (ADR 0106): one active provider, named
in the ClubSetting `cloud_storage_provider`, with its fields stored as
`cloud_storage_<type>_<field>`. The three `nextcloud_*` settings are
renamed to `cloud_storage_nextcloud_*` -- values untouched, so the
encrypted app password keeps working -- and a fully configured
Nextcloud becomes the active provider, so nothing changes for clubs
using it. Nextcloud Deck's own `deck_*` settings are separate and stay.
"""
from typing import Union

from alembic import op
import sqlalchemy as sa

revision: str = "0106_cloud_storage_providers"
down_revision: Union[str, None] = "0105_website_connectors"
branch_labels = None
depends_on = None

RENAMES = (
    ("nextcloud_base_url", "cloud_storage_nextcloud_base_url"),
    ("nextcloud_username", "cloud_storage_nextcloud_username"),
    ("nextcloud_app_password", "cloud_storage_nextcloud_app_password"),
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
            "VALUES ('cloud_storage_provider', 'nextcloud', 'Active cloud storage provider', now()) "
            "ON CONFLICT (key) DO NOTHING"
        ))


def downgrade() -> None:
    bind = op.get_bind()
    bind.execute(sa.text("DELETE FROM club_settings WHERE key = 'cloud_storage_provider'"))
    for old, new in RENAMES:
        bind.execute(sa.text("UPDATE club_settings SET key = :old WHERE key = :new"), {"old": old, "new": new})
