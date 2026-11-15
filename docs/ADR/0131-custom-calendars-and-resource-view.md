# Custom calendars: events with a calendar_id, never public; resources view

**Context:** issue #314. Besides the built-in calendars (community,
birthdays, council presence/absence), the board wants its own: e.g.
clubhouse bookings, board meetings. kermie's calls (2026-11-15):
admin-defined calendars, not personal ones, and for resources (cars,
rooms, keys, tables...) just show current inventory loans, with no
reservations yet.

## Decision

- **`CustomCalendar`** (name, colour, description, `full_access_only`,
  `is_active`). Only full-access users (ADMIN/BOARD or an equivalent
  group) create, edit and archive them, under Calendar → My calendars.
  Entries need the calendar module's write/delete permission, like the
  community calendar.
- **Entries are `CalendarEvent` rows with `calendar_id` set.** There's
  no second event table: same fields, same ICS rendering. `NULL` keeps
  meaning "community calendar", so existing rows didn't move.
  - **The sharp edge:** the community calendar's page, its *public*
    `community.ics` and `community.json`, and the community delete
    route all filter on `calendar_id IS NULL`. A new query on
    `CalendarEvent` for the community calendar must do the same, or
    private entries leak onto the club's public website. A test
    asserts this for all three URLs.
- **Never public.** The page needs calendar read permission. A
  `full_access_only` calendar answers 404 (not 403) to everyone else,
  so its existence doesn't leak either. Its ICS feed
  (`/calendar/custom/{id}/feed.ics`) uses the installation's ICS token,
  like the council feeds.
- **Archive, don't delete** (ADR 0005). An archived calendar keeps its
  entries, takes no new ones, drops out of the feed and stays listed
  for admins. The FK is `RESTRICT`.
- **Colour is validated server-side** (`#rrggbb`, else the default),
  because it goes into a `style` attribute.
- **Resources: a read-only list, not a calendar.** It shows club-owned,
  borrowable, non-retired inventory items and their open loans (member,
  since when, how many). Loans only have a lending date and an eventual
  return date, with no planned period, so there's no time grid and no
  conflict check. Who borrowed what is inventory data, so the page also
  needs the inventory module enabled and inventory read permission.

## Rejected

- **Personal per-user calendars.** kermie chose admin-defined ones.
- **Reservations with from/to and conflict checks.** kermie chose to
  show current loans only for now; that would need a new booking model
  and is a follow-up if wanted.
- **A separate `custom_calendar_events` table.** It would duplicate
  `CalendarEvent` and its ICS code for no gain.
