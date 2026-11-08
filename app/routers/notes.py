"""
Notes router (web UI, issue #286, docs/module-notes.md): Markdown notes
-- meeting minutes, board notes, anything -- filed under the club
taxonomy (ADR 0122), stored as .md files in the cloud when a notes
folder is configured (ADR 0123).

Business logic lives in app/services/notes.py (ADR 0070).
"""
import urllib.parse
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from markupsafe import Markup
from sqlalchemy.ext.asyncio import AsyncSession

from app.announcement_utils import render_markdown_to_html
from app.cloud_storage import CloudStorageError
from app.database import get_db
from app.i18n import AVAILABLE_LANGUAGES, t_for
from app.models import Note, TaxonomyCategory, TaxonomyTag
from app.module_flags import require_module
from app.note_files import render_note_file, slugify
from app.permissions import has_permission, require_permission
from app.security_headers import content_disposition
from app.services.errors import ServiceError
from app.services.notes import (
    NoteConflict, NoteFilter, NoteInput, count_term_notes, create_note, create_term, delete_note, delete_term,
    get_note, list_categories, list_tags, load_notes_folder, note_load_options, refresh_note,
    rename_term, set_term_translations, sync_from_cloud, update_note,
)
from app.tag_translations import tag_label
from app.templating import templates

MODULE = "notes"

router = APIRouter(
    prefix="/notes",
    tags=["notes"],
    dependencies=[Depends(require_module(MODULE))],
)

TAXONOMY_KINDS = {"categories": TaxonomyCategory, "tags": TaxonomyTag}


def render_body(markdown_text: str) -> Markup:
    """Bleach-sanitized HTML (app/announcement_utils.py), marked safe
    here in Python rather than with |safe in the template (CLAUDE.md)."""
    return Markup(render_markdown_to_html(markdown_text, allow_tables=True))


def _redirect(url: str, **params: str) -> RedirectResponse:
    query = urllib.parse.urlencode({k: v for k, v in params.items() if v})
    return RedirectResponse(f"{url}?{query}" if query else url, status_code=303)


async def _note_or_404(request: Request, db: AsyncSession, note_id: str) -> Note:
    note = await get_note(db, note_id)
    if note is None:
        raise HTTPException(status_code=404, detail=t_for(request, "notes.errors.not_found"))
    return note


async def _rollback(db: AsyncSession, user) -> None:
    """Rolls back a failed save. Rollback expires every loaded object,
    and the page re-rendered next reads the user (base.html) -- reload
    it now rather than lazily from the template (MissingGreenlet)."""
    await db.rollback()
    await db.refresh(user)


def _sync_message(request: Request, result) -> str:
    if not result.ran:
        return ""
    return t_for(
        request, "notes.sync.summary", imported=result.imported, updated=result.updated,
        removed=result.removed, pushed=result.pushed,
    )


# ---------------------------------------------------------------------------
# List
# ---------------------------------------------------------------------------

@router.get("/", response_class=HTMLResponse)
async def notes_list(
    request: Request,
    q: str = "", category: str = "", tag: str = "", date_from: str = "", date_to: str = "", sort: str = "",
    db: AsyncSession = Depends(get_db),
):
    user = await require_permission(request, db, MODULE, "read")
    sync = await sync_from_cloud(db)
    await db.commit()
    filters = NoteFilter.build(q, category, tag, date_from, date_to, sort)
    notes = (await db.scalars(filters.apply().options(*note_load_options()))).all()
    return templates.TemplateResponse("notes/list.html", {
        "request": request, "user": user, "notes": notes, "filters": filters,
        "categories": await list_categories(db), "tags": await list_tags(db),
        "cloud_folder": await load_notes_folder(db),
        "sync_errors": sync.errors, "sync_conflicts": sync.conflicts,
        "message": request.query_params.get("message", ""), "error": request.query_params.get("error", ""),
    })


@router.post("/sync")
async def notes_sync(request: Request, db: AsyncSession = Depends(get_db)):
    await require_permission(request, db, MODULE, "read")
    result = await sync_from_cloud(db, force=True)
    await db.commit()
    if result.errors:
        return _redirect("/notes/", error="; ".join(result.errors)[:500])
    if not result.ran:
        return _redirect("/notes/", error=t_for(request, "notes.sync.not_configured"))
    return _redirect("/notes/", message=_sync_message(request, result))


# ---------------------------------------------------------------------------
# Create / edit
# ---------------------------------------------------------------------------

def _parse_date(value: str) -> Optional[date]:
    try:
        return date.fromisoformat(value) if value else None
    except ValueError:
        return None


async def _input_from_form(request: Request) -> NoteInput:
    form = await request.form()
    return NoteInput(
        title=str(form.get("title", "")),
        note_date=_parse_date(str(form.get("note_date", ""))),
        category_id=str(form.get("category_id", "")),
        tag_ids=[str(v) for v in form.getlist("tag_ids")],
        new_tags=[part for part in str(form.get("new_tags", "")).split(",") if part.strip()],
        body_markdown=str(form.get("body_markdown", "")),
    )


