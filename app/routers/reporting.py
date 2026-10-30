"""
Reporting module (issue #264): club figures over time as charts, see
app/reporting.py for how each figure is computed and
docs/module-reporting.md for the definitions.
"""
from dataclasses import asdict

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.i18n import t_for
from app.module_flags import require_module
from app.permissions import require_permission
from app.reporting import build_reports
from app.templating import templates

MODULE = "reporting"

router = APIRouter(
    prefix="/reporting",
    tags=["reporting"],
    dependencies=[Depends(require_module(MODULE))],
)


@router.get("/", response_class=HTMLResponse)
async def reporting_index(request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_permission(request, db, MODULE, "read")
    reports = await build_reports(db, request.state.module_flags)
    return templates.TemplateResponse("reporting/index.html", {
        "request": request, "user": user,
        # Handed to Chart.js as JSON (|tojson in the template), never
        # built into markup; also drives the plain data tables.
        "charts": [_display(request, report) for report in reports],
    })


def _display(request: Request, report) -> dict:
    """A report plus its translated texts: title, category labels
    (years and quarters stay as they are), series names and the note."""
    prefix = f"reporting.{report.key}"
    data = asdict(report)
    data["title"] = t_for(request, f"{prefix}.title")
    data["display_labels"] = (
        [t_for(request, f"{prefix}.{label}") for label in report.labels] if report.categorical else report.labels
    )
    data["series_labels"] = [t_for(request, f"{prefix}.series_{series.key}") for series in report.series]
    data["note"] = t_for(request, report.note_key, **report.note_params) if report.note_key else None
    return data
