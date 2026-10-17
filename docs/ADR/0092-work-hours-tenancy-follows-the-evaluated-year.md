# Work hours: who counts as a tenant follows the evaluated year, not today

**Context:** The work-hours evaluation decided who owes hours with
`MemberParcel.is_current` -- "is this lease in effect *today*?". Issue
#206 had asked for exactly that ("former leasers -- lease end date in
the past -- shall not appear"). Issue #239 then showed the gap: a tenant
who cancels in June vanished from that year's evaluation, and from the
`WORK_HOURS_SHORTFALL` invoice line, although cancelling a lease
doesn't cancel the hours owed for the year. "Today" was also simply
wrong for past years: evaluating 2025 in 2026 used 2026's tenants.

**Decision:** A tenant, for the evaluation of year *Y*, is anyone whose
tenancy was in effect on at least one day of *Y*:
`assigned_from` empty or ≤ Dec 31, and `assigned_until` empty or > Jan 1
(strict, like `is_current`: the tenancy is already over on its
`assigned_until` day). Python: `MemberParcel.overlaps_year()`; SQL:
`tenant_in_year_filter()` in `app/database.py`.

- The obligation is the **full** year, not pro rata (kermie's call).
- PER_PARCEL: a leaver stays on the parcel's row, pooled with the
  successor against the parcel's single requirement -- the parcel owes
  the hours once, as it always did with co-tenants.
- PER_MEMBER: the leaver keeps their own row and is billed directly.
- Both #206 and #239 hold: a lease that ended *before* the year doesn't
  count, one that ended *during* it does. Rows of leavers carry a
  "lease ended" badge.
- A member who moved to another plot of the club during the year
  counts only on the new plot -- their hours and exemption are per
  member and must not fulfil two plots.
- `TERMINATED` parcels are evaluated too; `DELETED`/`COMMUNAL` aren't.
- `compute_work_hours_shortfalls()` (invoicing) now takes its rows
  from `evaluate_year()` instead of running its own parcel/member
  queries, which had already drifted (PER_MEMBER billed anyone who ever
  held a lease) -- same single-engine reasoning as ADR 0070.

**Consequences:** `is_current` stays the rule everywhere else (invoice
addresses, sign-in sheet, member pickers): those are about *now*. Only
year-scoped obligations use `overlaps_year`. Known gaps, documented in
docs/module-work-hours.md: a parcel left vacant can't be billed through
the parcel invoice (no current invoice address), a re-let parcel bills
the pooled shortfall to the successor, and soft-deleted members drop out
of every year.
