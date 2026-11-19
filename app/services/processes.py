"""
Processes (issue #331, ADR 0136, docs/module-processes.md): a club builds
its own process templates -- ordered stages, each with its own field set
-- and runs processes from them, optionally attached to a plot, a member
or an applicant. Called by app/routers/processes.py (HTML) and
app/routers/api_processes.py (API), same split as ADR 0070.

The rules are deliberately few and generic:
- Starting a process copies the template's stages and fields (a
  snapshot): later template edits never change a running process.
- A process moves forward one stage at a time, and only once every
  required field of the current stage is filled.
- It can go back to any earlier stage, with a reason; values are kept.
- Aborting needs a reason; a closed process is read-only.
- Every change writes a ProcessEvent.

Permissions (module "processes"): read to look, write to start and work
on processes, delete to abort or delete one. Templates are edited with
full access only (ADMIN/BOARD), like the task board's lists (ADR 0044).
"""
import re
import uuid
from dataclasses import dataclass
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.cloud_storage import CloudStorageError, get_cloud_storage_provider
from app.contact_documents import upload_filename
from app.i18n import translate
from app.models import (
    Applicant, ClubSetting, Member, MemberParcel, Parcel, Process, ProcessEvent, ProcessEventKind, ProcessField,
    ProcessFieldKind, ProcessFile, ProcessFileStorage, ProcessStage, ProcessStatus, ProcessSubjectKind,
    ProcessTemplate, ProcessTemplateField, ProcessTemplateStage, User,
)
from app.module_flags import load_module_flags
from app.database import current_tenant_filter
from app.note_files import slugify
from app.parcel_cloud_folders import InvalidCloudPathError, get_active_folder, sanitize_relative_path
from app.permissions import get_user_permissions, has_permission, is_full_access_user
from app.l10n import parse_decimal
from app.services.errors import ServiceError

MODULE = "processes"
CLOUD_FOLDER_SETTING = "processes_cloud_folder"

K = ProcessFieldKind
_ERR = "processes.errors."
_MAX_TEXT = 20000
_MAX_NAME = 200
_MAX_OPTIONS = 50


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _clean(value: Optional[str], limit: int = _MAX_TEXT) -> Optional[str]:
    value = (value or "").strip()
    return value[:limit] or None


def _required_name(value: Optional[str]) -> str:
    name = _clean(value, _MAX_NAME)
    if not name:
        raise ServiceError(_ERR + "name_required")
    return name


# ---------------------------------------------------------------------------
# Permissions
# ---------------------------------------------------------------------------

async def can(db: AsyncSession, user: Optional[User], level: str) -> bool:
    """level: read/write/delete on "processes", or "templates" (full access)."""
    if user is None:
        return False
    if level == "templates":
        return await is_full_access_user(db, user)
    return has_permission(await get_user_permissions(db, user), MODULE, level)


async def _require(db: AsyncSession, user: Optional[User], level: str) -> None:
    if not await can(db, user, level):
        raise ServiceError("errors.no_permission", http_status=403)


# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------

def _template_options():
    return (selectinload(ProcessTemplate.stages).selectinload(ProcessTemplateStage.fields),)


async def list_templates(db: AsyncSession, *, include_archived: bool = True) -> list[ProcessTemplate]:
    query = select(ProcessTemplate).options(*_template_options()).order_by(
        ProcessTemplate.is_active.desc(), func.lower(ProcessTemplate.name)
    )
    if not include_archived:
        query = query.where(ProcessTemplate.is_active.is_(True))
    return list((await db.scalars(query)).all())


async def get_template(db: AsyncSession, template_id: str) -> ProcessTemplate:
    template = await db.scalar(
        select(ProcessTemplate).options(*_template_options())
        .where(ProcessTemplate.id == template_id).execution_options(populate_existing=True)
    )
    if template is None:
        raise ServiceError(_ERR + "template_not_found", http_status=404)
    return template


async def template_usage(db: AsyncSession, template_id: str) -> int:
    return await db.scalar(select(func.count()).select_from(Process).where(Process.template_id == template_id)) or 0


def _subject_kind(value: Any) -> ProcessSubjectKind:
    try:
        return ProcessSubjectKind(value or "NONE")
    except ValueError:
        raise ServiceError(_ERR + "invalid_subject_kind")


async def create_template(
    db: AsyncSession, user: Optional[User], *, name: str, description: Optional[str] = None, subject_kind: Any = "NONE",
) -> ProcessTemplate:
    await _require(db, user, "templates")
    template = ProcessTemplate(
        name=_required_name(name), description=_clean(description), subject_kind=_subject_kind(subject_kind),
        created_by_id=user.id if user else None,
    )
    db.add(template)
    await db.commit()
    return await get_template(db, template.id)


