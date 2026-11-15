# Release policy

How Parcella decides what goes into which release, and when releases go
out. The why is in [ADR 0135](./ADR/0135-release-trains-and-semver-triage.md).
The release *mechanics* (bump PR, tag, `release.yml`, GitHub release) are in
[CLAUDE.md](../CLAUDE.md#releases).

## 1. Every change gets a release level when it's planned

When an issue moves to **Ready** on the
[project board](https://github.com/orgs/parcella-garden/projects/5), it gets
its level in the board's **Release** field (and the matching label on the
issue and its PR):

| Level | Label | What qualifies |
|---|---|---|
| **Patch** | `release: patch` | A bug fix. No new behaviour, no new or changed setting, no API change, **no database migration**. |
| **Minor** | `release: minor` | New functionality that doesn't break anything existing. Additive migrations (new tables/columns with defaults) are fine. |
| **Major** | `release: major` | Anything that breaks existing behaviour, settings, stored files, the REST API or the website plugin protocol, or needs manual work when updating. |

When in doubt, pick the higher level. A security fix is a **patch** if it
can be done without breaking anything; otherwise see the exceptions below.

## 2. Release trains

| Release | When | What it contains |
|---|---|---|
| **Patch** (x.y.**Z**) | every two weeks, **only if there's something to ship** | merged `release: patch` work |
| **Minor** (x.**Y**.0) | once a month | everything merged since the last minor |
| **Major** (**X**.0.0) | once a year, in the **winter** (after the gardening season, before the annual invoices in January) | the breaking changes collected over the year |

A release train with nothing on it doesn't run: no empty releases.

## 3. Merge windows (how patches stay patches)

Features and fixes both land on `main`. To keep `main` releasable as a patch
between minors:

- **Patch PRs** are merged as soon as they're green and smoke-tested.
- **Minor PRs** stay open (green, smoke-tested, approved) until the
  **merge window** in the days before the monthly minor release, then
  they're merged together and the minor goes out.
- **Major PRs** wait for the yearly window the same way. Where possible, a
  breaking change is split: the new behaviour ships in a minor *next to* the
  old one (with a notice that the old one is going away), and the old one is
  removed in the next major.

If a patch is due while minor work is already on `main` (e.g. after an
exception), release it as a minor instead of reverting anything.

## 4. Exceptions

- **Security fixes ship immediately**, as their own patch release, outside
  the schedule. If the fix has to break something, it ships anyway, as a
  major if strict semver requires it, with the reason in the release notes.
- **kermie can pull anything forward** (e.g. while Parcella has a single
  production user). The release notes say so.

Strict semantic versioning applies either way: the version number always
matches what actually shipped, not the train it was planned for.

## 5. In the release notes

Every release lists its changes under *Breaking* / *New* / *Changed* /
*Fixed* / *Security*, plus migrations and anything to do before updating.
Patch notes should be short enough to read in a minute.
