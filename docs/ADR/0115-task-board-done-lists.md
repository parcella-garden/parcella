# Task board: done lists and a done timestamp per card

**Context:** Issue #257. A card that was finished but had a due date in
the past stayed red, and kept counting in the dashboard's "Overdue
Tasks" card and the nav badge (ADR 0051, ADR 0100), because "overdue"
was simply `due_date < today` in any list. Lists are free text and
configurable (ADR 0044), so nothing in the code knew which list means
"done" -- the Markdown report (docs/module-tasks.md) said exactly that.
kermie asked for: a card dragged into the done list is marked done with a
timestamp and is no longer overdue; a card in any other list can be
marked done too.

**Decision:**

- **Only done is done:** `Task.completed_at` is the single source of
  truth for "finished". No code infers it from a list's name, its
  position or the age of a card; every consumer (overdue, badge,
  dashboard, report) reads `completed_at` only. A list becomes a done
  list only by being flagged explicitly.

- **`TaskList.is_done_list`** (bool) marks a list as a done list, set from
  the column's dropdown or the API. Several lists may carry the flag.
  Name matching ("Done", "Erledigt", ...) was rejected: names are free
  text in any language and can be renamed at any time.
- **`Task.completed_at`** (nullable timestamp) is the done state; set = done.
  A boolean plus a separate timestamp would just be two fields that can
  disagree.
- **Moves decide it** (`apply_done_state()` in `app/task_board.py`, called
  from `move_task()`, `create_task()` and `delete_list()`'s reassignment):
  - into a done list: done (an existing timestamp is kept);
  - out of a done list into a normal list: not done again (kermie's call);
  - between two normal lists: unchanged, so a card ticked "Done" by hand
    stays done.
- **The "Done" checkbox** in the card modal and `completed` on
  `PUT /api/v1/tasks/{id}` set it by hand in any list. In the web form a
  list change in the same submit wins over the checkbox, since the
  checkbox shows the state from before the move.
- **Flagging a list** marks the cards already in it done. Unflagging
  leaves all cards as they are -- some may have been ticked by hand, and
  there's no way to tell them apart.
- **Overdue** is now `due_date < today AND completed_at IS NULL`, the same
  in the board (`data-overdue`, red date), `app/nav_counts.py` (badge and
  dashboard card) and the report's snapshot.
- Done/undone changes are written to `change_history` as `completed_at`,
  like `list_id` (ADR 0085).
- **Migration 0114** flags lists named "Done" -- ignoring case, spaces and
  punctuation, so "DONE!" counts (migration 0054 seeded "Done"; kermie's
  board had "DONE!") -- and marks their cards done as of `updated_at`,
  the best available guess for when they got there. Only the English
  word: guessing "Erledigt", "Fertig", ... would be the name-based
  inference this ADR rejects.

**Consequences:**

- Additive API change only: `completed_at` on tasks, `completed` on task
  updates, `is_done_list` on lists; `PUT /api/v1/tasks/lists/{id}`'s
  `name` became optional.
- A club whose done list is called anything but some spelling of "done"
  ("Erledigt", "Archive", ...) has to flag it once by hand. The board
  says so: while no list is flagged it shows a notice pointing to the
  column menu, so non-English boards aren't left wondering why nothing
  turns done.
- Cards in a done list don't move anywhere and aren't hidden -- the done
  state only changes styling and overdue counting.
