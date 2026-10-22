# Manual spam marking and backlog re-scan: track human review to protect it from automation

**Note: retired.** The spam filter was removed with the built-in ticket
module (ADR 0080); its leftovers went in [ADR 0103](./0103-spam-filter-leftovers-removed.md).
Kept as the design record.

**Context:** the ticket spam filter (`app/spam_filter.py`, stage 3 --
see `docs/module-tickets.md`, and [ADR 0038](./0038-spam-filter-external-api-tied-to-apilayer-for-now.md)/[ADR 0066](./0066-spam-filter-external-api-back-to-a-generic-contract.md)
for the external-API side of it) only ever ran automatically, once, on
arrival of a new incoming email. There was a one-way escape hatch for
false positives (a "Not spam" button clearing `spam_suspected`), but no
way to flag a ticket the automated check missed, and no way to apply
an improved or newly-configured check retroactively to tickets that
already existed before the check (or its external API) was set up.

**Decision: two additive UI actions, plus a field to protect one from
the other.**

1. **Manual marking**, mirroring the existing "Not spam" button: "Mark
   as spam" on the ticket detail page (single ticket) and in the
   overview's bulk-select toolbar (multiple at once). Both set
   `spam_suspected` directly -- no score, no reasoning, since there's
   no heuristic behind a human's judgment call.
2. **Backlog re-scan** (`POST /tickets/rescan-spam`, a button in the
   overview topbar next to the existing "Fetch inbox now"): runs
   `check_for_spam()` against existing tickets that predate a check (or
   a check reconfiguration) that would have caught them.

The problem the re-scan creates on its own: a ticket a board member
deliberately cleared as a false positive looks identical in the
database to one nobody has ever looked at -- both just have
`spam_suspected = False`. Re-running the same heuristics/API that were
wrong once could re-flag it, silently overriding a human decision with
the same automation that already failed that ticket.

**Fix: `tickets.spam_reviewed_by_id` / `spam_reviewed_at`.** Set by
every human-driven path -- the mark/not-spam buttons, their bulk
equivalents, and the API's `PUT /{id}/spam-status` -- and *only* by
those paths, never by the automated check (arrival-time or re-scan).
The re-scan's query excludes any ticket where this is set, so it only
ever touches tickets no person has made a call on. A ticket a human
un-flagged stays un-flagged through any number of future re-scans; a
ticket a human flagged stays flagged. The field doubles as an audit
trail (who overrode the filter, and when) for free.

**Why a re-scan and not just "trust the automated check going
forward":** the automated check literally never re-runs for a ticket
once created (see module doc: "only runs on new tickets, not
replies"). Without a manual catch-up mechanism, any ticket predating a
spam-check configuration change -- including this club's own case,
configuring an external API for the first time after the deployment
already had a ticket backlog -- would simply never benefit from it.

**Why capped at `RESCAN_SPAM_BATCH_LIMIT` (200) tickets per run,
rather than the whole backlog at once:** the re-scan runs synchronously
inside one HTTP request, and each external-API call carries its own 5s
timeout (`app/spam_filter.py`). An unbounded backlog could turn one
button click into a request that hangs for minutes or times out
outright. Capping keeps a single run bounded and fast; the result
message tells the user to run it again if the cap was hit, rather than
silently leaving tickets unscanned with no indication more work
remains.

**Why not scope the re-scan to `CLOSED` tickets too:** spam suspicion
matters for triage -- keeping closed conversations out of the "Active"
view isn't a live concern the same way an open ticket cluttering the
inbox is. Closed tickets are excluded to keep each run cheap and
focused on what's operationally relevant; nothing stops a future
change from widening the scope if that turns out to matter.
