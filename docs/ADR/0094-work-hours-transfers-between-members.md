# Work hours: members give surplus hours to other members

**Context:** Issue #243: "I have already done more than expected in my
work sessions, I can still do more hours in order to help other garden
members and sponsor these hours to them." The existing `Sponsorship`
is something else (an area someone looks after, credited as flat
hours), and crediting a session's attendance straight to someone else
was considered and rejected by kermie in favour of a transfer of the
year's balance.

**Decision:** A separate `HoursTransfer` row (giver, receiver, year,
hours, note, who entered it), on its own page `/work-hours/transfers`
and in the API.

- It enters the engine at one point: `calculate_hours_for_member()`
  adds it for the receiver and subtracts it for the giver. Everything
  downstream -- PER_PARCEL pooling, exemptions, the CSV, invoicing's
  `WORK_HOURS_SHORTFALL` -- sees it without being touched (ADR 0070's
  single engine).
- Only the surplus can be given, kermie's call: `transferable_hours()`
  -- PER_MEMBER: own total − requirement; PER_PARCEL: the plot's
  surplus, capped at the giver's own hours; exempt members and members
  without a plot that year: all their own hours (nothing is owed).
  Transfers made earlier already count in "own total", so a surplus
  can't be given twice.
- Checked at creation only. Recomputing every transfer on each later
  change (an attendance corrected afterwards) would need either
  cascading rejections or silently shrinking transfers; both are worse
  than the evaluation showing the giver short, which the board sees.
- Deleting a transfer is a real delete: it corrects a wrong entry, it
  doesn't end something that was true (ADR 0005 doesn't apply).

**Consequences:** One more source of hours per member, visible as its
own column ("Transfers", net) in the evaluation. Transfers between
co-tenants of one plot are allowed but net to zero under PER_PARCEL.
