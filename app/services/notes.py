"""
Notes (issue #286, docs/module-notes.md) and the club taxonomy they're
filed under (ADR 0122). Shared by the HTML router (app/routers/notes.py)
and the REST API (app/routers/api_notes.py), ADR 0070. Callers commit.

With cloud storage on and a notes folder set (ClubSetting
NOTES_FOLDER_SETTING), each note's text is a .md file there (ADR 0123),
and that file is the master for the text. Title, date, category, tags
and source live in the notes table only (ADR 0127); the file holds
nothing but the text, and its top folder is the category.

- a save that changes the text or the category writes the file first
  and refuses (NoteConflict) when it changed since the editor was
  opened -- compared by content hash, so it works the same on WebDAV
  and S3. A save that only changes other metadata doesn't touch the
  cloud at all;
- sync_from_cloud() pulls new, changed, renamed and deleted files into
  the notes table, and rewrites files that still carry a front-matter
  header (from before ADR 0127, or written by another tool) as text only;
- notes saved or deleted while the cloud wasn't set up are pushed (or
  their file deleted) on the next sync, unless the file changed in the
  meantime: the cloud then wins and the local version is kept as a
  separate "conflict copy" note, so nothing is lost silently.

Without a notes folder, the table is the note and nothing else happens.
"""
import asyncio
import logging
import time as time_module
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from typing import Dict, List, Optional, Sequence, Tuple, Type, Union

from sqlalchemy import Select, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.cloud_storage import CloudFileEntry, CloudStorageError, CloudStorageProvider, get_cloud_storage_provider
from app.i18n import load_current_language
from app.models import ClubSetting, Note, TaxonomyCategory, TaxonomyTag, User, new_uuid
from app.bookmark_import import Bookmark
from app.module_flags import load_module_flags
from app.note_files import (
    ParsedNote, clean_source_url, content_hash, date_from_last_modified, fingerprint, note_filename, parse_note_file,
    render_note_body,
)
from app.services.errors import ServiceError
from app.tag_translations import all_names, clean_translations, find_tag_by_name, tag_label

logger = logging.getLogger(__name__)

NOTES_FOLDER_SETTING = "notes_cloud_folder"
# Set once by migration 0119 (issue #302): the next full sync re-dates
# notes that got their import day as date (see _import_day_fix()).
REDATE_IMPORT_DAY_SETTING = "notes_redate_import_day_pending"
# Set once by migration 0122 (issue #311, ADR 0127): the next full sync
# reads every file and rewrites the ones with a header as text only.
STRIP_HEADERS_SETTING = "notes_strip_headers_pending"
TITLE_MAX_LENGTH = 255
TAXONOMY_NAME_MAX_LENGTH = 100
# The list page syncs at most this often on its own; "Sync now" forces it.
SYNC_MAX_AGE_SECONDS = 60

TaxonomyModel = Union[Type[TaxonomyCategory], Type[TaxonomyTag]]


# ---------------------------------------------------------------------------
# Taxonomy (ADR 0122)
# ---------------------------------------------------------------------------

def _clean_name(raw: str) -> str:
    name = " ".join((raw or "").split())
    if not name:
        raise ServiceError("taxonomy.errors.name_required")
    if len(name) > TAXONOMY_NAME_MAX_LENGTH:
        raise ServiceError("taxonomy.errors.name_too_long", max=TAXONOMY_NAME_MAX_LENGTH)
    return name


async def list_categories(db: AsyncSession) -> List[TaxonomyCategory]:
    return list((await db.scalars(select(TaxonomyCategory).order_by(TaxonomyCategory.name))).all())


async def list_tags(db: AsyncSession) -> List[TaxonomyTag]:
    return list((await db.scalars(select(TaxonomyTag).order_by(TaxonomyTag.name))).all())


async def _list(db: AsyncSession, model: TaxonomyModel) -> list:
    return await (list_categories(db) if model is TaxonomyCategory else list_tags(db))


async def get_or_create_term(db: AsyncSession, model: TaxonomyModel, raw_name: str):
    """The category/tag called `raw_name` in any language, or a new one.
    Used by the note form's "new tags" field and by the cloud import
    (a file may name a category nobody has created yet)."""
    name = _clean_name(raw_name)
    existing = find_tag_by_name(await _list(db, model), name)
    if existing is not None:
        return existing
    term = model(id=new_uuid(), name=name)
    db.add(term)
    await db.flush()
    return term


async def create_term(db: AsyncSession, model: TaxonomyModel, raw_name: str):
    name = _clean_name(raw_name)
    clash = find_tag_by_name(await _list(db, model), name)
    if clash is not None:
        raise ServiceError("taxonomy.errors.name_taken", http_status=409, name=clash.name)
    term = model(id=new_uuid(), name=name)
    db.add(term)
    await db.flush()
    return term


