# New-registration notifications: a stateless rolling window, not a notification center

*(Filename retained from the original new-member-only scope; this ADR now also covers new work-session sign-ups -- see "Extended to work-session sign-ups" below.)*

**Context:** issue #217 -- kermie wanted to be told about newly
registered members across four surfaces (dashboard, a nav badge on
`/work-hours/`, email, and a "mayhap" topbar icon). Parcella had no
notification system at all before this: no bell icon, no
`Notification` table, no per-user read/unread state, no nav badges
anywhere. This is the first feature of its kind, so the shape chosen
here is a precedent future notification-style features should follow
or deliberately diverge from -- not re-derive from scratch.

**Scope correction, same issue:** the first implementation pass read
"newly registered ... members for work sessions" as meaning new
`Member` accounts. Kermie clarified after using it that it actually
meant a member being newly signed up as a participant **on a work
session** (a new `SessionParticipation` row) -- and wanted both kept:
the new-Member notification below, plus a second, parallel one for new
session sign-ups (see "Extended to work-session sign-ups" below). Two
genuinely different trigger events, sharing the same three surfaces and
the same stateless design.

## Decision: stateless, not stored

`count_new_members()` (`app/services/members.py`) counts currently-
active members created in the last `NEW_MEMBER_WINDOW_DAYS` (14) days,
recomputed fresh on every request via `new_members_count_middleware`
(`app/main.py`) -- no new table, no migration, no per-user "seen"
state. A member is simply "new" until the window passes, for everyone,
identically.

This was a deliberate, scoped choice, not an oversight:

- Matches this codebase's existing convention for day-count thresholds
  -- `ROUND_BIRTHDAY_INTERVAL` (`app/birthdays.py`), `INVITATION_VALID_DAYS`
  (`app/auth.py`) -- plain module constants, never a `ClubSetting` row.
- A real notification center (per-user dismissal, a stored model) is a
  materially bigger build for a small club-management tool where "N
  people joined in the last two weeks" is genuinely enough signal --
  nobody needs to individually acknowledge each one.
- If a future feature genuinely needs per-user read/unread tracking
  (e.g. ticket assignment notifications), that's a new, separate
  concern -- don't retrofit statefulness onto this window-count instead
  of building it properly for whichever feature actually needs it.

## Scope: 3 of the 4 requested surfaces, not 4

Dashboard tile + `/work-hours/` nav badge + email shipped. The topbar
icon was explicitly hedged in the issue ("mayhap") and would have
required inventing the app's first piece of *global* topbar content --
today `.topbar` (`base.html`) only carries a per-page `topbar_actions`
block, no shared markup at all. Deferred as a fast-follow once the
other three prove useful, rather than building new shared chrome
speculatively.

## Email: single-member creation only, actor excluded

`notify_new_member()` (`app/services/members.py`) emails active
Admin/Board users, **excluding** whoever performed the creation (they
obviously already know) -- called from the two single-member creation
call sites (`app/routers/members.py::member_create`,
`app/routers/api_members.py::member_create`), both of which share
`create_member()` (ADR 0070).

**Deliberately NOT called from CSV bulk import**
(`app/routers/members.py::members_import_csv`) -- that path builds
`Member` rows directly in a per-row loop rather than going through
`create_member()`, and even if it did, one email per imported member
would spam Admin/Board on a large import. An importer already knows
what they just imported; no notification needed there. If a digest-
style "N members imported via CSV" summary is ever wanted, that's a
separate, explicit addition to `members_import_csv` -- not something
`notify_new_member()` should grow a batch mode for.

Localization follows the ADR 0070 pattern already established by
`assign_ticket()` (`app/services/tickets.py`): the caller resolves
`lang` from `request.state.language` and passes it in, rather than the
service function taking a `Request` -- keeps the service layer
transport-agnostic (same function serves both the HTML router and the
JSON API router).

## Extended to work-session sign-ups (also issue #217)

`count_new_participations()`/`notify_new_participation()`/
`notify_new_participations_digest()` (`app/services/work_hours.py`)
mirror the member-side functions exactly -- same
`NEW_PARTICIPATION_WINDOW_DAYS` (14) constant shape, same stateless
`new_participations_count_middleware` (`app/main.py`), a **second,
separate** nav badge on `/work-hours/` (not merged into the members
count -- they're different concepts, and one opaque combined integer
would be less useful than two small distinguishable badges), a second
dashboard tile, and a "New" badge per row on the session detail page's
participant table (`session_detail.html`) -- the same treatment
`recent_members` got on the dashboard.

The count is **status-agnostic**: any `SessionParticipation` created in
the window counts, regardless of its current `REGISTERED`/`ATTENDED`/
`NO_SHOW` status. The staff add-participant form's default status is
actually `"ATTENDED"` (it's normally used to retroactively record who
showed up, not to pre-register someone) -- still counts, since it's
still a new participation record either way, and "newly registered" is
about when the row was created, not what it currently says.

**Two structurally different creation paths needed two different email
shapes**, unlike the member side's single `create_member()` choke
point:

- **Staff-initiated** (`app/routers/work_hours.py::participant_add`,
  `app/routers/api_work_hours.py::participation_create`) -- both call
  the shared `add_participation()` (`app/services/work_hours.py`),
  which returns `None` as a no-op if the member is already registered
  for that session. `notify_new_participation()` is only called when a
  row was actually created, one email per creation, actor excluded --
  same shape as `notify_new_member()`.
- **Public self-service signup**
  (`app/routers/api_public.py::submit_signup`, behind the
  `public_signup_api` module flag, off by default, ADR 0024) -- this
  path is **actorless** (token-authenticated, not a logged-in user) and
  can create **several** rows in one call: multiple sessions selected
  at once, and an ambiguous name match falls back to registering every
  current tenant of the parcel. A per-row email here would spam
  Admin/Board the same way one email per CSV-imported member would (see
  "Email: single-member creation only, actor excluded" above) --
  instead `notify_new_participations_digest()` sends **one** summary
  email per API call ("N new sign-up(s) via public signup") to every
  active Admin/Board user, with no actor to exclude. This is the same
  "bulk path gets a digest, not per-row spam" reasoning as CSV import,
  applied a second time -- worth naming as a pattern: any future bulk-
  creation path in this app should default to a digest, not silence
  *or* a flood, unless there's a specific reason to choose otherwise.

## Known gap

`docs/module-members.md` doesn't exist yet. Not created as part of
this ticket (out of scope) -- flagging it here so it isn't lost. A
future pass that documents the members module properly should fold
this ADR's content in as that module's "new member notifications"
section rather than leaving it permanently ADR-only.
