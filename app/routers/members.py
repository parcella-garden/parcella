"""
Members router: list, create, edit, CSV import/export.
"""
import csv
import io
import itertools
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Request, Form, Depends, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_
from sqlalchemy.orm import selectinload

from app.database import get_db, active_member_filter, current_tenant_filter
from app.csv_utils import csv_safe
from app.models import Member, MemberPhone, MemberEmail, MemberParcel, Parcel
from app.permissions import require_permission
from app.i18n import t_for, load_current_language
from app.branding import load_branding
from app.pdf_chrome import load_org_footer_context
from app.meeting_signin_sheet import render_meeting_signin_sheet_pdf
from app.services.members import (
    create_member, update_member, soft_delete_member,
    add_phone, remove_phone, add_email, remove_email,
)

router = APIRouter(prefix="/members", tags=["members"])
from app.templating import templates


async def _get_member_with_details(db: AsyncSession, member_id: str) -> Optional[Member]:
    result = await db.execute(
        select(Member)
        .options(
            selectinload(Member.phone_numbers),
            selectinload(Member.email_addresses),
            selectinload(Member.parcel_assignments).selectinload(MemberParcel.parcel),
        )
        .where(Member.id == member_id, Member.deleted_at.is_(None))
    )
    return result.scalar_one_or_none()


def _filtered_members_query(search: str, include_inactive: bool, pending_only: bool):
    """WHERE/ORDER BY for the member list, shared with its CSV export
    (issue #198) so an export always matches what's currently on screen
    instead of drifting into its own copy of this filtering logic.
    Callers still add their own `.options(...)` eager-loads, since the
    list and the export don't need exactly the same relationships."""
    query = select(Member)

    if pending_only:
        # Issue #167 follow-up: a dedicated view for pending
        # applications -- member_since in the future, OR blank (a
        # member entered into the system with no confirmed start date
        # at all is just as much "not actually a member yet" as one
        # with a future date, per the reporter). Deliberately narrower
        # than active_member_filter(), which still treats a blank
        # member_since as already-started everywhere else (invoices,
        # meetings, dashboard counts, etc.) -- only this review view
        # widens to catch incomplete records too. Sorted oldest-entered
        # first (by created_at, the "entered into the system" timestamp
        # the reporter asked for), since that's the order a board
        # actually works through a queue of applications in -- takes
        # precedence over include_inactive, which is meaningless here.
        #
        # Also requires zero parcel assignments at all (issue #167,
        # second follow-up): a member who already has a parcel is
        # clearly an actual resident, not a pending application -- most
        # likely just missing member_since data entry, not someone
        # still waiting to be let in. Confirmed trade-off, accepted for
        # now: this also hides a member pre-assigned a parcel ahead of a
        # future start date (e.g. approved today, moves in next month)
        # -- a real but rarer case, left as a follow-up.
        no_parcel_assigned = Member.id.not_in(select(MemberParcel.member_id))
        query = query.where(
            Member.deleted_at.is_(None),
            (Member.member_since.is_(None)) | (Member.member_since > date.today()),
            no_parcel_assigned,
        )
        query = query.order_by(Member.created_at.asc())
    else:
        query = query.order_by(Member.last_name, Member.first_name)
        if include_inactive:
            # Issue #169: this must show ONLY inactive members (expired
            # OR not-yet-started), not every non-deleted member
            # regardless of status -- previously this was the plain
            # complement of active_member_filter() done wrong (just
            # deleted_at IS NULL), which meant active members showed up
            # here too. The actual complement of active_member_filter()
            # is an OR (a member is inactive if EITHER half fails), not
            # an AND. Doesn't widen to blank member_since the way
            # pending_only does above -- that's still "active" per
            # active_member_filter() itself, unchanged.
            query = query.where(
                Member.deleted_at.is_(None),
                or_(
                    and_(Member.member_since.is_not(None), Member.member_since > date.today()),
                    and_(Member.member_until.is_not(None), Member.member_until < date.today()),
                ),
            )
        else:
            query = query.where(active_member_filter())

    if search:
        # Searches by first/last name OR parcel number. For the parcel
        # search: by default only current assignments (who lives there
        # NOW); with "include_inactive" also already-ended assignments (who
        # used to live there) -- the same toggle logic as for active/
        # inactive members, just applied to the parcel's tenant history.
        # "City" was deliberately removed, since searching by it wasn't
        # used in practice.
        parcel_condition = Parcel.plot_number.ilike(f"%{search}%")
        if not include_inactive:
            parcel_condition = and_(
                parcel_condition, current_tenant_filter()
            )
        parcel_matches = (
            select(MemberParcel.member_id)
            .join(Parcel, MemberParcel.parcel_id == Parcel.id)
            .where(parcel_condition)
        )
        query = query.where(
            or_(
                Member.first_name.ilike(f"%{search}%"),
                Member.last_name.ilike(f"%{search}%"),
                Member.id.in_(parcel_matches),
            )
        )

    return query