def _entered(data: NoteInput) -> dict:
    return {
        "title": data.title, "note_date": data.note_date.isoformat() if data.note_date else "",
        "category_id": data.category_id, "tag_ids": data.tag_ids,
        "new_tags": ", ".join(t.strip() for t in data.new_tags), "body_markdown": data.body_markdown,
    }


def _values_from_note(note: Optional[Note]) -> dict:
    if note is None:
        return {"title": "", "note_date": date.today().isoformat(), "category_id": "",
                "tag_ids": [], "new_tags": "", "body_markdown": ""}
    return {
        "title": note.title, "note_date": note.note_date.isoformat(),
        "category_id": note.category_id or "", "tag_ids": [t.id for t in note.tags],
        "new_tags": "", "body_markdown": note.body_markdown,
    }


async def _form_response(
    request: Request, db: AsyncSession, user, note: Optional[Note], values: dict,
    error: str = "", conflict_note: Optional[Note] = None, status_code: int = 200,
):
    return templates.TemplateResponse("notes/form.html", {
        "request": request, "user": user, "note": note, "values": values, "error": error,
        "categories": await list_categories(db), "tags": await list_tags(db),
        "conflict_note": conflict_note,
        "conflict_html": render_body(conflict_note.body_markdown) if conflict_note else None,
        "base_hash": (note.cloud_hash or "") if note else "",
        "cloud_folder": await load_notes_folder(db),
    }, status_code=status_code)


