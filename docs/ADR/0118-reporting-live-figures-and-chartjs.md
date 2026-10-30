# Reporting: figures computed live, Chart.js as the chart library

**Context:** Issue #264 asked for a reporting module showing how club
data changes over time (age groups, members per year, cancelled plots,
applicants, work-hours outcomes, hours transfers, electricity), with
pie charts and "room for more KPIs". Parcella had no chart library and
no stored history of figures. Two questions followed: where the
numbers come from, and how they're drawn.

**Decision:**

- **Computed live, no snapshot table.** Every figure is derived from
  the existing tables each time `/reporting/` or `GET
  /api/v1/reporting` is asked (`app/reporting.py`). Time series are
  rebuilt from dates already stored: `member_since`/`member_until`,
  `MemberParcel.assigned_until`, `Applicant.applied_at`,
  `HoursTransfer.year` and the work-hours evaluation per configured
  year (`evaluate_year()`, the same engine as `/work-hours/evaluation`
  and invoicing).
- **Chart.js 4** from jsDelivr (pinned version), which the CSP already
  allows for the EasyMDE editor. The data reaches it as JSON in a
  `<script type="application/json">` block (`|tojson`), never as
  markup built in JS. Each chart also has a plain data table, which
  keeps the figures readable for printing and screen readers.
- **One function per figure plus a `SECTIONS` entry** (with the module
  flag it needs). A new KPI doesn't touch the router, template or API.

**Rejected:**
- *Yearly snapshots* in a new table. They would make "how many plots
  had electricity in 2023" answerable, but only from the day
  snapshotting starts, they need a scheduler, and they go stale when
  past data is corrected. The issue's figures can all be rebuilt from
  current data.
- *Server-rendered SVG charts.* No JavaScript and prints cleanly, but
  every chart type becomes hand-written drawing code, with no
  tooltips. kermie chose Chart.js.

**Consequences:**
- A figure is only as good as the dates behind it. Members without a
  join date count in every year (kermie's call, matching
  `active_member_filter()`), and the page says how many. Soft-deleted
  members drop out of every year, because nothing records when they
  were deleted.
- Figures that describe a *state* with no date history (electricity
  connections, generations) are shown for today only.
- The page runs `evaluate_year()` for up to 10 configured years on
  every load. That's fine at club scale (a few hundred plots). If it
  ever isn't, cache per request or per day, not in a table.
- Chart.js is a new third-party script on one page. Its version is
  pinned in `app/templates/reporting/index.html`.
