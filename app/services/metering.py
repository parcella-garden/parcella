"""
Shared metering business logic (water + electricity), called by both
app/routers/metering.py (HTML) and app/routers/api_metering.py (API)
-- see ADR 0070. Medium-agnostic, same as app/meter_utils.py (which
already covers pure validation/computation -- check_monotonicity,
calculate_consumption -- imported independently by both routers; this
module extends the same pattern to persistence): every function takes
`medium: MeteringMedium` explicitly, mirroring the router-factory
pattern (ADR 0003) both routers themselves are built from.

No audit trail or notifications on either side, before or after this
extraction -- the findings here are pure CRUD/validation duplication,
plus one real behavioral gap: the API's create/update-reading path
resolved check_monotonicity()'s (key, params) via the deliberately
German-only format_monotonicity_error_de() instead of the shared i18n
catalog HTML uses via t_for() -- see meter_utils.py's own docstring for
why that was a deliberate scope decision at the time, now revisited
since both surfaces share one code path regardless.
"""
from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.meter_utils import check_monotonicity
from app.models import (
    Meter, MeteringMedium, MeteringPoint, MeteringPointType, MeterReading,
    MeteringPriceConfiguration,
)
from app.services.errors import ServiceError


async def create_metering_point(
    db: AsyncSession, medium: MeteringMedium, *,
    type: str, number: str,
    parcel_id: Optional[str] = None, label: Optional[str] = None, notes: Optional[str] = None,
    calibrated_until: Optional[int] = None, installed_at: Optional[date] = None,
    initial_reading: Decimal = Decimal("0"),
) -> MeteringPoint:
    metering_point = MeteringPoint(
        medium=medium, type=MeteringPointType(type),
        parcel_id=parcel_id, label=label, notes=notes,
    )
    db.add(metering_point)
    await db.flush()

    meter = Meter(
        metering_point_id=metering_point.id, number=number, is_active=True,
        calibrated_until=calibrated_until, installed_at=installed_at,
        initial_reading=initial_reading,
    )
    db.add(meter)
    await db.flush()
    return metering_point


async def update_metering_point(db: AsyncSession, metering_point: MeteringPoint, **fields) -> MeteringPoint:
    """Partial update -- only keys present in `fields` (label/notes)
    are changed. HTML always sends both (full-form semantics); the API
    is a genuine partial update (PUT with exclude_unset)."""
    for key in ("label", "notes"):
        if key in fields:
            setattr(metering_point, key, fields[key])
    await db.flush()
    return metering_point


async def delete_metering_point(db: AsyncSession, metering_point: MeteringPoint) -> None:
    """Also deletes all meters and readings (cascade)."""
    await db.delete(metering_point)
    await db.flush()


async def exchange_meter(
    db: AsyncSession, metering_point: MeteringPoint, *,
    new_number: str, removed_at: date, installed_at: date,
    calibrated_until: Optional[int] = None, initial_reading: Decimal = Decimal("0"),
) -> Meter:
    """Deactivates the current meter (removal date) and creates a new one."""
    old_meter = metering_point.current_meter
    if old_meter:
        old_meter.is_active = False
        old_meter.removed_at = removed_at

    new_meter = Meter(
        metering_point_id=metering_point.id, number=new_number, is_active=True,
        calibrated_until=calibrated_until, installed_at=installed_at,
        initial_reading=initial_reading,
    )
    db.add(new_meter)
    await db.flush()
    return new_meter


async def record_reading(
    db: AsyncSession, meter: Meter, *, year: int, reading_date: date, reading: Decimal,
    note: Optional[str], recorded_by_id: str,
) -> MeterReading:
    """Creates a new reading or updates the existing one for the same
    year. Checks plausibility (the reading must not decrease) --
    raises ServiceError((translation_key, params)-shaped, matching
    meter_utils.check_monotonicity()'s own return shape) if it does."""
    error_info = check_monotonicity(meter, year, reading)
    if error_info:
        key, params = error_info
        raise ServiceError(key, http_status=400, **params)

    existing = next((z for z in meter.readings if z.year == year), None)
    if existing:
        existing.reading = reading
        existing.date = reading_date
        existing.note = note
        existing.recorded_by_id = recorded_by_id
        await db.flush()
        return existing

    new_reading = MeterReading(
        meter_id=meter.id, year=year, date=reading_date,
        reading=reading, note=note, recorded_by_id=recorded_by_id,
    )
    db.add(new_reading)
    await db.flush()
    return new_reading


async def delete_reading(db: AsyncSession, reading_id: str) -> Optional[str]:
    """Deletes a reading and returns its metering_point_id (for the
    caller to redirect back to), or None if the reading didn't exist."""
    result = await db.execute(select(MeterReading).where(MeterReading.id == reading_id))
    reading_entry = result.scalar_one_or_none()
    if reading_entry is None:
        return None

    meter_result = await db.execute(select(Meter).where(Meter.id == reading_entry.meter_id))
    meter = meter_result.scalar_one_or_none()
    metering_point_id = meter.metering_point_id if meter else None

    await db.delete(reading_entry)
    await db.flush()
    return metering_point_id


async def get_price_configuration_for_year(
    db: AsyncSession, medium: MeteringMedium, year: int,
) -> Optional[MeteringPriceConfiguration]:
    result = await db.execute(
        select(MeteringPriceConfiguration).where(
            MeteringPriceConfiguration.medium == medium, MeteringPriceConfiguration.year == year,
        )
    )
    return result.scalar_one_or_none()


async def save_price_configuration_for_year(
    db: AsyncSession, medium: MeteringMedium, year: int, *, price_per_unit: float, note: Optional[str],
) -> MeteringPriceConfiguration:
    """Upsert by (medium, year) -- both HTML's price_configuration_create
    and the API's price_configuration_set key on year directly, no
    separate id involved (that's a different, HTML-only operation, see
    price_configuration_update in app/routers/metering.py)."""
    configuration = await get_price_configuration_for_year(db, medium, year)
    if configuration:
        configuration.price_per_unit = price_per_unit
        configuration.note = note
    else:
        configuration = MeteringPriceConfiguration(medium=medium, year=year, price_per_unit=price_per_unit, note=note)
        db.add(configuration)
    await db.flush()
    return configuration
