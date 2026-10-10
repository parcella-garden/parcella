# Parcella Connector (WordPress plugin)

A consolidated WordPress plugin for every integration between this site and a Parcella installation. Each capability lives in its own module under `includes/modules/`, sharing one Parcella base URL configured in a single settings screen -- rather than each integration shipping as its own separate plugin with its own separate settings.

**Currently included:**

- **Work session signup** (`includes/modules/signup.php`) -- a public work-session signup form via the `[parcella_work_signup]` shortcode,   backed by Parcella's public signup API.
- **Community calendar** (`includes/modules/calendar.php`) -- upcoming meetings, parcel inspections, and work sessions via the `[parcella_calendar limit="5"]` shortcode, backed by Parcella's public `/calendar/community.json` feed. Read-only, needs just the base URL.
- **Contact form** (`includes/modules/contact.php`) -- a public contact form via the `[parcella_contact_form]` shortcode whose messages land as conversations in the club's FreeScout inbox (through Parcella), instead of being sent as a plain email.

- **Garden plot applications** (`includes/modules/applicants.php`) -- an application form for free garden plots via the `[parcella_applicant_form]` shortcode; applications land in Parcella's applicants list.

Further modules are added the same way: a new file under `includes/modules/`, required from the main plugin file, using the same shared base URL rather than asking for its own settings.

## How the forms work (since 3.0.0)

The signup and contact forms are plain HTML forms that the visitor's
browser posts **straight to Parcella** (`/api/v1/public/forms/...`) --
exactly like a form on any other website, static or CMS. Parcella
answers with a redirect back to the page the form is on, carrying the
outcome in the URL fragment (`#ok`, `#session_full`, `#captcha`, ...),
and the page shows the matching message with CSS alone. WordPress
never sees the submission, and the plugin holds no secret.

That means every website talks to Parcella through the same form
contract (see `docs/module-public-api.md` in the Parcella repository):
the same fields, the same ALTCHA spam protection, and a rate limit per
visitor rather than one shared by the whole website.

Deliberately **not** supported: bridges to form-builder plugins
(Contact Form 7, WPForms, Gravity Forms, ...). Use the shortcodes, or
put a plain HTML form into a "Custom HTML" block following the contract.

This plugin is intentionally a thin client for every module it
contains: no business logic (capacity checks, matching, validation, ticket routing, etc.) lives here -- all of that lives in Parcella itself, behind the same kind of API contract any other CMS connector would use. See the relevant `docs/module-*.md` file in the Parcella repository for each module's contract.

## Installation

1. Copy the `parcella-connector` folder into your WordPress
   installation's `wp-content/plugins/` directory.
2. Activate "Parcella Connector" under Plugins.
3. Go to Settings -> Parcella Connector and fill in the **Parcella base
   URL**, e.g. `https://parcella.your-club.org`. The same page shows this
   site's own origin (e.g. `https://www.your-club.org`).
4. In Parcella, add that origin under Administration -> Integrations ->
   **Allowed website origins**. Until it's listed, Parcella refuses the
   forms (403).
5. In Parcella, make sure the modules you want to use are enabled (Administration -> Settings -> optional modules) - e.g. "Public signup API" and "Public contact-form API" are both off by default and enabled independently.
6. Optional: tick **Require ALTCHA** on the same Integrations page. The
   forms already carry the ALTCHA widget, so this can be switched on at
   any time.
7. Use whichever module-specific shortcodes/features you need (see below).

## Upgrading from 2.x

2.x sent the forms from WordPress to Parcella with the shared API token.
3.0.0 drops that path, so after updating the plugin:

1. Add this site's origin (shown on Settings -> Parcella Connector) to
   Parcella's **Allowed website origins** -- otherwise every submission
   is refused. Parcella 3.13.0 or later is needed.
2. Nothing else: the base URL carries over, and the shortcodes are
   unchanged. The stored API token is no longer used and is deleted from
   the WordPress database automatically. If no other connector uses it,
   regenerate it in Parcella to retire the old value.

Visitors need JavaScript only while "Require ALTCHA" is switched on in
Parcella (the widget solves its puzzle in the browser).

