"""
Handing a terminated parcel over to applicants (ADR 0101): the old
tenants become former tenants, the applicants become members and the
parcel's new tenants and invoice recipients, the parcel is ACTIVE
again and the applications are ACCEPTED -- one transaction, called by
both app/routers/applicants.py (HTML) and app/routers/api_applicants.py
(API), same split as ADR 0070.

Dates, for a handover date D:
- old tenancies end on D (assigned_until = D -- former from D on,
  same strict ">" as MemberParcel.is_current);
- an old tenant who holds no other current parcel leaves the club:
  member_until = D - 1 day, their last day as a member (member_until is
  inclusive, Member.is_active uses ">=");
- new tenancies and memberships start on D.
D may lie in the future (ADR 0102): the old tenants stay current tenants,
members and invoice recipients until D, the new ones are upcoming until
then and take over on D -- MemberParcel.is_current checks both dates.
"""
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from typing import Optional, Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.change_tracker import ChangeTracker
from app.database import active_member_filter
from app.models import (
    APPLICANT_OPEN_STATUSES, Applicant, ApplicantStatus, Member, MemberEmail, MemberParcel,
    Parcel, ParcelCloudFolder, ParcelStatus, User,
)
from app.parcel_cloud_folders import (
    InvalidCloudPathError, get_active_folder, sanitize_relative_path, schedule_handover_folders,
)
from app.services.errors import ServiceError
from app.services.members import add_email, add_phone, create_member
from app.services.parcels import assign_member, update_parcel


@dataclass
class OutgoingTenant:
    assignment: MemberParcel
    # Plot numbers of the other parcels this member still holds after
    # the handover -- empty means their membership ends.
    other_parcels: list[str] = field(default_factory=list)

    @property
    def membership_ends(self) -> bool:
        return not self.other_parcels


@dataclass
class IncomingTenant:
    applicant: Applicant
    # An active member with the applicant's email address (e.g. a
    # member applying for a bigger plot) is reused instead of creating
    # a duplicate.
    existing_member: Optional[Member] = None


@dataclass
class HandoverPlan:
    parcel: Parcel
    handover_date: date
    outgoing: list[OutgoingTenant]
    incoming: list[IncomingTenant]
    # The old tenants' documents folder (retired on the handover date)
    # and the one picked for the new tenants, if any (ADR 0102).
    current_folder: Optional[ParcelCloudFolder] = None
    new_folder_path: Optional[str] = None

    @property
    def last_member_day(self) -> date:
        """An outgoing tenant's last day as a member, if their membership ends."""
        return self.handover_date - timedelta(days=1)


async def terminated_parcels(db: AsyncSession) -> list[Parcel]:
    """The parcels a handover can start from, with their tenants."""
    result = await db.execute(
        select(Parcel)
        .options(selectinload(Parcel.member_assignments).selectinload(MemberParcel.member))
        .where(Parcel.status == ParcelStatus.TERMINATED)
        .order_by(Parcel.plot_number)
    )
    return list(result.scalars().all())


def _ends_on_or_after(assignment: MemberParcel, day: date) -> bool:
    """Still a tenant on `day`, i.e. the handover cuts this tenancy short."""
    return assignment.assigned_until is None or assignment.assigned_until > day


async def _member_by_email(db: AsyncSession, email: str) -> Optional[Member]:
    result = await db.execute(
        select(Member)
        .join(MemberEmail, MemberEmail.member_id == Member.id)
        .where(func.lower(MemberEmail.address) == email.lower(), active_member_filter())
        .order_by(Member.created_at)
        .limit(1)
    )
    return result.scalar_one_or_none()


