# Release trains, and a release level for every change up front

**Context:** until v7.0.0 (2026-11-15), releases were cut whenever kermie
asked, and the version level was decided at release time by looking back
at what had been merged. That worked with one production user, but other
clubs are expected to self-host Parcella. They need to know when updates
come and how risky each one is, and garden clubs have a season: breaking
changes in May hurt more than in December. kermie asked to (1) sort every
issue/PR into patch, minor or major up front and (2) release on a schedule:
majors yearly, minors monthly, patches every two weeks.

## Decision

- **Triage, not hindsight:** the level is set when an issue moves to Ready
  (board field "Release", labels `release: patch|minor|major`). Patch means
  no new behaviour and **no migration**; minor means additive; major means
  something breaks or needs manual work on update. Details in
  docs/release-policy.md.
- **Release trains:** patch every two weeks (only if there's something),
  minor monthly, major yearly in the winter: after the season, before the
  January invoices, so there's time for follow-up fixes.
- **Merge windows instead of release branches:** feature PRs wait (green and
  smoke-tested) until shortly before the monthly minor; patch PRs merge right
  away. That keeps `main` shippable as a patch between minors without the
  cost of cherry-picking every fix onto a `release/x.y` branch, which isn't
  worth it at this project's size.
- **Breaking changes get a transition** where feasible: the new behaviour
  ships in a minor next to the old, the old is removed in the yearly major.
- **Exceptions:** security fixes ship immediately as their own release; kermie
  can pull anything forward. The version number always follows strict semver
  for what actually shipped.

## Rejected

- **Release branches** (`release/7.1`, fixes cherry-picked): cleaner
  separation, but double work on every fix for a project with one maintainer
  and one AI agent. Can be added later if merge windows get in the way.
- **Purely time-based levels** (whatever is ready at the monthly date ships
  as a minor): it would bury breaking changes in minors, which is exactly
  what the version number is meant to warn about.

## Consequences

- A finished feature can wait up to a month before it's on `main`. Longer-lived
  PR branches need a merge of `main` before their window.
- No migrations in patches means a patch update never needs a database backup
  to be safe (a backup is still recommended).
- #311-style changes (a breaking change to a stored file format) need either a
  transition period or an explicit exception from kermie.
