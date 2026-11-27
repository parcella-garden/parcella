# Hand-picked members are part of the member-list filter

**Context:** Issue #337: after filtering `/members/` (e.g. everyone who
allows club emails, 102 people) the board wants to tick a few rows by
hand (12) and export or write to only those. Messages to filtered members
(#242, ADR 0095) store the `MemberListFilter` and re-resolve it at send
time; messages to picked applicants (#247, ADR 0112) store a plain id
list instead.

**Decision:** The selection is one more field of `MemberListFilter`:
`ids`, a tuple of member ids.

- **It narrows, it doesn't replace.** `apply()` adds `Member.id IN (ids)`
  on top of the other conditions, so a picked member who no longer
  matches the filter -- or was deleted -- drops out, the same as for any
  other filtered message. Picking and filtering can't contradict each
  other.
- **Everything that already takes a filter gets it for free:** the CSV
  export, the stored `Announcement.audience_filter` (JSON, no migration),
  letters, Previous/Next on the detail page and the list itself
  (`/members/?ids=...` shows just the picked ones).
- **Not a second audience kind** like `audience_applicant_ids`: members
  have letters, the opt-out rules and the "show list" link of #242, which
  an id list beside the filter would have to duplicate.
- Ids are cleaned where the filter is built (blank/overlong dropped,
  duplicates removed) and capped at 2000 with a 400 -- the same sanity
  cap as for applicants, never a silent cut.

**Consequences:**

- Long selections make long URLs (repeated `ids=`, ~40 bytes each);
  fine for the club sizes in view, and the cap keeps it bounded.
- Ticks live in the page only: changing the filter reloads the list
  and clears them.

**Update (issue #425, [ADR 0145](./0145-member-and-parcel-lists-paged-select-all-means-the-filter.md)):**
the list is paged now, so ticks live on one page (≤ 100 ids), and "all
matching" sends the filter without ids. "Fine for the club sizes in view"
did not hold: 2,000 ids are refused by the server before the cap is reached.
