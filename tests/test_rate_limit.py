"""The in-memory rate limiter must not keep a key per lookup: checking a
key that never had an event, or one whose events all expired, leaves
nothing behind (audit 2026-11-26: random login emails grew memory)."""
from app import rate_limit


def test_lookups_and_expired_windows_leave_no_keys(monkeypatch):
    for n in range(100):
        assert not rate_limit.is_rate_limited(f"login:test:{n}", 10, 60)
    assert not rate_limit._events

    now = [1000.0]
    monkeypatch.setattr(rate_limit.time, "monotonic", lambda: now[0])
    rate_limit.record_event("login:test:x", 60)
    assert "login:test:x" in rate_limit._events
    now[0] += 61
    assert not rate_limit.is_rate_limited("login:test:x", 1, 60)
    assert "login:test:x" not in rate_limit._events


def test_limit_still_applies():
    for _ in range(3):
        rate_limit.record_event("login:test:y", 60)
    assert rate_limit.is_rate_limited("login:test:y", 3, 60)
    assert not rate_limit.is_rate_limited("login:test:y", 4, 60)
