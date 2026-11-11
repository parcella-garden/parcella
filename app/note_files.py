"""
The .md file formats of a note (issue #286, ADR 0123, ADR 0127).

**In the cloud** a note file holds only the note's text (ADR 0127):
title, date, category, tags and source live in Parcella's database,
so editing them never touches the file (render_note_body). Older files
and files written by other tools may still start with a front-matter
header:

    ---
    id: 3f1c...                      (Parcella's note id, from before ADR 0127)
    title: "Board meeting March"
    date: 2026-03-04
    source: "https://example.org/page"
    category: "Board meeting"
    tags: ["budget", "water"]
    ---

    The body ...

parse_note_file still reads such a header, so a file that turns up in
the notes folder is adopted with its metadata; sync then rewrites it
as text only. Reading is lenient on purpose, since people edit these
files by hand: unquoted values, single quotes, a YAML block list for
tags, a date followed by a time (the time is ignored), a file with no
header at all (then the title comes from the first heading or the
file name). No YAML library: this is the whole grammar Parcella
needs, and a full YAML parser on files from outside is more attack
surface than it's worth.

**The download** of a single note (render_note_file) keeps the header,
so an exported note carries its metadata along. Every value written
there is valid YAML (strings and lists as JSON).

Pure functions only -- no database, no cloud. app/services/notes.py
does the I/O.
"""
import hashlib
import json
import re
import unicodedata
from urllib.parse import urlsplit
from email.utils import parsedate_to_datetime
from dataclasses import dataclass, field
from datetime import date
from typing import Iterable, List, Optional

_DATE_PREFIX_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})")
# A date at the start of a file name, in the forms clubs actually use
# (issue #302): "2026-11-08 ...", "20261108 ..." and month-only
# "202506_..." (the 1st of that month). Not followed by another digit, so
# a longer number ("2026110812") isn't misread as a date.
_FILENAME_DATE_RE = re.compile(
    r"^(?:(?P<y1>\d{4})-(?P<m1>\d{2})-(?P<d1>\d{2})"
    r"|(?P<y2>\d{4})(?P<m2>\d{2})(?P<d2>\d{2})(?!\d)"
    r"|(?P<y3>\d{4})(?P<m3>\d{2})(?!\d))"
)
_KNOWN_KEY_RE = re.compile(r"^(id|title|date|category|tags|source|url)\s*:", re.IGNORECASE)
_HEADING_RE = re.compile(r"^#{1,6}\s+(.+?)\s*#*\s*$")

MAX_SLUG_LENGTH = 60


@dataclass
class ParsedNote:
    title: Optional[str] = None
    note_date: Optional[date] = None
    category: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    note_id: Optional[str] = None
    source: Optional[str] = None
    body: str = ""
    had_header: bool = False  # the file started with a front-matter header


SOURCE_URL_MAX_LENGTH = 2048


def clean_source_url(raw: Optional[str]) -> Optional[str]:
    """A note's source link (issue #305), or None if it isn't a usable
    http(s) URL. Only http/https with a host is accepted -- the value
    ends up in an href, so `javascript:`, `data:` and friends never get
    through, whether they come from a hand-edited file, the form, the
    API or a bookmark import."""
    value = (raw or "").strip()
    if not value or len(value) > SOURCE_URL_MAX_LENGTH:
        return None
    if any(ch.isspace() or ord(ch) < 32 or ord(ch) == 127 for ch in value):
        return None
    try:
        parts = urlsplit(value)
    except ValueError:
        return None
    if parts.scheme.lower() not in ("http", "https") or not parts.hostname:
        return None
    return value


def content_hash(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def fingerprint(last_modified: Optional[str], size: Optional[int]) -> str:
    """What the folder listing says about a file, as one comparable
    string. Empty when the server reports neither -- then every sync
    downloads the file and compares hashes instead."""
    if not last_modified and size is None:
        return ""
    return f"{last_modified or ''}|{'' if size is None else size}"


def date_from_last_modified(value: Optional[str]) -> Optional[date]:
    """The day a cloud listing says a file was last modified: WebDAV
    sends an HTTP date ("Wed, 04 Mar 2026 18:00:00 GMT"), S3 ISO 8601
    ("2026-03-04T18:00:00.000Z"). None if it's missing or unreadable."""
    if not value:
        return None
    try:
        return parsedate_to_datetime(value).date()
    except (TypeError, ValueError, IndexError):
        pass
    match = _DATE_PREFIX_RE.match(value.strip())
    if match:
        try:
            return date.fromisoformat(match.group(1))
        except ValueError:
            return None
    return None


def date_from_filename(name: str) -> Optional[date]:
    """The date a file name starts with (see _FILENAME_DATE_RE), or None.
    Takes the bare name or a path; only the last segment counts."""
    stem = name.rsplit("/", 1)[-1]
    match = _FILENAME_DATE_RE.match(stem)
    if not match:
        return None
    year = match.group("y1") or match.group("y2") or match.group("y3")
    month = match.group("m1") or match.group("m2") or match.group("m3")
    day = match.group("d1") or match.group("d2") or "01"
    try:
        return date(int(year), int(month), int(day))
    except ValueError:
        return None


def slugify(text: str) -> str:
    """ASCII-only, lowercase, dashes: safe in any cloud backend, URL and
    shell, whatever the title contains."""
    ascii_text = unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_text.lower()).strip("-")
    return slug[:MAX_SLUG_LENGTH].strip("-") or "note"


