"""
Shared in-memory sliding-window rate limiting.

Extracted from the public signup API (app/routers/api_public.py), which
had the only limiter in the app, when login got one too -- the same
"count events per key in a moving time window" shape, so one
implementation rather than two near-identical copies (same reasoning as
ADR 0003 for router factories).

Deliberately no new dependency (no Redis, no slowapi): this is a small,
single-process app for a single club. The consequences are accepted and
worth stating plainly -- counters reset on restart and are not shared
across multiple workers, so this is a deterrent that raises the cost of
online guessing, not an authoritative lockout. It is layered on top of
the actual access control (password, API token), never instead of it.

Keying on the client IP inherits whatever `request.client.host` yields.
Behind a reverse proxy that is the proxy's address unless uvicorn runs
with --proxy-headers and the proxy sets X-Forwarded-For -- see
docs/operations.md; without that, per-IP limits degrade into one global
bucket (still a limit, just a blunter one).
"""
import time
from collections import defaultdict, deque
from typing import Deque, Dict, Optional

from fastapi import Request

_events: Dict[str, Deque[float]] = defaultdict(deque)


def _prune(key: str, window_seconds: int, now: float) -> Deque[float]:
    window = _events[key]
    while window and now - window[0] > window_seconds:
        window.popleft()
    return window


def is_rate_limited(key: str, max_events: int, window_seconds: int) -> bool:
    """True if `key` has already used up its budget. Read-only: does not
    itself count as an event, so a caller can check before doing work and
    record only the outcomes it actually wants to count (failed logins,
    for instance, but not successful ones)."""
    window = _prune(key, window_seconds, time.monotonic())
    return len(window) >= max_events


def record_event(key: str, window_seconds: int) -> None:
    """Counts one event against `key`."""
    now = time.monotonic()
    _prune(key, window_seconds, now)
    _events[key].append(now)


def check_and_record(key: str, max_events: int, window_seconds: int) -> bool:
    """Combined check-then-count for endpoints that limit every request
    rather than only failures (the public signup API). Returns False when
    the request should be rejected."""
    if is_rate_limited(key, max_events, window_seconds):
        return False
    record_event(key, window_seconds)
    return True


def clear_key(key: str) -> None:
    """Forgets a key's history -- used to reset the failure counter after
    a successful login, so a user who mistyped their password a few times
    isn't left near the limit for the rest of the window."""
    _events.pop(key, None)


def reset_all() -> None:
    """Test helper: drops every counter. Necessary because the state is
    module-level and would otherwise leak between tests."""
    _events.clear()


def client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"


def client_ip_key(
    request: Request, prefix: str, discriminator: Optional[str] = None, ip: Optional[str] = None,
) -> str:
    """Builds a namespaced key, e.g. "login:ip:203.0.113.5" or
    "login:ip+email:203.0.113.5|someone@example.org". The prefix keeps
    unrelated limiters from sharing a bucket. `ip` overrides the
    connection's address -- for a trusted connector that forwards its
    visitor's IP (see app/routers/api_public.py)."""
    base = f"{prefix}:{ip or client_ip(request)}"
    return f"{base}|{discriminator}" if discriminator else base