async def update_template(
    db: AsyncSession, template: ProcessTemplate, user: Optional[User], *,
    name: str, description: Optional[str], subject_kind: Any,
) -> None:
    await _require(db, user, "templates")
    template.name = _required_name(name)
    template.description = _clean(description)
    template.subject_kind = _subject_kind(subject_kind)
    await db.commit()


async def set_template_active(db: AsyncSession, template: ProcessTemplate, user: Optional[User], active: bool) -> None:
    await _require(db, user, "templates")
    template.is_active = active
    await db.commit()


async def delete_template(db: AsyncSession, template: ProcessTemplate, user: Optional[User]) -> None:
    """Only a template nothing was started from -- otherwise archive it
    (ADR 0005)."""
    await _require(db, user, "templates")
    if await template_usage(db, template.id):
        raise ServiceError(_ERR + "template_in_use", http_status=409)
    await db.delete(template)
    await db.commit()


def _stage(template: ProcessTemplate, stage_id: str) -> ProcessTemplateStage:
    stage = next((s for s in template.stages if s.id == stage_id), None)
    if stage is None:
        raise ServiceError(_ERR + "stage_not_found", http_status=404)
    return stage


def _template_field(template: ProcessTemplate, field_id: str) -> ProcessTemplateField:
    for stage in template.stages:
        for field in stage.fields:
            if field.id == field_id:
                return field
    raise ServiceError(_ERR + "field_not_found", http_status=404)


def _renumber(items) -> None:
    for index, item in enumerate(items):
        item.position = index


def _move(items: list, item, direction: str) -> None:
    items = list(items)
    index = items.index(item)
    target = index - 1 if direction == "up" else index + 1
    if 0 <= target < len(items):
        items[index], items[target] = items[target], items[index]
    _renumber(items)


async def add_stage(
    db: AsyncSession, template: ProcessTemplate, user: Optional[User], *, name: str, description: Optional[str] = None,
) -> ProcessTemplateStage:
    await _require(db, user, "templates")
    stage = ProcessTemplateStage(name=_required_name(name), description=_clean(description), position=len(template.stages))
    template.stages.append(stage)
    await db.commit()
    return stage


async def update_stage(
    db: AsyncSession, template: ProcessTemplate, stage_id: str, user: Optional[User], *,
    name: str, description: Optional[str],
) -> None:
    await _require(db, user, "templates")
    stage = _stage(template, stage_id)
    stage.name = _required_name(name)
    stage.description = _clean(description)
    await db.commit()


async def delete_stage(db: AsyncSession, template: ProcessTemplate, stage_id: str, user: Optional[User]) -> None:
    await _require(db, user, "templates")
    stage = _stage(template, stage_id)
    template.stages.remove(stage)
    _renumber(template.stages)
    await db.commit()


async def move_stage(db: AsyncSession, template: ProcessTemplate, stage_id: str, direction: str, user: Optional[User]) -> None:
    await _require(db, user, "templates")
    _move(template.stages, _stage(template, stage_id), direction)
    await db.commit()


def _reorder(items: list, ids: list[str]) -> None:
    """Puts `items` in the order of `ids` (drag and drop). The ids must be
    exactly the items' ids -- a stale page refuses rather than guesses."""
    by_id = {item.id: item for item in items}
    if len(ids) != len(by_id) or set(ids) != set(by_id):
        raise ServiceError(_ERR + "stale_order", http_status=409)
    items.sort(key=lambda item: ids.index(item.id))
    _renumber(items)


async def reorder_stages(db: AsyncSession, template: ProcessTemplate, ids: list[str], user: Optional[User]) -> None:
    await _require(db, user, "templates")
    _reorder(template.stages, ids)
    await db.commit()


async def reorder_fields(
    db: AsyncSession, template: ProcessTemplate, stage_id: str, ids: list[str], user: Optional[User],
) -> None:
    await _require(db, user, "templates")
    _reorder(_stage(template, stage_id).fields, ids)
    await db.commit()


async def move_field_to_stage(
    db: AsyncSession, template: ProcessTemplate, field_id: str, stage_id: str, user: Optional[User],
) -> None:
    """Moves a field to the end of another stage of the same template."""
    await _require(db, user, "templates")
    field = _template_field(template, field_id)
    target = _stage(template, stage_id)
    if target is field.stage:
        return
    source = field.stage
    source.fields.remove(field)
    _renumber(source.fields)
    field.position = len(target.fields)
    target.fields.append(field)
    await db.commit()


