"""Sponsorships."""
from fastapi import APIRouter
from datetime import date
from typing import Optional
from fastapi import Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, or_, select
from sqlalchemy.orm import selectinload
from app.database import active_member_filter, get_db
from app.models import Member, MemberParcel, Sponsorship
from app.permissions import require_permission
from app.i18n import t_for
from app.services.work_hours import (
    SponsorshipDatesError,
    create_sponsorship,
    get_config_for_year,
    update_sponsorship,
    sort_members_by_plot,
)
from app.templating import templates

router = APIRouter()


@router.get("/sponsorships", response_class=HTMLResponse)
async def sponsorships_page(
    request: Request,
    year: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
):
    user = await require_permission(request, db, "work_hours", "read")
    return await _render_sponsorships_page(request, db, user, year or date.today().year)


async def _render_sponsorships_page(
    request: Request, db: AsyncSession, user, year: int, *,
    error: Optional[str] = None, entered: Optional[dict] = None,
):
    query = (
        select(Sponsorship)
        .options(selectinload(Sponsorship.member))
        .where(
            or_(
                # Not yet claimed (no start date set) -- a standing offer,
                # shown regardless of which year is selected.
                Sponsorship.valid_from.is_(None),
                and_(
                    Sponsorship.valid_from <= date(year, 12, 31),
                    or_(Sponsorship.valid_until.is_(None), Sponsorship.valid_until >= date(year, 1, 1)),
                ),
            ),
            # Anything that has already ended as of today belongs in the
            # "Former Sponsorships" table below, not here -- otherwise a
            # sponsorship that ended earlier this calendar year would show
            # in both tables at once when viewing the current year.
            or_(Sponsorship.valid_until.is_(None), Sponsorship.valid_until >= date.today()),
        )
        .order_by(Sponsorship.area)
    )
    result = await db.execute(query)
    sponsorships = result.scalars().all()

    # Group by area, so multiple members per area are shown together
    grouped_areas = {}
    for p in sponsorships:
        grouped_areas.setdefault(p.area, []).append(p)

    # Former sponsorships: a permanent record of anything that has
    # actually ended, independent of the year selected above.
    former_result = await db.execute(
        select(Sponsorship)
        .options(selectinload(Sponsorship.member))
        .where(Sponsorship.valid_until.is_not(None), Sponsorship.valid_until < date.today())
        .order_by(Sponsorship.valid_until.desc(), Sponsorship.area)
    )
    former_sponsorships = former_result.scalars().all()

    # All known area names (for autocomplete, including past years, to
    # avoid typos when reusing one)
    all_areas_result = await db.execute(
        select(Sponsorship.area).distinct().order_by(Sponsorship.area)
    )
    all_areas = [r[0] for r in all_areas_result.all()]

    # Current work-hours configuration, for pre-filling
    config = await get_config_for_year(db, year)

    members_result = await db.execute(
        select(Member)
        .options(selectinload(Member.parcel_assignments).selectinload(MemberParcel.parcel))
        .where(active_member_filter())
        .order_by(Member.last_name, Member.first_name)
    )
    all_members = sort_members_by_plot(members_result.scalars().all())

    return templates.TemplateResponse(
        request, "work_hours/sponsorships.html",
        {
            "request": request,
            "user": user,
            "sponsorships": sponsorships,
            "grouped_areas": grouped_areas,
            "former_sponsorships": former_sponsorships,
            "all_areas": all_areas,
            "config": config,
            "all_members": all_members,
            "year": year,
            "error": error,
            "entered": entered,
        },
        status_code=400 if error else 200,
    )


