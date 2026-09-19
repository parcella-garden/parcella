# Module: Metering (Water & Electricity)

> **Note on the renaming:** the code (models, tables, URLs, API
> endpoints) has been fully converted to English:
> `Zaehlpunkt` -> `MeteringPoint`, `Zaehler` -> `Meter`,
> `Zaehlerstand` -> `MeterReading`, `/wasser/` -> `/water/`,
> `/strom/` -> `/electricity/`. Details and lessons learned in
> [Architecture Decisions](./ADR/0009-third-module-to-english-zaehlerwesen-metering.md).
> This page continues to describe the domain logic, which did not
> change in the process.

Manages water and electricity meters via **one shared codebase** -- the
clearest example in the project of generalizing structurally similar
requirements instead of duplicating them.

Module flags: `water` and `electricity` (independently toggleable)

## Data model

```
metering_points  – a metering point: main meter, parcel, or club connection.
                   Has a "medium" (WATER/ELECTRICITY) and a "type".
meters           – the physical meter at a metering point (number,
                   calibration deadline, install/removal date, initial reading)
meter_readings   – annual readings of a meter
```

A parcel can have both a water and an electricity metering point -- two
rows in the same table, distinguished by `medium`.

## Key decision: router factory instead of duplication

Water and electricity are structurally identical: main meter + sub-
meters, annual reading, consumption calculation, plausibility checks. The
only differences are the unit (m³ vs. kWh), decimal places (1 vs. 0), and
display labels.

Instead of maintaining two separate router files, there is **one**
factory function, `erstelle_metering_router()`, in
`app/routers/metering.py`, which produces a fully configured router for
**one** medium. `main.py` instantiates it twice:

```python
water_router = erstelle_metering_router(
    medium=MeteringMedium.WATER, url_prefix="/water", modul_name="water",
    medium_label="Wasser", unit="m³", icon="bi-droplet", dezimalstellen=1,
)
electricity_router = erstelle_metering_router(
    medium=MeteringMedium.ELECTRICITY, url_prefix="/electricity", modul_name="electricity",
    medium_label="Strom", unit="kWh", icon="bi-lightning-charge", dezimalstellen=0,
)
```

A bug fix or new feature therefore only has to be written **once**. The
templates (`app/templates/metering/`) are likewise shared -- they receive
`unit`, `medium_label`, `icon`, etc. as variables instead of hard-coding
the values.

If a third medium is added in the future (gas?), one more call to
`erstelle_metering_router()` with the matching configuration is enough.

## Plausibility checks

**Per-meter monotonicity** (hard, blocking): a new reading must not be
smaller than the previous reading for the *same* meter number -- both
backward (not smaller than the prior value) and forward (not larger than
an already-recorded later value, if one exists). See
`check_monotonicity()` in `app/zaehler_utils.py`.

**Overall plausibility** (warning, non-blocking): the sum of parcel and
club consumption must not exceed the main meter's consumption. This is
shown as a warning banner, not an error -- because readings are entered
with a time lag, and a temporarily "incomplete" data state is not an
error but normal.

## Meter exchange and history

When a meter is exchanged (e.g. every 6 years for water, due to
calibration deadlines), the old one is **not deleted** but deactivated
(`is_active = false`, `removed_at` set). The new meter gets its own row
with a new number and its own initial reading. This correctly separates
consumption calculations -- no mixing of old and new meter readings.

**Editing the current meter in place (issue #226)** is a separate
operation from exchanging it: `update_meter()`
(`app/services/metering.py`), `POST .../meter/edit` (HTML) and
`PUT .../meter` (API) correct a data-entry mistake on the still-current
`Meter` row's own fields (number, installed_at, calibrated_until,
initial_reading) -- no new row, no `removed_at`, no history entry.
Reach for exchange only for an actual physical meter swap; reach for
edit for "I mistyped this."

## Billing price configuration

`MeteringPriceConfiguration` (one row per `(medium, year)`, unique
constraint on the pair) holds the EUR price per m³/kWh that drives the
`water_usage`/`electricity_usage` invoice pricing modes in the finances
module -- see [ADR 0056](./ADR/0056-metering-price-drives-automatic-usage-billing.md).
Historized per year (like `WorkHoursConfiguration`), edited at
`/water/configuration` and `/electricity/configuration` (added to the
shared `create_metering_router()` factory, so both media get the CRUD
routes/templates for free). If no price is configured for a run's
year, that run's water/electricity items simply bill nothing for that
year -- same "nothing configured -> nothing billed" behavior as
`InsuranceConfiguration`/`WorkHoursConfiguration`.

## Overview page: parcels without a metering point

