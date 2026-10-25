"""
The /members/ list filter as one value (issue #241): the search box,
the three checkboxes and the tag dropdown.

Before, those five loose parameters were repeated in every place that
needs "the members currently on screen" -- the list, its CSV export
(issue #198), the detail page's Previous/Next (issue #202, ADR 0075)
and the list's query string -- and each new filter had to be threaded
through all of them by hand. They now all take a MemberListFilter.
Announcements to filtered members (issue #242) store one as JSON
(to_dict/from_dict) and resolve it to recipients with the same apply().
"""
from dataclasses import asdict, dataclass, fields
from datetime import date
from typing import Optional
from urllib.parse import urlencode

from sqlalchemy import Select, and_, or_, select

from app.database import active_member_filter, current_tenant_filter
from app.models import Member, MemberEmail, MemberParcel, MemberPhone, Parcel, member_tag_links


def has_tag_condition(tag_id: str):
    """WHERE clause "member carries this tag" -- shared by the list
    filter below and the REST API's ?tag=."""
    return Member.id.in_(select(member_tag_links.c.member_id).where(member_tag_links.c.tag_id == tag_id))


@dataclass(frozen=True)
class MemberListFilter:
    search: str = ""
    include_inactive: bool = False
    active_only: bool = False
    email_info_only: bool = False
    tag: str = ""  # MemberTag.id, "" = any

    @classmethod
    def from_query(
        cls,
        search: str = "",
        include_inactive: bool = False,
        active_only: bool = False,
        email_info_only: bool = False,
        tag: str = "",
    ) -> "MemberListFilter":
        """FastAPI dependency: `filters: MemberListFilter = Depends(MemberListFilter.from_query)`."""
        return cls(search.strip(), include_inactive, active_only, email_info_only, tag.strip())

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Optional[dict]) -> "MemberListFilter":
        """Ignores unknown keys, so a stored filter survives a field
        being dropped later."""
        known = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in (data or {}).items() if k in known})

    def is_empty(self) -> bool:
        return self == MemberListFilter()

    def query_string(self) -> str:
        """The filter as a query string (no leading '?', empty if
        nothing is set). Issue #202: carried from each list row onto
        its detail page, and back out again via the detail page's
        Previous/Next buttons, so paging through a filtered view (e.g.
        inactive members) doesn't silently fall back to the full,
        unfiltered member list."""
        params = {}
        for f in fields(self):
            value = getattr(self, f.name)
            if value is True:
                params[f.name] = "true"
            elif value:
                params[f.name] = value
        return urlencode(params)

    def apply(self) -> Select:
        """WHERE/ORDER BY for the member list, shared with its CSV export
        (issue #198) so an export always matches what's currently on
        screen instead of drifting into its own copy of this filtering
        logic. Callers still add their own `.options(...)` eager-loads,
        since the list and the export don't need exactly the same
        relationships."""
        # The "pending applications" view (issue #167) was removed in
        # issue #256: applications live in the applicants module now.
        query = select(Member).order_by(Member.last_name, Member.first_name)
        if self.include_inactive:
            # Issue #169: this must show ONLY inactive members (expired
            # OR not-yet-started), not every non-deleted member
            # regardless of status -- previously this was the plain
            # complement of active_member_filter() done wrong (just
            # deleted_at IS NULL), which meant active members showed up
            # here too. The actual complement of active_member_filter()
            # is an OR (a member is inactive if EITHER half fails), not
            # an AND. A blank member_since is still "active" per
            # active_member_filter() itself, unchanged.
            query = query.where(
                Member.deleted_at.is_(None),
                or_(
                    and_(Member.member_since.is_not(None), Member.member_since > date.today()),
                    and_(Member.member_until.is_not(None), Member.member_until < date.today()),
                ),
            )
        elif self.active_only:
            # Issue #200: active_member_filter() alone still counts a
            # blank member_since as active (deliberate, issue #167 --
            # keeps invoices/sign-in/dashboard totals unaffected for
            # pre-existing members without the field set). The list's
            # own status badge already treats that same blank case as
            # "pending" for display (issue #170). This filter makes the
            # two agree: a member only counts as active_only if they
            # also have a confirmed member_since, i.e. exactly the rows
            # that render the "active" (not "pending") badge.
            query = query.where(active_member_filter(), Member.member_since.is_not(None))
        else:
            query = query.where(active_member_filter())

        if self.search:
            # Searches every text field of the member (name, address, IBAN,
            # notes -- so a FreeScout ticket number noted down there finds
            # the member), plus parcel number, email and phone.
            # For the parcel search: by default only current assignments (who
            # lives there NOW); with "include_inactive" also already-ended
            # assignments (who used to live there) -- the same toggle logic as
            # for active/inactive members, just applied to the parcel's tenant
            # history.
            parcel_condition = Parcel.plot_number.ilike(f"%{self.search}%")
            if not self.include_inactive:
                parcel_condition = and_(
                    parcel_condition, current_tenant_filter()
                )
            parcel_matches = (
                select(MemberParcel.member_id)
                .join(Parcel, MemberParcel.parcel_id == Parcel.id)
                .where(parcel_condition)
            )
            # Matches any of a member's emails/phones (both are one-to-many,
            # app/models.py), not just the primary one -- same "find this
            # member no matter which record matches" logic as parcel number
            # above. No phone-number normalization (no precedent for that
            # anywhere in this app) -- a plain substring match, same as
            # everything else here.
            email_matches = select(MemberEmail.member_id).where(MemberEmail.address.ilike(f"%{self.search}%"))
            phone_matches = select(MemberPhone.member_id).where(MemberPhone.number.ilike(f"%{self.search}%"))
            query = query.where(
                or_(
                    Member.first_name.ilike(f"%{self.search}%"),
                    Member.last_name.ilike(f"%{self.search}%"),
                    Member.street.ilike(f"%{self.search}%"),
                    Member.postal_code.ilike(f"%{self.search}%"),
                    Member.city.ilike(f"%{self.search}%"),
                    Member.iban.ilike(f"%{self.search}%"),
                    Member.notes.ilike(f"%{self.search}%"),
                    Member.id.in_(parcel_matches),
                    Member.id.in_(email_matches),
                    Member.id.in_(phone_matches),
                )
            )

        if self.email_info_only:
            query = query.where(Member.email_notifications.is_(True))


        if self.tag:
            query = query.where(has_tag_condition(self.tag))

        return query
