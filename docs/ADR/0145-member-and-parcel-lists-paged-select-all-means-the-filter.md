# 0145: Member and parcel lists are paged; "all matching" means the filter

**Status:** accepted (issue #425, kermie, 2026-11-27)

## Context

`/members/` and `/parcels/` rendered every row. Measured against the test
database with 1,600 members and 800 parcels, the server needs about a
quarter of a second, but the pages weigh **2.7 MB** and **1.6 MB** (about
1.7 KB per member row), sent uncompressed: HTML is deliberately not
gzipped because it carries the CSRF token (BREACH, ADR 0143). The browser
then lays out every row, and "Select all" ticks all of them.

Ticked rows travel in the URL as repeated `ids=` (ADR 0137), about 40
bytes each. Uvicorn refuses a request line long before the 2,000-id cap
(tested: 800 ids pass, 2,000 don't), and nginx's default 8 KB limit is hit
at about 200. "Select all → Export" on a big club already failed.

## Decision

- **Server-side paging, 100 rows a page**, for the member and parcel lists
  only (the lists that grow with the club). `app/paging.py`: `paginate()`
  counts the filtered query and returns one page; a page past the end
  shows the last page. The page number is a separate query parameter, not
  part of `MemberListFilter`: that filter is stored with announcements,
  where a page means nothing. The pager carries the filter along, and a
  detail page's "Back" link returns to the page its row is on.
  Previous/Next on detail pages still walk the whole filtered list.
- **"Select all" ticks the current page.** When the filter has more rows,
  a "Select all N matching the filter" button appears. It sends the
  **filter instead of ids**:
  - members: the existing path. No ids = the whole filtered list, for the
    CSV export and for "Write to" (ADR 0095). An empty filter stays club
    news, as before.
  - parcels: the CSV export now honours the list's filter (`search`,
    `status_filter`); the notice to leaseholders gets `all_matching=1`
    and resolves the ids server-side, storing them as
    `audience_parcel_ids` as before (ADR 0142). Without the flag an empty
    selection is still refused.
- **Ticks stay on one page.** Changing the page clears them, as changing
  the filter already did. Bigger groups are made by refining the filter,
  or with a tag, not by ticking hundreds of rows (kermie's call). That
  keeps a hand-picked URL at 100 × 40 bytes ≈ 4 KB.
- `MAX_PICKED_MEMBERS` stays at 2,000 as a server-side sanity cap:
  stored announcement filters with more than 100 ids must keep loading.

## Rejected

- **Lazy or virtual rendering** of the full list: same 2.7 MB, more
  JavaScript, and the URL problem stays.
- **Keeping ticks across pages** (in the browser, submitted by POST):
  export, "Write to" and Previous/Next all take a GET filter; a large
  change for a case the filter covers better.

## Consequences

- Footers count the whole filter ("1,612 members"); the parcel footer's
  total area is summed in SQL over the filter, not over the page.
- Short lists (≤ 100 rows) look exactly as before: no pager, no "all
  matching" button.
- Other lists (applicants, contacts, inventory, …) stay unpaged until one
  of them grows comparably; `paginate()` and `_pagination.html` are ready.
