# Community calendar: JSON endpoint for widget rendering, not just ICS

**Context:** [ADR 0030](./0030-wordpress-connector-plugin-consolidated-into-one-plugin.md)
already flagged "calendar display via shortcode instead of passive ICS"
as planned work for the `parcella-connector` WordPress plugin. The
association's public site (`kgv-goldene-hoehe.de`) has a sidebar widget
("WICHTIGE TERMINE FÜR UNSERE GARTENFREUNDE") that needed to show
Parcella's upcoming community-calendar items, and explicitly not via an
ICS-subscription widget -- a generic ICS-consuming widget can't be
styled to match the surrounding sidebar the way a shortcode rendering
real HTML can.

**Decision: a read-only JSON twin of the existing ICS feed, not a
general calendar API.** `GET /calendar/community.json`
(`app/routers/calendar.py`) sits right next to `/calendar/community.ics`,
same router, same `require_module("calendar")` gate, same
public/unauthenticated posture ("contains only already-public
information"), and reuses the identical merge logic (`CalendarEvent`
rows plus `SessionType.STANDARD` work sessions, SPECIAL sessions
excluded) already shared by `community_overview()` and
`build_community_calendar()`. It deliberately does **not** live under
`/api/v1/public/...`: that router is gated by the unrelated
`public_signup_api` module flag, and a club should be able to expose
the calendar without opting into the signup API too.

This is a narrow, additive exception to `docs/module-calendar.md`'s
"no REST API for this module" stance, not a reversal of it -- that
stance was specifically about a conventional CRUD API for
creating/editing meetings and presence slots, which still doesn't
exist and still isn't planned speculatively. The ICS feed was always
this module's public integration surface; this just adds a JSON
transport for the exact same read-only data, for the one rendering need
(a styled widget) that iCalendar's grid-app-oriented format can't
serve.

**WordPress side:** a new `calendar.php` module in `parcella-connector`
(alongside `signup.php`), registering `[parcella_calendar limit="5"]`.
Unlike the signup module, this one never needs the shared API token --
only the base URL -- since it's read-only. Reuses
`parcella_connector_signup_fetch_json()`'s transient-caching GET helper
from `signup.php` rather than duplicating it; that helper was already
generic (path/cache-key/duration), not actually signup-specific despite
its name.
