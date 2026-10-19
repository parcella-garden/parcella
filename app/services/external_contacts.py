"""
Shared external-contact business logic, called by both
app/routers/external_contacts.py (HTML) and
app/routers/api_external_contacts.py (API) -- see ADR 0070.

The one real rule here, among non-deleted contacts and ignoring case
(ADR 0096): a given person name (first and/or last) is unique; a
contact without a person is unique by company name, which otherwise may
repeat. Every field is optional. The partial unique indexes
uq_external_contacts_person / uq_external_contacts_company are the
safety net; check_duplicate_free() runs first so the user gets a
readable error instead of an IntegrityError.

Tags work exactly like member tags (ADR 0093) but in their own pool.
"""
from datetime import datetime, timezone
from typing import Iterable, Optional

from sqlalchemy import delete, func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    ExternalContact, ExternalContactEmail, ExternalContactPhone, ExternalContactTag,
    external_contact_tag_links,
)
from app.services.errors import ServiceError
from app.tag_translations import clean_translations, find_tag_by_name

STRING_FIELDS = ("company_name", "first_name", "last_name", "street", "postal_code", "city", "iban", "notes")


def _clean(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    value = value.strip()
    return value or None


def _lower(value: Optional[str]) -> Optional[str]:
    value = _clean(value)
    return value.lower() if value else None


async def find_duplicate(
    db: AsyncSession, *, first_name: Optional[str], last_name: Optional[str], company_name: Optional[str],
) -> Optional[ExternalContact]:
    """The non-deleted contact these values would duplicate, if any:
    same person name if one is given, otherwise same company among the
    contacts without a person. None for a contact with neither."""
    first, last, company = _lower(first_name), _lower(last_name), _lower(company_name)
    query = select(ExternalContact).where(ExternalContact.deleted_at.is_(None))
    if first or last:
        query = query.where(
            func.lower(func.coalesce(ExternalContact.first_name, "")) == (first or ""),
            func.lower(func.coalesce(ExternalContact.last_name, "")) == (last or ""),
        )
    elif company:
        query = query.where(
            ExternalContact.first_name.is_(None), ExternalContact.last_name.is_(None),
            func.lower(ExternalContact.company_name) == company,
        )
    else:
        return None
    return await db.scalar(query)


async def check_duplicate_free(
    db: AsyncSession, *, first_name: Optional[str], last_name: Optional[str], company_name: Optional[str],
    exclude_id: Optional[str] = None,
) -> None:
    existing = await find_duplicate(db, first_name=first_name, last_name=last_name, company_name=company_name)
    if existing is None or existing.id == exclude_id:
        return
    if existing.has_person:
        raise ServiceError(
            "external_contacts.errors.name_taken", http_status=409,
            name=existing.full_name, company=existing.company_name or "–",
        )
    raise ServiceError("external_contacts.errors.company_taken", http_status=409, company=existing.company_name)


async def get_contact(db: AsyncSession, contact_id: Optional[str]) -> Optional[ExternalContact]:
    """A non-deleted contact by id, or None -- for validating a picked
    contact on incoming invoices / purchase requests."""
    if not contact_id:
        return None
    return await db.scalar(
        select(ExternalContact).where(ExternalContact.id == contact_id, ExternalContact.deleted_at.is_(None))
    )


async def list_active_contacts(db: AsyncSession) -> list[ExternalContact]:
    """For the contact pickers on other modules' forms."""
    return list((await db.scalars(
        select(ExternalContact)
        .where(ExternalContact.deleted_at.is_(None))
        .order_by(func.lower(func.coalesce(ExternalContact.company_name, "")), ExternalContact.last_name, ExternalContact.first_name)
    )).all())


async def create_contact(
    db: AsyncSession,
    *,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    company_name: Optional[str] = None,
    street: Optional[str] = None,
    postal_code: Optional[str] = None,
    city: Optional[str] = None,
    iban: Optional[str] = None,
    notes: Optional[str] = None,
) -> ExternalContact:
    await check_duplicate_free(db, first_name=first_name, last_name=last_name, company_name=company_name)
    contact = ExternalContact(
        company_name=_clean(company_name),
        first_name=_clean(first_name),
        last_name=_clean(last_name),
        street=_clean(street),
        postal_code=_clean(postal_code),
        city=_clean(city),
        iban=_clean(iban),
        notes=_clean(notes),
    )
    db.add(contact)
    await db.flush()
    return contact


async def update_contact(db: AsyncSession, contact: ExternalContact, **fields) -> ExternalContact:
    """Partial update: only keys present in `fields` are changed."""
    fields = {k: (_clean(v) if k in STRING_FIELDS and v is not None else v) for k, v in fields.items()}
    await check_duplicate_free(
        db,
        first_name=fields.get("first_name", contact.first_name),
        last_name=fields.get("last_name", contact.last_name),
        company_name=fields.get("company_name", contact.company_name),
        exclude_id=contact.id,
    )
    for key, value in fields.items():
        setattr(contact, key, value)
    await db.flush()
    return contact


async def soft_delete_contact(db: AsyncSession, contact: ExternalContact) -> None:
    """Sets deleted_at (ADR 0005) -- linked incoming invoices and
    purchase requests keep pointing at it. Frees the name for reuse."""
    contact.deleted_at = datetime.now(timezone.utc)
    await db.flush()


async def add_phone(
    db: AsyncSession, contact_id: str, *, number: str, label: Optional[str] = None, is_primary: bool = False,
) -> ExternalContactPhone:
    phone = ExternalContactPhone(
        contact_id=contact_id, number=number.strip(), label=_clean(label), is_primary=is_primary,
    )
    db.add(phone)
    await db.flush()
    return phone


async def remove_phone(db: AsyncSession, contact_id: str, phone_id: str) -> bool:
    phone = await db.scalar(
        select(ExternalContactPhone).where(
            ExternalContactPhone.id == phone_id, ExternalContactPhone.contact_id == contact_id,
        )
    )
    if phone is None:
        return False
    await db.delete(phone)
    await db.flush()
    return True


async def add_email(
    db: AsyncSession, contact_id: str, *, address: str, label: Optional[str] = None, is_primary: bool = False,
) -> ExternalContactEmail:
    email_obj = ExternalContactEmail(
        contact_id=contact_id, address=address.strip().lower(), label=_clean(label), is_primary=is_primary,
    )
    db.add(email_obj)
    await db.flush()
    return email_obj


async def remove_email(db: AsyncSession, contact_id: str, email_id: str) -> bool:
    email_obj = await db.scalar(
        select(ExternalContactEmail).where(
            ExternalContactEmail.id == email_id, ExternalContactEmail.contact_id == contact_id,
        )
    )
    if email_obj is None:
        return False
    await db.delete(email_obj)
    await db.flush()
    return True


async def merge_phones_and_emails(
    db: AsyncSession, contact: ExternalContact, *, phones: Iterable[str], emails: Iterable[str],
) -> None:
    """CSV import: adds the numbers/addresses the contact doesn't have
    yet, never removes any. The first one becomes primary only if the
    contact had none before. `contact` needs phone_numbers and
    email_addresses loaded."""
    known_phones = {p.number for p in contact.phone_numbers}
    for number in phones:
        number = number.strip()
        if number and number not in known_phones:
            await add_phone(db, contact.id, number=number, is_primary=not known_phones)
            known_phones.add(number)
    known_emails = {e.address for e in contact.email_addresses}
    for address in emails:
        address = address.strip().lower()
        if address and address not in known_emails:
            await add_email(db, contact.id, address=address, is_primary=not known_emails)
            known_emails.add(address)


# ---------------------------------------------------------------------------
# Tags -- same rules as member tags (ADR 0093), separate pool.
# ---------------------------------------------------------------------------

TAG_NAME_MAX_LENGTH = 100


async def list_tags(db: AsyncSession) -> list[ExternalContactTag]:
    return list((await db.scalars(select(ExternalContactTag).order_by(func.lower(ExternalContactTag.name)))).all())


def _clean_tag_name(name: Optional[str]) -> str:
    name = " ".join((name or "").split())
    if not name:
        raise ServiceError("external_contacts.tags.errors.name_required")
    if len(name) > TAG_NAME_MAX_LENGTH:
        raise ServiceError("external_contacts.tags.errors.name_too_long", max=TAG_NAME_MAX_LENGTH)
    return name


async def _tag_by_name(db: AsyncSession, name: str) -> Optional[ExternalContactTag]:
    """By name or any of its translations, ignoring case (ADR 0098)."""
    return find_tag_by_name(await list_tags(db), name)


async def _get_or_create_tag(db: AsyncSession, name: str) -> ExternalContactTag:
    clean = _clean_tag_name(name)
    tag = await _tag_by_name(db, clean)
    if tag is None:
        tag = ExternalContactTag(name=clean)
        db.add(tag)
        await db.flush()
    return tag


async def tag_contact(
    db: AsyncSession, contact_id: str, *, tag_id: Optional[str] = None, name: Optional[str] = None,
) -> ExternalContactTag:
    """An existing tag by id, or by name (reused ignoring case, or
    created). Tagging twice is a no-op."""
    if tag_id:
        tag = await db.get(ExternalContactTag, tag_id)
        if tag is None:
            raise ServiceError("external_contacts.tags.errors.not_found", http_status=404)
    else:
        tag = await _get_or_create_tag(db, name)
    await db.execute(
        pg_insert(external_contact_tag_links).values(contact_id=contact_id, tag_id=tag.id).on_conflict_do_nothing()
    )
    await db.flush()
    return tag


async def set_contact_tags(
    db: AsyncSession, contact_id: str, *, tag_ids: list[str], new_names: str = "",
) -> None:
    """The form's tag section: exactly the ticked tags plus the typed
    new ones (comma-separated)."""
    wanted = {tag_id for tag_id in tag_ids if tag_id}
    for name in (new_names or "").split(","):
        if name.strip():
            wanted.add((await _get_or_create_tag(db, name)).id)
    existing = set((await db.scalars(
        select(external_contact_tag_links.c.tag_id).where(external_contact_tag_links.c.contact_id == contact_id)
    )).all())
    for tag_id in existing - wanted:
        await untag_contact(db, contact_id, tag_id)
    for tag_id in wanted - existing:
        await tag_contact(db, contact_id, tag_id=tag_id)


async def untag_contact(db: AsyncSession, contact_id: str, tag_id: str) -> bool:
    result = await db.execute(
        delete(external_contact_tag_links).where(
            external_contact_tag_links.c.contact_id == contact_id, external_contact_tag_links.c.tag_id == tag_id,
        )
    )
    await db.flush()
    return result.rowcount > 0


async def set_tag_translations(db: AsyncSession, tag: ExternalContactTag, values: dict) -> ExternalContactTag:
    """Per-language names (ADR 0098); an empty field removes that language."""
    tag.translations = clean_translations(
        tag, values, await list_tags(db), max_length=TAG_NAME_MAX_LENGTH, error_prefix="external_contacts.tags.errors",
    ) or None
    await db.flush()
    return tag


async def rename_tag(db: AsyncSession, tag: ExternalContactTag, name: str) -> ExternalContactTag:
    clean = _clean_tag_name(name)
    existing = await _tag_by_name(db, clean)
    if existing is not None and existing.id != tag.id:
        raise ServiceError("external_contacts.tags.errors.name_taken", http_status=409, name=existing.name)
    tag.name = clean
    await db.flush()
    return tag


async def delete_tag(db: AsyncSession, tag: ExternalContactTag) -> None:
    await db.delete(tag)
    await db.flush()


async def count_tag_contacts(db: AsyncSession) -> dict[str, int]:
    """Tag id -> how many non-deleted contacts carry it (tags page)."""
    rows = await db.execute(
        select(external_contact_tag_links.c.tag_id, func.count())
        .join(ExternalContact, ExternalContact.id == external_contact_tag_links.c.contact_id)
        .where(ExternalContact.deleted_at.is_(None))
        .group_by(external_contact_tag_links.c.tag_id)
    )
    return dict(rows.all())