async def _move_category_files(db: AsyncSession, model: TaxonomyModel, term, deleting: bool = False) -> None:
    """A category is its notes' top folder (ADR 0123): after renaming,
    retranslating or deleting it, notes whose file no longer sits in a
    matching folder are pushed on the next sync, which moves the file.
    Tags aren't in the files any more (ADR 0127), so they change nothing
    there."""
    if model is not TaxonomyCategory:
        return
    await db.flush()
    notes = (await db.scalars(select(Note).where(
        Note.category_id == term.id, Note.deleted_at.is_(None), Note.cloud_filename.is_not(None),
    ))).all()
    for note in notes:
        if not _folder_matches(None if deleting else term, _top_folder(note.cloud_filename)):
            note.cloud_dirty = True


async def _notes_using(db: AsyncSession, model: TaxonomyModel, term_id: str) -> List[str]:
    if model is TaxonomyCategory:
        query = select(Note.id).where(Note.category_id == term_id)
    else:
        query = select(Note.id).where(Note.tags.any(TaxonomyTag.id == term_id))
    return list((await db.scalars(query.where(Note.deleted_at.is_(None)))).all())


async def rename_term(db: AsyncSession, model: TaxonomyModel, term, raw_name: str) -> None:
    name = _clean_name(raw_name)
    clash = find_tag_by_name([t for t in await _list(db, model) if t.id != term.id], name)
    if clash is not None:
        raise ServiceError("taxonomy.errors.name_taken", http_status=409, name=clash.name)
    term.name = name
    await _move_category_files(db, model, term)


async def set_term_translations(db: AsyncSession, model: TaxonomyModel, term, values: dict) -> None:
    term.translations = clean_translations(
        term, values, await _list(db, model),
        max_length=TAXONOMY_NAME_MAX_LENGTH, error_prefix="taxonomy.errors",
    ) or None
    await _move_category_files(db, model, term)


async def delete_term(db: AsyncSession, model: TaxonomyModel, term) -> None:
    """Notes keep existing: a deleted category leaves them uncategorised
    (FK SET NULL), a deleted tag just disappears from them."""
    await _move_category_files(db, model, term, deleting=True)
    await db.delete(term)
    await db.flush()


async def count_term_notes(db: AsyncSession, model: TaxonomyModel) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for term in await _list(db, model):
        counts[term.id] = len(await _notes_using(db, model, term.id))
    return counts


# ---------------------------------------------------------------------------
# Listing, searching, filtering, sorting
# ---------------------------------------------------------------------------

SORT_OPTIONS = ("date_desc", "date_asc", "title", "updated")


def note_load_options():
    return (
        selectinload(Note.category), selectinload(Note.tags),
        selectinload(Note.created_by), selectinload(Note.updated_by),
    )


@dataclass
class NoteFilter:
    search: str = ""
    category: str = ""
    tag: str = ""
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    sort: str = "date_desc"

    @classmethod
    def build(cls, search: str = "", category: str = "", tag: str = "", date_from: str = "",
              date_to: str = "", sort: str = "") -> "NoteFilter":
        def _date(value: str) -> Optional[date]:
            try:
                return date.fromisoformat(value) if value else None
            except ValueError:
                return None
        return cls(
            search=(search or "").strip()[:200], category=(category or "").strip(), tag=(tag or "").strip(),
            date_from=_date(date_from), date_to=_date(date_to),
            sort=sort if sort in SORT_OPTIONS else "date_desc",
        )

    @property
    def active(self) -> bool:
        return bool(self.search or self.category or self.tag or self.date_from or self.date_to)

    def apply(self) -> Select:
        query = select(Note).where(Note.deleted_at.is_(None))
        if self.search:
            # Escape LIKE wildcards: searching "100%" means the text.
            escaped = self.search.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
            pattern = f"%{escaped}%"
            query = query.where(or_(
                Note.title.ilike(pattern, escape="\\"),
                Note.body_markdown.ilike(pattern, escape="\\"),
                Note.source_url.ilike(pattern, escape="\\"),
                Note.tags.any(TaxonomyTag.name.ilike(pattern, escape="\\")),
            ))
        if self.category == "none":
            query = query.where(Note.category_id.is_(None))
        elif self.category:
            query = query.where(Note.category_id == self.category)
        if self.tag:
            query = query.where(Note.tags.any(TaxonomyTag.id == self.tag))
        if self.date_from:
            query = query.where(Note.note_date >= self.date_from)
        if self.date_to:
            query = query.where(Note.note_date <= self.date_to)
        order = {
            "date_desc": (Note.note_date.desc(), Note.title),
            "date_asc": (Note.note_date.asc(), Note.title),
            "title": (Note.title, Note.note_date.desc()),
            "updated": (Note.updated_at.desc(),),
        }[self.sort]
        return query.order_by(*order)


async def get_note(db: AsyncSession, note_id: str) -> Optional[Note]:
    return await db.scalar(
        select(Note).options(*note_load_options())
        .where(Note.id == note_id, Note.deleted_at.is_(None))
        .execution_options(populate_existing=True)
    )


