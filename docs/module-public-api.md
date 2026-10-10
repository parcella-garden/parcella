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

**Registration deadline: public signup only, checked twice.** A
session that had already happened that same morning still accepted
public signups that afternoon -- nothing checked whether a session's
date had passed at all. Fixed with `WorkSession.public_signup_open`
(`app/models.py`): a baseline "date hasn't passed" rule that always
applies, plus an optional per-session `signup_deadline_days` (set on
the session itself, `app/templates/work_hours/session_form.html`) that
closes registration earlier, e.g. `1` closes the day before the event.
Deliberately **public-signup-only** -- a board member adding a
participant in Parcella itself (`app/routers/work_hours.py::participant_add`,
normally used to record attendance *after* a session) is unaffected;
blocking that would break the normal "record who showed up" workflow
for anything in the past. Checked in two places, not redundantly: once
in `list_upcoming_sessions` (hides a closed session from the WordPress
dropdown, same precedent as hiding a full one) and again in
`submit_signup` (rejects it anyway if a stale page -- slow visitor,
bookmark, back-button, or a caching bug like the one fixed just before
this -- submits a closed session's ID regardless).

**`submit_signup`'s rejection reasons are now properly localized.**
They weren't, originally ("Session is full" etc. were hardcoded
English) -- inconsistent with this project's actual i18n convention
(ADR 0020, every user-facing string in all 7 `app/translations/*.json`
files). Fixed for all four reasons in this function, new
`public_api.signup.*` namespace, using `request.state.language` the
same way the notification emails in this router already do (`_lang()`,
defined here). The sibling `submit_contact` endpoint's own hardcoded
reason ("Data-protection consent is required...") has the same gap --
not fixed here, since it's a different endpoint/module; worth doing
the same pass there if it's ever touched again.

**SPECIAL sessions never appear on the public website -- a rule that
existed but wasn't actually enforced here.** The community calendar
(`docs/module-calendar.md`) has always filtered to
`type == SessionType.STANDARD` in both its list view and its ICS feed,
specifically because a SPECIAL session is spontaneous/unplanned and
the community calendar's whole point is helping members plan ahead.
This public signup API predates that rule being written down as
explicitly as it should have been and simply never had the filter
applied -- `list_upcoming_sessions` listed every session regardless of
type, meaning the public WordPress form let visitors sign up for
sessions that were never meant to be public-facing at all. Fixed the
same way as the registration-deadline check above: filtered out of
`list_upcoming_sessions`'s query, and rejected again in `submit_signup`
(treated identically to "session not found," since from this API's
perspective a SPECIAL session isn't a signup-eligible session at all,
not a distinct rejection reason) -- same defense-in-depth reasoning,
same "don't just fix the listing, a stale/crafted request could still
submit the ID directly" logic.

A second, independent public-write capability living in the same
router (`app/routers/api_public.py`) and reference plugin
(`integrations/wordpress/parcella-connector/includes/modules/contact.php`,
`[parcella_contact_form]`): `POST /api/v1/public/contact` lets an
external site's contact form create a **FreeScout conversation**
directly via the FreeScout API, instead of sending a plain email that
would otherwise appear to come from the club's own SMTP account rather
than the actual visitor. Originally built (see
[ADR 0074](./ADR/0074-public-contact-form-to-ticket-bridge.md)) to feed
Parcella's own built-in ticket module; rewritten when that module was
removed in favor of FreeScout (see
[ADR 0080](./ADR/0080-remove-builtin-ticket-module-freescout-conversation-bridge.md)
and `docs/module-freescout-bridge.md`) to call
`FreeScoutClient.create_conversation()` instead.

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

**No local spam check anymore.** The removed ticket module ran incoming
messages through a heuristics-plus-optional-external-API spam filter;
now that this endpoint creates a FreeScout conversation instead of a
local record, spam triage is FreeScout's own responsibility, same as
anything else landing in its inbox.

