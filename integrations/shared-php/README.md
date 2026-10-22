# Shared PHP core for the CMS plugins

`ParcellaProtocol.php` is the part of the
[Parcella Website Plugin Protocol](../../docs/website-plugin-protocol.md)
that every PHP plugin needs: signature check (HMAC-SHA256, constant-time
comparison, ±5 minute window), endpoint routing, and validation of the
draft body, including images (PNG/JPEG/WebP only, at most 5 MB, the
declared type must match the file's own signature, and stored files get
a random name instead of the sender's).

Marketplaces don't allow plugins to depend on each other, so the Drupal,
Joomla, TYPO3 and Contao plugins each carry a copy with their own
namespace. **Edit this file, never a copy**, then run:

    sh integrations/shared-php/sync.sh

## Tests

`tests/protocol_test.php` checks the core, including that a signature
made by Parcella itself verifies here:

    SIG=$(docker compose -f docker-compose.dev.yml exec -T web python -c \
      "from app.website_connectors.parcella_plugin import sign; print(sign('ab'*32, '1792700000', 'POST', '/parcella/v1/drafts', b'{\"title\":\"Hallo\"}'))")
    docker run --rm -v "$PWD/integrations/shared-php:/app:ro" -w /app php:8.3-cli php tests/protocol_test.php "$SIG"

Licensed GPL-2.0-or-later.
