"""Replace parcel_insurance.covers_household with per-member household selection

Revision ID: 0082_household_members
Revises: 0081_covers_household
Create Date: 2026-08-29

Issue #204 follow-up: the atomic "cover household" toggle (migration
0081) turned out to be the wrong shape -- what's actually needed is an
individual checkbox per household member, so the leaser specifically
can opt out while other household members / a named additional person
stay covered. Replaces covers_household with a new
accident_insurance_household_members table, symmetric to the existing
accident_insurance_additional_persons but opt-OUT by default instead
of opt-IN.

Data migration: every existing parcel_insurance row with
has_accident_insurance = true AND covers_household = true (i.e. not
already explicitly declined under 0081's toggle) gets seeded with its
parcel's CURRENT household members, using the same same-address-group
algorithm as household_grouping() (app/insurance_utils.py) --
reimplemented here since migrations don't import app code -- so
pre-existing billing-relevant data keeps "whole household covered"
instead of silently losing its base fee. A row that had already
declined household coverage stays declined (no seeding) rather than
being silently re-enrolled once covers_household is dropped.
"""
from collections import defaultdict
from typing import Union
import uuid

from alembic import op
import sqlalchemy as sa

revision: str = "0082_household_members"
down_revision: Union[str, None] = "0081_covers_household"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "accident_insurance_household_members",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "parcel_insurance_id", sa.String(36),
            sa.ForeignKey("parcel_insurance.id", ondelete="CASCADE"), nullable=False, index=True,
        ),
        sa.Column(
            "member_id", sa.String(36),
            sa.ForeignKey("members.id", ondelete="CASCADE"), nullable=False, index=True,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("parcel_insurance_id", "member_id", name="uq_accident_household_member"),
    )

    conn = op.get_bind()

    parcel_insurance = sa.table(
        "parcel_insurance", sa.column("id", sa.String), sa.column("parcel_id", sa.String),
        sa.column("has_accident_insurance", sa.Boolean), sa.column("covers_household", sa.Boolean),
    )
    member_parcels = sa.table(
        "member_parcels",
        sa.column("member_id", sa.String), sa.column("parcel_id", sa.String), sa.column("assigned_until", sa.Date),
    )
    members = sa.table(
        "members", sa.column("id", sa.String), sa.column("deleted_at", sa.DateTime),
        sa.column("member_until", sa.Date), sa.column("street", sa.String),
        sa.column("postal_code", sa.String), sa.column("city", sa.String),
    )

    # covers_household = false means the household was explicitly
    # declined under migration 0081/issue #204's now-replaced toggle --
    # skip seeding those rows, otherwise dropping the column below would
    # silently re-enroll and re-bill a household that opted out.
    pi_rows = conn.execute(
        sa.select(parcel_insurance.c.id, parcel_insurance.c.parcel_id)
        .where(
            parcel_insurance.c.has_accident_insurance.is_(True),
            parcel_insurance.c.covers_household.is_(True),
        )
    ).fetchall()

    insert_stmt = sa.text(
        "INSERT INTO accident_insurance_household_members (id, parcel_insurance_id, member_id, created_at) "
        "VALUES (:id, :pi_id, :member_id, now())"
    )

    for pi_id, parcel_id in pi_rows:
        tenants = conn.execute(
            sa.select(members.c.id, members.c.street, members.c.postal_code, members.c.city)
            .select_from(member_parcels.join(members, member_parcels.c.member_id == members.c.id))
            .where(
                member_parcels.c.parcel_id == parcel_id,
                sa.or_(member_parcels.c.assigned_until.is_(None), member_parcels.c.assigned_until > sa.func.current_date()),
                members.c.deleted_at.is_(None),
                sa.or_(members.c.member_until.is_(None), members.c.member_until >= sa.func.current_date()),
            )
            .order_by(members.c.id)
        ).fetchall()

        if not tenants:
            continue
        if len(tenants) == 1:
            household_ids = [tenants[0][0]]
        else:
            groups: dict = defaultdict(list)
            for member_id, street, postal_code, city in tenants:
                addr = ((street or "").strip().lower(), (postal_code or "").strip().lower(), (city or "").strip().lower())
                if addr == ("", "", ""):
                    continue
                groups[addr].append(member_id)
            household_ids = max(groups.values(), key=len) if groups else []

        for member_id in household_ids:
            conn.execute(insert_stmt, {"id": str(uuid.uuid4()), "pi_id": pi_id, "member_id": member_id})

    op.drop_column("parcel_insurance", "covers_household")


def downgrade() -> None:
    op.add_column(
        "parcel_insurance",
        sa.Column("covers_household", sa.Boolean(), nullable=False, server_default="true"),
    )
    op.drop_table("accident_insurance_household_members")
