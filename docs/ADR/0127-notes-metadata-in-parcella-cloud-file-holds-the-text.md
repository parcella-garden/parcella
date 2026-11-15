# Notes: metadata lives in Parcella, the cloud file holds only the text

**Context:** issue #311, right after v6.5.0. On prod, changing only a
note's title, tags or category failed with "Upload to Nextcloud failed
(HTTP 423)". 423 is WebDAV's *Locked*: the file was open in a Nextcloud
editor (Text, Collabora, OnlyOffice), or a lock had outlived the
editor. The save still hit the file because under ADR 0123 the `.md`
file was the master for *everything*: id, title, date, source,
category and tags sat in its front-matter header, so every metadata
edit rewrote the file.

kermie's call: Parcella replaces Nextcloud Notes and Nextcloud
Bookmarks. Nextcloud Files keeps only the notes' text as `.md`. The
metadata belongs to Parcella.

## Decision

This supersedes the parts of ADR 0123 that put metadata into the file.
Everything else there stays: folder = category, hash-based conflict
check, sync on use, soft delete, conflict copies.

- **The file is the text, nothing else** (`render_note_body()` in
  `app/note_files.py`). Title, date, tags and source live only in the
  `notes` table, and that table is now their master. Bookmarks get a
  file too, holding their description (often empty).
- **The folder is still the category**, both ways (kermie). Changing
  the category in Parcella moves the file. Moving the file in the cloud
  changes the category. A file in the notes folder itself means no
  category, both when it's read and when it's written.
- **A metadata-only save never touches the cloud.** `update_note()`
  writes the file only when the text changed or the category no
  longer matches the file's top folder (`_file_affected()`). So a file
  that's locked in an editor can't block a change to the title, tags,
  date or source. Text and category changes still go through the
  download + `base_hash` check + upload of ADR 0123.
- **A move that can't finish is undone.** If the new copy is uploaded
  but the old file can't be deleted (it's locked), the new copy is
  deleted again and the save is refused. Before this, the move only
  logged a warning, and the next sync imported the old file as a
  second note.
- **Renames are relinked by content**, since there's no `id:` header
  any more. Sync takes an unknown file as a renamed or moved note when
  its sha256 matches the last-known hash of exactly one note whose own
  file is gone (that note is live or soft-deleted). The note keeps its
  metadata, and its folder sets the category. Empty files and several
  matches are never relinked: a wrong guess would hand one note's tags
  and title to another. In that case the old note is soft-deleted and
  the file comes in as a new note. The `id:` header of a pre-0127 file
  is still honoured first.
- **Files from elsewhere are still adopted.** A new file in the folder
  (Obsidian, hand-written, from before 0127) is parsed as before:
  header, else first heading, file name or folder. Then it's rewritten
  as text only. A header in a file that's already linked is ignored
  (its text is taken, its metadata isn't) and stripped. Only a block
  with a key Parcella knows (`id`, `title`, `date`, `category`, `tags`,
  `source`, `url`) counts as a header, so a note that starts with a
  `---` horizontal rule keeps it.
- **A one-time strip** (migration 0122, ClubSetting
  `notes_strip_headers_pending`): while the setting exists, sync reads
  every file instead of only the changed ones. A file edited in the
  cloud since the last sync gets its header taken over one last time.
  Every file with a header is then rewritten as text only, with the
  push going over exactly the version just read. A root file with a
  `category:` header moves into that category's folder. The setting is
  removed after a sync with no errors, so a file that's locked at that
  moment is retried next time.
- **The `.md` download** from a note's page keeps the header
  (`render_note_file()`), so an exported note still carries its
  metadata. It's a copy for people, not the cloud file.
- **423 has a readable message** in the WebDAV client
  (`_locked()` in `app/cloud_storage.py`): the file is locked, probably
  open in an editor; close or unlock it and try again.

## Rejected

- **Keep the header as master and retry on 423**: a lock can last as
  long as someone keeps the file open. Every metadata edit would stay
  a cloud write that can fail, for data nobody edits in Nextcloud any
  more.
- **A sidecar file per note** (`.x.meta.json`) or one index file: it
  moves the same lock and conflict problem into another file, and it
  shows up as clutter in everybody's Nextcloud.
- **Folders mean nothing**: kermie wants the folder structure in
  Nextcloud to keep matching the categories.
- **Treat every rename as delete + new**: simpler, but a file tidied
  into another folder would lose its tags and title.

## Consequences / known gaps

- Editing the front matter of a file in Nextcloud no longer changes
  anything in Parcella. Title, tags, date and source are edited in
  Parcella or via the REST API only. This changes the file contract
  from ADR 0123, so it counts as a breaking change for versioning.
- A rename *and* a text edit in the cloud between two syncs can't be
  matched by content: the note comes back as a new one without its
  metadata, and the old one is soft-deleted (restorable).
- Two notes with identical text whose files were renamed in the same
  sync window aren't relinked, for the same reason.
- The strip drops unknown header keys (Obsidian `aliases`, ...), as
  rewriting already did under ADR 0123.
- A category change is still a cloud write, so a locked file blocks
  it, now with a clear message and without a stray copy.
