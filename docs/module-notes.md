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

**`Note`**: `title`, `note_date` + optional `note_time` (club-local wall
clock: when the meeting was, not when the note was written; that's
`created_at`/`updated_at`), `category_id`, `body_markdown`,
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
  file names, hashes. Pure, no I/O.
- `app/services/notes.py` -- taxonomy CRUD, `NoteFilter`
  (search/filter/sort), create/update/delete, `refresh_note`,
  `sync_from_cloud`. Shared by both routers (ADR 0070).
- `app/routers/notes.py` -- web UI under `/notes` (list, detail, form,
  `.md` download, `/notes/taxonomy`, `POST /notes/preview`,
  `POST /notes/sync`).
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

## Known gaps

- No dashboard stat card: there's no "needs attention" number for notes.
- Unknown front-matter keys are dropped when Parcella rewrites a file;
  subfolders of the notes folder aren't read; no attachments (ADR 0123).
- The taxonomy page lives under `/notes` until the knowledge base (#285)
  gives it a neutral home.
- Not yet on the website: publishing notes (or knowledge base articles)
  is #285's job.
