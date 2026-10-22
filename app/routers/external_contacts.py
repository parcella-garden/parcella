"""
External contacts router (web UI): suppliers, craftsmen, authorities --
a company plus a contact person (docs/module-external-contacts.md,
ADR 0096). Same shape as the members router, minus everything that
only makes sense for members (parcels, membership dates, email_info).

Business logic lives in app/services/external_contacts.py (ADR 0070).
"""
import base64
import csv
import io
import urllib.parse
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse, Response, StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.csv_utils import (
    csv_safe,
    decode_csv_upload,
    guess_column_mapping,
    parse_column_mapping,
    parse_mapped_csv_rows,
    sniff_csv_delimiter,
)
from app.database import get_db
from app.i18n import AVAILABLE_LANGUAGES, t_for
from app.cloud_storage import CloudStorageError, get_cloud_storage_provider
from app.contact_documents import contact_folder_path, load_base_folder, sanitize_folder_name, upload_filename
from app.contact_filters import ContactListFilter
from app.parcel_cloud_folders import InvalidCloudPathError, sanitize_browse_subpath
from app.models import ExternalContact, ExternalContactTag, IncomingInvoice, PurchaseRequest
from app.module_flags import require_module
from app.permissions import has_permission, require_permission
from app.services.errors import ServiceError
from app.services.applicants import load_red_flag_tag, save_red_flag_tag
from app.services.external_contacts import (
    add_email, add_phone, count_tag_contacts, create_contact, delete_tag, find_duplicate, get_contact,
    list_active_contacts, list_tags, merge_phones_and_emails, remove_email, remove_phone, rename_tag, set_contact_tags,
    set_tag_translations, soft_delete_contact, tag_contact, untag_contact, update_contact,
)
from app.templating import templates

MODULE = "external_contacts"

router = APIRouter(
    prefix="/contacts",
    tags=["external-contacts"],
    dependencies=[Depends(require_module(MODULE))],
)


async def _get_contact_with_details(db: AsyncSession, contact_id: str) -> Optional[ExternalContact]:
    return await db.scalar(
        select(ExternalContact)
        .options(
            selectinload(ExternalContact.phone_numbers),
            selectinload(ExternalContact.email_addresses),
            selectinload(ExternalContact.tags),
        )
        .where(ExternalContact.id == contact_id, ExternalContact.deleted_at.is_(None))
        # The CSV import re-reads a contact it already touched earlier in
        # the same file; without this, its phones/emails would come from
        # the identity map, missing the ones that row just added.
        .execution_options(populate_existing=True)
    )


async def _get_contact_or_404(request: Request, db: AsyncSession, contact_id: str) -> ExternalContact:
    contact = await _get_contact_with_details(db, contact_id)
    if contact is None:
        raise HTTPException(status_code=404, detail=t_for(request, "external_contacts.errors.not_found"))
    return contact


def _redirect_with_error(request: Request, url: str, error: ServiceError) -> RedirectResponse:
    message = t_for(request, error.key, **error.params)
    return RedirectResponse(f"{url}?error={urllib.parse.quote(message)}", status_code=303)


@router.get("/", response_class=HTMLResponse)
async def contacts_list(
    request: Request,
    filters: ContactListFilter = Depends(ContactListFilter.from_query),
    db: AsyncSession = Depends(get_db),
):
    user = await require_permission(request, db, MODULE, "read")
    contacts = (await db.scalars(filters.apply().options(
        selectinload(ExternalContact.email_addresses),
        selectinload(ExternalContact.phone_numbers),
        selectinload(ExternalContact.tags),
    ))).all()
    return templates.TemplateResponse("external_contacts/list.html", {
        "request": request, "user": user, "contacts": contacts,
        "search": filters.search, "tag": filters.tag, "all_tags": await list_tags(db),
        "list_query_string": filters.query_string(),
    })


# ---------------------------------------------------------------------------
# Create / edit
# ---------------------------------------------------------------------------

def _form_context(request: Request, user, contact, all_tags, values: Optional[dict] = None, error: str = "") -> dict:
    return {
        "request": request, "user": user, "contact": contact, "all_tags": all_tags,
        "values": values or {}, "fehler": error,
    }


