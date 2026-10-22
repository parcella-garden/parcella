# Automated Tests

## Philosophy

**No claim to 100% test coverage.** For a project of this size, that
would be its own bottomless pit. Instead:

1. **One "happy path" test per module** -- the basic functionality works
   (create, retrieve, link).
2. **Targeted tests for the spots with the highest regression risk** --
   that is, exactly the logic that has already caused headaches, or where
   a silent bug would be especially bad:
   - Two-person approval principle for purchase requests (self-approval
     lock, double-approval lock, veto rejection)
   - Meter-reading monotonicity check (must not decrease)
   - Work-hours group exemption (`any()` instead of `all()` for parcels)
   - Insurance cost calculation (base + additional amounts)

## Why real PostgreSQL, not SQLite

Several bugs in this project occurred **exclusively with PostgreSQL**
(e.g. the enum-casing issue, see
[Architecture Decisions](./ADR/0002-enum-values-always-uppercase.md)). A test run
against SQLite would have made such bugs invisible instead of catching
them -- SQLite is more lenient than PostgreSQL in many respects (type
system, enum handling, constraint enforcement). Tests therefore run
against a real, but entirely disposable, PostgreSQL instance.

## Running the tests

```bash
./run_tests.sh
```

The script wraps the whole process: starts an isolated test database
(`tmpfs`, disappears on stop), installs test dependencies, runs `pytest`,
and cleans up afterward -- even if tests fail.

The test database only runs with `docker compose --profile test`, so it
never shows up with a normal `docker compose up` and never interferes
with the running instance.

## Automatically on every push

`.github/workflows/tests.yml` runs the same test suite on every push and
pull request on GitHub (its own isolated PostgreSQL instance as a GitHub
Actions service, no Docker Compose needed on the CI side). A failed test
is visible directly in the pull request, before anything is merged into
`main`.

## How the test database works

`tests/conftest.py` sets `DATABASE_URL` to the test database **before**
any part of the app is imported. This matters: Python caches module
imports, and `app/database.py` creates the database connection on first
import from `settings.database_url` -- if the app had already been
imported once with the production URL, internal mechanisms too (the
module-flags middleware, the admin-creation logic at startup) would use
the wrong database. Because we set the environment variable right at the
top of `conftest.py`, this works correctly automatically, without having
to override every single spot in the code ourselves.

Before every individual test, all tables are emptied (not: nested
transactions with rollback). This is deliberately the simpler solution:
the application itself commits in many places along the way (e.g. after
every purchase-request approval) -- that would conflict with pure test
transactions that get rolled back at the end. Emptying tables is less
elegant, but robust and easy to reason about.

## Lessons from the first real test run

Two problems came up the very first time the tests ran -- both fixed, but
documented so they don't recur:

**Test email addresses must not use reserved special-use domains.**
`admin@test.local` was rejected by Pydantic's `EmailStr` validation,
because `.local` is on the list of reserved special-use names
(`localhost`, `local`, `test`, `example`, `invalid`, `onion`) that the
underlying `email-validator` library rejects as a TLD. Test addresses
have used `@example.com` ever since -- that's a perfectly normal `.com`
domain (only the second part happens to be called "example"), not a
special-use TLD, and by default Pydantic doesn't check actual
deliverability anyway (no DNS lookup).

**`pytest-asyncio` gives every test function its own event loop -- which
collides with our singleton database engine.** Our database engine
(`app.database.engine`) is a singleton that establishes connections once
on module import. If every test runs in its own loop, the engine
eventually tries to reuse a connection from an already-closed loop --
which shows up as `RuntimeError: ... attached to a different loop`.

Two attempted fixes via a custom `event_loop` fixture override failed due
to pytest-asyncio version issues: version 0.24 ignores such an override
for test functions themselves (only fixtures respect it); downgrading to
0.21.1, in turn, is incompatible with `pytest` 8.x
(`AttributeError: 'FixtureDef' object has no attribute 'unittest'`).

**The robust, version-independent solution:** instead of fighting
pytest-asyncio's internal loop behavior, the engine's connection pool is
discarded before **every single test** (`await engine.dispose()`, as an
autouse fixture `_frische_verbindung`). New connections then automatically
arise in whichever loop is currently active the next time they're needed
-- regardless of which pytest-asyncio version or loop-scope configuration
happens to be in effect. This fixture must run before the table-emptying
fixture; that's enforced via an explicit fixture dependency
(`_tabellen_leeren(_frische_verbindung)`), rather than relying on
definition order.

**Lesson:** with stubborn event-loop issues in async database libraries,
it's often more worthwhile to explicitly reset the resource (here: the
connection pool) than to try to exactly replicate the test framework's
behavior -- the latter tends to change between versions, the former
doesn't.

## SQLAlchemy identity map: stale relationships despite a fresh query

**`_zu_kosten_schema()` kept showing 0 EUR in property-insurance costs**,
even though the first `MissingGreenlet` fix was already in place. Cause:
the relationship `pv.sach_paket` had already been loaded once (with the
value `None`) **before** `sach_paket_id` was even set (namely, when the
row was newly created earlier in the function). SQLAlchemy's **identity
map** ensures that the same Python object is reused within the same
session for the same primary key -- re-querying with
`selectinload(sach_paket)` does NOT automatically overwrite a relationship
already **marked as loaded**, even after a `commit()`, as long as
`expire_on_commit=False` is set (which we deliberately configured to
avoid other greenlet issues).