# ---------------------------------------------------------------------------
# Cloud access
# ---------------------------------------------------------------------------

async def load_notes_folder(db: AsyncSession) -> Optional[str]:
    value = await db.scalar(select(ClubSetting.value).where(ClubSetting.key == NOTES_FOLDER_SETTING))
    return value or None


@dataclass
class NotesCloud:
    provider: CloudStorageProvider
    folder: str
    language: str

    async def aclose(self) -> None:
        await self.provider.aclose()


async def open_notes_cloud(db: AsyncSession) -> Optional[NotesCloud]:
    """The notes folder in the connected cloud storage, or None when
    notes live in the database only (cloud module off, no provider, or
    no folder set). Callers aclose() it."""
    folder = await load_notes_folder(db)
    if not folder:
        return None
    if not (await load_module_flags(db)).get("cloud_storage"):
        return None
    provider = await get_cloud_storage_provider(db)
    if provider is None:
        return None
    return NotesCloud(provider=provider, folder=folder, language=await load_current_language(db))


class NoteConflict(Exception):
    """The note's file changed in the cloud after the editor was opened.
    The note row already holds the cloud version; `cloud_hash` is the
    token to save over it deliberately."""

    def __init__(self, note: Note):
        self.note = note
        super().__init__("note changed in the cloud")


def _render(note: Note) -> bytes:
    """The note's file: its text only (ADR 0127)."""
    return render_note_body(note.body_markdown).encode("utf-8")


# --- Paths and category folders --------------------------------------------
#
# A note's cloud_filename is its path relative to the notes folder:
# "x.md" in the folder itself, "Vorstandssitzung/x.md" or
# "Vorstandssitzung/2026/x.md" below it. The FIRST folder level is the
# category, in both directions (ADR 0123): a file's folder sets its
# category (over any `category:` in its header), and a note saved with
# another category moves into that category's folder. Deeper folders are
# read and kept as they are, but mean nothing.

def _split(rel: str) -> Tuple[str, str]:
    """("Vorstandssitzung/2026", "x.md") for "Vorstandssitzung/2026/x.md"."""
    return tuple(rel.rsplit("/", 1)) if "/" in rel else ("", rel)  # type: ignore[return-value]


def _top_folder(rel: str) -> str:
    return rel.split("/", 1)[0] if "/" in rel else ""


def _dir_path(cloud: NotesCloud, folder: str) -> str:
    return f"{cloud.folder}/{folder}" if folder else cloud.folder


def _safe_folder_name(name: str) -> str:
    """A category name as one folder name: no separators, no "."/".."."""
    cleaned = " ".join(name.replace("/", "-").replace("\\", "-").split()).strip(" .")
    return cleaned or "Category"


def _folder_names(category: TaxonomyCategory) -> set:
    """Every folder name that means `category`, lowercased: its name and
    translations, as typed and as _safe_folder_name makes them."""
    names = all_names(category)
    return names | {_safe_folder_name(n).lower() for n in names}


def _folder_matches(category: Optional[TaxonomyCategory], top_folder: str) -> bool:
    if not top_folder:
        return category is None
    return category is not None and top_folder.lower() in _folder_names(category)


def _folder_for(category: Optional[TaxonomyCategory], top_folders: Sequence[str], language: str) -> str:
    """The top-level folder a note of `category` belongs in: an existing
    one that matches (any language), else one named in the club language."""
    if category is None:
        return ""
    names = _folder_names(category)
    for folder in top_folders:
        if folder.lower() in names:
            return folder
    return _safe_folder_name(tag_label(category, language))


async def _category_for_folder(db: AsyncSession, folder: str) -> TaxonomyCategory:
    for category in await list_categories(db):
        if folder.lower() in _folder_names(category):
            return category
    return await get_or_create_term(db, TaxonomyCategory, folder)


@dataclass
class CloudListing:
    files: Dict[str, CloudFileEntry]  # relative path -> entry, *.md only
    top_folders: List[str]


MAX_FOLDER_DEPTH = 8


async def _walk(cloud: NotesCloud) -> CloudListing:
    """Every .md file in the notes folder and its subfolders. Hidden
    entries (".something") are skipped. Raises CloudStorageError if any
    listing fails -- the sync then changes nothing."""
    files: Dict[str, CloudFileEntry] = {}
    top_folders: List[str] = []
    queue: List[Tuple[str, int]] = [("", 0)]
    while queue:
        folder, depth = queue.pop(0)
        for entry in await cloud.provider.list_files(_dir_path(cloud, folder)):
            name = entry.name or ""
            if not name or name.startswith(".") or "/" in name or "\\" in name:
                continue
            rel = f"{folder}/{name}" if folder else name
            if entry.is_directory:
                if depth == 0:
                    top_folders.append(name)
                if depth + 1 < MAX_FOLDER_DEPTH:
                    queue.append((rel, depth + 1))
            elif name.lower().endswith(".md"):
                files[rel] = entry
    return CloudListing(files=files, top_folders=top_folders)


