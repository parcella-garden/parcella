# Notes

Minutes of general meetings, board meetings, meetings with outside
people, and anything else worth writing down. Notes are written in
Markdown, filed under a category and tags, and can be searched,
filtered and sorted. If your club uses a cloud storage, every note can
live there as a `.md` file that you can also open and edit in the cloud.

!!! info "Who can use this"
    - The module switch is **Notes** under **Administration → Turning
      modules on and off**. It is **on** by default.
    - The **Board** and **Administrator** roles, and members of a group
      with **Full access to every module**, can do everything.
    - Everyone else needs the **Notes** permission in one of their
      [groups](../administration/groups.md):
        - *read*: see the list and notes, download them, run **Sync**;
        - *write*: create and edit notes, import bookmarks, add, rename
          and translate categories and tags;
        - *delete*: delete notes, categories and tags.
    - Storing notes in the cloud also needs the **Cloud storage** module
      and a notes folder, see [Notes in the cloud](#notes-in-the-cloud).

## Note list

![Note list](../assets/screenshots/notes/list.png)

Open **Notes** in the menu.

### Buttons at the top

| Button | What it does |
|---|---|
| **Sync** | Only shown when a notes folder is set up. Reads changes from the cloud folder now (see [Notes in the cloud](#notes-in-the-cloud)). |
| **Categories & tags** | Opens [Categories & tags](#categories-tags). |
| **Import bookmarks** | Opens [Import bookmarks](#import-bookmarks). Needs *write*. |
| **New note** | Opens an empty [note form](#writing-a-note). Needs *write*. |

### Search and filters

| Field / button | What it does |
|---|---|
| **Search** | Searches the title, the text and the tag names. Upper/lower case doesn't matter. |
| **Category** | **All**, **No category**, or one category. |
| **Tags** | **All** or one tag. |
| **From** / **To** | Only notes whose date falls in this range. |
| **Sort by** | **Date, newest first** (default), **Date, oldest first**, **Title**, **Last changed**. |
| **Apply** | Applies search, filters and sort. |
| **Reset** | Shown once something is set. Back to all notes, newest first. |

### Columns

| Column | What it shows |
|---|---|
| **Date** | The day the note is about (for minutes: the day of the meeting). |
| **Title** | Linked to the note. An arrow icon opens the note's source link in a new tab (bookmarks). An orange cloud icon means **Not yet saved to the cloud**. |
| **Category** | Click to filter the list by it. |
| **Tags** | Click one to filter the list by it. |
| **Changed** | When the note was last saved (hidden on small screens). |

When the list is empty it says **No notes yet.**, or
**No notes match these filters.** when a filter is set.

## Reading a note

![A note](../assets/screenshots/notes/detail.png)

Click a note's title. You see the title, the date, category and tags
(each clickable to filter the list), the **Source (link)** if it is a
bookmark, and the formatted text. The footer shows who created and who
last changed the note, and, with a cloud folder, the note's file path.

| Button | What it does |
|---|---|
| **All notes** | Back to the list. |
| **Download .md** | Downloads the note as a Markdown file, with title, date, category and tags in a header at the top. |
| **Download PDF** | Downloads the note as a PDF with your club's letterhead. Pictures that are only linked from the web are left out. |
| **Edit** | Opens the form. Needs *write*. |
| **Delete note** | Needs *delete*. Asks **Delete this note? Its file in the cloud is deleted too.** |

Opening a note re-reads its file from the cloud first, so you always
see the current text. If that fails, the page shows **Could not read the
cloud file, showing the last synced version: ...** with the reason.

## Writing a note

![Note form](../assets/screenshots/notes/form.png)

**New note** or **Edit** opens the form (**New note** / **Edit note**).

| Field / button | What it does |
|---|---|
| **Title** | Required, up to 255 characters. |
| **Date** | Required. The day the note is about, not the day you write it. |
| **Category** | **No category** or one of the club's categories. |
| **Tags** | Tick existing tags. |
| **New tags, comma-separated** | Type new tags, separated by commas. They are created when you save and added to the club's tag list. |
| **Source (link)** | Optional: the web page this note is about. A note with a source is a bookmark. Must start with `http://` or `https://`. |
| **Note** | The text, in Markdown. With a cloud folder, the box says where the file is saved. |
| **Save** | Saves the note. |
| **Cancel** | Back without saving. |

The editor has a toolbar for bold, italic, strikethrough, heading,
quote, lists, code, link, table and horizontal line. The eye icon shows
a preview, the split icon shows text and preview side by side, the
arrows switch to full screen, and the question mark opens a Markdown
guide.

Possible messages: **Please enter a title.**, **Please enter a date.**,
**The source must be a web address starting with http:// or https://.**,
**This category doesn't exist (any more).**, **This tag doesn't exist
(any more).**

## Notes in the cloud

When the **Cloud storage** module is on and an administrator has set a
**Notes folder** under **Administration → Integrations → Cloud storage
(parcel documents, invoices, backups)**, every note's text is a
Markdown file in that folder.

!!! note "The file is the master copy of the text"
    The text in the cloud file wins. You and others can open and change
    these files with any editor in the cloud (Nextcloud Text, Obsidian
    and so on); the changes show up in Parcella. Title, date, category,
    tags and source live only in Parcella and are not written into the
    file.

How it works in practice:

- **Saving** writes the file first. If the file can't be written, the
  note isn't saved and you see **Not saved, the cloud file could not be
  written: ...** with your text still in the form. Changing only title,
  date, tags or source doesn't touch the file at all.
- **Subfolders are categories.** A note in the folder "Board meeting/"
  gets the category "Board meeting" (created if needed). Saving a note
  with another category moves its file into that category's folder.
  Notes without a category sit directly in the notes folder.
- **New files** are named after the date and title, e.g.
  `20261108-board-meeting.md`. Parcella never renames a file afterwards.
- **Files created in the cloud** become notes. Their date is taken from
  the start of the file name (`2026-11-08`, `20261108`, or `202506` for
  the 1st of that month), otherwise from the file's last-changed date.
- **Sync**: opening the note list reads changes from the cloud in the
  background, at most once a minute; they show up the next time you open
  the list. **Sync** does it now and reports **Synced: {n}
  new, {n} changed, {n} removed, {n} uploaded.** A file deleted in the
  cloud removes its note from the list.
- **Deleting** a note in Parcella deletes its file too. If that fails,
  the note is not deleted: **Not deleted, the cloud file could not be
  deleted: ...**
- **No folder yet?** Notes are kept in Parcella only and marked **Not
  yet saved to the cloud**. They are uploaded on the first sync after a
  folder has been set.

### When someone changed the file at the same time

If the file was changed in the cloud while you were editing, saving
stops with **Not saved: the note was changed in the cloud in the
meantime.** A yellow card **Changed in the cloud meanwhile** shows the
cloud version (with **Show as Markdown** for the raw text), and your own
text stays in the form below. Copy over what you need and click
**Save** again to overwrite the cloud version.

If a note was changed both in Parcella (while no folder was set) and in
the cloud, the sync keeps the cloud version and saves yours as a
separate note marked "conflict copy". **Sync** then says how many such
copies were made. Nothing is lost.

## Categories & tags

![Categories & tags](../assets/screenshots/notes/taxonomy.png)

**Categories & tags** shows the club's categories and tags. Each note
has one category and any number of tags. The same categories and tags
are meant to be used by the future knowledge base too. New
installations start with four categories: "General meeting", "Board
meeting", "Meeting with externals" and "Other". **Notes** (top right)
takes you back.

The page has two cards, **Categories** and **Tags**, that work the same
way:

| Field / button | What it does |
|---|---|
| Name + tick button | Renames the category or tag. Needs *write*; otherwise the name is just shown. Renaming a category moves its notes' files into a folder with the new name on the next sync; the old, empty folder stays behind. |
| "{count} note(s)" | Opens the note list filtered by it. |
| Translate button | Opens the names per language. With *write* you can enter a name for each language Parcella supports and click **Save translations**; empty fields show the main name. |
| Bin button | Deletes the category or tag after **Delete "{name}"? Notes keep existing without it.** Needs *delete*. |
| **New category** / **New tag** + **Add** | Adds one. Needs *write*. |

## Import bookmarks

![Import bookmarks](../assets/screenshots/notes/import-bookmarks.png)

If your club collects useful links (suppliers, authorities, guides) in
Nextcloud Bookmarks or a browser, you can turn them into notes in one go.
Each bookmark becomes a note with the link as its source.

1. Export your bookmarks as an HTML file. Nextcloud Bookmarks and every
   browser can create one.
2. Click **Import bookmarks**, choose the file and click **Show preview**.
   Nothing is saved yet.
3. The preview says how many are "new", "already a note" (a note with the
   same link exists -- skipped) and "not a web link" (skipped). The table
   lists **Date**, **Title** (with link and description), **Tags** and
   **Status** for each bookmark.
4. Click **Import {count} bookmark(s)**, or **Choose another file**.

The new notes get no category; with a cloud folder they are saved in the
root of the notes folder. The bookmark's folders become tags, the
description becomes the text, and the date the bookmark was added becomes
the note's date. Parcella never opens the linked pages.

If the file contains no bookmarks: **No bookmarks found in this file.**

## Notes and AI assistants

An administrator can switch on the **MCP connector for AI clients**
module. An AI assistant such as Claude can then search, read and write
notes -- but only notes carrying the release tag (by default
`ki-freigegeben`). Every other note stays invisible to it. Notes the AI
writes are tagged (by default `ki-erstellt`) so you know what to review.
This is off by default, because it hands club notes to an outside
service.

<!-- TODO(verify): where the release and created tag names are configured in the UI (stored as club settings); and link to the API tokens page section on "MCP connector only" tokens. -->

## Related

- [Integrations](../administration/integrations.md) -- cloud storage and
  the notes folder.
- [API tokens](../administration/api-tokens.md)
- [Groups](../administration/groups.md) -- giving someone notes
  permissions.
- [Turning modules on and off](../administration/modules.md)
