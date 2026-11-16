"""
Processes, web side (issue #331, ADR 0135, docs/module-processes.md).

Every route needs read on "processes" to get this far; what a change
needs on top (write, delete, or full access for templates) is checked in
app/services/processes.py, which this router and the API share.

The template routes are declared before /{process_id}, so "templates"
is never taken for a process id.
"""
from types import SimpleNamespace
from typing import Optional
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import active_member_filter, get_db
from app.i18n import DEFAULT_LANGUAGE, t_for
from app.models import (
    Applicant, Member, Parcel, ProcessFieldKind, ProcessStatus, ProcessSubjectKind,
)
from app.module_flags import require_module
from app.permissions import require_permission
from app.security_headers import content_disposition
from app.services import processes as svc
from app.services.errors import ServiceError
from app.templating import templates

router = APIRouter(
    prefix="/processes",
    tags=["processes"],
    dependencies=[Depends(require_module(svc.MODULE))],
)

_STATUS_FILTERS = ("open", "closed", "all")
_ERROR_PREFIX = "processes.errors."


def _lang(request: Request) -> str:
    return getattr(request.state, "language", DEFAULT_LANGUAGE)


def _with_error(url: str, error: Optional[str], anchor: str = "") -> str:
    if error:
        url += ("&" if "?" in url else "?") + f"error={quote(error)}"
    return url + (f"#{anchor}" if anchor else "")


def shown_error(key: Optional[str]) -> Optional[str]:
    """Only our own error keys come back through ?error= -- anything else
    in the URL is ignored."""
    if key and (key.startswith(_ERROR_PREFIX) or key == "errors.no_permission"):
        return key
    return None


async def _fail(request: Request, db: AsyncSession, url: str, error: ServiceError, anchor: str = ""):
    """A refused change: roll back whatever the service had started and
    go back to the page with the reason. 403/404 behave as everywhere."""
    await db.rollback()
    if error.http_status == 403:
        raise HTTPException(status_code=403, detail=t_for(request, error.key))
    if error.http_status == 404:
        raise HTTPException(status_code=404, detail=t_for(request, error.key))
    return RedirectResponse(url=_with_error(url, error.key, anchor), status_code=303)


def _can_read_applicants(request: Request) -> bool:
    permissions = getattr(request.state, "permissions", {}) or {}
    return bool(permissions.get("applicants", {}).get("read"))


def _redirect(url: str, anchor: str = "") -> RedirectResponse:
    return RedirectResponse(url=url + (f"#{anchor}" if anchor else ""), status_code=303)


async def _choices(request: Request, db: AsyncSession, kinds: set) -> dict:
    """Options for the member/applicant/plot pickers -- only the lists a
    page actually needs. Applicants only for users who may read the
    applicants module (their names and emails are that module's data)."""
    out: dict = {"can_read_applicants": _can_read_applicants(request)}
    if kinds & {ProcessFieldKind.MEMBER, ProcessSubjectKind.MEMBER}:
        out["members"] = (await db.scalars(
            select(Member).where(active_member_filter()).order_by(Member.last_name, Member.first_name)
        )).all()
    if out["can_read_applicants"] and kinds & {ProcessFieldKind.APPLICANT, ProcessSubjectKind.APPLICANT}:
        out["applicants"] = (await db.scalars(select(Applicant).order_by(Applicant.applied_at.desc()))).all()
    if kinds & {ProcessFieldKind.PARCEL, ProcessSubjectKind.PARCEL}:
        out["parcels"] = (await db.scalars(select(Parcel).order_by(Parcel.plot_number))).all()
    return out


# ---------------------------------------------------------------------------
# Templates (full access)
# ---------------------------------------------------------------------------

def _template_url(template_id: str) -> str:
    return f"/processes/templates/{template_id}"


async def _require_templates(request: Request, db: AsyncSession):
    user = await require_permission(request, db, svc.MODULE, "read")
    if not await svc.can(db, user, "templates"):
        raise HTTPException(status_code=403, detail=t_for(request, "errors.no_permission"))
    return user


async def _load_template(request: Request, db: AsyncSession, template_id: str):
    try:
        return await svc.get_template(db, template_id)
    except ServiceError as e:
        raise HTTPException(status_code=404, detail=t_for(request, e.key))