@router.get("/new", response_class=HTMLResponse)
async def note_new_page(request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_permission(request, db, MODULE, "write")
    return await _form_response(request, db, user, None, _values_from_note(None))


@router.post("/new")
async def note_create(request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_permission(request, db, MODULE, "write")
    data = await _input_from_form(request)
    try:
        note = await create_note(db, user, data)
    except ServiceError as e:
        await _rollback(db, user)
        return await _form_response(request, db, user, None, _entered(data),
                                    error=t_for(request, e.key, **e.params), status_code=400)
    except CloudStorageError as e:
        await _rollback(db, user)
        return await _form_response(request, db, user, None, _entered(data),
                                    error=t_for(request, "notes.errors.cloud_save_failed", detail=str(e)),
                                    status_code=502)
    await db.commit()
    return RedirectResponse(f"/notes/{note.id}", status_code=303)


@router.post("/preview")
async def note_preview(request: Request, db: AsyncSession = Depends(get_db)):
    """Server-side preview for the editor: the same sanitizer the detail
    page uses, so a note from the cloud can't run script in someone
    else's browser through the editor's own (unsanitized) preview."""
    await require_permission(request, db, MODULE, "read")
    try:
        payload = await request.json()
    except ValueError:
        payload = {}
    text = payload.get("markdown", "") if isinstance(payload, dict) else ""
    return JSONResponse({"html": render_markdown_to_html(str(text)[:500_000], allow_tables=True)})


# ---------------------------------------------------------------------------
# Taxonomy (registered before /{note_id})
# ---------------------------------------------------------------------------

def _kind_or_404(kind: str):
    model = TAXONOMY_KINDS.get(kind)
    if model is None:
        raise HTTPException(status_code=404)
    return model


async def _term_or_404(db: AsyncSession, model, term_id: str):
    term = await db.get(model, term_id)
    if term is None:
        raise HTTPException(status_code=404)
    return term


@router.get("/taxonomy", response_class=HTMLResponse)
async def taxonomy_page(request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_permission(request, db, MODULE, "read")
    return templates.TemplateResponse("notes/taxonomy.html", {
        "request": request, "user": user,
        "categories": await list_categories(db), "tags": await list_tags(db),
        "category_counts": await count_term_notes(db, TaxonomyCategory),
        "tag_counts": await count_term_notes(db, TaxonomyTag),
        "languages": AVAILABLE_LANGUAGES,
        "message": request.query_params.get("message", ""), "error": request.query_params.get("error", ""),
    })


@router.post("/taxonomy/{kind}/new")
async def taxonomy_create(kind: str, request: Request, name: str = Form(""), db: AsyncSession = Depends(get_db)):
    await require_permission(request, db, MODULE, "write")
    model = _kind_or_404(kind)
    try:
        await create_term(db, model, name)
    except ServiceError as e:
        return _redirect("/notes/taxonomy", error=t_for(request, e.key, **e.params))
    await db.commit()
    return _redirect("/notes/taxonomy", message=t_for(request, "taxonomy.saved"))


@router.post("/taxonomy/{kind}/{term_id}/rename")
async def taxonomy_rename(kind: str, term_id: str, request: Request, name: str = Form(""),
                          db: AsyncSession = Depends(get_db)):
    await require_permission(request, db, MODULE, "write")
    model = _kind_or_404(kind)
    term = await _term_or_404(db, model, term_id)
    try:
        await rename_term(db, model, term, name)
    except ServiceError as e:
        return _redirect("/notes/taxonomy", error=t_for(request, e.key, **e.params))
    await db.commit()
    return _redirect("/notes/taxonomy", message=t_for(request, "taxonomy.saved"))


@router.post("/taxonomy/{kind}/{term_id}/translations")
async def taxonomy_translations(kind: str, term_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    await require_permission(request, db, MODULE, "write")
    model = _kind_or_404(kind)
    term = await _term_or_404(db, model, term_id)
    form = await request.form()
    try:
        await set_term_translations(db, model, term, {lang: str(form.get(f"name_{lang}", "")) for lang in AVAILABLE_LANGUAGES})
    except ServiceError as e:
        return _redirect("/notes/taxonomy", error=t_for(request, e.key, **e.params))
    await db.commit()
    return _redirect("/notes/taxonomy", message=t_for(request, "taxonomy.saved"))


@router.post("/taxonomy/{kind}/{term_id}/delete")
async def taxonomy_delete(kind: str, term_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    await require_permission(request, db, MODULE, "delete")
    model = _kind_or_404(kind)
    await delete_term(db, model, await _term_or_404(db, model, term_id))
    await db.commit()
    return _redirect("/notes/taxonomy", message=t_for(request, "taxonomy.deleted"))


# ---------------------------------------------------------------------------
# Single note
# ---------------------------------------------------------------------------

@router.get("/{note_id}", response_class=HTMLResponse)
async def note_detail(note_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_permission(request, db, MODULE, "read")
    note = await _note_or_404(request, db, note_id)
    cloud_error = await refresh_note(db, note)
    await db.commit()
    note = await _note_or_404(request, db, note_id)
    permissions = getattr(request.state, "permissions", {})
    return templates.TemplateResponse("notes/detail.html", {
        "request": request, "user": user, "note": note, "body_html": render_body(note.body_markdown),
        "cloud_error": cloud_error, "cloud_folder": await load_notes_folder(db),
        "can_write": has_permission(permissions, MODULE, "write"),
        "can_delete": has_permission(permissions, MODULE, "delete"),
        "error": request.query_params.get("error", ""),
    })


@router.get("/{note_id}/download")
async def note_download(note_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    """The note as a .md file, in the same format as in the cloud."""
    await require_permission(request, db, MODULE, "read")
    note = await _note_or_404(request, db, note_id)
    lang = getattr(request.state, "language", "en")
    content = render_note_file(
        note_id=note.id, title=note.title, note_date=note.note_date,
        category=tag_label(note.category, lang) if note.category else None,
        tags=[tag_label(t, lang) for t in note.tags], body=note.body_markdown,
    )
    filename = (note.cloud_filename or "").rsplit("/", 1)[-1] or f"{note.note_date.isoformat()}-{slugify(note.title)}.md"
    return Response(
        content.encode("utf-8"), media_type="text/markdown; charset=utf-8",
        headers={"Content-Disposition": content_disposition(filename)},
    )


@router.get("/{note_id}/edit", response_class=HTMLResponse)
async def note_edit_page(note_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_permission(request, db, MODULE, "write")
    note = await _note_or_404(request, db, note_id)
    cloud_error = await refresh_note(db, note)
    await db.commit()
    note = await _note_or_404(request, db, note_id)
    return await _form_response(request, db, user, note, _values_from_note(note), error=cloud_error or "")


@router.post("/{note_id}/edit")
async def note_update(note_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_permission(request, db, MODULE, "write")
    note = await _note_or_404(request, db, note_id)
    data = await _input_from_form(request)
    base_hash = str((await request.form()).get("base_hash", ""))
    try:
        await update_note(db, note, user, data, base_hash)
    except NoteConflict as conflict:
        await db.commit()  # the note row now holds the cloud version
        fresh = await _note_or_404(request, db, note_id)
        return await _form_response(
            request, db, user, fresh, _entered(data),
            error=t_for(request, "notes.errors.conflict"), conflict_note=fresh, status_code=409,
        )
    except ServiceError as e:
        await _rollback(db, user)
        note = await _note_or_404(request, db, note_id)
        return await _form_response(request, db, user, note, _entered(data),
                                    error=t_for(request, e.key, **e.params), status_code=400)
    except CloudStorageError as e:
        await _rollback(db, user)
        note = await _note_or_404(request, db, note_id)
        return await _form_response(request, db, user, note, _entered(data),
                                    error=t_for(request, "notes.errors.cloud_save_failed", detail=str(e)),
                                    status_code=502)
    await db.commit()
    return RedirectResponse(f"/notes/{note_id}", status_code=303)


@router.post("/{note_id}/delete")
async def note_delete(note_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    await require_permission(request, db, MODULE, "delete")
    note = await _note_or_404(request, db, note_id)
    try:
        await delete_note(db, note)
    except CloudStorageError as e:
        await db.rollback()
        return _redirect(f"/notes/{note_id}", error=t_for(request, "notes.errors.cloud_delete_failed", detail=str(e)))
    await db.commit()
    return _redirect("/notes/", message=t_for(request, "notes.deleted"))
