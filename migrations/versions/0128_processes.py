"""Processes: configurable process builder

Revision ID: 0128_processes
Revises: 0127_announcement_print_qr
Create Date: 2026-11-16

Issue #331 / ADR 0135: club-defined process templates (ordered stages,
each with its own field set) and the processes run from them. A running
process is a snapshot of its template -- its stages and fields are
copied on start -- so editing a template never changes a running
process. Enum labels are the uppercase member names, as everywhere else
(see CLAUDE.md's enum sharp edge).
"""
from typing import Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0128_processes"
down_revision: Union[str, None] = "0127_announcement_print_qr"
branch_labels = None
depends_on = None

_ENUMS = {
    "processsubjectkind": ("NONE", "PARCEL", "MEMBER", "APPLICANT"),
    "processfieldkind": (
        "TEXT", "LONG_TEXT", "NUMBER", "MONEY", "DATE", "CHECKBOX", "CHOICE", "FILE", "MEMBER", "APPLICANT", "PARCEL",
    ),
    "processstatus": ("OPEN", "COMPLETED", "ABORTED"),
    "processeventkind": (
        "CREATED", "ADVANCED", "REVERTED", "COMPLETED", "ABORTED", "FIELD_CHANGED", "FILE_ADDED", "FILE_REMOVED",
    ),
    "processfilestorage": ("LOCAL", "CLOUD"),
}


def _enum(name: str) -> postgresql.ENUM:
    return postgresql.ENUM(*_ENUMS[name], name=name, create_type=False)


def _user_fk(column: str) -> sa.Column:
    return sa.Column(column, sa.String(36), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)


def _fk(column: str, table: str, *, ondelete: str, nullable: bool, index: bool = False) -> sa.Column:
    return sa.Column(
        column, sa.String(36), sa.ForeignKey(f"{table}.id", ondelete=ondelete), nullable=nullable, index=index,
    )


def _timestamp(column: str) -> sa.Column:
    return sa.Column(column, sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False)


def _field_definition() -> list:
    return [
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("label", sa.String(200), nullable=False),
        sa.Column("help_text", sa.Text(), nullable=True),
        sa.Column("kind", _enum("processfieldkind"), nullable=False),
        sa.Column("required", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("options", sa.JSON(), nullable=True),
    ]


def upgrade() -> None:
    bind = op.get_bind()
    for name, values in _ENUMS.items():
        postgresql.ENUM(*values, name=name).create(bind, checkfirst=True)

    op.create_table(
        "process_templates",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("subject_kind", _enum("processsubjectkind"), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        _timestamp("created_at"),
        _timestamp("updated_at"),
        _user_fk("created_by_id"),
    )
    op.create_table(
        "process_template_stages",
        sa.Column("id", sa.String(36), primary_key=True),
        _fk("template_id", "process_templates", ondelete="CASCADE", nullable=False, index=True),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
    )
    op.create_table(
        "process_template_fields",
        sa.Column("id", sa.String(36), primary_key=True),
        _fk("stage_id", "process_template_stages", ondelete="CASCADE", nullable=False, index=True),
        *_field_definition(),
    )
    op.create_table(
        "processes",
        sa.Column("id", sa.String(36), primary_key=True),
        _fk("template_id", "process_templates", ondelete="SET NULL", nullable=True, index=True),
        sa.Column("template_name", sa.String(200), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("subject_kind", _enum("processsubjectkind"), nullable=False),
        _fk("parcel_id", "parcels", ondelete="SET NULL", nullable=True, index=True),
        _fk("member_id", "members", ondelete="SET NULL", nullable=True, index=True),
        _fk("applicant_id", "applicants", ondelete="SET NULL", nullable=True, index=True),
        sa.Column("status", _enum("processstatus"), nullable=False, index=True),
        sa.Column("current_position", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("abort_reason", sa.Text(), nullable=True),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        _timestamp("created_at"),
        _timestamp("updated_at"),
        _user_fk("created_by_id"),
    )
    op.create_table(
        "process_stages",
        sa.Column("id", sa.String(36), primary_key=True),
        _fk("process_id", "processes", ondelete="CASCADE", nullable=False, index=True),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        _user_fk("completed_by_id"),
        sa.UniqueConstraint("process_id", "position", name="uq_process_stages_position"),
    )
    op.create_table(
        "process_fields",
        sa.Column("id", sa.String(36), primary_key=True),
        _fk("stage_id", "process_stages", ondelete="CASCADE", nullable=False, index=True),
        *_field_definition(),
        sa.Column("value_text", sa.Text(), nullable=True),
        sa.Column("value_number", sa.Numeric(14, 2), nullable=True),
        sa.Column("value_date", sa.Date(), nullable=True),
        sa.Column("value_bool", sa.Boolean(), nullable=True),
        _fk("value_member_id", "members", ondelete="SET NULL", nullable=True),
        _fk("value_applicant_id", "applicants", ondelete="SET NULL", nullable=True),
        _fk("value_parcel_id", "parcels", ondelete="SET NULL", nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        _user_fk("updated_by_id"),
    )
    op.create_table(
        "process_files",
        sa.Column("id", sa.String(36), primary_key=True),
        _fk("field_id", "process_fields", ondelete="CASCADE", nullable=False, index=True),
        sa.Column("storage", _enum("processfilestorage"), nullable=False),
        sa.Column("stored_name", sa.String(100), nullable=False),
        sa.Column("cloud_path", sa.String(500), nullable=True),
        sa.Column("original_name", sa.String(200), nullable=False),
        sa.Column("content_type", sa.String(100), nullable=False),
        sa.Column("size", sa.Integer(), nullable=False),
        _timestamp("created_at"),
        _user_fk("uploaded_by_id"),
    )
    op.create_table(
        "process_events",
        sa.Column("id", sa.String(36), primary_key=True),
        _fk("process_id", "processes", ondelete="CASCADE", nullable=False, index=True),
        sa.Column("kind", _enum("processeventkind"), nullable=False),
        sa.Column("stage_name", sa.String(200), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        _timestamp("created_at"),
        _user_fk("user_id"),
    )


def downgrade() -> None:
    for table in (
        "process_events", "process_files", "process_fields", "process_stages", "processes",
        "process_template_fields", "process_template_stages", "process_templates",
    ):
        op.drop_table(table)
    bind = op.get_bind()
    for name in _ENUMS:
        postgresql.ENUM(name=name).drop(bind, checkfirst=True)
