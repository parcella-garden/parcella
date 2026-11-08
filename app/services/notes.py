"""
Notes (issue #286, docs/module-notes.md) and the club taxonomy they're
filed under (ADR 0122). Shared by the HTML router (app/routers/notes.py)
and the REST API (app/routers/api_notes.py), ADR 0070. Callers commit.

The cloud file is the master (ADR 0123). With cloud storage on and a
notes folder set (ClubSetting NOTES_FOLDER_SETTING):

- every save writes the note's .md file first and refuses (NoteConflict)
  when that file changed since the editor was opened -- compared by
  content hash, so it works the same on WebDAV and S3;
- sync_from_cloud() pulls new, changed, renamed and deleted files into
  the notes table, which is then only Parcella's searchable index;
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

from app.cloud_storage import CloudStorageError, CloudStorageProvider, get_cloud_storage_provider
from app.i18n import load_current_language
from app.models import ClubSetting, Note, TaxonomyCategory, TaxonomyTag, User, new_uuid
from app.module_flags import load_module_flags
from app.note_files import (
    ParsedNote, content_hash, fingerprint, note_filename, parse_note_file, render_note_file,
)
from app.services.errors import ServiceError
from app.tag_translations import clean_translations, find_tag_by_name, tag_label

logger = logging.getLogger(__name__)

NOTES_FOLDER_SETTING = "notes_cloud_folder"
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


async def _mark_notes_dirty(db: AsyncSession, note_ids: Sequence[str]) -> None:
    """A term's name is written into its notes' files: renaming or
    deleting it changes their content, so they're pushed on the next
    sync (ADR 0123)."""
    if not note_ids:
        return
    for note in (await db.scalars(select(Note).where(Note.id.in_(note_ids), Note.deleted_at.is_(None)))).all():
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
    await _mark_notes_dirty(db, await _notes_using(db, model, term.id))


async def set_term_translations(db: AsyncSession, model: TaxonomyModel, term, values: dict) -> None:
    term.translations = clean_translations(
        term, values, await _list(db, model),
        max_length=TAXONOMY_NAME_MAX_LENGTH, error_prefix="taxonomy.errors",
    ) or None
    await _mark_notes_dirty(db, await _notes_using(db, model, term.id))


async def delete_term(db: AsyncSession, model: TaxonomyModel, term) -> None:
    """Notes keep existing: a deleted category leaves them uncategorised
    (FK SET NULL), a deleted tag just disappears from them."""
    await _mark_notes_dirty(db, await _notes_using(db, model, term.id))
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


def _render(note: Note, language: str) -> bytes:
    return render_note_file(
        note_id=note.id, title=note.title, note_date=note.note_date,
        category=tag_label(note.category, language) if note.category else None,
        tags=[tag_label(t, language) for t in note.tags],
        body=note.body_markdown,
    ).encode("utf-8")


async def _taken_filenames(db: AsyncSession, cloud: NotesCloud, exclude_note_id: str = "") -> set:
    names = {e.name for e in await cloud.provider.list_files(cloud.folder) if not e.is_directory}
    names |= set((await db.scalars(
        select(Note.cloud_filename).where(Note.cloud_filename.is_not(None), Note.id != exclude_note_id)
    )).all())
    return names


async def _push(db: AsyncSession, cloud: NotesCloud, note: Note) -> None:
    """Writes the note's file (a new one if it has none yet). Raises
    CloudStorageError; the row is only marked clean once the upload
    went through."""
    content = _render(note, cloud.language)
    if not note.cloud_filename:
        note.cloud_filename = note_filename(
            note.note_date, note.title, await _taken_filenames(db, cloud, exclude_note_id=note.id),
        )
    await cloud.provider.upload_file(cloud.folder, note.cloud_filename, content)
    note.cloud_hash = content_hash(content)
    # Unknown until the next listing; that sync then sees the hash match
    # and just records the fingerprint, without re-importing.
    note.cloud_fingerprint = None
    note.cloud_synced_at = datetime.now(timezone.utc)
    note.cloud_dirty = False


async def _download(cloud: NotesCloud, filename: str) -> Tuple[bytes, str]:
    content = await cloud.provider.download_file(cloud.folder, filename)
    return content, content_hash(content)


async def _apply_parsed(db: AsyncSession, note: Note, parsed: ParsedNote) -> None:
    note.title = parsed.title or note.title or "Note"
    note.note_date = parsed.note_date or note.note_date or date.today()
    note.body_markdown = parsed.body
    note.category = await get_or_create_term(db, TaxonomyCategory, parsed.category) if parsed.category else None
    tags = []
    for name in parsed.tags:
        tag = await get_or_create_term(db, TaxonomyTag, name)
        if tag not in tags:
            tags.append(tag)
    note.tags = tags


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


async def _validated(db: AsyncSession, data: NoteInput) -> Tuple[str, date, Optional[TaxonomyCategory], List[TaxonomyTag]]:
    title = " ".join((data.title or "").split())
    if not title:
        raise ServiceError("notes.errors.title_required")
    if len(title) > TITLE_MAX_LENGTH:
        raise ServiceError("notes.errors.title_too_long", max=TITLE_MAX_LENGTH)
    if data.note_date is None:
        raise ServiceError("notes.errors.date_required")
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
        await _apply_parsed(db, note, parse_note_file(content, note.cloud_filename))
        note.cloud_hash = digest
        note.cloud_fingerprint = None
        note.cloud_synced_at = datetime.now(timezone.utc)
        await db.flush()
    return None


async def update_note(db: AsyncSession, note: Note, user: Optional[User], data: NoteInput, base_hash: str = "") -> Note:
    """`base_hash` is the cloud_hash the editor was opened with. If the
    file's content differs from it now, the cloud version is loaded into
    the note and NoteConflict raised instead of overwriting it -- checked
    before validating, so a conflicting save creates no new tags."""
    cloud = await open_notes_cloud(db)
    if cloud is None:
        title, note_date, category, tags = await _validated(db, data)
        _assign(note, user, title, note_date, category, tags, data)
        note.cloud_dirty = True
        await db.flush()
        return note
    try:
        if note.cloud_filename and not note.cloud_dirty:
            try:
                content, digest = await _download(cloud, note.cloud_filename)
            except CloudStorageError:
                content, digest = None, None  # file gone: saving recreates it
            if digest is not None and digest != (base_hash or note.cloud_hash):
                if digest != note.cloud_hash:
                    await _apply_parsed(db, note, parse_note_file(content, note.cloud_filename))
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
                await cloud.provider.delete_file(cloud.folder, note.cloud_filename)
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


async def _sync(db: AsyncSession, cloud: NotesCloud, result: SyncResult) -> None:
    entries = await cloud.provider.list_files(cloud.folder)
    files = {e.name: e for e in entries if not e.is_directory and e.name.lower().endswith(".md")}
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
                await cloud.provider.delete_file(cloud.folder, note.cloud_filename)
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
                    await _apply_parsed(db, note, parse_note_file(content, note.cloud_filename))
                    note.cloud_hash = digest
                    note.cloud_fingerprint = fingerprint(files[note.cloud_filename].last_modified,
                                                         files[note.cloud_filename].size)
                    note.cloud_dirty = False
                    result.conflicts += 1
                    handled.add(note.cloud_filename)
                    continue
            await _push(db, cloud, note)
            handled.add(note.cloud_filename)
            result.pushed += 1
        except CloudStorageError as e:
            result.errors.append(f"{note.title}: {e}")

    # 3. Pull new, changed and renamed files.
    by_filename = {n.cloud_filename: n for n in notes if n.deleted_at is None and n.cloud_filename}
    by_id = {n.id: n for n in notes}
    for name, entry in files.items():
        if name in handled:
            continue
        current_fp = fingerprint(entry.last_modified, entry.size)
        note = by_filename.get(name)
        if note is not None and current_fp and note.cloud_fingerprint == current_fp:
            continue
        try:
            content, digest = await _download(cloud, name)
        except CloudStorageError as e:
            result.errors.append(f"{name}: {e}")
            continue
        if note is not None and digest == note.cloud_hash:
            note.cloud_fingerprint = current_fp
            continue
        parsed = parse_note_file(content, name)
        if note is None:
            relinked = by_id.get(parsed.note_id or "")
            # A renamed (or restored) file: same note, new name. Not when
            # that note's own file is still there -- that's a copy.
            if relinked is not None and (relinked.deleted_at is not None or relinked.cloud_filename not in files):
                note = relinked
                note.cloud_filename = name
                note.deleted_at = None
                note.cloud_delete_pending = False
                by_filename[name] = note
            else:
                note = Note(id=new_uuid(), title=parsed.title, note_date=parsed.note_date or date.today(),
                            body_markdown="", cloud_filename=name)
                db.add(note)
                await db.flush()
                await _reload(db, note)
                by_filename[name] = note
                by_id[note.id] = note
                result.imported += 1
                note.cloud_dirty = False
                await _apply_parsed(db, note, parsed)
                note.cloud_hash, note.cloud_fingerprint = digest, current_fp
                note.cloud_synced_at = datetime.now(timezone.utc)
                continue
        await _apply_parsed(db, note, parsed)
        note.cloud_hash, note.cloud_fingerprint = digest, current_fp
        note.cloud_synced_at = datetime.now(timezone.utc)
        note.cloud_dirty = False
        result.updated += 1

    # 4. Files deleted in the cloud: soft-delete their notes. The file
    #    name stays on the row, so restoring the file relinks it.
    for note in notes:
        if (note.deleted_at is None and note.cloud_filename and not note.cloud_dirty
                and note.cloud_filename not in files and note.cloud_filename not in handled):
            note.deleted_at = datetime.now(timezone.utc)
            result.removed += 1


async def _keep_conflict_copy(db: AsyncSession, cloud: NotesCloud, note: Note) -> None:
    """The local version of a note whose file changed in the cloud while
    the local edit waited to be pushed: saved as a new note (and file)
    so neither version is lost (ADR 0123)."""
    copy = Note(
        id=new_uuid(), title=note.title[:TITLE_MAX_LENGTH - 20] + " (conflict copy)",
        note_date=note.note_date, body_markdown=note.body_markdown,
        created_by_user_id=note.updated_by_user_id or note.created_by_user_id,
        updated_by_user_id=note.updated_by_user_id,
    )
    db.add(copy)
    await db.flush()
    await _reload(db, copy)
    copy.category = note.category
    copy.tags = list(note.tags)
    await _push(db, cloud, copy)
