# Work-session sign-up confirmation: only to addresses on file

**Context:** issue #313. After a sign-up through the public website
form, the registrant should get a confirmation email: subject "RE: your
registration to work session on {date}", a boilerplate the board can
set, and the details. If the name matches one resident uniquely, only
that person gets it. Otherwise every resident of the parcel with an
email does, because those are exactly the members the sign-up
registered (see "Matching logic" in docs/module-public-api.md).

## Decision

- **Recipients are members, and only at the address stored on the
  member record** (`primary_email()`: the primary address, else the
  first). The address typed into the public form is **never** mailed.
  The form is unauthenticated, so mailing it would let anyone make
  Parcella send mail to any address under the club's name (kermie,
  2026-11-15). A sign-up whose members have no address on file sends
  nothing, and the board sees it in Parcella as before.
- **Only newly created registrations** are confirmed. A repeated
  sign-up for a session someone is already on sends nothing again.
  One email per member and session.
- **Not gated on `email_notifications`.** That flag is the opt-in for
  club news (announcements). A confirmation of your own registration is
  transactional mail you triggered yourself.
- **Subject: fixed translated template plus the session's date.** The
  visitor's remarks go into the body, quoted, never into the subject:
  they come from a public form, and a mail header is the wrong place
  for them (header-injection shape, see CLAUDE.md). Everything
  user-entered (member name, session title, boilerplate, remarks) is
  escaped into the HTML.
- **Settings: two ClubSetting keys** (`work_hours_signup_confirmation_enabled`,
  default on, and `..._text`), edited in a card on
  `/work-hours/configuration` (work-hours write permission). An empty
  text uses the translated default. The language is the club's
  language, the same as the other system emails.
- **Never breaks a sign-up.** It runs after the commit, and a failing
  send is logged and skipped.
