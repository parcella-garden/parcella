"""Custom fields on members and parcels (issue #443, ADR 0147).

Definitions are set up by a system admin (the routes check that); values
are written by whoever may edit the member or parcel. No HTTP here: the
routes turn ServiceError into a message.
"""
import math
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Dict, List, Optional

from sqlalchemy import delete, func, or_, select
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


async def value_counts(db: AsyncSession, target: CustomFieldTarget) -> Dict[str, int]:
    """{field id: number of members/parcels with a value}; a group counts
    its own values plus its sub-fields' -- what deleting it would remove."""
    rows = (await db.execute(
        select(CustomFieldValue.field_id, func.count())
        .join(CustomField, CustomField.id == CustomFieldValue.field_id)
        .where(CustomField.target == target)
        .group_by(CustomFieldValue.field_id)
    )).all()
    counts = dict(rows)
    fields = (await db.scalars(select(CustomField).where(CustomField.target == target))).all()
    totals = {f.id: counts.get(f.id, 0) for f in fields}
    for f in fields:
        if f.parent_id in totals:
            totals[f.parent_id] += counts.get(f.id, 0)
    return totals


async def delete_field(db: AsyncSession, field: CustomField) -> None:
    """Deletes a field for good, with its values -- a group with its
    sub-fields and theirs (kermie, #443: delete, not only archive). The
    database cascades the values; the delete is a plain statement so the
    ORM can't "orphan" sub-fields by nulling their parent_id instead."""
    await db.execute(delete(CustomField).where(or_(CustomField.id == field.id, CustomField.parent_id == field.id)))
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
        await _write(db, target, owner_id, by_id[field_id], existing, value)
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
    """A field without a value is no filter at all -- and must not count as
    one: an announcement started from such a list would otherwise be a
    "targeted" message to everybody (the issue #242 trap)."""
    field_id, value = (field_id or "").strip()[:36], (value or "").strip()[:FILTER_VALUE_MAX]
    return (field_id, value) if field_id and value else ("", "")


async def filter_context(db: AsyncSession, target: CustomFieldTarget, field_id: str) -> dict:
    """The list page's custom-field filter: the fields to pick from and the
    picked one (its type decides the value control)."""
    fields = await list_fields(db, target)
    return {"cf_fields": fields, "cf_picked": next((f for f in fields if f.id == field_id), None)}


# ---------------------------------------------------------------------------
# CSV export and import (issue #443 slice 3)
# ---------------------------------------------------------------------------

CSV_TARGET_PREFIX = "cf:"
_CSV_YES, _CSV_NO = "Ja", "Nein"  # like the existing exports' yes/no columns


def _csv_header(field: CustomField, by_id: Dict[str, CustomField]) -> str:
    parent = by_id.get(field.parent_id) if field.parent_id else None
    return f"{parent.label}: {field.label}" if parent else field.label


async def csv_columns(db: AsyncSession, target: CustomFieldTarget) -> List[tuple]:
    """[(field, column header)] for the export, in display order."""
    fields = await list_fields(db, target)
    by_id = {f.id: f for f in fields}
    return [(f, _csv_header(f, by_id)) for f in fields]


async def csv_values(db: AsyncSession, target: CustomFieldTarget, owner_ids: List[str]) -> Dict[str, Dict[str, CustomFieldValue]]:
    """{owner id: {field id: value}} for many members/parcels in one query."""
    if not owner_ids:
        return {}
    owner = owner_column(target)
    out: Dict[str, Dict[str, CustomFieldValue]] = {}
    for row in (await db.scalars(select(CustomFieldValue).where(owner.in_(owner_ids)))).all():
        out.setdefault(getattr(row, owner.key), {})[row.field_id] = row
    return out


def csv_cell(field: CustomField, value: Optional[CustomFieldValue]) -> str:
    raw = raw_value(field, value)
    if field.kind in (CustomFieldKind.CHECKBOX, CustomFieldKind.GROUP):
        return _CSV_YES if raw else _CSV_NO
    if raw is None:
        return ""
    if isinstance(raw, Decimal):
        return format(raw.normalize(), "f")
    if isinstance(raw, date):
        return raw.isoformat()
    return str(raw)


async def import_targets(db: AsyncSession, target: CustomFieldTarget):
    """The custom fields as column-mapping targets: (target names, their
    labels for the mapping form, aliases for guessing the mapping)."""
    columns = await csv_columns(db, target)
    names = [CSV_TARGET_PREFIX + f.id for f, _ in columns]
    labels = {CSV_TARGET_PREFIX + f.id: header for f, header in columns}
    aliases = {CSV_TARGET_PREFIX + f.id: {header.lower(), f.label.lower(), f.key} for f, header in columns}
    return names, labels, aliases


def import_cells(values: dict) -> Dict[str, str]:
    """The custom-field cells of one mapped CSV row, {field id: text}."""
    return {k[len(CSV_TARGET_PREFIX):]: v for k, v in values.items() if k.startswith(CSV_TARGET_PREFIX)}


def _parse_csv_bool(text: str) -> bool:
    return text.strip().lower() in ("ja", "yes", "true", "1", "x", "oui", "tak", "ano", "áno")


