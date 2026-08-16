# Calendar module

Four separate "calendars" (in the loose sense -- there's no month-grid
view anywhere, deliberately; every one of these is a simple upcoming-
items list, per the original feature request), each with its own ICS
export:

1. **Community calendar** -- member meetings, parcel inspections
   (entered directly), merged with STANDARD-type work sessions (read
   from the existing `work_sessions` table, not duplicated; SPECIAL
   sessions are excluded, see "Key decisions" below). Also has a JSON
   twin of its ICS feed (`/calendar/community.json`) for driving a
   styled widget rather than a calendar-app subscription -- see "REST
   API" below.
2. **Birthdays** -- derived entirely from `Member.date_of_birth`, no
   table of its own.
3. **Council presence** -- scheduled on-site slots for board/council
   members.
4. **Council absence** -- self-reported absence periods for any user
   account, not just the council.

## Data model

```
calendar_events    -- manually-created community calendar entries
                      (member meetings, parcel inspections, "other")
council_presence   -- scheduled on-site slots, one row per person per slot
council_absence    -- self-reported absence periods, one row per period
```

Notably absent: a `birthdays` table. See "Key decisions" below.

## Key decisions

**Work sessions are read directly, never duplicated into
`calendar_events`.** The tempting, obvious design is: whenever a work
session is created, insert a matching row into a generic calendar-events
table, so the community calendar has one uniform source. This was
deliberately rejected -- a copy immediately raises "what happens when
the original changes" (reschedule a work session, and now there are two
places with the date, one of them silently stale). Instead, the
community calendar's list view and its ICS feed both query
`CalendarEvent` and `WorkSession` separately and merge the results at
read time. One extra query, zero sync bugs, by construction.

**Only STANDARD-type work sessions appear on the community
calendar.** `WorkSession.type` (`SessionType.STANDARD` vs `SPECIAL`,
see `app/models.py`) already distinguishes a planned, signup-eligible
session from a spontaneous/unplanned one ("paint the garden bench
today"). The community calendar's whole point is helping members plan
ahead, so both the list view
(`app/routers/calendar.py::community_overview`) and the ICS feed
(`app/ics_utils.py::build_community_calendar`) filter to
`type == SessionType.STANDARD` -- a SPECIAL session simply never
appears there, in either place. Both filters need to stay in sync if
this is ever revisited; there's no shared query helper between the two
today since they're otherwise structured quite differently (one
renders a template, one builds an `icalendar.Calendar`).

**Birthdays are not stored anywhere.** A member's birthday calendar
entry is entirely computed from `Member.date_of_birth` each time it's
needed (`app/birthdays.py`). Correcting a birth date on the member
record is instantly reflected everywhere -- there's nothing to keep in
sync, because nothing is duplicated.

**"Round" birthday means a multiple of 10 (30th, 40th, 50th, ...).**
This is `ROUND_BIRTHDAY_INTERVAL` in `app/birthdays.py` -- change that
one constant if your association's convention differs (e.g. also
highlighting 25/75-style anniversaries).

**Two different birthday queries for two different purposes (issue
#99).** `upcoming_birthdays()` (the web page, `within_days=90` rolling
window from today) and `birthdays_for_year()` (the print PDF,
`/calendar/birthdays/pdf`) are deliberately separate functions rather
than one parameterized query: the web page is a "what's coming up"
dashboard-style list where entries drop off once their birthday
passes, while the PDF is a full-year reference meant to be printed once
and consulted all year, so everyone appears exactly once regardless of
today's date, grouped by (month, day) in calendar order (Jan-Dec), not
`Member.date_of_birth`'s literal chronological order (which would sort
by birth *year* first). `turning_age` in the PDF is "age reached in the
requested year," not "next occurrence from today" -- a January birthday
already past in a mid-year printout still correctly shows the age
turned this year, not next year's.
`app/birthday_calendar_pdf.py` renders it (WeasyPrint), grouped into
one heading row per month using `babel.dates.get_month_names(...,
context="stand-alone")` for the month name in the club's configured
language -- `context="stand-alone"` matters for languages with
grammatical case (Polish/Czech/Slovak's default "format" context
returns the genitive form used in phrases like "5th of March", not the
nominative name used for a standalone month heading).

**Shares its visual template with every other PDF in the app, via
`app/pdf_chrome.py`.** Requested explicitly: the header/footer chrome
(DIN-style fixed header with the logo at the true page edge and the
club name centered across the full sheet, the same color/font palette,
and a localized "Page X of Y") matches `app/invoice_pdf.py`'s
original look. First implemented as a duplicated copy of that CSS
directly in `birthday_calendar_pdf.py` (matching this codebase's
then-established convention of each PDF generator owning its full CSS
independently) -- then, once asked to apply the same treatment to the
work-session attendee sheet and meeting sign-in sheet too "from now
on," extracted into the shared `app/pdf_chrome.py` module instead (see
docs/ADR/0043), and this file switched to use it rather than keep its
own copy. The footer is the same three-column organization/register-
court/bank layout every other PDF now shows too (docs/ADR/0045) --
built from `app/pdf_chrome.py`'s `OrgFooterContext`/
`load_org_footer_context()`, loaded independently of the finances
module since it's club-identity data, not finances-owned.

