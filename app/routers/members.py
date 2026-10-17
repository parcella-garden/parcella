"""
Members router: list, create, edit, CSV import/export.
"""
import base64
import csv
import io
import itertools
import urllib.parse
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Request, Form, Depends, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db, active_member_filter, current_tenant_filter
from app.csv_utils import (
    csv_safe,
    decode_csv_upload,
    sniff_csv_delimiter,
    guess_column_mapping,
    parse_column_mapping,
    parse_mapped_csv_rows,
)
from app.member_filters import MemberListFilter
from app.models import Member, MemberPhone, MemberEmail, MemberParcel, MemberTag, Parcel
from app.services.errors import ServiceError
from app.permissions import require_permission
from app.i18n import t_for, load_current_language
from app.branding import load_branding
from app.pdf_chrome import load_org_footer_context
from app.meeting_signin_sheet import render_meeting_signin_sheet_pdf
from app.services.members import (
    create_member, update_member, soft_delete_member,
    add_phone, remove_phone, add_email, remove_email,
    list_tags, tag_member, untag_member, rename_tag, delete_tag, count_tag_members,
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
            selectinload(Member.tags),
        )
        .where(Member.id == member_id, Member.deleted_at.is_(None))
    )
    return result.scalar_one_or_none()


@router.get("/", response_class=HTMLResponse)
async def members_list(
    request: Request,
    filters: MemberListFilter = Depends(MemberListFilter.from_query),
    db: AsyncSession = Depends(get_db),
):
    user = await require_permission(request, db, "members_parcels", "read")

    query = filters.apply().options(
        selectinload(Member.email_addresses),
        selectinload(Member.parcel_assignments).selectinload(MemberParcel.parcel),
        selectinload(Member.tags),
    )

    result = await db.execute(query)
    members = result.scalars().all()
    all_tags = await list_tags(db)

    return templates.TemplateResponse(
        "members/list.html",
        {
            "request": request,
            "user": user,
            "members": members,
            "search": filters.search,
            "include_inactive": filters.include_inactive,
            "pending_only": filters.pending_only,
            "active_only": filters.active_only,
            "email_info_only": filters.email_info_only,
            "tag": filters.tag,
            "all_tags": all_tags,
            "list_query_string": filters.query_string(),
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
    email: str = Form(""),
    phone: str = Form(""),
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
    if email.strip():
        await add_email(db, member.id, address=email.strip(), is_primary=True)
    if phone.strip():
        await add_phone(db, member.id, number=phone.strip(), is_primary=True)
    await db.commit()

    return RedirectResponse(f"/members/{member.id}", status_code=302)


# ---------------------------------------------------------------------------
# Tags (issue #241, ADR 0093): free-form labels on members, filterable on
# the list. The management page is registered before /{member_id} so
# "/members/tags" isn't taken for a member id.
# ---------------------------------------------------------------------------

def _redirect_with_error(request: Request, url: str, error: ServiceError) -> RedirectResponse:
    message = t_for(request, error.key, **error.params)
    return RedirectResponse(f"{url}?error={urllib.parse.quote(message)}", status_code=303)


async def _get_tag_or_404(db: AsyncSession, tag_id: str) -> MemberTag:
    tag = await db.get(MemberTag, tag_id)
    if tag is None:
        raise HTTPException(status_code=404)
    return tag


@router.get("/tags", response_class=HTMLResponse)
async def tags_page(request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_permission(request, db, "members_parcels", "read")
    return templates.TemplateResponse("members/tags.html", {
        "request": request, "user": user,
        "tags": await list_tags(db), "member_counts": await count_tag_members(db),
    })


@router.post("/tags/{tag_id}/rename")
async def tag_rename(tag_id: str, request: Request, name: str = Form(""), db: AsyncSession = Depends(get_db)):
    await require_permission(request, db, "members_parcels", "write")
    tag = await _get_tag_or_404(db, tag_id)
    try:
        await rename_tag(db, tag, name)
    except ServiceError as e:
        await db.rollback()
        return _redirect_with_error(request, "/members/tags", e)
    await db.commit()
    return RedirectResponse("/members/tags", status_code=303)


@router.post("/tags/{tag_id}/delete")
async def tag_delete(tag_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    await require_permission(request, db, "members_parcels", "delete")
    await delete_tag(db, await _get_tag_or_404(db, tag_id))
    await db.commit()
    return RedirectResponse("/members/tags", status_code=303)


@router.post("/{member_id}/tags/add")
async def member_tag_add(
    member_id: str, request: Request,
    tag_id: str = Form(""), name: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    """Either pick an existing tag (tag_id) or type a name -- a new
    name creates the tag. A typed name wins over the dropdown."""
    await require_permission(request, db, "members_parcels", "write")
    if not await _get_member_with_details(db, member_id):
        raise HTTPException(status_code=404, detail=t_for(request, "members.errors.member_not_found"))
    try:
        if name.strip():
            await tag_member(db, member_id, name=name)
        else:
            await tag_member(db, member_id, tag_id=tag_id or None, name=name)
    except ServiceError as e:
        await db.rollback()
        return _redirect_with_error(request, f"/members/{member_id}", e)
    await db.commit()
    return RedirectResponse(f"/members/{member_id}", status_code=303)


@router.post("/{member_id}/tags/{tag_id}/remove")
async def member_tag_remove(member_id: str, tag_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    await require_permission(request, db, "members_parcels", "write")
    await untag_member(db, member_id, tag_id)
    await db.commit()
    return RedirectResponse(f"/members/{member_id}", status_code=303)


@router.get("/{member_id}", response_class=HTMLResponse)
async def member_detail(
    member_id: str,
    request: Request,
    filters: MemberListFilter = Depends(MemberListFilter.from_query),
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

    # Previous/Next buttons (issue #202): walk the same filtered, ordered
    # ID list the list page itself would show, so paging through e.g.
    # /members/?pending_only=true stays within that same set instead of
    # falling back to every member. If the current member isn't in that
    # set at all (filter changed since the list was loaded, or the
    # member was edited out of it), no prev/next is shown rather than
    # guessing.
    ordered_ids = (
        await db.scalars(
            filters.apply().with_only_columns(Member.id)
        )
    ).all()
    prev_member_id = None
    next_member_id = None
    if member_id in ordered_ids:
        idx = ordered_ids.index(member_id)
        if idx > 0:
            prev_member_id = ordered_ids[idx - 1]
        if idx < len(ordered_ids) - 1:
            next_member_id = ordered_ids[idx + 1]
    list_query_string = filters.query_string()
    all_tags = await list_tags(db)

    return templates.TemplateResponse(
        "members/detail.html",
        {
            "request": request,
            "user": user,
            "member": member,
            "all_parcels": all_parcels,
            "all_tags": all_tags,
            "prev_member_id": prev_member_id,
            "next_member_id": next_member_id,
            "nav_query_suffix": f"?{list_query_string}" if list_query_string else "",
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
    filters: MemberListFilter = Depends(MemberListFilter.from_query),
    db: AsyncSession = Depends(get_db),
):
    await require_permission(request, db, "members_parcels", "read")

    # Issue #198: exports whatever the list page is currently showing,
    # not always every active member -- same filters, same query, via
    # MemberListFilter.apply() so the two can't drift apart.
    query = filters.apply().options(
        selectinload(Member.email_addresses),
        selectinload(Member.phone_numbers),
        selectinload(Member.parcel_assignments).selectinload(MemberParcel.parcel),
        selectinload(Member.tags),
    )
    result = await db.execute(query)
    members = result.scalars().all()

    output = io.StringIO()
    writer = csv.writer(output, delimiter=";")
    writer.writerow([
        "Vorname", "Nachname", "Strasse", "PLZ", "Ort",
        "Geburtsdatum", "IBAN", "Member seit", "Member bis",
        "E-Mail-Benachrichtigungen", "E-Mail-Adressen", "Telefonnummern",
        "Parzellen", "Notizen", "Tags"
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
            csv_safe("; ".join(tag.name for tag in m.tags)),
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

CSV_IMPORT_PREVIEW_ROWS = 5
MEMBERS_IMPORT_TARGET_FIELDS = [
    "first_name", "last_name", "street", "postal_code", "city",
    "date_of_birth", "iban", "member_since", "member_until",
    "email_notifications", "email_addresses", "phone_numbers", "notes",
]
MEMBERS_IMPORT_FIELD_ALIASES = {
    "first_name": {"vorname", "first name", "firstname"},
    "last_name": {"nachname", "last name", "lastname", "surname"},
    "street": {"strasse", "straße", "street", "address"},
    "postal_code": {"plz", "postal code", "zip", "zip code", "postcode"},
    "city": {"ort", "city", "town"},
    "date_of_birth": {"geburtsdatum", "date of birth", "birthdate", "dob"},
    "iban": {"iban"},
    "member_since": {"member seit", "member since", "mitglied seit"},
    "member_until": {"member bis", "member until", "mitglied bis"},
    "email_notifications": {"e-mail-benachrichtigungen", "email notifications", "email-benachrichtigungen"},
    "email_addresses": {"e-mail-adressen", "email addresses", "emails", "e-mail"},
    "phone_numbers": {"telefonnummern", "phone numbers", "phones", "telefon"},
    "notes": {"notizen", "notes", "note"},
}


def _parse_member_date(s: str) -> Optional[date]:
    s = s.strip()
    for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d.%m.%y"):
        try:
            return date.fromisoformat(s) if fmt == "%Y-%m-%d" else datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


@router.post("/import/preview", response_class=HTMLResponse)
async def members_import_preview(
    request: Request,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """Step 1 of the column-mapping wizard (ADR 0062's pattern,
    generalized here -- see docs/ADR/0083): detects the header row and
    lets the user map each column to a Parcella field before anything
    is written. The raw CSV round-trips to step 2 as a hidden base64
    field, not server-side session state."""
    await require_permission(request, db, "members_parcels", "write")

    content = await file.read()
    text = decode_csv_upload(content)
    delimiter = sniff_csv_delimiter(text)

    reader = csv.reader(io.StringIO(text), delimiter=delimiter)
    rows = list(reader)
    if not rows:
        message = t_for(request, "members.list.csv_empty_error")
        import urllib.parse
        return RedirectResponse(f"/members/?error={urllib.parse.quote(message)}", status_code=303)
    headers = [h.strip() for h in rows[0]]
    preview_rows = rows[1:1 + CSV_IMPORT_PREVIEW_ROWS]
    default_mapping = guess_column_mapping(headers, MEMBERS_IMPORT_FIELD_ALIASES)

    return templates.TemplateResponse("members/import_preview.html", {
        "request": request,
        "headers": headers, "preview_rows": preview_rows,
        "default_mapping": default_mapping, "target_fields": MEMBERS_IMPORT_TARGET_FIELDS,
        "csv_content_b64": base64.b64encode(content).decode("ascii"), "delimiter": delimiter,
    })


@router.post("/import/finalize")
async def members_import_finalize(
    request: Request,
    csv_content_b64: str = Form(...), delimiter: str = Form(";"),
    db: AsyncSession = Depends(get_db),
):
    """Step 2: applies the confirmed column mapping and runs the same
    row logic the old fixed-header importer used -- name+DOB matching,
    update-or-create, email/phone seeding only on create -- are
    unchanged, just fed from the mapped dict instead of a literal
    DictReader header lookup."""
    await require_permission(request, db, "members_parcels", "write")

    form = await request.form()
    column_mapping = parse_column_mapping(form, MEMBERS_IMPORT_TARGET_FIELDS)
    if "first_name" not in column_mapping.values() or "last_name" not in column_mapping.values():
        message = t_for(request, "members.list.csv_mapping_required_error")
        import urllib.parse
        return RedirectResponse(f"/members/?error={urllib.parse.quote(message)}", status_code=303)
    rows = parse_mapped_csv_rows(csv_content_b64, delimiter, column_mapping)

    created = 0
    updated = 0
    errors = []

    for row_number, values in enumerate(rows, start=2):
        first_name = (values.get("first_name") or "").strip()
        last_name = (values.get("last_name") or "").strip()

        if not first_name or not last_name:
            errors.append(f"Zeile {row_number}: Vor- oder Nachname fehlt – übersprungen.")
            continue

        # Duplicate detection: same first + last name + date of birth
        date_of_birth = _parse_member_date(values.get("date_of_birth") or "")
        existing_query = select(Member).where(
            Member.first_name == first_name,
            Member.last_name == last_name,
            Member.deleted_at.is_(None),
        )
        if date_of_birth:
            existing_query = existing_query.where(Member.date_of_birth == date_of_birth)

        existing_result = await db.execute(existing_query)
        existing = existing_result.scalars().first()

        email_notifications_str = (values.get("email_notifications") or "Ja").strip().lower()
        email_notifications = email_notifications_str not in ("nein", "no", "false", "0")

        fields = dict(
            first_name=first_name,
            last_name=last_name,
            street=(values.get("street") or "").strip() or None,
            postal_code=(values.get("postal_code") or "").strip() or None,
            city=(values.get("city") or "").strip() or None,
            date_of_birth=date_of_birth,
            iban=(values.get("iban") or "").strip() or None,
            member_since=_parse_member_date(values.get("member_since") or ""),
            member_until=_parse_member_date(values.get("member_until") or ""),
            email_notifications=email_notifications,
            notes=(values.get("notes") or "").strip() or None,
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
        emails_str = (values.get("email_addresses") or "").strip()
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
        phones_str = (values.get("phone_numbers") or "").strip()
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
