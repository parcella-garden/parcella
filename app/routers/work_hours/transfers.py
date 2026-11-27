"""Hours transfers between members."""
import urllib.parse
from fastapi import APIRouter
from datetime import date
from typing import Optional
from fastapi import Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_, select
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models import HoursTransfer, Member, MemberParcel, WorkHoursConfiguration
from app.permissions import require_permission
from app.i18n import t_for
from app.services.errors import ServiceError
from app.services.work_hours import (
    create_hours_transfer,
    get_config_for_year,
    list_hours_transfers,
    sort_members_by_plot,
)
from app.templating import templates

router = APIRouter()


# ---------------------------------------------------------------------------
# Hours transfers (issue #243, ADR 0094): a member gives surplus hours of
# a year to another member. The surplus check lives in the service.
# ---------------------------------------------------------------------------

@router.get("/transfers", response_class=HTMLResponse)
async def transfers_page(
    request: Request,
    year: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
):
    user = await require_permission(request, db, "work_hours", "read")
    if not year:
        year = date.today().year

    # Anyone who was a member at some point in the year can give or
    # receive -- including a tenant who left mid-year and still owes
    # that year's hours (issue #239).
    members_result = await db.execute(
        select(Member)
        .options(selectinload(Member.parcel_assignments).selectinload(MemberParcel.parcel))
        .where(
            Member.deleted_at.is_(None),
            or_(Member.member_since.is_(None), Member.member_since <= date(year, 12, 31)),
            or_(Member.member_until.is_(None), Member.member_until >= date(year, 1, 1)),
        )
    )
    years_result = await db.execute(
        select(WorkHoursConfiguration.year).order_by(WorkHoursConfiguration.year.desc())
    )
    return templates.TemplateResponse(
        request, "work_hours/transfers.html",
        {
            "request": request,
            "user": user,
            "year": year,
            "config": await get_config_for_year(db, year),
            "available_years": [r[0] for r in years_result.all()],
            "transfers": await list_hours_transfers(db, year),
            "all_members": sort_members_by_plot(members_result.scalars().all()),
        },
    )


@router.post("/transfers/new")
async def transfer_create(
    request: Request,
    year: int = Form(...),
    giver_member_id: str = Form(""),
    receiver_member_id: str = Form(""),
    hours: str = Form(...),
    note: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    user = await require_permission(request, db, "work_hours", "write")
    try:
        try:
            parsed_hours = float(hours.replace(",", "."))
        except ValueError:
            raise ServiceError("work_hours.transfers.errors.hours_positive")
        await create_hours_transfer(
            db, giver_member_id=giver_member_id, receiver_member_id=receiver_member_id,
            year=year, hours=parsed_hours, note=note, created_by_id=user.id,
        )
    except ServiceError as e:
        await db.rollback()
        message = t_for(request, e.key, **e.params)
        return RedirectResponse(
            f"/work-hours/transfers?year={year}&error={urllib.parse.quote(message)}", status_code=303,
        )
    await db.commit()
    return RedirectResponse(f"/work-hours/transfers?year={year}", status_code=303)


@router.post("/transfers/{transfer_id}/delete")
async def transfer_delete(transfer_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    await require_permission(request, db, "work_hours", "delete")
    transfer = await db.get(HoursTransfer, transfer_id)
    year = transfer.year if transfer else date.today().year
    if transfer:
        await db.delete(transfer)
        await db.commit()
    return RedirectResponse(f"/work-hours/transfers?year={year}", status_code=303)
