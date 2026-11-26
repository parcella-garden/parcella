# 0143: Self-hosted vendor assets, gzip for static files only

**Status:** proposed (issue #413)

## Context

Bootstrap, Bootstrap Icons, EasyMDE, SortableJS and Chart.js loaded from
`cdn.jsdelivr.net`, without Subresource Integrity, on every page. Static
files had no `Cache-Control`, and the app compressed nothing itself.

## Decision

- **Self-host** the vendor files under `app/static/vendor/<package>@<version>/`
  (the CDN's own path layout). Every visitor's IP no longer goes to a
  third party, a CDN outage can't break the UI, and the CSP allows
  `'self'` only -- no CDN origin left. Upgrading a library means a new
  versioned folder, never overwriting files in an old one.
- **Caching:** `vendor/` is `public, max-age=31536000, immutable` (the
  version is in the path). Everything else under `/static` (uploads, the
  club logo, favicons) is `no-cache`: it can change under the same
  name, so it's revalidated by ETag (a cheap 304).
- **gzip for `/static` only.** HTML pages carry the CSRF token next to
  reflected input (search boxes), which is the shape a BREACH attack
  needs. The large, compressible responses are the vendor CSS/JS
  anyway. A reverse proxy may still compress HTML if its operator
  accepts that.

## Rejected

- **SRI hashes on the CDN links:** keeps the third-party request and
  the CDN in the CSP; only protects against a tampered file.
- **`GZipMiddleware` on the whole app:** BREACH, see above.

## Consequences

- About 1.3 MB of minified third-party files in the repo (all MIT).
- The inline `<style>`/`<script>` blocks in `base.html` are not moved
  out yet, so `'unsafe-inline'` stays in the CSP (ADR 0064).
