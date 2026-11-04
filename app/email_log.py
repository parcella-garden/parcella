"""
Email log (issue #270, ADR 0120): every message app.email_service.
send_email() tries to send gets a row with date/time, recipient,
subject and the SMTP result.

What it can know: whether the SMTP server *accepted* the message (SENT)
or refused it / couldn't be reached / wasn't configured (FAILED, with
the error). What it can't: a bounce that comes back later, as a mail
into the sending mailbox -- Parcella doesn't read that mailbox.

Recipient addresses are personal data, so rows are deleted after
`email_log_retention_days` (default 90), on regular site use at most
once an hour, the same way applicant retention works (ADR 0091).
"""
import logging
import time as time_module
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Tuple

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ClubSetting, EmailLog, EmailLogStatus

logger = logging.getLogger(__name__)

RETENTION_SETTING = "email_log_retention_days"
DEFAULT_RETENTION_DAYS = 90
MAX_RETENTION_DAYS = 3650
_PURGE_INTERVAL_SECONDS = 3600
_last_purge: Optional[float] = None

_MAX_RECIPIENT = 320
_MAX_SUBJECT = 500
_MAX_ERROR = 2000


def parse_retention_days(value: Optional[str]) -> int:
    """The setting as stored: whole days between 1 and 3650; anything
    else (unset, blank, garbage, out of range) means the default."""
    try:
        days = int((value or "").strip())
    except ValueError:
        return DEFAULT_RETENTION_DAYS
    return days if 1 <= days <= MAX_RETENTION_DAYS else DEFAULT_RETENTION_DAYS


async def load_retention_days(db: AsyncSession) -> int:
    return parse_retention_days(
        await db.scalar(select(ClubSetting.value).where(ClubSetting.key == RETENTION_SETTING))
    )


async def record_email(
    recipient: str, subject: str, status: EmailLogStatus,
    error: Optional[str] = None, attachment_count: int = 0,
) -> None:
    """Writes one log row in its own session and transaction, so a
    caller that rolls back (or never commits) doesn't lose the entry,
    and a caller's half-done transaction isn't committed by us. Never
    raises: a broken log must not stop mail from going out."""
    from app.database import AsyncSessionLocal

    try:
        async with AsyncSessionLocal() as session:
            session.add(EmailLog(
                recipient=(recipient or "")[:_MAX_RECIPIENT],
                subject=(subject or "")[:_MAX_SUBJECT],
                status=status,
                error=(error or None) and error[:_MAX_ERROR],
                attachment_count=attachment_count,
            ))
            await session.commit()
    except Exception as e:  # logging must never break sending
        logger.error(f"Could not write the email log entry for {recipient}: {e}")


async def purge_expired_email_logs(db: AsyncSession, now: Optional[datetime] = None) -> int:
    """Deletes rows older than the retention period; returns how many."""
    days = await load_retention_days(db)
    cutoff = (now or datetime.now(timezone.utc)) - timedelta(days=days)
    result = await db.execute(delete(EmailLog).where(EmailLog.sent_at < cutoff))
    await db.commit()
    return result.rowcount or 0


async def maybe_purge_expired_email_logs(db: AsyncSession) -> None:
    """Called on every logged-in request (nav_counts_middleware), runs
    at most once an hour per process."""
    global _last_purge
    now = time_module.monotonic()
    if _last_purge is not None and now - _last_purge < _PURGE_INTERVAL_SECONDS:
        return
    _last_purge = now
    await purge_expired_email_logs(db)


def parse_status(value: Optional[str]) -> Optional[EmailLogStatus]:
    """A status filter from a query string, or None for "all"."""
    try:
        return EmailLogStatus[(value or "").strip().upper()]
    except KeyError:
        return None


async def query_email_logs(
    db: AsyncSession, status: Optional[EmailLogStatus] = None, recipient: Optional[str] = None,
    limit: int = 50, offset: int = 0,
) -> Tuple[List[EmailLog], int]:
    """Newest first, optionally filtered by status and a recipient
    substring (case-insensitive, LIKE wildcards escaped). Returns the
    page and the total count. Shared by /admin/email-log and the API."""
    conditions = []
    if status is not None:
        conditions.append(EmailLog.status == status)
    if recipient and recipient.strip():
        conditions.append(EmailLog.recipient.icontains(recipient.strip(), autoescape=True))
    total = await db.scalar(select(func.count()).select_from(EmailLog).where(*conditions))
    rows = (await db.scalars(
        select(EmailLog).where(*conditions).order_by(EmailLog.sent_at.desc(), EmailLog.id)
        .limit(limit).offset(offset)
    )).all()
    return list(rows), total or 0
