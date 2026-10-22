# CMS plugins: GPL-licensed, one shared PHP core, copied per plugin

**Context:** ADR 0105 defined the Parcella Website Plugin Protocol and
left two things open: writing the CMS-side plugins (Drupal, TYPO3,
Contao, Joomla), and the license question before marketplace uploads.
drupal.org only hosts GPL-2.0-or-later code; WordPress.org, Joomla's JED
and the TYPO3 TER expect GPL-compatible extensions. Parcella and the
WordPress plugin were AGPL-3.0-or-later. kermie decided: GPL for the
plugins.

## Decision

1. **Everything in `integrations/` is GPL-2.0-or-later**, each plugin
   with its own license file; Parcella itself stays AGPL-3.0-or-later.
   The plugins only talk to Parcella over HTTP, so they're separate works
   and the license split is clean. The WordPress plugin moved from AGPL
   to GPL in 3.1.1 (kermie is its only author, so the relicensing needed
   no one else's consent). CONTRIBUTING.md says contributions to
   `integrations/` are GPL.

2. **One shared PHP core, copied into each plugin.** The security-relevant
   part (HMAC check in constant time, ±5 minute window, routing, draft
   validation, image checks) lives once in
   `integrations/shared-php/ParcellaProtocol.php`. Marketplaces don't
   allow one plugin to depend on another, so each plugin carries a copy
   with its own namespace; `sync.sh` makes the copies and
   `tests/protocol_test.php` checks the core, including against a
   signature produced by Parcella's own code. Edit the original only.

3. **Defense in depth in every plugin.** Parcella already sanitizes the
   HTML, but each plugin runs it through its CMS's own filter again
   (Drupal `Xss::filterAdmin` + text format, Joomla `InputFilter`, TYPO3
   HTML sanitizer, Contao allowed tags). Images are accepted only as PNG,
   JPEG or WebP up to 5 MB, must match their own file signature, and are
   stored under a random name -- never the sender's file name.

4. **Drafts only, as the protocol requires.** Each plugin creates
   unpublished content (Drupal unpublished node, Joomla state 0 article,
   TYPO3 hidden EXT:news record, Contao unpublished news entry) and never
   changes the publish state on update. All four are idempotent on
   `source_id`.

5. **Live-tested** against real installations in temporary containers
   (Drupal 11.4, Joomla 5, TYPO3 13.4 with news 12.3, Contao 5.3). That
   found three bugs the code alone didn't show: Drupal 11.4's standard
   profile creates no content type at all (the module now refuses with a
   clear message instead of saving a node of a non-existent type);
   Joomla articles need a workflow association or they're invisible in
   the backend list (the plugin assigns the default stage); Contao 5
   stores checkboxes as 0/1, not `''`/`'1'`.

6. **Signup and contact forms stay out of these plugins for now.** They
   already work on any website as plain HTML forms (ADR 0088); bundling
   them into each CMS plugin (as the WordPress plugin does) is version
   1.1.

## Not done

- The marketplace uploads themselves: they need the maintainer's
  accounts. `docs/cms-plugins-publishing.md` has the steps,
  `integrations/package.py` builds the files.
- Edit links back into the TYPO3 and Contao backends: they can't be
  built reliably from a frontend request (TYPO3) or need a request token
  (Contao). Parcella shows the record number instead.
