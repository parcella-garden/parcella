# Accident insurance: per-household-member opt-out, not an atomic household toggle

**Context:** issue #204 -- a household explicitly does not want accident
insurance for themselves, but wants a named additional person outside
the household (a relative at a different address) to stay insured.
Previously impossible: the household's flat base fee was always bundled
in automatically whenever `has_accident_insurance` was on, with no way
to separate "is accident insurance active for this parcel" from "is the
household part of what's covered."

## Rejected first attempt: an atomic `covers_household` toggle

Migration 0081 added a single boolean, `covers_household`, independent
of `has_accident_insurance`: on (default) meant the household's flat fee
applied as before; off meant it didn't, while the additional-person
picker kept working regardless. This shipped in v2.2.0.

kermie caught the mismatch after using it: "the Household co-insured
switcher is a bit too much and also misleading. We are not talking
about an household insurance ... all I wanted to achieve is to have the
actual leaser's check box un-checkable while the additional person ...
can be checked." The real requirement was always per-person, not
per-household -- an all-or-nothing switch was the wrong shape even
though it technically solved the reported symptom.

## Decision: `accident_insurance_household_members`, opt-out by default

Migration 0082 replaces `covers_household` with a new table,
`accident_insurance_household_members` (`parcel_insurance_id`,
`member_id`), symmetric to the existing
`accident_insurance_additional_persons` but with the opposite default
polarity:

- **Household members** (`household_grouping()` in
  `app/insurance_utils.py`): opt-**OUT**. A `ParcelInsurance` row is
  seeded with every detected household member at creation time
  (`get_or_create_parcel_insurance` in `app/services/insurance.py`), so
  "save without touching anything" preserves today's behavior. Each can
  then be individually unchecked in the UI.
- **Additional persons** (unchanged): opt-**IN**, exactly as before --
  covered only if explicitly checked.

The flat base fee (`accident_base_amount_eur`) applies once if
`pi.household_members` is non-empty; the per-head additional fee applies
per row in `pi.additional_persons` -- both are now cheap relationship-
length checks in `calculate_insurance_cost()`
(`app/insurance_utils.py`), not a live re-computation of address
grouping at cost-calculation time. `pi.household_members` only needed
eager-loading everywhere `pi.additional_persons` already was (7 call
sites across `app/routers/insurance.py`, `app/routers/api_insurance.py`,
`app/invoice_generation.py`, `app/services/insurance.py`) -- a
mechanical addition next to each, no cost-calc call site needed to start
loading `parcel.member_assignments`.

## Data migration lesson

0082's upgrade seeds `accident_insurance_household_members` for every
pre-existing `parcel_insurance` row with `has_accident_insurance = true`
from that parcel's current tenants (re-implementing
`household_grouping()`'s same-address-group algorithm self-contained,
since migrations don't import app code) -- otherwise every parcel with
accident insurance already active would silently lose its base fee the
moment `covers_household` (which defaulted true) is dropped.

**First version of this migration had a real bug, caught in review
before it shipped:** the seeding query didn't check `covers_household`
itself, so a row that had already been explicitly turned off under 0081
got silently re-seeded and re-billed -- the exact opposite of what the
migration's own stated goal was. Fixed by adding
`covers_household = true` to the seeding query's WHERE clause, so a
declined household stays declined instead of being reset by the schema
change that removes the column recording that decision. General lesson:
a migration that "preserves existing behavior" for a boolean it's about
to drop must branch on that boolean's actual value per row, not just on
whether the feature area is active at all.
