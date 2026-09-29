# Announcements: no overall status, one action per channel until the content changes

**Context:** `Announcement.status` (`DRAFT`/`PUBLISHED`/`ARCHIVED`, part of
the original data model from ADR 0025, though that ADR never discussed
it) never worked. No code path ever set `PUBLISHED`, and
`ARCHIVED` could only be reached through a `POST /archive` endpoint that
no page linked to. So every announcement showed "Draft" forever, even
after the email had gone out, the WordPress draft existed and the PDF had
been printed. At the same time, the edit page always showed all three
action buttons, so an admin could:

- send the email to every member a second time,
- create a second WordPress post next to the one already being edited
  and SEO-optimized in WordPress, and
- regenerate a PDF that would come out identical.

kermie's point: the status made no sense for Parcella. The real question
per channel is "is there anything new to deliver?", and the answer is
only yes after the content was changed and saved.

**Decision:**

1. **Drop `announcements.status` and its enum type** (migration 0092),
   together with the `/archive` endpoint. Deleting an announcement is
   still possible. The list page shows one icon per channel (done /
   failed / sending / not yet) instead of a single status badge.

2. **Each channel's action is offered only while it has something to
   do** (`_channel_action_available` in `app/routers/announcements.py`).
   This is enforced on the server with a 409, not just by hiding the
   button:

   | Channel | Action available when |
   |---|---|
   | Email | never attempted, or last attempt FAILED. **Never again after a successful send**, even after an edit (kermie's call: a second full send to every member isn't something to offer). The edit page notes when the content changed after sending. |
   | Blog | never attempted, FAILED, or title/body/image changed since the last successful delivery. |
   | Print | never attempted, FAILED, title/body/print text/image changed since, the stored PDF is missing, or the last PDF was shortened without a QR code (`qr_pending`) and a blog post now exists that may have been published since. |

3. **"Changed since" compares a content fingerprint, not a timestamp.**
   Each successful delivery stores `content_fingerprint` (sha256 of the
   text that channel delivers, `app.announcement_utils.channel_fingerprint`)
   and the `image_filename` it delivered. A `content_changed_at`
   timestamp was the first idea but was rejected: clicking **Save** without
   changing anything, or changing text and then changing it back, would
   still bump the timestamp and wrongly re-enable a channel. The
   fingerprint is per channel. Print includes `print_text_override`;
   email and blog don't, so editing only the print text re-enables only
   the PDF.

4. **Blog: after a change, update the same WordPress post instead of
   creating a new one** (`WordPressPublisher.update_post`, `POST
   /wp/v2/posts/{id}`). The payload deliberately contains only `title`,
   `content` and, if the image changed, `featured_media`. It never
   includes `status`: a post a human already published stays published.
   Excerpt, categories, tags and SEO plugin fields (stored separately as
   post meta) survive. Text edits made directly in WordPress's editor
   are overwritten, and the confirm dialog says so. The image is only
   re-uploaded when it actually changed, so the media library doesn't
   fill up with copies. If the post was deleted in WordPress (404/410),
   the update falls back to creating a fresh draft.

5. **Print: the generated PDF is stored** (`pdf_filename`, under
   `app/static/uploads/announcements/print/`) and can be downloaded again
   via `GET /announcements/{id}/print/download`. The stored copy is
   byte-identical to the printed one, with no regeneration. It lives under
   `static/uploads/` because that's the one persisted data directory
   (ADR 0077). The filenames are random UUIDs, and the content is a notice
   meant for the notice board anyway. The old file is removed when a new
   PDF is generated or the announcement is deleted.

**Rejected alternatives:**

- *Keep the status and set `PUBLISHED` automatically on the first
  successful send.* That fixes the label but not the actual problem,
  the always-active buttons. The status would also have stayed a lossy
  summary of three independent per-channel states.
- *Offer the email again after an edit ("send correction").* Offered
  and explicitly declined.
- *Create a new WordPress draft on every change* (the previous
  behavior). This leaves duplicates behind and loses track of the post
  the admin actually works on in WordPress.

**Consequences:** Existing SENT deliveries were backfilled with the
announcement's *current* content (migration 0092, which uses a frozen copy
of the fingerprint function), so nothing appears as "changed" right
after the upgrade. Print deliveries created before this change have no
stored PDF, so their "Generate PDF" button is offered once more.