def note_filename(note_date: date, title: str, taken: Iterable[str]) -> str:
    """`2026-03-04-board-meeting-march.md`, with -2, -3, ... appended if
    that name is taken (compared ignoring case: some backends are
    case-insensitive)."""
    taken_lower = {name.lower() for name in taken}
    stem = f"{note_date.isoformat()}-{slugify(title)}"
    candidate = f"{stem}.md"
    counter = 2
    while candidate.lower() in taken_lower:
        candidate = f"{stem}-{counter}.md"
        counter += 1
    return candidate


def _quote(value: str) -> str:
    return json.dumps(" ".join(value.split()), ensure_ascii=False)


def render_note_body(body: str) -> str:
    """A note's file in the cloud: its text only (ADR 0127)."""
    text = (body or "").replace("\r\n", "\n").rstrip("\n")
    return text + "\n" if text else ""


def render_note_file(
    *, note_id: str, title: str, note_date: date,
    category: Optional[str], tags: List[str], body: str, source: Optional[str] = None,
) -> str:
    lines = ["---", f"id: {note_id}", f"title: {_quote(title)}", f"date: {note_date.isoformat()}"]
    source = clean_source_url(source)
    if source:
        lines.append(f"source: {_quote(source)}")
    if category:
        lines.append(f"category: {_quote(category)}")
    if tags:
        lines.append("tags: [" + ", ".join(_quote(t) for t in tags) + "]")
    lines.append("---")
    text = "\n".join(lines) + "\n\n" + (body or "").replace("\r\n", "\n").rstrip("\n") + "\n"
    return text


def _scalar(raw: str) -> str:
    value = raw.strip()
    if value.startswith('"'):
        try:
            decoded = json.loads(value)
            if isinstance(decoded, str):
                return decoded
        except ValueError:
            pass
        return value.strip('"')
    if value.startswith("'") and value.endswith("'") and len(value) >= 2:
        return value[1:-1].replace("''", "'")
    # An unquoted YAML value ends at " #" (a comment).
    return value.split(" #", 1)[0].strip()


def _flow_list(raw: str) -> List[str]:
    value = raw.strip()
    if not value:
        return []
    if value.startswith("["):
        try:
            decoded = json.loads(value)
            if isinstance(decoded, list):
                return [str(v) for v in decoded if str(v).strip()]
        except ValueError:
            pass
        value = value.strip("[]")
    return [item for item in (_scalar(part) for part in value.split(",")) if item]


def _parse_date(raw: str) -> Optional[date]:
    """The day; a time written after it (`2026-03-04 19:00`,
    `2026-03-04T19:00:00+01:00`) is ignored -- notes are dated, not timed."""
    match = _DATE_PREFIX_RE.match(_scalar(raw))
    if not match:
        return None
    try:
        return date.fromisoformat(match.group(1))
    except ValueError:
        return None


def _split_front_matter(text: str) -> tuple[Optional[List[str]], str]:
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return None, text
    for index in range(1, len(lines)):
        if lines[index].strip() in ("---", "..."):
            header = lines[1:index]
            # Only a block with a key Parcella knows is a header: since
            # the cloud file holds plain text (ADR 0127), a note may well
            # start with a horizontal rule, and that text must survive.
            if not any(_KNOWN_KEY_RE.match(line) for line in header):
                return None, text
            body = "\n".join(lines[index + 1:])
            return header, body
    return None, text  # no closing line: not a header after all


def parse_note_file(content: bytes, filename: str = "") -> ParsedNote:
    text = content.decode("utf-8", errors="replace").lstrip("﻿").replace("\r\n", "\n")
    header, body = _split_front_matter(text)
    parsed = ParsedNote()

    if header is not None:
        parsed.had_header = True
        index = 0
        while index < len(header):
            line = header[index]
            index += 1
            if ":" not in line or line.startswith((" ", "\t", "#")):
                continue
            key, raw = line.split(":", 1)
            key = key.strip().lower()
            if key == "tags":
                if raw.strip():
                    parsed.tags = _flow_list(raw)
                else:  # YAML block list on the following lines
                    while index < len(header) and header[index].strip().startswith("- "):
                        item = _scalar(header[index].strip()[2:])
                        if item:
                            parsed.tags.append(item)
                        index += 1
            elif key == "title":
                parsed.title = _scalar(raw) or None
            elif key == "date":
                parsed.note_date = _parse_date(raw)
            elif key == "category":
                parsed.category = _scalar(raw) or None
            elif key == "id":
                parsed.note_id = _scalar(raw) or None
            elif key in ("source", "url"):
                # "url:" too: what Obsidian web clippers and many
                # bookmark exporters write.
                parsed.source = clean_source_url(_scalar(raw))
        body = body[1:] if body.startswith("\n") else body

    parsed.body = body.rstrip("\n")

    if not parsed.title:
        for line in parsed.body.split("\n"):
            match = _HEADING_RE.match(line.strip())
            if match:
                parsed.title = match.group(1)
                break
    stem = filename.rsplit("/", 1)[-1]
    stem = stem[:-3] if stem.lower().endswith(".md") else stem
    if not parsed.title:
        parsed.title = stem or "Note"
    if parsed.note_date is None:
        parsed.note_date = date_from_filename(stem)
    parsed.title = " ".join(parsed.title.split())[:255]
    parsed.tags = list(dict.fromkeys(" ".join(t.split())[:100] for t in parsed.tags if t.strip()))
    if parsed.category:
        parsed.category = " ".join(parsed.category.split())[:100]
    return parsed
