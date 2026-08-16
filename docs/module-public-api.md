# Public signup API module

Lets an external CMS (WordPress, TYPO3, Contao, or a hand-rolled site --
anything that can make an HTTP request) submit work-session signups to
Parcella without a Parcella login. Built to solve a concrete problem:
clubs already have a public website (usually WordPress) with its own
"sign up for a work session" form, and that form's list of dates
inevitably drifts out of sync with what's actually scheduled in
Parcella, because someone has to update it by hand in two places.

A reference WordPress connector lives in the "signup" module of the
consolidated `integrations/wordpress/parcella-connector/` plugin (see
its own README for installation) -- this plugin also hosts other
WordPress <-> Parcella integrations (see
docs/ADR/0030-wordpress-connector-plugin-consolidated-into-one-plugin.md for why it was consolidated rather than
shipping a separate plugin per integration). Writing an equivalent
connector for another CMS means implementing the same three-endpoint
contract below; none of the logic needs to be reimplemented per CMS.

## The core constraint: no member names on the public site

The public form only ever collects a **parcel number**, never a member
name picked from a list -- the club's public website must not expose
which members live on which parcel. That one requirement shapes
everything else in this module: Parcella, not the form, has to work out
who is actually signing up.

A submitted name is still accepted as free text (useful when several
people live on one parcel), and is used to narrow down *which* current
resident to register -- but it's never presented as a choice on the
public side, and an unmatched or ambiguous name doesn't block the
signup; see "Matching logic" below.

## Off by default

Unlike every other optional module (`app/module_flags.py`), this one
defaults to **disabled**. Every other module gates functionality that's
only reachable by an already-authenticated user; this one opens a public
HTTP endpoint that accepts writes from anyone with the API token. That's
a meaningfully different risk profile, so a board/admin has to
explicitly turn it on (Administration -> Settings) rather than it
silently being available after an upgrade.

## Data model

There is no dedicated public-signup table. A signup creates real
`SessionParticipation` rows directly, with `status=REGISTERED`, exactly
as if a board member had added that member from the session detail
page. This was a deliberate change from an earlier version of this
module that stored public signups in their own
`public_session_signups`/`public_session_signup_sessions` tables,
displayed in a separate UI card -- removed in migration
`0028_drop_signup_tables` once it became clear the signups needed to
behave like real participations (visible in the normal participants
table, contributing to the normal work-hours totals), not a parallel
structure the board had to check in a second place.

The submission's phone/email/remarks/submitted-name (and, when the
fallback below kicks in, a flag explaining why) are folded into the
`note` field of each `SessionParticipation` row created -- visible right
in the existing participants table, no separate UI needed.

## Matching logic

On each submission, Parcella looks up the parcel's **current**
residents (`MemberParcel` rows with `assigned_until IS NULL`) and tries
to match the optionally-submitted name against them
(case-insensitive, whitespace-normalized, checked against both
`"First Last"` and `"Last First"`):

- **Exactly one match** -> only that member is registered.
- **No name given, no match, or more than one plausible match** ->
  *every* current resident of the parcel is registered, each with a
  note flagging that the match was ambiguous and asking the board to
  verify and remove whoever didn't actually sign up.
- **No current residents at all** -> the signup is rejected for that
  session with reason `"No members are currently assigned to this
  parcel"` (nothing to register).

Overregistering is the deliberately safer default over the alternatives
(registering nobody, or silently guessing wrong with no trace) --
removing an extra participant from the normal participants table is a
one-click action the board already knows how to do; a signup that
silently went nowhere is much harder to notice and fix.

## Endpoints

| Method | Path | Auth |
|---|---|---|
| GET | `/api/v1/public/work-sessions/upcoming` | none |
| GET | `/api/v1/public/parcels` | none |
| POST | `/api/v1/public/work-sessions/signup` | `X-Parcella-API-Token` header |

The two GET endpoints are intentionally unauthenticated -- the same
posture as the public community ICS feed (`app/ics_utils.py`): an
external site's frontend can't send this app's session cookie, and the
data exposed (session dates/times, plot numbers) isn't sensitive on its
own. `GET /parcels` deliberately omits the parcel's internal id from
`PublicParcelOut` (`app/schemas.py`) -- the reference WordPress
connector matches by `plot_number` string alone, so there's no reason
to hand every unauthenticated caller a UUID that's usable elsewhere in
the app as `parcel_id` (flagged by an external pentest as IDOR
reconnaissance value).

The POST endpoint requires the installation's shared API token (see
`app/public_api_auth.py`, same shared-secret pattern as the private ICS
feeds) plus a lightweight honeypot field and a per-IP rate limit (20
requests/hour, in-memory, see `app/routers/api_public.py`) as
defense-in-depth on top of the token.

`POST .../signup` accepts multiple `session_ids` in one submission and
evaluates each independently -- a full session is rejected with a
`reason` while other sessions in the same submission can still succeed.
Capacity (`WorkSession.max_participants`/`available_spots`) is checked
against however many members are about to be registered for that
session (one if matched, all current residents otherwise) -- a session
with room for only 1 more spot rejects a 2-resident parcel's signup for
that session entirely, rather than registering only one of them.
Submitting the same parcel/session combination twice does not create
duplicate participations. See the admin "Integrations" page
(Administration -> Integrations) for the current token, endpoint URLs,
and a regenerate button.

