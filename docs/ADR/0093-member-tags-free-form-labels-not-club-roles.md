# Member tags: free-form labels, not club roles

**Context:** Issue #241 asked for tags on members -- "board member",
"extended board member", "water responsible" -- and a filter for them
on the member list. Parcella already has `ClubRole`/`MemberClubRole`
(work hours), whose example names overlap: board, extended board. That
looked like an invitation to reuse it, or to make tags its successor.

**Decision:** Tags are their own small model, `MemberTag` plus a link
table, and carry no meaning the app acts on.

- `ClubRole` stays what it is (see the project memory and
  docs/module-work-hours.md): a per-*year* office that can exempt a
  parcel from work hours. Its rows feed money (exemptions, invoices);
  a label someone types to find the "hedge team" must not.
- A tag has no year and no history. Removing it deletes the link row --
  an explicit exception to ADR 0005's historization, because a label
  records nothing about the club's past that anyone needs later. (If
  "who was water responsible in 2024" ever matters, that's a role with
  a year, not a tag.)
- Names are unique ignoring case and inner whitespace, and tags are
  created on first use from the member page -- otherwise "Water team"
  and "water team" would quietly split one group in two for the filter.
- No colors (kept out of the first version; one more field if wanted).

The list's filters became one `MemberListFilter`
(`app/member_filters.py`) in the same change, since a sixth loose
parameter would have had to be threaded through four places again, and
issue #242 needs to store a filter.

**Consequences:** Two parallel concepts with overlapping example names
("board" as a club role and possibly as a tag). That's accepted: the
role is for work hours, the tag for finding people. Don't merge them
and don't derive exemptions from tags.
