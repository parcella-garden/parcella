"""
Per-process cache for the ClubSetting values the request-context
middleware (app/main.py) loads on every page view: module flags, the
helpdesk web address, language, region/currency, nav order (issue #412).

Kept for TTL_SECONDS and dropped as soon as any session commits a change
to a ClubSetting row through the ORM -- the only way the app writes them.
The generation counter stops a request that started loading before such
a commit from storing the values it read before it. Branding is not
cached: its logo version is the file's mtime, which changes without a
ClubSetting write.
"""
import time
from typing import Any, Optional

from sqlalchemy import event
from sqlalchemy.orm import Session

from app.models import ClubSetting

TTL_SECONDS = 30

_value: Any = None
_loaded_at: Optional[float] = None
_generation = 0


def generation() -> int:
    return _generation


def get() -> Any:
    if _loaded_at is not None and time.monotonic() - _loaded_at < TTL_SECONDS:
        return _value
    return None


def put(value: Any, loaded_in_generation: int) -> None:
    global _value, _loaded_at
    if loaded_in_generation == _generation:
        _value, _loaded_at = value, time.monotonic()


def clear() -> None:
    global _loaded_at, _generation
    _loaded_at = None
    _generation += 1


@event.listens_for(Session, "after_flush")
def _note_setting_changes(session, flush_context):
    if any(isinstance(obj, ClubSetting) for obj in (*session.new, *session.dirty, *session.deleted)):
        session.info["club_settings_changed"] = True


@event.listens_for(Session, "after_commit")
def _clear_after_commit(session):
    if session.info.pop("club_settings_changed", False):
        clear()


@event.listens_for(Session, "after_rollback")
def _forget_after_rollback(session):
    session.info.pop("club_settings_changed", None)
