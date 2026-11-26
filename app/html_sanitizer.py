"""
Sanitizes HTML from externally-sourced messages so it can be rendered
safely in the browser -- currently used for helpdesk conversation
messages (app/templates/support/detail.html), fetched live from the
active helpdesk's API and rendered via the `sanitize_html` Jinja filter (see
app/templating.py).

WHY THIS MATTERS: the content ultimately comes from whoever emailed the
support inbox -- anyone can send an email there. That's a classic
stored-XSS setup if the HTML content were rendered unfiltered (e.g.
<script>, <img onerror=...>, javascript: links, hidden tracking).
Nothing from this source is ever output unfiltered with "|safe" (the
function itself returns a markupsafe.Markup instance, so the Jinja
filter needs no separate "| safe" and can't accidentally be re-escaped).
"""
import nh3
from markupsafe import Markup

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


def clean_html(html: str, tags, attributes) -> str:
    """The one nh3 call behind both sanitizers (this one and
    app/announcement_utils.py). Disallowed tags are stripped, keeping
    their text -- except <script>/<style>, whose content nh3 drops too
    (clean_content_tags). Links open in a new tab without
    window.opener access (rel="noopener noreferrer")."""
    return nh3.clean(
        html,
        tags=set(tags),
        attributes={tag: set(names) for tag, names in attributes.items()},
        url_schemes=set(ALLOWED_PROTOCOLS),
        strip_comments=True,
        link_rel="noopener noreferrer",
        set_tag_attribute_values={"a": {"target": "_blank"}},
    )


def sanitize_email_html(html: str) -> Markup:
    """Sanitizes HTML from an incoming, externally-sourced email/message
    for safe rendering. Returns a Markup instance (not a plain str) so
    the Jinja `sanitize_html` filter (app/templating.py) can be used
    directly as `{{ value | sanitize_html }}` -- no separate `| safe`
    needed, and no risk of it being escaped a second time on render.
    Empty/None input yields an empty Markup string."""
    if not html:
        return Markup("")

    cleaned = clean_html(html, ALLOWED_TAGS, ALLOWED_ATTRIBUTES)
    return Markup(cleaned)
