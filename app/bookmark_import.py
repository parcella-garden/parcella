"""
Parser for the standard bookmark export file (issue #305, ADR 0125).

The "Netscape bookmark file" is what Nextcloud Bookmarks, Firefox,
Chrome, Edge and Safari all export:

    <DL><p>
        <DT><H3>Folder</H3>
        <DL><p>
            <DT><A HREF="https://..." ADD_DATE="1700000000" TAGS="a,b">Title</A>
            <DD>Description
        </DL><p>
    </DL><p>

Tags are unclosed (no </DT>, </DD>), so this walks the parser's events
instead of building a tree. Pure: no database, no network -- Parcella
never fetches the bookmarked pages (ADR 0125). The stdlib HTMLParser
doesn't resolve external entities or load anything, so there's no XXE
or SSRF surface here.
"""
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from html.parser import HTMLParser
from typing import List, Optional

from app.note_files import clean_source_url

MAX_BOOKMARK_FILE_BYTES = 5 * 1024 * 1024
TITLE_MAX_LENGTH = 255
TAG_MAX_LENGTH = 100


@dataclass
class Bookmark:
    url: Optional[str]  # None: not an http(s) URL, skipped on import
    raw_url: str
    title: str
    added: Optional[date] = None
    description: str = ""
    tags: List[str] = field(default_factory=list)  # bookmark tags + folder names


def _clean(text: str, limit: int) -> str:
    return " ".join((text or "").split())[:limit]


def _date_from_epoch(raw: Optional[str]) -> Optional[date]:
    """ADD_DATE is seconds since 1970; some exporters write milli- or
    microseconds instead."""
    try:
        value = int((raw or "").strip())
    except ValueError:
        return None
    while value > 10**11:  # beyond year 5000 as seconds: ms or µs
        value //= 1000
    if value <= 0:
        return None
    try:
        return datetime.fromtimestamp(value, tz=timezone.utc).date()
    except (OverflowError, OSError, ValueError):
        return None


class _Parser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.bookmarks: List[Bookmark] = []
        self._folders: List[Optional[str]] = []  # one entry per open <DL>
        self._pending_folder: Optional[str] = None
        self._in_h3 = False
        self._h3_text: List[str] = []
        self._current: Optional[Bookmark] = None
        self._in_a = False
        self._a_text: List[str] = []
        self._dd_target: Optional[Bookmark] = None
        self._dd_text: List[str] = []

    def _finish_dd(self) -> None:
        if self._dd_target is not None:
            self._dd_target.description = "\n".join(
                line.strip() for line in "".join(self._dd_text).strip().splitlines()
            ).strip()
        self._dd_target = None
        self._dd_text = []

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag in ("dt", "dl"):
            self._finish_dd()
        if tag == "dl":
            self._folders.append(self._pending_folder)
            self._pending_folder = None
        elif tag == "h3":
            self._in_h3 = True
            self._h3_text = []
        elif tag == "a":
            values = {k.lower(): (v or "") for k, v in attrs}
            raw_url = values.get("href", "").strip()
            folder_tags = [f for f in self._folders if f]
            own_tags = [t for t in (part.strip() for part in values.get("tags", "").split(",")) if t]
            tags = list(dict.fromkeys(_clean(t, TAG_MAX_LENGTH) for t in own_tags + folder_tags if t.strip()))
            self._current = Bookmark(
                url=clean_source_url(raw_url), raw_url=raw_url, title="",
                added=_date_from_epoch(values.get("add_date")), tags=tags,
            )
            self._in_a = True
            self._a_text = []
        elif tag == "dd":
            self._dd_target = self.bookmarks[-1] if self.bookmarks else None
            self._dd_text = []

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag == "dl":
            self._finish_dd()
            if self._folders:
                self._folders.pop()
        elif tag == "h3" and self._in_h3:
            self._in_h3 = False
            self._pending_folder = _clean("".join(self._h3_text), TAG_MAX_LENGTH) or None
        elif tag == "a" and self._in_a and self._current is not None:
            self._in_a = False
            bookmark = self._current
            bookmark.title = _clean("".join(self._a_text), TITLE_MAX_LENGTH) or _clean(bookmark.raw_url, TITLE_MAX_LENGTH)
            self.bookmarks.append(bookmark)
            self._current = None

    def handle_data(self, data):
        if self._in_h3:
            self._h3_text.append(data)
        elif self._in_a:
            self._a_text.append(data)
        elif self._dd_target is not None:
            self._dd_text.append(data)

    def close(self):
        super().close()
        self._finish_dd()


def parse_bookmark_file(content: bytes) -> List[Bookmark]:
    """Every bookmark in the file, in file order. Within the file, a URL
    that appears more than once is merged into its first occurrence (its
    tags and folders are added there)."""
    text = content.decode("utf-8", errors="replace").lstrip("﻿")
    parser = _Parser()
    parser.feed(text)
    parser.close()
    merged: List[Bookmark] = []
    by_url = {}
    for bookmark in parser.bookmarks:
        first = by_url.get(bookmark.url) if bookmark.url else None
        if first is None:
            merged.append(bookmark)
            if bookmark.url:
                by_url[bookmark.url] = bookmark
            continue
        for tag in bookmark.tags:
            if tag not in first.tags:
                first.tags.append(tag)
        if not first.description and bookmark.description:
            first.description = bookmark.description
    return merged
