# ALTCHA proof of work for the plain-HTML-form endpoints

**Context:** The plain-HTML-form endpoints (ADR 0088) are posted to
straight from a public website, with no token. A honeypot field and a
per-IP rate limit stand against bulk submissions -- but a bot that
leaves the honeypot empty and spreads its posts over a few addresses
gets through both. kermie's club wanted a captcha on its contact and
work-session forms, under two constraints: no cookies and no third-party
service (anything else needs consent and a longer privacy policy), and
nothing for visitors to click or decipher.

**Decision:** An optional ALTCHA proof of work, switched on per
installation.

1. **Proof of work, not a puzzle for humans.** Before the form is sent,
   the ALTCHA widget on the website fetches a challenge from
   `GET /api/v1/public/forms/challenge` and solves it in the browser
   (PBKDF2/SHA-256, a second or so). The base64 solution is submitted as
   the form field `altcha`. A human doesn't notice; a bot has to spend
   that work on every single submission.

2. **The official library, not our own crypto.** `altcha` (MIT, no
   dependencies) creates and verifies the challenges -- its PoW v2 format
   is what the 3.x widget speaks, and getting KDF parameters, canonical
   JSON and HMAC encoding byte-for-byte right is exactly what shouldn't
   be re-implemented. `app/form_altcha.py` adds only the server's part:
   the HMAC key (derived from `SECRET_KEY`, nothing new to configure), a
   10-minute expiry, the switch, and replay protection.

3. **One use per challenge.** The library checks signature, expiry and
   solution but keeps no state, so the same solution would be valid
   until it expires. Accepted challenge signatures are remembered in
   memory until their expiry -- the same posture as `app/rate_limit.py`
   (per process, empty after a restart), which suffices for the single
   uvicorn worker Parcella runs.

4. **Off by default, a switch per installation.** `ClubSetting`
   `public_form_require_altcha` ("Require ALTCHA" on Administration ->
   Integrations, next to the allowed origins). A website must embed the
   widget *before* the switch goes on, otherwise every submission fails;
   other installations' static sites keep working unchanged. A failed
   check redirects to `error_url#captcha`.

5. **CORS, for this one endpoint only.** ADR 0088 needed no CORS because
   a form post is a top-level navigation. The challenge, though, is
   fetched with `fetch()` and its JSON must be readable by the website's
   script, so `/forms/challenge` answers with
   `Access-Control-Allow-Origin` for origins on the allowlist (and
   403 for anything else), plus `Cache-Control: no-store`. It is
   unauthenticated like the other read endpoints; issuing a challenge
   costs the server one HMAC.

**Not done** (superseded by ADR 0090, which extends the check to every
path): the JSON endpoints used by server-side connectors (the
WordPress plugin) don't check ALTCHA -- they are behind the API token,
and a connector would have to forward the widget's payload. The widget's
optional "human interaction signature" and the code (image/audio)
challenges need ALTCHA Sentinel or more server code and aren't used.

**Consequences:** New dependency `altcha` in `requirements.txt`. The
website loads the widget script (MIT) from its own webspace, so no
third party is involved; its privacy policy should mention that the
challenge is fetched from Parcella's server. Visitors need JavaScript
to submit the forms while the switch is on.