async def duplicate_field(db: AsyncSession, template: ProcessTemplate, field_id: str, user: Optional[User]) -> ProcessTemplateField:
    """A copy right below the original, labelled the same."""
    await _require(db, user, "templates")
    field = _template_field(template, field_id)
    stage = field.stage
    copy = ProcessTemplateField(
        kind=field.kind, label=field.label, help_text=field.help_text, required=field.required,
        options=list(field.options) if field.options else None, position=0,
    )
    stage.fields.insert(stage.fields.index(field) + 1, copy)
    _renumber(stage.fields)
    await db.commit()
    return copy


def _field_kind(value: Any) -> ProcessFieldKind:
    try:
        return ProcessFieldKind(value)
    except ValueError:
        raise ServiceError(_ERR + "invalid_field_kind")


def parse_options(raw: Any) -> list[str]:
    """CHOICE options: one per line (a list from the API)."""
    lines = raw if isinstance(raw, list) else str(raw or "").splitlines()
    options: list[str] = []
    for line in lines:
        option = _clean(str(line), _MAX_NAME)
        if option and option not in options:
            options.append(option)
    return options[:_MAX_OPTIONS]


def _field_definition(kind: ProcessFieldKind, label: str, help_text: Optional[str], required: bool, options: Any) -> dict:
    opts = parse_options(options) if kind == K.CHOICE else None
    if kind == K.CHOICE and not opts:
        raise ServiceError(_ERR + "choice_needs_options")
    return {
        "kind": kind, "label": _required_name(label), "help_text": _clean(help_text, 2000),
        "required": bool(required), "options": opts,
    }


async def add_field(
    db: AsyncSession, template: ProcessTemplate, stage_id: str, user: Optional[User], *,
    kind: Any, label: str, help_text: Optional[str] = None, required: bool = False, options: Any = None,
) -> ProcessTemplateField:
    await _require(db, user, "templates")
    stage = _stage(template, stage_id)
    field = ProcessTemplateField(
        position=len(stage.fields), **_field_definition(_field_kind(kind), label, help_text, required, options),
    )
    stage.fields.append(field)
    await db.commit()
    return field


async def update_field(
    db: AsyncSession, template: ProcessTemplate, field_id: str, user: Optional[User], *,
    kind: Any, label: str, help_text: Optional[str], required: bool, options: Any,
) -> None:
    await _require(db, user, "templates")
    field = _template_field(template, field_id)
    for key, value in _field_definition(_field_kind(kind), label, help_text, required, options).items():
        setattr(field, key, value)
    await db.commit()


async def delete_field(db: AsyncSession, template: ProcessTemplate, field_id: str, user: Optional[User]) -> None:
    await _require(db, user, "templates")
    field = _template_field(template, field_id)
    field.stage.fields.remove(field)
    _renumber(field.stage.fields)
    await db.commit()


async def move_field(db: AsyncSession, template: ProcessTemplate, field_id: str, direction: str, user: Optional[User]) -> None:
    await _require(db, user, "templates")
    field = _template_field(template, field_id)
    _move(field.stage.fields, field, direction)
    await db.commit()


# ---------------------------------------------------------------------------
# Built-in examples: a starting point, created in the user's language and
# then just an ordinary template the club edits. Labels come from
# processes.examples.<key>.* in the translation files.
# ---------------------------------------------------------------------------

EXAMPLES: dict[str, dict] = {
    "plot_handover": {
        "subject": ProcessSubjectKind.PARCEL,
        "stages": [
            ("inspection", [("inspection_date", K.DATE, True), ("defects", K.LONG_TEXT, False),
                            ("defect_photos", K.FILE, False), ("defects_resolved", K.CHECKBOX, True)]),
            ("valuation", [("appraiser", K.TEXT, True), ("valuation_date", K.DATE, True),
                           ("valuation_report", K.FILE, True)]),
            ("listing", [("listing_text", K.LONG_TEXT, True), ("listing_photos", K.FILE, False),
                         ("published_on", K.DATE, True)]),
            ("buyer", [("new_tenant", K.APPLICANT, True), ("contact_established", K.CHECKBOX, True),
                       ("documents_sent", K.CHECKBOX, True)]),
            ("contract", [("agreement_confirmed", K.CHECKBOX, True), ("deposit_amount", K.MONEY, False),
                          ("deposit_received_on", K.DATE, False)]),
            ("closing", [("signed_by_tenant", K.CHECKBOX, True), ("countersigned_by_board", K.CHECKBOX, True),
                         ("keys_handed_over", K.CHECKBOX, True), ("meters_read", K.CHECKBOX, True),
                         ("closing_protocol", K.FILE, False)]),
        ],
    },
    "member_onboarding": {
        "subject": ProcessSubjectKind.MEMBER,
        "stages": [
            ("welcome", [("welcome_meeting", K.DATE, True), ("statutes_handed_over", K.CHECKBOX, True)]),
            ("paperwork", [("membership_form", K.FILE, True), ("direct_debit_mandate", K.CHECKBOX, False)]),
            ("done", [("added_to_mailing_list", K.CHECKBOX, False), ("notes", K.LONG_TEXT, False)]),
        ],
    },
}


