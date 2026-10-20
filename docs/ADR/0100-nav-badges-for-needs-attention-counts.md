# Nav badges for the dashboard's "needs attention" counts

**Context:** the work-hours nav entry already showed a badge with the
number of recent work-session sign-ups (ADR 0079). kermie wanted the same
for new applicants, and also for purchase requests, support conversations
"and all other things" that someone should look at.

## Decision: one badge per actionable dashboard tile, same count

The dashboard already has a tile for each of these, and each tile counts
exactly what its link lists (ADR 0019). The badges reuse those counts
without changing them:

| Nav entry | Badge counts | Clears when |
|---|---|---|
| Applicants | status `NEW` | someone moves the applicant on (Contacted, Rejected, ...) or deletes it |
| Purchase requests | status `OPEN` | the request is approved or rejected |
| Support (FreeScout) | conversations not in `HIDDEN_STATUSES` | the conversation is closed in FreeScout (next sync) |
| Tasks | `due_date` in the past | the due date is moved or the task deleted |

The queries live in `app/nav_counts.py` (`load_nav_counts()`). A single
middleware (`nav_counts_middleware` in `app/main.py`, previously
`new_participations_count_middleware`) runs them once per logged-in
request and puts them on `request.state.nav_counts`. The nav (Jinja
global `nav_count(request, key)`) and the dashboard (`startseite()`) both
read from there. Before this, the dashboard ran these queries itself.
Having one source means a badge and its tile can't disagree.

## Stateless, like ADR 0079

There's no per-user "seen" state and no migration. Each badge only
reflects the status or date the item already has, so it goes away once
the item is dealt with. A "mark as seen" button would only hide the
number without changing anything about the item. ADR 0079 already
decided against building a notification center for this kind of signal.

## Gating

A badge is part of its nav entry's markup, so it only shows when that
entry does: when the module is on and the user has the permission.
The support badge is only on the internal `/freescout/` link, not on the
external FreeScout link shown to users without `freescout_bridge`
permission. The middleware runs before the module-flag and permission
middlewares (Starlette runs later-registered middlewares first), so it
counts unconditionally. That's four indexed `count(*)` queries, cheap
enough that skipping them per module isn't worth the extra code.

## Colour

Info-blue (`bg-info text-dark`) is used for "something new to look at",
the same as the work-sessions badge. Overdue tasks get red
(`bg-danger`) because they're already a problem, not just new.

## Not included

- Unpaid incoming invoices: they have no status column. "Unpaid" would
  mean comparing summed line items against summed payments, and there's
  no dashboard tile for it yet. If it's ever wanted, add the tile and
  the badge together in `load_nav_counts()`.
