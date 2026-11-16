"""
API router: Processes (issue #331, ADR 0135, docs/module-processes.md).

Business logic shared with app/routers/processes.py (HTML) lives in
app/services/processes.py (ADR 0070). Files are listed as metadata only;
uploading and downloading them is a web-side feature for now. Templates
are read-only here -- they're built in the web editor.
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api_auth import require_api_permission
from app.database import get_db
from app.i18n import t_for
from app.models import Process, User
from app.module_flags import require_module
from app.schemas import (
    ProcessAbort, ProcessBack, ProcessDetailOut, ProcessFieldUpdate, ProcessOut, ProcessStart, ProcessTemplateOut,
)
from app.services import processes as svc
from app.services.errors import ServiceError

router = APIRouter(
    prefix="/api/v1/processes",
    tags=["API: Processes"],
    dependencies=[Depends(require_module(svc.MODULE))],
)
template_router = APIRouter(
    prefix="/api/v1/process-templates",
    tags=["API: Processes"],
    dependencies=[Depends(require_module(svc.MODULE))],
)


def _service_error(request: Request, error: ServiceError) -> HTTPException:
    code = error.http_status if error.http_status in (403, 404, 409, 502) else status.HTTP_422_UNPROCESSABLE_ENTITY
    detail = t_for(request, error.key)
    if error.params.get("fields"):
        detail = f"{detail} {error.params['fields']}"
    return HTTPException(status_code=code, detail=detail)


def _detail(process: Process) -> ProcessDetailOut:
    out = ProcessDetailOut.model_validate(process)
    by_id = {f.id: f for s in process.stages for f in s.fields}
    for stage in out.stages:
        for field in stage.fields:
            field.filled = svc.is_filled(by_id[field.id])
            field.display_value = svc.display_value(by_id[field.id])
    return out


async def _load(request: Request, db: AsyncSession, process_id: str, *, lock: bool = False) -> Process:
    try:
        return await svc.get_process(db, process_id, lock=lock)
    except ServiceError as e:
        raise _service_error(request, e)


@template_router.get("", response_model=List[ProcessTemplateOut], summary="List process templates")
async def templates_list(
    include_archived: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission(svc.MODULE, "read")),
):
    return await svc.list_templates(db, include_archived=include_archived)


@router.get("", response_model=List[ProcessOut], summary="List processes")
async def processes_list(
    status_filter: str = Query("open", alias="status", description="open, closed or all"),
    template_id: str = Query(""),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission(svc.MODULE, "read")),
):
    filters = svc.ProcessFilter(status=status_filter if status_filter in ("open", "closed", "all") else "open",
                                template_id=template_id)
    return await svc.list_processes(db, filters, limit=limit, offset=offset)


@router.post("", response_model=ProcessDetailOut, status_code=201, summary="Start a process from a template")
async def process_start(
    data: ProcessStart, request: Request, db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission(svc.MODULE, "write")),
):
    try:
        process = await svc.start_process(
            db, user, template_id=data.template_id, title=data.title, subject_id=data.subject_id,
        )
    except ServiceError as e:
        await db.rollback()
        raise _service_error(request, e)
    return _detail(process)


@router.get("/{process_id}", response_model=ProcessDetailOut, summary="A process with its stages, fields and history")
async def process_detail(
    process_id: str, request: Request, db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission(svc.MODULE, "read")),
):
    return _detail(await _load(request, db, process_id))


async def _change(request: Request, db: AsyncSession, process_id: str, action) -> ProcessDetailOut:
    process = await _load(request, db, process_id, lock=True)
    try:
        await action(process)
    except ServiceError as e:
        await db.rollback()
        raise _service_error(request, e)
    return _detail(await svc.get_process(db, process_id))


@router.put("/{process_id}/fields/{field_id}", response_model=ProcessDetailOut, summary="Set a field's value")
async def process_field_set(
    process_id: str, field_id: str, data: ProcessFieldUpdate, request: Request, db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission(svc.MODULE, "write")),
):
    async def action(process):
        await svc.set_field(db, process, field_id, data.value, user)
    return await _change(request, db, process_id, action)


@router.post("/{process_id}/advance", response_model=ProcessDetailOut, summary="Complete the current stage")
async def process_advance(
    process_id: str, request: Request, db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission(svc.MODULE, "write")),
):
    async def action(process):
        await svc.advance(db, process, user)
    return await _change(request, db, process_id, action)


@router.post("/{process_id}/back", response_model=ProcessDetailOut, summary="Go back to an earlier stage")
async def process_back(
    process_id: str, data: ProcessBack, request: Request, db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission(svc.MODULE, "write")),
):
    async def action(process):
        await svc.go_back(db, process, data.to_position, data.reason, user)
    return await _change(request, db, process_id, action)


@router.post("/{process_id}/abort", response_model=ProcessDetailOut, summary="Abort the process")
async def process_abort(
    process_id: str, data: ProcessAbort, request: Request, db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission(svc.MODULE, "delete")),
):
    async def action(process):
        await svc.abort(db, process, data.reason, user)
    return await _change(request, db, process_id, action)
