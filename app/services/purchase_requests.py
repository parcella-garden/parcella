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
from typing import List, Optional, Tuple

from markupsafe import Markup, escape
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.config import settings
from app.email_service import send_email
from app.i18n import translate
from app.models import (
    PurchaseRequest, PurchaseRequestApproval, PurchaseRequestComment, PurchaseRequestStatus, User,
)
from app.services.errors import ServiceError

REQUIRED_APPROVALS = 2
# Long enough for any real discussion post, short enough to stay an email.
MAX_COMMENT_LENGTH = 5000


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


# ---------------------------------------------------------------------------
# Discussion (issue #249)
# ---------------------------------------------------------------------------

async def add_comment(db, pr: PurchaseRequest, *, author: User, content: str) -> PurchaseRequestComment:
    """Appends a comment; allowed in every status (a rejected request is
    exactly when someone may want to say why). Caller commits, then
    calls notify_comment()."""
    content = (content or "").strip()
    if not content:
        raise ServiceError("errors.comment_empty", http_status=400)
    if len(content) > MAX_COMMENT_LENGTH:
        raise ServiceError("errors.comment_too_long", http_status=400, max=MAX_COMMENT_LENGTH)
    comment = PurchaseRequestComment(purchase_request_id=pr.id, content=content, created_by_id=author.id)
    db.add(comment)
    await db.flush()
    return comment


async def comment_recipients(db, pr: PurchaseRequest, *, author: User) -> List[Tuple[Optional[User], str]]:
    """Who hears about a new comment: the requester (their account, or
    the external address for a request entered on their behalf), and
    every active user who commented or approved before -- not the
    author, and each address once. (user, address); user is None for
    the external requester."""
    users: List[User] = []
    if pr.requested_by_id:
        users.append(await db.get(User, pr.requested_by_id))
    commenter_ids = select(PurchaseRequestComment.created_by_id).where(
        PurchaseRequestComment.purchase_request_id == pr.id
    )
    approver_ids = select(PurchaseRequestApproval.user_id).where(PurchaseRequestApproval.purchase_request_id == pr.id)
    users += (await db.scalars(
        select(User).where(User.id.in_(commenter_ids) | User.id.in_(approver_ids)).order_by(User.name)
    )).all()

    recipients: List[Tuple[Optional[User], str]] = []
    seen = {(author.email or "").strip().lower()}
    for user in users:
        if user is None or not user.is_active or user.id == author.id:
            continue
        address = (user.email or "").strip()
        if address and address.lower() not in seen:
            seen.add(address.lower())
            recipients.append((user, address))
    if pr.requester_email and pr.requester_email.strip().lower() not in seen:
        recipients.append((None, pr.requester_email.strip()))
    return recipients


async def notify_comment(
    db, pr: PurchaseRequest, comment: PurchaseRequestComment, *, author: User, base_url: str, lang: str,
) -> int:
    """Emails the new comment to comment_recipients(). Users get a link
    to the request to answer there; an external requester has no login,
    so their email says to reply to the board instead. Every
    user-entered value is escaped. Returns how many emails went out."""
    link = f"{base_url}/purchase-requests/{pr.id}"
    # The title is user input and ends up in a mail header: no line breaks.
    subject = translate("email.purchase_request_comment.subject", lang, title=" ".join(pr.title.split()))
    comment_html = escape(comment.content).replace("\n", Markup("<br>"))
    sent = 0
    for user, address in await comment_recipients(db, pr, author=author):
        if user is not None:
            action = (
                f'<p><a href="{escape(link)}" style="background: #2d6a4f; color: white; padding: 10px 20px; '
                f'text-decoration: none; border-radius: 4px;">'
                f'{escape(translate("email.purchase_request_comment.button", lang))}</a></p>'
            )
        else:
            action = f'<p>{escape(translate("email.purchase_request_comment.external_hint", lang))}</p>'
        html = f"""
        <html><body style="font-family: sans-serif;">
        <p>{escape(translate("email.purchase_request_comment.body", lang, author=author.name, title=pr.title, app_name=settings.app_name))}</p>
        <blockquote style="border-left: 3px solid #ccc; margin: 0; padding-left: 12px;">{comment_html}</blockquote>
        {action}
        </body></html>
        """
        if await send_email(address, subject, html, db=db):
            sent += 1
    return sent