async def _taken_in(db: AsyncSession, cloud: NotesCloud, folder: str, exclude_note_id: str) -> set:
    try:
        names = {e.name for e in await cloud.provider.list_files(_dir_path(cloud, folder)) if not e.is_directory}
    except CloudStorageError:
        names = set()  # a folder that doesn't exist yet
    for path in (await db.scalars(
        select(Note.cloud_filename).where(Note.cloud_filename.is_not(None), Note.id != exclude_note_id)
    )).all():
        path_folder, name = _split(path)
        if path_folder == folder:
            names.add(name)
    return names


async def _push(db: AsyncSession, cloud: NotesCloud, note: Note) -> Optional[str]:
    """Writes the note's file -- a new one, or into its category's folder
    if the category changed (upload there, then delete the old file).
    Returns the old path after a move. Raises CloudStorageError; the row
    is only marked clean once the upload went through."""
    content = _render(note)
    current = note.cloud_filename
    moved_from = None
    if not current or not _folder_matches(note.category, _top_folder(current)):
        top_folders = [e.name for e in await cloud.provider.list_files(cloud.folder) if e.is_directory]
        target = _folder_for(note.category, top_folders, cloud.language)
        if target and target not in top_folders:
            await cloud.provider.create_folder(_dir_path(cloud, target))
        taken = await _taken_in(db, cloud, target, note.id)
        keep = _split(current)[1] if current else ""
        name = keep if keep and keep.lower() not in {t.lower() for t in taken} else \
            note_filename(note.note_date, note.title, taken)
        note.cloud_filename = f"{target}/{name}" if target else name
        moved_from = current
    folder, name = _split(note.cloud_filename)
    try:
        await cloud.provider.upload_file(_dir_path(cloud, folder), name, content)
    except CloudStorageError:
        note.cloud_filename = current
        raise
    if moved_from:
        try:
            await _delete(cloud, moved_from)
        except CloudStorageError:
            # The old file can't go (locked in an editor, say): take the
            # new copy back and leave the note where it was, instead of
            # two files of one note -- the save is refused.
            try:
                await _delete(cloud, note.cloud_filename)
            except CloudStorageError as e:
                logger.warning("Notes: could not undo the move of %s: %s", moved_from, e)
            note.cloud_filename = current
            raise
    note.cloud_hash = content_hash(content)
    # Unknown until the next listing; that sync then sees the hash match
    # and just records the fingerprint, without re-importing.
    note.cloud_fingerprint = None
    note.cloud_synced_at = datetime.now(timezone.utc)
    note.cloud_dirty = False
    return moved_from


async def _download(cloud: NotesCloud, rel: str) -> Tuple[bytes, str]:
    folder, name = _split(rel)
    content = await cloud.provider.download_file(_dir_path(cloud, folder), name)
    return content, content_hash(content)


async def _delete(cloud: NotesCloud, rel: str) -> None:
    folder, name = _split(rel)
    await cloud.provider.delete_file(_dir_path(cloud, folder), name)


async def _apply_body(db: AsyncSession, note: Note, parsed: ParsedNote, rel: str) -> None:
    """A file already linked to `note` changed in the cloud: its text
    and its folder (the category) are taken over. Title, date, tags and
    source are Parcella's (ADR 0127) -- a header in the file is ignored
    and stripped on the next push."""
    note.body_markdown = parsed.body
    top_folder = _top_folder(rel)
    if top_folder:
        if not _folder_matches(note.category, top_folder):
            note.category = await _category_for_folder(db, top_folder)
    else:
        note.category = None
    if parsed.had_header:
        note.cloud_dirty = True


async def _adopt_file(db: AsyncSession, note: Note, parsed: ParsedNote, rel: str = "") -> None:
    """A file new to Parcella becomes `note`: its metadata comes from
    its header if it has one (an older Parcella file, Obsidian, ...),
    else its first heading, file name and folder. A header is stripped
    on the next push (ADR 0127)."""
    note.title = parsed.title or note.title or "Note"
    note.note_date = parsed.note_date or note.note_date or date.today()
    note.body_markdown = parsed.body
    note.source_url = parsed.source
    top_folder = _top_folder(rel)
    if top_folder:  # the folder wins over the header
        note.category = await _category_for_folder(db, top_folder)
    else:
        note.category = await get_or_create_term(db, TaxonomyCategory, parsed.category) if parsed.category else None
    tags = []
    for name in parsed.tags:
        tag = await get_or_create_term(db, TaxonomyTag, name)
        if tag not in tags:
            tags.append(tag)
    note.tags = tags
    if parsed.had_header:
        note.cloud_dirty = True


