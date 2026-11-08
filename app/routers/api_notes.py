"""
API router: Notes (issue #286, docs/module-notes.md) and the club
taxonomy they're filed under (ADR 0122).

Business logic shared with app/routers/notes.py (HTML) lives in
app/services/notes.py (ADR 0070) -- including the cloud file being the
master (ADR 0123): a save whose file changed in the cloud is a 409, a
cloud that can't be written is a 502, and nothing is saved in either
case.
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api_auth import require_api_permission
from app.cloud_storage import CloudStorageError
from app.database import get_db
from app.i18n import t_for
from app.models import TaxonomyCategory, TaxonomyTag, User
from app.module_flags import require_module
from app.schemas import NoteCreate, NoteOut, NoteUpdate, TaxonomyTermCreate, TaxonomyTermOut
from app.services.errors import ServiceError
from app.services.notes import (
    NoteConflict, NoteFilter, NoteInput, create_note, create_term, delete_note, get_note, list_categories,
    list_tags, note_load_options, sync_from_cloud, update_note,
)

MODULE = "notes"

router = APIRouter(
    prefix="/api/v1/notes",
    tags=["API: Notes"],
    dependencies=[Depends(require_module(MODULE))],
)


def _service_error(request: Request, error: ServiceError) -> HTTPException:
    code = error.http_status if error.http_status in (404, 409) else status.HTTP_422_UNPROCESSABLE_ENTITY
    return HTTPException(status_code=code, detail=t_for(request, error.key, **error.params))


def _cloud_error(request: Request, error: CloudStorageError) -> HTTPException:
    return HTTPException(status_code=status.HTTP_502_BAD_GATEWAY,
                         detail=t_for(request, "notes.errors.cloud_save_failed", detail=str(error)))


def _input(data: NoteCreate) -> NoteInput:
    return NoteInput(
        title=data.title, note_date=data.note_date, note_time=data.note_time,
        category_id=data.category_id or "", tag_ids=list(data.tag_ids), new_tags=list(data.new_tags),
        body_markdown=data.body_markdown,
    )


async def _note_or_404(db: AsyncSession, note_id: str):
    note = await get_note(db, note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@router.get("", response_model=List[NoteOut], summary="List, search and filter notes")
async def notes_list(
    q: str = Query("", description="Text in title, body or a tag name (substring, case-insensitive)"),
    category: str = Query("", description="Category id, or 'none' for uncategorised notes"),
    tag: str = Query("", description="Tag id"),
    date_from: str = Query("", description="YYYY-MM-DD, inclusive"),
    date_to: str = Query("", description="YYYY-MM-DD, inclusive"),
    sort: str = Query("date_desc", description="date_desc, date_asc, title or updated"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission(MODULE, "read")),
):
    await sync_from_cloud(db)
    await db.commit()
    query = NoteFilter.build(q, category, tag, date_from, date_to, sort).apply()
    return (await db.scalars(query.options(*note_load_options()).limit(limit).offset(offset))).all()


@router.post("", response_model=NoteOut, status_code=status.HTTP_201_CREATED, summary="Create a note")
async def note_create(
    data: NoteCreate, request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission(MODULE, "write")),
):
    try:
        note = await create_note(db, user, _input(data))
    except ServiceError as e:
        await db.rollback()
        raise _service_error(request, e)
    except CloudStorageError as e:
        await db.rollback()
        raise _cloud_error(request, e)
    await db.commit()
    return await _note_or_404(db, note.id)


# --- Taxonomy (registered before /{note_id}) --------------------------------

@router.get("/categories", response_model=List[TaxonomyTermOut], summary="List the club's categories")
async def categories_list(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission(MODULE, "read")),
):
    return await list_categories(db)


@router.post("/categories", response_model=TaxonomyTermOut, status_code=status.HTTP_201_CREATED,
             summary="Create a category")
async def category_create(
    data: TaxonomyTermCreate, request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission(MODULE, "write")),
):
    try:
        term = await create_term(db, TaxonomyCategory, data.name)
    except ServiceError as e:
        raise _service_error(request, e)
    await db.commit()
    return term


@router.get("/tags", response_model=List[TaxonomyTermOut], summary="List the club's tags")
async def tags_list(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission(MODULE, "read")),
):
    return await list_tags(db)


@router.post("/tags", response_model=TaxonomyTermOut, status_code=status.HTTP_201_CREATED, summary="Create a tag")
async def tag_create(
    data: TaxonomyTermCreate, request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission(MODULE, "write")),
):
    try:
        term = await create_term(db, TaxonomyTag, data.name)
    except ServiceError as e:
        raise _service_error(request, e)
    await db.commit()
    return term


@router.post("/sync", summary="Sync notes with the cloud folder now")
async def notes_sync(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission(MODULE, "read")),
):
    result = await sync_from_cloud(db, force=True)
    await db.commit()
    return {
        "ran": result.ran, "imported": result.imported, "updated": result.updated, "removed": result.removed,
        "pushed": result.pushed, "conflicts": result.conflicts, "errors": result.errors,
    }


# --- Single note ------------------------------------------------------------

@router.get("/{note_id}", response_model=NoteOut, summary="Get a note")
async def note_get(
    note_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission(MODULE, "read")),
):
    return await _note_or_404(db, note_id)


@router.put("/{note_id}", response_model=NoteOut, summary="Update a note")
async def note_update(
    note_id: str, data: NoteUpdate, request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission(MODULE, "write")),
):
    note = await _note_or_404(db, note_id)
    try:
        await update_note(db, note, user, _input(data), data.base_hash or "")
    except NoteConflict:
        await db.commit()  # the row now holds the cloud version
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=t_for(request, "notes.errors.conflict"))
    except ServiceError as e:
        await db.rollback()
        raise _service_error(request, e)
    except CloudStorageError as e:
        await db.rollback()
        raise _cloud_error(request, e)
    await db.commit()
    return await _note_or_404(db, note_id)


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a note (and its cloud file)")
async def note_delete(
    note_id: str, request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission(MODULE, "delete")),
):
    note = await _note_or_404(db, note_id)
    try:
        await delete_note(db, note)
    except CloudStorageError as e:
        await db.rollback()
        raise _cloud_error(request, e)
    await db.commit()