@router.get("/", response_class=HTMLResponse)
async def members_list(
    request: Request,
    search: str = "",
    include_inactive: bool = False,
    pending_only: bool = False,
    db: AsyncSession = Depends(get_db),
):
    user = await require_permission(request, db, "members_parcels", "read")

    query = _filtered_members_query(search, include_inactive, pending_only).options(
        selectinload(Member.email_addresses),
        selectinload(Member.parcel_assignments).selectinload(MemberParcel.parcel),
    )

    result = await db.execute(query)
    members = result.scalars().all()

    return templates.TemplateResponse(
        "members/list.html",
        {
            "request": request,
            "user": user,
            "members": members,
            "search": search,
            "include_inactive": include_inactive,
            "pending_only": pending_only,
        },
    )


# ---------------------------------------------------------------------------
# General-meeting sign-in sheet (PDF): current members, grouped by
# parcel, one signature line each. Not gated by a module flag -- same
# permission level as the member list itself (members_parcels read),
# since it's just another view onto the same data, not a separate
# feature area with its own security surface.
# ---------------------------------------------------------------------------

@router.get("/signin-sheet", response_class=HTMLResponse)
async def signin_sheet_form(request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_permission(request, db, "members_parcels", "read")
    default_headline = f"General meeting on {date.today().isoformat()}"
    return templates.TemplateResponse("members/signin_sheet.html", {
        "request": request, "user": user, "default_headline": default_headline,
    })


@router.post("/signin-sheet")
async def signin_sheet_generate(request: Request, db: AsyncSession = Depends(get_db)):
    await require_permission(request, db, "members_parcels", "read")
    form = await request.form()
    headline = (form.get("headline") or "").strip()
    if not headline:
        headline = f"General meeting on {date.today().isoformat()}"

    # Current residents only (assigned_until IS NULL or in the future --
    # same "who lives here right now" definition used elsewhere, e.g. the
    # announcement email channel), same active-membership filter as the
    # member list itself. Already sorted by parcel then name, so grouping
    # consecutive rows below doesn't need to re-sort.
    result = await db.execute(
        select(Parcel.plot_number, Member.first_name, Member.last_name)
        .join(MemberParcel, MemberParcel.parcel_id == Parcel.id)
        .join(Member, Member.id == MemberParcel.member_id)
        .where(current_tenant_filter(), active_member_filter())
        .order_by(Parcel.plot_number, Member.last_name, Member.first_name)
    )
    rows = result.all()

    parcel_members = [
        (plot_number, [f"{first_name} {last_name}" for _, first_name, last_name in group])
        for plot_number, group in itertools.groupby(rows, key=lambda row: row[0])
    ]

    branding = await load_branding(db)
    logo_path = Path("app" + branding["logo_url"]) if branding["logo_url"] else None
    language = await load_current_language(db)
    footer_context = await load_org_footer_context(db, branding["club_name"])

    pdf_bytes = render_meeting_signin_sheet_pdf(headline, footer_context, logo_path, parcel_members, language)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="signin-sheet.pdf"'},
    )


