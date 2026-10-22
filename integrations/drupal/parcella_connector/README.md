# Parcella Connector for Drupal

Receives website drafts from [Parcella](https://github.com/parcella-garden/parcella),
the open-source club management software for allotment garden
associations, as **unpublished** content. Publishing stays your decision
in Drupal.

It implements the receiving side of the
[Parcella Website Plugin Protocol](https://github.com/parcella-garden/parcella/blob/main/docs/website-plugin-protocol.md):
every request is signed with a shared secret (HMAC-SHA256, valid for five
minutes), drafts are created as unpublished nodes, and updates never
change whether a node is published.

Requirements: Drupal 10.3 or 11, PHP 8.1+.

## Setup

1. Install and enable the module (`composer require drupal/parcella_connector`
   and `drush en parcella_connector`, or upload it under *Extend*).
2. Open *Configuration → Web services → Parcella Connector*. It shows the
   **plugin address** and a **shared secret** generated at install time.
   Choose the content type for drafts (default *Article*), its text field
   (default `body`) and image field (default `field_image`).
   Drupal 11.4's standard profile creates no content types; add one
   first, e.g. `drush recipe core/recipes/article_content_type`.
3. In Parcella: *Admin → Integrations → Website*, choose **Parcella
   plugin**, enter both values, *Test connection*, save.

Only users with the *Administer the Parcella Connector* permission can see
the secret.

## What it does with a draft

- Title, text and summary go into the chosen fields. The HTML arrives
  already sanitized from Parcella and is filtered again by Drupal's admin
  XSS filter and the chosen text format.
- The image (PNG, JPEG or WebP, at most 5 MB, checked against its file
  signature) is stored under `public://parcella/` with a random name.
- Sending the same announcement twice returns the same node.
- Parcella asks whether a node has been published, and uses its address
  for the QR code on the printed notice.

## License

GPL-2.0-or-later (`LICENSE.txt`). Parcella itself is AGPL-3.0-or-later;
the module only talks to it over HTTP.
