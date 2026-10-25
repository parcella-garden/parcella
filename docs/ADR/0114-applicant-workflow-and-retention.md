# Applicants: status workflow without "withdrawn", deletion after a retention period

**Context:** After the first weeks of real use, kermie reported six
issues against the applicants module (#251-#256). Three of them change
how the module is shaped rather than just how it looks:

- `ACCEPTED` meant "took a plot" and was set by the parcel handover
  (ADR 0101). In practice "accepted" is the long phase *before* the
  handover: the applicant wants the offered plot, and the old and new
  tenant still negotiate. "Assign a parcel" was hidden in exactly that
  phase (#252).
- `WITHDRAWN` had no clear meaning (#253). An applicant who turns a plot
  down either wants no further offers -- that's `REJECTED` -- or stays on
  the waiting list -- that's back to `CONTACTED`.
- Closed applications piled up; ADR 0091 left automatic deletion out
  "for now" (#255).

**Decision:**

- **Statuses:** `NEW` → `CONTACTED` → `OFFERED` → `ACCEPTED` → `CLOSED`,
  or `REJECTED`. `ACCEPTED` is an open status
  (`APPLICANT_OPEN_STATUSES`), so the handover button stays. The
  handover sets the new `CLOSED`. There is no `WITHDRAWN`.
- **Migration 0113** moves existing `WITHDRAWN` rows to `CONTACTED`
  (kermie's call: back on the waiting list) and renames the enum label
  `WITHDRAWN` to `CLOSED` -- Postgres can't drop a label, and a renamed
  one leaves no dead value behind. Existing `ACCEPTED` rows whose email
  belongs to a member were finished handovers under the old meaning and
  become `CLOSED`. Old `change_history` rows keep their "WITHDRAWN"
  text; the translation key stays for them.
- **Retention period:** the club setting `applicant_retention_months`
  (admin settings, "Applicants" card). Every application whose last
  status change -- or, without one, its application date -- is older
  than that is hard-deleted with its history (ADR 0091), **whatever its
  status**, open ones included (kermie's call: someone who's been on the
  waiting list untouched for two years has to re-apply). Blank or 0
  switches it off, which is the default.
- **No cron job, no notice:** `nav_counts_middleware` (app/main.py) calls
  `maybe_purge_expired_applicants()` on logged-in requests, at most once
  an hour per process. A retention measured in months doesn't need more
  precision, and Parcella has no scheduler to rely on. Nobody is told --
  not the board, not the applicant (#255 asked for exactly that).

**Consequences:**

- REST API clients that send or filter by `WITHDRAWN` now get a 422 --
  a breaking API change.
- An open application whose status the board never touches disappears
  once the period is over. Moving it to another status (or back) resets
  the clock; editing contact data or the board note doesn't.
- Deletion only happens while someone uses Parcella. On an instance
  nobody logs into, expired applications stay until the next login.
- The "Consent given" field was read as board approval (#251). It is
  the applicant's data-protection consent from the website form and is
  now labelled that way; there's no board-approval step.
