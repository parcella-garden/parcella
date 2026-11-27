"""Notes and the club taxonomy (categories, tags)."""

from datetime import datetime, date
from typing import Optional, List
from sqlalchemy import String, Boolean, Date, DateTime, Text, ForeignKey, Index, Column, Table, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func, text

from app.database import Base
from app.models._common import new_uuid


# ---------------------------------------------------------------------------
# Club taxonomy (issue #286, ADR 0122) -- shared by notes and, later, the
# knowledge base (issue #285)
# ---------------------------------------------------------------------------

class TaxonomyCategory(Base):
    """A club-wide category ("Board meeting", "General meeting", ...).
    One per note. Deliberately not a per-module pool like MemberTag or
    TaskTag: the knowledge base (#285) browses notes, links and
    documents by the same categories (ADR 0122). Per-language names
    work like the tag pools' (app/tag_translations.py, ADR 0098)."""
    __tablename__ = "taxonomy_categories"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    translations: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<TaxonomyCategory {self.name}>"


class TaxonomyTag(Base):
    """A club-wide free-form tag, many per note (ADR 0122)."""
    __tablename__ = "taxonomy_tags"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    translations: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<TaxonomyTag {self.name}>"


note_tag_links = Table(
    "note_tag_links",
    Base.metadata,
    Column("note_id", String(36), ForeignKey("notes.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", String(36), ForeignKey("taxonomy_tags.id", ondelete="CASCADE"), primary_key=True, index=True),
)


class Note(Base):
    """A Markdown note: meeting minutes, board notes, anything (issue
    #286, docs/module-notes.md).

    With cloud storage and a notes folder configured, the .md file in
    the cloud is the master and this row is Parcella's index of it
    (ADR 0123): app/services/notes.py pulls changed files in and pushes
    saves out, refusing a save when the file changed meanwhile. Without
    one, this row is the note.

    note_date is the day the note is about (the meeting), not when it
    was written -- that's created_at/updated_at. Date only, no time of
    day (kermie's call for #286).
    """
    __tablename__ = "notes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    note_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    category_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("taxonomy_categories.id", ondelete="SET NULL"), nullable=True, index=True
    )
    body_markdown: Mapped[str] = mapped_column(Text, nullable=False, default="")
    # The web page a note is about -- a bookmark is a note with a source
    # (issue #305, ADR 0125). http(s) only, see note_files.clean_source_url.
    source_url: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True, index=True)

    created_by_user_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    updated_by_user_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # --- Cloud file (ADR 0123) ---
    # Path relative to the notes folder ("x.md", "Board meeting/x.md");
    # its first folder is the category. NULL = never written to the cloud.
    cloud_filename: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    # "<last_modified>|<size>" from the folder listing when last synced:
    # a cheap "did it change?" check before downloading.
    cloud_fingerprint: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    # sha256 of the file content as last read or written -- the
    # optimistic-lock token a save compares against.
    cloud_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    cloud_synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    # Saved while the cloud wasn't set up: push on the next sync.
    cloud_dirty: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false", nullable=False)
    # Deleted while the cloud wasn't set up: delete the file on the next
    # sync, so it isn't imported back.
    cloud_delete_pending: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false", nullable=False
    )

    # Not lazy-loadable under asyncio: selectinload wherever read.
    category: Mapped[Optional["TaxonomyCategory"]] = relationship("TaxonomyCategory")
    tags: Mapped[List["TaxonomyTag"]] = relationship(
        "TaxonomyTag", secondary="note_tag_links", order_by="TaxonomyTag.name",
    )
    created_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[created_by_user_id])
    updated_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[updated_by_user_id])

    __table_args__ = (
        # One live note per cloud file -- also stops two concurrent syncs
        # importing the same new file twice.
        Index(
            "uq_notes_cloud_filename", "cloud_filename", unique=True,
            postgresql_where=text("deleted_at IS NULL AND cloud_filename IS NOT NULL"),
        ),
    )

    def __repr__(self) -> str:
        return f"<Note {self.note_date} {self.title}>"
