# Parcella Connector for Contao

Receives website drafts from [Parcella](https://github.com/parcella-garden/parcella),
the open-source club management software for allotment garden
associations, as **unpublished** news entries. Publishing stays your
decision in Contao.

It implements the receiving side of the
[Parcella Website Plugin Protocol](https://github.com/parcella-garden/parcella/blob/main/docs/website-plugin-protocol.md):
every request is signed with a shared secret (HMAC-SHA256, valid for five
minutes), drafts are created unpublished, and updates never change
whether an entry is published.

Requirements: Contao 5.3 LTS or newer with the news bundle, PHP 8.1+.

## Setup

1. Install `parcella/contao-parcella-connector` with the Contao Manager
   (or `composer require parcella/contao-parcella-connector`), then run
   the database migration.
2. *System → Settings → Parcella Connector*: leave **Shared secret**
   empty and save to generate one, and choose the **news archive** and
   **author** for drafts. For Parcella's QR code to find a published
   entry's address, the archive needs a reader page.
3. In Parcella: *Admin → Integrations → Website*, choose **Parcella
   plugin** and enter
   - plugin address: `https://YOUR-SITE/parcella/v1`
   - the shared secret
   then *Test connection* and save.

## What it does with a draft

- Title and summary become the headline and teaser of an unpublished
  news entry; the text becomes one text element in it. The HTML arrives
  already sanitized from Parcella and goes through Contao's allowed-tags
  filter (*System → Settings*) again.
- The image (PNG, JPEG or WebP, at most 5 MB, checked against its file
  signature) is stored in `files/parcella/` with a random name, added to
  the file manager and set as the entry's image.
- Sending the same announcement twice returns the same entry (its
  description holds `parcella:<id>`).
- Parcella asks whether an entry has been published, and uses its reader
  page address for the QR code on the printed notice.
- Parcella shows the entry's number, not an edit link: Contao backend
  links need a request token.

## License

GPL-2.0-or-later (`LICENSE`). Parcella itself is AGPL-3.0-or-later; the
bundle only talks to it over HTTP.
