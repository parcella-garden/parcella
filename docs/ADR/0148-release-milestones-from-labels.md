# Release milestones derived from the release labels; a static roadmap page

**Context:** since ADR 0135 every issue has a release level (`release:
patch|minor|major`), but nothing records *which* release an issue lands in,
and nobody outside can see what's coming. kermie wanted milestones per
release and a roadmap on parcella.org, generated, not maintained by hand.

## Decision

- **Milestones are computed from the labels, never set by hand.** The label
  and the board's Release field are already two places to set the level; a
  hand-set milestone would be a third, and it would drift. A workflow
  (`release-milestones.yml`, script `.github/scripts/release_milestones.py`)
  recomputes all unreleased labelled issues on every relevant event, so a
  missed or failed run is repaired by the next one.
- **Title = version, due date = train date** (docs/release-policy.md). The
  version follows from the last release and the level, and the date from the
  train rules. The script's `selftest` checks the date rules (weekend 15ths,
  ISO week 53).
- **The highest merged level wins**: once minor work is closed, patch issues
  join the minor milestone, matching policy section 3 ("release it as a
  minor instead"). Without that rule the roadmap would show a patch release
  that is never going to happen.
- **On release, closed issues move into the milestone named after the
  release.** The plan said 7.1.1, but if 7.2.0 shipped, the history should
  say 7.2.0.
- **Issues only, not PRs:** the roadmap is about what users get, and an issue
  and its PR would otherwise count twice.
- **The roadmap on parcella.org is static, generated on deploy** (website
  repo, `tools/roadmap.py` run by `.deploy.sh`). Rejected: fetching the
  GitHub API from the visitor's browser. That would always be current, but
  it would send every visitor's IP address to GitHub, needing a new paragraph
  in all seven privacy notices and handling of GitHub's limit of 60 requests
  an hour. The roadmap mostly changes at release time, when the site is
  deployed anyway. Also rejected: a page in the user docs. kermie wants the
  roadmap as a marketing page on the website.

## Consequences

- An issue manually moved to another milestone is moved back on the next
  run. To change where an issue lands, change its label.
- The roadmap is only as fresh as the last website deploy.
