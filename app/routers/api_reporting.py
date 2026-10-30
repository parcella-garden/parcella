"""
API router: Reporting (issue #264) -- the same figures as /reporting/,
from app/reporting.py. Category labels are stable ids ("boomers",
"owes_fee"); the web page translates them, API clients get them as-is.
"""
from dataclasses import asdict

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api_auth import require_api_permission
from app.database import get_db
from app.module_flags import require_module
from app.reporting import build_reports
from app.schemas import ReportingOut

MODULE = "reporting"

router = APIRouter(
    prefix="/api/v1/reporting",
    tags=["API: Reporting"],
    dependencies=[Depends(require_module(MODULE))],
)


@router.get("", response_model=ReportingOut, summary="All reporting figures")
async def reporting_all(
    request: Request,
    db: AsyncSession = Depends(get_db),
    _user=Depends(require_api_permission(MODULE, "read")),
):
    reports = await build_reports(db, getattr(request.state, "module_flags", {}))
    return ReportingOut(reports=[asdict(report) for report in reports])