**Fix:** `await db.refresh(pv, attribute_names=["sach_paket",
"zusatzpersonen"])` instead of a fresh `select(...)` -- `refresh()`
specifically forces exactly the given relationships to be reloaded from
the database, regardless of the object's previous (possibly stale)
loaded state.

**Context:** this is a third, distinct variant of the "freshly created
object + missing relationship reload" family of problems that we've
already run into several times in this project (ticket system, insurance
creation) -- this time not as a completely missing reload, but as a
reload that was rendered ineffective by the identity map. Whenever the
pattern "object X, then set field Y, then read relationship Z" occurs,
it's worth asking: was Z already loaded BEFORE Y was set?

## Further test runs: found a serious business-logic bug

**The "any() instead of all()" rule was implemented backwards in two out
of three places.** The web evaluation page in `pflichtstunden.py` had
implemented the rule correctly (`any(p["befreit"] for p in
paechter_details)`), but both the **CSV export** (also in
`pflichtstunden.py`) and the **REST API** (`api_pflichtstunden.py`)
accidentally implemented it as `all()` when rebuilding it: a variable
named `alle_befreit` was initialized with `True` and set to `False` for
every non-exempt tenant -- that's "ALL must be exempt", not "AT LEAST
ONE". The misleading variable name was likely the cause: it was
apparently copied without also copying the actual `any()` logic.

**This is not a cosmetic bug.** For parcels with one exempt and one
non-exempt tenant, the CSV export (which is used for the actual billing!)
would have shown an amount owed where none was actually due. Finding
exactly this kind of error automatically, before it shows up in a real
billing run, is the whole reason we started writing tests in the first
place.

**Fixed in both places**, and the consistently correct variable in the web
evaluation page was renamed from `alle_befreit` to `ist_befreit` -- the
old name practically invited being misunderstood again the next time it
was copied.

**Additionally:** a Pydantic validation error in `api_versicherungen.py`'s
`_zu_kosten_schema()` -- `model_validate(pv)` was called directly on the
target schema with the *calculated* cost fields, which aren't real ORM
columns. Pydantic therefore demanded these fields already during
validation, rather than only when they were set afterward. Fixed by first
validating the base schema (only real columns), and only adding the
calculated fields when constructing the complete target schema.

## First real test runs: found two app bugs (not just test infrastructure)

Once the event-loop infrastructure was in place, the first tests that
actually ran uncovered two real, previously unnoticed problems:

**`PflichtstundenModus` is lowercase, every other enum is uppercase.**
This enum dates back to phase 1 (migration `0002_pflichtstunden`), before
the "enum values always uppercase" convention was introduced (see
Architecture Decisions). It wasn't caught up during that conversion. This
isn't a bug in the sense of "behaves incorrectly" -- the code is
internally consistent (model and migration both use
`pro_pachtvertrag`) -- but it's a **trap for anyone who uses enum values
in the future and expects uppercase**, since it's the only outlier in the
entire project. Deliberately NOT retroactively unified (that would be
another migration purely for consistency, with no functional benefit) --
instead documented here so nobody stumbles over it again. Tests were
adjusted accordingly (`modus="pro_pachtvertrag"`, lowercase).

**`MissingGreenlet` in the insurance module too, not just the ticket
system.** `api_versicherungen.py`'s `versicherung_setzen()` created a new
`ParzelleVersicherung` row when needed, but immediately accessed
`pv.zusatzpersonen` right after, without reloading the row with
`selectinload` -- exactly the same pattern we had already found and fixed
in the ticket system (see Architecture Decisions). It simply hadn't been
applied consistently to every spot in the code where "create new, then
immediately read a relationship" happens. Fixed following the same
pattern: explicitly reload after creating.

**Lesson:** automated tests catch exactly this kind of "we actually
already know this, but didn't apply it everywhere" error -- that's the
real value of the test suite, not just preventing new bugs, but uncovering
existing, unnoticed ones.

## Known limits (deliberately not automated)

- **SMTP sending** (`app/email_service.py`): requires a real mail
  server, so it's tested manually. Mocking it would be possible, but was
  judged not worth it for the project's current scope -- the
  failure-proneness lies more in real network/configuration issues than
  in the app's own logic.
- **Email sending in general** (invitations, assignment notifications):
  `sende_email()` simply fails in the test environment for lack of SMTP
  configuration (returns `False`) -- that's intended, already-handled
  behavior in the code, not a test failure.

## The test client carries a CSRF token for you

Since [ADR 0064](./ADR/0064-csrf-and-security-response-headers.md) every
state-changing request from the web UI needs a CSRF token. The `client`
fixture is a `CsrfAwareClient` (`tests/conftest.py`) that holds the
cookie and mirrors the token back on every POST/PUT/PATCH/DELETE, the
same way a browser submitting a rendered form does -- so existing tests
didn't have to change and new ones don't have to think about it.

Two things worth knowing:

- A test that builds its **own** `AsyncClient` (a few do, to act as a
  second, differently-permissioned user) must use `CsrfAwareClient` too,
  or its POSTs get a 403 that looks exactly like a failed permission
  check. `tests/test_calendar.py` has an example.
- To test what happens **without** a token, use the `raw_client`
  fixture, which does none of this. That's what
  `tests/test_security.py` uses for the forgery cases.

`tests/test_security.py` also walks every template and fails if a
`method="post"` form is missing `{{ csrf_field() }}` -- so a forgotten
token shows up as a red test, not as a 403 in production.

## New module? Don't forget new tests

When building a new module (see also the checklist in
[docs/README.md](./README.md)), a `tests/test_<module>.py` file with at
least one happy-path test is now part of the deal from now on -- just
like docs and API endpoints have become a given by now.
