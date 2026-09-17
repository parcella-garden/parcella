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
from app.meter_utils import calculate_consumption
from app.services.errors import ServiceError
from app.services.metering import (
    create_metering_point, update_metering_point, delete_metering_point, exchange_meter,
    record_reading, delete_reading, get_price_configuration_for_year, save_price_configuration_for_year,
)
from app.schemas import (
    MeteringPointOut, MeteringPointDetailOut, MeteringPointCreate, MeteringPointUpdate,
    MeterOut, MeterSwapRequest, MeterReadingCreate, MeterReadingOut,
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
        db: AsyncSession = Depends(get_db),
        user: User = Depends(require_api_permission(modul_name, "read")),
    ):
        query = select(MeteringPoint).where(MeteringPoint.medium == medium)
        if type:
            query = query.where(MeteringPoint.type == MeteringPointType(type))
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
        zp = await _load_metering_point(db, metering_point_id)
        if not zp:
            raise HTTPException(status_code=404, detail="Metering point not found")
        out = MeteringPointDetailOut.model_validate(zp)
        out.current_meter = zp.current_meter
        out.former_meters = [z for z in zp.meters if not z.is_active]
        return out

    @router.post(
        "/metering-points", response_model=MeteringPointDetailOut, status_code=status.HTTP_201_CREATED,
        summary="Create metering point",
        description="Creates a metering point including its first meter in a single step.",
    )
    async def create_metering_point_endpoint(
        daten: MeteringPointCreate,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(require_api_permission(modul_name, "write")),
    ):
        zp = await create_metering_point(
            db, medium,
            type=daten.type, parcel_id=daten.parcel_id, label=daten.label, notes=daten.notes,
            number=daten.number, calibrated_until=daten.calibrated_until,
            installed_at=daten.installed_at, initial_reading=daten.initial_reading,
        )
        await db.commit()

        zp = await _load_metering_point(db, zp.id)
        out = MeteringPointDetailOut.model_validate(zp)
        out.current_meter = zp.current_meter
        out.former_meters = []
        return out

    @router.put("/metering-points/{metering_point_id}", response_model=MeteringPointOut, summary="Update metering point")
    async def update_metering_point_endpoint(
        metering_point_id: str,
        daten: MeteringPointUpdate,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(require_api_permission(modul_name, "write")),
    ):
        result = await db.execute(
            select(MeteringPoint).where(MeteringPoint.id == metering_point_id, MeteringPoint.medium == medium)
        )
        zp = result.scalar_one_or_none()
        if not zp:
            raise HTTPException(status_code=404, detail="Metering point not found")

        await update_metering_point(db, zp, **daten.model_dump(exclude_unset=True))
        await db.commit()
        await db.refresh(zp)
        return zp

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
        zp = result.scalar_one_or_none()
        if zp:
            await delete_metering_point(db, zp)
            await db.commit()

    @router.post(
        "/metering-points/{metering_point_id}/exchange", response_model=MeterOut,
        summary="Exchange meter",
        description="Deactivates the current meter (removal date) and creates a new one.",
    )
    async def exchange_meter_endpoint(
        metering_point_id: str,
        daten: MeterSwapRequest,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(require_api_permission(modul_name, "write")),
    ):
        zp = await _load_metering_point(db, metering_point_id)
        if not zp:
            raise HTTPException(status_code=404, detail="Metering point not found")

        new_meter = await exchange_meter(
            db, zp,
            new_number=daten.new_number, removed_at=daten.removed_at, installed_at=daten.installed_at,
            calibrated_until=daten.calibrated_until, initial_reading=daten.initial_reading,
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
        zp = await _load_metering_point(db, metering_point_id)
        if not zp:
            raise HTTPException(status_code=404, detail="Metering point not found")
        meter = zp.current_meter
        if not meter:
            return []
        return sorted(meter.readings, key=lambda z: z.year, reverse=True)

    @router.post(
        "/metering-points/{metering_point_id}/readings", response_model=MeterReadingOut,
        status_code=status.HTTP_201_CREATED, summary="Record reading",
        description="Creates a new reading or updates the existing one for the same year. "
                    "Checks plausibility (the reading must not decrease).",
    )
    async def create_reading(
        metering_point_id: str,
        daten: MeterReadingCreate,
        request: Request,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(require_api_permission(modul_name, "write")),
    ):
        zp = await _load_metering_point(db, metering_point_id)
        if not zp:
            raise HTTPException(status_code=404, detail="Metering point not found")
        meter = zp.current_meter
        if not meter:
            raise HTTPException(status_code=400, detail="No active meter for this metering point")

        try:
            reading = await record_reading(
                db, meter, year=daten.year, reading_date=daten.date, reading=daten.reading,
                note=daten.note, recorded_by_id=user.id,
            )
        except ServiceError as e:
            raise HTTPException(status_code=422, detail=t_for(request, e.key, **e.params))

        await db.commit()
        await db.refresh(reading)
        return reading

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
        for zp in metering_points:
            meter = zp.current_meter
            consumption = calculate_consumption(meter, year) if meter else None
            rows.append(ConsumptionRowOut(
                metering_point_id=zp.id, label=zp.display_name,
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
