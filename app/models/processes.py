"""Processes: templates, stages, fields, running processes, files, events."""

import enum
from datetime import datetime, date
from typing import Optional, List
from sqlalchemy import String, Integer, Boolean, Date, DateTime, Text, Numeric, ForeignKey, Enum as SAEnum, UniqueConstraint, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base
from app.models._common import new_uuid


# ---------------------------------------------------------------------------
# Processes (issue #331, ADR 0136, docs/module-processes.md): a club builds
# its own process templates -- ordered stages, each with its own field set --
# and runs them, optionally attached to a plot, a member or an applicant.
# A running process is a snapshot of its template (stages and fields are
# copied on start), so editing a template never changes a running process.
# ---------------------------------------------------------------------------

class ProcessSubjectKind(str, enum.Enum):
    NONE = "NONE"
    PARCEL = "PARCEL"
    MEMBER = "MEMBER"
    APPLICANT = "APPLICANT"


class ProcessFieldKind(str, enum.Enum):
    TEXT = "TEXT"
    LONG_TEXT = "LONG_TEXT"
    NUMBER = "NUMBER"
    MONEY = "MONEY"
    DATE = "DATE"
    CHECKBOX = "CHECKBOX"
    CHOICE = "CHOICE"
    FILE = "FILE"
    MEMBER = "MEMBER"
    APPLICANT = "APPLICANT"
    PARCEL = "PARCEL"


class ProcessStatus(str, enum.Enum):
    OPEN = "OPEN"
    COMPLETED = "COMPLETED"
    ABORTED = "ABORTED"


class ProcessEventKind(str, enum.Enum):
    CREATED = "CREATED"
    ADVANCED = "ADVANCED"
    REVERTED = "REVERTED"
    COMPLETED = "COMPLETED"
    ABORTED = "ABORTED"
    FIELD_CHANGED = "FIELD_CHANGED"
    FILE_ADDED = "FILE_ADDED"
    FILE_REMOVED = "FILE_REMOVED"


class ProcessFileStorage(str, enum.Enum):
    LOCAL = "LOCAL"
    CLOUD = "CLOUD"


class ProcessTemplate(Base):
    """A club-defined process. Archived (is_active=False) rather than
    deleted once processes were started from it (ADR 0005)."""
    __tablename__ = "process_templates"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    subject_kind: Mapped[ProcessSubjectKind] = mapped_column(
        SAEnum(ProcessSubjectKind), default=ProcessSubjectKind.NONE, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    created_by_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    stages: Mapped[List["ProcessTemplateStage"]] = relationship(
        "ProcessTemplateStage", back_populates="template", order_by="ProcessTemplateStage.position",
        cascade="all, delete-orphan",
    )
    created_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[created_by_id])

    def __repr__(self) -> str:
        return f"<ProcessTemplate {self.name!r}>"


class ProcessTemplateStage(Base):
    __tablename__ = "process_template_stages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    template_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("process_templates.id", ondelete="CASCADE"), nullable=False, index=True
    )
    position: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    template: Mapped["ProcessTemplate"] = relationship("ProcessTemplate", back_populates="stages")
    fields: Mapped[List["ProcessTemplateField"]] = relationship(
        "ProcessTemplateField", back_populates="stage", order_by="ProcessTemplateField.position",
        cascade="all, delete-orphan",
    )


class ProcessTemplateField(Base):
    __tablename__ = "process_template_fields"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    stage_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("process_template_stages.id", ondelete="CASCADE"), nullable=False, index=True
    )
    position: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    label: Mapped[str] = mapped_column(String(200), nullable=False)
    help_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    kind: Mapped[ProcessFieldKind] = mapped_column(SAEnum(ProcessFieldKind), nullable=False)
    required: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false", nullable=False)
    # CHOICE only: the list of allowed values.
    options: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)

    stage: Mapped["ProcessTemplateStage"] = relationship("ProcessTemplateStage", back_populates="fields")