async def create_from_example(db: AsyncSession, user: Optional[User], key: str, lang: str) -> ProcessTemplate:
    await _require(db, user, "templates")
    example = EXAMPLES.get(key)
    if example is None:
        raise ServiceError(_ERR + "example_not_found", http_status=404)
    base = f"processes.examples.{key}"
    template = ProcessTemplate(
        name=translate(f"{base}.name", lang), description=translate(f"{base}.description", lang),
        subject_kind=example["subject"], created_by_id=user.id if user else None,
    )
    for s_index, (stage_key, fields) in enumerate(example["stages"]):
        stage = ProcessTemplateStage(position=s_index, name=translate(f"{base}.stages.{stage_key}", lang))
        for f_index, (field_key, kind, required) in enumerate(fields):
            stage.fields.append(ProcessTemplateField(
                position=f_index, kind=kind, required=required,
                label=translate(f"processes.examples.fields.{field_key}", lang),
            ))
        template.stages.append(stage)
    db.add(template)
    await db.commit()
    return await get_template(db, template.id)


# ---------------------------------------------------------------------------
# Processes: loading
# ---------------------------------------------------------------------------

def _process_options():
    fields = selectinload(Process.stages).selectinload(ProcessStage.fields)
    return (
        selectinload(Process.parcel), selectinload(Process.member), selectinload(Process.applicant),
        selectinload(Process.created_by),
        selectinload(Process.stages).selectinload(ProcessStage.completed_by),
        fields.selectinload(ProcessField.value_member),
        fields.selectinload(ProcessField.value_applicant),
        fields.selectinload(ProcessField.value_parcel),
        fields.selectinload(ProcessField.updated_by),
        fields.selectinload(ProcessField.files).selectinload(ProcessFile.uploaded_by),
        selectinload(Process.events).selectinload(ProcessEvent.user),
    )


async def get_process(db: AsyncSession, process_id: str, *, lock: bool = False) -> Process:
    query = (
        select(Process).options(*_process_options()).where(Process.id == process_id)
        .execution_options(populate_existing=True)
    )
    if lock:
        query = query.with_for_update(of=Process)
    process = await db.scalar(query)
    if process is None:
        raise ServiceError(_ERR + "not_found", http_status=404)
    return process


@dataclass
class ProcessFilter:
    status: str = "open"          # open / closed / all
    template_id: str = ""

    def apply(self):
        query = select(Process).options(
            selectinload(Process.parcel), selectinload(Process.member), selectinload(Process.applicant),
            selectinload(Process.stages),
        )
        if self.status == "open":
            query = query.where(Process.status == ProcessStatus.OPEN)
        elif self.status == "closed":
            query = query.where(Process.status != ProcessStatus.OPEN)
        if self.template_id:
            query = query.where(Process.template_id == self.template_id)
        return query.order_by(Process.status, Process.created_at.desc())


async def list_processes(db: AsyncSession, filters: ProcessFilter, *, limit: int = 500, offset: int = 0) -> list[Process]:
    return list((await db.scalars(filters.apply().limit(limit).offset(offset))).all())


async def processes_for_subject(db: AsyncSession, kind: ProcessSubjectKind, subject_id: str) -> list[Process]:
    column = {
        ProcessSubjectKind.PARCEL: Process.parcel_id, ProcessSubjectKind.MEMBER: Process.member_id,
        ProcessSubjectKind.APPLICANT: Process.applicant_id,
    }[kind]
    return list((await db.scalars(
        select(Process).options(selectinload(Process.stages))
        .where(column == subject_id).order_by(Process.status, Process.created_at.desc())
    )).all())


async def count_open(db: AsyncSession) -> int:
    return await db.scalar(select(func.count()).select_from(Process).where(Process.status == ProcessStatus.OPEN)) or 0


def current_stage(process: Process) -> Optional[ProcessStage]:
    return next((s for s in process.stages if s.position == process.current_position), None)


def subject_label(process: Process) -> Optional[str]:
    if process.parcel is not None:
        return process.parcel.plot_number
    if process.member is not None:
        return process.member.full_name
    if process.applicant is not None:
        return process.applicant.display_name
    return None


# ---------------------------------------------------------------------------
# Processes: field values
# ---------------------------------------------------------------------------

def is_filled(field: ProcessField) -> bool:
    if field.kind == K.CHECKBOX:
        return bool(field.value_bool)
    if field.kind == K.FILE:
        return bool(field.files)
    if field.kind in (K.NUMBER, K.MONEY):
        return field.value_number is not None
    if field.kind == K.DATE:
        return field.value_date is not None
    if field.kind == K.MEMBER:
        return field.value_member_id is not None
    if field.kind == K.APPLICANT:
        return field.value_applicant_id is not None
    if field.kind == K.PARCEL:
        return field.value_parcel_id is not None
    return bool(field.value_text)