async def _reload(db: AsyncSession, note: Note) -> Note:
    """Loads a note's relationships (or makes sure they're loaded) before
    its tags are replaced -- assigning to an unloaded collection under
    asyncio is a MissingGreenlet."""
    await db.refresh(note, attribute_names=["category", "tags", "created_by", "updated_by"])
    return note


# ---------------------------------------------------------------------------
# Create / update / delete
# ---------------------------------------------------------------------------

@dataclass
class NoteInput:
    title: str
    note_date: Optional[date]
    category_id: str = ""
    tag_ids: List[str] = field(default_factory=list)
    new_tags: List[str] = field(default_factory=list)
    body_markdown: str = ""
    source_url: str = ""


async def _validated(db: AsyncSession, data: NoteInput) -> Tuple[str, date, Optional[TaxonomyCategory], List[TaxonomyTag]]:
    title = " ".join((data.title or "").split())
    if not title:
        raise ServiceError("notes.errors.title_required")
    if len(title) > TITLE_MAX_LENGTH:
        raise ServiceError("notes.errors.title_too_long", max=TITLE_MAX_LENGTH)
    if data.note_date is None:
        raise ServiceError("notes.errors.date_required")
    if (data.source_url or "").strip() and clean_source_url(data.source_url) is None:
        raise ServiceError("notes.errors.invalid_source_url")
    category = None
    if data.category_id:
        category = await db.get(TaxonomyCategory, data.category_id)
        if category is None:
            raise ServiceError("notes.errors.unknown_category")
    tags: List[TaxonomyTag] = []
    for tag_id in dict.fromkeys(data.tag_ids):
        tag = await db.get(TaxonomyTag, tag_id)
        if tag is None:
            raise ServiceError("notes.errors.unknown_tag")
        tags.append(tag)
    for name in data.new_tags:
        if not name.strip():
            continue
        tag = await get_or_create_term(db, TaxonomyTag, name)
        if tag not in tags:
            tags.append(tag)
    return title, data.note_date, category, tags


def _assign(note: Note, user: Optional[User], title: str, note_date: date, category, tags, data: NoteInput) -> None:
    note.title = title
    note.note_date = note_date
    note.category = category
    note.tags = sorted(tags, key=lambda t: t.name.lower())
    note.body_markdown = (data.body_markdown or "").replace("\r\n", "\n")
    note.source_url = clean_source_url(data.source_url)
    note.updated_by_user_id = user.id if user else None


async def create_note(db: AsyncSession, user: Optional[User], data: NoteInput) -> Note:
    """Raises ServiceError, or CloudStorageError when the cloud is set up
    but the file couldn't be written -- then nothing is saved."""
    title, note_date, category, tags = await _validated(db, data)
    # Fully built before it's added: a pending object's relationships
    # can be assigned without loading them first.
    note = Note(id=new_uuid(), created_by_user_id=user.id if user else None, tags=[])
    _assign(note, user, title, note_date, category, tags, data)
    db.add(note)
    cloud = await open_notes_cloud(db)
    if cloud is None:
        note.cloud_dirty = True  # pushed once a notes folder is set up
        await db.flush()
        return note
    try:
        await _push(db, cloud, note)
    finally:
        await cloud.aclose()
    await db.flush()
    return note


# ---------------------------------------------------------------------------
# Bookmark import (issue #305, ADR 0125): one note per bookmark, in the
# notes folder root (no category), its folders as extra tags.
# ---------------------------------------------------------------------------

BOOKMARK_NEW = "new"
BOOKMARK_EXISTS = "exists"
BOOKMARK_INVALID = "invalid"


async def classify_bookmarks(db: AsyncSession, bookmarks: Sequence[Bookmark]) -> List[Tuple[Bookmark, str]]:
    """Each bookmark with what the import would do with it: create a
    note, skip it because a live note already has that source URL (so
    re-running an import is safe), or skip it as not an http(s) link."""
    urls = [b.url for b in bookmarks if b.url]
    existing = set()
    if urls:
        existing = set((await db.scalars(
            select(Note.source_url).where(Note.deleted_at.is_(None), Note.source_url.in_(urls))
        )).all())
    result = []
    for bookmark in bookmarks:
        if not bookmark.url:
            result.append((bookmark, BOOKMARK_INVALID))
        elif bookmark.url in existing:
            result.append((bookmark, BOOKMARK_EXISTS))
        else:
            result.append((bookmark, BOOKMARK_NEW))
    return result


@dataclass
class BookmarkImportResult:
    imported: int = 0
    skipped_existing: int = 0
    skipped_invalid: int = 0
    failed: List[str] = field(default_factory=list)


