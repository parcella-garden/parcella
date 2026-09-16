# Documentation

This documentation accompanies the development of the Gartenmanager
association-management software and is extended continuously with every
new feature -- not added afterwards at the end, but written while the
decisions and reasoning are still fresh.

## Modules

- [Members & Parcels](./module-members-parcels.md) -- core module, always active
- [Work Hours](./module-work-hours.md) -- work sessions, sponsorships, club roles
- [Metering (Water & Electricity)](./module-metering.md) -- shared codebase for both media
- [Insurance](./module-insurance.md) -- property and accident insurance per parcel
- [FreeScout Bridge](./module-freescout-bridge.md) -- links FreeScout support conversations to members, parcels, and the task board
- [Purchase Requests](./module-purchase-requests.md) -- two-person approval principle for club expenses
- [Calendar](./module-calendar.md) -- community calendar, birthdays, council presence/absence, ICS export
- [Public Signup API](./module-public-api.md) -- CMS-agnostic public API for external site connectors (WordPress plugin included)
- [Finances](./module-finances.md) -- annual invoicing, payments, dunning reminders, bookkeeping categories

## Cross-cutting topics

- [Architecture Decisions](./ADR/README.md) -- why certain things are built the way they are
- [Operations](./operations.md) -- Docker, migrations, SMTP setup, troubleshooting
- [Security](./security.md) -- what protects the app, what a review fixed, what's still open
- [Automated Tests](./testing.md) -- testing philosophy, execution, known limits
- [i18n & l10n](./i18n-l10n.md) -- languages, region/currency, how to add a new one
- [Responsive Design](./responsive-design.md) -- mobile layout patterns for new templates

## For new modules

The following pattern has proven itself when building a new module (see
Architecture Decisions for details):

1. Models in `app/models.py`, enum values **always uppercase** (see the
   lesson learned from several bugs around this)
2. Migration in `migrations/versions/`, revision name under 32 characters
3. Router with `dependencies=[Depends(require_module("<name>"))]` -- both
   the web UI and the REST API from the start (API-first rule)
4. Entry in `app/module_flags.py` (`MODULE_DEFAULTS`) -- default `True`
   unless the module opens a new public/unauthenticated attack surface
   (e.g. a public write endpoint), in which case default `False` and
   require an explicit opt-in (see the public signup API for why)
5. Entry in `app/routers/admin.py` (`MODULE_FIELDS`) for the enable/disable UI
6. Navigation block in `app/templates/base.html` as a collapsible `nav-group`
7. If the module has something worth a headline number (open items, a
   count needing attention), a dashboard stat card in `app/main.py` +
   `app/templates/dashboard.html` -- gated on the module flag, matching
   the list page's own default filter exactly (see
   [Architecture Decisions](./ADR/0019-dashboard-stat-cards-the-pattern-new-modules-should-follow.md) for the pattern
   and a real bug that came from not doing this)
8. Translation keys in **all 7** `app/translations/*.json` files (de, en,
   pl, cs, sk, fr, nl) -- not just German -- see
   [i18n & l10n](./i18n-l10n.md). Any money value uses the `money` filter,
   any multi-column table gets a `.table-responsive` wrapper (see
   [Responsive Design](./responsive-design.md))
9. `tests/test_<module>.py` with at least one happy-path test
10. Write a new page here in `docs/` while the decisions are still fresh
11. If the module involved a cross-cutting architectural decision (not
    just domain logic for that module), add it as a new numbered file
    in [`docs/ADR/`](./ADR/README.md) rather than folding it into the
    module page -- one file per decision, listed in the ADR index