## Key decisions

**Signups are real `SessionParticipation` rows, not a parallel
structure.** See "Data model" above -- this replaced an earlier design
that kept public signups in their own tables specifically so a
submitter didn't have to be a `Member`. That constraint (a helping
neighbor without a Member record) turned out to be less important in
practice than the signups actually behaving like normal participants;
the parcel-based matching/fallback logic above resolves it well enough
for the common case, and there's no dedicated place left for a
non-Member submitter to go anyway.

**A dedicated token, not the member API's JWT.** The existing REST API
(`app/api_auth.py`) issues per-user JWTs from a login -- there's no
"user" for a CMS plugin to log in as. A single shared, regenerable
token per installation (mirroring `app/ics_utils.py`'s ICS feed tokens)
is simple to document in one settings screen and easy to rotate if a
site's credentials leak.

**Capacity check is not fully race-safe.** Two submissions arriving at
nearly the same moment could both read `available_spots` as sufficient
before either commits, both succeeding when only one spot existed.
Accepted as a known limitation for a small club's traffic volume rather
than adding row-level locking; worth revisiting if a club's usage
pattern makes this a real problem in practice.

**Blank optional fields must be treated as absent, not validated as-is.**
Found via the WordPress connector: an HTML form submits an untouched
`<input type="email">` as `""`, not as a missing field, and `EmailStr`
rejects `""` outright (`@-sign` missing) -- every real-world submission
with an empty email field returned a 422 that the connector's generic
error handler couldn't distinguish from an actual server error.
`PublicSignupCreate` now coerces blank strings to `None` for all
optional fields (`name`, `phone`, `email`, `remarks`, `website`) before
validation runs (`app/schemas.py`). Worth remembering for any future
public-facing form schema: assume every optional field arrives as `""`,
not absent, unless the client is JSON-native and deliberately omits it.

**In-memory rate limiting, not a new dependency.** No Redis/`slowapi` --
a per-process sliding-window counter keyed by IP is enough deterrence
layered on top of the actual access control (the token), and adding
infrastructure for this felt disproportionate. Resets on deploy and
doesn't share state across multiple workers if the app is ever run with
more than one; acceptable for now, revisit if that changes.

## Public contact-form API module

A second, independent public-write capability living in the same
router (`app/routers/api_public.py`) and reference plugin
(`integrations/wordpress/parcella-connector/includes/modules/contact.php`,
`[parcella_contact_form]`): `POST /api/v1/public/contact` lets an
external site's contact form create a Parcella **ticket** directly,
instead of sending a plain email that then has to round-trip through
the ticket mailbox's IMAP polling. Built for a concrete case: the
association's own `/kontakt` page previously emailed the ticket inbox
(confirmed live -- an existing ticket titled "Kontaktanfrage von
Website" was ingested that way, matching no Parcella translation key,
i.e. a literal string from whatever WordPress contact-form plugin sent
it). See [ADR 0074](./ADR/0074-public-contact-form-to-ticket-bridge.md).

**Its own module flag, `public_contact_api`, off by default** -- same
reasoning as `public_signup_api` above (opens a public write endpoint),
but deliberately a *separate* flag rather than reusing
`public_signup_api`: a club should be able to enable one bridge without
the other. Toggle at Administration -> Settings; the endpoint URL and
shared API token are shown on the same Administration -> Integrations
page as the signup endpoints (same token, since the plugin uses one
shared credential for every module).

**Fields: name, email, message, and a required consent flag.** No
parcel number here (unlike signup) -- a contact-form message isn't tied
to a parcel. `consent` must be `true` or the submission is rejected
(`accepted: false`, with a `reason`) -- same HTTP-200-with-a-rejection-flag
convention the signup endpoint already uses for per-session
acceptance, not an HTTP error status, since "consent missing" is a
normal, expected outcome for a real visitor who hasn't ticked the box
yet, not a server error.

**Runs through the same spam check as incoming ticket emails.**
`check_for_spam()` (`app/spam_filter.py`), the same function
`app/ticket_mailer.py` applies to every incoming email -- this endpoint
is exactly as public-facing as the ticket inbox itself, so it gets the
same heuristics-plus-optional-external-API treatment, setting
`spam_suspected`/`spam_score`/`spam_reasoning` on the created ticket.
Reuses `create_ticket()` (`app/services/tickets.py`, already shared
between the HTML and JWT-authenticated API surfaces per ADR 0070)
rather than duplicating ticket/message creation.

**No dedicated consent-tracking column.** Whether consent was given is
a submission-time gate (rejected outright if false), not something the
board needs to query later -- the created ticket's own message body
records that consent was given, for anyone reviewing it by hand.

## Extending to another CMS

Any connector needs to, in order:
1. `GET /work-sessions/upcoming` and `GET /parcels` to render a form
   (cache both briefly -- see the WordPress plugin's use of transients).
2. Collect parcel number (required), optional name/phone/email/remarks,
   and one or more chosen session IDs. The name field, if offered,
   should never be a dropdown of members -- see "The core constraint"
   above.
3. `POST /work-sessions/signup` with the API token in
   `X-Parcella-API-Token`, server-side only.
4. Handle a per-session `accepted`/`reason` in the response -- a
   submission can partially succeed.

New module checklist entries in `docs/README.md` apply here too if this
module gets extended (new translation keys go in all 7 language files).
