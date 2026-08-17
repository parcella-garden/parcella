"""
Shared parcel business logic, called by both app/routers/parcels.py
(HTML) and app/routers/api_parcels.py (API) -- see ADR 0070.

Closes the audit-trail gap ADR 0070's own tickets pilot found in its
most severe form (API-driven parcel edits, including status/termination
changes, previously wrote no ChangeHistory row at all -- only the HTML
side did). Auditing this module also turned up three further, real
divergences beyond that headline finding, all fixed here rather than
left as-is, since they're exactly the class of bug this initiative
exists to find:

1. Plot-number uniqueness was only checked on CREATE on the HTML side
   (its edit form let two parcels silently end up with the same plot
   number) and on both CREATE and UPDATE on the API side (409, hard-
   coded English) -- now checked on both operations, both surfaces,
   sharing one i18n'd message.
2. A former (ended) tenant assignment could be reactivated by
   reassigning them to the same parcel via the HTML UI, but the API
   treated ANY existing row (active or historical) as a 409 conflict --
   a former tenant could never be reassigned to the same parcel via the
   API at all. Both now reactivate.
3. The "a former tenant can never be the invoice address" rule (issue
   #172) was applied on assignment UPDATE and API's assignment CREATE,
   but not on the HTML CREATE path -- closed by applying it uniformly
   in assign_member() below.

Also: the API's single DELETE /assignments/{id} endpoint used to hard-
delete unconditionally, including an *active* assignment -- silently
discarding tenancy history the HTML side deliberately protects (it only
ever hard-deletes an already-ended assignment, via a separate, more
narrowly-permissioned action; ending an active one only ever soft-ends
it). The API's delete now routes through the same two functions
(end_assignment/delete_assignment_history) and picks between them based
on the assignment's current state, closing that data-loss risk without
changing the endpoint's URL/method contract.
"""
from datetime import date
from typing import Optional, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.change_tracker import ChangeTracker
from app.models import MemberParcel, Parcel, ParcelStatus, User
from app.services.errors import ServiceError

_TRACKED_FIELDS = ["plot_number", "area_sqm", "latitude", "longitude", "status", "termination_note", "notes"]


async def _plot_number_taken(db: AsyncSession, plot_number: str, *, exclude_parcel_id: Optional[str] = None) -> bool:
    query = select(Parcel).where(Parcel.plot_number == plot_number)
    if exclude_parcel_id:
        query = query.where(Parcel.id != exclude_parcel_id)
    result = await db.execute(query)
    return result.scalar_one_or_none() is not None


def _validate_coordinates(latitude: Optional[float], longitude: Optional[float]) -> None:
    if latitude is not None and not (-90 <= latitude <= 90):
        raise ServiceError("parcels.form.invalid_coordinates_error", http_status=400)
    if longitude is not None and not (-180 <= longitude <= 180):
        raise ServiceError("parcels.form.invalid_coordinates_error", http_status=400)


async def create_parcel(
    db: AsyncSession, *, plot_number: str, area_sqm: Optional[float] = None,
    latitude: Optional[float] = None, longitude: Optional[float] = None,
    notes: Optional[str] = None,
) -> Parcel:
    plot_number = plot_number.strip().upper()
    if await _plot_number_taken(db, plot_number):
        raise ServiceError("parcels.form.duplicate_plot_number_error", http_status=400, plot_number=plot_number)
    _validate_coordinates(latitude, longitude)

    parcel = Parcel(
        plot_number=plot_number, area_sqm=area_sqm, latitude=latitude, longitude=longitude,
        notes=(notes or "").strip() or None,
    )
    db.add(parcel)
    await db.flush()
    return parcel


