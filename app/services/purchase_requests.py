"""
Shared purchase-request business logic, called by both
app/routers/purchase_requests.py (HTML) and
app/routers/api_purchase_requests.py (API) -- see ADR 0070.

Four-eyes principle: two different board members must agree before a
PurchaseRequest counts as approved; the requester themselves may not
give either approval; a single rejection vetoes it. This is this
project's own documented highest-regression-risk area (see
docs/testing.md) -- what's shared here is deliberately narrow: only the
one rule that must never be bypassable regardless of caller (the
self-approval block) and the approval-counting/auto-transition logic.
The "already handled" short-circuits (not OPEN, already approved by
this user) stay in each router, since HTML and API already handled
those cases differently on purpose (HTML redirects silently, API
409s) -- unifying that wasn't broken, so it isn't touched.

Two real divergences found and fixed along the way:
1. Approval authority is deliberately narrower than ordinary module
   write access (see docs/module-purchase-requests.md) -- HTML's
   require_admin is Group-aware (ADMIN/BOARD role, or a
   grants_full_access/grants_system_admin group); the API's
   require_vorstand_api was role-only. The reverse-direction version of
   ADR 0071's TREASURER bug: here the API was *stricter* than HTML, not
   looser. Fixed via a new require_api_full_access (app/api_auth.py).
2. The API's confirmation email for an external (non-login) requester
   never actually included the confirmation link/button -- it told the
   requester to "log in", which they have no account to do. Fixed by
   sharing the same email content (incl. the actual link) HTML already
   built correctly.
"""
from datetime import datetime, timezone
from typing import Optional

from app.config import settings
from app.email_service import send_email
from app.i18n import translate
from app.models import PurchaseRequest, PurchaseRequestApproval, PurchaseRequestStatus
from app.services.errors import ServiceError

REQUIRED_APPROVALS = 2


async def create_purchase_request(
    db, *, title: str, justification: str, link: Optional[str], estimated_cost_eur,
    created_by_id: str, requester_name: Optional[str] = None, requester_email: Optional[str] = None,
    external_contact_id: Optional[str] = None,
) -> PurchaseRequest:
    """external_contact_id: an optional supplier, already validated by
    the caller (app/routers/external_contacts.py's resolve_picked_contact
    or the API's own check)."""
    pr = PurchaseRequest(
        title=title.strip(), justification=justification.strip(),
        link=(link or "").strip() or None, estimated_cost_eur=estimated_cost_eur,
        created_by_id=created_by_id, external_contact_id=external_contact_id,
    )

    if requester_email:
        from app.auth import serializer

        email = requester_email.strip().lower()
        pr.requester_name = (requester_name or "").strip() or None
        pr.requester_email = email
        pr.confirmation_token = serializer.dumps(email, salt="purchase_request")
    else:
        pr.requested_by_id = created_by_id

    db.add(pr)
    await db.flush()
    return pr


async def send_confirmation_email(
    pr: PurchaseRequest, *, admin_name: str, confirmation_link: str, lang: str, db=None,
) -> None:
    subject = translate("email.purchase_request_confirm.subject", lang, title=pr.title)
    html = f"""
    <html><body style="font-family: sans-serif;">
    <p>{translate("email.purchase_request_confirm.greeting", lang, name=pr.requester_name or "")}</p>
    <p>{translate("email.purchase_request_confirm.body", lang, admin_name=admin_name, app_name=settings.app_name)}</p>
    <p><strong>{pr.title}</strong><br>{pr.justification}</p>
    <p>{translate("email.purchase_request_confirm.instruction", lang)}</p>
    <p><a href="{confirmation_link}" style="background: #2d6a4f; color: white; padding: 10px 20px;
       text-decoration: none; border-radius: 4px;">{translate("email.purchase_request_confirm.button", lang)}</a></p>
    </body></html>
    """
    await send_email(pr.requester_email, subject, html, db=db)


async def approve_purchase_request(db, pr: PurchaseRequest, *, acting_user_id: str) -> None:
    """Records an approval and flips status to APPROVED once
    REQUIRED_APPROVALS distinct approvals are reached. Caller must
    already have checked pr.status == OPEN and that acting_user_id
    hasn't already approved -- this only enforces the one rule that's
    never conditional on caller: the requester can't approve their own
    request."""
    if acting_user_id in (pr.requested_by_id, pr.created_by_id):
        raise ServiceError("errors.requester_cannot_self_approve", http_status=403)

    db.add(PurchaseRequestApproval(purchase_request_id=pr.id, user_id=acting_user_id))
    await db.flush()

    # +1 since pr.approvals isn't reloaded to reflect the just-added row yet.
    if len(pr.approvals) + 1 >= REQUIRED_APPROVALS:
        pr.status = PurchaseRequestStatus.APPROVED
        pr.approved_at = datetime.now(timezone.utc)


async def reject_purchase_request(db, pr: PurchaseRequest, *, acting_user_id: str, reason: str) -> None:
    """Veto principle: a single rejection is enough. Caller must
    already have checked pr.status == OPEN."""
    pr.status = PurchaseRequestStatus.REJECTED
    pr.rejection_reason = reason.strip()
    pr.rejected_by_id = acting_user_id
    pr.rejected_at = datetime.now(timezone.utc)
    await db.flush()
