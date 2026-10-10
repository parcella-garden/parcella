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
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import (
    APPLICANT_OPEN_STATUSES, Applicant, ApplicantSource, ApplicantStatus, ChangeHistory,
)
from app.permissions import require_permission
from app.module_flags import require_module
from app.templating import templates
from app.services.errors import ServiceError
from app.services.applicants import create_applicant, delete_applicant, update_applicant

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
    return {field: form.get(field) for field in ("email", "first_name", "last_name", "phone", "message", "board_note")}


# ---------------------------------------------------------------------------
# List
# ---------------------------------------------------------------------------

@router.get("/", response_class=HTMLResponse)
async def applicants_list(request: Request, filter: str = "open", db: AsyncSession = Depends(get_db)):
    user = await require_permission(request, db, "applicants", "read")
    if filter not in _FILTERS:
        filter = "open"

    query = select(Applicant).order_by(Applicant.applied_at.desc())
    statuses = _FILTERS[filter]
    if statuses is not None:
        query = query.where(Applicant.status.in_(statuses))
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
        "filter": filter, "application_counts": counts,
    })


# ---------------------------------------------------------------------------
# Create by hand (registered before /{applicant_id})
# ---------------------------------------------------------------------------

@router.get("/new", response_class=HTMLResponse)
async def applicant_new_page(request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_permission(request, db, "applicants", "write")
    return templates.TemplateResponse("applicants/form.html", {
        "request": request, "user": user, "values": {},
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
            "request": request, "user": user, "values": values, "error": e.key,
        }, status_code=e.http_status)
    return RedirectResponse(url=f"/applicants/{applicant.id}", status_code=303)


# ---------------------------------------------------------------------------
# Detail / edit / delete
# ---------------------------------------------------------------------------

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
        "statuses": list(ApplicantStatus), "error": error,
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