def missing_fields(stage: Optional[ProcessStage]) -> list[ProcessField]:
    """The required fields of a stage still empty -- what blocks advancing."""
    if stage is None:
        return []
    return [f for f in stage.fields if f.required and not is_filled(f)]


def display_value(field: ProcessField) -> str:
    """Plain-text value, for the audit trail and the API (the web page
    formats numbers and dates by region itself)."""
    if field.kind == K.CHECKBOX:
        return "✓" if field.value_bool else "–"
    if field.kind in (K.NUMBER, K.MONEY):
        return "" if field.value_number is None else str(field.value_number)
    if field.kind == K.DATE:
        return field.value_date.isoformat() if field.value_date else ""
    if field.kind == K.MEMBER:
        return field.value_member.full_name if field.value_member else ""
    if field.kind == K.APPLICANT:
        return field.value_applicant.display_name if field.value_applicant else ""
    if field.kind == K.PARCEL:
        return field.value_parcel.plot_number if field.value_parcel else ""
    if field.kind == K.FILE:
        return ", ".join(f.original_name for f in field.files)
    return field.value_text or ""


def parse_number(value: Any) -> Optional[Decimal]:
    """Accepts a comma or a point as the decimal separator, and spaces or
    the other separator as thousands separators ("1.234,50", "1,234.50")."""
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    if isinstance(value, (int, float, Decimal)) and not isinstance(value, bool):
        number = Decimal(str(value))
    else:
        number = parse_decimal(value)  # shared with finances/metering since issue #350
        if number is None:
            raise ServiceError(_ERR + "invalid_number")
    if not number.is_finite() or abs(number) >= Decimal("1e12"):
        raise ServiceError(_ERR + "invalid_number")
    return number.quantize(Decimal("0.01"))


def _parse_date(value: Any) -> Optional[date]:
    if isinstance(value, date):
        return value
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return date.fromisoformat(text)
    except ValueError:
        raise ServiceError(_ERR + "invalid_date")


def _parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value or "").strip().lower() in ("1", "true", "on", "yes")


async def _reference(db: AsyncSession, model, value: Any) -> Optional[str]:
    text = str(value or "").strip()
    if not text:
        return None
    if await db.get(model, text) is None:
        raise ServiceError(_ERR + "invalid_reference")
    return text


def _field(process: Process, field_id: str) -> ProcessField:
    for stage in process.stages:
        for field in stage.fields:
            if field.id == field_id:
                return field
    raise ServiceError(_ERR + "field_not_found", http_status=404)


def _require_open(process: Process) -> None:
    if process.status != ProcessStatus.OPEN:
        raise ServiceError(_ERR + "process_closed", http_status=409)


def _require_editable(process: Process, field: ProcessField) -> None:
    """Fields of the current stage and the stages before it -- not of
    stages not reached yet."""
    _require_open(process)
    if field.stage.position > process.current_position:
        raise ServiceError(_ERR + "stage_not_reached", http_status=409)


def _event(process: Process, kind: ProcessEventKind, user: Optional[User], *,
           stage: Optional[ProcessStage] = None, note: Optional[str] = None) -> None:
    process.events.append(ProcessEvent(
        kind=kind, stage_name=stage.name if stage else None, note=_clean(note, 4000),
        user_id=user.id if user else None, created_at=_now(),
    ))


async def set_field(
    db: AsyncSession, process: Process, field_id: str, value: Any, user: Optional[User], *, commit: bool = True,
) -> None:
    """Sets one field's value from a form string or an API value. FILE
    fields go through store_file()/delete_file() instead."""
    await _require(db, user, "write")
    field = _field(process, field_id)
    _require_editable(process, field)
    before = display_value(field)

    if field.kind in (K.TEXT,):
        field.value_text = _clean(value, 1000)
    elif field.kind == K.LONG_TEXT:
        field.value_text = _clean(value)
    elif field.kind in (K.NUMBER, K.MONEY):
        field.value_number = parse_number(value)
    elif field.kind == K.DATE:
        field.value_date = _parse_date(value)
    elif field.kind == K.CHECKBOX:
        field.value_bool = _parse_bool(value)
    elif field.kind == K.CHOICE:
        choice = _clean(value, _MAX_NAME)
        if choice and choice not in (field.options or []):
            raise ServiceError(_ERR + "invalid_choice")
        field.value_text = choice
    elif field.kind == K.MEMBER:
        field.value_member_id = await _reference(db, Member, value)
    elif field.kind == K.APPLICANT:
        await _require_applicants_read(db, user)
        field.value_applicant_id = await _reference(db, Applicant, value)
    elif field.kind == K.PARCEL:
        field.value_parcel_id = await _reference(db, Parcel, value)
    else:
        raise ServiceError(_ERR + "invalid_field_kind")

    await db.flush()
    await db.refresh(field, attribute_names=["value_member", "value_applicant", "value_parcel"])
    after = display_value(field)
    if after != before:
        field.updated_at = _now()
        field.updated_by_id = user.id if user else None
        # An applicant's name isn't copied into the history: applicants
        # are purged after the retention period (ADR 0091), and the
        # audit trail would otherwise keep their name around.
        note = field.label if field.kind == K.APPLICANT else f"{field.label}: {before or '–'} → {after or '–'}"
        _event(process, ProcessEventKind.FIELD_CHANGED, user, stage=field.stage, note=note)
    if commit:
        await db.commit()


