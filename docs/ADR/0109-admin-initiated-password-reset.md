# Admin-initiated password reset: generated, shown once, forced change

**Context:** Issue #244. A user who forgot their password had no way
back in. A self-service "forgot password" link was ruled out on purpose:
it turns the mailbox into the account's real credential, and a lot of
member addresses in a garden club are shared family accounts. kermie
asked for an admin to reset the password instead, with the user forced
to choose a new one at the next login.

## Decision

1. **Only a system admin can reset, and only someone else's password.**
   `POST /admin/users/{id}/reset-password` (`require_system_admin`, CSRF
   like every form) on the user edit page. An admin's own account goes
   through `/auth/change-password`, which asks for the current password.

2. **Parcella generates the password; the admin doesn't type it.**
   `generate_temporary_password()` in `app/auth.py`: four groups of four
   from an alphabet without look-alike characters (no 0/O, 1/l/I), about
   90 bits. Hand-picked temporary passwords tend to be weak and reused
   ("Garten2026!").

3. **Shown once, never in a URL.** The POST renders the edit page
   directly with the password (`Cache-Control: no-store`) instead of
   redirecting, so it ends up in neither the address bar, the browser
   history nor an access log. Only the bcrypt hash is stored; there is no
   way to show it again -- reset again if it got lost.

4. **Reuse the bootstrap admin's mechanism.** The reset sets
   `must_change_password`, so `password_change_middleware` (`app/main.py`)
   sends every page to `/auth/change-password` and the REST API refuses
   to issue a token until the user picks their own password. The user
   enters the temporary password as "current password" there.

5. **The reset ends every open session** (`session_version += 1`), the
   same as a password change does.

## Not done (known gaps)

- No email delivery of the temporary password -- the admin passes it on
  by phone or in person. Mailing it would bring back the mailbox-as-
  credential problem from the context above.
- A reset doesn't reactivate a deactivated account (the page says so);
  that stays a separate, deliberate action.
- The login throttle (ADR 0065) is keyed by the user's IP, which the
  admin's request doesn't know, so it isn't cleared by a reset; a locked
  out user waits for the window to expire.
- No REST endpoint yet: there is no users API to put it on.