@router.post("/sponsorships/new")
async def sponsorship_create(
    request: Request,
    member_id: str = Form(""),
    area: str = Form(...),
    description: str = Form(""),
    credited_hours: str = Form(...),
    valid_from: str = Form(""),
    valid_until: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    user = await require_permission(request, db, "work_hours", "write")

    try:
        await create_sponsorship(
            db, member_id=member_id, area=area, description=description,
            credited_hours=float(credited_hours.replace(",", ".")),
            valid_from=(date.fromisoformat(valid_from) if valid_from.strip() else None),
            valid_until=(date.fromisoformat(valid_until) if valid_until.strip() else None),
        )
    except SponsorshipDatesError as e:
        # Show the form again with what was typed, instead of losing it.
        entered = dict(
            member_id=member_id, area=area, description=description,
            credited_hours=credited_hours, valid_from=valid_from, valid_until=valid_until,
        )
        return await _render_sponsorships_page(
            request, db, user, date.today().year, error=str(e), entered=entered,
        )
    await db.commit()
    return RedirectResponse("/work-hours/sponsorships", status_code=302)


@router.get("/sponsorships/{sponsorship_id}/edit", response_class=HTMLResponse)
async def sponsorship_edit_page(
    sponsorship_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user = await require_permission(request, db, "work_hours", "write")

    result = await db.execute(
        select(Sponsorship)
        .options(selectinload(Sponsorship.member))
        .where(Sponsorship.id == sponsorship_id)
    )
    sponsorship = result.scalar_one_or_none()
    if not sponsorship:
        raise HTTPException(status_code=404, detail=t_for(request, "work_hours.errors.sponsorship_not_found"))

    return await _render_sponsorship_form(request, db, user, sponsorship)


async def _render_sponsorship_form(
    request: Request, db: AsyncSession, user, sponsorship: Sponsorship, *,
    error: Optional[str] = None, entered: Optional[dict] = None,
):
    members_result = await db.execute(
        select(Member)
        .options(selectinload(Member.parcel_assignments).selectinload(MemberParcel.parcel))
        .where(active_member_filter())
        .order_by(Member.last_name, Member.first_name)
    )
    all_members = sort_members_by_plot(members_result.scalars().all())

    all_areas_result = await db.execute(
        select(Sponsorship.area).distinct().order_by(Sponsorship.area)
    )
    all_areas = [r[0] for r in all_areas_result.all()]

    return templates.TemplateResponse(
        request, "work_hours/sponsorship_form.html",
        {
            "request": request,
            "user": user,
            "sponsorship": sponsorship,
            "all_members": all_members,
            "all_areas": all_areas,
            "error": error,
            "entered": entered,
        },
        status_code=400 if error else 200,
    )


@router.post("/sponsorships/{sponsorship_id}/edit")
async def sponsorship_update(
    sponsorship_id: str,
    request: Request,
    member_id: str = Form(""),
    area: str = Form(...),
    description: str = Form(""),
    credited_hours: str = Form(...),
    valid_from: str = Form(""),
    valid_until: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    user = await require_permission(request, db, "work_hours", "write")

    result = await db.execute(select(Sponsorship).where(Sponsorship.id == sponsorship_id))
    sponsorship = result.scalar_one_or_none()
    if not sponsorship:
        raise HTTPException(status_code=404, detail=t_for(request, "work_hours.errors.sponsorship_not_found"))

    try:
        await update_sponsorship(
            db, sponsorship,
            member_id=member_id, area=area, description=description,
            credited_hours=float(credited_hours.replace(",", ".")),
            valid_from=(date.fromisoformat(valid_from) if valid_from.strip() else None),
            valid_until=(date.fromisoformat(valid_until) if valid_until.strip() else None),
        )
    except SponsorshipDatesError as e:
        # Show the form again with what was typed, instead of losing it.
        entered = dict(
            member_id=member_id, area=area, description=description,
            credited_hours=credited_hours, valid_from=valid_from, valid_until=valid_until,
        )
        return await _render_sponsorship_form(request, db, user, sponsorship, error=str(e), entered=entered)

    await db.commit()

    if sponsorship.valid_from:
        year = sponsorship.valid_from.year
    elif sponsorship.valid_until:
        year = sponsorship.valid_until.year
    else:
        year = date.today().year
    return RedirectResponse(f"/work-hours/sponsorships?year={year}", status_code=302)


@router.post("/sponsorships/{sponsorship_id}/delete")
async def sponsorship_delete(
    sponsorship_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    await require_permission(request, db, "work_hours", "delete")
    result = await db.execute(select(Sponsorship).where(Sponsorship.id == sponsorship_id))
    sponsorship = result.scalar_one_or_none()
    if sponsorship:
        await db.delete(sponsorship)
        await db.commit()
    return RedirectResponse("/work-hours/sponsorships", status_code=302)
