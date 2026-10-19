# Security audit 2026-10: fixes and the decisions behind them

**Context:** A whole-application review on 2026-10-19 (login, access
control, public endpoints, user data in HTML/CSV/headers, outside
services, configuration, dependencies) found two high, three medium and
several low issues. This records what was fixed, how, and what was
deliberately left, so a later change doesn't quietly undo one of them.
Regression tests: `tests/test_security_audit_fixes.py` and
`tests/test_api_club_settings_secrets.py`.

**Decision:**

- **Secrets never leave through the settings API.**
  `GET /api/v1/club-settings` served every `ClubSetting` row to any API
  account, including the plaintext ICS feed token and public form token.
  Keys ending in `password`, `token`, `secret` or `api_key` are now left
  out of the list, answer 404 individually, and can't be written through
  the API (403). This is a naming rule rather than a list, so a new
  credential key named the same way is covered without anyone
  remembering this file. Integrations are configured on the admin pages
  only.
- **The real client IP behind a proxy needs `--forwarded-allow-ips`.**
  With `--proxy-headers` alone, uvicorn trusts forwarded headers only
  from 127.0.0.1, but a host nginx reaches the container through the
  Docker gateway, so every visitor shared one address and the login
  throttle (`app/login_throttle.py`) became a global lockout switch.
  The fix is configuration (README override example,
  `docs/operations.md`), not code: the app can't know which proxy to
  trust. `*` is only acceptable because the documented port binding is
  `127.0.0.1`.
- **User data is never assembled into HTML strings in JavaScript.** The
  two member-search dropdowns built `innerHTML` from member names. They
  now create elements and set `textContent`. The CSP keeps
  `'unsafe-inline'` (see `app/security_headers.py`), so it can't serve
  as the safety net here.
- **The ICS feed token can be rotated** (admin → integrations), the same
  way the public form token already could. It still never expires on
  its own: rotating is the only way to cut off a leaked link or a board
  member who left.
- **A password change ends every other session.** `users.session_version`
  (migration 0101) is part of the signed session cookie and is bumped on
  a password change, and the browser that changed it gets a fresh
  cookie. Cookies from before the migration count as version 0, so the
  upgrade logs nobody out. Logout itself does *not* bump the version:
  that would end the session on every other device of the same person.
  Logout deletes the cookie, and a copied cookie stays valid until it
  expires (`session_max_age`, 8 hours). That residual risk is accepted.
- **PDF rendering loads only `data:` URIs.** WeasyPrint would otherwise
  fetch any `<img src="http…">` in an announcement from the server (blind
  SSRF, e.g. the cloud metadata address). Everything the app embeds
  itself is already a data URI (`app/pdf_utils.py`), so
  `URLFetcher(allowed_protocols=["data"])` costs nothing.
- **Filenames that hold user data go through `content_disposition()`**
  (`app/security_headers.py`). It writes an ASCII fallback plus an RFC
  6266 `filename*`. This fixes header breakage from quotes and CR/LF, and
  a 500 on invoices of members whose last name has letters outside
  latin-1 ("Ł", "ř").
- **Smaller ones:** CSV formula escaping on the remaining insurance and
  work-hours cells. Failed logins for unknown addresses run a dummy
  bcrypt check, so response timing doesn't reveal which addresses have
  accounts. pyjwt 2.15.0, aiosmtplib 5.1.2 and WeasyPrint 70.0 (whose
  URLFetcher API the PDF fix uses).

**Not changed, on purpose:**

- **Starlette stays on 0.49.3** despite open advisories: 1.x drops the
  `TemplateResponse(name, context)` signature every router uses (ADR
  0064). That migration is its own piece of work and the next security
  item to schedule.
- **`/api/docs` stays public.** The API is open source and documented
  anyway; hiding the page wouldn't hide the endpoints.
- **`GET …/print-bundle` still marks invoices printed.** The worst a
  forged request can do is set that flag, and the route needs finance
  write access.

**Consequences:** An API client that read credentials through
`/api/v1/club-settings` stops working. That's intended, but anyone who
used it must configure integrations in the UI. Existing installations
should rotate both the ICS token and the public form token after
upgrading, because either may already have been read.
