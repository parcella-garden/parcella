# Announcement summary: one plain-text field for preheader and excerpt

**Context:** issue #317. The board wants a short summary per
announcement, for accessibility and SEO. It should show as the second
line in the inbox (the preview under the subject) and as the summary in
the website's list of posts.

## Decision

- **One optional field, `Announcement.summary`**: plain text, one line
  (whitespace flattened), at most 300 characters. There's no Markdown,
  because every place it goes (preheader, excerpt, teaser, meta
  description) wants plain text.
- **Email: hidden preheader.** A `display:none` block at the very top of
  the HTML body, escaped. Mail clients show it as the preview line; the
  mail itself doesn't show it. Without a summary, there's no preheader,
  and the client previews the body as before.
- **Website: the existing `summary` slot.** The plugin protocol already
  had a `summary` field (always `""` until now) and the Markdown folder
  a `summary:` line (auto-generated from the first paragraph). Both now
  carry the board's summary when there is one. WordPress gets it as
  `excerpt`, and only when it's set, so an excerpt someone wrote in
  WordPress isn't wiped by an empty one.
- **Change tracking via the fingerprint, appended only when non-empty**,
  and only for EMAIL and BLOG. Every fingerprint stored before #317
  (no summary) hashes exactly as before, so nothing shows as "changed"
  after the upgrade, and migration 0092's frozen copy stays correct.
  Unlike the alt text (ADR 0128), no connector needs to know *that* the
  summary changed, so no separate delivery column is needed.
- While in there, the email shell now escapes the title and club name,
  which it used to insert raw.

## Rejected

- **A separate delivery column** like `image_alt`. Not needed, because
  the summary is sent on every update anyway.
- **Auto-generating a summary when empty** for the email. The client
  already previews the body, so a generated preheader would just repeat
  it.