@router.get("/templates/", response_class=HTMLResponse)
async def templates_list(request: Request, db: AsyncSession = Depends(get_db)):
    user = await _require_templates(request, db)
    items = await svc.list_templates(db)
    return templates.TemplateResponse("processes/templates.html", {
        "request": request, "user": user, "templates_list": items,
        "usage": {t.id: await svc.template_usage(db, t.id) for t in items},
        "examples": list(svc.EXAMPLES), "subject_kinds": list(ProcessSubjectKind),
        "error": shown_error(request.query_params.get("error")),
    })


@router.post("/templates/new")
async def template_create(request: Request, db: AsyncSession = Depends(get_db)):
    user = await _require_templates(request, db)
    form = await request.form()
    try:
        template = await svc.create_template(
            db, user, name=form.get("name"), description=form.get("description"),
            subject_kind=form.get("subject_kind"),
        )
    except ServiceError as e:
        return await _fail(request, db, "/processes/templates/", e)
    return _redirect(_template_url(template.id))


@router.post("/templates/example")
async def template_from_example(request: Request, db: AsyncSession = Depends(get_db)):
    user = await _require_templates(request, db)
    form = await request.form()
    try:
        template = await svc.create_from_example(db, user, str(form.get("key") or ""), _lang(request))
    except ServiceError as e:
        return await _fail(request, db, "/processes/templates/", e)
    return _redirect(_template_url(template.id))


def _preview_field(field):
    """A template field shaped like an empty ProcessField, so the preview
    renders through the very same _field_input.html as a real process."""
    return SimpleNamespace(
        id=f"preview-{field.id}", kind=field.kind, label=field.label, help_text=field.help_text,
        required=field.required, options=field.options, value_text=None, value_number=None, value_date=None,
        value_bool=None, value_member=None, value_member_id=None, value_applicant_id=None, value_parcel_id=None,
    )