@router.get("/new", response_class=HTMLResponse)
async def member_new_page(request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_permission(request, db, "members_parcels", "write")
    return templates.TemplateResponse(
        "members/form.html",
        {"request": request, "user": user, "member": None},
    )


@router.post("/new")
async def member_create(
    request: Request,
    first_name: str = Form(...),
    last_name: str = Form(...),
    street: str = Form(""),
    postal_code: str = Form(""),
    city: str = Form(""),
    date_of_birth: str = Form(""),
    iban: str = Form(""),
    member_since: str = Form(""),
    member_until: str = Form(""),
    email_notifications: bool = Form(False),
    notes: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    await require_permission(request, db, "members_parcels", "write")

    def parse_date(s: str) -> Optional[date]:
        if s:
            try:
                return date.fromisoformat(s)
            except ValueError:
                pass
        return None

    member = await create_member(
        db,
        first_name=first_name, last_name=last_name, street=street,
        postal_code=postal_code, city=city, date_of_birth=parse_date(date_of_birth),
        iban=iban, member_since=parse_date(member_since), member_until=parse_date(member_until),
        email_notifications=email_notifications, notes=notes,
    )
    await db.commit()

    return RedirectResponse(f"/members/{member.id}", status_code=302)


@router.get("/{member_id}", response_class=HTMLResponse)
async def member_detail(
    member_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user = await require_permission(request, db, "members_parcels", "read")
    member = await _get_member_with_details(db, member_id)

    if not member:
        raise HTTPException(status_code=404, detail=t_for(request, "members.errors.member_not_found"))

    # All active parcels, for assignment
    parcels_result = await db.execute(
        select(Parcel).order_by(Parcel.plot_number)
    )
    all_parcels = parcels_result.scalars().all()

    return templates.TemplateResponse(
        "members/detail.html",
        {
            "request": request,
            "user": user,
            "member": member,
            "all_parcels": all_parcels,
        },
    )


@router.get("/{member_id}/edit", response_class=HTMLResponse)
async def member_edit_page(
    member_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user = await require_permission(request, db, "members_parcels", "write")
    member = await _get_member_with_details(db, member_id)

    if not member:
        raise HTTPException(status_code=404, detail=t_for(request, "members.errors.member_not_found"))

    return templates.TemplateResponse(
        "members/form.html",
        {"request": request, "user": user, "member": member},
    )


@router.post("/{member_id}/edit")
async def member_update(
    member_id: str,
    request: Request,
    first_name: str = Form(...),
    last_name: str = Form(...),
    street: str = Form(""),
    postal_code: str = Form(""),
    city: str = Form(""),
    date_of_birth: str = Form(""),
    iban: str = Form(""),
    member_since: str = Form(""),
    member_until: str = Form(""),
    email_notifications: bool = Form(False),
    notes: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    await require_permission(request, db, "members_parcels", "write")
    member = await _get_member_with_details(db, member_id)

    if not member:
        raise HTTPException(status_code=404)

    def parse_date(s: str) -> Optional[date]:
        if s:
            try:
                return date.fromisoformat(s)
            except ValueError:
                pass
        return None

    await update_member(
        db, member,
        first_name=first_name, last_name=last_name, street=street,
        postal_code=postal_code, city=city, date_of_birth=parse_date(date_of_birth),
        iban=iban, member_since=parse_date(member_since), member_until=parse_date(member_until),
        email_notifications=email_notifications, notes=notes,
    )
    await db.commit()
    return RedirectResponse(f"/members/{member_id}", status_code=302)


@router.post("/{member_id}/delete")
async def member_delete(
    member_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Soft-delete: sets deleted_at, removes the member from lists/search.
    Already-recorded parcel assignments, tickets, work sessions etc.
    remain unchanged -- no FK cascade, since there's no real DELETE.
    Requires "delete" on members_parcels (ADMIN/BOARD always qualify,
    see app/permissions.py)."""
    await require_permission(request, db, "members_parcels", "delete")
    member = await _get_member_with_details(db, member_id)

    if not member:
        raise HTTPException(status_code=404, detail=t_for(request, "members.errors.member_not_found"))

    await soft_delete_member(db, member)
    await db.commit()

    message = t_for(request, "members.detail.deleted_message", name=member.full_name)
    import urllib.parse
    return RedirectResponse(
        f"/members/?message={urllib.parse.quote(message)}", status_code=302
    )


# ---------------------------------------------------------------------------
# Phone / Email management
# ---------------------------------------------------------------------------

@router.post("/{member_id}/phone/add")
async def phone_add(
    member_id: str,
    request: Request,
    number: str = Form(...),
    label: str = Form(""),
    is_primary: bool = Form(False),
    db: AsyncSession = Depends(get_db),
):
    await require_permission(request, db, "members_parcels", "write")
    await add_phone(db, member_id, number=number, label=label, is_primary=is_primary)
    await db.commit()
    return RedirectResponse(f"/members/{member_id}", status_code=302)


@router.post("/{member_id}/phone/{phone_id}/delete")
async def phone_delete(
    member_id: str,
    phone_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    await require_permission(request, db, "members_parcels", "delete")
    if await remove_phone(db, member_id, phone_id):
        await db.commit()
    return RedirectResponse(f"/members/{member_id}", status_code=302)


@router.post("/{member_id}/email/add")
async def email_add(
    member_id: str,
    request: Request,
    address: str = Form(...),
    label: str = Form(""),
    is_primary: bool = Form(False),
    db: AsyncSession = Depends(get_db),
):
    await require_permission(request, db, "members_parcels", "write")
    await add_email(db, member_id, address=address, label=label, is_primary=is_primary)
    await db.commit()
    return RedirectResponse(f"/members/{member_id}", status_code=302)


@router.post("/{member_id}/email/{email_id}/delete")
async def email_delete(
    member_id: str,
    email_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    await require_permission(request, db, "members_parcels", "delete")
    if await remove_email(db, member_id, email_id):
        await db.commit()
    return RedirectResponse(f"/members/{member_id}", status_code=302)


# ---------------------------------------------------------------------------
# CSV export
# ---------------------------------------------------------------------------

@router.get("/export/csv")
async def members_export_csv(
    request: Request,
    search: str = "",
    include_inactive: bool = False,
    pending_only: bool = False,
    db: AsyncSession = Depends(get_db),
):
    await require_permission(request, db, "members_parcels", "read")

    # Issue #198: exports whatever the list page is currently showing,
    # not always every active member -- same filters, same query, via
    # _filtered_members_query() so the two can't drift apart.
    query = _filtered_members_query(search, include_inactive, pending_only).options(
        selectinload(Member.email_addresses),
        selectinload(Member.phone_numbers),
        selectinload(Member.parcel_assignments).selectinload(MemberParcel.parcel),
    )
    result = await db.execute(query)
    members = result.scalars().all()

    output = io.StringIO()
    writer = csv.writer(output, delimiter=";")
    writer.writerow([
        "Vorname", "Nachname", "Strasse", "PLZ", "Ort",
        "Geburtsdatum", "IBAN", "Member seit", "Member bis",
        "E-Mail-Benachrichtigungen", "E-Mail-Adressen", "Telefonnummern",
        "Parzellen", "Notizen"
    ])

    for m in members:
        emails = "; ".join(e.address for e in m.email_addresses)
        phones = "; ".join(t.number for t in m.phone_numbers)
        parcels = "; ".join(z.parcel.plot_number for z in m.parcel_assignments)
        writer.writerow([
            csv_safe(m.first_name), csv_safe(m.last_name), csv_safe(m.street or ""),
            csv_safe(m.postal_code or ""), csv_safe(m.city or ""),
            m.date_of_birth.isoformat() if m.date_of_birth else "",
            csv_safe(m.iban or ""),
            m.member_since.isoformat() if m.member_since else "",
            m.member_until.isoformat() if m.member_until else "",
            "Ja" if m.email_notifications else "Nein",
            csv_safe(emails), csv_safe(phones), parcels,
            csv_safe(m.notes or ""),
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=members.csv"},
    )


# ---------------------------------------------------------------------------
# CSV import
# ---------------------------------------------------------------------------

@router.post("/import/csv")
async def members_import_csv(
    request: Request,
    datei: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    await require_permission(request, db, "members_parcels", "write")

    inhalt = await datei.read()
    try:
        text = inhalt.decode("utf-8-sig")  # BOM-safe (Excel)
    except UnicodeDecodeError:
        text = inhalt.decode("latin-1")    # Fallback for older Windows exports

    # Auto-detect the delimiter (semicolon or comma) -- many
    # spreadsheet programs save CSVs differently depending on the
    # language setting, even if the file was originally exported with
    # a semicolon.
    try:
        delimiter = csv.Sniffer().sniff(text[:2048], delimiters=";,").delimiter
    except csv.Error:
        delimiter = ";"

    reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)
    # Strip leading/trailing whitespace from column names, in case the
    # spreadsheet program inserted some on save.
    if reader.fieldnames:
        reader.fieldnames = [f.strip() if f else f for f in reader.fieldnames]

    created = 0
    updated = 0
    errors = []

    def parse_date(s: str) -> Optional[date]:
        s = s.strip()
        for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d.%m.%y"):
            try:
                return date.fromisoformat(s) if fmt == "%Y-%m-%d" else datetime.strptime(s, fmt).date()
            except ValueError:
                continue
        return None

    for row_number, row in enumerate(reader, start=2):
        first_name = (row.get("Vorname") or "").strip()
        last_name = (row.get("Nachname") or "").strip()

        if not first_name or not last_name:
            errors.append(f"Zeile {row_number}: Vor- oder Nachname fehlt – übersprungen.")
            continue

        # Duplicate detection: same first + last name + date of birth
        date_of_birth = parse_date(row.get("Geburtsdatum") or "")
        existing_query = select(Member).where(
            Member.first_name == first_name,
            Member.last_name == last_name,
            Member.deleted_at.is_(None),
        )
        if date_of_birth:
            existing_query = existing_query.where(Member.date_of_birth == date_of_birth)

        existing_result = await db.execute(existing_query)
        existing = existing_result.scalars().first()

        email_notifications_str = (row.get("E-Mail-Benachrichtigungen") or "Ja").strip().lower()
        email_notifications = email_notifications_str not in ("nein", "no", "false", "0")

        fields = dict(
            first_name=first_name,
            last_name=last_name,
            street=(row.get("Strasse") or "").strip() or None,
            postal_code=(row.get("PLZ") or "").strip() or None,
            city=(row.get("Ort") or "").strip() or None,
            date_of_birth=date_of_birth,
            iban=(row.get("IBAN") or "").strip() or None,
            member_since=parse_date(row.get("Member seit") or ""),
            member_until=parse_date(row.get("Member bis") or ""),
            email_notifications=email_notifications,
            notes=(row.get("Notizen") or "").strip() or None,
        )

        if existing:
            # Update the existing member
            for k, v in fields.items():
                setattr(existing, k, v)
            member = existing
            updated += 1
        else:
            member = Member(**fields)
            db.add(member)
            await db.flush()  # generate ID for sub-entries
            created += 1

        # Email addresses (semicolon-separated in one cell)
        emails_str = (row.get("E-Mail-Adressen") or "").strip()
        if emails_str and not existing:
            for i, email_address in enumerate(emails_str.split(";")):
                email_address = email_address.strip().lower()
                if email_address:
                    db.add(MemberEmail(
                        member_id=member.id,
                        address=email_address,
                        is_primary=(i == 0),
                    ))

        # Phone numbers (semicolon-separated in one cell)
        phones_str = (row.get("Telefonnummern") or "").strip()
        if phones_str and not existing:
            for i, phone_number in enumerate(phones_str.split(";")):
                phone_number = phone_number.strip()
                if phone_number:
                    db.add(MemberPhone(
                        member_id=member.id,
                        number=phone_number,
                        is_primary=(i == 0),
                    ))

    await db.commit()

    message = t_for(request, "members.list.csv_import_summary", created=created, updated=updated)
    if errors:
        message += t_for(request, "members.list.csv_import_errors_suffix", count=len(errors))
        # Show the first few error details so the cause is visible right away
        message += " – " + " | ".join(errors[:3])
        if len(errors) > 3:
            message += t_for(request, "members.list.csv_import_more_errors", count=len(errors) - 3)

    import urllib.parse
    return RedirectResponse(
        f"/members/?message={urllib.parse.quote(message)}",
        status_code=302,
    )
