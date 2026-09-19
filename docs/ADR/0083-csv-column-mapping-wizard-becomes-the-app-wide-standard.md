# CSV column-mapping wizard becomes the app-wide standard, replacing fixed headers everywhere

**Context:** ADR 0062 (issue #186/#188) introduced a 2-step upload →
map → confirm CSV import wizard for account bookings alone, replacing
that one fixed-header importer. Metering (points and readings,
`app/routers/metering.py`), parcels (`app/routers/parcels.py`), and
members (`app/routers/members.py`) still required an exact, fixed
header row on import as of [issue #227](https://github.com/parcella-garden/parcella/issues/227)
-- a self-hoster with a real-world export whose columns don't happen
to match Parcella's own export couldn't import it without hand-editing
the file first.

**Decision: generalize ADR 0062's wizard into shared `app/csv_utils.py`
helpers, and apply it to metering points, metering readings, parcels,
and members -- replacing each fixed-header importer, the same way ADR
0062 replaced the bank-bookings one.**

- `app/csv_utils.py` gained `decode_csv_upload`, `sniff_csv_delimiter`,
  `guess_column_mapping`, `parse_column_mapping`, and
  `parse_mapped_csv_rows` -- lifted from finances.py's own
  `_decode_csv_upload`/`_sniff_csv_delimiter`/`_guess_column_mapping`/
  `_parse_column_mapping`/`_parse_mapped_csv_rows`, generalized so
  `guess_column_mapping` takes a per-field alias set as a parameter
  instead of hardcoding finances' own Date/Amount/... vocabulary.
  `finances.py` itself was refactored onto these (pure refactor, no
  behavior change -- its own 3-step flow, including the
  invoice-matching `match` step, is unchanged and stays finances-only,
  since no other module has an equivalent matching concept).
- Each of the four modules keeps its **own** alias set as local data
  (Type/Parzelle/Zählernummer for metering vs. Vorname/Nachname for
  members vs. Gartennummer for parcels) -- the vocabulary is
  module-specific, only the mapping *mechanism* is shared.
- Each importer becomes a 2-step `.../import/preview` →
  `.../import/finalize` pair (metering keeps its existing per-medium
  factory structure, so both water and electricity get the wizard for
  free, same as before). The old single-step `.../import/csv`
  endpoints are **removed**, not kept alongside the wizard -- per ADR
  0062's own reasoning, maintaining two import code paths for the same
  target table invites them drifting apart. All downstream row
  semantics (dedup/matching keys, create-vs-skip vs. create-vs-update,
  the metering monotonicity check, the members name+DOB update
  matching) are unchanged -- only how a row's raw values get from "CSV
  column" to "named field" changed, from a literal `DictReader` header
  lookup to a confirmed column→field mapping.
- Each module still requires its own minimum viable mapping before
  proceeding (metering: `type`; parcels: `plot_number`; members:
  `first_name` **and** `last_name`) -- mirroring ADR 0062's own
  required-`date`-and-`amount` check for bookings. Everything else is
  optional to map; an unmapped field just behaves as if the column
  were blank, same as a missing column did under the old fixed-header
  importers.
- `app/routers/members.py`'s import file-upload field was renamed from
  `datei` to `file`, matching the other three modules (internal form
  field name only, no user-visible or translation impact).

**Consequence, accepted:** members CSV import had zero prior test
coverage (no `tests/test_members.py` existed at all) -- this change
adds one alongside the wizard rather than as a separate followup,
since its update-by-name+DOB matching is the most subtle row logic of
the four modules touched and shouldn't ship a UI change unverified.
Alias guesses are best-effort, not exhaustively multilingual across
all 7 UI languages (German aliases matter most, since that's the
recurring real-world case) -- manual override in the mapping form
always works, so guess accuracy is a convenience, not a correctness
requirement. `app/routers/parcels.py` and `app/routers/members.py`
still have their own inline BOM-decode/delimiter-sniff duplicates in
places `csv_utils.py` doesn't yet reach (e.g. `parcels_export_csv`
doesn't need them, but any future CSV endpoint added to those files
should reach for the shared helpers rather than re-inlining the old
pattern).
