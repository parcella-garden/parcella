"""Year-end evaluation and its CSV export."""
from fastapi import APIRouter
import csv
import io
from datetime import date
from typing import Optional
from fastapi import Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.csv_utils import csv_safe
from app.models import WorkHoursConfiguration, WorkHoursMode
from app.permissions import require_permission
from app.i18n import t_for
from app.services.work_hours import attended_sessions_by_member, evaluate_year
from app.templating import templates

router = APIRouter()


# ---------------------------------------------------------------------------
# Evaluation: annual standing per member/parcel
# ---------------------------------------------------------------------------

@router.get("/evaluation", response_class=HTMLResponse)
async def evaluation(
    request: Request,
    year: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
):
    user = await require_permission(request, db, "work_hours", "read")

    if not year:
        year = date.today().year

    years_result = await db.execute(
        select(WorkHoursConfiguration.year).order_by(WorkHoursConfiguration.year.desc())
    )
    available_years = [r[0] for r in years_result.all()]

    config, rows = await evaluate_year(db, year)
    sessions_by_member = await attended_sessions_by_member(db, year) if config else {}

    return templates.TemplateResponse(
        request, "work_hours/evaluation.html",
        {
            "request": request,
            "user": user,
            "year": year,
            "config": config,
            "rows": rows,
            "sessions_by_member": sessions_by_member,
            "available_years": available_years,
            "WorkHoursMode": WorkHoursMode,
        },
    )


@router.get("/evaluation/csv")
async def evaluation_export_csv(
    request: Request,
    year: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
):
    await require_permission(request, db, "work_hours", "read")

    if not year:
        year = date.today().year

    config, rows = await evaluate_year(db, year)
    if not config:
        raise HTTPException(status_code=404, detail=t_for(request, "work_hours.errors.no_configuration_for_year", year=year))

    output = io.StringIO()
    writer = csv.writer(output, delimiter=";")
    # Issue #364: headers and yes/no in the club's language (were German),
    # the same labels as the evaluation page.
    t = lambda key: t_for(request, key)
    yes, no = t("common.yes"), t("common.no")
    writer.writerow([
        t("work_hours.evaluation.col_parcel"), t("work_hours.evaluation.col_tenant"),
        f'{t("work_hours.evaluation.col_required")} (h)', f'{t("work_hours.evaluation.col_sessions")} (h)',
        f'{t("work_hours.evaluation.col_sponsorship")} (h)', f'{t("work_hours.evaluation.col_transfers")} (h)',
        f'{t("work_hours.evaluation.col_total")} (h)', f'{t("work_hours.evaluation.col_open")} (h)',
        f'{t("work_hours.evaluation.col_debt")} (EUR)', t("work_hours.evaluation.status_exempt"),
        t("work_hours.evaluation.fulfilled_label"),
    ])

    # Same rule as the evaluation page for what counts as "exempt": ONE
    # exempt tenant is enough to exempt the whole parcel (any(), not
    # all() -- see docs/ADR/README.md). Computed once, in
    # app.services.work_hours.evaluate_parcel(), not re-derived here.
    if config.mode == WorkHoursMode.PER_PARCEL:
        for row in rows:
            session_hours = sum(t["hours"]["session_hours"] for t in row["tenant_details"])
            sponsorship_hours = sum(t["hours"]["sponsorship_hours"] for t in row["tenant_details"])
            transferred_net = sum(t["hours"]["transferred_net"] for t in row["tenant_details"])
            names = [t["member"].full_name for t in row["tenant_details"]]
            writer.writerow([
                csv_safe(row["parcel"].plot_number),
                csv_safe("; ".join(names)),
                f"{row['required_hours']:.1f}",
                f"{session_hours:.1f}",
                f"{sponsorship_hours:.1f}",
                f"{transferred_net:.1f}",
                f"{row['total_hours']:.1f}",
                f"{row['outstanding_hours']:.1f}",
                f"{row['amount_due']:.2f}".replace(".", ","),
                yes if row["exempt"] else no,
                yes if row["fulfilled"] else no,
            ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=work_hours_{year}.csv"},
    )
