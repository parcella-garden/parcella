"""Custom fields on members and parcels (issue #443, ADR 0147).

Definitions are set up by a system admin (the routes check that); values
are written by whoever may edit the member or parcel. No HTTP here: the
routes turn ServiceError into a message.
"""
import math
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Dict, List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.l10n import parse_decimal
from app.models import CustomField, CustomFieldKind, CustomFieldTarget, CustomFieldValue
from app.services.errors import ServiceError
from app.website_connectors.markdown_folder import slugify

LABEL_MAX = 200
UNIT_MAX = 20
TEXT_MAX = 2000
LONG_TEXT_MAX = 20000
OPTION_MAX = 100
OPTIONS_MAX_COUNT = 50
KEY_MAX = 80

FORM_PREFIX = "cf_"
FORM_MARKER = "custom_fields_present"

# The kinds a field inside a group may have (no groups in groups).
SUB_FIELD_KINDS = [k for k in CustomFieldKind if k != CustomFieldKind.GROUP]


def parse_target(value: str) -> CustomFieldTarget:
    try:
        return CustomFieldTarget(value)
    except ValueError:
        raise ServiceError("custom_fields.errors.unknown_target", http_status=404)


def owner_column(target: CustomFieldTarget):
    return CustomFieldValue.member_id if target == CustomFieldTarget.MEMBER else CustomFieldValue.parcel_id


# ---------------------------------------------------------------------------
# Definitions
# ---------------------------------------------------------------------------

async def list_fields(db: AsyncSession, target: CustomFieldTarget, include_archived: bool = False) -> List[CustomField]:
    """All fields of a target in display order: each top-level field or
    group, followed directly by its sub-fields."""
    query = select(CustomField).where(CustomField.target == target)
    if not include_archived:
        query = query.where(CustomField.archived_at.is_(None))
    fields = list((await db.scalars(query.order_by(CustomField.position, CustomField.created_at))).all())
    top = [f for f in fields if f.parent_id is None]
    # Sub-fields of an archived group are hidden with it -- and so never
    # touched by save_values, which would otherwise clear them.
    top_ids = {f.id for f in top}
    children: Dict[str, List[CustomField]] = {}
    for f in fields:
        if f.parent_id and f.parent_id in top_ids:
            children.setdefault(f.parent_id, []).append(f)
    ordered = []
    for f in top:
        ordered.append(f)
        ordered.extend(children.get(f.id, []))
    return ordered


async def has_values(db: AsyncSession, field: CustomField) -> bool:
    return bool(await db.scalar(select(func.count()).select_from(CustomFieldValue).where(CustomFieldValue.field_id == field.id)))


def _clean_label(label: str) -> str:
    label = (label or "").strip()
    if not label:
        raise ServiceError("custom_fields.errors.label_required")
    if len(label) > LABEL_MAX:
        raise ServiceError("custom_fields.errors.label_too_long", max=LABEL_MAX)
    return label


def _clean_options(kind: CustomFieldKind, options_text: str) -> Optional[list]:
    if kind != CustomFieldKind.CHOICE:
        return None
    options = list(dict.fromkeys(o.strip() for o in (options_text or "").splitlines() if o.strip()))
    if not options:
        raise ServiceError("custom_fields.errors.options_required")
    if len(options) > OPTIONS_MAX_COUNT or any(len(o) > OPTION_MAX for o in options):
        raise ServiceError("custom_fields.errors.options_too_long", count=OPTIONS_MAX_COUNT, max=OPTION_MAX)
    return options


def _clean_unit(kind: CustomFieldKind, unit: str) -> Optional[str]:
    unit = (unit or "").strip()
    if kind != CustomFieldKind.NUMBER or not unit:
        return None
    if len(unit) > UNIT_MAX:
        raise ServiceError("custom_fields.errors.unit_too_long", max=UNIT_MAX)
    return unit


