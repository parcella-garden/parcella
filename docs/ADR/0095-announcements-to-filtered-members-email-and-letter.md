# Announcements to filtered members: same module, stored filter, email + letter

**Context:** Issue #242: from the filtered member list, send a message
by email or by post to exactly those members, "re-using the
announcement feature". Announcements so far were club news: one text to
every active member who opted into "email info", plus a WordPress draft
and a printable notice.

**Decision:** A targeted message is an ordinary `Announcement` with a
stored member-list filter.

- `audience_filter` holds `MemberListFilter.to_dict()` -- the same
  object the list, its CSV export and Previous/Next use (ADR 0093), so
  "who is on screen" and "who gets the message" can't drift apart. NULL
  keeps every existing announcement exactly as it was.
- The filter is resolved when shown and when sent, not frozen into a
  recipient list: the board sees who will get it right now, and fixing
  a member's record (adding an email address) takes effect without
  rewriting the message.
- Email goes to everyone in the filter with an address, **ignoring the
  email-info opt-out** (kermie's call): a message to some members is
  operational, the opt-out is about newsletters. Club news keeps
  honouring it.
- Members without an email address get a letter (or everyone, with
  "letters for everyone"): a new `LETTER` channel, one DIN 5008 letter
  per recipient in one PDF, address window shared with invoices.
  Members with neither are named as unreachable, not silently dropped.
- BLOG and PRINT don't apply and are refused server-side (409), like
  any unavailable channel action (ADR 0087).
- Letters are **never stored**. They contain names and addresses, and
  the only persistent upload directory is served publicly under
  `/static`. They're rendered on click instead; the delivery row keeps
  only when, how many and for which content -- no names.
- An empty filter isn't a targeted message (the button only shows on a
  filtered list, and the server treats an empty filter as club news):
  "everyone, ignoring the opt-out" must not be one click away.

**Consequences:** One module, two kinds of announcement, told apart by
`is_targeted`. The audience can change between sending the email and
generating the letters; the page shows the current split, and that's
accepted over freezing a list that would then go stale. If stored
generated documents with personal data are ever needed, they need a
non-public storage location first -- not `app/static/uploads/`.
