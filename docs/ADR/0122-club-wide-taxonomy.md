# One club-wide taxonomy (categories and tags), shared by notes and the knowledge base

**Context:** issue #286 (notes) asks for notes that "can be categorised
and/or tagged with my taxonomy", and says notes "shall become part of
the knowledge base according to #285". #285 wants to browse the
knowledge base (laws, links, blog posts, decisions from notes, cloud
documents, ...) "by taxonomy (category or tag)" and publish selections
"by different taxonomies".

Until now every module with labels had its **own** tag pool:
`MemberTag` (ADR 0093), `ExternalContactTag` (ADR 0096), `TaskTag`
(issue #259). That was right for them: "electrician" has no business in
the member filter. It's wrong here: if notes got a `NoteTag` pool, the
knowledge base would either need a second pool for its other sources
(and "Water" would exist twice, drifting apart) or a migration merging
them later.

## Decision

Two new club-wide tables, not tied to one module:

- `taxonomy_categories`: one per item (a note has at most one).
  Seeded with the four kinds the issue names: General meeting, Board
  meeting, Meeting with externals, Other, with names in all seven UI
  languages.
- `taxonomy_tags`: many per item, free-form.

Both carry `translations` like the tag pools (ADR 0098) and reuse
`app/tag_translations.py`, so typing "Vorstandssitzung" in a German
club finds "Board meeting", and the UI shows each term in the club
language. Notes link to them with `notes.category_id` (FK, `SET NULL`)
and `note_tag_links`. The knowledge base (#285) adds its own link
tables to the same two tables.

Management lives at `/notes/taxonomy` for now, guarded by the `notes`
module permission (write to add/rename/translate, delete to delete),
because notes are its only user so far. When #285 lands, the page
moves to a neutral place (and its own permission) without a data
change.

## Rejected

- **A `NoteTag` pool like the others** -- see context; a guaranteed
  merge later.
- **Hierarchical categories** (a tree): nothing in #285/#286 asks for
  it, and a flat list plus tags covers "General meeting 2026, budget".
  A `parent_id` can be added later without breaking anything.
- **Folding the existing member/contact/task pools into this one**:
  they're deliberately separate (ADR 0093/0096) and have nothing to do
  with knowledge.

## Consequences

- Renaming or deleting a term changes the content of every note file
  that names it (ADR 0123): those notes are marked `cloud_dirty` and
  rewritten on the next sync.
- A cloud file may name a category or tag nobody created yet; the sync
  creates it rather than dropping the information.
