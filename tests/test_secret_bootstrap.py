"""
Zero-config SECRET_KEY (issue #296, ADR 0121): the published image
generates a key file when SECRET_KEY is unset, and re-encrypts stored
secrets that older installs encrypted with the public default key.
"""
import os
import stat

import pytest
from sqlalchemy import select

from app.config import Settings
from app.crypto_utils import fernet_for
from app.database import AsyncSessionLocal
from app.models import ClubSetting
from app.secret_bootstrap import (
    DEFAULT_SECRET_KEY,
    ensure_secret_file,
    main,
    read_secret_file,
    rekey_database,
    rekey_values,
)


def _encrypt(key: str, plaintext: str) -> str:
    return fernet_for(key).encrypt(plaintext.encode()).decode()


def _decrypt(key: str, token: str) -> str:
    return fernet_for(key).decrypt(token.encode()).decode()


def test_ensure_creates_private_file_once(tmp_path):
    path = tmp_path / "secrets" / "secret_key"
    key, created = ensure_secret_file(path)
    assert created and len(key) >= 48
    assert stat.S_IMODE(path.stat().st_mode) == 0o600

    again, created_again = ensure_secret_file(path)
    assert again == key and not created_again
    assert read_secret_file(path) == key


def test_ensure_replaces_empty_file(tmp_path):
    path = tmp_path / "secret_key"
    path.write_text("\n")
    key, created = ensure_secret_file(path)
    assert created and read_secret_file(path) == key


def test_explicit_secret_key_wins(tmp_path, monkeypatch):
    path = tmp_path / "secret_key"
    monkeypatch.setenv("SECRET_KEY_FILE", str(path))
    monkeypatch.setenv("SECRET_KEY", "explicitly-configured")
    assert main(["x", "ensure"]) == 0
    assert not path.exists()


def test_config_reads_key_file_when_secret_key_empty(tmp_path, monkeypatch):
    path = tmp_path / "secret_key"
    path.write_text("from-the-generated-file\n")
    monkeypatch.setenv("SECRET_KEY_FILE", str(path))
    assert Settings(environment="production", secret_key="").secret_key == "from-the-generated-file"


def test_config_without_key_file_still_refuses_production(tmp_path, monkeypatch):
    monkeypatch.setenv("SECRET_KEY_FILE", str(tmp_path / "missing"))
    with pytest.raises(ValueError, match="SECRET_KEY"):
        Settings(environment="production", secret_key="")
    assert Settings(environment="development", secret_key="").secret_key == DEFAULT_SECRET_KEY


def test_rekey_values_only_touches_default_key_tokens():
    new_key = "the-new-generated-key"
    rows = [
        ("smtp_password", _encrypt(DEFAULT_SECRET_KEY, "mail-pw")),
        ("already_new", _encrypt(new_key, "keep-me")),
        ("foreign", _encrypt("some-other-key", "unreadable")),
        ("club_name", "KGV Test"),
        ("empty", ""),
    ]
    updates = rekey_values(rows, new_key)
    assert set(updates) == {"smtp_password"}
    assert _decrypt(new_key, updates["smtp_password"]) == "mail-pw"
    assert rekey_values(rows, DEFAULT_SECRET_KEY) == {}


async def test_rekey_database_is_idempotent():
    new_key = "the-new-generated-key"
    async with AsyncSessionLocal() as db:
        db.add_all([
            ClubSetting(key="smtp_password", value=_encrypt(DEFAULT_SECRET_KEY, "mail-pw")),
            ClubSetting(key="club_name", value="KGV Test"),
        ])
        await db.commit()

    url = os.environ["DATABASE_URL"]
    assert await rekey_database(url, new_key) == 1
    assert await rekey_database(url, new_key) == 0

    async with AsyncSessionLocal() as db:
        values = dict((await db.execute(select(ClubSetting.key, ClubSetting.value))).all())
    assert _decrypt(new_key, values["smtp_password"]) == "mail-pw"
    assert values["club_name"] == "KGV Test"
