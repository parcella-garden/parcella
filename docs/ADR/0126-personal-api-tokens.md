# Personal API tokens: hashed, revocable, exactly the user's permissions, no scopes

**Context:** issue #306, step 2 of the knowledge base (#285). Until now
the REST API only accepted the JWT from the email + password login,
valid for 24 hours (`app/api_auth.py`). An integration that runs for
months, the MCP connector for an external AI (#307) above all, can't log
in again every day and shouldn't hold a password.

## Decision

- **A personal token per user** (`api_tokens` table, migration 0121):
  name, created, created by, last used, optional expiry (30/90/365 days
  or never; 365 is the default), revoked.
  - The token is `pct_` + 256 random bits. It's shown once
    (`Cache-Control: no-store`, never in a URL) and stored only as its
    SHA-256. A fast hash is enough because the input is random, and it
    allows an indexed lookup.
  - Creating one is Post/Redirect/Get. The first version answered the
    POST with the page itself, so F5 re-submitted the form and silently
    minted a second token (found in the smoke test). The raw token now
    crosses the redirect in a one-time cookie: HttpOnly,
    SameSite=Strict, scoped to the tokens page, 2-minute max-age,
    deleted on first read. The page shows it only if its hash matches
    one of the tokens that page lists, so a planted or leftover cookie
    shows nothing.
  - The prefix tells `get_current_api_user` which kind it is. Anything
    else is still treated as a login JWT, so existing clients are
    unaffected.
- **Exactly the user's permissions, no scopes.** The token resolves to
  its `User`, and every existing check (`require_api_permission`,
  `require_api_role`, ...) applies unchanged. To give an integration
  less access, give it its own user in a Group with only what it needs
  (for #307: notes). One permission system instead of two that can
  drift apart.
- **When a token stops working (401):**
  - it was revoked, or it has expired;
  - its user was deactivated, or must set a new password;
  - its user's password changed. The token stores the user's
    `session_version` at creation; a password change or an admin reset
    bumps that value, ending every older token the same way it ends the
    session cookies.
  The check runs on every request, so revoking takes effect immediately.
- **Revoking sets `revoked_at`; the row stays** (historization,
  ADR 0005). The list shows what existed and when it was last used.
  `last_used_at` is written at most every 5 minutes per token. Deleting
  a user (only possible without history) deletes their tokens.
- **Managed in the web UI only, not via the API.** Creating and revoking
  need a cookie session and a CSRF token, so a leaked token can't create
  more tokens and make itself permanent.
  - Every user manages their own tokens (profile → API tokens).
  - System admins see and revoke everyone's (`/admin/api-tokens`).
  - Admins can also create one for another account, for a dedicated
    integration user that never logs in itself. That's refused for
    another full-access account: a token acts silently, so it would let
    one admin act as another unnoticed. Each token records who created it.

## Rejected

- **Scopes per token.** They would be a second, parallel permission
  system next to Groups (ADR 0041/0070), checked in every API route.
  A dedicated user achieves the same with what already exists.
- **Longer-lived JWTs.** They can't be revoked one by one and would
  still need a password to obtain.
- **bcrypt/argon2 for the hash.** Built for low-entropy passwords; for a
  256-bit random token it only costs time on every request and rules out
  the lookup by hash.
- **OAuth for remote MCP connectors.** Possibly needed by some AI clients
  (#307 checks this); it would sit on top of these tokens, not replace
  them.
