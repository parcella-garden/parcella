# Module: Insurance (Versicherungen)

> **Note on the renaming:** the code (models, tables, URLs, API
> endpoints) has been fully converted to English:
> `SachversicherungPaket` -> `PropertyInsurancePackage`,
> `VersicherungsKonfiguration` -> `InsuranceConfiguration`,
> `ParzelleVersicherung` -> `ParcelInsurance`,
> `UnfallversicherungZusatzperson` -> `AccidentInsuranceAdditionalPerson`,
> `/versicherungen/` -> `/insurance/`. Details and lessons learned in
> [Architecture Decisions](./ADR/0008-fourth-module-to-english-versicherungen-insurance.md).
> This page continues to describe the domain logic, which did not
> change in the process.

Manages two optional insurance types taken out per parcel: property
insurance (selectable package) and accident insurance (with automatic
household detection).

Module flag: `insurance`

## Data model

```
property_insurance_packages          – configurable packages per year (e.g. 40/60/80/100 EUR)
insurance_configuration              – year basis: accident base and additional amount
parcel_insurance                     – insurance status of a parcel for a year
accident_insurance_household_members – who of the detected household is actually covered (opt-out)
accident_insurance_additional_persons – who is additionally insured beyond the household (opt-in)
```

## Key decision: household detection via address comparison, coverage itself is opt-out per person

Accident insurance's flat base fee is meant for all residents of a parcel
who share **the same address** with each other (street, postal code, city
in the member record) -- one price regardless of household size, since
they live in the same household. There's no designated "primary"
resident to anchor this comparison on (that role distinction was
removed, see
[Architecture Decisions](./ADR/0018-removed-the-primary-co-tenant-role-distinction.md)); instead, current
residents are grouped by matching address to each other, and the largest
matching group is the detected household.

Residents with a **different address** are shown as candidates but **not**
added automatically -- the association deliberately decides per person
(checkbox) whether they should be additionally insured for the extra
amount. This was an explicit requirement: "can be additionally insured"
means opt-in, not automatic.

The detection itself happens in `household_grouping()`
(`app/insurance_utils.py`) and stays a display aid for *who counts as
household vs. external*, but unlike the additional-persons side,
household coverage **is** a real per-row decision in the database, not
just automatic: a `ParcelInsurance` row is seeded with every detected
household member checked/covered by default when first created
(`get_or_create_parcel_insurance` in `app/services/insurance.py`), and
each can individually be unchecked from there -- e.g. a leaser declines
coverage for themselves while a named additional person outside the
household stays insured (issue #204,
[Architecture Decisions](./ADR/0078-accident-insurance-per-household-member-opt-out.md)).
The base fee applies once if `accident_insurance_household_members` has
at least one row for that `ParcelInsurance`; billing is based on that
explicit selection, not a live recalculation of addresses -- so a
member's address changing later doesn't retroactively affect past
years' billing, same reasoning as the additional-persons side always had.

## "Insured parcels" counts only count real leaser coverage

`has_accident_insurance` on `ParcelInsurance` can be `True` while
`household_members` is empty -- that's exactly the state a leaser
reaches by opting out of their own coverage while a named additional
person (outside the household) stays opted in (see above). In that
state `calculate_insurance_cost()` already charges no household base
fee. Any "how many parcels are accident-insured" aggregate (the
`/insurance/` overview stat, the `/insurance/parcels` footer sum) must
apply the same rule -- `has_accident_insurance and household_members`,
not the flag alone -- otherwise a parcel where only a non-leaser is
covered gets counted as an insured parcel it isn't (issue #208).

## `/insurance/parcels` also lists terminated parcels, by default

A lease termination (`Parcel.status` -> `TERMINATED`) does not
automatically cancel the actual, external insurance contract -- so
`/insurance/parcels` includes `TERMINATED` parcels for a given year
alongside all `ACTIVE` ones (`_insurance_parcels_query()` in
`app/routers/insurance.py`, issue #207). This is why the query now
takes `year` as a parameter instead of being a static filter.

**Visibility defaults to shown, not hidden.** The first cut of #207
gated a `TERMINATED` parcel's visibility on already having a
`ParcelInsurance` row with either flag set for that year -- which is
backwards in practice: a parcel that was terminated before anyone
touched this year's insurance data has *no* row yet, so it was
invisible in the exact case the issue was about (confirmed against
real production data: three terminated parcels with zero insurance
history anywhere in the table). Corrected same-day: a `TERMINATED`
parcel is now excluded only once someone has explicitly reviewed it and
recorded a row for that year with **both** flags `False` -- i.e.
"checked, nothing to track." No row at all, or a row with either flag
set, both keep it visible.

## Configurable packages instead of fixed values

The property insurance packages (currently 40/60/80/100 EUR) are their
own table (`property_insurance_packages`), year-based, with a freely
editable number of packages and amounts -- not a hard-coded four-package
model. This follows the same principle as the work-hours configuration:
values that can change annually belong in a table, not in code.

## Known pitfalls

- Same `MissingGreenlet` pitfall as in the metering module: when a
  `ParcelInsurance` is created for the first time (when a parcel is
  opened for a year for the first time), the relationships must be
  explicitly reloaded after the commit before accessing `property_package`,
  `household_members`, or `additional_persons`. See
  `get_or_create_parcel_insurance()` in `app/services/insurance.py`.

## REST API

This module has (added after the fact) a complete set of REST API
endpoints for this module (JWT-authenticated, see `/api/docs`). See the
README for the endpoint overview. Background: early modules were
initially built as web UI only, with the API added later -- since then
the rule is that every new module gets **both** the web UI and API
endpoints **from the start** (see Architecture Decisions).

**Implementation note (ADR 0070):** configuration/package CRUD and the
parcel-insurance upsert (incl. "fully replace additional persons") now
live in `app/services/insurance.py`, called by both
`app/routers/insurance.py` and `app/routers/api_insurance.py`. The API
router also now checks permissions the same fine-grained, `Group`-based
way the HTML side does (`require_api_permission`), not the coarser
role-only check most other API routers still use.
