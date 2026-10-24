"""External contacts: companies with people underneath

Revision ID: 0109_contact_companies
Revises: 0108_rename_legacy_indexes
Create Date: 2026-10-24

- external_contacts.kind (COMPANY / PERSON), company_id (a person's
  company, self-reference) and position (a person's role there).
- Existing rows: a row with a person name becomes a PERSON, every other
  row a COMPANY. Persons that carried a company_name are linked to the
  company of that name (ignoring case and surrounding blanks), which is
  created from their data if there's no company-only row for it yet.
  Their company_name is cleared; address, IBAN and documents folder
  move to the company where the company has none, and are cleared on
  the person where they equal the company's. A differing value stays on
  the person, so nothing is lost.

The unique indexes stay as they are: persons never have a company_name,
companies never a person name. See ADR 0110.
"""
import uuid
from typing import Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0109_contact_companies"
down_revision: Union[str, None] = "0108_rename_legacy_indexes"
branch_labels = None
depends_on = None

_kind_enum = postgresql.ENUM("COMPANY", "PERSON", name="externalcontactkind", create_type=False)

_ADDRESS = ("street", "postal_code", "city")


def _clean(value):
    return (value or "").strip() or None


def upgrade() -> None:
    _kind_enum.create(op.get_bind(), checkfirst=True)
    op.add_column("external_contacts", sa.Column("kind", _kind_enum, nullable=False, server_default="COMPANY"))
    op.add_column("external_contacts", sa.Column("company_id", sa.String(36), nullable=True))
    op.add_column("external_contacts", sa.Column("position", sa.String(100), nullable=True))
    op.create_foreign_key(
        "fk_external_contacts_company_id", "external_contacts", "external_contacts",
        ["company_id"], ["id"], ondelete="SET NULL",
    )
    op.create_index("ix_external_contacts_company_id", "external_contacts", ["company_id"])
    op.alter_column("external_contacts", "kind", server_default=None)
    op.execute("UPDATE external_contacts SET kind = 'PERSON' WHERE first_name IS NOT NULL OR last_name IS NOT NULL")

    bind = op.get_bind()
    columns = "id, company_name, street, postal_code, city, iban, cloud_folder, deleted_at, created_at"
    persons = bind.execute(sa.text(
        f"SELECT {columns} FROM external_contacts "
        "WHERE kind = 'PERSON' AND company_name IS NOT NULL AND trim(company_name) <> '' "
        "ORDER BY deleted_at NULLS FIRST, created_at"
    )).mappings().all()
    groups: dict[str, list] = {}
    for person in persons:
        groups.setdefault(" ".join(person["company_name"].lower().split()), []).append(person)

    for key, members in groups.items():
        company = bind.execute(sa.text(
            f"SELECT {columns} FROM external_contacts "
            "WHERE kind = 'COMPANY' AND deleted_at IS NULL AND lower(trim(company_name)) = :key"
        ), {"key": key}).mappings().first()
        if company is None:
            active = [m for m in members if m["deleted_at"] is None]
            company = {
                "id": str(uuid.uuid4()),
                "company_name": members[0]["company_name"].strip(),
                **{f: None for f in (*_ADDRESS, "iban", "cloud_folder")},
                # A company only its deleted people knew about stays deleted.
                "deleted_at": None if active else members[0]["deleted_at"],
            }
            bind.execute(sa.text(
                "INSERT INTO external_contacts (id, kind, company_name, deleted_at, created_at, updated_at) "
                "VALUES (:id, 'COMPANY', :company_name, :deleted_at, now(), now())"
            ), company)
        company = dict(company)

        # Fill what the company lacks from its people, then link them.
        if not any(_clean(company[f]) for f in _ADDRESS):
            source = next((m for m in members if any(_clean(m[f]) for f in _ADDRESS)), None)
            if source is not None:
                company.update({f: _clean(source[f]) for f in _ADDRESS})
        for field in ("iban", "cloud_folder"):
            if not _clean(company[field]):
                company[field] = next((_clean(m[field]) for m in members if _clean(m[field])), None)
        bind.execute(sa.text(
            "UPDATE external_contacts SET street = :street, postal_code = :postal_code, city = :city, "
            "iban = :iban, cloud_folder = :cloud_folder WHERE id = :id"
        ), company)

        for member in members:
            same_address = all(_clean(member[f]) == _clean(company[f]) for f in _ADDRESS)
            bind.execute(sa.text(
                "UPDATE external_contacts SET company_id = :company_id, company_name = NULL"
                + (", street = NULL, postal_code = NULL, city = NULL" if same_address else "")
                + (", iban = NULL" if _clean(member["iban"]) == _clean(company["iban"]) else "")
                + (", cloud_folder = NULL" if _clean(member["cloud_folder"]) == _clean(company["cloud_folder"]) else "")
                + " WHERE id = :id"
            ), {"company_id": company["id"], "id": member["id"]})

    # Persons with a blank-only company_name.
    op.execute("UPDATE external_contacts SET company_name = NULL WHERE kind = 'PERSON'")


def downgrade() -> None:
    # Back to "company + person in one row": persons take their company's
    # name, and its address/IBAN where they have none of their own.
    # The companies themselves stay, as company-only contacts.
    op.execute("""
        UPDATE external_contacts AS p SET
            company_name = c.company_name,
            street = coalesce(p.street, c.street),
            postal_code = coalesce(p.postal_code, c.postal_code),
            city = coalesce(p.city, c.city),
            iban = coalesce(p.iban, c.iban)
        FROM external_contacts AS c
        WHERE p.company_id = c.id
    """)
    op.drop_index("ix_external_contacts_company_id", table_name="external_contacts")
    op.drop_constraint("fk_external_contacts_company_id", "external_contacts", type_="foreignkey")
    op.drop_column("external_contacts", "position")
    op.drop_column("external_contacts", "company_id")
    op.drop_column("external_contacts", "kind")
    _kind_enum.drop(op.get_bind(), checkfirst=True)
