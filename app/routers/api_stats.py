"""
API router: statistics for the dashboard.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from pydantic import BaseModel
from typing import Optional
from datetime import date

from app.api_auth import get_current_api_user
from app.birthdays import average_age
from app.database import get_db
from app.models import Member, Parcel, ParcelStatus, MemberParcel

# Same JWT bearer authentication as every other /api/v1 router (see
# app/api_auth.py). Declared on the router rather than per endpoint so a
# second stats endpoint can't be added unauthenticated by omission --
# which is exactly how this one shipped reachable without any login,
# handing out member/parcel counts and total areas to anyone who could
# reach the port.
router = APIRouter(
    prefix="/api/v1/stats",
    tags=["API: Stats"],
    dependencies=[Depends(get_current_api_user)],
)


class DashboardStats(BaseModel):
    members_total: int
    members_active: int
    # Average exact age of active members with a date of birth on file,
    # None if there are none (issue #263).
    members_average_age: Optional[float] = None
    parcels_total: int
    parcels_active: int
    parcels_terminated: int
    parcels_vacant: int
    area_total_sqm: float
    area_terminated_sqm: float


@router.get("", response_model=DashboardStats, summary="Dashboard statistics")
async def dashboard_stats(db: AsyncSession = Depends(get_db)):
    # Members
    members_total = await db.scalar(
        select(func.count()).where(Member.deleted_at.is_(None))
    )
    members_active = await db.scalar(
        select(func.count()).where(
            Member.deleted_at.is_(None),
            Member.member_until.is_(None) | (Member.member_until >= date.today())
        )
    )

    # Parcels by status
    parcels_total = await db.scalar(
        select(func.count()).select_from(Parcel).where(
            Parcel.status != ParcelStatus.DELETED
        )
    )
    parcels_active = await db.scalar(
        select(func.count()).select_from(Parcel).where(
            Parcel.status == ParcelStatus.ACTIVE
        )
    )
    parcels_terminated = await db.scalar(
        select(func.count()).select_from(Parcel).where(
            Parcel.status == ParcelStatus.TERMINATED
        )
    )

    # Vacant parcels (active, but no member assigned)
    besetzte_ids = select(MemberParcel.parcel_id).distinct()
    parcels_vacant = await db.scalar(
        select(func.count()).select_from(Parcel).where(
            Parcel.status == ParcelStatus.ACTIVE,
            Parcel.id.not_in(besetzte_ids)
        )
    )

    # Areas
    area_total = await db.scalar(
        select(func.coalesce(func.sum(Parcel.area_sqm), 0)).where(
            Parcel.status == ParcelStatus.ACTIVE
        )
    )
    area_terminated = await db.scalar(
        select(func.coalesce(func.sum(Parcel.area_sqm), 0)).where(
            Parcel.status == ParcelStatus.TERMINATED
        )
    )

    return DashboardStats(
        members_total=members_total or 0,
        members_active=members_active or 0,
        members_average_age=await average_age(db),
        parcels_total=parcels_total or 0,
        parcels_active=parcels_active or 0,
        parcels_terminated=parcels_terminated or 0,
        parcels_vacant=parcels_vacant or 0,
        area_total_sqm=float(area_total or 0),
        area_terminated_sqm=float(area_terminated or 0),
    )
