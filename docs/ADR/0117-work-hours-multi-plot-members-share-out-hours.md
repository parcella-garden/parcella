# Work hours: a member holding several plots owes each plot, hours fill them in order

**Context:** Under `PER_PARCEL` the requirement is per plot, but hours
are per member (`calculate_hours_for_member()`). `evaluate_parcel()`
put a tenant's whole year on every plot they held, so one member with
G048 and G049 and 7.5 h of a 5 h requirement showed both plots as
fulfilled -- 7.5 h counted twice, 10 h owed. ADR 0092 had already
listed this as a known gap ("a member holding two plots at once still
counts on both") and fixed only the mid-year move case (`_moved_on()`).

**Decision:** After all of a year's parcel rows are built,
`evaluate_year()` runs `_share_out_multi_plot_hours()`. For every
member who is a tenant of more than one evaluated plot:

- Single-plot tenants count first, in full, on their plot (as before).
- Then the member's hours fill their plots in plot-number order: each
  plot gets what it still needs to reach the requirement; the last
  plot gets whatever is left (a surplus, or all of it if nothing was
  needed). An exempt plot needs nothing, so the hours go to the others.
- Sessions, sponsorship and transfers are split in the same proportion
  as the total, so a row's columns still add up and the CSV/API/
  invoicing (`WORK_HOURS_SHORTFALL`) need no change -- they read the
  same `tenant_details[].hours` and row totals as before.
- `tenant_details[].own_hours` keeps the member's full year; the page
  shows such a tenant as "5,0 of 7,5 h".
- `transferable_hours()` now evaluates the whole year (the share-out on
  one plot depends on the member's others) and adds up the member's
  credited surplus across their plots, instead of taking the smallest
  per-plot surplus of hours that were counted on each plot in full.

**Rejected:** splitting a member's hours evenly across their plots
(3.75 h + 3.75 h). Same total owed, but no plot ever shows fulfilled
until all are, and the invoice is split across plots for no reason.
kermie chose "fill in order".

**Consequences:** When two multi-plot members share a plot, the one
whose first plot comes first in plot-number order is shared out first
-- deterministic, but not an optimal allocation. Fine for real data
(couples holding the same two plots fill them the same way). Creating
a transfer now runs a full-year evaluation; that is one admin action,
not a page render.
