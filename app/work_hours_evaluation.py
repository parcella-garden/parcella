"""
Work-hours shortfall amounts for invoicing (issue #83): "charge those
who not completely or never used their work sessions, according to
/work-hours/evaluation. Exclude people and garden plots which
exempted or fulfilled their duty."

Reuses app.services.work_hours' evaluation engine (ADR 0070 -- the same
one /work-hours/evaluation and its API equivalent use), but returns
just what invoice generation needs: how much each parcel or member
currently owes for the year, already excluding anyone exempt or who
already fulfilled their hours (both computed to 0, then dropped from
the result entirely -- see app/invoice_generation.py's
WORK_HOURS_SHORTFALL pricing mode, which bills exactly this,
automatically, with no manual scoping).
"""
from typing import Dict, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import WorkHoursMode
from app.services.work_hours import evaluate_year


async def compute_work_hours_shortfalls(
    db: AsyncSession, year: int
) -> Tuple[Optional[WorkHoursMode], Dict[str, float], Dict[str, float]]:
    """Returns (mode, amounts_by_parcel_id, amounts_by_member_id).

    `mode` is None (both dicts empty) if no WorkHoursConfiguration
    exists for `year`. Otherwise exactly one of the two dicts is
    populated, matching whichever mode that year is configured for --
    the other pricing family gets nothing to bill, same as
    /work-hours/evaluation itself only ever shows one table shape per
    year.

    Takes its rows straight from evaluate_year() -- the exact rows the
    evaluation page shows -- instead of selecting parcels/members on its
    own. It used to, and the two selections had drifted (PER_MEMBER here
    took anyone who ever held a lease); issue #239 then changed who
    counts as a tenant for a year, which would have had to be repeated
    here by hand."""
    config, rows = await evaluate_year(db, year)
    if not config:
        return None, {}, {}

    # Exempt or fully-fulfilled rows are dropped, not billed at 0 --
    # same rule /work-hours/evaluation itself applies.
    billable = [row for row in rows if not row["exempt"] and row["amount_due"] > 0]
    if config.mode == WorkHoursMode.PER_PARCEL:
        return WorkHoursMode.PER_PARCEL, {row["parcel"].id: row["amount_due"] for row in billable}, {}
    return WorkHoursMode.PER_MEMBER, {}, {row["member"].id: row["amount_due"] for row in billable}