async def import_bookmarks(db: AsyncSession, user: Optional[User], bookmarks: Sequence[Bookmark]) -> BookmarkImportResult:
    """Creates a note per new bookmark through create_note(), so each one
    is written to the cloud like a note saved by hand. A bookmark whose
    file can't be written is reported and leaves nothing behind (its own
    savepoint); the others still go through."""
    result = BookmarkImportResult()
    for bookmark, status_ in await classify_bookmarks(db, bookmarks):
        if status_ == BOOKMARK_INVALID:
            result.skipped_invalid += 1
            continue
        if status_ == BOOKMARK_EXISTS:
            result.skipped_existing += 1
            continue
        data = NoteInput(
            title=bookmark.title, note_date=bookmark.added or date.today(),
            body_markdown=bookmark.description, source_url=bookmark.url or "",
            new_tags=list(bookmark.tags),
        )
        try:
            async with db.begin_nested():
                await create_note(db, user, data)
        except (ServiceError, CloudStorageError) as e:
            result.failed.append(f"{bookmark.title}: {e}")
            continue
        result.imported += 1
    return result


async def refresh_note(db: AsyncSession, note: Note) -> Optional[str]:
    """Re-reads one note's file before it's shown or edited, so the page
    and the editor's conflict token are current. Returns an error
    message to show (the cached version is shown then), or None."""
    if not note.cloud_filename or note.cloud_dirty:
        return None
    cloud = await open_notes_cloud(db)
    if cloud is None:
        return None
    try:
        content, digest = await _download(cloud, note.cloud_filename)
    except CloudStorageError as e:
        return str(e)
    finally:
        await cloud.aclose()
    if digest != note.cloud_hash:
        parsed = parse_note_file(content, note.cloud_filename)
        if parsed.had_header and await db.get(ClubSetting, STRIP_HEADERS_SETTING) is not None:
            # Before the one-time strip (migration 0122) the header still
            # counts, as it does for that sync.
            await _adopt_file(db, note, parsed, note.cloud_filename)
        else:
            await _apply_body(db, note, parsed, note.cloud_filename)
        note.cloud_hash = digest
        note.cloud_fingerprint = None
        note.cloud_synced_at = datetime.now(timezone.utc)
        await db.flush()
    return None


def _file_affected(note: Note, category: Optional[TaxonomyCategory], data: NoteInput) -> bool:
    """Whether saving `data` changes the note's file: its text, or its
    folder (the category). Title, date, tags and source aren't in the
    file (ADR 0127), so changing only those never touches the cloud --
    which also means a file locked in a cloud editor can't block them."""
    if not note.cloud_filename or note.cloud_dirty:
        return True
    if render_note_body(data.body_markdown or "") != render_note_body(note.body_markdown or ""):
        return True
    return not _folder_matches(category, _top_folder(note.cloud_filename))


async def update_note(db: AsyncSession, note: Note, user: Optional[User], data: NoteInput, base_hash: str = "") -> Note:
    """`base_hash` is the cloud_hash the editor was opened with. If the
    save changes the file and the file's content differs from it now,
    the cloud version is loaded into the note and NoteConflict raised
    instead of overwriting it -- checked before validating, so a
    conflicting save creates no new tags."""
    cloud = await open_notes_cloud(db)
    if cloud is None:
        title, note_date, category, tags = await _validated(db, data)
        _assign(note, user, title, note_date, category, tags, data)
        note.cloud_dirty = True
        await db.flush()
        return note
    try:
        category = await db.get(TaxonomyCategory, data.category_id) if data.category_id else None
        if not _file_affected(note, category, data):
            title, note_date, category, tags = await _validated(db, data)
            _assign(note, user, title, note_date, category, tags, data)
            await db.flush()
            return note
        if note.cloud_filename:
            try:
                content, digest = await _download(cloud, note.cloud_filename)
            except CloudStorageError:
                content, digest = None, None  # file gone: saving recreates it
            if digest is not None and digest != (base_hash or note.cloud_hash):
                if digest != note.cloud_hash:
                    await _apply_body(db, note, parse_note_file(content, note.cloud_filename), note.cloud_filename)
                    note.cloud_hash = digest
                    note.cloud_fingerprint = None
                    await db.flush()
                raise NoteConflict(note)
        title, note_date, category, tags = await _validated(db, data)
        _assign(note, user, title, note_date, category, tags, data)
        await _push(db, cloud, note)
    finally:
        await cloud.aclose()
    await db.flush()
    return note


async def delete_note(db: AsyncSession, note: Note) -> None:
    """Soft delete (ADR 0005). The cloud file goes too: it's the master,
    and leaving it would import the note right back on the next sync."""
    if note.cloud_filename:
        cloud = await open_notes_cloud(db)
        if cloud is None:
            note.cloud_delete_pending = True
        else:
            try:
                await _delete(cloud, note.cloud_filename)
            finally:
                await cloud.aclose()
    note.deleted_at = datetime.now(timezone.utc)
    await db.flush()


# ---------------------------------------------------------------------------
# Sync (ADR 0123)
# ---------------------------------------------------------------------------

@dataclass
class SyncResult:
    ran: bool = False
    imported: int = 0
    updated: int = 0
    removed: int = 0
    pushed: int = 0
    conflicts: int = 0
    errors: List[str] = field(default_factory=list)


