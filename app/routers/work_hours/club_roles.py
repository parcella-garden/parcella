"""Club roles (work-hours exemptions) and their members."""
from fastapi import APIRouter
from datetime import date
from typing import Optional
from fastapi import Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.database import active_member_filter, get_db
from app.models import ClubRole, ExemptionReason, Member, MemberClubRole
from app.permissions import require_permission
from app.i18n import t_for
from app.services.work_hours import assign_member_to_club_role, create_club_role, update_club_role
from app.templating import templates

router = APIRouter()


# ---------------------------------------------------------------------------
# Club Roles
# ---------------------------------------------------------------------------

@router.get("/club-roles", response_class=HTMLResponse)
async def club_roles_page(
    request: Request,
    year: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
):
    user = await require_permission(request, db, "work_hours", "read")

    if not year:
        year = date.today().year

    roles_result = await db.execute(
        select(ClubRole).order_by(ClubRole.name)
    )
    roles = roles_result.scalars().all()

    assignments_result = await db.execute(
        select(MemberClubRole)
        .options(
            selectinload(MemberClubRole.member),
            selectinload(MemberClubRole.club_role),
        )
        .where(MemberClubRole.year == year)
        .order_by(MemberClubRole.club_role_id)
    )
    assignments = assignments_result.scalars().all()

    members_result = await db.execute(
        select(Member)
        .where(active_member_filter())
        .order_by(Member.last_name, Member.first_name)
    )
    all_members = members_result.scalars().all()

    return templates.TemplateResponse(
        request, "work_hours/club-roles.html",
        {
            "request": request,
            "user": user,
            "roles": roles,
            "assignments": assignments,
            "all_members": all_members,
            "year": year,
            "ExemptionReason": ExemptionReason,
            "current_year": date.today().year,
        },
    )


@router.post("/club-roles/assign-member")
async def member_club_role_assign(
    request: Request,
    member_id: str = Form(...),
    club_role_id: str = Form(...),
    year: int = Form(...),
    valid_from: str = Form(""),
    valid_until: str = Form(""),
    note: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    await require_permission(request, db, "work_hours", "write")

    assignment = await assign_member_to_club_role(
        db, member_id=member_id, club_role_id=club_role_id, year=year,
        valid_from=(date.fromisoformat(valid_from) if valid_from.strip() else None),
        valid_until=(date.fromisoformat(valid_until) if valid_until.strip() else None),
        note=note,
    )
    if assignment is not None:
        await db.commit()

    return RedirectResponse(f"/work-hours/club-roles?year={year}", status_code=302)


@router.get("/club-roles/assignment/{assignment_id}/edit", response_class=HTMLResponse)
async def member_club_role_edit_page(
    assignment_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user = await require_permission(request, db, "work_hours", "write")

    result = await db.execute(
        select(MemberClubRole)
        .options(
            selectinload(MemberClubRole.member),
            selectinload(MemberClubRole.club_role),
        )
        .where(MemberClubRole.id == assignment_id)
    )
    assignment = result.scalar_one_or_none()
    if not assignment:
        raise HTTPException(status_code=404, detail=t_for(request, "work_hours.errors.assignment_not_found"))

    members_result = await db.execute(
        select(Member)
        .where(active_member_filter())
        .order_by(Member.last_name, Member.first_name)
    )
    all_members = members_result.scalars().all()

    roles_result = await db.execute(select(ClubRole).order_by(ClubRole.name))
    all_roles = roles_result.scalars().all()

    return templates.TemplateResponse(
        request, "work_hours/member_club_role_form.html",
        {
            "request": request,
            "user": user,
            "assignment": assignment,
            "all_members": all_members,
            "all_roles": all_roles,
        },
    )


@router.post("/club-roles/assignment/{assignment_id}/edit")
async def member_club_role_update(
    assignment_id: str,
    request: Request,
    member_id: str = Form(...),
    club_role_id: str = Form(...),
    year: int = Form(...),
    valid_from: str = Form(""),
    valid_until: str = Form(""),
    note: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    await require_permission(request, db, "work_hours", "write")

    result = await db.execute(
        select(MemberClubRole).where(MemberClubRole.id == assignment_id)
    )
    assignment = result.scalar_one_or_none()
    if not assignment:
        raise HTTPException(status_code=404, detail=t_for(request, "work_hours.errors.assignment_not_found"))

    assignment.member_id = member_id
    assignment.club_role_id = club_role_id
    assignment.year = year
    assignment.valid_from = date.fromisoformat(valid_from) if valid_from.strip() else None
    assignment.valid_until = date.fromisoformat(valid_until) if valid_until.strip() else None
    assignment.note = note.strip() or None

    await db.commit()
    return RedirectResponse(f"/work-hours/club-roles?year={year}", status_code=302)


@router.post("/club-roles/assignment/{assignment_id}/remove")
async def member_club_role_remove(
    assignment_id: str,
    request: Request,
    year: int = Form(0),
    db: AsyncSession = Depends(get_db),
):
    await require_permission(request, db, "work_hours", "delete")

    result = await db.execute(
        select(MemberClubRole).where(MemberClubRole.id == assignment_id)
    )
    assignment = result.scalar_one_or_none()
    return_year = assignment.year if assignment else date.today().year
    if assignment:
        await db.delete(assignment)
        await db.commit()

    return RedirectResponse(f"/work-hours/club-roles?year={return_year}", status_code=302)


@router.post("/club-roles/new")
async def club_role_create(
    request: Request,
    name: str = Form(...),
    description: str = Form(""),
    hours_exempt: bool = Form(False),
    exemption_reason: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    await require_permission(request, db, "work_hours", "write")

    await create_club_role(
        db, name=name, description=description, hours_exempt=hours_exempt, exemption_reason=(exemption_reason or None),
    )
    await db.commit()
    return RedirectResponse("/work-hours/club-roles", status_code=302)


@router.get("/club-roles/{role_id}/edit", response_class=HTMLResponse)
async def club_role_edit_page(
    role_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user = await require_permission(request, db, "work_hours", "write")

    result = await db.execute(select(ClubRole).where(ClubRole.id == role_id))
    role = result.scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=404, detail=t_for(request, "work_hours.errors.club_role_not_found"))

    return templates.TemplateResponse(
        request, "work_hours/club_role_form.html",
        {
            "request": request,
            "user": user,
            "role": role,
        },
    )


@router.post("/club-roles/{role_id}/edit")
async def club_role_update(
    role_id: str,
    request: Request,
    name: str = Form(...),
    description: str = Form(""),
    hours_exempt: bool = Form(False),
    exemption_reason: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    await require_permission(request, db, "work_hours", "write")

    result = await db.execute(select(ClubRole).where(ClubRole.id == role_id))
    role = result.scalar_one_or_none()
    if role:
        await update_club_role(
            db, role, name=name, description=description, hours_exempt=hours_exempt,
            exemption_reason=(exemption_reason or None),
        )
        await db.commit()

    return RedirectResponse("/work-hours/club-roles", status_code=302)


@router.post("/club-roles/{role_id}/delete")
async def club_role_delete(
    role_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    await require_permission(request, db, "work_hours", "delete")
    result = await db.execute(select(ClubRole).where(ClubRole.id == role_id))
    role = result.scalar_one_or_none()
    if role:
        await db.delete(role)
        await db.commit()
    return RedirectResponse("/work-hours/club-roles", status_code=302)
