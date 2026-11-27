"""Server-side paging for the member and parcel lists (issue #425, ADR 0145)."""
from dataclasses import dataclass
from typing import Any, List

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

PAGE_SIZE = 100


@dataclass(frozen=True)
class Page:
    items: List[Any]
    page: int   # 1-based, already clamped to 1..pages
    pages: int  # at least 1, also for an empty list
    total: int

    @property
    def first(self) -> int:
        """1-based number of the first row shown (0 for an empty list)."""
        return (self.page - 1) * PAGE_SIZE + 1 if self.total else 0

    @property
    def last(self) -> int:
        return min(self.page * PAGE_SIZE, self.total)


def with_page(query_string: str, page: int) -> str:
    """'?<filter>&page=N' for a list link, page 1 left out; '' if both are empty."""
    parts = [query_string] if query_string else []
    if page > 1:
        parts.append(f"page={page}")
    return "?" + "&".join(parts) if parts else ""


def page_of(index: int) -> int:
    """The page a 0-based row index lands on."""
    return index // PAGE_SIZE + 1


async def paginate(db: AsyncSession, query: Select, page: int) -> Page:
    """One page of `query` (which carries its own ORDER BY). A page past
    the end shows the last page instead of an empty one: after a filter
    change or deletions an old ?page= link still lands somewhere useful."""
    total = await db.scalar(select(func.count()).select_from(query.order_by(None).subquery()))
    pages = max(1, -(-total // PAGE_SIZE))
    page = min(max(page, 1), pages)
    items = (await db.scalars(query.limit(PAGE_SIZE).offset((page - 1) * PAGE_SIZE))).all()
    return Page(list(items), page, pages, total)