The `/water/` and `/electricity/` overview pages (`overview()` in
`app/routers/metering.py`) include a fifth stat tile, alongside main
meter/parcels/club connections/difference, counting every `ACTIVE`/
`TERMINATED` parcel that has no `MeteringPointType.PARCEL` metering
point for that medium (issue #223) -- e.g. a new parcel that was never
wired up, or one whose only metering point was deleted. `DELETED`
parcels are excluded, and a `TERMINATED` parcel still counts as missing
one (same convention as the "new metering point" form's parcel
dropdown, issue #219) -- a cancelled lease doesn't retroactively make a
missing metering point irrelevant. Water and electricity coverage are
independent: a parcel with only a water metering point still counts as
missing on the electricity tile and vice versa. Deliberately just a
count, matching the other four tiles -- not a list of parcel names/links,
which was the first cut at this but didn't match the page's existing
visual language.

Each of the five stat tiles (except Difference, which is a computed
value, not a category) has a "Show" footer button linking into
`/{medium}/metering-points` with a filter (issue #224) -- same
"stat card + Show button -> filtered list" pattern the main dashboard
already uses (e.g. its Terminated-parcels card linking to
`/parcels/?status_filter=TERMINATED`):

- Main meter / Parcels / Club connections -> `?type=MAIN_METER`/`PARCEL`/`CLUB`,
  filtering the normal metering-points table to that `MeteringPointType`.
- Missing metering points -> `?missing=1`. There's no `MeteringPoint` row
  to filter to for these, so this switches the *same* list page to a
  distinct view: the actual parcels with none, each linking to the "new
  metering point" form with that parcel pre-selected
  (`?parcel_id=<id>` on `/metering-points/new`) so it's actionable
  rather than a dead end. `_load_parcels_without_metering_point()` is
  shared between the overview tile's count and this filtered view so
  the two can't drift apart.

## Known pitfalls

- **The "new metering point" parcel dropdown includes `TERMINATED`
  parcels, not just `ACTIVE`** (issue #219): a lease being cancelled
  doesn't mean the parcel's water/electricity connection stops needing
  tracking -- staff still need to add a metering point (or record a
  final handover reading) for a just-terminated parcel before a new
  tenant moves in. `DELETED` parcels stay excluded. Same reasoning as
  the insurance module's `_insurance_parcels_query()` (issue #207):
  filtering a "new/action" list down to `ACTIVE` only quietly hides the
  parcels that most need attention right after a status change, not
  just the settled ones.

- **`Meter.number` is a free-text field, not an enforced-unique
  identifier** (see [ADR 0082](./ADR/0082-meter-number-uniqueness-removed-entirely.md),
  which supersedes [ADR 0081](./ADR/0081-meter-number-uniqueness-scoped-per-medium.md)):
  a real prod 500 led to briefly making it unique per medium, which
  turned out to be just as wrong as the global uniqueness it replaced
  -- don't reintroduce a `unique=True`/uniqueness check on `number` in
  any scope. A meter's real identity is its row id.

- **Jinja2 can't do Python's `.format()`**: `"%.{}f"|format(places)|format(value)`
  does not work (Jinja's `format` filter uses the old `%` operator).
  Solution: a custom Jinja filter `fmt`, registered directly on the
  `Jinja2Templates` object in `metering.py`:
  ```python
  templates.env.filters["fmt"] = lambda value, places: f"{float(value):.{places}f}"
  ```
- **MissingGreenlet on creation**: when a database row is newly created
  via `db.add()` + `commit()` (rather than loaded via a query), its
  relationships (`relationship` fields) are not eagerly loaded. A later
  access triggers a synchronous lazy load, which raises `MissingGreenlet`
  with the async database driver. Fix: explicitly reload the row with
  `selectinload(...)` after creating it (see
  `get_or_create_parcel_insurance()` in `app/services/insurance.py` for
  an example of this pattern).

## CSV import/export (issue #225)

Both metering points and their readings can be exported to and
imported from CSV, on `/{medium}/metering-points` and
`/{medium}/readings` respectively -- same two-step "export first, hand-
edit, re-import" pattern `app/routers/parcels.py` already uses, and
added to the shared router factory so both media get it automatically.

- **Metering points** (`.../metering-points/export/csv` and
  `.../import/preview` → `.../import/finalize`): the metering point's
  and its *current* meter's static attributes -- type, parcel number,
  label, meter number, installed on, calibrated until, initial reading.
  Import only *creates* new metering points, matched for dedup by
  `(type, parcel number)` for `PARCEL` rows or `(type, label)` for
  `MAIN_METER`/`CLUB` rows -- re-importing an unchanged export is a
  no-op rather than a pile of duplicates. A row with no `Label` for a
  `MAIN_METER`/`CLUB` type can't be deduplicated (there's nothing to
  key on) and is always created fresh.
- **Readings** (`.../readings/export/csv` and `.../import/preview` →
  `.../import/finalize`): scoped by year on export (mirrors
  `/{medium}/readings?year=` and the existing `/evaluation/csv`), one
  row per metering point's current meter. Import carries a `Year`
  column per row instead, so one file can cover several years at once
  (the actual motivating case: water metering points entered via CSV
  for 2024+2025 after electricity was already entered by hand).
  Readings are only ever attached to an *existing* metering point
  (looked up by the same `(type, parcel number)`/`(type, label)` key as
  the metering-points import) -- import never creates one.
- **Column-mapping wizard (issue #227, ADR 0083):** both importers are
  2-step -- upload → a preview page guesses a column→field mapping
  (English and German header aliases; e.g. `Zählernummer` guesses
  `meter_number`) which the user confirms or corrects, then finalize
  applies it. This generalizes the wizard ADR 0062 built for finances'
  bank-statement import into shared `app/csv_utils.py` helpers, and
  **replaces** the old fixed-header endpoints rather than keeping both
  (same call ADR 0062 made, for the same reason). The row-processing
  logic below is unchanged either way -- only how a row's raw values
  get from "CSV column" to "named field" changed. `Type` doesn't need
  to be mapped at all -- a real single-medium export is usually
  all-`PARCEL` rows with no Type column (points/readings both default
  every row to `PARCEL` when `type` isn't mapped); only mapping
  *nothing at all* is refused.
- Both readings imports go through `record_reading()`
  (`app/services/metering.py`), so a bulk-loaded reading is subject to
  exactly the same monotonicity check as one entered by hand through
  the UI; a row that fails it is skipped (counted, not silently
  dropped) rather than aborting the whole file.
- **Pitfall hit building this:** `record_reading()` sets `meter_id` on
  the new `MeterReading` directly rather than through the relationship,
  so the already-eagerly-loaded `meter.readings` Python list doesn't
  pick up a newly inserted reading automatically (same identity-map
  shape as the "freshly created rows" pitfall above, just via a raw FK
  assignment instead of a fresh `select()`). Since one import request
  can record several years for the *same* meter in a loop, a later
  row's monotonicity check needs to see the earlier row's newly
  inserted reading -- fixed by appending the returned `MeterReading` to
  `meter.readings` by hand after each call, in `readings_import_finalize()`.
- CSV headers are plain English (`Type`, `Parcel number`, ...) for both
  formats -- a deliberate difference from `parcels.py`'s CSV export,
  which keeps German headers as a legacy fact (see its own docstring);
  this is new functionality, so it follows the "English first, going
  forward" convention instead of copying that precedent. The mapping
  wizard means a non-English-headed file no longer needs hand-editing
  first, though.
- XLSX import was raised alongside this (a self-hoster's data
  sometimes arrives as an Excel file rather than CSV) and then
  explicitly dropped, not just deferred -- kermie: CSV is the way to
  go. Not a gap to revisit; an Excel export can be saved as CSV before
  importing.

## REST API

This module has (added after the fact) a complete set of REST API
endpoints for this module (JWT-authenticated, see `/api/docs`). See the
README for the endpoint overview. Background: early modules were
initially built as web UI only, with the API added later -- since then
the rule is that every new module gets **both** the web UI and API
endpoints **from the start** (see Architecture Decisions).

**Implementation note (ADR 0070):** metering-point/meter/reading CRUD
and price-configuration upsert now live in `app/services/metering.py`,
called by both `app/routers/metering.py` and
`app/routers/api_metering.py` -- medium-agnostic like `app/meter_utils.py`
already was (every function takes `medium` explicitly, same shape as
the router factories themselves, ADR 0003). Closed one real gap along
the way: the API used to resolve `check_monotonicity()`'s error via a
German-only `format_monotonicity_error_de()` (now removed) instead of
the shared i18n catalog the HTML side used via `t_for()` -- both now
resolve the same `(key, params)` through one path
(`record_reading()`), so the API's plausibility-check error is no
longer always German regardless of the club's configured language. The
API router also now checks permissions the same fine-grained,
`Group`-based way the HTML side does (`require_api_permission`), not
the coarser role-only check most other API routers still use.
`price_configuration_update` (HTML-only: editing an existing price
configuration's year by id, with a same-year collision check) has no
API equivalent and stays router-local -- there's nothing to unify it
against.
