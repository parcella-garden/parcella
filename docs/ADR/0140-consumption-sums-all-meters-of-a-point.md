# 0140: A point's consumption sums all its meters; the exchange records a final reading

**Status:** accepted (issue #354, 2026-11-20)

## Context

Readings are stored per meter and year (`MeterReading.year`, one per meter
and year). Invoices (`app/invoice_generation.py`, usage pricing) and the
metering Evaluation page only used the point's **current** meter. The
Overview tiles (`total_consumption_for_type`) already summed **all** meters.

In the year of a meter exchange, the old meter's consumption from its last
reading up to the exchange was therefore never billed, and the Overview and
the Evaluation showed different totals. `exchange_meter()` didn't record a
final reading for the old meter either, so even summing would have found
nothing for it in that year.

## Decision

1. **The exchange records the old meter's final reading** (optional field
   "Final reading of the old meter" in the form, `final_reading` in the
   API's `MeterSwapRequest`). It's saved as the old meter's reading for the
   year of the removal date, dated on that day, through `record_reading()`
   (so it replaces an earlier reading of the same year, which it supersedes,
   and gets the usual monotonicity warning).
2. **A point's consumption in a year is the sum over all its meters that
   have a reading in that year**: `point_year_consumption()` in
   `app/meter_utils.py`. Old meter: final reading minus its previous
   reading; new meter: its reading minus its initial reading.
3. **Used by invoices** (raw, `with_factor=False`, ADR 0138), **the
   Evaluation page and its CSV** (with the point's factor). The Overview
   already summed all meters and now agrees with both. The Evaluation marks
   such rows "incl. replaced meter".

The metering point page's readings table still lists the current meter's
readings (and the old meter under **Former meters**): it's a per-meter
view, not a total.

## Consequences

- An exchange without a final reading still bills only the new meter for
  that year (as before); the form explains why the field matters.
- Invoice amounts change for parcels with an exchange during the billing
  year, so this shipped as a **minor** release (7.1.0), not a patch.
- No schema change and no migration: the final reading is an ordinary
  `MeterReading`.

## Rejected

- **A dedicated "final reading" column on `Meter`:** a second place for a
  reading, ignored by every existing reading view, export and check.
- **Prorating the new meter's consumption by date:** guesses a number the
  board can simply read off the old meter.
