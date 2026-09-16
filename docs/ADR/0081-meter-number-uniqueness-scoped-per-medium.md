# Meter-number uniqueness is scoped per medium, not global

**Context:** production 500 on `POST /electricity/metering-points/new`
(kermie, 2026-09-17): `sqlalchemy.exc.IntegrityError` /
`UniqueViolationError` on constraint `wasseruhren_nummer_key`, `Key
(number)=(ohne) already exists`. "ohne" ("none") is a placeholder
number used for a parcel with no distinct physical meter -- a real,
recurring value, not bad data.

`Meter.number` (`app/models.py`) had a **global** `unique=True`,
across water AND electricity, even though both media have shared one
`meters` table since the module's generalization (ADR 0003,
[docs/module-metering.md](../module-metering.md)). The constraint
name itself -- still `wasseruhren_nummer_key` -- is a fossil from when
the table only held water meters, before the German→English rename
(ADR 0009): renaming a Postgres table does not rename its constraints
or indexes, so the name never followed. Once any water meter used
"ohne", no electricity meter could ever use it too, and vice versa --
and `create_metering_point()`/`exchange_meter()` had no pre-check, so
the raw `IntegrityError` reached the user as a 500.

## Decision

Scope the uniqueness to `(medium, number)` instead of `number` alone.
Water and electricity are physically unrelated meter registries --
there's no real-world reason a water meter's serial and an electricity
meter's serial can't coincide, and both need the same "no distinct
meter" placeholder independently.

**Mechanism:**

- `Meter.medium` is a new column, denormalized from the parent
  `MeteringPoint.medium` -- set once at creation
  (`create_metering_point()`/`exchange_meter()` in
  `app/services/metering.py`) and never changed afterwards. A meter
  never moves between metering points, so this can't drift.
- `uq_meter_medium_number` replaces the old global unique constraint
  (migration 0089; drops `wasseruhren_nummer_key` by its real, legacy
  name -- it was never renamed to match the table).
- `create_metering_point()`/`exchange_meter()` now check for a
  same-medium duplicate before insert and raise `ServiceError` (the
  same `app/services/errors.py` shape parcels/inventory/finances
  already use for their own duplicate-key checks), instead of letting
  the DB constraint be the only thing standing between a duplicate
  and a 500. Both HTML routes (redirect with `?error=`, matching the
  existing `metering.errors.invalid_reading` convention in
  `app/routers/metering.py`) and the API (`422`, matching this
  router's existing `record_reading` error handling) now surface it
  as a normal validation error.

## Not done here

Uniqueness *within* one medium is still enforced -- two electricity
meters can't both be "ohne" at the same time. That collision is
possible in practice (several parcels with no distinct meter) but
wasn't the reported failure and is a separate product question (does
"ohne" need to be usable more than once per medium, i.e. should
non-empty real-looking numbers be unique while placeholder-like values
aren't?) -- left for a future ticket if it comes up for real, rather
than guessed at now.
