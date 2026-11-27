"""Custom fields on members and parcels

Revision ID: 0133_custom_fields
Revises: 0132_announcement_parcels
Create Date: 2026-11-27

Issue #443 (ADR 0147): field definitions set up by a system admin
(groups are fields of kind GROUP with sub-fields), and one typed value
row per member or parcel and field.
"""
from typing import Union

from alembic import op
import sqlalchemy as sa

revision: str = "0133_custom_fields"
down_revision: Union[str, None] = "0132_announcement_parcels"
branch_labels = None
depends_on = None

TARGET = sa.Enum("MEMBER", "PARCEL", name="customfieldtarget")
KIND = sa.Enum("TEXT", "LONG_TEXT", "NUMBER", "DATE", "CHECKBOX", "CHOICE", "GROUP", name="customfieldkind")


def upgrade() -> None:
    op.create_table(
        "custom_fields",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("target", TARGET, nullable=False),
        sa.Column("parent_id", sa.String(36), sa.ForeignKey("custom_fields.id", ondelete="CASCADE"), nullable=True),
        sa.Column("key", sa.String(80), nullable=False),
        sa.Column("label", sa.String(200), nullable=False),
        sa.Column("help_text", sa.Text(), nullable=True),
        sa.Column("kind", KIND, nullable=False),
        sa.Column("unit", sa.String(20), nullable=True),
        sa.Column("options", sa.JSON(), nullable=True),
        sa.Column("required", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("target", "key", name="uq_custom_fields_target_key"),
    )
    op.create_index("ix_custom_fields_target", "custom_fields", ["target"])
    op.create_index("ix_custom_fields_parent_id", "custom_fields", ["parent_id"])
    op.create_table(
        "custom_field_values",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("field_id", sa.String(36), sa.ForeignKey("custom_fields.id", ondelete="CASCADE"), nullable=False),
        sa.Column("member_id", sa.String(36), sa.ForeignKey("members.id", ondelete="CASCADE"), nullable=True),
        sa.Column("parcel_id", sa.String(36), sa.ForeignKey("parcels.id", ondelete="CASCADE"), nullable=True),
        sa.Column("value_text", sa.Text(), nullable=True),
        sa.Column("value_number", sa.Numeric(14, 2), nullable=True),
        sa.Column("value_date", sa.Date(), nullable=True),
        sa.Column("value_bool", sa.Boolean(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("field_id", "member_id", name="uq_custom_field_values_member"),
        sa.UniqueConstraint("field_id", "parcel_id", name="uq_custom_field_values_parcel"),
        sa.CheckConstraint("(member_id IS NULL) <> (parcel_id IS NULL)", name="ck_custom_field_values_one_owner"),
    )
    op.create_index("ix_custom_field_values_field_id", "custom_field_values", ["field_id"])
    op.create_index("ix_custom_field_values_member_id", "custom_field_values", ["member_id"])
    op.create_index("ix_custom_field_values_parcel_id", "custom_field_values", ["parcel_id"])


def downgrade() -> None:
    op.drop_table("custom_field_values")
    op.drop_table("custom_fields")
    KIND.drop(op.get_bind(), checkfirst=True)
    TARGET.drop(op.get_bind(), checkfirst=True)