**No dedicated consent-tracking column.** Whether consent was given is
a submission-time gate (rejected outright if false), not something the
board needs to query later -- the created FreeScout conversation's
message body records that consent was given, for anyone reviewing it
by hand.

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

## Static websites: plain HTML forms

A site with no server-side code (static HTML on FTP-only hosting, for
instance) can't keep the API token secret, so it uses two form endpoints
instead -- see [ADR 0088](./ADR/0088-plain-html-form-endpoints-origin-allowlist.md)
for the reasoning.

| Method | Path | Auth |
|---|---|---|
| POST | `/api/v1/public/forms/work-session-signup` | origin allowlist |
| POST | `/api/v1/public/forms/contact` | origin allowlist |
| GET | `/api/v1/public/forms/challenge` | origin allowlist (CORS) |

They run the exact same logic as the JSON endpoints, take ordinary
`application/x-www-form-urlencoded` form posts, and answer with a 303
redirect back to the website. Requirements:

- the module flag (`public_signup_api` / `public_contact_api`) is on, and
- the website's origin (e.g. `https://example.org`) is listed under
  Administration -> Integrations -> "Allowed website origins". While that
  list is empty both endpoints answer 403.

Form fields: the same names as in the JSON payloads (`session_ids`
repeated once per ticked checkbox; `consent` as a checkbox), the hidden
honeypot `website`, and optional `success_url`/`error_url`. Both URLs
must be on an allowed origin -- anything else is ignored in favour of the
submitting page, so the endpoint can't be used as an open redirect.

Outcome, as the URL fragment: `success_url#ok`, `success_url#partial`
(signup: some ticked sessions were rejected), or `error_url#<code>` with
`code` one of `session_full`, `registration_closed`, `session_not_found`,
`no_members_for_parcel`, `unknown_parcel`, `no_session_selected`,
`consent_missing`, `invalid`, `rate_limited`, `unavailable`, `captcha`,
`error`. A
static page can show the matching message with CSS alone:

```html
<form method="post" action="https://parcella.example.org/api/v1/public/forms/contact">
  <input name="name" required> <input name="email" type="email" required>
  <textarea name="message" required></textarea>
  <label><input type="checkbox" name="consent" required> I agree to the privacy policy</label>
  <input name="website" tabindex="-1" autocomplete="off" hidden>
  <input type="hidden" name="success_url" value="https://example.org/danke/">
  <input type="hidden" name="error_url" value="https://example.org/fehler/">
  <button>Send</button>
</form>

<!-- on /fehler/ -->
<style>.reason { display: none } .reason:target { display: block }</style>
<p id="consent_missing" class="reason">Please tick the privacy checkbox.</p>
<p id="rate_limited" class="reason">Too many messages -- please try again later.</p>
```

The session and parcel choices for the signup form come from the two
unauthenticated GET endpoints above -- fetched when the static site is
built, so the page itself stays plain HTML.

### Optional: ALTCHA against spam bots

With "Require ALTCHA" ticked (Administration -> Integrations, next to the
allowed origins), both form endpoints only accept submissions carrying a
solved ALTCHA proof of work in the field `altcha`; anything else
redirects to `error_url#captcha`. See
[ADR 0089](./ADR/0089-altcha-proof-of-work-for-plain-html-forms.md).
Embed the [ALTCHA widget](https://altcha.org) (3.x) in each form first,
then tick the box:

```html
<form method="post" action="https://parcella.example.org/api/v1/public/forms/contact">
  ...
  <altcha-widget challenge="https://parcella.example.org/api/v1/public/forms/challenge"
                 auto="onfocus" configuration='{"humanInteractionSignature": false}'></altcha-widget>
  <button>Send</button>
</form>
<script src="/altcha.min.js" defer></script>
```

The widget fetches a challenge (answered with CORS headers for the
allowed origins only), solves it in a second or so, and puts the
solution into a hidden `altcha` field. Each solution is accepted once
and expires after 10 minutes. No cookies, no third party.
