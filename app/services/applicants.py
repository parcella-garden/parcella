"""
Shared applicant business logic, called by app/routers/applicants.py
(HTML), app/routers/api_applicants.py (API) and the public form/JSON
endpoints in app/routers/api_public.py -- see ADR 0070 for the split.

Small on purpose: normalize what an applicant typed, record status
changes in the audit log, and the one deliberate exception to
historization -- applicants can be hard-deleted (ADR 0091).
"""
from datetime import date, datetime, time, timezone
from typing import Optional, Union

from email_validator import EmailNotValidError, validate_email
from sqlalchemy import delete

from app.change_tracker import ChangeTracker
from app.models import Applicant, ApplicantSource, ApplicantStatus, ChangeHistory
from app.services.errors import ServiceError

# Fields whose changes are worth an audit-log entry. Contact data and
# the board note are edited freely and would only add noise; the
# application date decides the waiting-list order (issue #240), so a
# change to it is recorded like a status change.
_TRACKED_FIELDS = ["status", "applied_at"]


def _clean(value: Optional[str]) -> Optional[str]:
    """Blank counts as absent -- HTML forms send untouched fields as ""."""
    value = (value or "").strip()
    return value or None


def normalize_email(value: Optional[str]) -> str:
    try:
        return validate_email((value or "").strip(), check_deliverability=False).normalized
    except EmailNotValidError:
        raise ServiceError("applicants.errors.invalid_email")


def parse_applied_at(
    value: Union[None, str, date, datetime], current: Optional[datetime] = None,
) -> Optional[datetime]:
    """The application date as entered by the board (issue #240): a
    date from the HTML form (YYYY-MM-DD) or a datetime from the API.
    Returns None for "leave it as it is" -- blank, or the same calendar
    day as `current`, so re-saving the form never loses the original
    time of a web application. A bare date is stored as midnight UTC,
    the zone every applied_at is displayed in. Future dates are refused:
    nobody can have applied tomorrow -- a date against the server's
    date.today() (what the form's max= uses), a datetime against now.
    Datetimes are normalized to UTC, so the same instant sent with
    another offset isn't logged as a change."""
    if value is None or value == "":
        return None
    if isinstance(value, str):
        try:
            value = date.fromisoformat(value.strip())
        except ValueError:
            raise ServiceError("applicants.errors.invalid_applied_at")
    if isinstance(value, datetime):
        new = (value if value.tzinfo else value.replace(tzinfo=timezone.utc)).astimezone(timezone.utc)
        if new > datetime.now(timezone.utc):
            raise ServiceError("applicants.errors.applied_at_in_future")
        return new
    if value > date.today():
        raise ServiceError("applicants.errors.applied_at_in_future")
    if current is not None and current.astimezone(timezone.utc).date() == value:
        return None
    return datetime.combine(value, time.min, tzinfo=timezone.utc)


async def create_applicant(
    db, *, email: str, first_name: Optional[str] = None, last_name: Optional[str] = None,
    phone: Optional[str] = None, message: Optional[str] = None, board_note: Optional[str] = None,
    source: ApplicantSource = ApplicantSource.WEBSITE, consent_given: bool = False,
    created_by_id: Optional[str] = None,
    applied_at: Union[None, str, date, datetime] = None,
) -> Applicant:
    applied = parse_applied_at(applied_at)
    applicant = Applicant(
        email=normalize_email(email),
        first_name=_clean(first_name), last_name=_clean(last_name),
        phone=_clean(phone), message=_clean(message), board_note=_clean(board_note),
        source=source, status=ApplicantStatus.NEW,
        consent_at=datetime.now(timezone.utc) if consent_given else None,
        created_by_id=created_by_id,
    )
    if applied is not None:
        applicant.applied_at = applied
    db.add(applicant)
    await db.commit()
    await db.refresh(applicant)
    return applicant


async def update_applicant(
    db, applicant: Applicant, *, changed_by_id: Optional[str], **changes,
) -> Applicant:
    """Applies the given fields (any of email, first_name, last_name,
    phone, message, board_note, status, applied_at); fields not passed
    stay as they are. A status or application-date change is written
    to change_history."""
    tracker = ChangeTracker(applicant, "Applicant", _TRACKED_FIELDS)

    if "email" in changes:
        applicant.email = normalize_email(changes.pop("email"))
    new_status = changes.pop("status", None)
    if "applied_at" in changes:
        applied = parse_applied_at(changes.pop("applied_at"), current=applicant.applied_at)
        if applied is not None:
            applicant.applied_at = applied
    for field in ("first_name", "last_name", "phone", "message", "board_note"):
        if field in changes:
            setattr(applicant, field, _clean(changes.pop(field)))
    if changes:
        raise ValueError(f"Unknown applicant fields: {sorted(changes)}")

    if new_status is not None:
        new_status = ApplicantStatus(new_status)
        if new_status != applicant.status:
            applicant.status = new_status
            applicant.status_changed_at = datetime.now(timezone.utc)

    await tracker.commit(db, changed_by_id)
    await db.commit()
    await db.refresh(applicant)
    return applicant


async def delete_applicant(db, applicant: Applicant) -> None:
    """Hard delete -- see ADR 0091. Its change_history rows go too: they
    carry nothing personal, but would be orphans pointing at nothing."""
    await db.execute(delete(ChangeHistory).where(
        ChangeHistory.entity_type == "Applicant", ChangeHistory.entity_id == applicant.id,
    ))
    await db.delete(applicant)
    await db.commit()
