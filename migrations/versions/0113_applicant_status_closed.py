"""Applicants: WITHDRAWN becomes CLOSED

Revision ID: 0113_applicant_status_closed
Revises: 0112_finance_budget_lines
Create Date: 2026-10-26

- Issue #253: no more "withdrawn" status. An applicant who turns an
  offer down either wants no further offers (REJECTED) or stays on the
  waiting list (CONTACTED) -- existing WITHDRAWN applications go back
  to CONTACTED, as kermie decided.
- Issue #252: ACCEPTED is now an open status (handover still being
  negotiated); a parcel handover moves the application to the new
  CLOSED status instead. Until now a handover set ACCEPTED, so an
  ACCEPTED application whose email address belongs to a member is
  taken to be a finished handover and becomes CLOSED -- otherwise it
  would show up as open again, with an "Assign a parcel" button.

Postgres can't drop an enum label, so the now unused WITHDRAWN label is
renamed to CLOSED (uppercase member name, see CLAUDE.md "Enum values").
Unlike ADD VALUE, RENAME VALUE runs fine inside a transaction.
Old change_history rows keep their "WITHDRAWN" text -- history stays
truthful, and the translation key for it is kept.

The downgrade turns CLOSED back into ACCEPTED (what a handover used to
set) and renames the label back to WITHDRAWN; which applications were
WITHDRAWN before can't be restored.
"""
from typing import Union

from alembic import op

revision: str = "0113_applicant_status_closed"
down_revision: Union[str, None] = "0112_finance_budget_lines"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE applicants SET status = 'CONTACTED' WHERE status = 'WITHDRAWN'")
    op.execute("ALTER TYPE applicantstatus RENAME VALUE 'WITHDRAWN' TO 'CLOSED'")
    op.execute("""
        UPDATE applicants SET status = 'CLOSED'
        WHERE status = 'ACCEPTED'
          AND EXISTS (SELECT 1 FROM member_emails WHERE lower(member_emails.address) = lower(applicants.email))
    """)


def downgrade() -> None:
    op.execute("UPDATE applicants SET status = 'ACCEPTED' WHERE status = 'CLOSED'")
    op.execute("ALTER TYPE applicantstatus RENAME VALUE 'CLOSED' TO 'WITHDRAWN'")
