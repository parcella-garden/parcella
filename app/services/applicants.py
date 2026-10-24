"""
Shared applicant business logic, called by app/routers/applicants.py
(HTML), app/routers/api_applicants.py (API) and the public form/JSON
endpoints in app/routers/api_public.py -- see ADR 0070 for the split.

Small on purpose: normalize what an applicant typed, record status
changes in the audit log, and the one deliberate exception to
historization -- applicants can be hard-deleted (ADR 0091).
"""
import re
from dataclasses import dataclass, field
from datetime import date, datetime, time, timezone
from typing import Optional, Sequence, Union

from email_validator import EmailNotValidError, validate_email
from sqlalchemy import delete, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.change_tracker import ChangeTracker
from app.models import (
    Applicant, ApplicantSource, ApplicantStatus, ChangeHistory, ClubSetting, ExternalContact, ExternalContactTag,
    external_contact_tag_links,
)
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


# ---------------------------------------------------------------------------
# Red flag (ADR 0098): an applicant who matches an external contact that
# carries the club's chosen "red flag" tag -- by name, email or phone,
# any one is enough. Computed live on every list/detail view, never
# stored: applicants get hard-deleted (ADR 0091), and a contact flagged
# later must still show up on an older application.
# ---------------------------------------------------------------------------

RED_FLAG_TAG_SETTING = "applicant_red_flag_tag_id"


@dataclass
class RedFlagMatch:
    contact: ExternalContact
    fields: list[str] = field(default_factory=list)  # "name", "email", "phone"


def _name_key(first: Optional[str], last: Optional[str]) -> Optional[str]:
    if not (first or "").strip() or not (last or "").strip():
        return None
    return " ".join(f"{first} {last}".lower().split())


def _phone_key(number: Optional[str]) -> Optional[str]:
    """Digits only, so "0170 999" and "0170-999" match -- a normalization
    used for this check only; the search elsewhere stays plain text."""
    digits = re.sub(r"\D", "", number or "")
    return digits or None


async def load_red_flag_tag(db: AsyncSession) -> Optional[ExternalContactTag]:
    """The chosen tag, or None if none is chosen or it was deleted since."""
    tag_id = await db.scalar(select(ClubSetting.value).where(ClubSetting.key == RED_FLAG_TAG_SETTING))
    return await db.get(ExternalContactTag, tag_id) if tag_id else None


async def save_red_flag_tag(db: AsyncSession, tag_id: Optional[str]) -> None:
    if tag_id and await db.get(ExternalContactTag, tag_id) is None:
        raise ServiceError("external_contacts.tags.errors.not_found", http_status=404)
    entry = await db.scalar(select(ClubSetting).where(ClubSetting.key == RED_FLAG_TAG_SETTING))
    if entry is None:
        entry = ClubSetting(key=RED_FLAG_TAG_SETTING, description="External-contact tag that flags matching applicants")
        db.add(entry)
    entry.value = tag_id or ""
    await db.flush()


async def find_red_flags(db: AsyncSession, applicants: Sequence[Applicant]) -> dict[str, list[RedFlagMatch]]:
    """Applicant id -> the flagged contacts it matches (only applicants
    with at least one match appear). A flagged company flags its people
    too (ADR 0110)."""
    tag = await load_red_flag_tag(db)
    if tag is None or not applicants:
        return {}
    tagged_ids = select(external_contact_tag_links.c.contact_id).where(external_contact_tag_links.c.tag_id == tag.id)
    contacts = (await db.scalars(
        select(ExternalContact)
        .options(selectinload(ExternalContact.email_addresses), selectinload(ExternalContact.phone_numbers))
        .where(
            ExternalContact.deleted_at.is_(None),
            or_(ExternalContact.id.in_(tagged_ids), ExternalContact.company_id.in_(tagged_ids)),
        )
    )).all()
    if not contacts:
        return {}

    keyed = []
    for contact in contacts:
        keyed.append((
            contact,
            _name_key(contact.first_name, contact.last_name),
            {e.address.lower() for e in contact.email_addresses if e.address},
            {key for key in (_phone_key(p.number) for p in contact.phone_numbers) if key},
        ))

    flags: dict[str, list[RedFlagMatch]] = {}
    for applicant in applicants:
        name = _name_key(applicant.first_name, applicant.last_name)
        email = (applicant.email or "").lower()
        phone = _phone_key(applicant.phone)
        for contact, contact_name, contact_emails, contact_phones in keyed:
            fields = [
                label for label, hit in (
                    ("name", name is not None and name == contact_name),
                    ("email", bool(email) and email in contact_emails),
                    ("phone", phone is not None and phone in contact_phones),
                ) if hit
            ]
            if fields:
                flags.setdefault(applicant.id, []).append(RedFlagMatch(contact, fields))
    return flags
