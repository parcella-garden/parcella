"""
API router: the email log (issue #270, ADR 0120), read-only.

ADMIN role only -- the web page sits in the administration panel
(require_system_admin), and the JWT API's role check is the closest
equivalent (app/api_auth.py is a separate role system, see CLAUDE.md).
"""
from typing import Literal, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api_auth import require_api_role
from app.database import get_db
from app.email_log import parse_status, query_email_logs
from app.models import User, UserRole
from app.schemas import EmailLogPage

router = APIRouter(prefix="/api/v1/email-log", tags=["API: Email log"])


@router.get("", response_model=EmailLogPage, summary="List outgoing emails, newest first")
async def email_log_list(
    status: Optional[Literal["SENT", "FAILED"]] = Query(None, description="Omit for all"),
    recipient: Optional[str] = Query(None, max_length=320, description="Substring of the recipient address"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_role(UserRole.ADMIN)),
):
    rows, total = await query_email_logs(
        db, status=parse_status(status), recipient=recipient, limit=limit, offset=offset,
    )
    return EmailLogPage(total=total, items=rows)
