# Contributing to Gartenmanager

Thanks for your interest in this project! It's intended as open-source
software for allotment garden associations -- generic enough to be useful
beyond the association it originated from.

## License and what that means for you

This project is licensed under the **GNU Affero General Public License
v3.0 (AGPL-3.0)**. In short:

- You may freely use, modify, and redistribute the code.
- If you run a modified version **as a network service** (e.g. SaaS for
  other associations), you must make the source code of your version
  publicly available -- even without classic redistribution.
- Derivative works must likewise be licensed under AGPL-3.0 (copyleft).

By contributing (pull request), you agree that your code is licensed
under the same terms (AGPL-3.0).

## How you can contribute

1. **Issues**: found a bug or have an idea? Open an issue before starting
   larger changes -- this avoids duplicate work.
2. **Fork & branch**: create a fork, work in a feature branch
   (`git checkout -b feature/my-change`).
3. **Pull request**: briefly describe what changes and why.

## Development environment

```bash
git clone <your-fork-url>
cd parcella
cp .env.example .env
docker compose -f docker-compose.dev.yml build web
docker compose -f docker-compose.dev.yml run --rm --entrypoint alembic web upgrade head
docker compose -f docker-compose.dev.yml up -d
```

The app then runs at http://localhost:8000, API docs at
http://localhost:8000/api/docs.

## Code conventions

- **Language**: this is an open-source project meant for adoption by any
  allotment garden association, in any country -- **English is the one
  and only base/authoring language**, for code and prose alike. Technical
  identifiers (class/table/column names, function names, URLs, API
  endpoints) are in English, as always. User-facing UI text (labels,
  error messages, email content) is now also written in **English
  first**, then translated into the other supported languages (German,
  Polish, Czech, Slovak, French, Dutch) via the i18n system; see
  [i18n & l10n](./docs/i18n-l10n.md) for how that works and what a new
  module needs. Code comments and docstrings should be written in
  **English** too going forward. A fair amount of existing German-language
  comments/docstrings remain from before this policy and are being
  translated incrementally rather than in one disruptive sweep -- if
  you're touching a file for another reason, translating its comments to
  English while you're in there is welcome, but not required just to make
  an unrelated change (see
  [Architecture Decisions](./docs/ADR/0020-english-becomes-the-one-and-only-base-authoring-language.md) for the
  history of this policy and the identifier-vs-UI-text split it grew out
  of).
- **Genericity**: new fields/functions should, where sensible, not only
  fit the originating association but allotment garden associations in
  general (e.g. configurable area types instead of hard-coded A/B/C
  logic, in case other associations need different categories).
- **Migrations**: every model change in `app/models.py` needs an
  accompanying Alembic migration:
  ```bash
  docker compose -f docker-compose.dev.yml run --rm web alembic revision --autogenerate -m "Short description"
  ```
  Always review a migration manually before committing it --
  autogenerate occasionally misses things (e.g. renames are detected as
  drop+create).
- **API schemas**: new/changed models should get matching Pydantic
  schemas in `app/schemas.py`, so they're available via the REST API.
- **Tests**: new modules should come with a `tests/test_<module>.py` file
  with at least one happy-path test (see [docs/testing.md](./docs/testing.md)
  for the testing philosophy and how to run the suite).

## Releasing (maintainers)

1. Bump `app_version` in `app/config.py` to the new version number.
2. Commit that change.
3. `git tag vX.Y.Z` (must match `app_version` exactly) and `git push origin vX.Y.Z`.

Pushing the tag triggers `.github/workflows/release.yml`: it runs the full
test suite, then (only if that passes and the tag matches `app_version`)
builds and pushes `ghcr.io/parcella-garden/parcella:X.Y.Z` and `:latest`. See
[ADR 0068](./docs/ADR/0068-publish-web-image-to-ghcr-prod-compose-split.md).

## What helps us most

- Translating module UI text into English (the i18n foundation exists --
  one language per installation, switchable in admin settings -- but only
  the Tickets module's UI text is fully translated so far; every other
  module still shows German text even when English is selected; see
  `app/i18n.py` and `app/translations/`)
- Documentation for additional deployment scenarios
- Accessibility (a11y) of the templates
- Additional language translations (adding a new `app/translations/<code>.json`)

If you have questions: open an issue, we'll take a look.