## Upgrading from "Parcella Work Session Signup" (the old plugin name)

If you already have the old single-purpose plugin
(`parcella-work-signup`) installed and configured:

1. Deactivate and delete the old "Parcella Work Session Signup" plugin.
2. Install and activate this plugin as above.
3. **Your base URL carries over automatically** -- the underlying
   WordPress option name was kept identical on purpose, so there's
   nothing to re-enter. Then follow "Upgrading from 2.x" above.
4. Any page/post already using `[parcella_work_signup]` keeps working
   unchanged -- the shortcode tag itself didn't change either.

The only visible difference after upgrading is the settings page now
lives at Settings -> Parcella Connector (same menu position, new name)
and shows a "Modules" table for whatever's active.

## Module: Work session signup

- Fetches the current upcoming sessions and parcel list from Parcella
  (server-side, unauthenticated -- these are public read endpoints),
  cached for 60 seconds (sessions) and an hour (parcels) via WordPress
  transients so a busy page doesn't hit Parcella on every view.
- Renders a form via the `[parcella_work_signup]` shortcode.
- The form posts straight to Parcella (see "How the forms work"
  above); coming back from a signup refreshes the cached session list.
- A hidden honeypot field and the ALTCHA widget are included; Parcella
  decides what to do with both.
- Styling is deliberately minimal (a few inline rules for the honeypot,
  outcome messages, and the submit button) so it inherits your theme's
  form styling. Override `.parcella-work-signup` (or
  `.parcella-signup-submit` for just the button, `.parcella-outcome-*`
  for the messages) in your theme's CSS as needed.
- The form only collects a parcel number, an optional name, and
  optional remarks -- no phone or email field, since a matched
  member's contact details already live on their Parcella Member
  record. If you need them for some other reason, Parcella still
  accepts optional `phone`/`email` fields -- add the inputs back in
  `parcella_connector_signup_render_shortcode()` in
  `includes/modules/signup.php`.
- Fields use the contract's plain names (`name`, `parcel_number`,
  `session_ids`, ...). 2.x had to rename `name`, since WordPress
  reserves it as a query variable; the form no longer posts to
  WordPress, so that no longer applies -- but keep it in mind for any
  form that does post to WordPress (`page`, `paged`, `author`, `cat`,
  `tag`, `feed`, `search`, `attachment` and others are reserved too).
- If you run a full-page caching plugin (WP Super Cache, WP Rocket, W3
  Total Cache, WP Fastest Cache, etc.), any page containing this
  shortcode is automatically excluded from that cache (via the
  `DONOTCACHEPAGE` constant most such plugins respect -- see
  `parcella_connector_disable_page_cache()` in the main plugin file) --
  otherwise a cached page keeps showing whatever sessions were upcoming
  at cache time, including ones that have since passed, until the cache
  happens to expire or be purged.

## Module: Community calendar

- Fetches upcoming community-calendar items (meetings, parcel
  inspections, and standard work sessions -- same set as Parcella's
  `/calendar/community.ics` feed, just as JSON) server-side,
  unauthenticated, cached for 5 minutes via a WordPress transient.
- Renders a simple list via the `[parcella_calendar]` shortcode.
  Accepts a `limit` attribute (default `5`) controlling how many
  upcoming items to show, e.g. `[parcella_calendar limit="10"]` for a
  longer list.
- Read-only -- needs just the base URL.
- Styling is deliberately minimal (`.parcella-calendar-list` /
  `.parcella-calendar-item` and a few child classes). Override in your
  theme's CSS as needed, e.g. to match an existing sidebar widget's
  look.
- Meant to replace an ICS-subscription-based sidebar widget with one
  that actually inherits the site's own styling -- drop the shortcode
  into a Text/HTML/Shortcode widget wherever the calendar should
  appear.
- Same full-page-cache exclusion as the signup module above, for the
  same reason (a cached page would otherwise keep showing already-past
  calendar entries).

## Module: Contact form

- Renders a form (name, email, message, and a required data-protection
  consent checkbox) via the `[parcella_contact_form]` shortcode.
