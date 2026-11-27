# 0146: Models and the big routers are packages by domain

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

## The same shape for the big routers

The largest routers (`finances`, `admin`, `work_hours`; separate PRs
under #416) follow the same pattern:

- `app/routers/<module>/__init__.py` owns the one `APIRouter` with the
  prefix and the module guard (`require_module(...)`) and includes one
  sub-router per area (`runs.py`, `accounts.py`, `users.py`, …). The
  sub-routers have no prefix and no guard of their own, so a route can't
  end up outside the guard. `app/main.py` keeps including `<module>.router`.
- Helpers several sub-routers need that touch HTTP (404s, form parsing,
  rendering) go into `_common.py` next to them.
- Database/domain helpers without any HTTP (no `Request`, templates or
  `HTTPException`) move into `app/services/<module>.py` under public
  names, where a route or the REST API can call them.
- Overlapping paths (`/runs/new` vs `/runs/{run_id}`) keep their
  relative order; the split was checked against the old route table.
- Tests that monkeypatch a name patch it where it now lives
  (`app.routers.admin.users.send_email`).

## Consequences

- A new model goes into its domain's module (or a new one) **and** into
  `__init__.py`; a model missing there is invisible to the app.
- Further slices of #416 (service layer out of the big routers, the
  remaining German identifiers) are separate changes.
