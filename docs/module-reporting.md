# Module: Reporting

Club figures over time as charts, at `/reporting/` (issue #264). The
data is also available at `GET /api/v1/reporting`. Everything is read-only and computed live
from existing tables, with no stored snapshots. See [ADR 0118](./ADR/0118-reporting-live-figures-and-chartjs.md).

- **Module flag:** `modul_reporting`, on by default. It's read-only
  aggregates of internal data, with no public endpoint and no outbound
  credentials.
- **Permission:** `reporting` read, in the group permission matrix.
  ADMIN/BOARD always have it. It shows aggregates only, so it doesn't
  also require read access to work hours, applicants or metering.
- **Sections follow their module.** The applicant figures need
  `applicants`, work hours and transfers need `work_hours`, and
  electricity needs `electricity`. If that module is off, the section
  is hidden.

## Figures and their definitions

Time series cover at most the last 10 years, starting at the first
year with data and ending with the current year. A year is measured on
31 Dec, or today for the current year.

| Figure | Definition |
|---|---|
| Members by generation | Active members (`active_member_filter()`) grouped by birth year: Silent ≤1945, Boomers 1946–64, Gen X 1965–80, Millennials 1981–96, Gen Z 1997–2012, Alpha 2013+. Members without a date of birth are left out, and a note says how many. |
| Members per year | Non-deleted members whose `member_since` ≤ that day and whose `member_until` is empty or ≥ that day. **A blank `member_since` counts in every year** (kermie's call), with a note giving the number. |
| Cancelled plots per year | Leases (`MemberParcel`) whose `assigned_until` falls in the year, including end dates already scheduled for the current year. **A lease ending counts as a cancelled plot** (kermie's call). Parcel status changes were rejected because the change history only reaches back to July 2026. |
| Applicants per quarter / per year | By `applied_at`. The quarter view shows the previous and the current year. |
| Work hours per year | Only years with a `WorkHoursConfiguration`, using the rows of `evaluate_year()`. **Each row lands in exactly one category**, checked in this order: exempt → owes the fee (`outstanding_hours > 0`) → fulfilled with sponsorship hours → fulfilled by sessions. A row is a plot in PER_PARCEL years and a member in PER_MEMBER years, and a note names those years. |
| Hours transfers per year | Number of `HoursTransfer` rows and their total hours, by `year`. |
| Plots with electricity | Today only: `ACTIVE` parcels with at least one `MeteringPoint` (medium ELECTRICITY, type PARCEL) vs. without. |

## How it's built

- `app/reporting.py`: one async function per figure, each returning a
  `Report` (`labels`, `series`, optional note).
  - Years and quarters are plain labels. Categories are stable ids
    (`boomers`, `owes_fee`). The page translates them as
    `reporting.<report key>.<id>`, and the API returns the ids.
  - `SECTIONS` sets the page order and the module flag each section
    needs.
- `app/routers/reporting.py` adds the translated texts. The template
  hands the data to Chart.js as JSON and also renders a collapsible
  data table per chart.
- `app/routers/api_reporting.py` returns the same reports, with schemas
  `ReportingOut`/`ReportOut` in `app/schemas.py`.

## Adding a figure

1. Write `async def my_report(db, today) -> Report` in
   `app/reporting.py`, and add `(my_report, "<module flag or None>")`
   to `SECTIONS`.
2. Add `reporting.<key>.title`, `reporting.<key>.series_<series key>`
   and, for categorical labels, `reporting.<key>.<label id>` to all 7
   translation files.
3. Add a test in `tests/test_reporting.py`.

## Known gaps

- Figures with no date history (electricity, generations) are shown
  for today only. Answering "how was it in 2023" would need snapshots,
  which ADR 0118 rejects for now.
- Soft-deleted members disappear from every past year.
- Nothing is exported yet (no CSV or PDF of a chart). The data tables
  and the API cover copying the numbers.