async def _unique_key(db: AsyncSession, target: CustomFieldTarget, label: str) -> str:
    base = slugify(label)[:KEY_MAX - 4].strip("-") or "field"
    taken = set((await db.scalars(select(CustomField.key).where(CustomField.target == target))).all())
    key, n = base, 2
    while key in taken:
        key, n = f"{base}-{n}", n + 1
    return key


async def _next_position(db: AsyncSession, target: CustomFieldTarget, parent_id: Optional[str]) -> int:
    same_level = CustomField.parent_id.is_(None) if parent_id is None else CustomField.parent_id == parent_id
    current = await db.scalar(select(func.max(CustomField.position)).where(CustomField.target == target, same_level))
    return (current or 0) + 10


async def create_field(
    db: AsyncSession, target: CustomFieldTarget, *, label: str, kind: str, parent_id: Optional[str] = None,
    unit: str = "", options_text: str = "", help_text: str = "", required: bool = False,
) -> CustomField:
    try:
        kind = CustomFieldKind(kind)
    except ValueError:
        raise ServiceError("custom_fields.errors.unknown_kind")
    parent = None
    if parent_id:
        parent = await db.get(CustomField, parent_id)
        if parent is None or parent.target != target or parent.kind != CustomFieldKind.GROUP or parent.archived_at:
            raise ServiceError("custom_fields.errors.parent_not_a_group")
        if kind == CustomFieldKind.GROUP:
            raise ServiceError("custom_fields.errors.no_group_in_group")
    field = CustomField(
        target=target, parent_id=parent.id if parent else None, label=_clean_label(label), kind=kind,
        unit=_clean_unit(kind, unit), options=_clean_options(kind, options_text),
        help_text=(help_text or "").strip() or None,
        required=bool(required) and kind not in (CustomFieldKind.GROUP, CustomFieldKind.CHECKBOX),
        key=await _unique_key(db, target, label),
        position=await _next_position(db, target, parent.id if parent else None),
    )
    db.add(field)
    await db.flush()
    return field


async def update_field(
    db: AsyncSession, field: CustomField, *, label: str, kind: Optional[str] = None, unit: str = "",
    options_text: str = "", help_text: str = "", required: bool = False,
) -> CustomField:
    """The kind can only change while no member/parcel has a value for the
    field yet, and never to or from a group."""
    new_kind = field.kind
    if kind and kind != field.kind.value:
        try:
            new_kind = CustomFieldKind(kind)
        except ValueError:
            raise ServiceError("custom_fields.errors.unknown_kind")
        if CustomFieldKind.GROUP in (new_kind, field.kind) or await has_values(db, field):
            raise ServiceError("custom_fields.errors.kind_locked")
    field.label = _clean_label(label)
    field.kind = new_kind
    field.unit = _clean_unit(new_kind, unit)
    field.options = _clean_options(new_kind, options_text)
    field.help_text = (help_text or "").strip() or None
    field.required = bool(required) and new_kind not in (CustomFieldKind.GROUP, CustomFieldKind.CHECKBOX)
    await db.flush()
    return field


async def set_archived(db: AsyncSession, field: CustomField, archived: bool) -> None:
    """Archiving hides the field and its values (a group: with its
    sub-fields); restoring a sub-field of an archived group isn't possible."""
    if not archived and field.parent_id:
        parent = await db.get(CustomField, field.parent_id)
        if parent and parent.archived_at:
            raise ServiceError("custom_fields.errors.parent_archived")
    field.archived_at = datetime.now(timezone.utc) if archived else None
    await db.flush()


async def move_field(db: AsyncSession, field: CustomField, direction: int) -> None:
    """Swaps the field with its previous (-1) or next (+1) sibling."""
    siblings = [f for f in await list_fields(db, field.target, include_archived=True) if f.parent_id == field.parent_id]
    index = next(i for i, f in enumerate(siblings) if f.id == field.id)
    other = index + direction
    if 0 <= other < len(siblings):
        # Renumber first, so equal positions from older rows can't make a swap a no-op.
        for i, f in enumerate(siblings):
            f.position = (i + 1) * 10
        siblings[index].position, siblings[other].position = siblings[other].position, siblings[index].position
        await db.flush()


