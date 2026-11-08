"""
Helper functions for the metering module (water + electricity):
consumption calculation and plausibility checking. Medium-agnostic --
works identically for water meters and electricity meters.
"""
from datetime import date
from typing import Optional, List
from decimal import Decimal

from app.models import Meter, MeterReading


def sorted_readings(meter: Meter) -> List[MeterReading]:
    """A meter's readings, sorted chronologically by year."""
    return sorted(meter.readings, key=lambda z: z.year)


def reading_before_year(meter: Meter, year: int, exclude_id: Optional[str] = None) -> Decimal:
    """
    Determines the relevant prior reading for calculating a given
    year's consumption: the last reading BEFORE that year, or the
    meter's initial reading if none exists.
    """
    earlier_readings = [
        z for z in sorted_readings(meter)
        if z.year < year and z.id != exclude_id
    ]
    if earlier_readings:
        return Decimal(str(earlier_readings[-1].reading))
    return Decimal(str(meter.initial_reading))


def reading_after_year(meter: Meter, year: int, exclude_id: Optional[str] = None) -> Optional[Decimal]:
    """The next existing reading AFTER a year, if any (for edit-time plausibility checks)."""
    later_readings = [
        z for z in sorted_readings(meter)
        if z.year > year and z.id != exclude_id
    ]
    if later_readings:
        return Decimal(str(later_readings[0].reading))
    return None


def calculate_consumption(meter: Meter, year: int) -> Optional[Decimal]:
    """
    A meter's consumption in a given year = that year's reading minus
    the last reading before it (or the initial reading). Returns None
    if no reading exists for that year.
    """
    current_reading = next((z for z in meter.readings if z.year == year), None)
    if not current_reading:
        return None
    previous_value = reading_before_year(meter, year, exclude_id=current_reading.id)
    return Decimal(str(current_reading.reading)) - previous_value


def check_monotonicity(
    meter: Meter, year: int, new_value: Decimal, exclude_id: Optional[str] = None
) -> Optional[tuple]:
    """
    Plausibility check: a meter's reading should not decrease over time.
    If it does, returns a tuple (translation key, formatting
    parameters); otherwise None. Since issue #300 (ADR 0124) this is a
    non-blocking warning -- callers save the reading anyway and show
    the message.

    A tuple instead of a ready-formatted string, so the result can be
    resolved via app.i18n.translate()/t_for() -- shared by both the
    HTML and API surfaces via app.services.metering.record_reading()
    (ADR 0070; the API used to format this in German only, via a now-
    removed format_monotonicity_error_de(), regardless of the club's
    configured language).
    """
    previous_value = reading_before_year(meter, year, exclude_id=exclude_id)
    if new_value < previous_value:
        return ("metering.warnings.reading_below_previous", {"new_value": new_value, "previous_value": previous_value})

    later_value = reading_after_year(meter, year, exclude_id=exclude_id)
    if later_value is not None and new_value > later_value:
        return ("metering.warnings.reading_above_later", {"new_value": new_value, "later_value": later_value})

    return None


def total_consumption_for_type(metering_points: List, year: int) -> Decimal:
    """
    Sums the consumption of all active meters across a list of
    MeteringPoints for a given year. MeteringPoints/meters with no
    reading for that year contribute 0 (instead of skewing the sum or
    raising an error) -- the evaluation page reports gaps separately.
    """
    total = Decimal("0")
    for metering_point in metering_points:
        for meter in metering_point.meters:
            consumption = calculate_consumption(meter, year)
            if consumption is not None:
                total += consumption
    return total


# Rounding: how many decimal places are shown/recorded per medium?
# Water is read to one decimal place (m³), electricity as a whole number (kWh).
DECIMAL_PLACES_PER_MEDIUM = {
    "WATER": 1,
    "ELECTRICITY": 0,
}


def round_for_medium(value: Decimal, medium: str) -> Decimal:
    """Rounds a value to the number of decimal places customary for the medium."""
    places = DECIMAL_PLACES_PER_MEDIUM.get(medium, 1)
    quant = Decimal("1") if places == 0 else Decimal("1." + "0" * places)
    return value.quantize(quant)