**Two different privacy postures for the four ICS feeds, not one.**
This was the single most important design decision in this module, so
it gets its own ADR entry (see Architecture Decisions) -- summary: the
community calendar's feed is fully public and unauthenticated (needed
for the WordPress embed request), while birthdays, council presence,
and council absence all require a secret token, because member birth
dates and staff schedules are meaningfully more sensitive than "there's
a members' meeting on this date."

**One shared secret token for the whole installation, not per-user.**
`get_or_create_ics_token()` in `app/ics_utils.py` generates one token
(stored as the `ics_secret_token` ClubSetting) the first time any
private feed is requested, and every private feed uses the same token.
This is deliberately simple rather than maximally secure -- a small,
trusted club doesn't need per-user revocation, and per-user tokens would
meaningfully complicate both the code and the "here's your calendar
link" UX for very little real benefit at this scale. If per-user tokens
are ever needed (e.g. a much larger association, or wanting to revoke
one person's access without regenerating everyone's link), that's a
contained change scoped to `app/ics_utils.py` and each calendar page's
ICS subscribe dropdown (see "No central hub page" below).

**No member-ability data, again.** Same principle as the work-tasks
feature (see its own ADR entry): nothing here stores or reasons about a
member's health or ability. Council absence is a plain self-reported
date range with an optional free-text note -- the person logging it
decides what, if anything, to explain.

**No central hub page.** `/calendar/` originally rendered an overview
page listing all four calendars with a "View" button and ICS link for
each -- since the nav sidebar already links directly to every
sub-calendar, that page was pure duplication with an extra click in
front of it. Removed in favor of each sub-calendar page showing its
own ICS subscribe link directly (a small dropdown behind an RSS-style
icon in the page's toolbar, using `calendar.hub.ics_public_label` /
`ics_private_label` for the public/private distinction -- those two
translation keys were kept even though the rest of the old hub's keys
were removed, since they're still in active use). `/calendar/` itself
still exists as a plain redirect to `/calendar/community` rather than
disappearing outright, so an old bookmark or link still lands
somewhere useful instead of 404ing.

**Permission split:** creating/deleting community calendar entries and
council presence slots requires Admin/Board (these are "official"
announcements and internal coordination). Logging your OWN council
absence requires only being logged in at all, matching the explicit
request that "everybody with access to the system" can do this --
and deleting an absence entry is allowed for the entry's own owner or
for Admin/Board (for cleanup), never for anyone else.

## RFC 5545 detail worth knowing if you touch `app/ics_utils.py`

`DTEND` for an all-day (`VALUE=DATE`) event is **exclusive** per the
spec -- the day itself is not part of the event. `_add_event()` takes an
*inclusive* end day (the last day the event should visibly cover,
matching how a human reads a date range) and adds one day internally
before writing `DTEND`. Get this wrong and multi-day events render one
day short in real calendar apps (Google Calendar, Outlook, Apple
Calendar all follow the spec here) -- easy mistake to reintroduce if
this function gets refactored, so it's called out explicitly in its own
docstring too.

## REST API

**No conventional CRUD API for this module**, unlike every other module
in this project (see the API-first ADR entry). A full API for creating
meetings or presence slots is a reasonable follow-up if a real
integration need shows up, but wasn't built speculatively.

**One narrow exception (see [ADR
0073](./ADR/0073-community-calendar-json-endpoint-for-widget-rendering.md)):**
`GET /calendar/community.json`, a read-only JSON twin of
`/calendar/community.ics` -- same data (CalendarEvent rows plus
STANDARD work sessions), same public/unauthenticated posture, just JSON
instead of iCalendar. This exists specifically to drive the
`parcella-connector` WordPress plugin's `[parcella_calendar]` shortcode
(`integrations/wordpress/parcella-connector/includes/modules/calendar.php`),
which renders a styled HTML list matching the surrounding page/widget --
something a generic ICS-consuming calendar widget can't do. This is
*not* a reversal of the "ICS is the integration surface" reasoning
above for the module as a whole: it's one additional read-only endpoint
for one specific rendering need, not a general JSON API for the
calendar module. Write operations (creating meetings, presence slots,
etc.) still have no API and still aren't planned speculatively.

## Known pitfalls

- The first version of `build_council_presence_calendar()` and
  `build_council_absence_calendar()` accessed `entry.user` without
  eager-loading it via `selectinload` -- the exact async SQLAlchemy
  lazy-loading pitfall this project has hit before (see the dedicated
  ADR entry on this). Caught before shipping by testing the actual ICS
  output, not just the function in isolation.
- The first version of all four `build_*_calendar()` functions queried
  *every* row ever created, with no date filter -- meaning the ICS
  feeds would have grown forever, including years of past meetings,
  diverging from what the list-view pages already correctly showed
  (upcoming only). Fixed to filter consistently with their list views.