_sync_lock = asyncio.Lock()
_last_sync_monotonic: Optional[float] = None


def reset_sync_throttle() -> None:
    global _last_sync_monotonic
    _last_sync_monotonic = None


async def sync_from_cloud(db: AsyncSession, *, force: bool = False) -> SyncResult:
    """Brings the notes table in line with the notes folder. Throttled to
    once per SYNC_MAX_AGE_SECONDS per process unless `force`. A failed
    listing changes nothing (so a wrong folder can't "delete" every
    note); a failed single file is reported and skipped."""
    global _last_sync_monotonic
    result = SyncResult()
    now = time_module.monotonic()
    if not force and _last_sync_monotonic is not None and now - _last_sync_monotonic < SYNC_MAX_AGE_SECONDS:
        return result
    async with _sync_lock:
        cloud = await open_notes_cloud(db)
        if cloud is None:
            return result
        _last_sync_monotonic = now
        result.ran = True
        try:
            await _sync(db, cloud, result)
        except CloudStorageError as e:
            result.errors.append(str(e))
        finally:
            await cloud.aclose()
        await db.flush()
    return result


def _was_import_day(note: Note) -> bool:
    """True if the note's date is the day its row was created -- what
    the very first notes imports (before the last-modified fallback)
    gave every file without a date of its own."""
    if note.created_at is None:
        return False
    created = note.created_at if note.created_at.tzinfo else note.created_at.replace(tzinfo=timezone.utc)
    return note.note_date in {created.astimezone(timezone.utc).date(), created.astimezone().date()}


async def _sync(db: AsyncSession, cloud: NotesCloud, result: SyncResult) -> None:
    files = (await _walk(cloud)).files
    redate_setting = await db.get(ClubSetting, REDATE_IMPORT_DAY_SETTING)
    strip_setting = await db.get(ClubSetting, STRIP_HEADERS_SETTING)
    notes = list((await db.scalars(
        select(Note).options(*note_load_options()).execution_options(populate_existing=True)
    )).all())
    handled: set = set()  # file names already in sync after steps 1-2

    # 1. Deleted while the cloud was off: delete the file, unless it was
    #    edited in the cloud since -- then the note comes back.
    for note in notes:
        if not note.cloud_delete_pending:
            continue
        note.cloud_delete_pending = False
        if note.cloud_filename not in files:
            continue
        try:
            content, digest = await _download(cloud, note.cloud_filename)
            if digest == note.cloud_hash:
                await _delete(cloud, note.cloud_filename)
                handled.add(note.cloud_filename)
                files.pop(note.cloud_filename, None)
            else:
                note.deleted_at = None  # step 3 pulls the cloud version in
        except CloudStorageError as e:
            note.cloud_delete_pending = True
            result.errors.append(f"{note.cloud_filename}: {e}")

    # 2. Saved while the cloud was off (or a taxonomy rename touched it).
    for note in notes:
        if note.deleted_at is not None or not note.cloud_dirty:
            continue
        try:
            if note.cloud_filename and note.cloud_filename in files:
                content, digest = await _download(cloud, note.cloud_filename)
                if digest != note.cloud_hash:
                    await _keep_conflict_copy(db, cloud, note)
                    note.cloud_dirty = False  # unless the file has a header to strip
                    await _apply_body(db, note, parse_note_file(content, note.cloud_filename), note.cloud_filename)
                    note.cloud_hash = digest
                    note.cloud_fingerprint = fingerprint(files[note.cloud_filename].last_modified,
                                                         files[note.cloud_filename].size)
                    result.conflicts += 1
                    handled.add(note.cloud_filename)
                    continue
            moved_from = await _push(db, cloud, note)
            if moved_from:
                files.pop(moved_from, None)
            handled.add(note.cloud_filename)
            result.pushed += 1
        except CloudStorageError as e:
            result.errors.append(f"{note.title}: {e}")

    # 3. Pull new, changed and renamed files. While the one-time header
    #    strip (ADR 0127) is pending, every file is read, not only the
    #    changed ones.
    by_filename = {n.cloud_filename: n for n in notes if n.deleted_at is None and n.cloud_filename}
    to_strip: List[Note] = []  # linked files that still carry a header
    for name, entry in files.items():
        if name in handled:
            continue
        current_fp = fingerprint(entry.last_modified, entry.size)
        note = by_filename.get(name)
        if (note is not None and current_fp and note.cloud_fingerprint == current_fp
                and strip_setting is None):
            continue
        try:
            content, digest = await _download(cloud, name)
        except CloudStorageError as e:
            result.errors.append(f"{name}: {e}")
            continue
        parsed = parse_note_file(content, name)
        if note is not None and digest == note.cloud_hash:
            note.cloud_fingerprint = current_fp
            if parsed.had_header and note not in to_strip:
                to_strip.append(note)
            continue
        if (redate_setting is not None and note is not None and parsed.note_date is None
                and _was_import_day(note)):
            # One-time fix (issue #302): no date in the header or the file
            # name, and the note still has the day it was imported -- use
            # the file's own date, as an import does today.
            parsed.note_date = date_from_last_modified(entry.last_modified) or None
        if note is None:
            relinked = _relink_target(notes, files, parsed, content, digest)
            if relinked is not None:
                # A renamed or moved (or restored) file: same note, new
                # place -- its metadata stays, its folder sets the category.
                note = relinked
                note.cloud_filename = name
                note.deleted_at = None
                note.cloud_delete_pending = False
                by_filename[name] = note
            else:
                # The day the note is about: its header or file name, else
                # the file's own date -- never the day it was imported.
                note_date = parsed.note_date or date_from_last_modified(entry.last_modified) or date.today()
                note = Note(id=new_uuid(), title=parsed.title, note_date=note_date,
                            body_markdown="", cloud_filename=name)
                db.add(note)
                await db.flush()
                await _reload(db, note)
                by_filename[name] = note
                result.imported += 1
                note.cloud_dirty = False
                await _adopt_file(db, note, parsed, name)
                note.cloud_hash, note.cloud_fingerprint = digest, current_fp
                note.cloud_synced_at = datetime.now(timezone.utc)
                if note.cloud_dirty:
                    to_strip.append(note)
                continue
        note.cloud_dirty = False
        if redate_setting is not None or (strip_setting is not None and parsed.had_header):
            # A one-time full re-read (migrations 0119 and 0122): the file
            # is parsed as if new, so a file-name date -- or header edits
            # made in the cloud since the previous sync -- are taken over
            # once before the header goes.
            await _adopt_file(db, note, parsed, name)
        else:
            await _apply_body(db, note, parsed, name)
        note.cloud_hash, note.cloud_fingerprint = digest, current_fp
        note.cloud_synced_at = datetime.now(timezone.utc)
        if note.cloud_dirty:
            to_strip.append(note)
        result.updated += 1

    # 4. Files deleted in the cloud: soft-delete their notes. The file
    #    name stays on the row, so restoring the file relinks it.
    for note in notes:
        if (note.deleted_at is None and note.cloud_filename and not note.cloud_dirty
                and note.cloud_filename not in files and note.cloud_filename not in handled):
            note.deleted_at = datetime.now(timezone.utc)
            result.removed += 1

    # 5. Files that still carry a front-matter header are rewritten as
    #    text only (ADR 0127): their content was read a moment ago, so
    #    the push goes over exactly that version. A failure (the file is
    #    locked in an editor, say) leaves the note dirty for the next sync.
    for note in to_strip:
        if note.deleted_at is not None:
            continue
        try:
            await _push(db, cloud, note)
        except CloudStorageError as e:
            note.cloud_dirty = True
            result.errors.append(f"{note.cloud_filename}: {e}")

    # The one-time re-dating and header strip are done once a sync read
    # every file without an error; otherwise the next sync retries the
    # files that failed (their hash is still unset, so they're re-read).
    if redate_setting is not None and not result.errors:
        await db.delete(redate_setting)
    if strip_setting is not None and not result.errors:
        await db.delete(strip_setting)


