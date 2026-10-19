"""
Security-related HTTP response headers.

The app previously sent none of these, which mattered more here than in
a typical server-rendered app because user-uploaded files are served
from the SAME origin as the UI (/static/uploads/: avatars, announcement
images, and the club logo -- which is allowed to be an SVG, and an SVG
opened directly runs its own script).

The CSP is deliberately not maximal. Bootstrap and Bootstrap Icons come
from jsdelivr (see base.html), and the templates carry inline <style>
blocks and inline <script> blocks, so 'unsafe-inline' has to stay for
now -- removing it means nonce-ing every inline block, which is a
separate, much larger change. What the policy DOES buy today:
  * no script may be loaded from anywhere except this origin and the
    one pinned CDN -- an injected <script src> to an attacker host is
    dead on arrival,
  * form-action 'self' stops an injected <form> from posting a member's
    data (or an admin's) off-site,
  * frame-ancestors 'none' + X-Frame-Options makes clickjacking of the
    admin panel impossible,
  * object-src 'none' and base-uri 'self' close the two classic
    injection escapes.

HSTS is only sent outside development: sending it from a local http://
instance would pin the browser to https://localhost for months.
"""
import re
from urllib.parse import quote

from app.config import settings

CDN_ORIGIN = "https://cdn.jsdelivr.net"

CONTENT_SECURITY_POLICY = "; ".join([
    "default-src 'self'",
    f"script-src 'self' 'unsafe-inline' {CDN_ORIGIN}",
    f"style-src 'self' 'unsafe-inline' {CDN_ORIGIN}",
    f"font-src 'self' data: {CDN_ORIGIN}",
    # data: for the QR codes and inline PDFs the app generates itself.
    "img-src 'self' data:",
    "connect-src 'self'",
    "form-action 'self'",
    "frame-ancestors 'none'",
    "base-uri 'self'",
    "object-src 'none'",
])

# 1 year, the value the preload lists expect. No preload directive: that
# is a per-installation decision (it's effectively irreversible), not
# ours to make for every club.
HSTS_VALUE = "max-age=31536000; includeSubDomains"


def security_headers() -> dict:
    headers = {
        "Content-Security-Policy": CONTENT_SECURITY_POLICY,
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        # same-origin, not no-referrer: internal links still get a
        # referrer (useful in logs), but member/parcel URLs -- which
        # carry ids -- never leak to an external site.
        "Referrer-Policy": "same-origin",
    }
    if not settings.is_development:
        headers["Strict-Transport-Security"] = HSTS_VALUE
    return headers


def content_disposition(filename: str, disposition: str = "attachment") -> str:
    """Content-Disposition value for a filename that holds user data (an
    uploaded file's name, a member's last name, an account name). A quote,
    CR/LF or a character outside latin-1 ("Ł", "ř") written straight into
    the header either breaks the response with a 500 or splits it (see
    the header sharp edge in CLAUDE.md). The plain `filename` is an ASCII
    fallback; browsers use the exact, percent-encoded `filename*`."""
    fallback = re.sub(r"[^A-Za-z0-9._ -]+", "_", filename).strip(" ._") or "download"
    return f"{disposition}; filename=\"{fallback}\"; filename*=UTF-8''{quote(filename, safe='')}"
