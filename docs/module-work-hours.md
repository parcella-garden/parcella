# Module: Work Hours (Pflichtstunden)

> **Note on the renaming:** the code (models, tables, URLs, API
> endpoints) has been fully converted to English:
> `Arbeitseinsatz` -> `WorkSession`, `Vereinsrolle` -> `ClubRole`,
> `Patenschaft` -> `Sponsorship`, `/pflichtstunden/` -> `/work-hours/`.
> Details and lessons learned in
> [Architecture Decisions](./ADR/0010-second-module-to-english-pflichtstunden-work-hours.md).
> This page continues to describe the domain logic, which did not
> change in the process.

Manages the annual mandatory work-hours requirement: standard and special
work sessions, sponsorships as an alternative, club roles with automatic
exemption.

Module flag: `work_hours` (see `app/module_flags.py`)

Signups made through the public signup API (see
`docs/module-public-api.md`) show up directly in this module's normal
participations table on `session_detail.html`, with status `REGISTERED`
and a `note` explaining they came from the public form (and, if the
submitted name couldn't be confidently matched, that every current
resident of the parcel was registered as a precaution -- see that doc
for why). No separate UI for them; they're real `SessionParticipation`
rows.

## Data model

```
work_hours_configuration – year-based hours/rate configuration
club_roles                – club offices (board, extended board, etc.)
member_club_roles         – member -> club role assignment (year-based)
work_sessions             – standard and special sessions
session_participations    – who attended which session, with hours
sponsorships              – area responsibilities (flat-rate credit)
work_tasks                – task backlog, optionally scheduled/assigned
```

## Key decisions

**Configurable billing mode.** Some associations bill mandatory hours per
member, others per lease (parcel). Both are configurable via
`WorkHoursMode` (`PER_MEMBER` / `PER_PARCEL`) instead of being hard-coded
-- an example of "what belongs generically in the product, not just in
our association".

**Tenant groups under PER_PARCEL.** When several people lease the same
parcel, their hours are added together against the parcel's single
requirement (not counted individually per person). One tenant might
contribute 2 hours, the other 3 -- together the 5 hours are fulfilled.

**Club-role exemption applies to the whole parcel.** If a member is on the
(extended) board and is therefore exempt from mandatory hours, that
exemption applies to the **entire parcel**, not just to the exempt
person -- the reasoning: the board position "covers" the rest of the
family/co-tenants. Implemented as `any()` (at least one tenant exempt ->
whole parcel exempt), not `all()`.

**Exemption applies per calendar year, not to the exact day.** If a board
member steps down in October, the exemption still applies for the whole
year. Only the following year is subject to the normal requirement again.
The `member_club_roles` table has a `year` field instead of pure date
ranges for exactly this reason.

**Sponsorships are projects, not assignments.** Originally the UI forced
you to assign a member immediately when creating a sponsorship. That was
changed: sponsorships ("areas") can be created without a member ("not yet
assigned") -- the real-world workflow is that the association first
advertises sponsorship areas and then assigns applicants. Multiple members
can share an area by creating multiple sponsorship rows with the same
area name (autocomplete via `<datalist>`) -- each gets the full hour
credit.

**`valid_from` is optional too, for the same "advertise before it's
claimed" reason (issue #213).** A sponsorship can be entered with no
member *and* no start date -- just an area name waiting for someone to
adopt it. `/work-hours/sponsorships` always shows these unclaimed rows
in the active table regardless of which year is selected (they don't
belong to a year yet), and a separate "Former Sponsorships" card below
lists everything whose `valid_until` has already passed, as a permanent
record independent of the year filter -- previously an ended sponsorship
simply vanished once its year fell out of view.

**The active table additionally requires "not yet ended as of today", on
top of the year-overlap check.** Without that, a sponsorship that ended
earlier in the *current* calendar year (e.g. `valid_until` in June, viewed
in September) would satisfy the existing-year window and show as
"active" while simultaneously appearing in the Former table below --
confusing and reported as a bug the same day this feature shipped. The
REST API's `GET /api/v1/work-hours/sponsorships?year=` deliberately does
*not* carry this extra restriction: it's a flat "what was active during
year X" historical query with no separate former/active split to be
confused by, so a past year correctly still returns sponsorships that
have since ended. One consequence: if a
member is attached to a sponsorship that still has no `valid_from`,
`calculate_hours_for_member` won't credit it for any year (the
`valid_from <= ...` comparison is NULL, hence excluded) until a start
date is actually set -- expected, not a bug: an unscheduled sponsorship
hasn't started yet. The member-select dropdowns (create card and edit
form) are labeled and sorted plot-number-first (`G001 - Peter Ahnert`),
not alphabetically by name -- kermie's follow-up request, since a large
club gets scanned by garden plot far more often than by surname. Members
with no current plot assignment sort last, after every plot-holder
(`_sort_members_by_plot` in `app/routers/work_hours.py`; the plot number
comes from `Member.parcel_assignments`, a Python-side sort since the
member list also needs to include people without any current parcel, which
a plain SQL join would drop or duplicate).

