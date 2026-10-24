# Announcements to picked applicants: a stored id list, email only

**Context:** Issue #246 asked for picking applicants on `/applicants/`
(all, none or some), and issue #247 for emailing exactly those from
Parcella with the existing paced SMTP sending, once per address even
when someone applied twice. #242 already writes to *filtered members*
through the announcements module (ADR 0095), storing the member-list
filter and resolving it again at send time.

**Decision:** Reuse announcements again, with a second kind of audience.

- `Announcement.audience_applicant_ids` (JSON list) holds the ticked
  applicant ids. It is mutually exclusive with `audience_filter`;
  `is_targeted` covers both, and `is_applicant_message` tells them apart.
- **An id list, not a filter.** The selection is hand-picked row by row,
  so there is no filter to re-run. It is fixed when the message is
  created: applicants ticked later are not added. An applicant deleted
  in the meantime simply drops out.
- **Email only.** Applicants have no postal address on file, so there
  are no letters (LETTER refused with 409); like #242, no blog post and
  no notice-board page.
- **One email per address.** `resolve_audience()` compares addresses
  ignoring case and surrounding blanks; the oldest application keeps the
  slot and the page shows how many were merged.
- **Refused, not downgraded:** an empty or entirely unknown selection is
  a 400. It never falls back to club news (the #242 review finding was
  the same shape: one click must not reach the whole club).
- Starting one needs board/full access (announcements' `require_admin`),
  the applicants module on, and applicants read permission.

**Consequences:**

- No REST API field for it, the same as `audience_filter` (#242): the
  announcements API doesn't expose audiences at all yet.
- No per-recipient delivery log, as for every announcement.
