"""CSV import/export helpers shared across routers.

Also home to the defense against CSV formula injection (see
docs/security.md): cells that start with `=`, `+`, `-`, or `@` are
interpreted as formulas by Excel and LibreOffice Calc when the file is
opened. Any export column that carries user-entered free text needs to
go through `csv_safe()` before `writer.writerow()`.
"""

import base64
import csv
import io

_FORMULA_TRIGGER_CHARS = ("=", "+", "-", "@")


def csv_safe(value) -> str:
    text = "" if value is None else str(value)
    if text and text[0] in _FORMULA_TRIGGER_CHARS:
        return "'" + text
    return text


def decode_csv_upload(content: bytes) -> str:
    """BOM-safe decode: utf-8-sig first (strips a BOM if present), falls
    back to latin-1 for exports from tools that don't emit UTF-8."""
    try:
        return content.decode("utf-8-sig")
    except UnicodeDecodeError:
        return content.decode("latin-1")


def sniff_csv_delimiter(text: str) -> str:
    """csv.Sniffer()-based delimiter detection restricted to the two
    candidates seen in the wild across this app's CSV imports; falls
    back to ';' when Sniffer can't decide."""
    try:
        return csv.Sniffer().sniff(text[:2048], delimiters=";,").delimiter
    except csv.Error:
        return ";"


def guess_column_mapping(headers: list, aliases: dict) -> dict:
    """Best-effort default {column_index: target_field} mapping from a
    per-field alias set (each caller supplies its own vocabulary --
    e.g. finances' Date/Amount vs. metering's Parcel number/Zählernummer
    -- so the aliases stay data, not logic, passed in by the caller).
    Always fully overridable by the user in the mapping form afterward,
    so this only needs to be a good guess, not exhaustive."""
    mapping = {}
    for i, header in enumerate(headers):
        key = (header or "").strip().lower()
        for field, candidates in aliases.items():
            if key in candidates and field not in mapping.values():
                mapping[i] = field
                break
    return mapping


def parse_column_mapping(form, target_fields: list) -> dict:
    """Reads back {index: target_field} from a submitted mapping form's
    `map_{index}` fields, dropping anything that isn't a known target
    field (e.g. the "ignore this column" option)."""
    column_mapping: dict = {}
    for key, value in form.items():
        if key.startswith("map_") and value in target_fields:
            column_mapping[int(key.removeprefix("map_"))] = value
    return column_mapping


def parse_mapped_csv_rows(csv_content_b64: str, delimiter: str, column_mapping: dict) -> list:
    """Re-decodes the base64-round-tripped CSV and returns one
    {target_field: raw_stripped_string} dict per data row, via the
    confirmed column mapping. The header row is assumed already
    consumed by the preview step. Field-level parsing (dates, numbers,
    enums, ...) is intentionally left to the caller, so there is one
    parsing implementation per field, not one per import path."""
    text = base64.b64decode(csv_content_b64).decode("utf-8")
    reader = csv.reader(io.StringIO(text), delimiter=delimiter)
    rows = list(reader)[1:]
    return [
        {field: (row[i].strip() if i < len(row) else "") for i, field in column_mapping.items()}
        for row in rows
    ]