**Creditable hours are pre-filled from the current configuration**, but
remain freely editable (e.g. in case a sponsorship takes more effort than
the standard requirement).

**Tasks track a workload label, deliberately nothing about the person.**
The task backlog (`work_tasks`) has a three-stage lifecycle, each stage
optional: backlog (no session yet) -> scheduled (tied to a specific work
session) -> assigned (tied to one specific participant who signed up for
that session). Every task carries a `workload` (Light / Moderate /
Demanding) so whoever coordinates a session can hand out appropriately
matched work -- but that's the *only* thing the system tracks. There is
no field anywhere for a member's age, health, or ability, and no
automated matching of any kind; the actual pairing of task to person is
a manual judgment call made by the coordinator, who knows the people
involved. Rescheduling a task to a different session (or back to the
backlog) automatically clears any participant assignment, since an
assignment only makes sense for the session that person actually signed
up for -- enforced identically in the web UI and the REST API, with the
API additionally rejecting outright any attempt to assign a task to a
participant of a session other than the one it's currently scheduled to.

**The `/work-hours/` nav link carries two separate badges (issue
#217).** The first (amber, exclamation icon) is a "new members" badge,
unrelated to work-hours eligibility -- a general new-member visibility
feature (not tied into exemption/eligibility logic) that happens to
live on this nav entry because members newly showing up are relevant
context for whoever's organizing sessions. The count itself
(`count_new_members()`, `app/services/members.py`) and its
dashboard-tile and email counterparts are members-module concerns.

The second badge (blue, clipboard icon) IS work-hours-owned: a "new
work-session sign-ups" count (`count_new_participations()`,
`app/services/work_hours.py`) tracking recently-created
`SessionParticipation` rows, with the same dashboard tile / email
pattern, plus a "New" badge per row on the session detail page's
participant table (`session_detail.html`). Both badges share the same
stateless-rolling-window design; see
[ADR 0079](./ADR/0079-new-member-notifications-stateless-not-a-notification-center.md)
for the full design, including why the public self-service signup path
gets one digest email per call instead of one per row.

## Known pitfalls

- `SessionType` and `ParticipationStatus` had to be corrected to uppercase
  after the fact (like several other enums) -- see
  [Architecture Decisions](./ADR/0002-enum-values-always-uppercase.md) for the full
  explanation of this recurring bug.
- `session_detail.html` crashed with a 500 error for *any* session with
  at least one participant, for a long time -- a `sort(attribute=...)`
  filter referenced the old German attribute name (`mitglied.last_name`)
  from before the identifier rename instead of `member.last_name`. Found
  and fixed while building the task-assignment feature, since assigning
  a task to a participant meant actually loading that page with real
  participants for the first time in a while.
