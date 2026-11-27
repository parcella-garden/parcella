# 0146: Models are a package by domain, re-exported from `app.models`

**Status:** accepted (issue #416, slice 1, kermie, 2026-11-27)

## Context

`app/models.py` had grown to 4,122 lines: 90 models, 29 enums and four
link tables of every module in one file. Finding a model, reviewing a
change to it and keeping parallel PRs from colliding all got harder.

## Decision

- `app/models/` is a package with one module per domain (`members.py`,
  `parcels.py`, `finances.py`, `tasks.py`, …; `calendars.py` rather than
  `calendar.py` next to the standard library's name). `_common.py` holds
  `new_uuid`.
- **`app/models/__init__.py` re-exports every name explicitly.** The rest
  of the app keeps importing `from app.models import X`; nothing imports
  from a domain module directly. Alembic's `migrations/env.py` still
  imports `app.models`, which loads every module, so the metadata is
  complete.
- **No imports between domain modules.** A model only refers directly to
  its own enums and constants; links to other domains are strings
  (`relationship("Member")`, `ForeignKey("members.id")`,
  `secondary="member_tag_links"`), resolved when the mappers are
  configured, after `__init__` has loaded every module. That keeps the
  package free of import cycles. If a model ever needs another domain's
  enum at class-definition time, import it from that module (never from
  `app.models` inside the package).
- The split was mechanical: every definition is unchanged (checked by
  comparing the AST of each class with the old file), table and enum
  names come from `__tablename__` and the class names and didn't move,
  and `alembic check` reports the same result before and after.

## Consequences

- A new model goes into its domain's module (or a new one) **and** into
  `__init__.py`; a model missing there is invisible to the app.
- Further slices of #416 (service layer out of the big routers, the
  remaining German identifiers) are separate changes.
