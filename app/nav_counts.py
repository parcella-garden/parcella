"""
"Needs attention" counts shared by the nav badges (base.html) and the
dashboard tiles -- computed once per request by nav_counts_middleware
(app/main.py) so the badge on a nav entry and the matching dashboard
tile can never disagree (ADR 0019, ADR 0100).

Same stateless shape as the work-session sign-up badge (ADR 0079): each
count is a plain query over existing status/date columns, no per-user
"seen" state. A badge clears itself when the underlying item is dealt
with (applicant moved past NEW, purchase request decided, conversation
closed, task's due date moved or task deleted).
"""
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.helpdesk.base import HIDDEN_STATUSES
from app.helpdesk.registry import get_active_helpdesk_type
from app.models import (
    Applicant, ApplicantStatus, HelpdeskConversationLink, PurchaseRequest,
    PurchaseRequestStatus, Task,
)

NAV_COUNT_KEYS = ("applicants_new", "purchase_requests_open", "freescout_open", "tasks_overdue")


async def load_nav_counts(db: AsyncSession) -> dict[str, int]:
    # Counts exactly what /applicants/?filter=new lists.
    applicants_new = await db.scalar(
        select(func.count()).select_from(Applicant).where(Applicant.status == ApplicantStatus.NEW)
    )
    purchase_requests_open = await db.scalar(
        select(func.count()).select_from(PurchaseRequest).where(
            PurchaseRequest.status == PurchaseRequestStatus.OPEN
        )
    )
    # Currently active/pending conversations of the active helpdesk,
    # regardless of member association (issue #231) -- the same rows the
    # /support/ list shows (app/routers/support.py).
    freescout_open = await db.scalar(
        select(func.count()).select_from(HelpdeskConversationLink).where(
            HelpdeskConversationLink.provider == await get_active_helpdesk_type(db),
            HelpdeskConversationLink.status.notin_(HIDDEN_STATUSES),
        )
    )
    # "Overdue" means exactly what the board shows in red (issue #127):
    # a due_date in the past and not done (issue #257, docs/ADR/0115),
    # whichever list the card is in.
    tasks_overdue = await db.scalar(
        select(func.count()).select_from(Task).where(
            Task.due_date < date.today(), Task.completed_at.is_(None),
        )
    )
    return {
        "applicants_new": applicants_new or 0,
        "purchase_requests_open": purchase_requests_open or 0,
        "freescout_open": freescout_open or 0,
        "tasks_overdue": tasks_overdue or 0,
    }


def jinja_nav_count(request, key: str) -> int:
    """Jinja global for base.html's nav badges -- reads the counts
    nav_counts_middleware already computed for this request."""
    return getattr(request.state, "nav_counts", {}).get(key, 0)
