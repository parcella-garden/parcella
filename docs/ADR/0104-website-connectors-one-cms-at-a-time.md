# Website connectors: one dropdown, one CMS at a time

**Context:** The announcements module's blog channel was built for
WordPress only (`app/blog_publisher.py`, three `wordpress_*` settings, a
WordPress card on Admin -> Integrations, "WordPress" wording on the
announcement page). kermie's club then replaced its WordPress site with
a static site that a home-grown generator rebuilds from a Nextcloud
folder every ~30 minutes (ADR 0088 covers the forms side of that move).
Its posts are Markdown files with a YAML header, and a post stays hidden
while it has `draft: true`. Parcella is meant to be a product for any
club, so swapping one hard-wired CMS for another wouldn't have solved
the problem: other clubs run TYPO3, Contao, Drupal, Joomla or WordPress.

## Decision

1. **A connector setting, not one module per CMS.** Modules
   (`modul_*`, ADR 0001) are whole feature areas with a nav entry,
   permissions and a dashboard card. A CMS is a backend choice for one
   channel of one module, the same way Nextcloud is one backend behind
   cloud storage. Admin -> Integrations has one "Website" card with a
   dropdown (None, WordPress, Markdown folder, Parcella plugin). Below
   it, the page shows only the chosen CMS's fields.

2. **One CMS at a time** (kermie's call). The ClubSetting
   `website_connector` holds the active type. Choosing another type
   switches the previous one off but keeps its stored settings
   (`website_<type>_<field>`), so switching back needs no retyping.
   Because only one connector is ever active, the one-BLOG-delivery-per-
   announcement data model stays unchanged, and the print QR code always
   has one unambiguous post to point at.

3. **One interface, a registry, generic UI.** `app/website_connectors/` (the registry itself was later shared with cloud storage as `app/provider_registry.py`, ADR 0106):
   `WebsiteConnector` in `base.py` (`test_connection`, `publish_draft`,
   `update_post`, `get_public_url_if_published`, plus `config_fields`
   metadata), `registry.py` mapping type to class and handling storage,
   validation and encryption of the fields. The admin card, the
   "Test connection" button and the REST API are all rendered from
   `config_fields`. Adding a CMS = one class + one registry entry +
   translations.

4. **Drafts only, everywhere.** No connector may publish, and
   `update_post` must never change a post's publish state. Publishing
   stays a human decision in the CMS.

5. **The Markdown folder connector writes through `CloudStorageProvider`**,
   not Nextcloud directly, so it keeps working if cloud storage gets
   another backend. It owns only the title, summary, image and body:
   every other header line (categories, author, date, url, and above all
   the presence or absence of `draft: true`) is kept as the human left
   it, mirroring how the WordPress connector leaves categories and the
   publish status alone. File names and slugs are ASCII-only (the site's
   own rule, and it keeps a title from injecting a path); header values
   are written as JSON string literals, which are valid YAML scalars.

6. **REST API, ADMIN only for configuration.** `api_website.py` lists the
   connector types and their fields, reads and sets the active one and
   its non-secret fields, and runs the connection test. As in
   `/api/v1/club-settings`, secrets can only be entered on the admin
   page and are never returned. Creating a draft through the API needs
   full access, like the button.

7. **Migration 0105** renames `wordpress_*` to `website_wordpress_*`
   (values untouched, so the encrypted Application Password still
   decrypts) and makes WordPress the active connector if it was fully
   configured, so nothing changes for a club that uses it.

## Rejected

- **One `modul_<cms>` flag per CMS:** nothing would stop two being on at
  once, and the announcement button would need a rule for which one wins.
- **A table of several website targets per club** (several drafts per
  announcement): more flexible, but it changes the delivery model and
  the QR-code rule for a need no club has stated. If it comes up, a
  targets table can replace the single `website_connector` setting
  without touching the connectors themselves.
- **Writing a Parcella-side client per CMS (TYPO3, Contao, ...):** see
  ADR 0105.
