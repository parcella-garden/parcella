# Ticket emails: sanitize untrusted HTML, don't just strip it to text

**Context:** incoming ticket emails were being reduced to plain text
even when they arrived as HTML -- and when an email had *only* an HTML
part (no `text/plain` alternative, common with many email clients), the
fallback was a crude regex tag-strip that left things like raw CSS from
`<style>` blocks visible as text. The board wanted HTML emails to
actually render properly instead.

**The security constraint that shapes everything here:** the ticket
inbox accepts email from any external sender -- there's no
authentication, no relationship required. Rendering that content as HTML
without sanitizing it first is a textbook stored-XSS vector: a malicious
email could contain `<script>`, event-handler attributes, `javascript:`
links, or tracking pixels via `<img>`. This is *not* the same trust
level as, say, a club-settings field a logged-in board member typed in.

**Decision: sanitize with an allowlist (bleach; since #419 nh3, as bleach is archived upstream), not a denylist.**
`app/html_sanitizer.py` allows a small set of formatting tags (`p`,
`b`/`i`/`strong`/`em`, `a`, lists, tables, headings, `blockquote`) and
only `href`/`title` on `<a>`, with link protocols restricted to
`http`/`https`/`mailto`. Everything else is stripped, including all
`style=`/`class=` attributes (blocks CSS-based tricks like invisible
text) and `<img>` entirely (blocks both tracking pixels and the classic
`onerror=` attack). External links get `target="_blank"
rel="noopener noreferrer"` added automatically.

**One bleach behavior that needed a workaround:** `bleach.clean()`
strips disallowed *tags* but keeps their *inner text* by default --
correct for something like a stripped `<div>`, wrong for `<script>`/
`<style>`, whose content isn't human-readable text at all. Confirmed
this empirically before relying on it (`<script>alert(1)</script>`
survives `bleach.clean()` as the bare text `alert(1)`). Fixed by
regex-stripping `<script>`/`<style>` blocks -- tag *and* content --
before bleach ever sees the HTML.

**Sanitize at ingestion, plus a second pass at render time.** The
association's inbox only ever needs to render this content in one
place (the ticket detail page) today, but ingestion-time sanitization
alone relies on every future display surface remembering to never
bypass it. A `sanitize_html` Jinja filter is applied again at render
time as a cheap, idempotent defense-in-depth safety net -- re-sanitizing
already-clean HTML costs nothing and costs nothing to get wrong, but
catches a future code path that might render this content without
going through the same ingestion path.

**Plain text (`TicketMessage.content`) is kept regardless**, for search,
notifications, and as the display fallback for emails with no HTML part
-- HTML rendering is additive, not a replacement for the existing plain
text handling.