async def _sync_form_tags(request: Request, db: AsyncSession, contact_id: str) -> bool:
    """Same contract as the member form's tag section: returns False on
    an invalid new tag name, the caller saves the rest and sends the
    user back to the form."""
    form = await request.form()
    if form.get("tags_present") != "1":
        return True
    try:
        await set_contact_tags(db, contact_id, tag_ids=form.getlist("tag_ids"), new_names=form.get("new_tags", ""))
    except ServiceError:
        await db.commit()
        return False
    return True


@router.get("/new", response_class=HTMLResponse)
async def contact_new_page(request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_permission(request, db, MODULE, "write")
    return templates.TemplateResponse(
        "external_contacts/form.html", _form_context(request, user, None, await list_tags(db)),
    )


@router.post("/new")
async def contact_create(
    request: Request,
    company_name: str = Form(""),
    first_name: str = Form(""),
    last_name: str = Form(""),
    street: str = Form(""),
    postal_code: str = Form(""),
    city: str = Form(""),
    iban: str = Form(""),
    email: str = Form(""),
    phone: str = Form(""),
    notes: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    user = await require_permission(request, db, MODULE, "write")
    fields = dict(
        company_name=company_name, first_name=first_name, last_name=last_name,
        street=street, postal_code=postal_code, city=city, iban=iban, notes=notes,
    )
    try:
        contact = await create_contact(db, **fields)
    except ServiceError as e:
        # Raised before anything was added to the session -- nothing to roll back.
        return templates.TemplateResponse(
            "external_contacts/form.html",
            _form_context(request, user, None, await list_tags(db), {**fields, "email": email, "phone": phone},
                          t_for(request, e.key, **e.params)),
            status_code=e.http_status,
        )
    if email.strip():
        await add_email(db, contact.id, address=email, is_primary=True)
    if phone.strip():
        await add_phone(db, contact.id, number=phone, is_primary=True)
    if not await _sync_form_tags(request, db, contact.id):
        return RedirectResponse(f"/contacts/{contact.id}/edit", status_code=303)
    await db.commit()
    return RedirectResponse(f"/contacts/{contact.id}", status_code=302)


# ---------------------------------------------------------------------------
# Tags management page -- registered before /{contact_id}.
# ---------------------------------------------------------------------------

async def _get_tag_or_404(db: AsyncSession, tag_id: str) -> ExternalContactTag:
    tag = await db.get(ExternalContactTag, tag_id)
    if tag is None:
        raise HTTPException(status_code=404)
    return tag


@router.get("/tags", response_class=HTMLResponse)
async def tags_page(request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_permission(request, db, MODULE, "read")
    return templates.TemplateResponse("external_contacts/tags.html", {
        "request": request, "user": user,
        "tags": await list_tags(db), "contact_counts": await count_tag_contacts(db),
        "languages": AVAILABLE_LANGUAGES, "red_flag_tag": await load_red_flag_tag(db),
    })


@router.post("/tags/red-flag")
async def tag_red_flag(request: Request, tag_id: str = Form(""), db: AsyncSession = Depends(get_db)):
    """Which tag marks contacts whose name/email/phone flags a matching
    applicant (ADR 0098); empty = none."""
    await require_permission(request, db, MODULE, "write")
    try:
        await save_red_flag_tag(db, tag_id.strip() or None)
    except ServiceError as e:
        await db.rollback()
        return _redirect_with_error(request, "/contacts/tags", e)
    await db.commit()
    return RedirectResponse("/contacts/tags", status_code=303)


@router.post("/tags/{tag_id}/rename")
async def tag_rename(tag_id: str, request: Request, name: str = Form(""), db: AsyncSession = Depends(get_db)):
    await require_permission(request, db, MODULE, "write")
    tag = await _get_tag_or_404(db, tag_id)
    try:
        await rename_tag(db, tag, name)
    except ServiceError as e:
        await db.rollback()
        return _redirect_with_error(request, "/contacts/tags", e)
    await db.commit()
    return RedirectResponse("/contacts/tags", status_code=303)


@router.post("/tags/{tag_id}/translations")
async def tag_translations(tag_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    await require_permission(request, db, MODULE, "write")
    tag = await _get_tag_or_404(db, tag_id)
    form = await request.form()
    try:
        await set_tag_translations(db, tag, {lang: form.get(f"name_{lang}", "") for lang in AVAILABLE_LANGUAGES})
    except ServiceError as e:
        await db.rollback()
        return _redirect_with_error(request, "/contacts/tags", e)
    await db.commit()
    return RedirectResponse("/contacts/tags", status_code=303)


@router.post("/tags/{tag_id}/delete")
async def tag_delete(tag_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    await require_permission(request, db, MODULE, "delete")
    await delete_tag(db, await _get_tag_or_404(db, tag_id))
    await db.commit()
    return RedirectResponse("/contacts/tags", status_code=303)


# ---------------------------------------------------------------------------
# CSV export / import -- registered before /{contact_id}. Export and
# import use the same columns, so an exported file imports unchanged.
# ---------------------------------------------------------------------------

CSV_IMPORT_PREVIEW_ROWS = 5
CONTACTS_IMPORT_TARGET_FIELDS = [
    "company_name", "first_name", "last_name", "street", "postal_code", "city",
    "iban", "email_addresses", "phone_numbers", "tags", "notes",
]
CONTACTS_EXPORT_HEADERS = [
    "Firma", "Vorname", "Nachname", "Strasse", "PLZ", "Ort",
    "IBAN", "E-Mail-Adressen", "Telefonnummern", "Tags", "Notizen",
]
CONTACTS_IMPORT_FIELD_ALIASES = {
    "company_name": {"firma", "company", "company name", "unternehmen", "firmenname"},
    "first_name": {"vorname", "first name", "firstname"},
    "last_name": {"nachname", "last name", "lastname", "surname", "name"},
    "street": {"strasse", "straße", "street", "address", "adresse"},
    "postal_code": {"plz", "postal code", "zip", "zip code", "postcode"},
    "city": {"ort", "city", "town", "stadt"},
    "iban": {"iban"},
    "email_addresses": {"e-mail-adressen", "email addresses", "emails", "e-mail", "email"},
    "phone_numbers": {"telefonnummern", "phone numbers", "phones", "telefon", "phone"},
    "tags": {"tags", "schlagworte", "labels"},
    "notes": {"notizen", "notes", "note", "bemerkung"},
}


def _split_multi(value: Optional[str]) -> list[str]:
    return [part.strip() for part in (value or "").split(";") if part.strip()]


def _uncsv_safe(value: Optional[str]) -> str:
    """Undoes csv_safe()'s leading apostrophe, so a phone number like
    +49... exported by us comes back without it."""
    value = (value or "").strip()
    if len(value) > 1 and value[0] == "'" and value[1] in ("=", "+", "-", "@"):
        return value[1:]
    return value


@router.get("/export/csv")
async def contacts_export_csv(
    request: Request,
    filters: ContactListFilter = Depends(ContactListFilter.from_query),
    db: AsyncSession = Depends(get_db),
):
    await require_permission(request, db, MODULE, "read")
    contacts = (await db.scalars(filters.apply().options(
        selectinload(ExternalContact.email_addresses),
        selectinload(ExternalContact.phone_numbers),
        selectinload(ExternalContact.tags),
    ))).all()

    output = io.StringIO()
    writer = csv.writer(output, delimiter=";")
    writer.writerow(CONTACTS_EXPORT_HEADERS)
    for c in contacts:
        writer.writerow([
            csv_safe(c.company_name or ""), csv_safe(c.first_name), csv_safe(c.last_name),
            csv_safe(c.street or ""), csv_safe(c.postal_code or ""), csv_safe(c.city or ""),
            csv_safe(c.iban or ""),
            csv_safe("; ".join(e.address for e in c.email_addresses)),
            csv_safe("; ".join(p.number for p in c.phone_numbers)),
            csv_safe("; ".join(tag.name for tag in c.tags)),
            csv_safe(c.notes or ""),
        ])
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=external-contacts.csv"},
    )


@router.post("/import/preview", response_class=HTMLResponse)
async def contacts_import_preview(request: Request, file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    """Step 1 of the column-mapping wizard (ADR 0083), same as members:
    nothing is written yet, the raw CSV round-trips as base64."""
    user = await require_permission(request, db, MODULE, "write")
    content = await file.read()
    text = decode_csv_upload(content)
    delimiter = sniff_csv_delimiter(text)
    rows = list(csv.reader(io.StringIO(text), delimiter=delimiter))
    if not rows:
        message = t_for(request, "external_contacts.import.empty_error")
        return RedirectResponse(f"/contacts/?error={urllib.parse.quote(message)}", status_code=303)
    headers = [h.strip() for h in rows[0]]
    return templates.TemplateResponse("external_contacts/import_preview.html", {
        "request": request, "user": user,
        "headers": headers, "preview_rows": rows[1:1 + CSV_IMPORT_PREVIEW_ROWS],
        "default_mapping": guess_column_mapping(headers, CONTACTS_IMPORT_FIELD_ALIASES),
        "target_fields": CONTACTS_IMPORT_TARGET_FIELDS,
        "csv_content_b64": base64.b64encode(content).decode("ascii"), "delimiter": delimiter,
    })


@router.post("/import/finalize")
async def contacts_import_finalize(
    request: Request,
    csv_content_b64: str = Form(...), delimiter: str = Form(";"),
    db: AsyncSession = Depends(get_db),
):
    """Step 2. A row matches an existing contact the same way duplicates
    are defined (ignoring case): by the person name if the row has one,
    otherwise by company among the contacts without a person -- both
    unique, so the match is unambiguous. A match gets its fields updated
    from the non-empty cells, and phones, emails and tags it doesn't
    have yet added; nothing is removed. Every field is optional; only
    completely empty rows are skipped."""
    await require_permission(request, db, MODULE, "write")
    form = await request.form()
    column_mapping = parse_column_mapping(form, CONTACTS_IMPORT_TARGET_FIELDS)
    if not column_mapping:
        message = t_for(request, "external_contacts.import.mapping_required_error")
        return RedirectResponse(f"/contacts/?error={urllib.parse.quote(message)}", status_code=303)
    rows = parse_mapped_csv_rows(csv_content_b64, delimiter, column_mapping)

    created = updated = 0
    errors: list[str] = []
    scalar_fields = ("company_name", "first_name", "last_name", "street", "postal_code", "city", "iban", "notes")

    for row_number, values in enumerate(rows, start=2):
        values = {k: _uncsv_safe(v) for k, v in values.items()}
        if not any(values.values()):
            continue  # blank line

        try:
            existing = await find_duplicate(
                db, first_name=values.get("first_name"), last_name=values.get("last_name"),
                company_name=values.get("company_name"),
            )
            if existing is not None:
                contact = await _get_contact_with_details(db, existing.id)
                await update_contact(db, contact, **{k: values[k] for k in scalar_fields if values.get(k)})
                updated += 1
            else:
                contact = await create_contact(db, **{k: values.get(k) or None for k in scalar_fields})
                await db.refresh(contact, attribute_names=["phone_numbers", "email_addresses"])
                created += 1
            await merge_phones_and_emails(
                db, contact,
                phones=_split_multi(values.get("phone_numbers")), emails=_split_multi(values.get("email_addresses")),
            )
            for tag_name in _split_multi(values.get("tags")):
                await tag_contact(db, contact.id, name=tag_name)
        except ServiceError as e:
            errors.append(t_for(request, "external_contacts.import.row_error", row=row_number,
                                error=t_for(request, e.key, **e.params)))

    await db.commit()

    message = t_for(request, "external_contacts.import.summary", created=created, updated=updated)
    if errors:
        message += " " + t_for(request, "external_contacts.import.errors_suffix", count=len(errors))
        message += " – " + " | ".join(errors[:3])
        if len(errors) > 3:
            message += " " + t_for(request, "external_contacts.import.more_errors", count=len(errors) - 3)
    return RedirectResponse(f"/contacts/?message={urllib.parse.quote(message)}", status_code=302)


# ---------------------------------------------------------------------------
# Detail / edit / delete
# ---------------------------------------------------------------------------

@router.get("/{contact_id}", response_class=HTMLResponse)
async def contact_detail(
    contact_id: str,
    request: Request,
    filters: ContactListFilter = Depends(ContactListFilter.from_query),
    docs_path: str = "",
    docs_pick: str = "",
    db: AsyncSession = Depends(get_db),
):
    user = await require_permission(request, db, MODULE, "read")
    contact = await _get_contact_or_404(request, db, contact_id)

    ordered_ids = (await db.scalars(filters.apply().with_only_columns(ExternalContact.id))).all()
    prev_id = next_id = None
    if contact_id in ordered_ids:
        idx = ordered_ids.index(contact_id)
        prev_id = ordered_ids[idx - 1] if idx > 0 else None
        next_id = ordered_ids[idx + 1] if idx < len(ordered_ids) - 1 else None

    # Linked records from other modules -- only if that module is on and
    # the user may read it there anyway.
    flags = getattr(request.state, "module_flags", {})
    permissions = getattr(request.state, "permissions", {})
    incoming_invoices = None
    if flags.get("finances") and has_permission(permissions, "finances", "read"):
        incoming_invoices = (await db.scalars(
            select(IncomingInvoice)
            .options(selectinload(IncomingInvoice.line_items), selectinload(IncomingInvoice.payments))
            .where(IncomingInvoice.external_contact_id == contact_id)
            .order_by(IncomingInvoice.invoice_date.desc())
        )).all()
    purchase_requests = None
    if flags.get("purchase_requests") and has_permission(permissions, "purchase_requests", "read"):
        purchase_requests = (await db.scalars(
            select(PurchaseRequest)
            .where(PurchaseRequest.external_contact_id == contact_id)
            .order_by(PurchaseRequest.created_at.desc())
        )).all()

    documents = None
    if flags.get("cloud_storage"):
        documents = await _documents_context(
            request, db, contact,
            browse_path=sanitize_browse_subpath(docs_path),
            picking=docs_pick == "1" and has_permission(permissions, MODULE, "write"),
        )

    list_query_string = filters.query_string()
    return templates.TemplateResponse("external_contacts/detail.html", {
        "request": request, "user": user, "contact": contact, "all_tags": await list_tags(db),
        "prev_contact_id": prev_id, "next_contact_id": next_id,
        "nav_query_suffix": f"?{list_query_string}" if list_query_string else "",
        "incoming_invoices": incoming_invoices, "purchase_requests": purchase_requests,
        "documents": documents,
    })


# ---------------------------------------------------------------------------
# Documents in the cloud (ADR 0097): one subfolder of the club-wide base
# folder per contact, picked from the folders that exist there. Only
# with the cloud_storage module on; read lists/downloads, write picks the
# folder and uploads. Deleting files is left to the cloud itself.
# ---------------------------------------------------------------------------

async def _documents_context(
    request: Request, db: AsyncSession, contact: ExternalContact, *, browse_path: str, picking: bool,
) -> dict:
    """Everything the detail page's documents card needs. Cloud errors
    end up in `error` instead of breaking the page."""
    docs = {
        "base_folder": await load_base_folder(db), "browse_path": browse_path, "breadcrumbs": [],
        "files": None, "folder_options": None, "error": None,
    }
    listing = bool(contact.cloud_folder) and not picking
    may_pick = has_permission(getattr(request.state, "permissions", {}), MODULE, "write")
    if not docs["base_folder"] or not (listing or may_pick):
        return docs
    provider = await get_cloud_storage_provider(db)
    if provider is None:
        docs["error"] = t_for(request, "external_contacts.documents.cloud_not_configured")
        return docs
    try:
        if listing:
            docs["breadcrumbs"] = [{"name": contact.cloud_folder, "path": ""}]
            accumulated = []
            for segment in browse_path.split("/") if browse_path else []:
                accumulated.append(segment)
                docs["breadcrumbs"].append({"name": segment, "path": "/".join(accumulated)})
            docs["files"] = await provider.list_files(
                contact_folder_path(docs["base_folder"], contact.cloud_folder, browse_path)
            )
        else:
            entries = await provider.list_files(docs["base_folder"])
            docs["folder_options"] = sorted((e.name for e in entries if e.is_directory), key=str.lower)
    except CloudStorageError as e:
        docs["error"] = str(e)
    finally:
        await provider.aclose()
    return docs


def _documents_redirect(contact_id: str, browse_path: str = "", **params: str) -> RedirectResponse:
    query = {k: v for k, v in params.items() if v}
    if browse_path:
        query["docs_path"] = browse_path
    suffix = f"?{urllib.parse.urlencode(query)}" if query else ""
    return RedirectResponse(f"/contacts/{contact_id}{suffix}#documents", status_code=303)


@router.post("/{contact_id}/documents/folder", dependencies=[Depends(require_module("cloud_storage"))])
async def documents_folder_set(
    contact_id: str, request: Request, folder_name: str = Form(""), db: AsyncSession = Depends(get_db),
):
    """Picks the contact's subfolder ("" unlinks it -- the files stay in
    the cloud)."""
    await require_permission(request, db, MODULE, "write")
    contact = await _get_contact_or_404(request, db, contact_id)
    if folder_name.strip():
        try:
            contact.cloud_folder = sanitize_folder_name(folder_name)
        except InvalidCloudPathError:
            return _documents_redirect(
                contact_id, docs_error=t_for(request, "external_contacts.documents.invalid_folder"),
            )
    else:
        contact.cloud_folder = None
    await db.commit()
    return _documents_redirect(contact_id, docs_saved="1")


async def _documents_folder_or_404(request: Request, db: AsyncSession, contact: ExternalContact) -> str:
    base_folder = await load_base_folder(db)
    if not base_folder or not contact.cloud_folder:
        raise HTTPException(status_code=404, detail=t_for(request, "external_contacts.documents.no_folder"))
    return base_folder


@router.post("/{contact_id}/documents/upload", dependencies=[Depends(require_module("cloud_storage"))])
async def documents_upload(
    contact_id: str, request: Request,
    file: UploadFile = File(...), docs_path: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    """Uploads into the subfolder currently being browsed."""
    await require_permission(request, db, MODULE, "write")
    contact = await _get_contact_or_404(request, db, contact_id)
    base_folder = await _documents_folder_or_404(request, db, contact)
    browse_path = sanitize_browse_subpath(docs_path)
    try:
        filename = upload_filename(file.filename)
    except InvalidCloudPathError:
        return _documents_redirect(
            contact_id, browse_path, docs_error=t_for(request, "external_contacts.documents.invalid_file"),
        )
    provider = await get_cloud_storage_provider(db)
    if provider is None:
        raise HTTPException(status_code=400, detail=t_for(request, "external_contacts.documents.cloud_not_configured"))
    try:
        await provider.upload_file(
            contact_folder_path(base_folder, contact.cloud_folder, browse_path), filename, await file.read(),
        )
    except CloudStorageError as e:
        return _documents_redirect(contact_id, browse_path, docs_error=str(e))
    finally:
        await provider.aclose()
    return _documents_redirect(contact_id, browse_path, docs_uploaded="1")


@router.get("/{contact_id}/documents/download", dependencies=[Depends(require_module("cloud_storage"))])
async def documents_download(
    contact_id: str, request: Request, filename: str, docs_path: str = "",
    db: AsyncSession = Depends(get_db),
):
    await require_permission(request, db, MODULE, "read")
    contact = await _get_contact_or_404(request, db, contact_id)
    base_folder = await _documents_folder_or_404(request, db, contact)
    provider = await get_cloud_storage_provider(db)
    if provider is None:
        raise HTTPException(status_code=400, detail=t_for(request, "external_contacts.documents.cloud_not_configured"))
    try:
        content = await provider.download_file(
            contact_folder_path(base_folder, contact.cloud_folder, sanitize_browse_subpath(docs_path)), filename,
        )
    except CloudStorageError as e:
        raise HTTPException(status_code=502, detail=str(e))
    finally:
        await provider.aclose()
    # The name is percent-encoded, so a CR/LF or quote in a cloud file
    # name can't break out of the header (see CLAUDE.md).
    return Response(
        content=content, media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{urllib.parse.quote(filename)}"},
    )


@router.get("/{contact_id}/edit", response_class=HTMLResponse)
async def contact_edit_page(contact_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_permission(request, db, MODULE, "write")
    contact = await _get_contact_or_404(request, db, contact_id)
    return templates.TemplateResponse(
        "external_contacts/form.html", _form_context(request, user, contact, await list_tags(db)),
    )


@router.post("/{contact_id}/edit")
async def contact_update(
    contact_id: str,
    request: Request,
    company_name: str = Form(""),
    first_name: str = Form(""),
    last_name: str = Form(""),
    street: str = Form(""),
    postal_code: str = Form(""),
    city: str = Form(""),
    iban: str = Form(""),
    notes: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    user = await require_permission(request, db, MODULE, "write")
    contact = await _get_contact_or_404(request, db, contact_id)
    fields = dict(
        company_name=company_name, first_name=first_name, last_name=last_name,
        street=street, postal_code=postal_code, city=city, iban=iban, notes=notes,
    )
    try:
        await update_contact(db, contact, **fields)
    except ServiceError as e:
        # Raised before any field was changed (update_contact validates
        # first). A rollback here would expire `contact` and make the
        # template lazy-load under asyncio.
        return templates.TemplateResponse(
            "external_contacts/form.html",
            _form_context(request, user, contact, await list_tags(db), fields, t_for(request, e.key, **e.params)),
            status_code=e.http_status,
        )
    if not await _sync_form_tags(request, db, contact_id):
        return RedirectResponse(f"/contacts/{contact_id}/edit", status_code=303)
    await db.commit()
    return RedirectResponse(f"/contacts/{contact_id}", status_code=302)


@router.post("/{contact_id}/delete")
async def contact_delete(contact_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    """Soft delete (ADR 0005): linked incoming invoices and purchase
    requests keep pointing at the contact."""
    await require_permission(request, db, MODULE, "delete")
    contact = await _get_contact_or_404(request, db, contact_id)
    await soft_delete_contact(db, contact)
    await db.commit()
    name = contact.display_name or t_for(request, "external_contacts.unnamed")
    message = t_for(request, "external_contacts.detail.deleted_message", name=name)
    return RedirectResponse(f"/contacts/?message={urllib.parse.quote(message)}", status_code=302)


# ---------------------------------------------------------------------------
# Tags / phones / emails on one contact
# ---------------------------------------------------------------------------

@router.post("/{contact_id}/tags/add")
async def contact_tag_add(
    contact_id: str, request: Request, name: str = Form(""), db: AsyncSession = Depends(get_db),
):
    await require_permission(request, db, MODULE, "write")
    await _get_contact_or_404(request, db, contact_id)
    try:
        await tag_contact(db, contact_id, name=name)
    except ServiceError as e:
        await db.rollback()
        return _redirect_with_error(request, f"/contacts/{contact_id}", e)
    await db.commit()
    return RedirectResponse(f"/contacts/{contact_id}", status_code=303)


@router.post("/{contact_id}/tags/{tag_id}/remove")
async def contact_tag_remove(contact_id: str, tag_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    await require_permission(request, db, MODULE, "write")
    await untag_contact(db, contact_id, tag_id)
    await db.commit()
    return RedirectResponse(f"/contacts/{contact_id}", status_code=303)


@router.post("/{contact_id}/phone/add")
async def phone_add(
    contact_id: str, request: Request,
    number: str = Form(...), label: str = Form(""), is_primary: bool = Form(False),
    db: AsyncSession = Depends(get_db),
):
    await require_permission(request, db, MODULE, "write")
    await _get_contact_or_404(request, db, contact_id)
    await add_phone(db, contact_id, number=number, label=label, is_primary=is_primary)
    await db.commit()
    return RedirectResponse(f"/contacts/{contact_id}", status_code=302)


@router.post("/{contact_id}/phone/{phone_id}/delete")
async def phone_delete(contact_id: str, phone_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    await require_permission(request, db, MODULE, "delete")
    if await remove_phone(db, contact_id, phone_id):
        await db.commit()
    return RedirectResponse(f"/contacts/{contact_id}", status_code=302)


@router.post("/{contact_id}/email/add")
async def email_add(
    contact_id: str, request: Request,
    address: str = Form(...), label: str = Form(""), is_primary: bool = Form(False),
    db: AsyncSession = Depends(get_db),
):
    await require_permission(request, db, MODULE, "write")
    await _get_contact_or_404(request, db, contact_id)
    await add_email(db, contact_id, address=address, label=label, is_primary=is_primary)
    await db.commit()
    return RedirectResponse(f"/contacts/{contact_id}", status_code=302)


@router.post("/{contact_id}/email/{email_id}/delete")
async def email_delete(contact_id: str, email_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    await require_permission(request, db, MODULE, "delete")
    if await remove_email(db, contact_id, email_id):
        await db.commit()
    return RedirectResponse(f"/contacts/{contact_id}", status_code=302)


# ---------------------------------------------------------------------------
# Contact pickers on other modules' forms (incoming invoices, purchase
# requests -- ADR 0096).
# ---------------------------------------------------------------------------

async def picker_contacts(request: Request, db: AsyncSession) -> Optional[list[ExternalContact]]:
    """The contacts to offer in a picker, or None if this user shouldn't
    see one (module off, or no read access to contacts)."""
    flags = getattr(request.state, "module_flags", {})
    permissions = getattr(request.state, "permissions", {})
    if not flags.get(MODULE) or not has_permission(permissions, MODULE, "read"):
        return None
    return await list_active_contacts(db)


async def resolve_picked_contact(request: Request, db: AsyncSession, contact_id: str) -> Optional[str]:
    """Validates a submitted picker value: "" clears the link, anything
    else must be a non-deleted contact the user may see."""
    if not contact_id.strip():
        return None
    if await picker_contacts(request, db) is None or await get_contact(db, contact_id.strip()) is None:
        raise HTTPException(status_code=400, detail=t_for(request, "external_contacts.errors.not_found"))
    return contact_id.strip()
