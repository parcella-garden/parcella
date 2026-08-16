# Parcella Connector (WordPress plugin)

A consolidated WordPress plugin for every integration between this site and a Parcella installation. Each capability lives in its own module under `includes/modules/`, sharing one Parcella base URL and API token configured in a single settings screen -- rather than each integration shipping as its own separate plugin with its own separate credentials.

**Currently included:**

- **Work session signup** (`includes/modules/signup.php`) -- a public work-session signup form via the `[parcella_work_signup]` shortcode,   backed by Parcella's public signup API.
- **Community calendar** (`includes/modules/calendar.php`) -- upcoming meetings, parcel inspections, and work sessions via the `[parcella_calendar limit="5"]` shortcode, backed by Parcella's public `/calendar/community.json` feed. Read-only, no API token needed -- just the base URL.
- **Contact form** (`includes/modules/contact.php`) -- a public contact form via the `[parcella_contact_form]` shortcode that creates a Parcella ticket directly, instead of sending a plain email.

More modules (applicant management) are planned and will be added the same way: a new file under `includes/modules/`, required from the main plugin file, using the same shared base URL/token rather than asking for its own credentials.

This plugin is intentionally a thin client for every module it
contains: no business logic (capacity checks, matching, validation, ticket routing, etc.) lives here -- all of that lives in Parcella itself, behind the same kind of API contract any other CMS connector would use. See the relevant `docs/module-*.md` file in the Parcella repository for each module's contract.

## Installation

1. Copy the `parcella-connector` folder into your WordPress
   installation's `wp-content/plugins/` directory.
2. Activate "Parcella Connector" under Plugins.
3. Go to Settings -> Parcella Connector and fill in:
   - **Parcella base URL** -- e.g. `https://parcella.your-club.org`
   - **API token** -- from Parcella's admin area under
     Administration -> Integrations
4. In Parcella, make sure the modules you want to use are enabled (Administration -> Settings -> optional modules) - e.g. "Public signup API" and "Public contact-form API" are both off by default and enabled independently.
5. Use whichever module-specific shortcodes/features you need (see below).

## Upgrading from "Parcella Work Session Signup" (the old plugin name)

If you already have the old single-purpose plugin
(`parcella-work-signup`) installed and configured:

1. Deactivate and delete the old "Parcella Work Session Signup" plugin.
2. Install and activate this plugin as above.
3. **Your base URL and API token carry over automatically** -- the
   underlying WordPress option names were kept identical on purpose, so
   there's nothing to re-enter.
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
- Submits signups back to Parcella's public API, server-side, using the
  shared API token -- never exposed to visitors.
- A hidden honeypot field is included and forwarded to Parcella as-is;
  Parcella decides what to do with it.
- Styling is deliberately minimal (a few inline rules for the honeypot,
  feedback messages, and the submit button) so it inherits your theme's
  form styling. Override `.parcella-work-signup` (or
  `.parcella-signup-submit` for just the button) in your theme's CSS as
  needed.
- The form only collects a parcel number, an optional name, and
  optional remarks -- no phone or email field, since a matched
  member's contact details already live on their Parcella Member
  record. If you need them for some other reason, Parcella's API still
  accepts optional `phone`/`email` fields in the signup payload -- add
  the inputs back in `parcella_connector_signup_render_shortcode()` in
  `includes/modules/signup.php`.
- The name field's HTML `name` attribute is `parcella_signup_name`, not
  `name` -- WordPress reserves `name` as a core query variable (used to
  look up a page/post by slug). A form field literally called `name`
  gets picked up by `WP::parse_request()` and causes a 404 the moment
  it's non-empty. Worth remembering if you add a new module with its
  own form: WordPress also reserves `page`, `paged`, `author`, `cat`,
  `tag`, `feed`, `search`, `attachment`, and several others.

## Module: Community calendar

- Fetches upcoming community-calendar items (meetings, parcel
  inspections, and standard work sessions -- same set as Parcella's
  `/calendar/community.ics` feed, just as JSON) server-side,
  unauthenticated, cached for 5 minutes via a WordPress transient.
- Renders a simple list via the `[parcella_calendar]` shortcode.
  Accepts a `limit` attribute (default `5`) controlling how many
  upcoming items to show, e.g. `[parcella_calendar limit="10"]` for a
  longer list.
- Read-only -- no API token needed for this module, just the base URL.
- Styling is deliberately minimal (`.parcella-calendar-list` /
  `.parcella-calendar-item` and a few child classes). Override in your
  theme's CSS as needed, e.g. to match an existing sidebar widget's
  look.
- Meant to replace an ICS-subscription-based sidebar widget with one
  that actually inherits the site's own styling -- drop the shortcode
  into a Text/HTML/Shortcode widget wherever the calendar should
  appear.

## Module: Contact form

- Renders a form (name, email, message, and a required data-protection
  consent checkbox) via the `[parcella_contact_form]` shortcode.
- Submits directly to Parcella's public contact API, server-side, using
  the shared API token -- creates a real Parcella ticket, not an email.
  Needs its own module enabled in Parcella (**Public contact-form API**,
  separate from the signup module's flag) in addition to the base
  URL/token.
- Consent is required both client-side (`required` on the checkbox) and
  server-side (Parcella rejects a submission with `consent: false`) --
  the wording is hard-coded in `contact.php`'s
  `parcella_connector_contact_render_shortcode()`; edit it there
  directly if your privacy policy text or link needs to change.
- A hidden honeypot field is included and forwarded to Parcella as-is,
  same as the signup module.
- Styling is deliberately minimal and self-contained (its own
  `.parcella-contact-*` classes, not shared with the signup module's
  `.parcella-signup-*` ones, since a page may only include one of the
  two shortcodes). Override in your theme's CSS as needed.

## Adding a new module

1. Create `includes/modules/your-module.php`, guarded with the usual
   `if (!defined('ABSPATH')) { exit; }` at the top.
2. Use `parcella_connector_base_url()` and `parcella_connector_api_token()`
   (defined in the main plugin file) rather than reading your own
   options -- every module shares the one settings screen.
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
