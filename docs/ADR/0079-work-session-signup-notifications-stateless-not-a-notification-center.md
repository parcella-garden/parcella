# Work-session sign-up notifications: a stateless rolling window, not a notification center

**Context:** issue #217 -- kermie wanted to be told, via any of the
dashboard/nav/email, whenever somebody registers for a work session,
whether that happens through the public web sign-up form or through a
board member manually adding a participant on a session's detail page.
Parcella had no notification system at all before this: no bell icon,
no `Notification` table, no per-user read/unread state, no nav badges
anywhere. This is the first feature of its kind, so the shape chosen
here is a precedent future notification-style features should follow
or deliberately diverge from -- not re-derive from scratch.

*(An earlier pass on this same issue also built a "new Member account
created" notification, from misreading "newly registered ... members
for work sessions" as being about Member records rather than session
sign-ups. That was wrong and has been removed entirely -- this ADR
covers only what was actually asked for.)*

## Decision: stateless, not stored

`count_new_participations()` (`app/services/work_hours.py`) counts
`SessionParticipation` rows created in the last
`NEW_PARTICIPATION_WINDOW_DAYS` (14) days, recomputed fresh on every
request via `new_participations_count_middleware` (`app/main.py`) --
no new table, no migration, no per-user "seen" state. A sign-up is
simply "new" until the window passes, for everyone, identically.

This was a deliberate, scoped choice, not an oversight:

- Matches this codebase's existing convention for day-count thresholds
  -- `ROUND_BIRTHDAY_INTERVAL` (`app/birthdays.py`), `INVITATION_VALID_DAYS`
  (`app/auth.py`) -- plain module constants, never a `ClubSetting` row.
- A real notification center (per-user dismissal, a stored model) is a
  materially bigger build for a small club-management tool where "N
  people signed up in the last two weeks" is genuinely enough signal --
  nobody needs to individually acknowledge each one.
- If a future feature genuinely needs per-user read/unread tracking
  (e.g. ticket assignment notifications), that's a new, separate
  concern -- don't retrofit statefulness onto this window-count instead
  of building it properly for whichever feature actually needs it.

## Surfaces: dashboard tile, nav badge, email -- no topbar icon

A dashboard tile (gated on `request.state.module_flags.work_hours`,
matching the existing `purchase_requests`/`tickets`/`tasks` tile
pattern), a badge on the `/work-hours/` nav entry (`base.html`), a
"New" badge per row on the session detail page's participant table
(`session_detail.html`), and an email to active Admin/Board users.
No topbar icon -- there's currently no shared global content in
`.topbar` at all (only a per-page `topbar_actions` block), and nothing
in the original ask called for one.

## Count is status-agnostic, but not session-agnostic

Any `SessionParticipation` created in the window counts, regardless of
its current `REGISTERED`/`ATTENDED`/`NO_SHOW` status. The staff
add-participant form's default status is actually `"ATTENDED"` (it's
normally used to retroactively record who showed up, not to
pre-register someone) -- still counts, since it's still a new
participation record either way, and "newly registered" is about when
the row was created, not what it currently says.

**Correction, found in real use:** the first version counted a new
participation regardless of its *session's* own type or date, which in
practice surfaced 83 "new" sign-ups spanning SPECIAL (spontaneous)
sessions and long-past STANDARD sessions where staff were simply
recording historical attendance -- noise nobody needed to act on, since
"here's who newly signed up" only makes sense for a session someone
could still plan around. `count_new_participations()` now also requires
`WorkSession.type == SessionType.STANDARD` and `WorkSession.date >=
today` (`app/services/work_hours.py`) -- same STANDARD-only distinction
the community calendar and the public signup API both already draw,
applied here too. The session-detail "New" badge and the overview
list's per-session pill (`session_detail.html`, `overview.html`) follow
the same rule: a participation on a SPECIAL or already-past session
never shows a "New" badge, however recently it was actually created.

## Two structurally different creation paths needed two different email shapes

- **Staff-initiated** (`app/routers/work_hours.py::participant_add`,
  `app/routers/api_work_hours.py::participation_create`) -- both call
  the shared `add_participation()` (`app/services/work_hours.py`),
  which returns `None` as a no-op if the member is already registered
  for that session. `notify_new_participation()` is only called when a
  row was actually created, one email per creation, with the acting
  user excluded from the recipients (they obviously already know).
- **Public self-service signup**
  (`app/routers/api_public.py::submit_signup`, behind the
  `public_signup_api` module flag, off by default, ADR 0024) -- this
  path is **actorless** (token-authenticated, not a logged-in user) and
  can create **several** rows in one call: multiple sessions selected
  at once, and an ambiguous name match falls back to registering every
  current tenant of the parcel. A per-row email here would spam
  Admin/Board on a household sign-up -- instead
  `notify_new_participations_digest()` sends **one** summary email per
  API call ("N new sign-up(s) via public signup") to every active
  Admin/Board user, with no actor to exclude. Worth naming as a
  pattern: any future bulk-creation path in this app should default to
  a digest, not silence *or* a flood, unless there's a specific reason
  to choose otherwise.

Both email paths use the same recipient rule: `select(User).where(role
IN (ADMIN, BOARD), is_active == True)` (`_active_admin_board_recipients()`
in `app/services/work_hours.py`), matching the existing pattern used
elsewhere for admin/board lookups (`app/sample_data.py`,
`app/permissions.py`).

Localization follows the ADR 0070 pattern already established by
`assign_ticket()` (`app/services/tickets.py`): the caller resolves
`lang` from `request.state.language` and passes it in, rather than the
service function taking a `Request` -- keeps the service layer
transport-agnostic (same function serves both the HTML router and the
JSON API router).

## "Mark reviewed": a small escape hatch from the stateless design, not a reversal of it

Once a board member had actually looked at a session's new sign-ups,
the badges kept showing for the rest of the 14-day window regardless
-- annoying in practice, but the fix is deliberately *not* the full
per-user read/unread system this ADR's opening section argued against
building. Instead: one nullable `WorkSession.signups_reviewed_at`
timestamp, set by a "Mark reviewed" button on the session detail page
(`mark_signups_reviewed()`, `app/services/work_hours.py`). A
participation only counts as new if it's both inside the rolling
window *and* newer than this timestamp (`NULL` = never reviewed, no
extra filtering) -- so reviewing clears what exists right now, but a
member who signs up five minutes later still shows as new again. This
is session-scoped and boolean (reviewed or not), not per-user or
per-participation -- deliberately simpler than "did user X see
participation Y," matching this feature's existing small-club
proportions rather than growing toward a real notification center one
button at a time.

## Known gap

`docs/module-work-hours.md` has a note pointing here (see its "Key
decisions" section), but there's no standalone "notifications" section
in that doc yet -- folded into this ADR for now rather than duplicated.
