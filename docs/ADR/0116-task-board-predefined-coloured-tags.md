# Task board: predefined, coloured tags

**Context:** Issue #259. Task tags were free text per card (issue #107,
ADR-less, documented in docs/module-tasks.md): a Postgres text array,
typed as a comma-separated input. kermie asked for predefined tags in
different colours, no other tags on cards, managed only by board
members. Free text had drifted the way free text does ("Garten",
"garten", "Garten "), and there was nowhere to hang a colour.

**Decision:**

- **A `TaskTag` table plus a `task_tag_links` join table**, replacing
  `tasks.tags`. Cards reference tags, so a rename or recolour shows on
  every card at once. Shaped like `MemberTag` (ADR 0093) but a separate
  pool: task tags and member tags mean different things to different
  audiences. No per-language names (ADR 0098) -- not asked for; can be
  added later the same way.
- **Colour from a fixed palette** of eight keys (`TASK_TAG_COLORS`),
  light background/dark text, so every combination stays readable.
  A free colour picker was rejected (kermie's call): contrast would be
  the user's problem. Stored as a plain string checked in code, not a
  Postgres enum, so adding a colour needs no `ALTER TYPE` (see CLAUDE.md
  on enum migrations).
- **Predefined only, everywhere:** the card form offers a checkbox per
  tag; the web form and the API reject unknown tags with a 400. The API
  keeps taking and returning tag *names* (matched ignoring case), so
  responses keep their shape -- but a request that used to create a
  free-text tag now fails. kermie chose this over auto-creating unknown
  names in the API, accepting a **breaking API change and a MAJOR
  version** (6.0.0).
- **Who manages tags:** admin and board, through `require_admin` /
  `require_admin_api` -- the same people who can see the task board at
  all (ADR 0034), so no new permission. kermie confirmed this over the
  stricter system-admin check.
- **Names are unique ignoring case**, so "Garten" and "garten" can't
  coexist again.
- **Migration 0115** keeps existing data: each distinct tag becomes a
  grey `TaskTag` (case/space variants merged, alphabetically first
  spelling wins, cut to 100 characters), linked to its cards; then the
  array column is dropped. Downgrade restores the array, without colours.
- **Change history** keeps a `tags` field, now written by
  `set_task_tags()` as the sorted tag names (`ChangeTracker` can't diff a
  relationship). Old rows keep the array's text form.

**Consequences:**

- API clients sending tag names that don't exist get a 400 and must
  create the tags first (`POST /api/v1/tasks/tags`).
- Deleting a tag removes it from every card without a per-card history
  row, like a list delete's bulk reassignment (ADR 0085).
- The board's tag filter uses tag ids, since a predefined name may
  contain a comma.