async def update_parcel(db: AsyncSession, parcel: Parcel, *, acting_user: User, **fields) -> Parcel:
    """Partial update -- only keys present in `fields` are changed.
    Writes the ChangeHistory audit trail unconditionally regardless of
    caller (ADR 0070's headline fix for this module)."""
    if "plot_number" in fields and fields["plot_number"] is not None:
        new_number = fields["plot_number"].strip().upper()
        if new_number != parcel.plot_number and await _plot_number_taken(db, new_number, exclude_parcel_id=parcel.id):
            raise ServiceError("parcels.form.duplicate_plot_number_error", http_status=400, plot_number=new_number)
        fields["plot_number"] = new_number

    if "notes" in fields:
        fields["notes"] = (fields["notes"] or "").strip() or None
    if "termination_note" in fields:
        fields["termination_note"] = (fields["termination_note"] or "").strip() or None
    if "latitude" in fields or "longitude" in fields:
        _validate_coordinates(
            fields.get("latitude", parcel.latitude), fields.get("longitude", parcel.longitude),
        )

    tracker = ChangeTracker(parcel, "Parcel", _TRACKED_FIELDS)
    for key, value in fields.items():
        if key in _TRACKED_FIELDS:
            setattr(parcel, key, value)

    await tracker.commit(db, acting_user.id)
    await db.flush()
    return parcel


async def assign_member(
    db: AsyncSession, parcel_id: str, member_id: str, *,
    is_invoice_address: bool, assigned_from: Optional[date] = None, assigned_until: Optional[date] = None,
) -> Tuple[MemberParcel, bool]:
    """Reactivates a former (ended) assignment for this member/parcel
    pair instead of creating a duplicate row, if one already exists --
    even a historical one (see module docstring, point 2). Returns
    (assignment, created)."""
    result = await db.execute(
        select(MemberParcel).where(MemberParcel.parcel_id == parcel_id, MemberParcel.member_id == member_id)
    )
    assignment = result.scalar_one_or_none()

    if assignment is not None and assignment.assigned_until is None:
        return assignment, False  # already actively assigned, nothing to do

    created = assignment is None
    if created:
        # Brand-new assignment: an unspecified start date stays NULL
        # (no defined start date), same as before this extraction.
        assignment = MemberParcel(parcel_id=parcel_id, member_id=member_id, assigned_from=assigned_from)
        db.add(assignment)
    else:
        # Reactivating a former assignment: default to today if no date
        # given, rather than leaving the old (now-stale) start date.
        assignment.assigned_from = assigned_from or date.today()
    assignment.assigned_until = assigned_until
    # A former tenant can never be the invoice address -- but a future-
    # dated assigned_until (notice given, not yet moved out -- ADR 0052)
    # doesn't make them former yet (issue #172).
    assignment.is_invoice_address = is_invoice_address if assignment.is_current else False

    await db.flush()
    return assignment, created


async def update_assignment(
    db: AsyncSession, assignment: MemberParcel, *,
    is_invoice_address: bool, assigned_from: Optional[date], assigned_until: Optional[date],
) -> MemberParcel:
    """Caller is responsible for calling deactivate_if_vacant()
    afterward -- see end_assignment()'s docstring for why."""
    assignment.assigned_from = assigned_from
    assignment.assigned_until = assigned_until
    assignment.is_invoice_address = is_invoice_address if assignment.is_current else False
    await db.flush()
    return assignment


async def end_assignment(db: AsyncSession, assignment: MemberParcel) -> bool:
    """Ends a tenant assignment (sets assigned_until), but does NOT
    delete it -- history stays intact. Returns False (no-op) if it was
    already ended. Caller is responsible for calling
    app.parcel_cloud_folders.deactivate_if_vacant() afterward (it does
    its own internal commit, so it can't run inside this flush-only
    service -- see that module for why)."""
    if assignment.assigned_until is not None:
        return False
    assignment.assigned_until = date.today()
    assignment.is_invoice_address = False
    await db.flush()
    return True


async def delete_assignment_history(db: AsyncSession, assignment: MemberParcel) -> None:
    """Fully deletes an already-ended tenant entry. Raises ServiceError
    if the assignment is still active -- it must be ended via
    end_assignment() first, so this can't be used as a bypass for that."""
    if assignment.assigned_until is None:
        raise ServiceError("parcels.detail.cannot_delete_active_assignment", http_status=400)
    await db.delete(assignment)
    await db.flush()


async def remove_assignment(db: AsyncSession, assignment: MemberParcel) -> None:
    """API's single DELETE endpoint: ends an active assignment (soft),
    hard-deletes an already-ended one -- picks the safe behavior based
    on current state instead of always hard-deleting (see module
    docstring). Caller is responsible for calling
    deactivate_if_vacant() afterward if this ended (rather than
    deleted) the assignment."""
    if assignment.assigned_until is None:
        await end_assignment(db, assignment)
    else:
        await delete_assignment_history(db, assignment)
