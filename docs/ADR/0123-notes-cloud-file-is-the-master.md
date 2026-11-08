# Notes: the .md file in the cloud is the master, the database is its index

**Context:** issue #286. Notes "shall be stored in a defined folder of
my cloud file hosting (if configured)" and "shall be searchable,
filterable and sortable". Two ways to read that: Parcella keeps notes
and mirrors them to the cloud, or the files in the cloud *are* the
notes and Parcella works on them. kermie chose the second: the board
also opens, edits and creates these files directly (Nextcloud Text,
Obsidian, any editor), and those edits must show up in Parcella.

## Decision

With the cloud storage module on, a provider configured and a notes
folder set (`ClubSetting notes_cloud_folder`, Admin -> Integrations ->
Cloud storage), the folder's `*.md` files are the notes:

- **File format** (`app/note_files.py`): Markdown with a YAML-compatible
  front-matter header -- `id`, `title`, `date` (`YYYY-MM-DD`; a time
  written after it by hand is ignored), `category`, `tags`. Category and tags are
  written by name, in the club language. Parsing is lenient for
  hand-written files (unquoted values, block lists, no header at all:
  title from the first heading or the file name, date from a
  file name prefix, see below). No YAML library: this small grammar
  is all that's needed, and a full YAML parser on files from outside
  is attack surface for nothing.
- **File names** are generated once (`2026-03-04-board-meeting.md`,
  ASCII slug, `-2` on a clash) and never changed by Parcella, so a
  retitled note doesn't move under someone's open editor.
- **Subfolders are categories, both ways** (kermie, follow-up on #286:
  clubs already keep notes sorted into folders on ownCloud/Nextcloud).
  The notes folder is read recursively (hidden `.folders` skipped, 8
  levels deep), and `cloud_filename` holds the path relative to it.
  The *first* folder level is the category: it wins over a `category:`
  in the header, matches an existing category by name or any
  translation, and creates the category if none matches. Files directly
  in the notes folder take the header's category. Deeper levels
  (`Vorstandssitzung/2026/`) are kept as they are and mean nothing.
  Saving a note whose category doesn't match its top folder moves the
  file (upload into the category's folder, created in the club language
  if missing, then delete the old one); no category = the notes folder
  itself. Renaming or deleting a category marks its notes dirty, so the
  next sync moves their files. A file moved between folders in the cloud
  is relinked by its `id` and changes category.
- **The note's date is the day it's about, never the import day**:
  header `date:`, else a file name prefix (`YYYY-MM-DD`, `YYYYMMDD` or
  `YYYYMM`; the last two added in issue #302), else the file's
  last-modified date from the listing (WebDAV HTTP date or S3 ISO
  timestamp), else today. Once Parcella has written the file, the date
  is in the header. A later edit in the cloud without a date keeps the
  date the note already has.
- **The `notes` table is the index**: title, date, category, tags and
  body are cached there for search, filter, sort and the REST API.
  `cloud_hash` (sha256 of the content last read or written) and
  `cloud_fingerprint` (`last_modified|size` from the listing) track
  what the cache is based on.
- **Save = write the file first.** If the upload fails, nothing is
  saved (502 / form re-shown with the text). Before writing, the
  current file is downloaded and its hash compared with the hash the
  editor was opened with (`base_hash`): if it differs, someone changed
  the file meanwhile -- the cloud version is loaded into the index, the
  save is refused (409), and the form shows the cloud version next to
  the user's kept text. Saving again (now with the new hash) overwrites
  deliberately. Hash, not timestamp: works the same on WebDAV and S3,
  and an unchanged re-upload isn't a conflict.
- **Pull (`sync_from_cloud`)**: the list page syncs at most once a
  minute per process, "Sync" forces it, opening/editing a note
  re-reads that one file. New file -> new note; changed fingerprint ->
  download, and if the hash differs, re-parse; file gone -> note
  soft-deleted (ADR 0005), keeping its file name; a file whose `id`
  matches a note whose own file is gone -> that note, renamed (or
  restored). A file copied in the cloud (same `id`, original still
  there) becomes a new note. A failed *listing* changes nothing, so a
  wrong or unreachable folder can't "delete" every note.
- **Without a notes folder**, the table is the note. Saves set
  `cloud_dirty`, deletes of a note that had a file set
  `cloud_delete_pending`. Once a folder is (re)configured, the next
  sync pushes dirty notes and deletes pending files -- unless the file
  changed in the cloud in the meantime. Then the cloud wins (it's the
  master), and the local version is saved as a separate note "(conflict
  copy)" with its own file, so nothing is lost silently. A pending
  delete of a file edited in the cloud meanwhile brings the note back.
- **Deleting a note deletes its file.** Leaving it would re-import the
  note on the next sync. This extends `delete_file` (until now only
  used by scheduled backups for their own files, ADR 0055) to the notes
  folder -- again only files Parcella itself manages there.
- **Rendering**: Markdown -> HTML through the same bleach pipeline as
  announcements, plus tables. The editor's preview is rendered by the
  server (`POST /notes/preview`), not EasyMDE's own renderer, because a
  note can come from a file anyone with cloud access wrote.

## Rejected

- **Database as master, cloud as a write-only mirror**: simpler, but
  edits made in the cloud would be silently overwritten by the next
  save in Parcella -- the opposite of what was asked.
- **Locking a note while it's edited**: there's no lock the cloud
  editors would respect; optimistic concurrency with a hash is the only
  check both sides honour.
- **Merging both versions automatically** (three-way merge): wrong
  merges in meeting minutes are worse than an explicit conflict.
- **A background sync loop**: a sync on use is enough for the volume
  (dozens to hundreds of notes per club), and avoids polling the
  club's cloud all day.

## Consequences / known gaps

- Unknown front-matter keys (e.g. Obsidian `aliases`) are dropped when
  Parcella rewrites a file.
- Moving a file leaves its old folder behind, even when empty (the
  storage interface has no folder delete).
- Attachments/images are links; nothing is uploaded with a note.
- Switching the notes folder hides notes whose files aren't in the new
  folder (soft delete); switching back restores them via their `id`.
- Sync cost: one listing per sync plus a download per changed file.
  Servers that report neither `last_modified` nor size get every file
  downloaded and hash-compared on each sync.