# ---------------------------------------------------------------------------
# Values
# ---------------------------------------------------------------------------

async def load_values(db: AsyncSession, target: CustomFieldTarget, owner_id: str) -> Dict[str, CustomFieldValue]:
    rows = (await db.scalars(select(CustomFieldValue).where(owner_column(target) == owner_id))).all()
    return {v.field_id: v for v in rows}


def raw_value(field: CustomField, value: Optional[CustomFieldValue]):
    """The stored value in its Python type, or None."""
    if value is None:
        return None
    if field.kind in (CustomFieldKind.CHECKBOX, CustomFieldKind.GROUP):
        return value.value_bool
    if field.kind == CustomFieldKind.NUMBER:
        return value.value_number
    if field.kind == CustomFieldKind.DATE:
        return value.value_date
    return value.value_text


def form_value(field: CustomField, value: Optional[CustomFieldValue]) -> str:
    """The value as an edit form shows it (ISO date, plain number)."""
    raw = raw_value(field, value)
    if raw is None:
        return ""
    if isinstance(raw, Decimal):
        return format(raw.normalize(), "f")
    if isinstance(raw, date):
        return raw.isoformat()
    return str(raw)


def parse_input(field: CustomField, text: Optional[str]):
    """One submitted value -> its Python value (None = empty). Raises
    ServiceError naming the field when it doesn't fit the kind."""
    text = (text or "").strip()
    if field.kind in (CustomFieldKind.CHECKBOX, CustomFieldKind.GROUP):
        return text.lower() in ("1", "true", "on", "yes", "ja")
    if not text:
        return None
    if field.kind == CustomFieldKind.NUMBER:
        number = parse_decimal(text)
        if number is None or not math.isfinite(number) or abs(number) >= Decimal("1e12"):
            raise ServiceError("custom_fields.errors.invalid_number", label=field.label)
        return number.quantize(Decimal("0.01"))
    if field.kind == CustomFieldKind.DATE:
        try:
            return date.fromisoformat(text)
        except ValueError:
            raise ServiceError("custom_fields.errors.invalid_date", label=field.label)
    if field.kind == CustomFieldKind.CHOICE:
        if text not in (field.options or []):
            raise ServiceError("custom_fields.errors.invalid_choice", label=field.label)
        return text
    limit = LONG_TEXT_MAX if field.kind == CustomFieldKind.LONG_TEXT else TEXT_MAX
    if len(text) > limit:
        raise ServiceError("custom_fields.errors.text_too_long", label=field.label, max=limit)
    return text


async def save_values(db: AsyncSession, target: CustomFieldTarget, owner_id: str, submitted: Dict[str, Optional[str]]) -> None:
    """Writes the values of all active fields from `submitted`
    ({field_id: text}; a missing checkbox means "no"). Everything is
    validated before anything is written. An unticked group clears its
    sub-fields: no pool, no pool measurements. Archived fields keep
    their values untouched."""
    fields = await list_fields(db, target)
    by_id = {f.id: f for f in fields}
    parsed = {f.id: parse_input(f, submitted.get(f.id)) for f in fields}
    for f in fields:
        group_on = f.parent_id is None or (f.parent_id in parsed and parsed[f.parent_id])
        if not group_on:
            parsed[f.id] = None
        elif f.required and parsed[f.id] is None:
            raise ServiceError("custom_fields.errors.required", label=f.label)
    existing = await load_values(db, target, owner_id)
    for field_id, value in parsed.items():
        field = by_id[field_id]
        row = existing.get(field_id)
        empty = value is None or (value is False and field.kind == CustomFieldKind.CHECKBOX)
        if empty and field.kind != CustomFieldKind.GROUP:
            if row is not None:
                await db.delete(row)
            continue
        if field.kind == CustomFieldKind.GROUP and not value:
            if row is not None:
                await db.delete(row)
            continue
        if row is None:
            row = CustomFieldValue(field_id=field_id, **{owner_column(target).key: owner_id})
            db.add(row)
        row.value_text = row.value_number = row.value_date = row.value_bool = None
        if field.kind in (CustomFieldKind.CHECKBOX, CustomFieldKind.GROUP):
            row.value_bool = True
        elif field.kind == CustomFieldKind.NUMBER:
            row.value_number = value
        elif field.kind == CustomFieldKind.DATE:
            row.value_date = value
        else:
            row.value_text = value
    await db.flush()


