"""Work-hours overview and the yearly configuration (mandatory hours, signup confirmation)."""
from fastapi import APIRouter
from datetime import date, datetime, timezone
from typing import Optional
from fastapi import Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models import (
    ParticipationStatus,
    SessionType,
    WorkHoursConfiguration,
    WorkHoursMode,
    WorkSession,
)
from app.permissions import require_permission
from app.i18n import t_for
from app.services.work_hours import (
    get_config_for_year,
    load_signup_confirmation_settings,
    new_participation_cutoff,
    save_configuration_for_year,
    save_signup_confirmation_settings,
)
from app.templating import templates

router = APIRouter()


# ---------------------------------------------------------------------------
# Dashboard / Overview
# ---------------------------------------------------------------------------

@router.get("/", response_class=HTMLResponse)
async def work_hours_overview(
    request: Request,
    year: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
):
    user = await require_permission(request, db, "work_hours", "read")

    if not year:
        year = date.today().year

    config = await get_config_for_year(db, year)

    # All available years, for the dropdown
    years_result = await db.execute(
        select(WorkHoursConfiguration.year).order_by(WorkHoursConfiguration.year.desc())
    )
    available_years = [r[0] for r in years_result.all()]

    # Sessions of the year
    sessions_result = await db.execute(
        select(WorkSession)
        .options(selectinload(WorkSession.participations))
        .where(func.extract("year", WorkSession.date) == year)
        .order_by(WorkSession.date.desc())
    )
    sessions = sessions_result.scalars().all()

    return templates.TemplateResponse(
        request, "work_hours/overview.html",
        {
            "request": request,
            "user": user,
            "year": year,
            "config": config,
            "sessions": sessions,
            "available_years": available_years,
            "SessionType": SessionType,
            "ParticipationStatus": ParticipationStatus,
            "new_participation_cutoff": new_participation_cutoff(),
            "epoch_datetime": datetime.min.replace(tzinfo=timezone.utc),
            "today": date.today(),
        },
    )


# ---------------------------------------------------------------------------
# Work hours configuration
# ---------------------------------------------------------------------------

@router.get("/configuration", response_class=HTMLResponse)
async def configuration_page(request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_permission(request, db, "work_hours", "read")

    result = await db.execute(
        select(WorkHoursConfiguration).order_by(WorkHoursConfiguration.year.desc())
    )
    configurations = result.scalars().all()
    confirmation_enabled, confirmation_text = await load_signup_confirmation_settings(db)

    return templates.TemplateResponse(
        request, "work_hours/configuration.html",
        {
            "request": request,
            "user": user,
            "configurations": configurations,
            "confirmation_enabled": confirmation_enabled,
            "confirmation_text": confirmation_text,
            "confirmation_saved": request.query_params.get("confirmation_saved") == "1",
            "WorkHoursMode": WorkHoursMode,
            "current_year": date.today().year,
        },
    )


@router.get("/configuration/{configuration_id}/edit", response_class=HTMLResponse)
async def configuration_edit_page(
    configuration_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user = await require_permission(request, db, "work_hours", "write")

    result = await db.execute(
        select(WorkHoursConfiguration).where(WorkHoursConfiguration.id == configuration_id)
    )
    configuration = result.scalar_one_or_none()
    if not configuration:
        raise HTTPException(status_code=404, detail=t_for(request, "work_hours.errors.configuration_not_found"))

    return templates.TemplateResponse(
        request, "work_hours/configuration_form.html",
        {
            "request": request,
            "user": user,
            "configuration": configuration,
            "WorkHoursMode": WorkHoursMode,
        },
    )


@router.post("/configuration/{configuration_id}/edit")
async def configuration_update(
    configuration_id: str,
    request: Request,
    year: int = Form(...),
    hours_required: str = Form(...),
    rate_per_hour_eur: str = Form(...),
    mode: str = Form("PER_PARCEL"),
    note: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    await require_permission(request, db, "work_hours", "write")

    result = await db.execute(
        select(WorkHoursConfiguration).where(WorkHoursConfiguration.id == configuration_id)
    )
    configuration = result.scalar_one_or_none()
    if not configuration:
        raise HTTPException(status_code=404, detail=t_for(request, "work_hours.errors.configuration_not_found"))

    # If the year is being changed: check for a collision with another entry
    if year != configuration.year:
        kollision = await get_config_for_year(db, year)
        if kollision and kollision.id != configuration_id:
            raise HTTPException(
                status_code=400,
                detail=t_for(request, "work_hours.errors.configuration_year_exists", year=year)
            )

    configuration.year = year
    configuration.hours_required = float(hours_required.replace(",", "."))
    configuration.rate_per_hour_eur = float(rate_per_hour_eur.replace(",", "."))
    configuration.mode = WorkHoursMode(mode)
    configuration.note = note.strip() or None

    await db.commit()
    return RedirectResponse("/work-hours/configuration", status_code=302)


@router.post("/configuration/{configuration_id}/delete")
async def configuration_delete(
    configuration_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    await require_permission(request, db, "work_hours", "delete")

    result = await db.execute(
        select(WorkHoursConfiguration).where(WorkHoursConfiguration.id == configuration_id)
    )
    configuration = result.scalar_one_or_none()
    if configuration:
        await db.delete(configuration)
        await db.commit()

    return RedirectResponse("/work-hours/configuration", status_code=302)


@router.post("/configuration/new")
async def configuration_create(
    request: Request,
    year: int = Form(...),
    hours_required: str = Form(...),
    rate_per_hour_eur: str = Form(...),
    mode: str = Form("PER_PARCEL"),
    note: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    await require_permission(request, db, "work_hours", "write")

    await save_configuration_for_year(
        db, year,
        hours_required=float(hours_required.replace(",", ".")),
        rate_per_hour_eur=float(rate_per_hour_eur.replace(",", ".")),
        mode=mode, note=(note.strip() or None),
    )
    await db.commit()
    return RedirectResponse("/work-hours/configuration", status_code=302)


@router.post("/configuration/signup-confirmation")
async def signup_confirmation_save(request: Request, db: AsyncSession = Depends(get_db)):
    """Issue #313: on/off and the boilerplate of the confirmation email
    sent after a public work-session sign-up."""
    await require_permission(request, db, "work_hours", "write")
    form = await request.form()
    await save_signup_confirmation_settings(
        db, enabled=form.get("enabled") == "true", text=str(form.get("text") or ""),
    )
    await db.commit()
    return RedirectResponse("/work-hours/configuration?confirmation_saved=1", status_code=303)
