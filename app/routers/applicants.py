"""
Applicants module web router: people who applied for a free garden
plot. See docs/module-applicants.md.

Gated by the "applicants" module permission (see app/permissions.py):
ADMIN/BOARD always have full access; other roles need a group grant.
Viewing requires "read"; adding an applicant by hand, editing contact
data, status and board note require "write"; deleting an applicant for
good requires "delete" (ADR 0091 -- the GDPR exception to
historization).

The public side -- the application form on the club website -- lives in
app/routers/api_public.py, behind its own module flag.
"""
from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Request, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, or_, select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import (
    APPLICANT_OPEN_STATUSES, Applicant, ApplicantSource, ApplicantStatus, ChangeHistory,
)
from app.permissions import require_permission
from app.module_flags import require_module
from app.templating import templates
from app.services.errors import ServiceError
from app.services.applicants import create_applicant, delete_applicant, find_red_flags, update_applicant
from app.services.parcel_handover import hand_over_parcel, plan_handover, terminated_parcels
from app.parcel_cloud_folders import browse_folder_picker
from app.i18n import t_for

router = APIRouter(
    prefix="/applicants",
    tags=["applicants"],
    dependencies=[Depends(require_module("applicants"))],
)

# ?filter= on the list page. "open" is the default, and the dashboard
# card counts exactly the "new" one -- keep the two in sync (ADR 0019).
_FILTERS = {
    "open": APPLICANT_OPEN_STATUSES,
    "new": (ApplicantStatus.NEW,),
    "closed": (ApplicantStatus.ACCEPTED, ApplicantStatus.WITHDRAWN, ApplicantStatus.REJECTED),
    "all": None,
}


async def _get_or_404(db: AsyncSession, applicant_id: str) -> Applicant:
    result = await db.execute(
        select(Applicant).options(selectinload(Applicant.created_by)).where(Applicant.id == applicant_id)
    )
    applicant = result.scalar_one_or_none()
    if applicant is None:
        raise HTTPException(status_code=404, detail="Applicant not found")
    return applicant


def _form_values(form) -> dict:
    return {field: form.get(field) for field in ("email", "first_name", "last_name", "phone", "message", "board_note", "applied_at")}


# ---------------------------------------------------------------------------
# List
# ---------------------------------------------------------------------------

@router.get("/", response_class=HTMLResponse)
async def applicants_list(request: Request, filter: str = "open", search: str = "", db: AsyncSession = Depends(get_db)):
    user = await require_permission(request, db, "applicants", "read")
    if filter not in _FILTERS:
        filter = "open"

    query = select(Applicant).order_by(Applicant.applied_at.desc())
    statuses = _FILTERS[filter]
    if statuses is not None:
        query = query.where(Applicant.status.in_(statuses))
    search = search.strip()
    if search:
        # Every text field, the board note included -- so a FreeScout
        # ticket number noted down there finds the applicant.
        pattern = f"%{search}%"
        query = query.where(or_(
            Applicant.first_name.ilike(pattern), Applicant.last_name.ilike(pattern),
            Applicant.email.ilike(pattern), Applicant.phone.ilike(pattern),
            Applicant.message.ilike(pattern), Applicant.board_note.ilike(pattern),
        ))
    applicants = (await db.execute(query)).scalars().all()

    # How often each listed address has applied in total -- a hint for
    # the board that someone applied twice, not a merge (see the module
    # doc's "known gaps").
    emails = {a.email for a in applicants}
    counts = {}
    if emails:
        rows = await db.execute(
            select(Applicant.email, func.count()).where(Applicant.email.in_(emails)).group_by(Applicant.email)
        )
        counts = dict(rows.all())

    return templates.TemplateResponse("applicants/list.html", {
        "request": request, "user": user, "applicants": applicants,
        "filter": filter, "search": search, "application_counts": counts,
        "red_flags": await _red_flags(request, db, applicants),
    })


# ---------------------------------------------------------------------------
# Create by hand (registered before /{applicant_id})
# ---------------------------------------------------------------------------

