# CLAUDE.md

Guidance for Claude Code (or any AI coding agent) working in this repository. This file is a map to the *other* docs and a list of sharp edges specific to this codebase -- it doesn't replace [README.md](./README.md),[CONTRIBUTING.md](./CONTRIBUTING.md), or `docs/`. Read this first, then go to the linked doc for depth.

## What this project is

Parcella: an open-source web app for allotment garden associations
("Kleingartenverein" / "Schrebergarten"). Members, parcels/leases, work hours, metering, insurance, tickets, purchase requests, finances/invoicing, and more, each as an independently toggleable module. AGPL-3.0-licensed, public repo - see [CONTRIBUTING.md](./CONTRIBUTING.md) for the license implications before assuming anything here is private.

Stack: Python 3.12 + FastAPI, Jinja2 (server-rendered, Bootstrap 5), PostgreSQL 16 + SQLAlchemy (async) + Alembic, Docker Compose. Full table in [README.md](./README.md#tech-stack).

## Before touching anything: got to plan mode and find the relevant doc

- call me by my name when asking me something
- offer to go to /plan mode first
- **`docs/ADR/README.md`** - 40+ numbered Architecture Decision Records, "why things are built the way they are." Check here before assuming a design is accidental or before reverting something that looks odd - it's very likely a deliberate call with a documented reason.
- **`docs/module-*.md`** -- one file per module (data model, key
  decisions, known gaps). If you're working in a module, read its doc first; if the module has no doc yet, that's a gap worth closing (see "Documentation expectations" below).
- **`docs/testing.md`**, **`docs/operations.md`**, **`docs/i18n-l10n.md`**,
  **`docs/responsive-design.md`** -- cross-cutting topics, not tied to one
  module.
- **`docs/README.md`** -- the index, and the numbered checklist for
  building a new module (models -> migration -> router -> module flag ->
  admin toggle -> nav entry -> dashboard stat -> translations -> tests ->
  docs -> ADR if it's architecturally significant).

## Dev loop

```bash
docker compose build web
docker compose run --rm --entrypoint alembic web upgrade head
docker compose up -d db web          # app at http://localhost:8000
./run_tests.sh                       # full suite against real Postgres
```

`run_tests.sh` starts a disposable `db_test` container (`--profile test`,
tmpfs, never touches the real `db` volume), installs test deps, runs
pytest, and tears the test DB down again -- even on failure. It does
**not** touch the regular `db`/`web` containers' running state, but it
does run its own `docker compose` invocations under the same project
name, so expect `db`/`web` to need a `docker compose up -d db web`
afterward if you were also using them for manual testing.

Default admin login after first startup: `admin@parcella.local` /
`admin1234` -- change it immediately on anything beyond a throwaway local
instance.

If a Github issue is declared as a bug, write a test for it so it never appears again.

Always trigger a database backup before changing anything.

You never ever expose your user name to Github. Use my handle instead!

## Architectural conventions (the load-bearing ones)

- **Module flags** (`app/module_flags.py`): every optional feature area is
  a `ClubSetting` row `modul_<name>` (boolean-ish string), defaulted in
  `MODULE_DEFAULTS`, loaded once per request into
  `request.state.module_flags`. Guard new routers with
  `dependencies=[Depends(require_module("<name>"))]`. New modules default
  `True` *unless* they open a public/unauthenticated endpoint, in which
  case default `False` (see the public signup API, ADR 0024).
- **Permission matrix** (`app/permissions.py`): ADMIN/BOARD bypass
  everything and get full access; everyone else starts from a narrow
  baseline (read-only on members/parcels) that a `Group` can widen. The
  admin panel itself is a separate, narrower `require_system_admin` check.
  The REST API (`app/api_auth.py`) is a wholly separate JWT-based role
  system -- don't assume the two are in sync.
- **`ClubSetting`** is a flexible key/value table for club master data
  (`app/models.py`) -- reach for a new key here before adding a new
  dedicated column/table for a single scalar setting.
- **Router factory pattern**: structurally identical modules (e.g. water
  vs. electricity metering) share one router factory rather than two
  near-duplicate files -- see ADR 0003 before copy-pasting a whole router.
- **Historization over deletion**: ending something (a tenancy, a role
  assignment) sets an end date/status rather than deleting the row -- see
  ADR 0005. Don't introduce a hard delete where the rest of the codebase
  historizes.
- **i18n**: English is the base/authoring language (ADR 0020); every
  user-facing string needs a key in **all 7** `app/translations/*.json`
  files (`en`, `de`, `pl`, `cs`, `sk`, `fr`, `nl`), not just English. Grep
  for a key before bulk-editing translation files -- a blind
  `dict.update()` has silently overwritten an existing field's labels
  before. See [docs/i18n-l10n.md](./docs/i18n-l10n.md).
- **l10n** (region/currency) is a setting independent of language (ADR
  0014) -- don't assume language implies number/currency format.
- **Every `method="post"` form needs `{{ csrf_field() }}`** (ADR 0064).
  The check is a middleware, so a missing token is a 403 at runtime --
  and a failing test in `tests/test_security.py`, which walks all
  templates. `fetch()`-based POSTs send the `X-CSRF-Token` header from
  the `<meta name="csrf-token">` tag instead. `/api/**` is exempt (it
  authenticates by bearer token, not by cookie).
- **Never render user-controlled data with `|safe`.** The one place that
  did (a member's address, joined with `<br>`) was a stored XSS: Jinja's
  `join` returns a plain `str` for plain-str items, so `|safe` marked
  the raw input as trusted. Build markup in Python with `Markup`/
  `escape` instead -- see `address_html` in `app/l10n.py`.

## Sharp edges (things that have already caused real bugs)

- **Enum values: always uppercase, and SQLAlchemy's `Enum` column stores
  the member *name*, not `.value`, by default (no `values_callable`
  override is set anywhere in `app/models.py`).** Every `enum.Enum` there
  uses uppercase Python member names (`FIXED_PER_PARCEL =
  "fixed_per_parcel"`). When you add a new value to an *existing*
  Postgres enum type via a raw `ALTER TYPE ... ADD VALUE` migration, the
  string you add must match the member **name** (uppercase), not the
  lowercase `.value`. Getting this backwards produces a 500 (`invalid
  input value for enum ...`) on the very first insert, and Postgres has
  no `ALTER TYPE ... DROP VALUE` to clean up a wrong entry afterward (hit
  and fixed for real in migrations 0052/0053; `autocommit_block()` is
  required since `ADD VALUE` can't run inside a transaction, same
  pattern as migration 0030). **Note:** ADR 0002 documents the original
  "always uppercase" convention but describes the mechanism backwards
  (it says SQLAlchemy sends the *value*, not the name) -- the convention
  it prescribes is still correct, since making name and value identical
  sidesteps the distinction either way, but don't take its mechanism
  explanation as authoritative if you're debugging a *new* enum-casing
  issue.
- **Migration revision IDs must be ≤32 characters** -- `alembic_version`
  is a `VARCHAR(32)`. A too-long autogenerated name truncates silently at
  the DB level and breaks `alembic upgrade` with a cryptic
  `StringDataRightTruncationError`.
- **`any()`, not `all()`, for group exemptions.** Work-hours parcel
  exemption is "if at least one tenant is exempt, the whole parcel is
  exempt" -- this has been implemented backwards (as `all()`) more than
  once when the logic was copied to a new consumer (CSV export, REST
  API). If you're duplicating an exemption/eligibility check, verify
  which quantifier the original actually uses; don't infer it from a
  variable name.
- **PostgreSQL-only test DB, deliberately.** Several bugs (the enum-casing
  one above included) only reproduce against real Postgres; SQLite is
  more lenient across the board. Don't swap the test DB for SQLite for
  convenience.
- **SQLAlchemy identity map + freshly created rows.** "Create row X, set a
  field, then read a relationship on X" can return a stale/`None`
  relationship even after commit, because the identity map already marked
  it loaded before the field was set. Fix is `db.refresh(obj,
  attribute_names=[...])`, not a fresh `select()` (a fresh select doesn't
  overwrite an already-loaded relationship on the same identity-mapped
  object). See `docs/testing.md` for three separate real occurrences of
  this exact shape of bug.
- **Never put a raw email-header-derived string straight into an HTTP
  response header.** `email.message.Message.get_filename()` returns
  whatever the sender's mail client sent -- an unencoded header fold
  can leave a literal `\r\n` in the decoded filename. Putting that
  straight into a `Content-Disposition` header (ticket attachment
  downloads, `app/routers/tickets.py`) isn't just a display glitch,
  it's a header-injection shape and crashes the response outright
  (uvicorn: `RuntimeError: Invalid HTTP header value`) -- hit for real
  the first time a member's mail client folded a screenshot's filename.
  Fixed via `sanitize_attachment_filename()` in `app/ticket_mailer.py`,
  applied once at ingestion **and** again defensively where the header
  is built (same "sanitize at ingestion + defensive pass at render
  time" pattern `sanitize_email_html`/`sanitize_html` already use for
  ticket HTML content) -- don't assume that pattern only applies to
  HTML; any externally-sourced string heading for a header, path, or
  shell argument needs the same treatment, not just the field that
  happened to get sanitized first.

## Testing

`./run_tests.sh` runs the full suite against a real, disposable Postgres
instance (never SQLite -- see above). Philosophy (full detail in
[docs/testing.md](./docs/testing.md)): one happy-path test per module,
plus targeted tests at the highest-regression-risk spots (two-person
approval, meter monotonicity, work-hours exemption, insurance cost calc).
No claim to 100% coverage. New modules get a `tests/test_<module>.py` with
at least one happy-path test -- this is now expected, same as docs and API
endpoints.

## Documentation expectations

This isn't optional polish: `docs/README.md` states docs get written
*while building*, not afterward. Concretely:

- New module -> `docs/module-<name>.md` (data model, key decisions, known
  gaps).
- Cross-cutting architectural decision (new data-model shape, a rejected
  approach, anything future-you would otherwise re-derive from scratch or
  accidentally revert) -> a new numbered file in `docs/ADR/`, added to the
  index in `docs/ADR/README.md`.
- Code and commit messages are not a substitute for either of the above --
  they explain *what changed*, not *why the system is shaped this way*.

## Code conventions (see CONTRIBUTING.md for the full list)

- English first, for identifiers *and* user-facing text *and*
  comments/docstrings going forward -- a fair amount of older German
  prose remains and is translated incrementally, not required to fix in
  an unrelated change.
- Genericity: prefer configurable structures over hardcoding this
  association's specifics. (Note: `flaeche_a_qm`/`_b_qm`/`_c_qm` --
  hardcoded "Area A/B/C" club settings -- predate this guideline and
  haven't been generalized; know this is a named exception, not a
  pattern to copy for new features.)
- Every `app/models.py` change needs an Alembic migration, reviewed by
  hand (autogenerate misses renames, treating them as drop+create).
- New/changed models get matching Pydantic schemas in `app/schemas.py`
  for REST API availability (API-first, ADR 0012).

## When you're not sure

Prefer grep-ing `docs/ADR/` and the relevant `docs/module-*.md` over
guessing from the code alone -- a schema shape or a seemingly-redundant
check is more often a deliberate fix for a specific past bug than dead
weight.