async def import_values(db: AsyncSession, target: CustomFieldTarget, owner_id: str, cells: Dict[str, str]) -> bool:
    """Applies one row's custom-field cells. Like the rest of the import,
    only what the file says (issue #352): empty cells change nothing.
    A filled-in sub-field ticks its group; a group set to "no" clears
    its sub-fields. Raises ServiceError (nothing of the row written) when
    a cell doesn't fit. Returns whether anything was given."""
    fields = {f.id: f for f in await list_fields(db, target)}
    parsed = {}
    for field_id, text in cells.items():
        field = fields.get(field_id)
        if field is None or not (text or "").strip():
            continue
        if field.kind in (CustomFieldKind.CHECKBOX, CustomFieldKind.GROUP):
            parsed[field_id] = _parse_csv_bool(text)
        else:
            parsed[field_id] = parse_input(field, text)
    if not parsed:
        return False
    for field_id, value in list(parsed.items()):
        field = fields[field_id]
        if field.parent_id and not _is_empty(value) and field.parent_id in fields:
            parsed[field.parent_id] = parsed.get(field.parent_id) or True
    existing = await load_values(db, target, owner_id)
    for field_id, value in parsed.items():
        field = fields[field_id]
        if field.kind == CustomFieldKind.GROUP and value is False:
            for child in (f for f in fields.values() if f.parent_id == field_id):
                if child.id in existing:
                    await db.delete(existing.pop(child.id))
        await _write(db, target, owner_id, field, existing, value)
    await db.flush()
    return True


async def _write(db: AsyncSession, target: CustomFieldTarget, owner_id: str, field: CustomField,
                 existing: Dict[str, CustomFieldValue], value) -> None:
    """Stores one parsed value. A row only exists for a ticked yes/no or a
    filled-in field, so "no" and empty remove it."""
    row = existing.get(field.id)
    if _is_empty(value):
        if row is not None:
            await db.delete(existing.pop(field.id))
        return
    if row is None:
        row = CustomFieldValue(field_id=field.id, **{owner_column(target).key: owner_id})
        db.add(row)
        existing[field.id] = row
    row.value_text = row.value_number = row.value_date = row.value_bool = None
    if field.kind in (CustomFieldKind.CHECKBOX, CustomFieldKind.GROUP):
        row.value_bool = True
    elif field.kind == CustomFieldKind.NUMBER:
        row.value_number = value
    elif field.kind == CustomFieldKind.DATE:
        row.value_date = value
    else:
        row.value_text = value


# ---------------------------------------------------------------------------
# REST API (issue #443 slice 4): values by field key
# ---------------------------------------------------------------------------

def api_value(field: CustomField, value: Optional[CustomFieldValue]):
    """JSON value: bool for yes/no and groups, numbers as strings (no
    float rounding, like the API's other amounts), ISO dates, text."""
    raw = raw_value(field, value)
    if field.kind in (CustomFieldKind.CHECKBOX, CustomFieldKind.GROUP):
        return bool(raw)
    if isinstance(raw, Decimal):
        return format(raw.normalize(), "f")
    if isinstance(raw, date):
        return raw.isoformat()
    return raw


async def api_values(db: AsyncSession, target: CustomFieldTarget, owner_id: str) -> dict:
    """{key: value} for every active field; None = empty."""
    fields = await list_fields(db, target)
    values = await load_values(db, target, owner_id)
    return {f.key: api_value(f, values.get(f.id)) for f in fields}


def _api_text(field: CustomField, value) -> str:
    if value is None:
        return ""
    if field.kind in (CustomFieldKind.CHECKBOX, CustomFieldKind.GROUP):
        if not isinstance(value, bool):
            raise ServiceError("custom_fields.errors.expects_bool", label=field.label)
        return "1" if value else ""
    if isinstance(value, bool) or not isinstance(value, (str, int, float)):
        raise ServiceError("custom_fields.errors.invalid_value", label=field.label)
    return str(value)


def _api_parse(field: CustomField, value):
    # A JSON number is taken as it is: "1.234" through parse_decimal would
    # read as 1234 in German notation.
    if field.kind == CustomFieldKind.NUMBER and isinstance(value, (int, float)) and not isinstance(value, bool):
        return parse_input(field, format(Decimal(str(value)), "f").replace(".", ","))
    return parse_input(field, _api_text(field, value))


async def api_update(db: AsyncSession, target: CustomFieldTarget, owner_id: str, changes: dict) -> None:
    """Sets the given keys only; None / false clears a value. A filled-in
    sub-field ticks its group, a group set to false clears its sub-fields,
    and a required field can't be cleared while its group is on. Unknown
    keys are refused. Everything is validated before anything is written."""
    fields = await list_fields(db, target)
    by_key = {f.key: f for f in fields}
    by_id = {f.id: f for f in fields}
    unknown = sorted(set(changes) - set(by_key))
    if unknown:
        raise ServiceError("custom_fields.errors.unknown_keys", keys=", ".join(unknown[:10]))
    parsed = {by_key[k].id: _api_parse(by_key[k], v) for k, v in changes.items()}
    for field_id, value in list(parsed.items()):
        parent_id = by_id[field_id].parent_id
        if parent_id and not _is_empty(value) and parent_id in by_id and parsed.get(parent_id) is not False:
            parsed.setdefault(parent_id, True)
    existing = await load_values(db, target, owner_id)

    def is_on(field: CustomField) -> bool:
        if field.parent_id is None:
            return True
        if field.parent_id in parsed:
            return bool(parsed[field.parent_id])
        return field.parent_id in existing

    for field_id, value in parsed.items():
        field = by_id[field_id]
        if field.required and _is_empty(value) and is_on(field):
            raise ServiceError("custom_fields.errors.required", label=field.label)
    for field_id, value in parsed.items():
        field = by_id[field_id]
        if field.kind == CustomFieldKind.GROUP and not value:
            for child in (f for f in fields if f.parent_id == field_id):
                if child.id in existing and child.id not in parsed:
                    await db.delete(existing.pop(child.id))
        if field.parent_id and not is_on(field):
            value = None  # a sub-field of a group that is (being set) off
        await _write(db, target, owner_id, field, existing, value)
    await db.flush()
