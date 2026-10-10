# One form contract for every website; the WordPress plugin posts plain forms

**Context:** After ADR 0088/0089 there were three ways for a website to
submit the public signup and contact forms, and they had drifted apart:

- the token-authenticated JSON endpoints (ADR 0024, ADR 0074), used by
  server-side connectors;
- the plain-HTML-form endpoints `/forms/*` (origin allowlist, optional
  ALTCHA), used by static sites;
- the WordPress plugin, a server-side connector on the JSON path.

The differences mattered in practice. The rate limit keyed on the
connection's IP, which for a server-side connector is the CMS server:
**every visitor of a WordPress site shared one bucket**, 10 contact
messages and 20 signups per hour for the whole site. "Require ALTCHA"
only covered `/forms/*` (ADR 0089, "Not done"), so ticking it left the
WordPress forms unprotected without saying so. Only `/forms/*` returned
machine-readable reason codes, and the contact rejections were
hardcoded English. kermie asked for forms to behave the same in
WordPress, any other CMS, and the API -- and explicitly not to support
third-party WordPress form-builder plugins.

**Decision:**

1. **The WordPress plugin (3.0.0) posts plain HTML forms to `/forms/*`.**
   Its shortcodes render a form whose `action` is Parcella; the visitor's
   browser submits it directly, and Parcella redirects back with the
   outcome in the fragment. The plugin tags the return URL with
   `?parcella_form=signup|contact` and renders only that form's messages,
   so two shortcodes on one page don't both carry `id="ok"`. The ALTCHA
   widget is bundled with the plugin and always embedded. The plugin no
   longer needs, stores or sends the API token. The WordPress site's
   origin goes on the allowlist like any other website's.

   This makes `/forms/*` *the* integration for websites, whatever renders
   them: per-visitor rate limiting and ALTCHA come for free, because the
   visitor's browser is the client.

2. **The JSON endpoints stay, aligned to the same contract** for
   server-side connectors:
   - **ALTCHA moves into the shared helpers** (`_process_signup`/
     `_process_contact`). One switch now covers every path; a missing or
     bad solution is rejected with code `captcha` -- after the honeypot,
     before the rate limit and before any lookup, so a bot without the
     proof of work costs nothing and learns nothing (e.g. which parcel
     numbers exist). The JSON schemas gain an optional `altcha` field.
   - **`code` next to `reason`** in `PublicSignupSessionResult` and
     `PublicContactResult`: the same codes the form fragment uses, so a
     connector can word its own messages. Additive, backward compatible.
   - **Contact reasons are translated** (`public_api.contact.*`), like
     the signup ones already were.
   - **`X-Parcella-Client-IP`**: a connector forwards its visitor's IP,
     and the rate limit uses it. Only honoured on the token endpoints,
     after the token checked out -- an anonymous caller must not be able
     to pick its own bucket -- and only if it parses as an IP address.

3. **No form-builder bridges.** Contact Form 7, WPForms, Gravity Forms
   and the like are not supported, neither as plugin add-ons nor as
   dedicated Parcella endpoints. A site uses the contract directly: a
   plain HTML form, the shortcodes, or its own small connector.

**Consequences:**

- Existing WordPress sites must add their origin to "Allowed website
  origins" when updating the plugin to 3.0.0, or every submission is
  refused (403). The plugin's settings page shows the origin to add.
- An installation that already switched on "Require ALTCHA" (3.12.0)
  and still runs plugin 2.x or another token connector that doesn't
  forward `altcha` now gets its submissions rejected with `captcha`.
  The switch was opt-in and only just released; the admin hint says so.
- A server-side connector whose site wants ALTCHA must list the site's
  origin too, because the widget fetches its challenge from the
  visitor's browser.
- Visitors need JavaScript only while "Require ALTCHA" is on.
- Supersedes the "Not done" note in ADR 0089 about the JSON endpoints.
