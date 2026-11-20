"""
Parcella runs `alembic upgrade head` on every start. Two migrations that
build on the same parent (e.g. two PRs each adding "0131") leave two
heads, and the upgrade -- and so the app -- refuses to start. This test
fails on such a branch before it can be merged.
"""
from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory

ROOT = Path(__file__).resolve().parent.parent


def test_migrations_form_one_chain():
    script = ScriptDirectory.from_config(Config(str(ROOT / "alembic.ini")))
    heads = script.get_heads()
    assert len(heads) == 1, f"More than one migration head: {heads} -- chain the newer one onto the other"


def test_revision_ids_fit_the_version_column():
    """alembic_version.version_num is VARCHAR(32) (see CLAUDE.md)."""
    script = ScriptDirectory.from_config(Config(str(ROOT / "alembic.ini")))
    too_long = [r.revision for r in script.walk_revisions() if len(r.revision) > 32]
    assert not too_long, too_long
