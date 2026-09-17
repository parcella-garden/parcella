# Meter number uniqueness removed entirely

**Context:** [ADR 0081](./0081-meter-number-uniqueness-scoped-per-medium.md)
fixed a prod 500 (`POST /electricity/metering-points/new` failing with
a `UniqueViolationError` when the placeholder number "ohne"/"none" --
used for a parcel with no distinct physical meter -- was already used
by a meter of the other medium) by scoping `meters.number`'s
uniqueness to `(medium, number)` instead of leaving it global.

kermie, immediately after that shipped: "who the heck told you to make
Current Electricity meter Number unique? this is folly. can you revert
it?" -- rejecting per-medium scoping too, not just the global version.
Nobody had asked for uniqueness on this field in the first place; ADR
0081 preserved *some* scope of uniqueness by default, as the
"recommended" option in the question that led to it, rather than
questioning whether the field needed enforced uniqueness at all.

## Decision

`meters.number` is a plain free-text field, like `label`/`notes` --
no DB constraint, no validation check, not even a non-blocking
warning. A meter's real identity is its row id
(`Meter.id`/`metering_point_id`); `number` is just what gets printed
on the metering point's detail page and CSV exports. Two meters,
water+electricity or the same medium, can share any number, including
duplicates that are actual data-entry mistakes -- this software does
not gatekeep that.

**Reverted, migration 0090:**

- Drops `uq_meter_medium_number` and the `medium` column added to
  support it (ADR 0081/migration 0089).
- `create_metering_point()`/`exchange_meter()`
  (`app/services/metering.py`) lose the pre-insert duplicate check and
  the `ServiceError` they raised.
- Both routers (`app/routers/metering.py`, `app/routers/api_metering.py`)
  lose the `try`/`except ServiceError` wrapping and the `?error=`
  query-param plumbing added only to surface that check.
- `metering.errors.duplicate_meter_number` removed from all 7
  translation catalogs.

## Not done here

The original bug this whole chain started from -- a *global* unique
constraint 500ing instead of failing gracefully -- can't recur, since
there's no constraint left to violate. If a real product need for
duplicate detection ever comes up (e.g. flagging, not blocking, an
accidental copy-paste of the same serial number), it should be scoped
from an actual reported case, not re-guessed from this history.