def _relink_target(notes: Sequence[Note], files: Dict[str, CloudFileEntry], parsed: ParsedNote,
                   content: bytes, digest: str) -> Optional[Note]:
    """The note a file new to this folder really belongs to, if it was
    renamed or moved in the cloud: the note its `id` header names (files
    from before ADR 0127), else the one note whose last-known content is
    exactly this file's and whose own file is gone. Not when that note's
    file is still there -- that's a copy -- and not by content when
    several notes or an empty file would match: guessing wrong would
    hand one note's metadata to another."""
    def file_gone(note: Note) -> bool:
        return note.deleted_at is not None or note.cloud_filename not in files

    if parsed.note_id:
        for note in notes:
            if note.id == parsed.note_id:
                return note if file_gone(note) else None
    if not content.strip():
        return None
    matches = [n for n in notes if n.cloud_hash == digest and n.cloud_filename and file_gone(n)
               and not n.cloud_delete_pending]
    return matches[0] if len(matches) == 1 else None


async def _keep_conflict_copy(db: AsyncSession, cloud: NotesCloud, note: Note) -> None:
    """The local version of a note whose file changed in the cloud while
    the local edit waited to be pushed: saved as a new note (and file)
    so neither version is lost (ADR 0123)."""
    copy = Note(
        id=new_uuid(), title=note.title[:TITLE_MAX_LENGTH - 20] + " (conflict copy)",
        note_date=note.note_date, body_markdown=note.body_markdown, source_url=note.source_url,
        created_by_user_id=note.updated_by_user_id or note.created_by_user_id,
        updated_by_user_id=note.updated_by_user_id,
    )
    db.add(copy)
    await db.flush()
    await _reload(db, copy)
    copy.category = note.category
    copy.tags = list(note.tags)
    await _push(db, cloud, copy)
