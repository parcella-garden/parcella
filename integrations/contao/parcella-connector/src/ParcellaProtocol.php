<?php

declare(strict_types=1);

/*
 * Parcella Website Plugin Protocol v1 -- the part every CMS plugin shares
 * (docs/website-plugin-protocol.md in the Parcella repository).
 *
 * Do not edit this copy: edit (integrations/shared-php/ParcellaProtocol.php), then run
 * integrations/shared-php/sync.sh. Marketplaces don't allow plugins to
 * depend on each other, so each plugin carries its own copy.
 *
 * Licensed GPL-2.0-or-later.
 */

namespace Parcella\ContaoParcellaConnector;

final class ParcellaProtocol
{
    public const PROTOCOL = 'parcella-website/1';
    public const MAX_CLOCK_SKEW_SECONDS = 300;
    public const MAX_BODY_BYTES = 10 * 1024 * 1024;
    public const MAX_IMAGE_BYTES = 5 * 1024 * 1024;
    public const MAX_TITLE_LENGTH = 255;
    public const MAX_SOURCE_ID_LENGTH = 100;

    /** Allowed image types and the file extension each one gets. */
    public const IMAGE_TYPES = ['image/png' => 'png', 'image/jpeg' => 'jpg', 'image/webp' => 'webp'];

    /** A new shared secret: 32 random bytes, hex encoded (64 characters). */
    public static function generateSecret(): string
    {
        return bin2hex(random_bytes(32));
    }

    /**
     * Checks a request's X-Parcella-Signature. $path is the URL path exactly
     * as the request line carried it (no host, no query string), $body the
     * raw request body. Rejects a secret shorter than 32 characters, a
     * missing or non-numeric timestamp, a timestamp more than five minutes
     * off, and anything but an exact signature match (compared in constant
     * time).
     */
    public static function verify(
        string $secret,
        string $method,
        string $path,
        string $body,
        ?string $timestamp,
        ?string $signature,
        ?int $now = null
    ): bool {
        if (strlen($secret) < 32 || $timestamp === null || $signature === null || !ctype_digit($timestamp)) {
            return false;
        }
        $now = $now ?? time();
        if (abs($now - (int) $timestamp) > self::MAX_CLOCK_SKEW_SECONDS) {
            return false;
        }
        $message = $timestamp . "\n" . strtoupper($method) . "\n" . $path . "\n" . $body;
        $expected = 'sha256=' . hash_hmac('sha256', $message, $secret);

        return hash_equals($expected, $signature);
    }

    /** The URL path of a raw request URI, e.g. "/parcella/v1/drafts/42". */
    public static function requestPath(string $requestUri): string
    {
        $path = parse_url($requestUri, PHP_URL_PATH);

        return is_string($path) ? $path : '/';
    }

    /**
     * The route below the plugin's base path: ['ping', null],
     * ['drafts', null], ['drafts', '42'] -- or null if the path isn't one of
     * the protocol's endpoints.
     *
     * @return array{0: string, 1: ?string}|null
     */
    public static function route(string $path, string $basePath = '/parcella/v1'): ?array
    {
        $base = rtrim($basePath, '/');
        $position = strpos($path, $base . '/');
        if ($position === false) {
            return null;
        }
        $rest = substr($path, $position + strlen($base) + 1);
        $parts = explode('/', trim($rest, '/'));
        if ($parts === ['ping']) {
            return ['ping', null];
        }
        if ($parts === ['drafts']) {
            return ['drafts', null];
        }
        if (count($parts) === 2 && $parts[0] === 'drafts' && $parts[1] !== '') {
            return ['drafts', rawurldecode($parts[1])];
        }

        return null;
    }

    /** The answer to GET /ping. */
    public static function pingPayload(string $name, string $version): array
    {
        return ['protocol' => self::PROTOCOL, 'name' => $name, 'version' => $version];
    }

