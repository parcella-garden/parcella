"""
The /contacts/ list filter as one value: search box and tag dropdown.
Shared by the list, its CSV export, the detail page's Previous/Next and
the REST API's list endpoint -- same idea as MemberListFilter
(app/member_filters.py), so they can't drift apart.

apply() is the flat list of matching contacts (API); apply_top_level()
the list page's rows: companies and persons without a company, where
the row itself or one of its people matches (ADR 0110).
"""
from dataclasses import dataclass
from urllib.parse import urlencode

from sqlalchemy import Select, func, or_, select

from app.models import ExternalContact, ExternalContactEmail, ExternalContactPhone, external_contact_tag_links


@dataclass(frozen=True)
class ContactListFilter:
    search: str = ""
    tag: str = ""  # ExternalContactTag.id, "" = any

    @classmethod
    def from_query(cls, search: str = "", tag: str = "") -> "ContactListFilter":
        return cls(search.strip(), tag.strip())

    def query_string(self) -> str:
        return urlencode({k: v for k, v in (("search", self.search), ("tag", self.tag)) if v})

    def apply(self) -> Select:
        query = (
            select(ExternalContact)
            .where(ExternalContact.deleted_at.is_(None))
            .order_by(
                ExternalContact.company_name.asc().nulls_last(),
                ExternalContact.last_name, ExternalContact.first_name,
            )
        )
        return self._filter(query)

    def apply_top_level(self) -> Select:
        query = (
            select(ExternalContact)
            .where(ExternalContact.deleted_at.is_(None), ExternalContact.company_id.is_(None))
            .order_by(
                func.lower(func.coalesce(
                    ExternalContact.company_name, ExternalContact.last_name, ExternalContact.first_name,
                )).asc().nulls_last(),
                ExternalContact.first_name,
            )
        )
        if not self.active:
            return query
        matches = self._filter(select(ExternalContact.id, ExternalContact.company_id).where(
            ExternalContact.deleted_at.is_(None)
        )).subquery()
        return query.where(or_(
            ExternalContact.id.in_(select(matches.c.id)),
            ExternalContact.id.in_(select(matches.c.company_id).where(matches.c.company_id.is_not(None))),
        ))

    @property
    def active(self) -> bool:
        return bool(self.search or self.tag)

    def _filter(self, query: Select) -> Select:
        if self.search:
            pattern = f"%{self.search}%"
            email_matches = select(ExternalContactEmail.contact_id).where(ExternalContactEmail.address.ilike(pattern))
            phone_matches = select(ExternalContactPhone.contact_id).where(ExternalContactPhone.number.ilike(pattern))
            query = query.where(or_(
                ExternalContact.company_name.ilike(pattern),
                ExternalContact.first_name.ilike(pattern),
                ExternalContact.last_name.ilike(pattern),
                ExternalContact.position.ilike(pattern),
                ExternalContact.street.ilike(pattern),
                ExternalContact.postal_code.ilike(pattern),
                ExternalContact.city.ilike(pattern),
                ExternalContact.iban.ilike(pattern),
                ExternalContact.notes.ilike(pattern),
                ExternalContact.id.in_(email_matches),
                ExternalContact.id.in_(phone_matches),
            ))
        if self.tag:
            query = query.where(ExternalContact.id.in_(
                select(external_contact_tag_links.c.contact_id).where(external_contact_tag_links.c.tag_id == self.tag)
            ))
        return query