async def plan_handover(
    db: AsyncSession, *, parcel_id: str, applicant_ids: Sequence[str], handover_date: date,
    new_folder_path: Optional[str] = None,
) -> HandoverPlan:
    """Validates and works out what hand_over_parcel() will do, without
    changing anything -- the HTML form shows this as its preview.
    `applicant_ids[0]` is the applicant the handover started from; the
    rest become co-tenants. `new_folder_path` is the new tenants' cloud
    folder -- the caller only passes it for a user allowed to manage
    cloud folders."""
    if new_folder_path and new_folder_path.strip():
        try:
            new_folder_path = sanitize_relative_path(new_folder_path)
        except InvalidCloudPathError:
            raise ServiceError("applicants.handover.errors.invalid_folder_path", http_status=400)
    else:
        new_folder_path = None
    result = await db.execute(
        select(Parcel)
        .options(selectinload(Parcel.member_assignments).selectinload(MemberParcel.member))
        .where(Parcel.id == parcel_id)
    )
    parcel = result.scalar_one_or_none()
    if parcel is None:
        raise ServiceError("applicants.handover.errors.parcel_not_found", http_status=404)
    if parcel.status != ParcelStatus.TERMINATED:
        raise ServiceError("applicants.handover.errors.parcel_not_terminated", http_status=400, plot_number=parcel.plot_number)

    unique_ids = list(dict.fromkeys(applicant_ids))
    result = await db.execute(select(Applicant).where(Applicant.id.in_(unique_ids)))
    by_id = {a.id: a for a in result.scalars().all()}
    if not unique_ids or len(by_id) != len(unique_ids):
        raise ServiceError("applicants.handover.errors.applicant_not_found", http_status=404)

    incoming = []
    for applicant_id in unique_ids:
        applicant = by_id[applicant_id]
        if applicant.status not in APPLICANT_OPEN_STATUSES:
            raise ServiceError("applicants.handover.errors.applicant_closed", http_status=400, name=applicant.display_name)
        if not (applicant.first_name or "").strip() or not (applicant.last_name or "").strip():
            raise ServiceError("applicants.handover.errors.name_missing", http_status=400, name=applicant.display_name)
        incoming.append(IncomingTenant(applicant, await _member_by_email(db, applicant.email)))

    incoming_member_ids = {t.existing_member.id for t in incoming if t.existing_member}
    outgoing = []
    for assignment in parcel.member_assignments:
        if not _ends_on_or_after(assignment, handover_date):
            continue
        if assignment.member_id in incoming_member_ids:
            # Already a tenant here and also one of the applicants --
            # they simply stay.
            continue
        result = await db.execute(
            select(Parcel.plot_number)
            .join(MemberParcel, MemberParcel.parcel_id == Parcel.id)
            .where(
                MemberParcel.member_id == assignment.member_id,
                MemberParcel.parcel_id != parcel.id,
                (MemberParcel.assigned_until.is_(None)) | (MemberParcel.assigned_until > handover_date),
            )
            .order_by(Parcel.plot_number)
        )
        outgoing.append(OutgoingTenant(assignment, list(result.scalars().all())))
    outgoing.sort(key=lambda t: (t.assignment.member.last_name, t.assignment.member.first_name))

    return HandoverPlan(
        parcel=parcel, handover_date=handover_date, outgoing=outgoing, incoming=incoming,
        current_folder=await get_active_folder(db, parcel.id), new_folder_path=new_folder_path,
    )


async def hand_over_parcel(db: AsyncSession, plan: HandoverPlan, *, acting_user: User) -> list[Member]:
    """Carries out a plan from plan_handover() and commits. Returns the
    parcel's new tenants (members)."""
    day = plan.handover_date

    for tenant in plan.outgoing:
        tenant.assignment.assigned_until = day
        # Still billed until they actually leave (ADR 0058) -- read paths
        # check is_current, so the flag stops mattering on D by itself.
        tenant.assignment.is_invoice_address = tenant.assignment.is_invoice_address and not tenant.assignment.is_former
        member = tenant.assignment.member
        if tenant.membership_ends and (member.member_until is None or member.member_until > plan.last_member_day):
            member.member_until = plan.last_member_day

    new_tenants = []
    for tenant in plan.incoming:
        applicant = tenant.applicant
        member = tenant.existing_member
        if member is None:
            member = await create_member(
                db, first_name=applicant.first_name, last_name=applicant.last_name, member_since=day,
            )
            await add_email(db, member.id, address=applicant.email, is_primary=True)
            if applicant.phone:
                await add_phone(db, member.id, number=applicant.phone, is_primary=True)
        staying = next(
            (a for a in plan.parcel.member_assignments
             if a.member_id == member.id and _ends_on_or_after(a, day)),
            None,
        )
        if staying is not None:
            # Already a tenant here (left out of `outgoing`): keep the
            # tenancy and its start date, just withdraw a pending notice.
            staying.assigned_until = None
            staying.is_invoice_address = True
        else:
            await assign_member(db, plan.parcel.id, member.id, is_invoice_address=True, assigned_from=day)
        new_tenants.append(member)

        tracker = ChangeTracker(applicant, "Applicant", ["status"])
        if applicant.status != ApplicantStatus.ACCEPTED:
            applicant.status = ApplicantStatus.ACCEPTED
            applicant.status_changed_at = datetime.now(timezone.utc)
        await tracker.commit(db, acting_user.id)

    # Never vacant in between, so deactivate_if_vacant() can't catch this
    # turnover -- the new tenants must not inherit the old folder.
    await schedule_handover_folders(
        db, plan.parcel.id, handover_date=day,
        new_relative_path=plan.new_folder_path, set_by_user_id=acting_user.id,
    )
    await update_parcel(db, plan.parcel, acting_user=acting_user, status=ParcelStatus.ACTIVE)
    await db.commit()
    return new_tenants
