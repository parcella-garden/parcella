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
| **Patch** (x.y.**Z**) | every other **Monday** (even ISO calendar weeks), **only if there's something to ship** | merged `release: patch` work |
| **Minor** (x.**Y**.0) | on the **15th of each month** (a weekend moves it to the next Monday) | everything merged since the last minor |
| **Major** (**X**.0.0) | once a year, in the **winter** (after the gardening season, before the annual invoices in January): the **15 December** slot, when breaking changes are waiting | the breaking changes collected over the year |

A release train with nothing on it doesn't run: no empty releases. The
first minor on this schedule is **7.1.0 on 15 December 2026**.

**Reminders:** `.github/workflows/release-reminders.yml` opens a reminder
issue (label `release-reminder`, assigned to the maintainer) on the 10th
(merge window opens), on the 15th (minor due) and on patch Mondays, but
only when there are merged `release: patch` PRs since the last tag.

## 3. Merge windows (how patches stay patches)

Features and fixes both land on `main`. To keep `main` releasable as a patch
between minors:

- **Patch PRs** are merged as soon as they're green and smoke-tested.
- **Minor PRs** stay open (green, smoke-tested, approved) until the
  **merge window**, which opens on the **10th** of the month. They're
  merged between the 10th and the 15th, and the minor goes out on the
  15th.
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

## 6. Milestones and the public roadmap

Every upcoming release has a GitHub milestone, titled with its version
(`7.2.0`) and due on its train date. **Nobody sets milestones by hand:**
`.github/workflows/release-milestones.yml` derives them from the
`release: *` labels whenever an issue is labelled, unlabelled, closed or
reopened, and when a release is published.

- An issue goes to the next version of its level: `release: minor` after
  7.1.0 means `7.2.0`, due on the next 15th.
- **The highest merged level wins.** Once minor work is closed and waiting,
  patch issues go to the minor's milestone too, because that is what they
  will ship in (section 3). The same goes for minor issues once a major is
  merged.
- Removing the label (or closing an issue as *not planned*) takes the issue
  out of the milestone. A milestone left empty is deleted.
- When a release is published, everything closed in a milestone up to that
  version is moved into the milestone named after the release, which is then
  closed: the history shows what really shipped where. Open issues move on
  to the next release.
- Only issues get milestones, not PRs.

**parcella.org/roadmap/** shows the open milestones: one card per release,
the minor and major issues by title, the patch issues as a count. The page
is generated by `tools/roadmap.py` in the website repo when the website is
deployed, so it's only as fresh as the last deploy (deploy after each
release). It says "Planned, not promised", and so do the milestones.

To fix things up by hand (e.g. after changing many labels), run the workflow
via **Run workflow**: it recomputes everything.
