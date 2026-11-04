# Email log: the SMTP result, its own session, deleted after 90 days

**Context:** Issue #270 asked for a log of outgoing emails: date/time,
recipient, and whether delivery worked, "provide bounce notification
if applicable". All mail goes through one function,
`app.email_service.send_email()` (invoices, announcements, applicant
and purchase-request mails, work-hours notifications, invitations).

**Decision:**

- **Log in `send_email()`, nowhere else.** One `email_logs` row per
  attempt (`app/email_log.py`): recipient, subject, `SENT`/`FAILED`,
  the error, attachment count. Every caller is covered, and so is any
  future one.
- **The SMTP result only.** `SENT` means the server accepted the
  message. A bounce comes back later as a mail into the sending
  mailbox, and Parcella doesn't read that mailbox. kermie chose this
  over IMAP bounce reading for now; "SMTP not configured" is logged as
  `FAILED` too, so a missing setup shows up.
- **Own session and transaction** (`record_email()` opens
  `AsyncSessionLocal`). The caller's session is left alone: a caller
  that rolls back doesn't lose the entry, and we never commit a
  caller's half-done work. Any error while logging is caught and only
  logged, so a broken log never stops mail.
- **Deleted after a retention period** (`email_log_retention_days`,
  default 90, 1-3650, on `/admin/settings`). Recipient addresses are
  personal data. The purge runs on regular site use at most once an
  hour, like applicant retention (ADR 0091), with no scheduler. A hard
  delete, like ADR 0091, not historization: a log line isn't club
  history.
- **System admins only** (`require_system_admin`, admin nav), and
  ADMIN role on the read-only `GET /api/v1/email-log`.

**Rejected:**
- *Reading bounces via IMAP* (new settings, polling, parsing RFC 3464
  delivery reports, matching them to log rows by Message-ID). It's the
  only way to see real non-delivery, but much more code, and the
  sending mailbox may already be read by the helpdesk (FreeScout),
  which would race for the same messages. A possible follow-up.
- *Logging in each caller.* Six modules, easy to miss in a seventh.
- *Storing the message body.* Invoices and announcements would then
  sit in the log a second time, with the personal data in them; the
  subject is enough to tell mails apart.

**Consequences:**
- `SENT` can be read as "delivered" by mistake; the page says what it
  means in its intro line.
- Every send costs one extra small insert in its own connection.