async def set_fields(db: AsyncSession, process: Process, values: dict[str, Any], user: Optional[User]) -> None:
    """Several fields at once (the stage form). A field id that isn't in
    `values` is left alone -- except checkboxes of the given stage, which
    a browser doesn't send when unticked; the caller passes those as False.
    All or nothing: one invalid value saves none of them."""
    for field_id, value in values.items():
        await set_field(db, process, field_id, value, user, commit=False)
    await db.commit()


# ---------------------------------------------------------------------------
# Processes: lifecycle
# ---------------------------------------------------------------------------

async def _require_applicants_read(db: AsyncSession, user: Optional[User]) -> None:
    """Picking an applicant shows and links applicant data -- that's the
    applicants module's, so it needs read there too (security review)."""
    if user is None or not has_permission(await get_user_permissions(db, user), "applicants", "read"):
        raise ServiceError("errors.no_permission", http_status=403)


async def _subject(db: AsyncSession, kind: ProcessSubjectKind, subject_id: Optional[str], user: Optional[User]) -> dict:
    if kind == ProcessSubjectKind.NONE:
        return {}
    if kind == ProcessSubjectKind.APPLICANT:
        await _require_applicants_read(db, user)
    model, column = {
        ProcessSubjectKind.PARCEL: (Parcel, "parcel_id"),
        ProcessSubjectKind.MEMBER: (Member, "member_id"),
        ProcessSubjectKind.APPLICANT: (Applicant, "applicant_id"),
    }[kind]
    if not subject_id or await db.get(model, subject_id) is None:
        raise ServiceError(_ERR + "subject_required")
    return {column: subject_id}


async def start_process(
    db: AsyncSession, user: Optional[User], *, template_id: str, title: Optional[str] = None,
    subject_id: Optional[str] = None,
) -> Process:
    await _require(db, user, "write")
    template = await get_template(db, template_id)
    if not template.is_active:
        raise ServiceError(_ERR + "template_archived", http_status=409)
    if not template.stages:
        raise ServiceError(_ERR + "template_without_stages", http_status=409)
    process = Process(
        template_id=template.id, template_name=template.name, subject_kind=template.subject_kind,
        title=_clean(title, _MAX_NAME) or template.name, status=ProcessStatus.OPEN, current_position=0,
        created_by_id=user.id if user else None,
        **await _subject(db, template.subject_kind, subject_id, user),
    )
    for t_stage in template.stages:
        stage = ProcessStage(position=t_stage.position, name=t_stage.name, description=t_stage.description)
        for t_field in t_stage.fields:
            stage.fields.append(ProcessField(
                position=t_field.position, label=t_field.label, help_text=t_field.help_text, kind=t_field.kind,
                required=t_field.required, options=list(t_field.options) if t_field.options else None,
            ))
        process.stages.append(stage)
    process.events = []
    _event(process, ProcessEventKind.CREATED, user, stage=process.stages[0])
    db.add(process)
    await db.commit()
    return await get_process(db, process.id)


async def advance(db: AsyncSession, process: Process, user: Optional[User]) -> None:
    await _require(db, user, "write")
    _require_open(process)
    stage = current_stage(process)
    missing = missing_fields(stage)
    if missing:
        raise ServiceError(_ERR + "missing_fields", http_status=409, fields=", ".join(f.label for f in missing))
    stage.completed_at = _now()
    stage.completed_by_id = user.id if user else None
    if process.current_position >= max(s.position for s in process.stages):
        process.status = ProcessStatus.COMPLETED
        process.closed_at = _now()
        _event(process, ProcessEventKind.COMPLETED, user, stage=stage)
    else:
        process.current_position = min(s.position for s in process.stages if s.position > stage.position)
        _event(process, ProcessEventKind.ADVANCED, user, stage=current_stage(process))
    await db.commit()


