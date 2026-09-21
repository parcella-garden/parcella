# Task board: per-card change history, via the existing generic audit log

**Context:** kermie wanted a change history visible inside each task
ticket. The task board previously kept none -- only each card's current
`list_id` plus `created_at`/`updated_at`, and an append-only comment
thread (see `docs/module-tasks.md`; this was also the explicit caveat
baked into the Markdown activity export, ADR-less feature shipped just
before this one). Meanwhile the app already has a generic mechanism for
exactly this, used elsewhere: `ChangeHistory` (`app/models.py`, "logs
field changes on arbitrary entities... without needing a separate
history table for every table") plus `ChangeTracker`
(`app/change_tracker.py`, snapshot-before / diff-at-commit), with
`app/services/parcels.py::update_parcel` as the reference consumer (ADR
0070) and `app/templates/parcels/detail.html`'s history table as the
reference display.

**Decision:** reuse `ChangeHistory`/`ChangeTracker` rather than a
bespoke `TaskHistory` table -- no migration needed at all, since
`ChangeHistory` is schema-agnostic (`entity_type`/`entity_id`, not a
dedicated table per module).

Tracked fields, and where each is written:

- `title`, `description`, `due_date`, `priority`, `tags` -- via
  `ChangeTracker(task, "Task", TASK_TRACKED_FIELDS)` in **both**
  `app/routers/tasks.py::task_update` (web) and
  `app/routers/api_tasks.py::task_update` (API). There's no shared
  "update task fields" service function for tasks today (unlike
  parcels' single `update_parcel`), so this duplicates the tracker call
  the same way the field-setting loop itself is already duplicated
  between the two routers -- not introducing a new shared service
  function just for this.
- `list_id` -- written directly inside `app/task_board.py::move_task()`
  as a single `ChangeHistory` row (not the full `ChangeTracker` class,
  since `move_task` already computes `old_list_id`/`new_list_id`
  itself), only when the card's list actually changes (not on a
  same-list drag-reorder). `move_task()` is the single funnel every
  list change goes through -- web drag-and-drop, the edit modal's list
  dropdown, and the API's dedicated move endpoint all call it (the
  API's `PUT /{task_id}` can't change `list_id` at all --
  `KanbanTaskUpdate` has no such field) -- so writing history here once
  covers every surface for free.

Display: a "Change history" section in the edit modal (`#taskModal`,
see ADR 0084), below Comments -- same table shape as
`parcels/detail.html`'s (timestamp, raw `field_name` in `<code>`, old
value, new value, changed by), untranslated field names, matching that
existing convention rather than adding a translation key per field. One
special case: `list_id`'s old/new values are resolved to list *names*
via the board's already-loaded `lists`, since a raw `TaskList` id would
otherwise be meaningless -- no other tracked field needs this (parcels
never tracks an FK-valued field, so there was no prior art for it).

**Explicitly out of scope, to avoid a half-baked result:**

- **Assignee changes.** `assigned_to_ids` is a derived property over the
  `TaskAssignee` join table, not a plain column -- feeding it through
  `ChangeTracker` as-is would stringify a raw Python list of user UUIDs,
  worse than not showing it. Would need its own bespoke
  before/after-with-names diff. Reasonable follow-up, not this one.
- **Bulk list reassignment on list deletion.** `delete_list()` moves
  every card in a deleted list to another one; every affected card's
  `list_id` changes, but as a side effect of deleting the *list*, not a
  deliberate per-card edit. Looping a history entry per reassigned card
  adds complexity for a secondary path -- noted, not implemented.

**Consequence:** history only exists from when this feature shipped
onward. There's no retroactive data for moves/edits that happened
before it, and the activity-report export (Markdown) doesn't read this
table either yet -- both are known, accepted gaps, not oversights.
