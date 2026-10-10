"""
ALTCHA proof of work for the plain-HTML-form endpoints
(app/routers/api_public.py, ADR 0089).

Before a form is submitted, the visitor's browser fetches a challenge
from GET /api/v1/public/forms/challenge and the ALTCHA widget on the
website solves it (a second or so of hashing, no interaction, no
cookies, no third party). The solution travels with the form as the
field `altcha` and is checked here. A bot posting forms in bulk has to
pay that cost for every single submission -- a deterrent on top of the
honeypot and the per-IP rate limit, not instead of them.

The cryptography is the official `altcha` library (PoW v2, matching the
3.x widget); this module only adds what the library leaves to the
server: the HMAC key, expiry, the admin switch, and replay protection.

Replay protection is in-memory, the same accepted posture as
app/rate_limit.py: a used challenge is remembered until it expires
anyway (CHALLENGE_LIFETIME_SECONDS), the set is per process and empty
after a restart. Parcella runs a single uvicorn worker, so that's
sufficient here; a multi-worker setup would let one solution be reused
once per worker within those few minutes.
"""
import hashlib
import hmac
import logging
import time
from typing import Optional

from altcha import create_challenge, verify_solution, Payload
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import ClubSetting

logger = logging.getLogger(__name__)

REQUIRE_ALTCHA_SETTING_KEY = "public_form_require_altcha"

ALGORITHM = "PBKDF2/SHA-256"
# PBKDF2 iterations per attempt; the widget needs ~256 attempts on
# average (key prefix "00"), a second or so on a phone. Verification
# re-derives the key once.
COST = 5_000
CHALLENGE_LIFETIME_SECONDS = 600

# signature of an accepted challenge -> its expiry (unix time)
_used: dict[str, float] = {}


def _hmac_secret() -> str:
    """Derived from SECRET_KEY, so there's nothing extra to configure --
    and rotating SECRET_KEY invalidates outstanding challenges along
    with everything else signed by it."""
    return hmac.new(settings.secret_key.encode(), b"parcella-altcha", hashlib.sha256).hexdigest()


def new_challenge() -> dict:
    challenge = create_challenge(
        algorithm=ALGORITHM, cost=COST,
        expires_at=int(time.time()) + CHALLENGE_LIFETIME_SECONDS,
        hmac_secret=_hmac_secret(),
    )
    return challenge.to_dict()


def _forget_expired(now: float) -> None:
    for signature in [s for s, expires in _used.items() if expires < now]:
        del _used[signature]


def verify(payload: Optional[str]) -> bool:
    """True for a correct, unexpired solution of a challenge this server
    issued and that hasn't been used before."""
    if not payload:
        return False
    try:
        parsed = Payload.from_base64(payload)
        result = verify_solution(parsed, _hmac_secret())
    except (ValueError, KeyError, TypeError, AttributeError):  # malformed payload
        return False
    if not result.verified:
        return False

    now = time.time()
    _forget_expired(now)
    signature = parsed.challenge.signature
    if signature in _used:
        logger.info("ALTCHA solution replayed, rejecting form submission")
        return False
    _used[signature] = parsed.challenge.parameters.expires_at or now + CHALLENGE_LIFETIME_SECONDS
    return True


def reset_used() -> None:
    """For tests: forget all accepted challenges."""
    _used.clear()


async def altcha_required(db: AsyncSession) -> bool:
    result = await db.execute(select(ClubSetting).where(ClubSetting.key == REQUIRE_ALTCHA_SETTING_KEY))
    entry = result.scalar_one_or_none()
    return bool(entry and (entry.value or "").strip().lower() in ("1", "true", "on", "yes"))
