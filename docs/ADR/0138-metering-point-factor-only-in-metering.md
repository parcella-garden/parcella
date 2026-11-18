# The metering point factor stays inside the metering module

**Context:** Issue #341: a bulk buyer's main electricity meter counts
through current transformers, so its display shows 1/20 of the real
consumption. To compare the main meter with the sum of the parcel and
club points, its consumption needs a multiplier.

**Decision:** `MeteringPoint.factor` (default 1), for water and
electricity points alike.

- **On the metering point,** as the issue asks: it describes the
  connection, and it stays when a meter is exchanged.
- **Readings stay raw display values.** Converting at entry would make
  people do arithmetic at the meter and break monotonicity against
  older readings. The multiplication happens when consumption is
  computed: `point_consumption()` and `total_consumption_for_type()`
  pass the point's factor to `calculate_consumption()`.
- **Metering only.** `calculate_consumption()` defaults to no factor;
  only the metering module's own views, exports and API pass it.
  Usage-based invoice items and other modules keep using the raw
  difference -- kermie: the factor is "just for metering points ...
  nothing else". Making it reach invoices would be a separate, explicit
  decision.

**Rejected:** a factor per meter (it would follow meter exchanges and
keep earlier years exact, but the issue and the club think of it as a
property of the point).

**Consequences:** changing a point's factor changes the consumption it
shows for every year, past ones included. A parcel point with a factor
would show multiplied consumption in metering but be invoiced on the raw
difference.
