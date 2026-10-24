"""
Shared external-contact business logic, called by both
app/routers/external_contacts.py (HTML) and
app/routers/api_external_contacts.py (API) -- see ADR 0070.

A contact is a company or a person, and a person may belong to one
company (ADR 0110). The uniqueness rule, among non-deleted contacts and
ignoring case (ADR 0096): a given person name (first and/or last) is
unique, and so is a company name. Every field is optional. The partial
unique indexes uq_external_contacts_person / uq_external_contacts_company
are the safety net; check_duplicate_free() runs first so the user gets
a readable error instead of an IntegrityError.

Wherever a person comes with a company *name* (web form, CSV import,
API), resolve_company() links the company of that name, or creates it.

Tags work exactly like member tags (ADR 0093) but in their own pool.
"""
from datetime import datetime, timezone
from typing import Iterable, Optional

from sqlalchemy import delete, func, select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    ExternalContact, ExternalContactEmail, ExternalContactKind, ExternalContactPhone, ExternalContactTag,
    IncomingInvoice, PurchaseRequest, external_contact_tag_links,
)
from app.services.errors import ServiceError
from app.tag_translations import clean_translations, find_tag_by_name

STRING_FIELDS = (
    "company_name", "first_name", "last_name", "position", "street", "postal_code", "city", "iban", "notes",
)
ADDRESS_FIELDS = ("street", "postal_code", "city")


