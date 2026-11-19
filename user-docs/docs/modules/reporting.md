# Reporting

Your club's key figures over time, as charts: how old your members are,
how membership has developed, how many plots were given up, how many
people apply, and how the work hours went. Handy for the annual report
or the general meeting.

!!! info "Who can use this"
    - The module switch is **Reporting** under **Administration →
      Turning modules on and off**. It is **on** by default.
    - The **Board** and **Administrator** roles, and members of a group
      with **Full access to every module**, can always see it.
    - Everyone else needs *read* on **Reporting** in one of their
      [groups](../administration/groups.md). The page only shows totals
      and counts, never names, so it doesn't also need access to members,
      work hours or applicants.

## Reporting page

![Reporting](../assets/screenshots/reporting/index.png)

Open **Reporting** in the menu. The page is read-only. Every figure is
worked out from your current data each time you open the page; nothing
is stored or needs updating. Time series show up to the last 10 years,
from the first year with data up to the current year. A past year is
counted as it stood on 31 December, the current year as it stands
today.

Each chart is a card with:

- the chart itself (hover over it to see the exact numbers);
- a grey note with an info icon where something needs explaining, for
  example how many members were left out;
- **Show figures as a table**, which unfolds the same numbers as a
  table, ready to copy. Pie charts add a **Share / total** column with
  the percentages, stacked charts a column with the total per year.

A chart without any data says **No data yet.**

Some charts only appear when their module is switched on: the applicant
charts need **Applicants**, the work-hours charts need **Work-hours management**,
and the electricity chart needs **Electricity management**.

## The charts

| Chart | What it counts |
|---|---|
| **Members by generation** | Pie chart of today's active members by year of birth: **Silent Generation (until 1945)**, **Baby boomers (1946–1964)**, **Generation X (1965–1980)**, **Millennials (1981–1996)**, **Generation Z (1997–2012)**, **Generation Alpha (2013 on)**. Members without a date of birth are left out; the note says how many. |
| **Members per year** | Line chart of the number of **Members** in each year: everyone whose "member since" date is on or before the end of that year and who hadn't left by then. Members with no join date are counted in every year; the note says how many. |
| **Cancelled plots per year** | Bar chart of **Leases ended** per year: every lease whose end date falls in that year, including end dates already set for later this year. A plot handed from one tenant to the next counts as one ended lease. |
| **Applicants per quarter** | Bar chart of new **Applicants** by the date they applied, for each quarter of last year and this year. |
| **Applicants per year** | The same per year. |
| **Work hours per year** | Stacked bars for each year that has a work-hours setup. Each plot (or member, see below) is counted in exactly one group, checked in this order: **Exempt**, **Pays the fee (hours short)**, **Fulfilled with sponsorship**, **Fulfilled by work sessions**. In years where work hours were owed per member instead of per plot, the note says "Counted per member instead of per plot in ...". |
| **Hours transfers per year** | Two bars per year: the number of **Transfers** of hours, and the **Hours transferred** in total. |
| **Plots with electricity** | Pie chart of today's active plots **With electricity connection** (at least one electricity meter on the plot) and **Without electricity connection**. |

!!! note "Things to keep in mind"
    - **Members by generation** and **Plots with electricity** show
      today only. Parcella doesn't keep snapshots, so it can't say what
      these looked like in an earlier year.
    - A member who was deleted (rather than given an end date)
      disappears from every past year too. End memberships instead of
      deleting members, and the history stays right.
    - Figures come from the data as entered. A missing join date or
      date of birth shows up in the notes; fix it on the
      [member](members.md) and reload the page.

There is no export button for the charts. Use **Show figures as a
table** to copy the numbers, for example into a spreadsheet or the
annual report.

## Related

- [Members](members.md) -- join dates and dates of birth.
- [Parcels](parcels.md) -- leases and their end dates.
- [Applicants](applicants.md)
- [Work hours](work-hours.md) -- exemptions, sponsorship and hours
  transfers.
- [Water and electricity](metering.md) -- electricity meters per plot.