async def go_back(db: AsyncSession, process: Process, to_position: int, reason: Optional[str], user: Optional[User]) -> None:
    await _require(db, user, "write")
    _require_open(process)
    if not _clean(reason):
        raise ServiceError(_ERR + "reason_required")
    if to_position >= process.current_position or to_position not in {s.position for s in process.stages}:
        raise ServiceError(_ERR + "invalid_stage")
    for stage in process.stages:
        if stage.position >= to_position:
            stage.completed_at = None
            stage.completed_by_id = None
    process.current_position = to_position
    _event(process, ProcessEventKind.REVERTED, user, stage=current_stage(process), note=reason)
    await db.commit()


async def abort(db: AsyncSession, process: Process, reason: Optional[str], user: Optional[User]) -> None:
    await _require(db, user, "delete")
    _require_open(process)
    if not _clean(reason):
        raise ServiceError(_ERR + "reason_required")
    process.status = ProcessStatus.ABORTED
    process.abort_reason = _clean(reason)
    process.closed_at = _now()
    _event(process, ProcessEventKind.ABORTED, user, stage=current_stage(process), note=reason)
    await db.commit()


async def delete_process(db: AsyncSession, process: Process, user: Optional[User]) -> None:
    """A process started by mistake. Local files go with it; cloud files
    stay in the club's cloud (Parcella never deletes club files there)."""
    await _require(db, user, "delete")
    paths = [local_path(f) for stage in process.stages for field in stage.fields for f in field.files
             if f.storage == ProcessFileStorage.LOCAL]
    await db.delete(process)
    await db.commit()
    for path in paths:
        if path.is_file():
            path.unlink()


# ---------------------------------------------------------------------------
# Files: in the club's cloud folder when the cloud_storage module is on and
# processes_cloud_folder is set, otherwise a private local directory on the
# persisted uploads volume (./data/uploads, ADR 0077) -- part of every
# backup, and blocked from /static in app/main.py. The only way to a file
# is read_file() behind the permission-checked download route (ADR 0136).
# ---------------------------------------------------------------------------

