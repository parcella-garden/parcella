# Meter readings: a decreasing reading warns, it doesn't block

**Context:** issue #300. The per-meter monotonicity check
(`check_monotonicity()` in `app/meter_utils.py`) used to refuse a
reading lower than the previous year's (or higher than an already
recorded later year's), on every surface: manual entry, CSV import and
the REST API. Then a club had to *estimate* last year's readings, and
some estimates came out above this year's real values. The real
readings could not be entered at all, and the refusal was barely
visible: the metering-point page only put the message in the URL, and
`/readings` showed raw 422 JSON (the redirect appended a second `?` to
a `return_url` that already had `?year=`).

## Decision

The check stays, but it **warns instead of blocking**, everywhere:

- `record_reading()` (`app/services/metering.py`) always saves and
  returns `(reading, warning)`, where `warning` is
  `check_monotonicity()`'s `(translation_key, params)` or `None`.
- HTML: both entry pages (`/<medium>/metering-points/{id}` and
  `/<medium>/readings`) show a yellow "saved, but please check" banner
  after saving, and a lasting marker next to every stored reading that
  is still implausible. The marker matters as much as the banner: the
  person who notices the odd consumption figure months later is often
  not the one who entered it.
- CSV import: implausible rows are recorded and listed in a separate
  warning banner (count plus the first few rows), no longer skipped.
- REST API: `201` with the stored reading plus a `warning` string
  (`MeterReadingRecordedOut`), no longer `422`. This changes the API
  contract for that one case: a client that relied on the 422 to stop
  bad data now gets it stored. Accepted: the data is not *wrong* (it is
  what was read off the meter), the warning is in the response, and an
  estimated value is fixed by editing it, not by refusing the truth.

Unchanged: an unparsable number is still an error, and the
overall-plausibility check (parcels + club > main meter) was already a
warning.

## Rejected alternatives

- **Keep blocking, add a "force" checkbox.** Every legitimate case
  (estimated prior value, meter rolled over, typo in last year's entry)
  ends with the user forcing it anyway; one more click doesn't add any
  safety, it just hides the reason behind a second step.
- **Warn only in the UI, keep CSV import and API strict.** kermie chose
  one rule for all surfaces (issue #300): the same reading shouldn't be
  accepted by hand and refused by import.
- **An "estimated" flag on readings.** Would explain *why* a value looks
  off, but it's a data-model change for a case the warning already
  surfaces. Revisit if clubs start estimating routinely.

## Also fixed along the way

`reading_create`'s redirect now builds its query string properly
(`_with_query_param()`), and `return_url` (a form field) is only
honoured if it stays inside the module's own URL prefix. Before, it was
an open redirect.
