# Website plugin protocol: one open contract instead of one client per CMS

**Context:** ADR 0104 made the website channel pluggable. WordPress has
a built-in REST API for creating drafts and a static Markdown site only
needs files, so both connectors live inside Parcella. TYPO3 and Contao
have no built-in API for creating content at all, and Drupal and Joomla
each have their own very different one. kermie wants Parcella to work
with as many CMSes as possible, and wants small CMS-side plugins that
can go into each CMS's marketplace and that third parties can extend
("enlarging the ecosystem").

## Decision

1. **Parcella defines one small, versioned HTTP contract**, the Parcella
   Website Plugin Protocol (`docs/website-plugin-protocol.md`, version
   `parcella-website/1`): `GET /ping`, `POST /drafts`,
   `PUT /drafts/{id}`, `GET /drafts/{id}`, under a base URL the plugin
   chooses. Parcella has exactly one client for it,
   `app/website_connectors/parcella_plugin.py`, selectable in the
   Website dropdown as "Parcella plugin".

2. **Each CMS gets a plugin that implements the receiving side.** The
   plugin turns the payload into a native draft (a TYPO3 news record, a
   Contao news entry, a Drupal node, a Joomla article). A new CMS
   therefore needs no change to Parcella. Anyone can write a plugin from
   the spec, and the reference receiver in
   `integrations/website-plugin-reference/` is the readable example.

3. **Drafts only is part of the contract.** A plugin must create
   unpublished content and must never change the publish state on
   update.

4. **Authentication: HMAC-SHA256** over
   `timestamp \n METHOD \n path \n body`, with a secret the plugin
   generates and the admin pastes into Parcella (encrypted at rest).
   Method and path are signed so a captured request can't be replayed
   against another endpoint. Plugins reject timestamps outside a ±5
   minute window. Shared-secret HMAC was chosen over OAuth because every
   CMS can implement it in a few lines of standard-library code, and
   over a bearer token because the secret never travels over the wire.

5. **CMS plugins come later, one ticket each** (Drupal, TYPO3, Contao,
   Joomla). Each one should also bundle the inbound features the
   WordPress plugin already has (work-session signup, contact and
   applicant forms, calendar), the same "one plugin per CMS"
   consolidation ADR 0030 did for WordPress. They live in
   `integrations/<cms>/` and are published to their marketplaces from
   there.

## Open before the first marketplace upload

**Licensing.** drupal.org only hosts GPL-2.0-or-later code, and the
WordPress.org directory expects GPL-compatible plugins. Parcella and
today's WordPress plugin are AGPL-3.0-or-later. The plugins talk to
Parcella only over HTTP, so they can carry a different license than
Parcella itself (for example GPL-2.0-or-later) while Parcella stays
AGPL. That's a decision for the copyright holder, to be made per plugin
before it is uploaded. Nothing in this ADR depends on it.

## Rejected

- **A Parcella-side client per CMS:** N clients to maintain against N
  APIs, several of which (TYPO3, Contao) don't exist without an
  extension anyway, and every new CMS would need a Parcella release.
- **Pull instead of push** (the CMS polls Parcella for new drafts): it
  needs a scheduler on every CMS and still a plugin, and it makes "Create
  website draft" asynchronous with no immediate success or error.