LOCAL_DIR = Path("app/static/uploads/private/processes")
MAX_FILE_BYTES = 20 * 1024 * 1024
ALLOWED_FILE_TYPES = {
    "application/pdf": ".pdf",
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


def _sniff(content: bytes) -> Optional[str]:
    """The type from the file's first bytes -- the browser's claim isn't
    trusted."""
    if content.startswith(b"%PDF-"):
        return "application/pdf"
    if content.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if content.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if content[:4] == b"RIFF" and content[8:12] == b"WEBP":
        return "image/webp"
    return None


def _safe_name(raw: Optional[str]) -> str:
    try:
        name = upload_filename(raw)
    except InvalidCloudPathError:
        name = "file"
    return re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("._")[:120] or "file"


async def cloud_base_folder(db: AsyncSession) -> Optional[str]:
    if not (await load_module_flags(db)).get("cloud_storage"):
        return None
    base = await db.scalar(select(ClubSetting.value).where(ClubSetting.key == CLOUD_FOLDER_SETTING))
    if not (base or "").strip():
        return None
    try:
        return sanitize_relative_path(base)
    except InvalidCloudPathError:
        return None


async def subject_cloud_folder(db: AsyncSession, process: Process) -> Optional[str]:
    """The cloud folder already set up for the process's subject: the
    plot's active folder (parcel page, ADR 0102), or -- for a member --
    that of their only current plot. None for an applicant, a member with
    no or several current plots, or a plot without a folder."""
    if not (await load_module_flags(db)).get("cloud_storage"):
        return None
    parcel_id = process.parcel_id
    if parcel_id is None and process.member_id:
        parcel_ids = (await db.scalars(
            select(MemberParcel.parcel_id).where(MemberParcel.member_id == process.member_id, current_tenant_filter())
        )).all()
        parcel_id = parcel_ids[0] if len(set(parcel_ids)) == 1 else None
    if parcel_id is None:
        return None
    folder = await get_active_folder(db, parcel_id)
    if folder is None:
        return None
    try:
        return sanitize_relative_path(folder.relative_path)
    except InvalidCloudPathError:
        return None


def _process_folder_name(process: Process, label: str) -> str:
    return f"{slugify(label)[:60]}_{process.created_at:%Y-%m-%d}_{process.id[:8]}"


async def _cloud_folder(db: AsyncSession, process: Process) -> Optional[str]:
    """Where a process's files go in the cloud, or None for local storage:
    1. a subfolder of the subject's own folder (the plot's), if it has one;
    2. otherwise a subfolder of the processes folder (admin setting)."""
    subject_folder = await subject_cloud_folder(db, process)
    if subject_folder is not None:
        return f"{subject_folder}/{_process_folder_name(process, process.template_name or process.title or 'process')}"
    base = await cloud_base_folder(db)
    if base is None:
        return None
    # The plot number or the member's name -- never an applicant's name,
    # which outlives their purge (ADR 0091) in a cloud folder name.
    label = process.parcel.plot_number if process.parcel else (
        process.member.full_name if process.member else process.template_name
    )
    return f"{base}/{_process_folder_name(process, label or 'process')}"


async def upload_folder(db: AsyncSession, process: Process) -> Optional[str]:
    """Where the next upload goes (shown next to the upload form), or None
    for Parcella's private storage."""
    return await _cloud_folder(db, process)


def local_path(file: ProcessFile) -> Path:
    base = (LOCAL_DIR / file.field.stage.process_id).resolve()
    path = (base / file.stored_name).resolve()
    if base not in path.parents:
        raise ServiceError(_ERR + "file_not_found", http_status=404)
    return path


async def store_file(
    db: AsyncSession, process: Process, field_id: str, user: Optional[User], *, content: bytes, filename: Optional[str],
) -> ProcessFile:
    await _require(db, user, "write")
    field = _field(process, field_id)
    _require_editable(process, field)
    if field.kind != K.FILE:
        raise ServiceError(_ERR + "invalid_field_kind")
    if not content:
        raise ServiceError(_ERR + "file_empty")
    if len(content) > MAX_FILE_BYTES:
        raise ServiceError(_ERR + "file_too_large")
    content_type = _sniff(content)
    if content_type is None:
        raise ServiceError(_ERR + "file_type_not_allowed")

    original = _safe_name(filename)
    extension = ALLOWED_FILE_TYPES[content_type]
    stored_name = f"{uuid.uuid4().hex}{extension}"
    folder = await _cloud_folder(db, process)
    provider = await get_cloud_storage_provider(db) if folder else None
    if provider is not None:
        # People browse this folder in the cloud too: a readable, still
        # unique name instead of a bare uuid.
        raw = (filename or "").replace("\\", "/").rsplit("/", 1)[-1]
        stem = raw.rsplit(".", 1)[0] if "." in raw else raw
        stored_name = f"{_now():%Y%m%d}-{slugify(stem)[:60]}-{uuid.uuid4().hex[:8]}{extension}"
        try:
            await provider.create_folder(folder)
            await provider.upload_file(folder, stored_name, content)
        except CloudStorageError:
            raise ServiceError(_ERR + "cloud_upload_failed", http_status=502)
        finally:
            await provider.aclose()
        storage = ProcessFileStorage.CLOUD
    else:
        folder = None
        storage = ProcessFileStorage.LOCAL
        directory = LOCAL_DIR / process.id
        directory.mkdir(parents=True, exist_ok=True)
        (directory / stored_name).write_bytes(content)

    record = ProcessFile(
        storage=storage, stored_name=stored_name, cloud_path=folder, original_name=original,
        content_type=content_type, size=len(content), uploaded_by_id=user.id if user else None,
    )
    field.files.append(record)
    field.updated_at = _now()
    field.updated_by_id = user.id if user else None
    _event(process, ProcessEventKind.FILE_ADDED, user, stage=field.stage, note=f"{field.label}: {original}")
    await db.commit()
    return record


def _file(process: Process, file_id: str) -> ProcessFile:
    for stage in process.stages:
        for field in stage.fields:
            for record in field.files:
                if record.id == file_id:
                    return record
    raise ServiceError(_ERR + "file_not_found", http_status=404)


async def read_file(db: AsyncSession, process: Process, file_id: str) -> tuple[ProcessFile, bytes]:
    record = _file(process, file_id)
    if record.storage == ProcessFileStorage.LOCAL:
        path = local_path(record)
        if not path.is_file():
            raise ServiceError(_ERR + "file_not_found", http_status=404)
        return record, path.read_bytes()
    provider = await get_cloud_storage_provider(db)
    if provider is None:
        raise ServiceError(_ERR + "cloud_not_configured", http_status=502)
    try:
        return record, await provider.download_file(record.cloud_path or "", record.stored_name)
    except CloudStorageError:
        raise ServiceError(_ERR + "cloud_download_failed", http_status=502)
    finally:
        await provider.aclose()


async def delete_file(db: AsyncSession, process: Process, file_id: str, user: Optional[User]) -> None:
    """A wrong upload. A local file is removed; a cloud file stays in the
    cloud and is only unlinked from the process."""
    await _require(db, user, "write")
    record = _file(process, file_id)
    field = record.field
    _require_editable(process, field)
    if record.storage == ProcessFileStorage.LOCAL:
        path = local_path(record)
        if path.is_file():
            path.unlink()
    field.files.remove(record)
    _event(process, ProcessEventKind.FILE_REMOVED, user, stage=field.stage, note=f"{field.label}: {record.original_name}")
    await db.commit()
