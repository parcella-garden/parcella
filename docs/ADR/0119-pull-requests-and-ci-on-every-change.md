# Pull requests and CI on every change

**Context:** From August to November 2026 every ticket went straight to
`main` as a direct push (PRs #151-#164 in July were the last ones). The
test suite only ran on GitHub when a release tag was pushed
(`release.yml`), so a broken `main` surfaced at release time at the
earliest, and there was no reviewable diff on GitHub before a change
landed. The maintainer wanted to review changes as pull requests again.

**Decision:**

- **Every change goes through a pull request**, including the
  maintainer's own and the AI agent's. Branch names follow
  `issue-<N>-<slug>` for ticket work, a short slug otherwise. The PR body
  says `Fixes #N`, so the issue closes on merge.
- **`.github/workflows/ci.yml` runs the full suite** (`./run_tests.sh`,
  real Postgres) on every pull request and every push to `main`. It's a
  reusable workflow: `release.yml` calls it as its `test` job, so a PR
  and a release are tested the same way, with no duplicated steps.
- **`main` is protected**: a PR and a green `test` check are required,
  and force-pushes and branch deletion are blocked. Admins may bypass,
  which is the escape hatch for an emergency fix while the sole
  maintainer is around.
- **Squash merge** keeps one commit per ticket on `main`, the same shape
  the history had with direct pushes.
- **The manual smoke test gates the merge, not the push.** Pushing a
  branch is harmless now, so it can happen as soon as tests and the
  security review are done. The maintainer checks the change in dev,
  then merges.

**Rejected:**
- *CI only, keep pushing to `main`.* It catches breakage, but after the
  fact, and leaves no place to review a diff before it lands.
- *Required approving reviews.* With one maintainer, GitHub won't let
  you approve your own PR, so it would force an admin bypass on every
  merge and mean nothing.

**Consequences:**
- A ticket takes a few minutes longer (one CI run, about the length of
  `./run_tests.sh`).
- Release notes can be put together from the merged PRs since the last
  tag.
- `CLAUDE.md` and `CONTRIBUTING.md` describe the flow. An agent that
  still tries `git push origin main` gets rejected by the branch
  protection.
