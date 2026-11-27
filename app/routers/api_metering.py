"""
API router factory for metering (water & electricity) -- analogous to
the HTML router factory in app/routers/metering.py. One codebase for
both media, instantiated twice (see main.py).

Business logic shared with app/routers/metering.py (HTML) lives in
app/services/metering.py (ADR 0070) -- this router owns bearer-token
authentication, the fine-grained permission check (require_api_permission,
Group-based like the HTML side), Pydantic body parsing, and JSON
response serialization.
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import (
    MeteringPoint, MeteringPointType, MeteringMedium, Meter, MeterReading, User,
    MeteringPriceConfiguration,
)
from app.api_auth import require_api_permission
from app.module_flags import require_module
from app.i18n import t_for
from app.meter_utils import point_consumption
from app.services.metering import (
    create_metering_point, update_metering_point, delete_metering_point, exchange_meter, update_meter,
    record_reading, delete_reading, get_price_configuration_for_year, save_price_configuration_for_year,
)
from app.schemas import (
    MeteringPointOut, MeteringPointDetailOut, MeteringPointCreate, MeteringPointUpdate,
    MeterOut, MeterUpdate, MeterSwapRequest, MeterReadingCreate, MeterReadingOut, MeterReadingRecordedOut,
    ConsumptionRowOut, MeteringPriceConfigurationOut, MeteringPriceConfigurationCreate,
)


def create_metering_api_router(
    medium: MeteringMedium, url_prefix: str, modul_name: str,
) -> APIRouter:
    router = APIRouter(
        prefix=f"/api/v1{url_prefix}",
        tags=[f"API: {modul_name.capitalize()}"],
        dependencies=[Depends(require_module(modul_name))],
    )

    async def _load_metering_point(db: AsyncSession, metering_point_id: str) -> Optional[MeteringPoint]:
        result = await db.execute(
            select(MeteringPoint)
            .options(selectinload(MeteringPoint.meters).selectinload(Meter.readings))
            .where(MeteringPoint.id == metering_point_id, MeteringPoint.medium == medium)
        )
        return result.scalar_one_or_none()

    @router.get("/metering-points", response_model=List[MeteringPointOut], summary="List metering points")
    async def list_metering_points(
        type: Optional[str] = Query(None, description="MAIN_METER, PARCEL, or CLUB"),
        active: Optional[bool] = Query(None, description="true: only active points, false: only switched-off ones"),
        db: AsyncSession = Depends(get_db),
        user: User = Depends(require_api_permission(modul_name, "read")),
    ):
        query = select(MeteringPoint).where(MeteringPoint.medium == medium)
        if type:
            query = query.where(MeteringPoint.type == MeteringPointType(type))
        if active is not None:
            query = query.where(MeteringPoint.is_active == active)
        result = await db.execute(query)
        return result.scalars().all()

    @router.get(
        "/metering-points/{metering_point_id}", response_model=MeteringPointDetailOut,
        summary="Retrieve metering point incl. meter history",
    )
    async def get_metering_point(
        metering_point_id: str,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(require_api_permission(modul_name, "read")),
    ):
        metering_point = await _load_metering_point(db, metering_point_id)
        if not metering_point:
            raise HTTPException(status_code=404, detail="Metering point not found")
        out = MeteringPointDetailOut.model_validate(metering_point)
        out.current_meter = metering_point.current_meter
        out.former_meters = [z for z in metering_point.meters if not z.is_active]
        return out

    @router.post(
        "/metering-points", response_model=MeteringPointDetailOut, status_code=status.HTTP_201_CREATED,
        summary="Create metering point",
        description="Creates a metering point including its first meter in a single step.",
    )
    async def create_metering_point_endpoint(
        payload: MeteringPointCreate,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(require_api_permission(modul_name, "write")),
    ):
        metering_point = await create_metering_point(
            db, medium,
            type=payload.type, parcel_id=payload.parcel_id, label=payload.label, notes=payload.notes,
            number=payload.number, calibrated_until=payload.calibrated_until,
            installed_at=payload.installed_at, initial_reading=payload.initial_reading,
            factor=payload.factor,
        )
        await db.commit()

        metering_point = await _load_metering_point(db, metering_point.id)
        out = MeteringPointDetailOut.model_validate(metering_point)
        out.current_meter = metering_point.current_meter
        out.former_meters = []
        return out

    @router.put("/metering-points/{metering_point_id}", response_model=MeteringPointOut, summary="Update metering point")
    async def update_metering_point_endpoint(
        metering_point_id: str,
        payload: MeteringPointUpdate,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(require_api_permission(modul_name, "write")),
    ):
        result = await db.execute(
            select(MeteringPoint).where(MeteringPoint.id == metering_point_id, MeteringPoint.medium == medium)
        )
        metering_point = result.scalar_one_or_none()
        if not metering_point:
            raise HTTPException(status_code=404, detail="Metering point not found")

        await update_metering_point(db, metering_point, **payload.model_dump(exclude_unset=True))
        await db.commit()
        await db.refresh(metering_point)
        return metering_point

    @router.delete(
        "/metering-points/{metering_point_id}", status_code=status.HTTP_204_NO_CONTENT,
        summary="Delete metering point", description="Also deletes all meters and readings (cascade).",
    )
    async def delete_metering_point_endpoint(
        metering_point_id: str,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(require_api_permission(modul_name, "delete")),
    ):
        result = await db.execute(
            select(MeteringPoint).where(MeteringPoint.id == metering_point_id, MeteringPoint.medium == medium)
        )
        metering_point = result.scalar_one_or_none()
        if metering_point:
            await delete_metering_point(db, metering_point)
            await db.commit()

    @router.put(
        "/metering-points/{metering_point_id}/meter", response_model=MeterOut,
        summary="Edit current meter",
        description="In-place correction of the current meter's own fields "
                     "(number, installed_at, calibrated_until, initial_reading) -- "
                     "not a physical swap, see the exchange endpoint for that.",
    )
    async def update_meter_endpoint(
        metering_point_id: str,
        payload: MeterUpdate,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(require_api_permission(modul_name, "write")),
    ):
        metering_point = await _load_metering_point(db, metering_point_id)
        if not metering_point:
            raise HTTPException(status_code=404, detail="Metering point not found")
        meter = metering_point.current_meter
        if not meter:
            raise HTTPException(status_code=404, detail="No active meter")

        await update_meter(db, meter, **payload.model_dump(exclude_unset=True))
        await db.commit()
        await db.refresh(meter)
        return meter

    @router.post(
        "/metering-points/{metering_point_id}/exchange", response_model=MeterOut,
        summary="Exchange meter",
        description="Deactivates the current meter (removal date) and creates a new one.",
    )
    async def exchange_meter_endpoint(
        metering_point_id: str,
        payload: MeterSwapRequest,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(require_api_permission(modul_name, "write")),
    ):
        metering_point = await _load_metering_point(db, metering_point_id)
        if not metering_point:
            raise HTTPException(status_code=404, detail="Metering point not found")

        new_meter = await exchange_meter(
            db, metering_point,
            new_number=payload.new_number, removed_at=payload.removed_at, installed_at=payload.installed_at,
            calibrated_until=payload.calibrated_until, initial_reading=payload.initial_reading,
            final_reading=payload.final_reading, recorded_by_id=user.id,
        )
        await db.commit()
        await db.refresh(new_meter)
        return new_meter

    @router.get(
        "/metering-points/{metering_point_id}/readings", response_model=List[MeterReadingOut],
        summary="List meter readings",
    )
    async def list_meter_readings(
        metering_point_id: str,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(require_api_permission(modul_name, "read")),
    ):
        metering_point = await _load_metering_point(db, metering_point_id)
        if not metering_point:
            raise HTTPException(status_code=404, detail="Metering point not found")
        meter = metering_point.current_meter
        if not meter:
            return []
        return sorted(meter.readings, key=lambda z: z.year, reverse=True)

    @router.post(
        "/metering-points/{metering_point_id}/readings", response_model=MeterReadingRecordedOut,
        status_code=status.HTTP_201_CREATED, summary="Record reading",
        description="Creates a new reading or updates the existing one for the same year. "
                    "Checks plausibility (the reading should not decrease): an implausible "
                    "reading is still saved, and `warning` explains why it looks off.",
    )
    async def create_reading(
        metering_point_id: str,
        payload: MeterReadingCreate,
        request: Request,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(require_api_permission(modul_name, "write")),
    ):
        metering_point = await _load_metering_point(db, metering_point_id)
        if not metering_point:
            raise HTTPException(status_code=404, detail="Metering point not found")
        meter = metering_point.current_meter
        if not meter:
            raise HTTPException(status_code=400, detail="No active meter for this metering point")

        reading, warning = await record_reading(
            db, meter, year=payload.year, reading_date=payload.date, reading=payload.reading,
            note=payload.note, recorded_by_id=user.id,
        )
        await db.commit()
        await db.refresh(reading)

        # Implausible readings are saved anyway (issue #300, ADR 0124);
        # the reason comes back in `warning` instead of a 422.
        result = MeterReadingRecordedOut.model_validate(reading)
        if warning:
            key, params = warning
            result.warning = t_for(request, key, **params)
        return result

    @router.delete(
        "/readings/{reading_id}", status_code=status.HTTP_204_NO_CONTENT,
        summary="Delete reading",
    )
    async def delete_reading_endpoint(
        reading_id: str,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(require_api_permission(modul_name, "delete")),
    ):
        if await delete_reading(db, reading_id):
            await db.commit()

    @router.get(
        "/evaluation/{year}", response_model=List[ConsumptionRowOut],
        summary="Consumption report for a year",
    )
    async def evaluation(
        year: int,
        type: Optional[str] = Query(None, description="Filter by MAIN_METER, PARCEL, or CLUB"),
        db: AsyncSession = Depends(get_db),
        user: User = Depends(require_api_permission(modul_name, "read")),
    ):
        query = (
            select(MeteringPoint)
            .options(selectinload(MeteringPoint.meters).selectinload(Meter.readings))
            .where(MeteringPoint.medium == medium)
        )
        if type:
            query = query.where(MeteringPoint.type == MeteringPointType(type))
        result = await db.execute(query)
        metering_points = result.scalars().all()

        rows = []
        for metering_point in metering_points:
            meter = metering_point.current_meter
            consumption = point_consumption(metering_point, meter, year)
            rows.append(ConsumptionRowOut(
                metering_point_id=metering_point.id, label=metering_point.display_name,
                meter_number=meter.number if meter else None,
                consumption=consumption,
            ))
        return rows

    # -----------------------------------------------------------------
    # Price configuration -- see app/routers/metering.py's HTML
    # counterpart and app/routers/api_work_hours.py's identically-shaped
    # configuration endpoints.
    # -----------------------------------------------------------------

    @router.get("/configuration", response_model=List[MeteringPriceConfigurationOut], summary="List price configurations")
    async def price_configurations_list(
        db: AsyncSession = Depends(get_db),
        user: User = Depends(require_api_permission(modul_name, "read")),
    ):
        result = await db.execute(
            select(MeteringPriceConfiguration)
            .where(MeteringPriceConfiguration.medium == medium)
            .order_by(MeteringPriceConfiguration.year.desc())
        )
        return result.scalars().all()

    @router.get("/configuration/{year}", response_model=MeteringPriceConfigurationOut, summary="Retrieve price configuration for a year")
    async def price_configuration_get(
        year: int,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(require_api_permission(modul_name, "read")),
    ):
        config = await get_price_configuration_for_year(db, medium, year)
        if not config:
            raise HTTPException(status_code=404, detail=f"No price configuration for {year}")
        return config

    @router.put(
        "/configuration/{year}", response_model=MeteringPriceConfigurationOut,
        summary="Set price configuration (upsert)",
        description="Creates the price configuration for a year or updates it if one already exists.",
    )
    async def price_configuration_set(
        year: int,
        data: MeteringPriceConfigurationCreate,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(require_api_permission(modul_name, "write")),
    ):
        config = await save_price_configuration_for_year(
            db, medium, year, price_per_unit=data.price_per_unit, note=data.note,
        )
        await db.commit()
        await db.refresh(config)
        return config

    return router