    /**
     * Parses and validates a draft body (POST /drafts, PUT /drafts/{id}).
     * Returns the normalized draft; 'image' is one of
     *   ['state' => 'unchanged']                      (key absent, PUT only)
     *   ['state' => 'remove']                         (null)
     *   ['state' => 'replace', 'bytes' => ..., 'mime' => ..., 'extension' => ...]
     * The visitor-supplied file name is never used: callers name stored
     * files with storedFilename().
     *
     * @throws \InvalidArgumentException with a message safe to send back
     */
    public static function parseDraft(string $body): array
    {
        if (strlen($body) > self::MAX_BODY_BYTES) {
            throw new \InvalidArgumentException('Request body too large.');
        }
        try {
            $data = json_decode($body, true, 16, JSON_THROW_ON_ERROR);
        } catch (\JsonException $e) {
            throw new \InvalidArgumentException('Body is not valid JSON.');
        }
        if (!is_array($data)) {
            throw new \InvalidArgumentException('Body must be a JSON object.');
        }

        $title = self::stringField($data, 'title');
        $title = trim(preg_replace('/[\r\n\t]+/', ' ', $title) ?? '');
        if ($title === '') {
            throw new \InvalidArgumentException('Field "title" is required.');
        }
        if (mb_strlen($title) > self::MAX_TITLE_LENGTH) {
            $title = mb_substr($title, 0, self::MAX_TITLE_LENGTH);
        }
        $sourceId = self::stringField($data, 'source_id');
        if (strlen($sourceId) > self::MAX_SOURCE_ID_LENGTH || preg_match('/[^A-Za-z0-9_.:-]/', $sourceId)) {
            throw new \InvalidArgumentException('Field "source_id" is invalid.');
        }

        return [
            'title' => $title,
            'markdown' => self::stringField($data, 'markdown'),
            'html' => self::stringField($data, 'html'),
            'summary' => trim(self::stringField($data, 'summary')),
            'language' => substr(preg_replace('/[^A-Za-z_-]/', '', self::stringField($data, 'language')) ?? '', 0, 10),
            'source_id' => $sourceId,
            'image' => self::parseImage($data),
        ];
    }

    /** A random file name for a stored image -- never the sender's. */
    public static function storedFilename(string $extension): string
    {
        return 'parcella-' . bin2hex(random_bytes(8)) . '.' . $extension;
    }

    private static function stringField(array $data, string $key): string
    {
        $value = $data[$key] ?? '';
        if (!is_string($value)) {
            throw new \InvalidArgumentException(sprintf('Field "%s" must be a string.', $key));
        }

        return $value;
    }

    private static function parseImage(array $data): array
    {
        if (!array_key_exists('image', $data)) {
            return ['state' => 'unchanged'];
        }
        $image = $data['image'];
        if ($image === null) {
            return ['state' => 'remove'];
        }
        if (!is_array($image) || !is_string($image['data_base64'] ?? null) || !is_string($image['mime'] ?? null)) {
            throw new \InvalidArgumentException('Field "image" is invalid.');
        }
        $mime = strtolower($image['mime']);
        if (!isset(self::IMAGE_TYPES[$mime])) {
            throw new \InvalidArgumentException('Only PNG, JPEG and WebP images are accepted.');
        }
        $bytes = base64_decode($image['data_base64'], true);
        if ($bytes === false || $bytes === '') {
            throw new \InvalidArgumentException('Image data is not valid base64.');
        }
        if (strlen($bytes) > self::MAX_IMAGE_BYTES) {
            throw new \InvalidArgumentException('Image is larger than 5 MB.');
        }
        // The declared type must match the file's own signature, so nothing
        // but a real image is ever written into the CMS's file storage.
        if (self::detectImageType($bytes) !== $mime) {
            throw new \InvalidArgumentException('Image content does not match its declared type.');
        }

        return ['state' => 'replace', 'bytes' => $bytes, 'mime' => $mime, 'extension' => self::IMAGE_TYPES[$mime]];
    }

    private static function detectImageType(string $bytes): ?string
    {
        if (strncmp($bytes, "\x89PNG\r\n\x1a\n", 8) === 0) {
            return 'image/png';
        }
        if (strncmp($bytes, "\xFF\xD8\xFF", 3) === 0) {
            return 'image/jpeg';
        }
        if (strncmp($bytes, 'RIFF', 4) === 0 && substr($bytes, 8, 4) === 'WEBP') {
            return 'image/webp';
        }

        return null;
    }
}