- When adding `work_tasks` via a migration, an explicit `CREATE TYPE`
  statement before `op.create_table(...)` failed with "type already
  exists" -- `sa.Enum(...)` used directly in a column definition inside
  `create_table` already creates the Postgres enum type automatically.
  Matches the pattern already used by every other enum column in this
  project's migrations; no separate `CREATE TYPE` needed.

## REST API

This module has (added after the fact) a complete set of REST API
endpoints for this module (JWT-authenticated, see `/api/docs`). See the
README for the endpoint overview. Background: early modules were
initially built as web UI only, with the API added later -- since then
the rule is that every new module gets **both** the web UI and API
endpoints **from the start** (see Architecture Decisions). The `tasks`
endpoints followed this rule from the start when they were added.

One current limitation worth knowing if you're integrating against
`PUT /api/v1/work-hours/tasks/{id}`: `TaskUpdate.session_id` can't
distinguish "this field wasn't sent" from "this field was explicitly
set to null" -- both arrive as Python `None`. To send a task back to
the backlog via the API, send an empty string (`"session_id": ""`)
rather than JSON `null`. Proper PATCH sentinel semantics would fix this
cleanly but felt like over-engineering for what's currently a single
field with this ambiguity; revisit if it becomes a real integration
pain point.

**Implementation note (ADR 0070):** the evaluation/exemption engine
(`get_config_for_year`, `calculate_hours_for_member`, `is_exempt`,
`evaluate_year`/`evaluate_parcel`/`evaluate_member`) plus configuration
upsert, club-role/assignment CRUD, session/participation CRUD,
sponsorship CRUD, and task scheduling/assignment now live in
`app/services/work_hours.py`, called by both `app/routers/work_hours.py`
and `app/routers/api_work_hours.py`. This was the headline fix of the
whole ADR 0070 rollout: the evaluation engine used to be reimplemented
independently 3 times (the HTML evaluation page, the HTML CSV export --
which only ever supported PER_PARCEL mode, unchanged -- and the API,
which imported the HTML router's private helper functions directly, a
fragile shape this replaces). That exact duplication already caused a
real shipped bug once: an inverted `all()`-copy of the "any exempt
tenant exempts the whole parcel" rule. All three now compute a row's
standing through one path, so that mistake can't be reintroduced
independently in a fourth place. Also closed: `MemberClubRole` has no
DB uniqueness constraint, so the API's assignment-create used to allow
silent duplicates for the same (member, role, year) where the HTML side
already checked first -- now shared, surfaced as a 409 via the API. The
API router also now checks permissions the same fine-grained,
`Group`-based way the HTML side does (`require_api_permission`), not
the coarser role-only check most other API routers still use.

## Attendee sheet (PDF)

`/work-hours/sessions/{id}/attendee-sheet` (button on the session
detail page) generates a PDF via `app/session_attendee_sheet.py`
(WeasyPrint): one row per registered participant, with parcel, member
name, expected hours, any task assigned to them for this session, and
a blank signature line. Meant for printing and bringing to the actual
session, so the coordinator can confirm attendance/hours on paper
rather than at a laptop.

**Hours shown are a starting point, not a locked value.** If the
participation has an `hours_completed` override, that's shown;
otherwise it falls back to the session's `hours_per_participant`
default; if neither exists, the field is blank. Either way it's meant
to be corrected by hand on the printout to match what actually
happened, then entered back into Parcella afterward -- this PDF
doesn't feed back into the database itself.

**A task field is left blank, not "Not assigned" or similar, when no
task has been assigned to that participant yet** -- explicit product
requirement, so the coordinator can write one in by hand on the
printed page rather than the PDF asserting an absence that might just
be "not decided yet."

**Sorted by (current parcel, last name, first name)**, same ordering
convention as the general-meeting sign-in sheet
(`app/meeting_signin_sheet.py`) and the member list itself -- makes a
specific attendee easy to find on a printed page by which garden plot
they're from.

**Multi-page, not one-page-constrained**, for the same reason as the
meeting sign-in sheet: a real session's attendee count can exceed what
fits on one page, and there's no sensible way to "shorten" a list of
people who need to sign in.