@router.get("/templates/{template_id}", response_class=HTMLResponse)
async def template_edit_page(template_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    user = await _require_templates(request, db)
    template = await _load_template(request, db, template_id)
    wanted = request.query_params.get("stage")
    stage = next((s for s in template.stages if s.id == wanted), template.stages[0] if template.stages else None)
    return templates.TemplateResponse("processes/template_edit.html", {
        "request": request, "user": user, "template": template, "stage": stage,
        "preview_fields": [_preview_field(f) for f in stage.fields] if stage else [],
        "usage": await svc.template_usage(db, template.id),
        "subject_kinds": list(ProcessSubjectKind), "field_kinds": list(ProcessFieldKind),
        "members": [], "applicants": [], "parcels": [], "can_read_applicants": True,
        "error": shown_error(request.query_params.get("error")),
    })


def _wants_json(request: Request) -> bool:
    """The builder's background saves (fetch) ask for JSON; a plain form
    post without JavaScript still gets the redirect."""
    return request.headers.get("x-requested-with") == "fetch"


async def _template_action(request: Request, db: AsyncSession, template_id: str, action, anchor: str = ""):
    """Runs one template change, then redirects back to the editor -- or,
    for the builder's fetch calls, answers {"ok": true, ...} / {"error": ...}."""
    user = await _require_templates(request, db)
    template = await _load_template(request, db, template_id)
    form = await request.form()
    try:
        result = await action(user, template, form)
    except ServiceError as e:
        if _wants_json(request):
            await db.rollback()
            return JSONResponse({"error": t_for(request, e.key)}, status_code=e.http_status or 422)
        return await _fail(request, db, _template_url(template_id), e, anchor)
    if _wants_json(request):
        return JSONResponse({"ok": True, **(result if isinstance(result, dict) else {})})
    if isinstance(result, dict):
        return _redirect(result.get("url") or _template_url(template_id), result.get("anchor", anchor))
    stage = str(form.get("return_stage") or "")
    url = _template_url(template_id) + (f"?stage={quote(stage)}" if stage else "")
    return result or _redirect(url, anchor)


@router.post("/templates/{template_id}")
async def template_update(template_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    async def action(user, template, form):
        await svc.update_template(db, template, user, name=form.get("name"), description=form.get("description"),
                                  subject_kind=form.get("subject_kind"))
    return await _template_action(request, db, template_id, action)


@router.post("/templates/{template_id}/archive")
async def template_archive(template_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    async def action(user, template, form):
        await svc.set_template_active(db, template, user, form.get("active") == "1")
    return await _template_action(request, db, template_id, action)


@router.post("/templates/{template_id}/delete")
async def template_delete(template_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    async def action(user, template, form):
        await svc.delete_template(db, template, user)
        return {"url": "/processes/templates/"}
    return await _template_action(request, db, template_id, action)


@router.post("/templates/{template_id}/stages")
async def template_stage_add(template_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    async def action(user, template, form):
        stage = await svc.add_stage(db, template, user, name=form.get("name"), description=form.get("description"))
        return {"id": stage.id, "url": f"{_template_url(template_id)}?stage={stage.id}"}
    return await _template_action(request, db, template_id, action, "add-stage")


def _ids(form) -> list[str]:
    return [str(v) for v in form.getlist("ids")]


@router.post("/templates/{template_id}/stages/order")
async def template_stages_order(template_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    async def action(user, template, form):
        await svc.reorder_stages(db, template, _ids(form), user)
    return await _template_action(request, db, template_id, action)


@router.post("/templates/{template_id}/stages/{stage_id}")
async def template_stage_update(template_id: str, stage_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    async def action(user, template, form):
        await svc.update_stage(db, template, stage_id, user, name=form.get("name"), description=form.get("description"))
    return await _template_action(request, db, template_id, action, f"stage-{stage_id}")


@router.post("/templates/{template_id}/stages/{stage_id}/delete")
async def template_stage_delete(template_id: str, stage_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    async def action(user, template, form):
        await svc.delete_stage(db, template, stage_id, user)
    return await _template_action(request, db, template_id, action)


@router.post("/templates/{template_id}/stages/{stage_id}/move")
async def template_stage_move(template_id: str, stage_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    async def action(user, template, form):
        await svc.move_stage(db, template, stage_id, str(form.get("direction") or ""), user)
    return await _template_action(request, db, template_id, action, f"stage-{stage_id}")


def _field_values(form) -> dict:
    return {
        "kind": form.get("kind"), "label": form.get("label"), "help_text": form.get("help_text"),
        "required": form.get("required") == "1", "options": form.get("options"),
    }


@router.post("/templates/{template_id}/stages/{stage_id}/fields")
async def template_field_add(template_id: str, stage_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    async def action(user, template, form):
        field = await svc.add_field(db, template, stage_id, user, **_field_values(form))
        return {"id": field.id, "url": f"{_template_url(template_id)}?stage={stage_id}", "anchor": f"field-{field.id}"}
    return await _template_action(request, db, template_id, action, f"stage-{stage_id}")


@router.post("/templates/{template_id}/fields/{field_id}")
async def template_field_update(template_id: str, field_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    async def action(user, template, form):
        await svc.update_field(db, template, field_id, user, **_field_values(form))
    return await _template_action(request, db, template_id, action, f"field-{field_id}")


@router.post("/templates/{template_id}/fields/{field_id}/delete")
async def template_field_delete(template_id: str, field_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    async def action(user, template, form):
        await svc.delete_field(db, template, field_id, user)
    return await _template_action(request, db, template_id, action)


@router.post("/templates/{template_id}/fields/{field_id}/move")
async def template_field_move(template_id: str, field_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    async def action(user, template, form):
        await svc.move_field(db, template, field_id, str(form.get("direction") or ""), user)
    return await _template_action(request, db, template_id, action, f"field-{field_id}")


@router.post("/templates/{template_id}/stages/{stage_id}/fields/order")
async def template_fields_order(template_id: str, stage_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    async def action(user, template, form):
        await svc.reorder_fields(db, template, stage_id, _ids(form), user)
    return await _template_action(request, db, template_id, action)


@router.post("/templates/{template_id}/fields/{field_id}/stage")
async def template_field_to_stage(template_id: str, field_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    async def action(user, template, form):
        stage_id = str(form.get("stage_id") or "")
        await svc.move_field_to_stage(db, template, field_id, stage_id, user)
        return {"url": f"{_template_url(template_id)}?stage={stage_id}", "anchor": f"field-{field_id}"}
    return await _template_action(request, db, template_id, action)


@router.post("/templates/{template_id}/fields/{field_id}/duplicate")
async def template_field_duplicate(template_id: str, field_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    async def action(user, template, form):
        copy = await svc.duplicate_field(db, template, field_id, user)
        return {"id": copy.id, "anchor": f"field-{copy.id}",
                "url": f"{_template_url(template_id)}?stage={copy.stage_id}"}
    return await _template_action(request, db, template_id, action)


# ---------------------------------------------------------------------------
# Processes
# ---------------------------------------------------------------------------

@router.get("/", response_class=HTMLResponse)
async def processes_list(
    request: Request, status: str = "open", template: str = "", db: AsyncSession = Depends(get_db),
):
    user = await require_permission(request, db, svc.MODULE, "read")
    if status not in _STATUS_FILTERS:
        status = "open"
    items = await svc.list_processes(db, svc.ProcessFilter(status=status, template_id=template))
    return templates.TemplateResponse("processes/list.html", {
        "request": request, "user": user, "processes": items, "status": status, "template_id": template,
        "templates_list": await svc.list_templates(db),
        "current_stage": svc.current_stage, "subject_label": svc.subject_label,
    })


async def _new_context(request: Request, db: AsyncSession, user, values: dict, error: Optional[str] = None) -> dict:
    """Coming from a plot/member/applicant page, only the templates for
    that kind of subject are offered, and a single one is preselected."""
    active = await svc.list_templates(db, include_archived=False)
    if values.get("subject_kind") in {k.value for k in ProcessSubjectKind}:
        active = [t for t in active if t.subject_kind.value == values["subject_kind"]]
    chosen = next((t for t in active if t.id == values.get("template_id")), None)
    if chosen is None and values.get("subject_kind") and len(active) == 1:
        chosen = active[0]
    return {
        "request": request, "user": user, "templates_list": active, "chosen": chosen, "values": values,
        "error": error, **(await _choices(request, db, {chosen.subject_kind} if chosen else set())),
    }


@router.get("/new", response_class=HTMLResponse)
async def process_new_page(
    request: Request, template_id: str = "", subject_id: str = "", subject_kind: str = "",
    db: AsyncSession = Depends(get_db),
):
    user = await require_permission(request, db, svc.MODULE, "write")
    return templates.TemplateResponse("processes/new.html", await _new_context(
        request, db, user,
        {"template_id": template_id, "subject_id": subject_id, "subject_kind": subject_kind, "title": ""},
    ))


@router.post("/new")
async def process_create(request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_permission(request, db, svc.MODULE, "write")
    form = await request.form()
    values = {key: str(form.get(key) or "") for key in ("template_id", "subject_id", "title")}
    try:
        process = await svc.start_process(
            db, user, template_id=values["template_id"], title=values["title"], subject_id=values["subject_id"],
        )
    except ServiceError as e:
        await db.rollback()
        if e.http_status == 403:
            raise HTTPException(status_code=403, detail=t_for(request, e.key))
        user = await require_permission(request, db, svc.MODULE, "write")
        status_code = 400 if e.http_status == 404 else e.http_status
        return templates.TemplateResponse(
            "processes/new.html", await _new_context(request, db, user, values, e.key), status_code=status_code,
        )
    return _redirect(f"/processes/{process.id}")


async def _load(request: Request, db: AsyncSession, process_id: str, *, lock: bool = False):
    try:
        return await svc.get_process(db, process_id, lock=lock)
    except ServiceError as e:
        raise HTTPException(status_code=404, detail=t_for(request, e.key))


@router.get("/{process_id}", response_class=HTMLResponse)
async def process_detail(process_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_permission(request, db, svc.MODULE, "read")
    process = await _load(request, db, process_id)
    stage = svc.current_stage(process)
    kinds = {f.kind for s in process.stages for f in s.fields} if process.is_open else set()
    has_file_fields = any(f.kind == ProcessFieldKind.FILE for s in process.stages for f in s.fields)
    upload_folder = await svc.upload_folder(db, process) if process.is_open and has_file_fields else None
    return templates.TemplateResponse("processes/detail.html", {
        "upload_folder": upload_folder,
        "request": request, "user": user, "process": process, "stage": stage,
        "missing": svc.missing_fields(stage) if process.is_open else [],
        "can_write": await svc.can(db, user, "write"), "can_delete": await svc.can(db, user, "delete"),
        "subject_label": svc.subject_label(process), "error": shown_error(request.query_params.get("error")),
        "is_filled": svc.is_filled, "K": ProcessFieldKind, "ProcessStatus": ProcessStatus,
        **(await _choices(request, db, kinds)),
    })


def _process_url(process_id: str) -> str:
    return f"/processes/{process_id}"


@router.post("/{process_id}/stages/{stage_id}")
async def process_stage_save(process_id: str, stage_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    """The stage form: every non-file field of that stage. An unticked
    checkbox isn't sent by the browser, so its absence means False."""
    user = await require_permission(request, db, svc.MODULE, "read")
    process = await _load(request, db, process_id, lock=True)
    stage = next((s for s in process.stages if s.id == stage_id), None)
    if stage is None:
        raise HTTPException(status_code=404, detail=t_for(request, "processes.errors.stage_not_found"))
    form = await request.form()
    values = {}
    for field in stage.fields:
        name = f"field-{field.id}"
        if field.kind == ProcessFieldKind.FILE:
            continue
        if field.kind == ProcessFieldKind.CHECKBOX:
            values[field.id] = form.get(name) == "1"
        elif name in form:
            values[field.id] = form.get(name)
    try:
        await svc.set_fields(db, process, values, user)
    except ServiceError as e:
        return await _fail(request, db, _process_url(process_id), e, f"stage-{stage_id}")
    return _redirect(_process_url(process_id), f"stage-{stage_id}")


@router.post("/{process_id}/advance")
async def process_advance(process_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_permission(request, db, svc.MODULE, "read")
    process = await _load(request, db, process_id, lock=True)
    try:
        await svc.advance(db, process, user)
    except ServiceError as e:
        return await _fail(request, db, _process_url(process_id), e)
    return _redirect(_process_url(process_id))


@router.post("/{process_id}/back")
async def process_back(process_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_permission(request, db, svc.MODULE, "read")
    process = await _load(request, db, process_id, lock=True)
    form = await request.form()
    try:
        position = int(str(form.get("to_position") or "-1"))
    except ValueError:
        position = -1
    try:
        await svc.go_back(db, process, position, str(form.get("reason") or ""), user)
    except ServiceError as e:
        return await _fail(request, db, _process_url(process_id), e)
    return _redirect(_process_url(process_id))


@router.post("/{process_id}/abort")
async def process_abort(process_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_permission(request, db, svc.MODULE, "read")
    process = await _load(request, db, process_id, lock=True)
    form = await request.form()
    try:
        await svc.abort(db, process, str(form.get("reason") or ""), user)
    except ServiceError as e:
        return await _fail(request, db, _process_url(process_id), e)
    return _redirect(_process_url(process_id))


@router.post("/{process_id}/delete")
async def process_delete(process_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_permission(request, db, svc.MODULE, "read")
    process = await _load(request, db, process_id, lock=True)
    try:
        await svc.delete_process(db, process, user)
    except ServiceError as e:
        return await _fail(request, db, _process_url(process_id), e)
    return _redirect("/processes/")


@router.post("/{process_id}/fields/{field_id}/files")
async def process_file_upload(
    process_id: str, field_id: str, request: Request, file: UploadFile, db: AsyncSession = Depends(get_db),
):
    user = await require_permission(request, db, svc.MODULE, "read")
    process = await _load(request, db, process_id, lock=True)
    content = await file.read(svc.MAX_FILE_BYTES + 1)
    try:
        await svc.store_file(db, process, field_id, user, content=content, filename=file.filename)
    except ServiceError as e:
        return await _fail(request, db, _process_url(process_id), e, f"field-{field_id}")
    return _redirect(_process_url(process_id), f"field-{field_id}")


@router.get("/{process_id}/files/{file_id}")
async def process_file_download(process_id: str, file_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    await require_permission(request, db, svc.MODULE, "read")
    process = await _load(request, db, process_id)
    try:
        record, content = await svc.read_file(db, process, file_id)
    except ServiceError as e:
        raise HTTPException(status_code=e.http_status, detail=t_for(request, e.key))
    disposition = "inline" if record.is_image else "attachment"
    return Response(content=content, media_type=record.content_type, headers={
        "Content-Disposition": content_disposition(record.original_name, disposition),
        "Cache-Control": "private, no-store",
    })


@router.post("/{process_id}/files/{file_id}/delete")
async def process_file_delete(process_id: str, file_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_permission(request, db, svc.MODULE, "read")
    process = await _load(request, db, process_id, lock=True)
    try:
        await svc.delete_file(db, process, file_id, user)
    except ServiceError as e:
        return await _fail(request, db, _process_url(process_id), e)
    return _redirect(_process_url(process_id))


async def subject_processes(request: Request, db: AsyncSession, kind: ProcessSubjectKind, subject_id: str):
    """For the "Processes" card on a plot/member/applicant page: the
    subject's processes, or None when the module is off or the user may
    not read it (the card is then not shown)."""
    flags = getattr(request.state, "module_flags", {})
    permissions = getattr(request.state, "permissions", {}) or {}
    if not flags.get(svc.MODULE, True) or not permissions.get(svc.MODULE, {}).get("read"):
        return None
    return await svc.processes_for_subject(db, kind, subject_id)
