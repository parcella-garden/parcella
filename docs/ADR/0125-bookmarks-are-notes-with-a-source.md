# Bookmarks are notes with a source; Parcella never fetches the pages

**Context:** issue #305, step 1 of the knowledge base (#285). kermie
wants to drop Nextcloud Bookmarks: notes in Parcella become the only
source of truth for the club's knowledge, later steered from an
external AI (#307). The bookmarks already collected in Nextcloud have to
come across, and what the linked sites say should end up in notes.

## Decision

- **A bookmark is a note with a `source`.** No separate bookmark table:
  `notes.source_url` (since ADR 0127 only there; at first also a
  `source:` line in the note file's header, ADR 0123 -- a header from
  a file that turns up in the notes folder is still read on import,
  `url:` too, which is what web clippers write). A bookmark has a title,
  a date, tags and a text, the same as a note, and it should be found by
  the same search and filters. A second entity would duplicate all of
  that, and the AI connector would need two sets of tools.
- **Only `http`/`https` URLs with a host**, checked in one place
  (`clean_source_url()` in `app/note_files.py`). It runs on every way
  in: the form, the API, a hand-edited file and the import. The value
  goes into an `href`, so `javascript:`/`data:` must never get through.
  Links open with `rel="noopener noreferrer nofollow"`.
- **One-time import from the standard bookmark export file** (Netscape
  HTML), not the Nextcloud Bookmarks API. Nextcloud and every browser
  export this format, so the import works for clubs without Nextcloud
  (cloud storage stays backend-agnostic), and nothing Nextcloud-specific
  needs maintaining after the migration.
  - Each bookmark becomes a note **in the notes folder root**, no
    category (kermie: "shall go to /kgv_notizen/").
  - The bookmark's folders become **extra tags** next to its own
    tags, so the grouping survives without creating subfolders.
  - The date comes from `ADD_DATE`, the text from the description.
  - Preview first, then import. The file round-trips as hidden base64,
    as in the CSV wizards (ADR 0083).
  - A URL that a live note already has as its source is skipped, so
    re-running is safe. A URL that appears twice in the file is merged.
  - Every note goes through `create_note()`, in its own savepoint. One
    failed cloud upload leaves nothing behind and doesn't stop the rest.
- **Parcella never fetches the bookmarked pages.** Getting a page's
  content into a note (summary, key points) is the external AI's job
  (#307). A server that fetches URLs on request is an SSRF tool. Useful
  summaries would need an AI inside Parcella. And many pages only
  render with JavaScript or sit behind paywalls. Laws and rulings may be
  copied in full; press articles get a summary and the link.

## Rejected

- **A dedicated `Bookmark` model.** It would duplicate taxonomy, search,
  cloud sync and API for something that is a note plus one field.
- **Syncing with Nextcloud Bookmarks permanently.** The goal is to
  retire it, and a two-way sync would tie the knowledge base to one
  backend.
- **Folders → categories for imported bookmarks.** kermie chose the
  notes root, with folders kept as tags.
