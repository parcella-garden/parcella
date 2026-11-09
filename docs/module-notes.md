# Notes module

Markdown notes for general meetings, board meetings, meetings with
externals and anything else (issue #286): written in Parcella with an
editor and live preview, filed under one category and any number of
tags from the club taxonomy, searchable, filterable and sortable. With
a notes folder in the connected cloud storage, each note is a `.md`
file there, and that file is the master. Later part of the knowledge
base (#285).

Module flag `notes`, on by default: internal data, no public endpoint,
and the cloud part needs the off-by-default `cloud_storage` module
anyway. Permission module `notes` in the group matrix: read (list,
view, download, sync), write (create, edit, add/rename/translate
categories and tags), delete (delete notes and terms). ADMIN/BOARD
have all three, as everywhere.

## Data model

```
taxonomy_categories  -- club-wide categories (ADR 0122), seeded with four
taxonomy_tags        -- club-wide tags (ADR 0122)
notes                -- one row per note; the index of its cloud file
note_tag_links       -- note <-> tag
```

**`Note`**: `title`, `note_date` (the day the meeting was, not when the
note was written; that's `created_at`/`updated_at`; date only, no time
of day), `category_id`, `body_markdown`, `source_url` (the web page the
note is about: a bookmark is a note with a source, ADR 0125),
`created_by`/`updated_by`, `deleted_at` (soft delete, ADR 0005). The
`cloud_*` columns track the file: `cloud_filename`, `cloud_hash`
(sha256 of the content last read/written, the conflict token),
`cloud_fingerprint` (listing's `last_modified|size`), `cloud_synced_at`,
`cloud_dirty` (saved while no folder was set up: push later),
`cloud_delete_pending` (deleted while no folder was set up: delete the
file later). A partial unique index keeps one live note per file name.

**`TaxonomyCategory` / `TaxonomyTag`**: `name` plus per-language
`translations`, exactly like the member/contact tag pools (ADR 0098,
`app/tag_translations.py`) -- but club-wide, see ADR 0122 for why.

## Code

- `app/note_files.py` -- the file format: render/parse front matter,
  file names, hashes, `clean_source_url()` (http/https only). Pure, no I/O.
- `app/bookmark_import.py` -- parser for the standard bookmark export
  file (Netscape HTML). Pure, no I/O, never fetches a page.
- `app/services/notes.py` -- taxonomy CRUD, `NoteFilter`
  (search/filter/sort), create/update/delete, `refresh_note`,
  `sync_from_cloud`. Shared by both routers (ADR 0070).
- `app/routers/notes.py` -- web UI under `/notes` (list, detail, form,
  `.md` download, `/notes/taxonomy`, `POST /notes/preview`,
  `POST /notes/sync`, `/notes/import/bookmarks` with `/preview` and
  `/finalize`).
- `app/routers/api_notes.py` -- REST API under `/api/v1/notes`
  (list with the same filters, CRUD, categories, tags, sync). `PUT`
  takes an optional `base_hash`; a changed cloud file is a 409, an
  unwritable cloud a 502.
- Notes folder setting: Admin -> Integrations -> Cloud storage,
  `POST /admin/integrations/nextcloud/notes-folder`, ClubSetting
  `notes_cloud_folder`.

## Key decisions

- **The cloud file is the master** when a folder is set: ADR 0123 has
  the save/conflict/sync rules and the rejected alternatives.
- **One club-wide taxonomy** instead of a per-module tag pool: ADR 0122.
- **Subfolders = categories**, both directions: the first folder level
  below the notes folder is a note's category, saving with another
  category moves the file, deeper folders are kept (ADR 0123).
- **Date**: header, else file name prefix, else the file's own
  last-modified date -- an imported note never gets the import day.
  The prefix may be `2026-11-08`, `20261108` or month-only `202506`
  (the 1st of that month), see `date_from_filename()` in
  `app/note_files.py`. Only `YYYY-MM-DD` was read at first (issue
  #302), and the fallback bit hard: a copy made in Nextcloud keeps the
  original's last-modified time, so a protocol copied from a template
  got the *template's* date and sank out of sight in the date-sorted
  list. Migration 0119 cleared the stored hashes once so the next sync
  re-read every file with the new rule. It also set the one-time
  ClubSetting `notes_redate_import_day_pending`: that sync moved notes
  with no date of their own that were still on the day they were
  imported (the very first imports had no last-modified fallback yet)
  to the file's last-modified date, then removed the setting.
- **Search** is `ILIKE` over title, body and tag names (wildcards
  escaped), not Postgres full-text: language-agnostic across the seven
  UI languages, and fast enough for a club's notes. Revisit if the
  knowledge base (#285) needs ranking.
- **Rendering**: `render_markdown_to_html(..., allow_tables=True)`
  (bleach-sanitized, `app/announcement_utils.py`), wrapped in `Markup`
  in Python, never `|safe` in a template. The editor's preview calls the
  same sanitizer on the server.
- **Editor**: EasyMDE 2.18 (same as announcements), with its toggle
  between writing, preview and side-by-side -- the "switch" the issue
  asks for.

- **Bookmarks** (ADR 0125): a note with a `source:` header. The
  one-time import takes the export file of Nextcloud Bookmarks or any
  browser and creates one note per bookmark in the notes folder root,
  with no category. The date comes from `ADD_DATE`, the text from the
  description, and folders become extra tags. URLs that already have
  a note are skipped. Parcella never fetches the pages; summarizing
  them is for the external AI (#307).

## Known gaps

- No dashboard stat card: there's no "needs attention" number for notes.
- Unknown front-matter keys are dropped when Parcella rewrites a file;
  no attachments; emptied category folders stay behind (ADR 0123).
- The taxonomy page lives under `/notes` until the knowledge base (#285)
  gives it a neutral home.
- Not yet on the website: publishing notes (or knowledge base articles)
  is #285's job.
