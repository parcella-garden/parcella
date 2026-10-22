# Parcella Website Plugin Protocol, version 1

How a CMS plugin receives website drafts from Parcella. A plugin that
follows this spec works with the "Parcella plugin" choice on Parcella's
Admin -> Integrations -> Website, without any change to Parcella itself.
Why it exists: ADR 0105. A runnable reference receiver:
`integrations/website-plugin-reference/`.

Protocol identifier: `parcella-website/1`.

## Ready-made plugins

| CMS | Plugin | Drafts become |
|---|---|---|
| Drupal 10.3 / 11 | `integrations/drupal/parcella_connector` | unpublished nodes |
| Joomla 4.4 / 5 | `integrations/joomla/plg_system_parcellaconnector` | unpublished articles |
| TYPO3 12.4 / 13.4 (EXT:news) | `integrations/typo3/parcella_connector` | hidden news records |
| Contao 5.3 (news) | `integrations/contao/parcella-connector` | unpublished news entries |

They share one PHP core (`integrations/shared-php/`) and are
GPL-2.0-or-later (ADR 0108). WordPress needs no plugin for drafts:
Parcella uses its REST API directly. How to publish them to their
marketplaces: `docs/cms-plugins-publishing.md`.

## Setup

1. The plugin generates a random **shared secret** (at least 32 bytes
   of randomness, e.g. 64 hex characters) and shows it to the CMS admin
   together with its **endpoint URL**, the base all paths below hang off
   (for example `https://example.org/parcella/v1`).
2. The Parcella admin chooses "Parcella plugin" in the Website dropdown,
   enters both values and clicks "Test connection", which calls `/ping`.

## Authentication (every request)

Parcella sends these headers:

| Header | Value |
|---|---|
| `X-Parcella-Protocol` | `parcella-website/1` |
| `X-Parcella-Timestamp` | Unix time in seconds, e.g. `1792700000` |
| `X-Parcella-Signature` | `sha256=` + lowercase hex HMAC-SHA256 |

The signed message is the timestamp, the upper-case HTTP method and the
URL **path** (without host or query string), each followed by a newline
(`\n`), then the raw request body bytes (empty for GET):

```
<timestamp>\n<METHOD>\n<path>\n<body>
```

The plugin must:

- recompute the signature with its secret and compare it in constant
  time (`hash_equals` in PHP, `hmac.compare_digest` in Python);
- reject a timestamp more than 300 seconds away from its own clock;
- answer `401` if either check fails, without any further detail.

## Endpoints

All bodies are JSON (`Content-Type: application/json`, UTF-8).

### `GET /ping`

Answer `200`:

```json
{"protocol": "parcella-website/1", "name": "Parcella Connector for TYPO3", "version": "1.0.0"}
```

`protocol` must match exactly. Parcella refuses to talk to a different
version.

### `POST /drafts` (create a draft)

Request:

```json
{
  "title": "New compost bins",
  "markdown": "We installed **new** bins.",
  "html": "<p>We installed <strong>new</strong> bins.</p>",
  "summary": "",
  "language": "de",
  "source_id": "6f1c...-announcement-uuid",
  "image": {"filename": "4b2e....png", "mime": "image/png", "data_base64": "iVBORw0..."}
}
```

- Use whichever of `markdown`/`html` suits the CMS: both carry the same
  text. `html` is already sanitized by Parcella.
- `image` is `null` when there is none. Allowed MIME types: `image/png`,
  `image/jpeg`, `image/webp`. Parcella limits images to 5 MB.
- `source_id` identifies the announcement. A plugin may use it to avoid
  duplicates (if a draft for this `source_id` already exists, return it
  instead of creating a second one).
- The content **must be created unpublished** (draft/hidden).

Answer `201`:

```json
{"id": "42", "edit_url": "https://example.org/typo3/record/edit?..."}
```

`id` is a string of at most 100 characters that the plugin recognises
later. `edit_url` is optional; if present, the announcement page links
to it.

### Only the plugin's own drafts

`PUT /drafts/{id}` and `GET /drafts/{id}` must only work on content the
plugin created through `POST /drafts`. For any other id -- an existing
page, article or news entry a human made -- answer `404`, exactly as if
it didn't exist. Otherwise the shared secret would grant write access to
all of the CMS's content instead of "may create drafts", and an update
would put the overwritten text live at once, since updates keep the
publish state. Keep a record of what you created (a mapping table, a
marker field) and check it on every lookup.

### `PUT /drafts/{id}` (update)

The same body as `POST`. The `image` key has three states:

- **absent**: the image didn't change, so keep the current one;
- **`null`**: the image was removed, so remove it;
- **an object**: a new image, so replace the current one.

Update title and text. **Never change the publish state**: a post a
human has published stays published. Keep anything Parcella doesn't
send (categories, tags, SEO fields, author).

Answer `200` with the same shape as for `POST`, or `404` if the draft no
longer exists. Parcella then creates a new one with `POST`.

### `GET /drafts/{id}` (status)

Answer `200`:

```json
{"status": "draft", "public_url": null}
```

or, once a human has published it:

```json
{"status": "published", "public_url": "https://example.org/news/new-compost-bins"}
```

`404` if it no longer exists. Parcella uses `public_url` for the QR code
on the printed notice.

## Errors

Any other status is shown to the Parcella admin as a failure, with the
first 200 characters of the response body, so a short plain-text or
JSON message helps them. Never put secrets or stack traces in it.

## Versioning

Additions that old plugins can safely ignore (new optional JSON keys)
keep the protocol at `/1`. Anything else becomes `parcella-website/2`,
and Parcella will keep speaking `/1` alongside it for a transition
period.
