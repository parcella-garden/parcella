"""External contacts (companies and people), their tags, phones and e-mails."""

import enum
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Boolean, DateTime, Text, ForeignKey, Enum as SAEnum, Index, Column, Table, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func, text

from app.database import Base
from app.models._common import new_uuid


# ---------------------------------------------------------------------------
# External contacts (suppliers, craftsmen, authorities ...)
# ---------------------------------------------------------------------------

class ExternalContactKind(str, enum.Enum):
    COMPANY = "COMPANY"
    PERSON = "PERSON"


class ExternalContact(Base):
    """
    Someone the club deals with who isn't a member (see
    docs/module-external-contacts.md, ADR 0096). Deliberately its own
    table rather than a Member with a flag -- no parcels, work hours,
    invoices or email_info for anything to accidentally pull a contact
    into.

    Two kinds in one table (ADR 0110): a COMPANY (company_name, no
    person name) and a PERSON (first/last name, company_name always
    NULL), who may belong to one company via company_id. Phones, emails,
    tags, documents and the links from invoices/purchase requests work
    the same for both.

    Every field is optional, names included (migration 0098). Duplicates
    among non-deleted contacts, ignoring case: a given person name
    (first and/or last) is unique; a company name is unique. Enforced by
    the partial indexes uq_external_contacts_person and
    uq_external_contacts_company, checked up front in
    app/services/external_contacts.py for a readable error.
    """
    __tablename__ = "external_contacts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)

    kind: Mapped[ExternalContactKind] = mapped_column(
        SAEnum(ExternalContactKind), default=ExternalContactKind.COMPANY, nullable=False
    )
    # Companies only; a person's company is `company`.
    company_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    # Persons only: the company they work for, and their role there.
    company_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("external_contacts.id", ondelete="SET NULL"), nullable=True, index=True
    )
    position: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Company address; on a person only where it differs from the company's.
    street: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    postal_code: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    iban: Mapped[Optional[str]] = mapped_column(String(34), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Documents received from / sent to this contact: the name of one
    # subfolder of the club-wide base folder (ClubSetting
    # "external_contacts_cloud_folder", e.g. kgv_dokumente/extern) in the
    # connected cloud storage. The folders are created by hand in the
    # cloud and picked here; NULL = no documents folder. See ADR 0097.
    cloud_folder: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    phone_numbers: Mapped[List["ExternalContactPhone"]] = relationship(
        "ExternalContactPhone", back_populates="contact", cascade="all, delete-orphan"
    )
    email_addresses: Mapped[List["ExternalContactEmail"]] = relationship(
        "ExternalContactEmail", back_populates="contact", cascade="all, delete-orphan"
    )
    # Own tag pool, separate from MemberTag. Not lazy-loadable under
    # asyncio: selectinload(ExternalContact.tags) wherever it's read.
    tags: Mapped[List["ExternalContactTag"]] = relationship(
        "ExternalContactTag", secondary="external_contact_tag_links", back_populates="contacts",
        order_by="ExternalContactTag.name",
    )
    # lazy="selectin": display_name reads it, and contacts are shown from
    # many places (pickers, invoices, purchase requests, applicants) --
    # one forgotten selectinload would be a MissingGreenlet 500.
    # join_depth: a self-referential eager load doesn't happen at all
    # without one; 1 is enough, a company has no company.
    company: Mapped[Optional["ExternalContact"]] = relationship(
        "ExternalContact", remote_side=[id], back_populates="people", lazy="selectin", join_depth=1,
    )
    # Includes soft-deleted people -- see active_people.
    # selectinload(ExternalContact.people) wherever it's read.
    people: Mapped[List["ExternalContact"]] = relationship(
        "ExternalContact", back_populates="company",
        order_by="[ExternalContact.last_name, ExternalContact.first_name]",
    )

    __table_args__ = (
        Index(
            "uq_external_contacts_person",
            text("lower(coalesce(first_name, ''))"), text("lower(coalesce(last_name, ''))"), unique=True,
            postgresql_where=text("deleted_at IS NULL AND (first_name IS NOT NULL OR last_name IS NOT NULL)"),
        ),
        Index(
            "uq_external_contacts_company",
            text("lower(company_name)"), unique=True,
            postgresql_where=text(
                "deleted_at IS NULL AND first_name IS NULL AND last_name IS NULL AND company_name IS NOT NULL"
            ),
        ),
    )

    @property
    def is_company(self) -> bool:
        return self.kind == ExternalContactKind.COMPANY

    @property
    def has_person(self) -> bool:
        return bool(self.first_name or self.last_name)

    @property
    def organisation_name(self) -> Optional[str]:
        """A company's own name, or a person's company's name."""
        if self.is_company:
            return self.company_name
        return self.company.company_name if self.company is not None else None

    @property
    def active_people(self) -> List["ExternalContact"]:
        """Needs `people` loaded."""
        return [p for p in self.people if p.deleted_at is None]

    @property
    def full_name(self) -> str:
        """"First Last", or whichever part is set; "" without a person."""
        return " ".join(part for part in (self.first_name, self.last_name) if part)

    @property
    def sort_name(self) -> str:
        """"Last, First" for the list, or whichever part is set."""
        return ", ".join(part for part in (self.last_name, self.first_name) if part)

    @property
    def display_name(self) -> str:
        """A company's name; a person as "Company (First Last)", or just
        the name without a company. "" for a contact with neither --
        templates fall back to external_contacts.unnamed."""
        organisation = self.organisation_name
        if organisation and self.has_person:
            return f"{organisation} ({self.full_name})"
        return organisation or self.full_name

    def __repr__(self) -> str:
        return f"<ExternalContact {self.display_name}>"


class ExternalContactTag(Base):
    """A free-form label on external contacts -- same idea as MemberTag
    (ADR 0093), but its own pool: "supplier" or "electrician" has no
    business in the member tag filter."""
    __tablename__ = "external_contact_tags"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    # {language code: name shown in that language}, e.g. {"en": "red flag"}
    # for "Rote Liste" -- see app/tag_translations.py, ADR 0098.
    translations: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    contacts: Mapped[List["ExternalContact"]] = relationship(
        "ExternalContact", secondary="external_contact_tag_links", back_populates="tags"
    )

    def __repr__(self) -> str:
        return f"<ExternalContactTag {self.name}>"


external_contact_tag_links = Table(
    "external_contact_tag_links",
    Base.metadata,
    Column("contact_id", String(36), ForeignKey("external_contacts.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", String(36), ForeignKey("external_contact_tags.id", ondelete="CASCADE"), primary_key=True, index=True),
)


class ExternalContactPhone(Base):
    __tablename__ = "external_contact_phones"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    contact_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("external_contacts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    number: Mapped[str] = mapped_column(String(50), nullable=False)
    label: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    contact: Mapped["ExternalContact"] = relationship("ExternalContact", back_populates="phone_numbers")


class ExternalContactEmail(Base):
    __tablename__ = "external_contact_emails"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    contact_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("external_contacts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    label: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    contact: Mapped["ExternalContact"] = relationship("ExternalContact", back_populates="email_addresses")