class Process(Base):
    """One run of a template. `current_position` is the position of the
    stage being worked on; stages before it are completed."""
    __tablename__ = "processes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    template_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("process_templates.id", ondelete="SET NULL"), nullable=True, index=True
    )
    # The template's name at the time it was started (the template may be
    # renamed or archived later).
    template_name: Mapped[str] = mapped_column(String(200), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    subject_kind: Mapped[ProcessSubjectKind] = mapped_column(
        SAEnum(ProcessSubjectKind), default=ProcessSubjectKind.NONE, nullable=False
    )
    parcel_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("parcels.id", ondelete="SET NULL"), nullable=True, index=True
    )
    member_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("members.id", ondelete="SET NULL"), nullable=True, index=True
    )
    # Applicants can be hard-deleted (ADR 0091): the process stays, the
    # link goes.
    applicant_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("applicants.id", ondelete="SET NULL"), nullable=True, index=True
    )
    status: Mapped[ProcessStatus] = mapped_column(
        SAEnum(ProcessStatus), default=ProcessStatus.OPEN, nullable=False, index=True
    )
    current_position: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    abort_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    created_by_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    template: Mapped[Optional["ProcessTemplate"]] = relationship("ProcessTemplate")
    parcel: Mapped[Optional["Parcel"]] = relationship("Parcel")
    member: Mapped[Optional["Member"]] = relationship("Member")
    applicant: Mapped[Optional["Applicant"]] = relationship("Applicant")
    created_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[created_by_id])
    stages: Mapped[List["ProcessStage"]] = relationship(
        "ProcessStage", back_populates="process", order_by="ProcessStage.position", cascade="all, delete-orphan",
    )
    events: Mapped[List["ProcessEvent"]] = relationship(
        "ProcessEvent", back_populates="process", order_by="ProcessEvent.created_at.desc()",
        cascade="all, delete-orphan",
    )

    @property
    def is_open(self) -> bool:
        return self.status == ProcessStatus.OPEN

    def __repr__(self) -> str:
        return f"<Process {self.title!r} {self.status.value}>"


class ProcessStage(Base):
    __tablename__ = "process_stages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    process_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("processes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    position: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_by_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    process: Mapped["Process"] = relationship("Process", back_populates="stages")
    completed_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[completed_by_id])
    fields: Mapped[List["ProcessField"]] = relationship(
        "ProcessField", back_populates="stage", order_by="ProcessField.position", cascade="all, delete-orphan",
    )

    __table_args__ = (UniqueConstraint("process_id", "position", name="uq_process_stages_position"),)


class ProcessField(Base):
    """A field of a running process: the definition copied from the
    template plus its value -- one row, one typed value column per kind
    (ADR 0136)."""
    __tablename__ = "process_fields"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    stage_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("process_stages.id", ondelete="CASCADE"), nullable=False, index=True
    )
    position: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    label: Mapped[str] = mapped_column(String(200), nullable=False)
    help_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    kind: Mapped[ProcessFieldKind] = mapped_column(SAEnum(ProcessFieldKind), nullable=False)
    required: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false", nullable=False)
    options: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)

    value_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    value_number: Mapped[Optional[float]] = mapped_column(Numeric(14, 2), nullable=True)
    value_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    value_bool: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    value_member_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("members.id", ondelete="SET NULL"), nullable=True
    )
    value_applicant_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("applicants.id", ondelete="SET NULL"), nullable=True
    )
    value_parcel_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("parcels.id", ondelete="SET NULL"), nullable=True
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_by_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    stage: Mapped["ProcessStage"] = relationship("ProcessStage", back_populates="fields")
    value_member: Mapped[Optional["Member"]] = relationship("Member", foreign_keys=[value_member_id])
    value_applicant: Mapped[Optional["Applicant"]] = relationship("Applicant", foreign_keys=[value_applicant_id])
    value_parcel: Mapped[Optional["Parcel"]] = relationship("Parcel", foreign_keys=[value_parcel_id])
    updated_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[updated_by_id])
    files: Mapped[List["ProcessFile"]] = relationship(
        "ProcessFile", back_populates="field", order_by="ProcessFile.created_at", cascade="all, delete-orphan",
    )


class ProcessFile(Base):
    """A file attached to a FILE field. Stored in the club's cloud folder
    when one is set, otherwise under the private uploads directory --
    never served from /static (ADR 0136)."""
    __tablename__ = "process_files"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    field_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("process_fields.id", ondelete="CASCADE"), nullable=False, index=True
    )
    storage: Mapped[ProcessFileStorage] = mapped_column(SAEnum(ProcessFileStorage), nullable=False)
    stored_name: Mapped[str] = mapped_column(String(100), nullable=False)
    cloud_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    original_name: Mapped[str] = mapped_column(String(200), nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    size: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    uploaded_by_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    field: Mapped["ProcessField"] = relationship("ProcessField", back_populates="files")
    uploaded_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[uploaded_by_id])

    @property
    def is_image(self) -> bool:
        return self.content_type.startswith("image/")


class ProcessEvent(Base):
    """The audit trail of a process."""
    __tablename__ = "process_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    process_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("processes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    kind: Mapped[ProcessEventKind] = mapped_column(SAEnum(ProcessEventKind), nullable=False)
    stage_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    user_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    process: Mapped["Process"] = relationship("Process", back_populates="events")
    user: Mapped[Optional["User"]] = relationship("User", foreign_keys=[user_id])
