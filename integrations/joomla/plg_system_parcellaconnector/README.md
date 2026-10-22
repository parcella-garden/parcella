# Parcella Connector for Joomla

A system plugin that receives website drafts from
[Parcella](https://github.com/parcella-garden/parcella), the open-source
club management software for allotment garden associations, as
**unpublished** articles. Publishing stays your decision in Joomla.

It implements the receiving side of the
[Parcella Website Plugin Protocol](https://github.com/parcella-garden/parcella/blob/main/docs/website-plugin-protocol.md):
every request is signed with a shared secret (HMAC-SHA256, valid for five
minutes), drafts become unpublished articles, and updates never change
whether an article is published.

Requirements: Joomla 4.4 or 5, PHP 8.1+.

## Setup

1. Install the package under *System → Install → Extensions*.
2. Open *System → Plugins → System - Parcella Connector*, **enable** it,
   and choose the category and author for new drafts. The shared secret
   was generated at install time.
3. In Parcella: *Admin → Integrations → Website*, choose **Parcella
   plugin** and enter
   - plugin address: `https://YOUR-SITE/index.php/parcella/v1`
     (works with and without URL rewriting)
   - the shared secret from the plugin settings
   then *Test connection* and save.

## What it does with a draft

- Title and text become an unpublished article in the chosen category,
  assigned to the default workflow stage (so it shows up in the article
  list). The HTML arrives already sanitized from Parcella and goes
  through Joomla's input filter again.
- The summary becomes the meta description.
- The image (PNG, JPEG or WebP, at most 5 MB, checked against its file
  signature) is stored under `images/parcella/` with a random name and
  used as intro and full-text image.
- Sending the same announcement twice returns the same article (the
  article's note field holds `parcella:<id>`).
- Parcella asks whether an article has been published, and uses its
  address for the QR code on the printed notice.

## License

GPL-2.0-or-later (`LICENSE.txt`). Parcella itself is AGPL-3.0-or-later;
the plugin only talks to it over HTTP.
