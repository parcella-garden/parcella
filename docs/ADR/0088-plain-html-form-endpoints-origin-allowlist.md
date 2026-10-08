# Plain-HTML-form endpoints for static websites, gated by an origin allowlist

**Context:** The public signup and contact endpoints (ADR 0024, ADR 0074)
were designed for a server-side connector -- the WordPress plugin under
`integrations/wordpress/` -- that keeps the shared `X-Parcella-API-Token`
secret, sends JSON and turns the JSON answer into a page. kermie's club is
replacing its WordPress site with plain static HTML built from Markdown,
served from FTP-only hosting. Such a site has no server-side code at all:
its forms are submitted by the visitor's browser directly to Parcella.
That rules out all three assumptions at once -- the token would have to
be written into public HTML (and so stop being a secret), a browser form
sends `application/x-www-form-urlencoded`, not JSON, and a JSON response
is a dead end for a visitor who needs to land back on the club's site.

**Decision:** Two additional endpoints next to the existing ones, same
router (`app/routers/api_public.py`):

- `POST /api/v1/public/forms/work-session-signup`
- `POST /api/v1/public/forms/contact`

1. **Same logic, not a copy.** The bodies of `submit_signup` and
   `submit_contact` moved into `_process_signup`/`_process_contact`,
   which both the JSON and the form endpoints call. Honeypot, rate limit
   (same buckets), registration deadline, capacity, the SPECIAL-session
   rule and the consent gate therefore behave identically on both paths.
   The helpers additionally return reason codes (the existing
   `public_api.signup.*` key suffixes, plus `consent_missing`/
   `unavailable` for contact) for the form endpoints to use.

2. **An origin allowlist replaces the token.** A new `ClubSetting`,
   `public_form_allowed_origins` (one `scheme://host[:port]` per line,
   edited on Administration -> Integrations), lists the websites allowed
   to submit. The request's `Origin` header -- which every current
   browser sends on a cross-origin POST -- must match exactly; `Referer`
   is the fallback when `Origin` is missing or `null`. While the list is
   empty, both endpoints answer 403, so this is off by default on top of
   the existing module flags (`public_signup_api`, `public_contact_api`),
   which still apply.

   This is not weaker than the token in practice: the token never kept
   the *public* out (anyone can submit the WordPress form, which then
   forwards with the token) -- it only kept out callers other than the
   plugin. A non-browser client can forge `Origin`, just as it could
   submit the WordPress form in a loop; the honeypot and per-IP rate
   limit are what stand against that on both paths. What the allowlist
   does stop is another website embedding a form that posts into this
   club's Parcella.

3. **Answer with a 303 redirect, outcome in the fragment.** Post/
   Redirect/Get: the visitor lands on `success_url#ok` / `#partial`, or
   `error_url#<code>` (e.g. `#session_full`, `#unknown_parcel`,
   `#no_session_selected`, `#consent_missing`, `#rate_limited`,
   `#invalid`, `#unavailable`). A fragment, not a query parameter, so a
   static thank-you/error page can show the matching message with CSS
   `:target` alone -- no JavaScript, no server code on the website. The
   rate limit and validation failures redirect too, rather than leaving
   the visitor on a raw JSON 429/422.

4. **Redirect targets are restricted to allowed origins.** `success_url`/
   `error_url` come from the form and are therefore attacker-controlled;
   honoring them unchecked would make these endpoints an open redirect.
   A target on a non-allowed origin is ignored in favour of the
   submitting page (`Referer`), then the allowed origin's root.

**Not done:** no CORS headers. A plain form submission is a "simple"
cross-origin request that browsers send without a preflight, and the
redirect is a top-level navigation, so CORS doesn't apply. A site that
wants to submit via `fetch()` instead would need it, and can keep using
the read endpoints and the JSON contract through a connector meanwhile.

**Consequences:** A static site needs only HTML: the form's `action`
points at Parcella, the session/parcel choices are rendered at build time
from the two unauthenticated GET endpoints, and two static pages carry
the success and error messages. The admin "Integrations" card lists the
new endpoints and the allowlist field.
