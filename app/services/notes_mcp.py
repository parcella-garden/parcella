"""
The notes knowledge base for AI clients over MCP (issue #307, ADR 0132).

Hard rule (kermie, 2026-11-08): no personal data goes to any AI. So this
module is deny-by-default: the AI sees only notes a person has released
for it with the release tag (ClubSetting `mcp_release_tag`, default
"ki-freigegeben"). Every tool goes through `_released()`; anything else
does not exist for the AI -- an unreleased note is "not found", even by
id, and is never matched by a search. Notes the AI creates are released
automatically and get the created tag (`mcp_created_tag`, default
"ki-erstellt"), as do notes it changes, so people see what to review.

What leaves Parcella is only what the AI needs: title, date, category,
tags, body, source, plus the note id and a version for the conflict
check. No author/user fields, no cloud file name (file names can contain
names), no member or parcel ids. Category and tag lists only show terms
used on released notes (a tag could be a name). There is no delete tool
(kermie): mistakes are undone via the cloud's file versions.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any, Dict, List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ClubSetting, Note, TaxonomyCategory, TaxonomyTag, User
from app.services.errors import ServiceError
from app.services.notes import (
    NoteConflict, NoteInput, create_note, get_note, note_load_options, sync_from_cloud, update_note,
)

RELEASE_TAG_KEY = "mcp_release_tag"
CREATED_TAG_KEY = "mcp_created_tag"
DEFAULT_RELEASE_TAG = "ki-freigegeben"
DEFAULT_CREATED_TAG = "ki-erstellt"

SEARCH_DEFAULT_LIMIT = 20
SEARCH_MAX_LIMIT = 50
EXCERPT_LENGTH = 300


class McpToolError(Exception):
    """A tool-level failure the AI should read (MCP `isError: true`),
    not a protocol error. The message is plain and never contains data
    from unreleased notes."""


@dataclass
class TagNames:
    release: str
    created: str


async def load_tag_names(db: AsyncSession) -> TagNames:
    rows = (await db.execute(
        select(ClubSetting).where(ClubSetting.key.in_([RELEASE_TAG_KEY, CREATED_TAG_KEY]))
    )).scalars().all()
    values = {r.key: (r.value or "").strip() for r in rows}
    return TagNames(
        release=values.get(RELEASE_TAG_KEY) or DEFAULT_RELEASE_TAG,
        created=values.get(CREATED_TAG_KEY) or DEFAULT_CREATED_TAG,
    )


def _released(tags: TagNames):
    """THE filter. Every query that hands notes to the AI starts here."""
    return select(Note).where(
        Note.deleted_at.is_(None),
        Note.tags.any(func.lower(TaxonomyTag.name) == tags.release.lower()),
    )


def _escape_like(text: str) -> str:
    return text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _note_out(note: Note, with_body: bool = True) -> Dict[str, Any]:
    out: Dict[str, Any] = {
        "id": note.id,
        "title": note.title,
        "date": note.note_date.isoformat(),
        "category": note.category.name if note.category else None,
        "tags": [t.name for t in note.tags],
        "source": note.source_url,
    }
    if with_body:
        out["body"] = note.body_markdown or ""
        # Opaque version for update_note's conflict check (the content hash
        # of the cloud file as last read; not personal data).
        out["version"] = note.cloud_hash or ""
    else:
        body = " ".join((note.body_markdown or "").split())
        out["excerpt"] = body[:EXCERPT_LENGTH] + (" …" if len(body) > EXCERPT_LENGTH else "")
    return out


def _parse_date(value: Any, field: str) -> Optional[date]:
    if value in (None, ""):
        return None
    try:
        return date.fromisoformat(str(value))
    except ValueError:
        raise McpToolError(f"'{field}' must be a date like 2026-11-15.")


def _str(args: Dict[str, Any], key: str, max_len: int = 100_000) -> Optional[str]:
    value = args.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise McpToolError(f"'{key}' must be a string.")
    return value[:max_len]


async def _sync(db: AsyncSession) -> None:
    """Same as the REST list: pull cloud changes first (throttled)."""
    await sync_from_cloud(db)
    await db.commit()


# ---------------------------------------------------------------------------
# Read tools
# ---------------------------------------------------------------------------

async def search_notes(db: AsyncSession, args: Dict[str, Any]) -> Dict[str, Any]:
    tags = await load_tag_names(db)
    await _sync(db)
    query = _released(tags)
    text = (_str(args, "query", 200) or "").strip()
    if text:
        pattern = f"%{_escape_like(text)}%"
        query = query.where(
            Note.title.ilike(pattern, escape="\\")
            | Note.body_markdown.ilike(pattern, escape="\\")
            | Note.source_url.ilike(pattern, escape="\\")
        )
    category = (_str(args, "category", 100) or "").strip()
    if category:
        query = query.where(Note.category.has(func.lower(TaxonomyCategory.name) == category.lower()))
    tag = (_str(args, "tag", 100) or "").strip()
    if tag:
        query = query.where(Note.tags.any(func.lower(TaxonomyTag.name) == tag.lower()))
    date_from = _parse_date(args.get("date_from"), "date_from")
    date_to = _parse_date(args.get("date_to"), "date_to")
    if date_from:
        query = query.where(Note.note_date >= date_from)
    if date_to:
        query = query.where(Note.note_date <= date_to)
    try:
        limit = int(args.get("limit") or SEARCH_DEFAULT_LIMIT)
    except (TypeError, ValueError):
        raise McpToolError("'limit' must be a number.")
    limit = max(1, min(limit, SEARCH_MAX_LIMIT))
    notes = (await db.scalars(
        query.options(*note_load_options()).order_by(Note.note_date.desc(), Note.title).limit(limit)
    )).all()
    return {"notes": [_note_out(n, with_body=False) for n in notes]}


async def _get_released(db: AsyncSession, tags: TagNames, note_id: Any) -> Note:
    if not isinstance(note_id, str) or not note_id:
        raise McpToolError("'id' is required.")
    note = (await db.scalars(_released(tags).where(Note.id == note_id).options(*note_load_options()))).first()
    if note is None:
        # The same answer for "doesn't exist" and "not released".
        raise McpToolError("Note not found.")
    return note


async def get_note_tool(db: AsyncSession, args: Dict[str, Any]) -> Dict[str, Any]:
    tags = await load_tag_names(db)
    await _sync(db)
    return _note_out(await _get_released(db, tags, args.get("id")))


async def _visible_terms(db: AsyncSession, tags: TagNames) -> tuple[List[str], List[str]]:
    released_ids = _released(tags).with_only_columns(Note.id)
    categories = (await db.scalars(
        select(TaxonomyCategory.name)
        .where(TaxonomyCategory.id.in_(select(Note.category_id).where(Note.id.in_(released_ids))))
        .order_by(TaxonomyCategory.name)
    )).all()
    return list(categories), await _tags_on_released(db, released_ids)


async def _tags_on_released(db: AsyncSession, released_ids) -> List[str]:
    from app.models import note_tag_links
    return list((await db.scalars(
        select(TaxonomyTag.name).distinct()
        .join(note_tag_links, note_tag_links.c.tag_id == TaxonomyTag.id)
        .where(note_tag_links.c.note_id.in_(released_ids))
        .order_by(TaxonomyTag.name)
    )).all())


async def list_categories(db: AsyncSession, args: Dict[str, Any]) -> Dict[str, Any]:
    tags = await load_tag_names(db)
    categories, _ = await _visible_terms(db, tags)
    return {"categories": categories}


async def list_tags(db: AsyncSession, args: Dict[str, Any]) -> Dict[str, Any]:
    tags = await load_tag_names(db)
    _, tag_names = await _visible_terms(db, tags)
    return {"tags": tag_names}


# ---------------------------------------------------------------------------
# Write tools
# ---------------------------------------------------------------------------

async def _category_id(db: AsyncSession, tags: TagNames, name: Optional[str]) -> str:
    """Only categories the AI can see (used on released notes): naming
    another one must not confirm that it exists."""
    if not name:
        return ""
    visible, _ = await _visible_terms(db, tags)
    if name.strip().lower() not in {c.lower() for c in visible}:
        raise McpToolError("Unknown category. Use list_categories, or leave it empty.")
    category = (await db.scalars(
        select(TaxonomyCategory).where(func.lower(TaxonomyCategory.name) == name.strip().lower())
    )).first()
    return category.id if category else ""


async def _tag_input(db: AsyncSession, tags: TagNames, names: Any) -> tuple[List[str], List[str]]:
    """(existing tag ids, new tag names), always including the release
    and created tags.

    The AI may only use tags it can already see (list_tags) -- matched by
    exact base name, never through the translation lookup of the notes
    service, which would resolve a name to a tag used only on unreleased
    notes and hand back its base name (security review, #307). Any other
    name is refused with one message, whether such a tag exists or not,
    so the refusal is no oracle either. New tags are created by people."""
    if names is None:
        names = []
    if not isinstance(names, list) or not all(isinstance(n, str) for n in names):
        raise McpToolError("'tags' must be a list of strings.")
    wanted = {" ".join(n.split())[:100].lower() for n in names if n.strip()}
    wanted -= {tags.release.lower(), tags.created.lower()}
    released_ids = _released(tags).with_only_columns(Note.id)
    visible = {name.lower() for name in await _tags_on_released(db, released_ids)}
    if wanted - visible:
        raise McpToolError("Unknown tag. Use only tags from list_tags.")
    lookup = wanted | {tags.release.lower(), tags.created.lower()}
    existing = (await db.scalars(
        select(TaxonomyTag).where(func.lower(TaxonomyTag.name).in_(lookup))
    )).all()
    found = {t.name.lower() for t in existing}
    # Only the release/created tags can be missing here (first AI note).
    new = sorted(n for n in (tags.release, tags.created) if n.lower() not in found)
    return [t.id for t in existing], new


async def create_note_tool(db: AsyncSession, args: Dict[str, Any], user: User) -> Dict[str, Any]:
    tags = await load_tag_names(db)
    tag_ids, new_tags = await _tag_input(db, tags, args.get("tags"))
    data = NoteInput(
        title=_str(args, "title", 300) or "",
        note_date=_parse_date(args.get("date"), "date") or date.today(),
        category_id=await _category_id(db, tags, _str(args, "category", 100)),
        tag_ids=tag_ids, new_tags=new_tags,
        body_markdown=_str(args, "body") or "",
        source_url=_str(args, "source", 2048) or "",
    )
    note = await create_note(db, user, data)
    await db.commit()
    return _note_out(await get_note(db, note.id))


async def update_note_tool(db: AsyncSession, args: Dict[str, Any], user: User) -> Dict[str, Any]:
    tags = await load_tag_names(db)
    await _sync(db)
    note = await _get_released(db, tags, args.get("id"))
    current_tags = [t.name for t in note.tags]
    tag_ids, new_tags = await _tag_input(
        db, tags, args["tags"] if "tags" in args else current_tags,
    )
    if "category" in args:
        category_id = await _category_id(db, tags, _str(args, "category", 100))
    else:
        category_id = note.category_id or ""
    data = NoteInput(
        title=_str(args, "title", 300) if "title" in args else note.title,
        note_date=_parse_date(args.get("date"), "date") or note.note_date,
        category_id=category_id, tag_ids=tag_ids, new_tags=new_tags,
        body_markdown=_str(args, "body") if "body" in args else note.body_markdown,
        source_url=(_str(args, "source", 2048) or "") if "source" in args else (note.source_url or ""),
    )
    try:
        await update_note(db, note, user, data, _str(args, "version", 64) or "")
    except NoteConflict:
        await db.commit()  # the row now holds the cloud version
        raise McpToolError("The note was changed elsewhere meanwhile. Call get_note again and redo the change.")
    await db.commit()
    return _note_out(await get_note(db, note.id))


TOOLS = {
    "search_notes": {
        "description": (
            "Search the club's knowledge-base notes (only notes released for AI). Matches text in "
            "title, body and source URL; filter by category, tag and date range. Returns id, title, "
            "date, category, tags, source and a short excerpt; use get_note for the full text."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Text to look for (case-insensitive)."},
                "category": {"type": "string", "description": "Exact category name (see list_categories)."},
                "tag": {"type": "string", "description": "Exact tag name (see list_tags)."},
                "date_from": {"type": "string", "description": "YYYY-MM-DD, inclusive."},
                "date_to": {"type": "string", "description": "YYYY-MM-DD, inclusive."},
                "limit": {"type": "integer", "minimum": 1, "maximum": SEARCH_MAX_LIMIT},
            },
        },
        "read_only": True,
    },
    "get_note": {
        "description": "The full note (Markdown body) by id. Cite the title and date when you use it.",
        "inputSchema": {
            "type": "object", "properties": {"id": {"type": "string"}}, "required": ["id"],
        },
        "read_only": True,
    },
    "list_categories": {
        "description": "Category names used on released notes.",
        "inputSchema": {"type": "object", "properties": {}},
        "read_only": True,
    },
    "list_tags": {
        "description": "Tag names used on released notes.",
        "inputSchema": {"type": "object", "properties": {}},
        "read_only": True,
    },
    "create_note": {
        "description": (
            "Create a note. It is released for AI and tagged as AI-created automatically, so people "
            "can review it. Never put personal data (names of members, parcel numbers, contact details) "
            "into a note."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "body": {"type": "string", "description": "Markdown."},
                "date": {"type": "string", "description": "YYYY-MM-DD; default today."},
                "category": {"type": "string", "description": "An existing category name, or omit."},
                "tags": {"type": "array", "items": {"type": "string"}},
                "source": {"type": "string", "description": "http(s) URL the note is about, if any."},
            },
            "required": ["title"],
        },
        "read_only": False,
    },
    "update_note": {
        "description": (
            "Change a released note: only the fields you pass change. Pass the 'version' from get_note; "
            "if the note changed meanwhile you get an error and should fetch it again. The note gets "
            "the AI-created tag. There is no delete."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "version": {"type": "string"},
                "title": {"type": "string"},
                "body": {"type": "string"},
                "date": {"type": "string"},
                "category": {"type": "string"},
                "tags": {"type": "array", "items": {"type": "string"}},
                "source": {"type": "string"},
            },
            "required": ["id"],
        },
        "read_only": False,
    },
}


async def call_tool(db: AsyncSession, name: str, args: Dict[str, Any], user: User) -> Dict[str, Any]:
    """Raises McpToolError (shown to the AI) or KeyError (unknown tool).
    ServiceErrors from the notes service become McpToolError with their
    key, so a validation message reaches the AI without internals."""
    try:
        if name == "search_notes":
            return await search_notes(db, args)
        if name == "get_note":
            return await get_note_tool(db, args)
        if name == "list_categories":
            return await list_categories(db, args)
        if name == "list_tags":
            return await list_tags(db, args)
        if name == "create_note":
            return await create_note_tool(db, args, user)
        if name == "update_note":
            return await update_note_tool(db, args, user)
    except ServiceError as e:
        await db.rollback()
        raise McpToolError(f"Rejected: {e.key}")
    raise KeyError(name)
