# Detail page Previous/Next buttons walk the filtered list, not the whole table

**Context:** issue #202 asked for Previous/Next buttons on `/members/{id}`
and `/parcels/{id}` so a board member working through records one at a
time doesn't have to keep returning to the list and re-finding their
place. kermie: "it feels clumsy to go onto a member or parcel detail
page, change something, go back to the list ... find the next candidate
to adapt and step into the according detail page again."

## Decision

Previous/Next don't walk the full, unfiltered table. They walk exactly
the ordered result set the list page itself would show for whatever
filter is currently active -- e.g. `/members/?pending_only=true`'s
Previous/Next only moves between pending applications, never jumping
out to an unrelated active member. Without this, a board member
working through a filtered queue (pending applications, terminated
parcels) would have Next silently drop them into an item outside that
queue, which is worse than no Next button at all.

**Mechanism, identical in both routers:**

1. `_filtered_members_query()` / `_filtered_parcels_query()` (the
   latter newly extracted from `parcels_list`'s inline query, mirroring
   the former) already encode the list page's WHERE/ORDER BY -- these
   already existed as (or became) the single source of truth so the
   list, its CSV export, and this navigation can't drift apart, same
   reasoning as issue #198.
2. A small `_members_list_query_string()` / `_parcels_list_query_string()`
   turns the active filter params into a query string (empty if
   nothing is set). Each list row's link to its detail page carries
   this string; the detail page threads it into its own Previous/Next
   hrefs and its "back to list" link, so the filter survives an entire
   browsing session, not just one hop.
3. The detail route re-runs the filtered query (`.with_only_columns(id)`
   -- ID list only, no eager loads) to find the current record's index,
   then looks up its neighbors. **If the current record isn't in that
   filtered set at all** (filter changed since the list was loaded, or
   the record was just edited out of it -- e.g. a pending application
   that just got a `member_since` set while paging through
   `pending_only=true`), Previous/Next are both simply absent rather
   than guessing.

Both buttons render as disabled (`aria-disabled="true"`, `tabindex="-1"`,
Bootstrap's `.disabled` class) rather than being omitted, so the layout
stays stable and a screen reader announces the disabled state instead
of the link just not existing (`usability`/`a11y` labels on the issue).

**Keyboard shortcut: Ctrl+Left/Ctrl+Right, not bare arrow keys.**
Requested as a follow-up once the buttons existed. Bare
`ArrowLeft`/`ArrowRight` was rejected up front: screen readers rely on
them for reading content, and they also move the cursor/selection
inside any text input -- hijacking them globally would be an
accessibility regression on a feature whose own issue was tagged
`a11y`, not an improvement.

Landed on Ctrl+Left/Right after two iterations, kept here so the next
person doesn't have to rediscover either failure mode by hand:

1. **Alt+Left/Alt+Right** (mirroring the browser's own back/forward)
   shipped first but **didn't work in practice**: it's a
   browser-*chrome*-level shortcut in Firefox (and some Chrome setups)
   -- intercepted before the keystroke ever reaches page JavaScript, so
   the handler silently never fired. No page-level `preventDefault()`
   can claw that back; it isn't a page event at all in those browsers.
2. Replaced with **`[`/`]`** (unreserved by any mainstream browser, an
   established web-app convention -- Gmail, GitHub use similar
   bracket/letter shortcuts) as the safe default. Worked, but kermie
   specifically wanted the arrow keys back, just with Ctrl instead of
   Alt as the modifier.
3. Settled on **Ctrl+Left/Ctrl+Right**. Known remaining caveat, flagged
   rather than silently hit a third time: on macOS, Ctrl+Left/Right is
   the default Mission Control "switch Space" shortcut -- an *OS*-level
   binding that neither the browser nor this page can intercept,
   the same failure shape as (1) but one layer further down the stack.
   Accepted as a known trade-off for this specific request rather than
   solved, since there's no page-level fix for an OS-level binding.

Same focus guard throughout all three attempts: the handler bails out
entirely when focus is in an `input`/`textarea`/`select`/
contenteditable element.

**Lesson for next time a page wants to claim a browser- or
OS-native-feeling shortcut:** verify it isn't *already* a reserved
binding at the browser-chrome or OS level before committing to it --
"mirrors a familiar convention" is not the same guarantee as "the page
can actually intercept it." An unreserved key (`[`/`]`, letters) is the
safer default when the exact keys aren't a hard requirement.

Implemented as a single handler in `app/templates/base.html` (alongside
the existing sidebar Escape-key handler) rather than duplicated inline
script in both detail templates -- it looks for `#nav-prev-link`/
`#nav-next-link` by id and is a no-op on every other page, so adding
this to a third module's detail page later (if one ever gets its own
Previous/Next) is "give the links these ids," not "write the handler
again."

## Not done here

Scanning a filtered ID list in Python (`list.index()`) rather than a
single indexed SQL query is intentionally the simple option -- fine at
this project's scale (a few hundred members/parcels per club), and
avoids a window-function query for what's a rarely-large list. Revisit
only if a club-scale report ever makes this a real cost.

This pattern (filter-carrying list links + a small query-string helper
+ re-running the same filtered query for neighbor lookup) is a
reasonable template for a future module's own detail page, the same
way ADR 0019 is for dashboard stat cards -- but it wasn't extracted
into a shared helper here, since Members and Parcels are the only two
detail pages with this need today and the actual filter shape differs
per module; a generic version would be guessing at a shape from two
data points.
