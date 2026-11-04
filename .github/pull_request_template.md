## What and why

<!-- What changes, and why. Link the issue: "Fixes #123" closes it on merge. -->

Fixes #

## How to check it

<!-- Where to click in the dev environment to see the change working. -->

## Checklist

- [ ] Tests green (`./run_tests.sh` locally, and CI on this PR)
- [ ] New/changed model -> hand-reviewed Alembic migration (revision ID <= 32 chars)
- [ ] New user-facing strings in all 7 `app/translations/*.json` files
- [ ] Docs updated (`docs/module-*.md`, a new ADR if the decision is architectural)
- [ ] Security-relevant (routes, forms, permissions, headers, user-rendered data)? `/security-review` run, findings fixed or accepted below
