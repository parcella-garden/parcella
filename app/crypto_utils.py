"""
Encryption for sensitive setting values (e.g. SMTP password) stored in
the database. Uses Fernet (symmetric encryption from the
`cryptography` library), with a key derived from SECRET_KEY.

Important: if SECRET_KEY changes, already-encrypted values can no
longer be decrypted. This is intentional -- SECRET_KEY should stay
stable and secret regardless.
"""
import base64
import binascii
import hashlib
import logging
from typing import Optional

from cryptography.fernet import Fernet, InvalidToken

from app.config import settings

logger = logging.getLogger(__name__)

_FERNET_VERSION_BYTE = 0x80


class DecryptionError(Exception):
    """
    Raised when a value structurally looks like a Fernet token (i.e. it
    was actually encrypted at some point) but can't be decrypted with
    the current SECRET_KEY -- most likely SECRET_KEY was rotated without
    re-encrypting stored values. Deliberately distinct from the legacy
    plaintext fallback below: silently returning ciphertext here would
    mean sending it on as if it were the real secret (e.g. as an SMTP
    password), which fails in a much more confusing way downstream.
    """


def fernet_for(secret_key: str) -> Fernet:
    """A Fernet for an arbitrary SECRET_KEY value (a Fernet-valid 32-byte
    key derived from it). Used directly by app/secret_bootstrap.py to
    re-encrypt values from the old default key."""
    digest = hashlib.sha256(secret_key.encode("utf-8")).digest()
    return Fernet(base64.urlsafe_b64encode(digest))


_fernet = fernet_for(settings.secret_key)


def _looks_like_fernet_token(value: str) -> bool:
    """
    Distinguishes "was never encrypted" (arbitrary legacy plaintext)
    from "was encrypted, but can't be decrypted now" -- both raise
    InvalidToken/ValueError from Fernet, but only the latter should be
    treated as an error. Every Fernet token is urlsafe-base64 and its
    first decoded byte is a fixed version marker; plaintext passwords
    essentially never happen to satisfy that by chance.
    """
    try:
        padded = value + "=" * (-len(value) % 4)
        raw = base64.urlsafe_b64decode(padded.encode("utf-8"))
    except (ValueError, binascii.Error):
        return False
    return len(raw) > 0 and raw[0] == _FERNET_VERSION_BYTE


def encrypt(plaintext: str) -> str:
    """Encrypts a string for storage in the database."""
    if not plaintext:
        return plaintext
    return _fernet.encrypt(plaintext.encode("utf-8")).decode("utf-8")


def decrypt(value: Optional[str]) -> Optional[str]:
    """
    Decrypts a previously encrypted string.

    Backwards compatibility: values stored in plaintext before
    encryption was introduced aren't a valid Fernet token -- in that
    case the value is returned unchanged (as plaintext). A value that
    *does* look like a Fernet token but still fails to decrypt (e.g.
    after a SECRET_KEY rotation) raises DecryptionError instead of
    being passed through -- see DecryptionError's docstring.
    """
    if not value:
        return value
    try:
        return _fernet.decrypt(value.encode("utf-8")).decode("utf-8")
    except (InvalidToken, ValueError):
        if _looks_like_fernet_token(value):
            raise DecryptionError(
                "Value looks like an encrypted token but could not be decrypted -- "
                "did SECRET_KEY change since it was stored?"
            )
        logger.warning("Could not decrypt value -- treating it as plaintext (legacy data?).")
        return value