async def save_form_values(db: AsyncSession, target: CustomFieldTarget, owner_id: str, form) -> None:
    """The custom-field part of a member/parcel edit form. A post without
    the marker (an older form, a script) leaves the values alone."""
    if form.get(FORM_MARKER) != "1":
        return
    submitted = {k[len(FORM_PREFIX):]: v for k, v in form.items() if k.startswith(FORM_PREFIX)}
    await save_values(db, target, owner_id, submitted)


def _is_empty(value) -> bool:
    # Not `value in (None, "", False)`: Decimal("0") == False, and 0 is a real value.
    return value is None or value is False or value == "" and isinstance(value, str)


def _shown(value):
    """Numbers as plain text without trailing zeros (12.5, 1234567)."""
    return format(value.normalize(), "f") if isinstance(value, Decimal) else value


async def view_rows(db: AsyncSession, target: CustomFieldTarget, owner_id: str) -> list:
    """What a detail page shows: [(field, raw value, [(sub-field, raw value), ...])]
    for every top-level field with a value; a group only when ticked,
    with its sub-fields that have one."""
    fields = await list_fields(db, target)
    values = await load_values(db, target, owner_id)
    rows = []
    for f in fields:
        if f.parent_id:
            continue
        raw = raw_value(f, values.get(f.id))
        if _is_empty(raw):
            continue
        subs = [(c, raw_value(c, values.get(c.id))) for c in fields if c.parent_id == f.id]
        rows.append((f, _shown(raw), [(c, _shown(v)) for c, v in subs if not _is_empty(v)]))
    return rows


async def form_context(db: AsyncSession, target: CustomFieldTarget, owner_id: Optional[str]) -> dict:
    """Template context for the edit form's custom-field card."""
    fields = await list_fields(db, target)
    values = await load_values(db, target, owner_id) if owner_id else {}
    return {
        "custom_fields": fields,
        "custom_values": {f.id: form_value(f, values.get(f.id)) for f in fields},
    }


# ---------------------------------------------------------------------------
# List filter (issue #443 slice 2)
# ---------------------------------------------------------------------------

FILTER_YES = "__yes__"   # ticked / filled in
FILTER_NO = "__no__"     # not ticked / empty
FILTER_VALUE_MAX = 200


def filter_condition(target: CustomFieldTarget, owner_id_column, field_id: str, value: str):
    """WHERE condition for "members/parcels whose custom field ...", or None
    when the filter is incomplete. A value row only exists for a ticked
    yes/no or a filled-in field, so "yes" is "has a row". A value starting
    with "=" must match exactly (a choice), anything else is a substring
    search in the text."""
    if not field_id or not value:
        return None
    owner = owner_column(target)
    rows = select(owner).where(CustomFieldValue.field_id == field_id, owner.is_not(None))
    if value == FILTER_YES:
        return owner_id_column.in_(rows)
    if value == FILTER_NO:
        return owner_id_column.not_in(rows)
    if value.startswith("="):
        return owner_id_column.in_(rows.where(CustomFieldValue.value_text == value[1:]))
    return owner_id_column.in_(rows.where(CustomFieldValue.value_text.ilike(f"%{value}%")))


def clean_filter(field_id: str, value: str):
    return (field_id or "").strip()[:36], (value or "").strip()[:FILTER_VALUE_MAX]


async def filter_context(db: AsyncSession, target: CustomFieldTarget, field_id: str) -> dict:
    """The list page's custom-field filter: the fields to pick from and the
    picked one (its type decides the value control)."""
    fields = await list_fields(db, target)
    return {"cf_fields": fields, "cf_picked": next((f for f in fields if f.id == field_id), None)}