def _clean(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    value = value.strip()
    return value or None


def _lower(value: Optional[str]) -> Optional[str]:
    value = _clean(value)
    return value.lower() if value else None


def _kind_for(kind, first_name: Optional[str], last_name: Optional[str]) -> ExternalContactKind:
    """An explicit kind, else a person if a name is given -- so callers
    that predate the two kinds (old CSV files, API clients) keep working."""
    if kind:
        return ExternalContactKind(kind)
    return ExternalContactKind.PERSON if _clean(first_name) or _clean(last_name) else ExternalContactKind.COMPANY


async def find_duplicate(
    db: AsyncSession, *, first_name: Optional[str], last_name: Optional[str], company_name: Optional[str],
) -> Optional[ExternalContact]:
    """The non-deleted contact these values would duplicate, if any:
    the person of that name if one is given, otherwise the company of
    that name. None for a contact with neither."""
    first, last, company = _lower(first_name), _lower(last_name), _lower(company_name)
    query = select(ExternalContact).where(ExternalContact.deleted_at.is_(None))
    if first or last:
        query = query.where(
            func.lower(func.coalesce(ExternalContact.first_name, "")) == (first or ""),
            func.lower(func.coalesce(ExternalContact.last_name, "")) == (last or ""),
        )
    elif company:
        query = query.where(
            ExternalContact.kind == ExternalContactKind.COMPANY,
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
            name=existing.full_name, company=existing.organisation_name or "–",
        )
    raise ServiceError("external_contacts.errors.company_taken", http_status=409, company=existing.company_name)


async def resolve_company(db: AsyncSession, name: Optional[str]) -> Optional[ExternalContact]:
    """The non-deleted company of that name (ignoring case), created if
    there's none yet. None for an empty name."""
    if not _clean(name):
        return None
    company = await find_duplicate(db, first_name=None, last_name=None, company_name=name)
    if company is None:
        company = ExternalContact(kind=ExternalContactKind.COMPANY, company_name=_clean(name))
        db.add(company)
        await db.flush()
    return company


async def _company_or_error(db: AsyncSession, company_id: str) -> ExternalContact:
    company = await get_contact(db, company_id)
    if company is None or not company.is_company:
        raise ServiceError("external_contacts.errors.company_not_found", http_status=404)
    return company


def place_address_on_company(company: ExternalContact, values: dict) -> dict:
    """A new person's address and IBAN, entered together with the
    company (form, CSV row, API): they fill in what the company doesn't
    have yet; whatever equals the company's is dropped. Returns what's
    left for the person -- only a value that really differs."""
    values = dict(values)
    address = {f: _clean(values.get(f)) for f in ADDRESS_FIELDS}
    if any(address.values()):
        if not any(getattr(company, f) for f in ADDRESS_FIELDS):
            for f in ADDRESS_FIELDS:
                setattr(company, f, address[f])
        if all(getattr(company, f) == address[f] for f in ADDRESS_FIELDS):
            for f in ADDRESS_FIELDS:
                values[f] = None
    iban = _clean(values.get("iban"))
    if iban:
        if not company.iban:
            company.iban = iban
        if company.iban == iban:
            values["iban"] = None
    return values


async def get_contact(db: AsyncSession, contact_id: Optional[str]) -> Optional[ExternalContact]:
    """A non-deleted contact by id, or None -- for validating a picked
    contact on incoming invoices / purchase requests."""
    if not contact_id:
        return None
    return await db.scalar(
        select(ExternalContact).where(ExternalContact.id == contact_id, ExternalContact.deleted_at.is_(None))
    )


async def list_active_contacts(db: AsyncSession) -> list[ExternalContact]:
    """For the contact pickers on other modules' forms, in picker order:
    each company followed by its people, then the people without a
    company (see picker_groups())."""
    return list((await db.scalars(
        select(ExternalContact)
        .where(ExternalContact.deleted_at.is_(None))
        .order_by(func.lower(func.coalesce(ExternalContact.company_name, "")), ExternalContact.last_name, ExternalContact.first_name)
    )).all())


def picker_groups(contacts: list[ExternalContact]) -> list[tuple[ExternalContact, list[ExternalContact]]]:
    """(top-level contact, its people) pairs for a grouped picker:
    companies with their people, then persons without a company (with
    an empty list). A person whose company isn't in `contacts` is listed
    on its own."""
    ids = {c.id for c in contacts}
    people: dict[str, list[ExternalContact]] = {}
    for contact in contacts:
        if contact.company_id in ids:
            people.setdefault(contact.company_id, []).append(contact)
    groups = [(c, people.get(c.id, [])) for c in contacts if c.is_company]
    groups += [(c, []) for c in contacts if not c.is_company and c.company_id not in ids]
    return groups


async def create_contact(
    db: AsyncSession,
    *,
    kind: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    company_name: Optional[str] = None,
    company_id: Optional[str] = None,
    position: Optional[str] = None,
    street: Optional[str] = None,
    postal_code: Optional[str] = None,
    city: Optional[str] = None,
    iban: Optional[str] = None,
    notes: Optional[str] = None,
) -> ExternalContact:
    """For a person, company_name names its company (linked, or created
    by resolve_company()); company_id picks one directly and wins."""
    kind = _kind_for(kind, first_name, last_name)
    values = dict(street=street, postal_code=postal_code, city=city, iban=iban)
    if kind == ExternalContactKind.COMPANY:
        await check_duplicate_free(db, first_name=None, last_name=None, company_name=company_name)
        contact = ExternalContact(kind=kind, company_name=_clean(company_name))
    else:
        await check_duplicate_free(db, first_name=first_name, last_name=last_name, company_name=None)
        company = await _company_or_error(db, company_id) if company_id else await resolve_company(db, company_name)
        if company is not None:
            values = place_address_on_company(company, values)
        contact = ExternalContact(
            kind=kind, first_name=_clean(first_name), last_name=_clean(last_name), position=_clean(position),
            company=company,
        )
    for key, value in values.items():
        setattr(contact, key, _clean(value))
    contact.notes = _clean(notes)
    db.add(contact)
    await db.flush()
    return contact


async def update_contact(db: AsyncSession, contact: ExternalContact, **fields) -> ExternalContact:
    """Partial update: only keys present in `fields` are changed. The
    kind can't change. On a person, company_name re-links the company by
    name ("" unlinks), company_id by id; person names on a company and
    company_name on a person are ignored otherwise."""
    fields = {k: (_clean(v) if k in STRING_FIELDS and v is not None else v) for k, v in fields.items()}
    if fields.get("kind") and ExternalContactKind(fields["kind"]) != contact.kind:
        raise ServiceError("external_contacts.errors.kind_fixed", http_status=422)
    fields.pop("kind", None)
    if contact.is_company:
        for key in ("first_name", "last_name", "position", "company_id"):
            fields.pop(key, None)
        await check_duplicate_free(
            db, first_name=None, last_name=None,
            company_name=fields.get("company_name", contact.company_name), exclude_id=contact.id,
        )
    else:
        await check_duplicate_free(
            db, first_name=fields.get("first_name", contact.first_name),
            last_name=fields.get("last_name", contact.last_name), company_name=None, exclude_id=contact.id,
        )
        if fields.get("company_id"):
            contact.company = await _company_or_error(db, fields["company_id"])
        elif "company_id" in fields or "company_name" in fields:
            contact.company = await resolve_company(db, fields.get("company_name"))
        fields.pop("company_id", None)
        fields.pop("company_name", None)
    for key, value in fields.items():
        setattr(contact, key, value)
    await db.flush()
    return contact


async def soft_delete_contact(db: AsyncSession, contact: ExternalContact) -> None:
    """Sets deleted_at (ADR 0005) -- linked incoming invoices and
    purchase requests keep pointing at it. Frees the name for reuse. A
    company with people left is refused: move or delete them first."""
    if contact.is_company and await db.scalar(
        select(func.count()).select_from(ExternalContact)
        .where(ExternalContact.company_id == contact.id, ExternalContact.deleted_at.is_(None))
    ):
        raise ServiceError("external_contacts.errors.company_has_people", http_status=409)
    contact.deleted_at = datetime.now(timezone.utc)
    await db.flush()


async def merge_companies(db: AsyncSession, source: ExternalContact, target: ExternalContact) -> None:
    """Folds `source` into `target` (two spellings of one firm): people,
    phones, emails, tags and the links from incoming invoices and
    purchase requests move over; address, IBAN, documents folder and
    notes fill in where the target has none. `source` is soft-deleted."""
    if not (source.is_company and target.is_company) or source.id == target.id or target.deleted_at:
        raise ServiceError("external_contacts.errors.merge_invalid", http_status=422)
    for model, column in (
        (ExternalContact, ExternalContact.company_id),
        (ExternalContactPhone, ExternalContactPhone.contact_id),
        (ExternalContactEmail, ExternalContactEmail.contact_id),
        (IncomingInvoice, IncomingInvoice.external_contact_id),
        (PurchaseRequest, PurchaseRequest.external_contact_id),
    ):
        await db.execute(update(model).where(column == source.id).values({column.key: target.id}))
    tag_ids = (await db.scalars(
        select(external_contact_tag_links.c.tag_id).where(external_contact_tag_links.c.contact_id == source.id)
    )).all()
    for tag_id in tag_ids:
        await tag_contact(db, target.id, tag_id=tag_id)
    await db.execute(delete(external_contact_tag_links).where(external_contact_tag_links.c.contact_id == source.id))
    if not any(getattr(target, f) for f in ADDRESS_FIELDS):
        for f in ADDRESS_FIELDS:
            setattr(target, f, getattr(source, f))
    for f in ("iban", "cloud_folder"):
        if not getattr(target, f):
            setattr(target, f, getattr(source, f))
    if source.notes:
        target.notes = f"{target.notes}\n\n{source.notes}" if target.notes else source.notes
    source.deleted_at = datetime.now(timezone.utc)
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
