"""
Sanitizes HTML from externally-sourced messages so it can be rendered
safely in the browser -- currently used for FreeScout conversation
threads (app/templates/freescout/detail.html), fetched live from
FreeScout's API and rendered via the `sanitize_html` Jinja filter (see
app/templating.py).

WHY THIS MATTERS: the content ultimately comes from whoever emailed the
support inbox -- anyone can send an email there. That's a classic
stored-XSS setup if the HTML content were rendered unfiltered (e.g.
<script>, <img onerror=...>, javascript: links, hidden tracking).
Nothing from this source is ever output unfiltered with "|safe" (the
function itself returns a markupsafe.Markup instance, so the Jinja
filter needs no separate "| safe" and can't accidentally be re-escaped).
"""
import re

import bleach
from markupsafe import Markup

# <script>/<style> must be removed COMPLETELY (tag AND content) --
# bleach.clean() only strips disallowed tags themselves and keeps the
# text between them (correct for e.g. a stripped <div>, but wrong for
# <script>/<style>, whose content isn't human-readable text). So these
# are removed upfront via regex instead.
_SCRIPT_STYLE_RE = re.compile(r"<(script|style)[^>]*>.*?</\1>", re.IGNORECASE | re.DOTALL)

# Deliberately NO images allowed: prevents both tracking pixels (the
# sender would otherwise learn when/whether the message was opened) and
# the classic <img onerror=...> trick as extra attack surface.
# Deliberately NO class/style attribute allowed: prevents CSS-based
# tricks (e.g. invisible text, spoofed UI elements) and keeps rendering
# consistent with the rest of the page.
ALLOWED_TAGS = [
    "p", "br", "b", "i", "u", "strong", "em", "a",
    "ul", "ol", "li", "blockquote", "span", "div",
    "h1", "h2", "h3", "h4", "h5", "h6",
    "table", "thead", "tbody", "tr", "td", "th",
    "hr", "pre", "code",
]
ALLOWED_ATTRIBUTES = {
    "a": ["href", "title"],
}
ALLOWED_PROTOCOLS = ["http", "https", "mailto"]


def sanitize_email_html(html: str) -> Markup:
    """Sanitizes HTML from an incoming, externally-sourced email/message
    for safe rendering. Returns a Markup instance (not a plain str) so
    the Jinja `sanitize_html` filter (app/templating.py) can be used
    directly as `{{ value | sanitize_html }}` -- no separate `| safe`
    needed, and no risk of it being escaped a second time on render.
    Empty/None input yields an empty Markup string."""
    if not html:
        return Markup("")

    html = _SCRIPT_STYLE_RE.sub("", html)

    cleaned = bleach.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=ALLOWED_PROTOCOLS,
        strip=True,
        strip_comments=True,
    )

    # Open external links in a new tab without letting the target reach
    # the calling page via window.opener -- the content comes from an
    # untrusted sender.
    cleaned = re.sub(
        r'<a\s+href="([^"]*)"([^>]*)>',
        r'<a href="\1" target="_blank" rel="noopener noreferrer"\2>',
        cleaned,
    )
    return Markup(cleaned)