- Posts straight to Parcella (see "How the forms work" above), which
  creates a conversation in the club's FreeScout inbox -- not an email.
  Needs its own module enabled in Parcella (**Public contact-form API**,
  separate from the signup module's flag) and FreeScout configured
  there.
- Consent is required both client-side (`required` on the checkbox) and
  server-side (Parcella rejects a submission with `consent: false`) --
  the wording is hard-coded in `contact.php`'s
  `parcella_connector_contact_render_shortcode()`; edit it there
  directly if your privacy policy text or link needs to change.
- A hidden honeypot field and the ALTCHA widget are included, same as
  the signup module.
- Both shortcodes can sit on the same page: each one only renders the
  outcome messages for its own submission.
- Styling is deliberately minimal (`.parcella-contact-form`,
  `.parcella-contact-submit`, plus the shared `.parcella-outcome-*`
  messages). Override in your theme's CSS as needed.

## Module: Garden plot applications

- Renders an application form for a free garden plot via the
  `[parcella_applicant_form]` shortcode: email address (required), first
  and last name, phone and a free-text message (all optional), and a
  required data-protection consent checkbox.
- Posts straight to Parcella (see "How the forms work" above), which adds
  the applicant to its applicants list for the board. Needs **Applicants**
  and **Public applicant-form API** enabled in Parcella (Administration ->
  Settings -> optional modules); the latter is off by default.
- The consent wording is hard-coded in `applicants.php`; edit it there if
  your privacy policy text or link needs to change.
- Honeypot and ALTCHA widget included, same as the other forms. Styling:
  `.parcella-applicant-form`, `.parcella-applicant-submit`, plus the shared
  `.parcella-outcome-*` messages.

## Spam protection: ALTCHA

Both forms embed the [ALTCHA](https://altcha.org) widget, bundled with
the plugin under `assets/altcha/` (version 3.2.3, MIT, see its
`LICENSE.txt`) -- served from this site, no third party, no cookies. It
fetches a small proof-of-work puzzle from Parcella
(`/api/v1/public/forms/challenge`) and solves it in the browser. Whether
the solution is required is decided in Parcella ("Require ALTCHA" on
Administration -> Integrations); while that's off, it's ignored. Your
privacy policy should mention that the visitor's browser contacts the
Parcella server when the form is used.

## Adding a new module

1. Create `includes/modules/your-module.php`, guarded with the usual
   `if (!defined('ABSPATH')) { exit; }` at the top.
2. Use `parcella_connector_base_url()` and the shared form helpers
   (`parcella_connector_form_action()`, `parcella_connector_render_outcome()`,
   `parcella_connector_render_common_fields()`,
   `parcella_connector_render_altcha()`, all in the main plugin file)
   rather than reading your own options -- every module shares the one
   settings screen.
3. `require_once PARCELLA_CONNECTOR_PATH . 'includes/modules/your-module.php';`
   at the bottom of `parcella-connector.php`, next to the existing
   `signup.php` require.
4. Add a row for it to the Modules table in
   `parcella_connector_render_settings_page()`.
5. Prefix every function you add with `parcella_connector_your_module_`
   to avoid collisions with other modules.

## Translations

The plugin text is translated out of the box into every language the
main Parcella application supports -- German, Polish, Czech, Slovak,
French, and Dutch (`languages/parcella-connector-{de_DE,pl_PL,cs_CZ,
sk_SK,fr_FR,nl_NL}.mo`), alongside the English source strings. It
follows the WordPress site's configured language automatically -- no
settings needed. For any other language, copy
`languages/parcella-connector.pot` to `parcella-connector-{locale}.po`
(e.g. `parcella-connector-it_IT.po` for Italian), translate the
strings, and compile it:

    msgfmt -o parcella-connector-{locale}.mo parcella-connector-{locale}.po

Drop both files into the `languages/` folder and WordPress picks them
up automatically based on the site's language setting. Keep this file
set in sync with `app/translations/*.json` on the Parcella side when
adding a new shortcode module or changing user-facing text -- the
`.pot` lists every current source string as a starting point.
