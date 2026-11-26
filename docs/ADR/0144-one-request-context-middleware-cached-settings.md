# 0144: One request-context middleware, club settings cached per process

**Status:** proposed (issue #412)

## Context

Eight `@app.middleware("http")` functions each opened a session on every
request, `/static/` included; three looked up the logged-in user. Every
page view also re-read the same `ClubSetting` rows (module flags,
language, region, currency, nav order, helpdesk link).

## Decision

- **One `request_context_middleware`** (`app/main.py`) fills
  `request.state` in one session with one user lookup. `/static/` skips
  it (and its 404 is plain text, since the error page needs that state).
  `/api/` skips the web-only parts: permissions, group names, nav
  counts, the forced password change (the API refuses a token instead).
- **`app/settings_cache.py`** keeps those settings for 30 seconds per
  process. Any ORM commit that touches a `ClubSetting` row clears it
  (SQLAlchemy `after_flush` marks the session, `after_commit` clears),
  so an admin's change shows on the very next request. A generation
  counter stops a request that read the old values just before the
  commit from caching them. A backup restore clears it too.
- **Not cached:** branding (the logo version is the file's mtime, which
  changes without a settings write) and the nav badge counts (they
  follow every booking, sign-up and approval).

## Consequences

- A `ClubSetting` written outside the ORM (raw SQL, another process)
  shows up within 30 seconds, not at once. Today only the startup
  re-key does that, before the app serves requests.
- With more than one worker process (#418), a change shows at once in
  the process that made it and within 30 seconds in the others.