@router.get("/new", response_class=HTMLResponse)
async def applicant_new_page(request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_permission(request, db, "applicants", "write")
    return templates.TemplateResponse("applicants/form.html", {
        "request": request, "user": user, "values": {}, "today": date.today(),
    })


@router.post("/new")
async def applicant_create(request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_permission(request, db, "applicants", "write")
    values = _form_values(await request.form())
    try:
        applicant = await create_applicant(
            db, **values, source=ApplicantSource.MANUAL, created_by_id=user.id,
        )
    except ServiceError as e:
        return templates.TemplateResponse("applicants/form.html", {
            "request": request, "user": user, "values": values, "error": e.key, "today": date.today(),
        }, status_code=e.http_status)
    return RedirectResponse(url=f"/applicants/{applicant.id}", status_code=303)


# ---------------------------------------------------------------------------
# Detail / edit / delete
# ---------------------------------------------------------------------------

async def _red_flags(request: Request, db: AsyncSession, applicants) -> dict:
    """Matches against red-flagged external contacts (ADR 0098) -- none
    while the external contacts module is switched off."""
    if not getattr(request.state, "module_flags", {}).get("external_contacts", True):
        return {}
    return await find_red_flags(db, applicants)


async def _detail_context(request, db, user, applicant, error=None) -> dict:
    others = (await db.execute(
        select(Applicant)
        .where(Applicant.email == applicant.email, Applicant.id != applicant.id)
        .order_by(Applicant.applied_at.desc())
    )).scalars().all()
    history = (await db.execute(
        select(ChangeHistory)
        .options(selectinload(ChangeHistory.changed_by))
        .where(ChangeHistory.entity_type == "Applicant", ChangeHistory.entity_id == applicant.id)
        .order_by(ChangeHistory.changed_at.desc())
    )).scalars().all()
    return {
        "request": request, "user": user, "applicant": applicant,
        "other_applications": others, "history": history,
        "statuses": list(ApplicantStatus), "error": error, "today": date.today(),
        "is_open": applicant.status in APPLICANT_OPEN_STATUSES,
        "red_flags": (await _red_flags(request, db, [applicant])).get(applicant.id, []),
    }


@router.get("/{applicant_id}", response_class=HTMLResponse)
async def applicant_detail(applicant_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_permission(request, db, "applicants", "read")
    applicant = await _get_or_404(db, applicant_id)
    return templates.TemplateResponse(
        "applicants/detail.html", await _detail_context(request, db, user, applicant),
    )


@router.post("/{applicant_id}/edit")
async def applicant_update(applicant_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_permission(request, db, "applicants", "write")
    applicant = await _get_or_404(db, applicant_id)
    form = await request.form()
    changes = _form_values(form)
    if form.get("status") in ApplicantStatus.__members__:
        changes["status"] = form.get("status")
    try:
        await update_applicant(db, applicant, changed_by_id=user.id, **changes)
    except ServiceError as e:
        await db.rollback()
        applicant = await _get_or_404(db, applicant_id)
        return templates.TemplateResponse(
            "applicants/detail.html", await _detail_context(request, db, user, applicant, error=e.key),
            status_code=e.http_status,
        )
    return RedirectResponse(url=f"/applicants/{applicant_id}", status_code=303)


@router.post("/{applicant_id}/delete")
async def applicant_delete(applicant_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    await require_permission(request, db, "applicants", "delete")
    applicant = await _get_or_404(db, applicant_id)
    await delete_applicant(db, applicant)
    return RedirectResponse(url="/applicants/", status_code=303)


# ---------------------------------------------------------------------------
# Handing a terminated parcel over (ADR 0101)
# ---------------------------------------------------------------------------

def _parse_handover_date(value: Optional[str]) -> date:
    try:
        return date.fromisoformat(value) if value else date.today()
    except ValueError:
        return date.today()


async def _handover_permission(request: Request, db: AsyncSession):
    """Touches applicants and members/parcels alike -- needs write on both."""
    user = await require_permission(request, db, "applicants", "write")
    await require_permission(request, db, "members_parcels", "write")
    return user


def _can_manage_folders(request: Request) -> bool:
    """Parcel cloud folders are full-access only (docs/module-cloud-storage.md);
    the old folder is retired on a handover regardless."""
    return bool(getattr(request.state, "module_flags", {}).get("cloud_storage")) and getattr(
        request.state, "is_full_access", False,
    )


async def _handover_context(
    request: Request, db: AsyncSession, user, applicant: Applicant, *,
    parcel_id: str, handover_date: date, co_applicant_ids: list[str],
    new_folder_path: str = "", pick_path: Optional[str] = None, error=None,
) -> dict:
    can_manage_folders = _can_manage_folders(request)
    result = await db.execute(
        select(Applicant)
        .where(Applicant.id != applicant.id, Applicant.status.in_(APPLICANT_OPEN_STATUSES))
        .order_by(Applicant.last_name, Applicant.first_name, Applicant.applied_at)
    )
    plan = None
    if parcel_id and error is None:
        try:
            plan = await plan_handover(
                db, parcel_id=parcel_id, applicant_ids=[applicant.id, *co_applicant_ids],
                handover_date=handover_date, new_folder_path=new_folder_path if can_manage_folders else None,
            )
        except ServiceError as e:
            error = e
    picker = None
    if can_manage_folders and pick_path is not None:
        picker = await browse_folder_picker(
            db, pick_path,
            root_label=t_for(request, "parcels.detail.cloud_picker_root_label"),
            not_configured_message=t_for(request, "parcels.cloud_storage.not_configured"),
        )
    return {
        "request": request, "user": user, "applicant": applicant,
        "parcels": await terminated_parcels(db), "co_applicant_candidates": result.scalars().all(),
        "parcel_id": parcel_id, "handover_date": handover_date, "co_applicant_ids": co_applicant_ids,
        "can_manage_folders": can_manage_folders, "new_folder_path": new_folder_path, "picker": picker,
        "plan": plan, "error": error,
    }


@router.get("/{applicant_id}/assign-parcel", response_class=HTMLResponse)
async def applicant_assign_parcel_page(
    applicant_id: str, request: Request,
    parcel_id: str = "", handover_date: str = "", co_applicant_ids: List[str] = Query([]),
    new_folder_path: str = "", cloud_pick: str = "", pick_path: str = "",
    db: AsyncSession = Depends(get_db),
):
    user = await _handover_permission(request, db)
    applicant = await _get_or_404(db, applicant_id)
    return templates.TemplateResponse(
        "applicants/assign_parcel.html",
        await _handover_context(
            request, db, user, applicant, parcel_id=parcel_id,
            handover_date=_parse_handover_date(handover_date), co_applicant_ids=co_applicant_ids,
            new_folder_path=new_folder_path, pick_path=pick_path if cloud_pick == "1" else None,
        ),
    )


@router.post("/{applicant_id}/assign-parcel")
async def applicant_assign_parcel(applicant_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    user = await _handover_permission(request, db)
    applicant = await _get_or_404(db, applicant_id)
    form = await request.form()
    parcel_id = form.get("parcel_id") or ""
    handover_date = _parse_handover_date(form.get("handover_date"))
    co_applicant_ids = form.getlist("co_applicant_ids")
    new_folder_path = (form.get("new_folder_path") or "") if _can_manage_folders(request) else ""
    try:
        plan = await plan_handover(
            db, parcel_id=parcel_id, applicant_ids=[applicant.id, *co_applicant_ids],
            handover_date=handover_date, new_folder_path=new_folder_path,
        )
    except ServiceError as e:
        # plan_handover() validates before anything is changed -- no rollback needed.
        return templates.TemplateResponse(
            "applicants/assign_parcel.html",
            await _handover_context(
                request, db, user, applicant, parcel_id=parcel_id, handover_date=handover_date,
                co_applicant_ids=co_applicant_ids, new_folder_path=new_folder_path, error=e,
            ),
            status_code=e.http_status,
        )
    await hand_over_parcel(db, plan, acting_user=user)
    return RedirectResponse(url=f"/parcels/{parcel_id}", status_code=303)
