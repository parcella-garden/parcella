# Parcella Connector for TYPO3

Receives website drafts from [Parcella](https://github.com/parcella-garden/parcella),
the open-source club management software for allotment garden
associations, as **hidden** news records
([EXT:news](https://extensions.typo3.org/extension/news)). Publishing
stays your decision in TYPO3.

It implements the receiving side of the
[Parcella Website Plugin Protocol](https://github.com/parcella-garden/parcella/blob/main/docs/website-plugin-protocol.md):
every request is signed with a shared secret (HMAC-SHA256, valid for five
minutes), drafts are created hidden, and updates never change whether a
record is hidden.

Requirements: TYPO3 12.4 or 13.4 LTS, EXT:news 11 or 12, PHP 8.1+.

## Setup

1. `composer require parcella/typo3-parcella-connector`
   (or install it from the TER), then `vendor/bin/typo3 extension:setup`.
2. *Admin Tools → Settings → Extension Configuration → parcella_connector*:
   - **Shared secret**: 64 hexadecimal characters, e.g. from
     `openssl rand -hex 32`
   - **Storage folder**: the page id of the sysfolder new news drafts go to
   - **Detail page** (optional): the page with the news detail plugin, so
     Parcella can find a published draft's address for its QR code
3. In Parcella: *Admin → Integrations → Website*, choose **Parcella
   plugin** and enter
   - plugin address: `https://YOUR-SITE/parcella/v1`
   - the shared secret
   then *Test connection* and save.

## What it does with a draft

- Title, teaser (the summary) and text become a hidden news record in the
  storage folder, with a URL segment. The HTML arrives already sanitized
  from Parcella and goes through TYPO3's HTML sanitizer again.
- The image (PNG, JPEG or WebP, at most 5 MB, checked against its file
  signature) is stored in the default file storage under `parcella/` with
  a random name and attached as the news media.
- Sending the same announcement twice returns the same record.
- Parcella asks whether a record has been published, and uses its detail
  page address for the QR code on the printed notice.
- Parcella shows the record's number, not an edit link: TYPO3 backend
  links can't be built reliably from a frontend request.

## License

GPL-2.0-or-later (`LICENSE.txt`). Parcella itself is AGPL-3.0-or-later;
the extension only talks to it over HTTP.
