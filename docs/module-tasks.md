# Task board module

A general-purpose kanban board for club business that isn't tied to a
work session -- "renew the insurance policy," "call the electrician,"
"follow up with the roofer." Admin/board only, both for viewing and
editing. Columns ("lists") are user-configurable: a board/admin user can
add, rename, reorder, and delete them (issue #100).

## Why a separate module from WorkTask

The work-hours module already has a `WorkTask` model (see
`docs/module-work-hours.md`), but it's deliberately scoped to a single
work session: a task there is either in the backlog, scheduled to a
session, or assigned to one of that session's signed-up participants.
That's a fundamentally different shape from a general club task --
there's no session to schedule against, no participant to assign to,
and no reason a card should ever need to "belong" to a work session.

Rather than stretch `WorkTask` to cover both use cases (nullable session
fields growing more nullable, status semantics diverging), this is a
fully separate model, table, and pair of routers. Confirmed with the
person requesting the feature before building it -- see
[Architecture Decisions](./ADR/0034-task-board-a-separate-module-from-worktask-admin-board-only.md).

## Data model

```
task_lists     -- one row per kanban column
tasks          -- one row per kanban card
task_comments  -- one row per comment on a card (issue #108)
```

**`TaskList`** (issue #100, [ADR 0044](./ADR/0044-task-board-configurable-lists.md))
is a column: `name` (free text -- see "Column labels are no longer
translated" below) and `position` (a gapless 0-based index among all
lists on the board). Originally (v1, [ADR 0034](./ADR/0034-task-board-a-separate-module-from-worktask-admin-board-only.md))
columns were a fixed `TaskStatus` enum (`TODO`/`IN_PROGRESS`/`DONE`);
migration `0054_task_lists` replaced it with this table and seeded
those same three as the default lists, so existing boards look
unchanged right after the upgrade.

**`Task`** has `list_id` (FK to `TaskList`, replacing the old `status`
enum column) and `position` (a gapless 0-based index within its list,
used for both drag-and-drop ordering and the CSV/API iteration order).
`created_by_id` references `User` (not `Member`) -- consistent with this
being an internal admin/board tool, not member-facing club business
(compare `ChangeHistory.changed_by_id`, `WorkSession.created_by_id`).

**`TaskAssignee`** (issue #109, [ADR 0046](./ADR/0046-task-board-multiple-assignees-per-card.md))
is a card's assignment to a `User` -- a card can have any number of
assignees. Migration `0057_task_multiple_assignees` replaced the original
single `Task.assigned_to_id` FK with this join table, mirroring
`GroupMembership`'s shape (own `id`, `UniqueConstraint` on the
task_id/user_id pair). `Task.assigned_to_ids` is a Python `@property`
(`[a.user_id for a in self.assignees]`), not a mapped column, so callers
must eager-load `Task.assignees` before reading it or serializing a
`KanbanTaskOut` -- see the routers for the `selectinload(Task.assignees)`
call on every fetch, and note that a write there refreshes only the
specific attributes touched (`attribute_names=[...]`) rather than a
blanket `db.refresh()`, since that would expire the already-loaded
`assignees` collection (see CLAUDE.md's identity-map sharp edge).
Web-form and API updates fully resync the assignee set on every write
(delete what's no longer submitted, add what's new), the same pattern
`finances.py` already uses for `parcel_scopes`/`member_scopes`.

`priority` (issue #106, migration `0055_task_priority`) is an optional
`TaskPriority` enum (`LOW`/`MEDIUM`/`HIGH`). Nullable with no default --
unset means "no priority" rather than implicitly `MEDIUM`, since every
card that existed before this migration has no real basis for a guessed
priority. Shown on the board as a small colored badge on the card
(`app/templates/tasks/board.html`) and editable from the same
create/edit form as due date and assignee; there's no separate
"priority" column or swimlane, and cards aren't auto-sorted by
priority -- `position` (drag-and-drop order) still governs ordering
within a list.

`tags` (issue #107, migration `0056_task_tags`) is a Postgres text array
(`ARRAY(String)`), not a join table to a separate `Tag` entity: there's
no cross-card vocabulary to enforce or reuse-by-reference here (unlike,
say, `InventoryCategory`), just a per-card list of short free-text
strings. `NOT NULL` with a `'{}'` server default -- an untagged card is
an empty list, not `NULL`, so every consumer (board template, CSV/API
iteration) can iterate `task.tags` unconditionally. The web form takes a
single comma-separated text input (`app/templates/tasks/form.html`),
split/stripped/deduped by `_parse_tags()` in `app/routers/tasks.py`; the
API takes a plain `list[str]` (`KanbanTaskBase.tags`). Shown on the board
as small pill badges under the card title/meta line, one per tag, in the
same style family as the priority badge but a single neutral color
(tags have no fixed small set of values to give distinct colors to,
unlike priority's three).

**Migration gotcha, the mirror image of the one in
[docs/module-work-hours.md](./module-work-hours.md#known-pitfalls):**
inside `op.create_table(...)`, an inline `sa.Enum(...)` column
auto-creates the Postgres type as a side effect -- but a standalone
`op.add_column(...)` on an *existing* table does not. `0055_task_priority`
needs an explicit `op.execute("CREATE TYPE taskpriority AS ENUM (...)")`
before the `add_column` call (with `create_type=False` on the column's
`sa.Enum(...)` to stop SQLAlchemy from trying a second, redundant
`CREATE TYPE`), same pattern as `0008_zaehlerwesen`'s `medium` column.
Skipping it fails at `alembic upgrade head` with `type "taskpriority"
does not exist` -- caught before merge because `run_tests.sh` runs
migrations against the disposable web image entrypoint, not just
`create_all` in the test suite itself.

## Comments (issue #108)

`TaskComment` is a simple append-only comment thread per card -- `task_id`
(FK, `ON DELETE CASCADE` -- a comment can't outlive its task), `content`
(plain text), `created_by_id` (FK to `User`, `ON DELETE SET NULL`), and
`created_at`. Modeled after `TicketMessage`
(`docs/module-tickets.md`) but without that model's
email/direction/HTML-sanitization concerns, none of which apply to an
internal task comment.

Add and delete only, no edit -- an append-only log is enough for "leave a
note for whoever picks this up next," and keeping it add/delete-only
avoids a second write path and an audit-trail question (was this
comment edited after someone read it?) that wasn't asked for. Delete is
not restricted to the comment's own author: like the rest of this
module, every admin/board user already has full read/write access to
every card, so there is no finer-grained permission to enforce here
either.

Web: comments live on the task edit page (`/tasks/{id}/edit`,
`app/templates/tasks/form.html`) since that's the only page a single
card is ever shown on -- `POST /tasks/{id}/comments` to add, `POST
/tasks/{id}/comments/{comment_id}/delete` to remove, both redirecting
back to the edit page. API: `GET`/`POST /api/v1/tasks/{id}/comments` and
`DELETE /api/v1/tasks/{id}/comments/{comment_id}`, same
`require_admin_api` boundary as the rest of `/api/v1/tasks`.

## Card and list ordering: `app/task_board.py`

Shared between the web router and the REST API so both move cards/lists
with identical semantics:

- `next_position()` / `next_list_position()`: a new card/list is
  appended to the end of its list/the board.
- `move_task()`: moves a card to a list + index. Renumbers the affected
  list(s) in one pass -- correct whether it's a cross-list move or a
  pure same-list reorder, since a same-list move is just "exclude this
  card, reinsert at the new index, renumber."
- `move_list()`: same reinsert-and-renumber shape as `move_task()`, for
  reordering the columns themselves (there's only one board, so no
  cross-container case).
- `close_gap_after_delete()`: renumbers the remaining cards in a list
  after one is deleted, so `position` never has holes.
- `delete_list()`: the one genuinely new piece of logic -- see "List
  management" below.

All of these fully rewrite the affected list's `position` values rather
than doing fractional/gap-based positioning -- correct and simple at
the card/list counts a club's task board will realistically ever have.

## List management

A board must always have at least one list. `delete_list()` enforces
two rules, each raising a `ValueError` with a short code
(`last_list`/`missing_target`/`target_not_found`) that the routers turn
into a translated 400 (web) or a plain-English 400 (API):

- The last remaining list on a board cannot be deleted.
- Deleting a list that still has cards requires a `move_to_list_id`
  identifying a *different*, existing list -- its cards are appended (in
  their existing relative order) to the end of that list, which is then
  renumbered. Chosen over silently cascade-deleting the cards (this
  repo historizes rather than deletes, see ADR 0005) and over an
  Inventory-style `ON DELETE SET NULL` (which doesn't fit here: a card
  must always be in a visible column, unlike an inventory item, which
  can fall back to "uncategorized").

The web UI enforces the same "last list" rule client-side too (the
delete action is disabled in the dropdown when only one list remains) --
belt and braces, not a substitute for the backend check.

## Column labels are no longer translated

Before configurable lists, `column_todo`/`column_in_progress`/
`column_done` were i18n keys, translated per viewer language. Now that
an admin can add or rename lists, a list's `name` is free text stored
once per club -- like `InventoryCategory.name` -- not re-translated per
viewer. The migration seeds the three default lists in English; a club
that wants them in another language renames them once, the same way
they'd rename an Inventory category.

## Web UI: drag-and-drop

`app/templates/tasks/board.html` implements native HTML5 drag-and-drop
(no library) for both cards and columns, using the same insertion-point
technique for each (comparing the pointer position against the target's
siblings' bounding rects) but kept in separate JS state (`draggedCard`
vs. `draggedColumn`) so the two gestures never interfere:

- Dragging a **card** shows an insertion point among the target list's
  other cards and calls `POST /tasks/{id}/move` with the resulting
  `list_id` + index as JSON.
- Dragging a **column header** reorders the columns and calls
  `POST /tasks/lists/{id}/move` with the resulting index.

On any request failure, the page reloads to resync with the server
rather than leaving the UI in a state the backend disagrees with.
Rename/delete are Bootstrap modals (one shared modal per action,
populated from the clicked column's `data-*` attributes), following the
same `data-bs-toggle="modal"` pattern as the CSV-import modal in
`app/templates/members/list.html`, rather than one modal per column.

## Search and filter (issue #119)

A search box (title, description, tags, comment content) plus filters
for priority, tag, owner (assignee), and due month/year sit above the
board. All of it is client-side JS over `data-*` attributes already
rendered on each card -- see [ADR 0049](./ADR/0049-task-board-search-and-filter-client-side.md)
for why (the board is a single all-at-once page, same as admin
settings' own card search) and for why card dragging is disabled while
any filter is active (position ambiguity among hidden siblings) while
column/list dragging stays unaffected. `board()`'s query gained
`selectinload(Task.comments)` to make comment text searchable -- the
one server-side change this needed, since everything else the search/
filter reads was already loaded for some other reason (assignees for
the meta line, tags for the tag pills, etc.).

## Sort (issue #120)

A "Sort tasks" dropdown next to the filter bar reorders each column's
cards by due date (`data-due-month`, month/year granularity -- same as
the due-month filter, not exact day) or priority (High -> Medium ->
Low, no-priority last), or back to "Manual" (drag order). Purely
visual, client-side, and never touches `Task.position` -- see
[ADR 0050](./ADR/0050-task-board-sort-client-side-visual-only.md) for
why sorting doesn't persist and, like an active filter, disables card
dragging while it's non-manual (there's no meaningful `position` to
write while the board isn't showing manual order).

## Dashboard overdue-tasks card (issue #127)

The dashboard (`/`, `app/main.py`'s `startseite()`) shows an "Overdue
Tasks" count (gated on `module_flags.tasks`) linking to
`/tasks/?overdue=1`, which pre-checks the board's own "Overdue only"
filter checkbox -- same `data-overdue="1"` attribute and definition of
"overdue" (`due_date` in the past, any list) the board already used to
color a card red. See [ADR 0051](./ADR/0051-dashboard-overdue-tasks-card.md).

Lists themselves are managed inline on the board (rename/delete via the
column header's dropdown), since there's no other data to edit on a
list besides its name.

## Create/edit as a modal, with a real per-card URL (issue #232 follow-up)

`/tasks/new` and `/tasks/{id}/edit` used to render a separate page
(`app/templates/tasks/form.html`, now deleted) -- a deliberate choice
for consistency with Members/Parcels/Work Hours. That's since been
reversed: both routes now render the *board* itself
(`app/routers/tasks.py::_render_board()`, shared by all three of
`board()`/`task_new_page()`/`task_edit_page()`) with a `#taskModal`
pre-opened on top of it, instead of navigating to a separate page. See
[ADR 0084](./ADR/0084-task-board-modal-editing-with-real-urls.md) for
why, and for the alternative (a true AJAX/pushState modal) explicitly
rejected in favor of this simpler, reload-based approach: clicking a
card is a normal navigation to `/tasks/{id}/edit`, which is a real,
unique, bookmarkable/refreshable URL -- there's no client-side routing
in this codebase, deliberately not introduced here either. Closing the
modal (X, backdrop, Esc, or Cancel) all funnel through Bootstrap's
`hidden.bs.modal` event, which navigates back to `/tasks/`.

The edit modal now also shows the card's change history -- see below.

## Change history per card (issue #232 follow-up)

Each card's edit modal has a "Change history" section below Comments,
listing every recorded field change (timestamp, field, old value, new
value, changed by), newest first. This reuses the app's existing
generic audit log rather than a bespoke table -- see
[ADR 0085](./ADR/0085-task-board-change-history-via-change-history.md).
Tracked fields: `title`, `description`, `due_date`, `priority`, `tags`
(via `app/change_tracker.py`'s `ChangeTracker`, in both
`app/routers/tasks.py::task_update` and
`app/routers/api_tasks.py::task_update`) and `list_id` (written
directly inside `app/task_board.py::move_task()` -- the single funnel
every list change goes through, web drag-and-drop and the API's move
endpoint included -- only when the list actually changes, not on a
same-list reorder). `list_id`'s old/new values are resolved to list
*names* in the template, not shown as raw ids.

**Not tracked, deliberately:** assignee changes (`assigned_to_ids` is a
derived property over the `TaskAssignee` join table, not a plain
column -- would need its own before/after-with-names diff to display
sensibly, not a good fit for the generic field-diff mechanism as-is),
and the bulk list reassignment `delete_list()` does when a list with
cards is deleted (a side effect of deleting the list, not a deliberate
per-card edit). Both are reasonable follow-ups, not done here.

History only exists from when this feature shipped onward -- there's no
retroactive data for moves/edits that happened before it.

## Activity report export (Markdown)

A third header button ("Export report", next to "Add list"/"New task")
opens a modal to pick a date range and downloads a Markdown file
(`GET /tasks/export?date_from=...&date_to=...`, `app/task_report.py`)
meant to be pasted into an LLM to draft board minutes or a monthly
protocol. Defaults to the last 30 days if hit without query params.
Admin/board only, same `require_admin` check as every other route in
`app/routers/tasks.py`.

The report has three sections:

1. **Cards touched in the period** -- created or updated within the
   range.
2. **Comments in the period** -- the closest thing this module has to a
   decision/discussion log.
3. **Full board snapshot** -- every current card, any list, as of
   generation time, for context regardless of the chosen window. Not
   filtered by any "done"-looking list name, since lists are free text
   and user-configurable (see "Column labels are no longer translated"
   above) -- there's no reliable way to infer which list means "done".

**Important limitation, stated in the generated file itself (not just
here):** "Touched" in section 1 means created or updated in the window,
not necessarily "moved to its current list on this date" -- the report
itself doesn't read the change-history table described below (a
reasonable follow-up, not done here), so it still can't reconstruct an
exact move timeline from before this feature shipped or reflect the new
per-field history it now records. Whoever reads the exported file
(human or LLM) needs that caveat to avoid inventing a precise timeline
the data doesn't support.

## A full REST API, alongside the web UI

`/api/v1/tasks` covers list (with an optional `list_id` filter),
retrieve, create, update, delete, a dedicated `POST .../move`
endpoint that runs the same `move_task()` logic the web UI's
drag-and-drop uses, and `.../{id}/comments` (list/add) plus
`.../{id}/comments/{comment_id}` (delete) for the comment thread (issue
#108, see "Comments" above). `/api/v1/tasks/lists` (registered before the
`/{task_id}` routes so a literal path like `/lists` is never captured by
a `{task_id}` path parameter) covers the equivalent CRUD + move for
columns, plus `DELETE .../lists/{id}?move_to_list_id=...` for the
reassign-then-delete flow above. Admin/board only (`require_admin_api`),
matching the web UI's permission level -- unlike most modules, viewing
is not open to regular members here (see the ADR entry for why).

**Breaking change (issue #100):** `status` (`TODO`/`IN_PROGRESS`/`DONE`)
on the task endpoints was replaced by `list_id`. There's no versioning
scheme in this API to preserve the old shape alongside the new one, and
once lists are user-renameable/addable, "status" has no stable meaning
left to preserve.

**Breaking change (issue #109):** `assigned_to_id` (a single, optional
user id) was replaced by `assigned_to_ids` (a list) on
`KanbanTaskCreate`/`KanbanTaskUpdate`/`KanbanTaskOut`, same
no-versioning rationale as the `status` -> `list_id` change above.

## A naming collision found while building this

`app/schemas.py` already defined `TaskBase`/`TaskCreate`/`TaskUpdate`/
`TaskOut` for `WorkTask`. Python doesn't error on a duplicate class
name in the same module -- it silently lets the later definition shadow
the earlier one. This first went unnoticed (both sets of names looked
individually correct in isolation) and broke `api_work_hours.py`'s task
endpoints at runtime, caught by the existing
`test_task_lifecycle` test in `tests/test_work_hours.py`. Fixed by
prefixing this module's schemas `KanbanTask*` instead, with a comment
in `app/schemas.py` explaining why -- worth checking for whenever a new
module's domain noun (here, "task") is generic enough to already be in
use elsewhere.

## Testing

`tests/test_tasks.py` covers: default placement in the first list at the
end, cross-list moves (and that the old list compacts correctly),
same-list reordering, delete closing the gap in the remaining list,
field updates, list create/rename/reorder, deleting an empty list,
deleting a list with cards (reassignment, order preserved, target
renumbered), the "can't delete the last list" and
"non-empty delete needs a target" 400s, the admin/board-only permission
boundary on both the web UI and the API (403 for a readonly member, on
both task and list endpoints), the full web create/edit/move/delete flow
for both cards and lists, the module-disabled-returns-404 case,
setting/updating/clearing `priority` via both the API and the web
form (including that the priority badge disappears from the rendered
board once cleared), (issue #109) creating/reading a task with
multiple assignees, resyncing the assignee set on update (including
that omitting `assigned_to_ids` from a `PUT` body leaves existing
assignees untouched), the web form's checkbox grid pre-selecting
existing assignees on edit, (issue #108) adding/listing/deleting
comments (both web and API, plus the 404s for a comment on a
nonexistent task or a nonexistent comment id), and (issue #119) that
the board renders the right `data-search-text`/`data-priority`/
`data-tags`/`data-assignee-ids`/`data-due-month` attributes (including
comment content folded into the search text) and that the tag/owner
filter dropdowns only offer options actually present on the board, and
(issue #120) that the sort dropdown and its options render -- the
search/filter/sort behavior itself is client-side JS, untestable via
`pytest`, so these tests only cover the server-rendered data/markup it
reads.

**Test-DB sharp edge:** the test suite builds its schema from
`app/models.py` via `Base.metadata.create_all` (see `tests/conftest.py`),
not by running Alembic migrations -- so migration `0054`'s seeded
"To Do"/"In Progress"/"Done" rows never exist in tests. Any test that
creates a `Task` needs to seed its own `TaskList` rows first (see
`_seed_lists()` in `tests/test_tasks.py` and `_seed_task_lists()` in
`tests/test_sample_data.py`, both of which mirror the migration's seed
data). `app/sample_data.py`'s `_seed_tasks()` looks its three default
lists up by name for the same reason -- it runs after migrations in
production, but tests have to seed them manually first.
