"""Invoice runs: list, create, items, preview, finalize, delivery, print bundle."""
from fastapi import APIRouter
from datetime import date, datetime
from fastapi import Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.i18n import t_for
from app.models import (
    FinanceAccount,
    FinanceCategory,
    Invoice,
    InvoiceItemDefinition,
    InvoiceItemDefinitionMember,
    InvoiceItemDefinitionParcel,
    InvoiceItemTemplate,
    InvoicePayment,
    InvoicePricingMode,
    InvoiceRun,
    InvoiceRunStatus,
    Parcel,
)
from app.permissions import require_permission
from app.l10n import parse_decimal
from app.cloud_storage import get_cloud_storage_provider
from app.invoice_generation import SequenceCollisionError, compute_invoices_for_run, finalize_run
from app.invoice_pdf import InvoicePdfData, InvoicePdfLineItem, render_invoice_pdf
from app.invoice_delivery import (
    build_print_bundle,
    copies_to_print,
    send_invoice_email,
    upload_invoice_to_cloud,
)
from app.templating import templates
from app.routers.finances._common import _AUTOMATIC_PRICING_MODES, _dedupe_ids, _get_run_or_404
from app.services.finances import (
    list_active_members,
    list_active_parcels,
    list_item_templates,
    pdf_context,
    run_invoices,
)

router = APIRouter()


# ---------------------------------------------------------------------------
# Invoice runs: list, create
# ---------------------------------------------------------------------------

@router.get("/runs", response_class=HTMLResponse)
async def run_list(
    request: Request, year: str = "", subject: str = "", status: str = "",
    db: AsyncSession = Depends(get_db),
):
    """Issue #266: filterable by year, subject and status, same layout as
    the incoming invoices list; "New invoice run" is a modal."""
    user = await require_permission(request, db, "finances", "read")

    query = (
        select(InvoiceRun)
        .options(selectinload(InvoiceRun.item_definitions))
        .order_by(InvoiceRun.year.desc(), InvoiceRun.created_at.desc())
    )
    year = year.strip()
    if year.isdigit():
        query = query.where(InvoiceRun.year == int(year))
    if subject.strip():
        query = query.where(InvoiceRun.subject.ilike(f"%{subject.strip()}%"))
    if status in {s.value for s in InvoiceRunStatus}:
        query = query.where(InvoiceRun.status == InvoiceRunStatus(status))
    result = await db.execute(query)
    runs = list(result.scalars().all())

    return templates.TemplateResponse(request, "finances/run_list.html", {
        "request": request, "user": user, "runs": runs,
        "today": date.today().isoformat(),
        "current_year": date.today().year,
        "filter_year": year, "filter_subject": subject, "filter_status": status,
        "filtered": bool(year or subject.strip() or status),
    })


@router.post("/runs")
async def run_create(
    request: Request,
    year: int = Form(...),
    subject: str = Form(...),
    issued_date: str = Form(...),
    due_date: str = Form(...),
    footer_text: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    user = await require_permission(request, db, "finances", "write")

    run = InvoiceRun(
        year=year,
        subject=subject.strip(),
        issued_date=datetime.strptime(issued_date, "%Y-%m-%d").date(),
        due_date=datetime.strptime(due_date, "%Y-%m-%d").date(),
        footer_text=footer_text.strip() or None,
        created_by_id=user.id,
    )
    db.add(run)
    await db.commit()
    return RedirectResponse(f"/finances/runs/{run.id}", status_code=302)


@router.post("/runs/{run_id}/delete")
async def run_delete(run_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    await require_permission(request, db, "finances", "delete")

    run = await _get_run_or_404(db, run_id)
    if run.status != InvoiceRunStatus.DRAFT:
        return RedirectResponse(
            f"/finances/runs?error={t_for(request, 'finances.errors.cannot_delete_finalized_run')}",
            status_code=302,
        )
    await db.delete(run)
    await db.commit()
    return RedirectResponse("/finances/runs?success=1", status_code=302)


# ---------------------------------------------------------------------------
# Invoice run detail: item definitions
# ---------------------------------------------------------------------------

@router.get("/runs/{run_id}", response_class=HTMLResponse)
async def run_detail(
    run_id: str, request: Request,
    invoice_number: str = "", recipient: str = "", parcel: str = "",
    amount_min: str = "", amount_max: str = "", status: str = "",
    db: AsyncSession = Depends(get_db),
):
    """Issue #190 follow-up: the flat /finances/invoices list got
    search/filter, but a single run's own invoice table (which can
    still run to one row per parcel) had none at all -- same fields,
    scoped to this run."""
    user = await require_permission(request, db, "finances", "read")

    run = await _get_run_or_404(db, run_id)
    parcels = await list_active_parcels(db)
    members = await list_active_members(db)

    next_order = (max((i.order_number for i in run.item_definitions), default=0) + 10)

    invoices = []
    accounts = []
    if run.status == InvoiceRunStatus.FINALIZED:
        query = (
            select(Invoice)
            .options(
                selectinload(Invoice.parcel), selectinload(Invoice.member),
                selectinload(Invoice.payments).selectinload(InvoicePayment.account),
                selectinload(Invoice.reminders),
            )
            .outerjoin(Parcel, Invoice.parcel_id == Parcel.id)
            .where(Invoice.invoice_run_id == run.id)
            .order_by(Invoice.invoice_number)
        )
        if invoice_number.strip():
            query = query.where(Invoice.invoice_number.ilike(f"%{invoice_number.strip()}%"))
        if recipient.strip():
            query = query.where(Invoice.recipient_names.ilike(f"%{recipient.strip()}%"))
        if parcel.strip():
            query = query.where(Parcel.plot_number.ilike(f"%{parcel.strip()}%"))
        parsed_amount_min = parse_decimal(amount_min) if amount_min.strip() else None
        if parsed_amount_min is not None:
            query = query.where(Invoice.subtotal >= parsed_amount_min)
        parsed_amount_max = parse_decimal(amount_max) if amount_max.strip() else None
        if parsed_amount_max is not None:
            query = query.where(Invoice.subtotal <= parsed_amount_max)

        result = await db.execute(query)
        invoices = list(result.scalars().all())
        if status in ("open", "partially_paid", "paid"):
            invoices = [i for i in invoices if i.payment_status == status]

        accounts_result = await db.execute(
            select(FinanceAccount).where(FinanceAccount.is_active == True).order_by(FinanceAccount.name)  # noqa: E712
        )
        accounts = list(accounts_result.scalars().all())

    item_templates = []
    catalog_all_used = False
    if run.status == InvoiceRunStatus.DRAFT:
        all_item_templates = await list_item_templates(db)
        # Issue #94: don't offer a catalog item the run already has --
        # matched by name, since applying a template copies its fields
        # onto a brand new InvoiceItemDefinition with no stored link
        # back to the template it came from (see items_add_from_catalog).
        # Recomputed fresh on every load, so renaming/deleting an item
        # directly on the run makes its template reappear here again.
        used_names = {d.name for d in run.item_definitions}
        item_templates = [t for t in all_item_templates if t.name not in used_names]
        catalog_all_used = bool(all_item_templates) and not item_templates

    categories_result = await db.execute(select(FinanceCategory).order_by(FinanceCategory.code))
    categories = list(categories_result.scalars().all())

    return templates.TemplateResponse(request, "finances/run_detail.html", {
        "request": request, "user": user, "run": run, "parcels": parcels, "members": members,
        "pricing_modes": list(InvoicePricingMode),
        "next_order": next_order,
        "invoices": invoices,
        "accounts": accounts,
        "today": date.today().isoformat(),
        "item_templates": item_templates,
        "catalog_all_used": catalog_all_used,
        "categories": categories,
        "filter_invoice_number": invoice_number, "filter_recipient": recipient, "filter_parcel": parcel,
        "filter_amount_min": amount_min, "filter_amount_max": amount_max, "filter_status": status,
    })


@router.post("/runs/{run_id}/items")
async def item_create(
    run_id: str,
    request: Request,
    order_number: int = Form(0),
    name: str = Form(...),
    description: str = Form(""),
    pricing_mode: str = Form(...),
    unit_price: str = Form(""),
    applies_to_all_parcels: str = Form(""),
    applies_to_all_members: str = Form(""),
    parcel_ids: list[str] = Form([]),
    member_ids: list[str] = Form([]),
    category_id: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    await require_permission(request, db, "finances", "write")

    run = await _get_run_or_404(db, run_id)
    if run.status != InvoiceRunStatus.DRAFT:
        raise HTTPException(status_code=400, detail=t_for(request, "finances.errors.run_not_draft"))

    try:
        mode = InvoicePricingMode(pricing_mode)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid pricing_mode")

    applies_all_parcels = applies_to_all_parcels == "on"
    applies_all_members = applies_to_all_members == "on"
    item = InvoiceItemDefinition(
        invoice_run_id=run.id,
        order_number=order_number,
        name=name.strip(),
        description=description.strip() or None,
        pricing_mode=mode,
        unit_price=parse_decimal(unit_price) if mode not in _AUTOMATIC_PRICING_MODES else None,
        applies_to_all_parcels=applies_all_parcels,
        applies_to_all_members=applies_all_members,
        category_id=category_id.strip() or None,
    )
    db.add(item)
    await db.flush()

    if not applies_all_parcels:
        for parcel_id in _dedupe_ids(parcel_ids):
            db.add(InvoiceItemDefinitionParcel(invoice_item_definition_id=item.id, parcel_id=parcel_id))
    if not applies_all_members:
        for member_id in _dedupe_ids(member_ids):
            db.add(InvoiceItemDefinitionMember(invoice_item_definition_id=item.id, member_id=member_id))

    await db.commit()
    return RedirectResponse(f"/finances/runs/{run_id}", status_code=302)


@router.post("/runs/{run_id}/items/add-from-catalog")
async def items_add_from_catalog(
    run_id: str,
    request: Request,
    template_ids: list[str] = Form([]),
    db: AsyncSession = Depends(get_db),
):
    """Adds one InvoiceItemDefinition per selected InvoiceItemTemplate
    to `run_id` -- the visible, curated replacement for the old "copy
    items from another run" mechanism (issue #66), so a board member
    picks known-good recurring items by name/price instead of blindly
    duplicating everything from a specific past run (which may have
    included one-off items). Inherits the template's own scope
    verbatim, including specific parcel_scopes/member_scopes -- itself
    still freely editable afterward on the new item, same as the
    template. Adds to whatever's already on the target run rather than
    replacing it."""
    await require_permission(request, db, "finances", "write")

    run = await _get_run_or_404(db, run_id)
    if run.status != InvoiceRunStatus.DRAFT:
        raise HTTPException(status_code=400, detail=t_for(request, "finances.errors.run_not_draft"))

    if template_ids:
        result = await db.execute(
            select(InvoiceItemTemplate)
            .options(
                selectinload(InvoiceItemTemplate.parcel_scopes), selectinload(InvoiceItemTemplate.member_scopes),
            )
            .where(InvoiceItemTemplate.id.in_(template_ids))
        )
        for template in result.scalars().all():
            item = InvoiceItemDefinition(
                invoice_run_id=run.id,
                order_number=template.order_number,
                name=template.name,
                description=template.description,
                pricing_mode=template.pricing_mode,
                unit_price=template.unit_price,
                applies_to_all_parcels=template.applies_to_all_parcels,
                applies_to_all_members=template.applies_to_all_members,
                category_id=template.category_id,
            )
            db.add(item)
            await db.flush()

            if not template.applies_to_all_parcels:
                for scope in template.parcel_scopes:
                    db.add(InvoiceItemDefinitionParcel(invoice_item_definition_id=item.id, parcel_id=scope.parcel_id))
            if not template.applies_to_all_members:
                for scope in template.member_scopes:
                    db.add(InvoiceItemDefinitionMember(invoice_item_definition_id=item.id, member_id=scope.member_id))

    await db.commit()
    return RedirectResponse(f"/finances/runs/{run_id}", status_code=302)


@router.post("/runs/{run_id}/items/{item_id}/edit")
async def item_update(
    run_id: str,
    item_id: str,
    request: Request,
    order_number: int = Form(0),
    name: str = Form(...),
    description: str = Form(""),
    pricing_mode: str = Form(...),
    unit_price: str = Form(""),
    applies_to_all_parcels: str = Form(""),
    applies_to_all_members: str = Form(""),
    parcel_ids: list[str] = Form([]),
    member_ids: list[str] = Form([]),
    category_id: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    """
    Edits an item definition, including its scope (specific parcels for
    plot-scoped modes, specific members for fixed_per_person) --
    editable freely any time before the run is finalized (a member
    asked for this explicitly: the picker should stay open to change up
    until the next invoice run actually happens, not be locked in at
    creation). Once finalized, item definitions can't be changed at all
    (see the run.status check below), matching how every other field
    here already works.
    """
    await require_permission(request, db, "finances", "write")

    result = await db.execute(
        select(InvoiceItemDefinition)
        .options(
            selectinload(InvoiceItemDefinition.parcel_scopes), selectinload(InvoiceItemDefinition.member_scopes),
        )
        .where(InvoiceItemDefinition.id == item_id, InvoiceItemDefinition.invoice_run_id == run_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404)

    run = await _get_run_or_404(db, run_id)
    if run.status != InvoiceRunStatus.DRAFT:
        raise HTTPException(status_code=400, detail=t_for(request, "finances.errors.run_not_draft"))

    try:
        mode = InvoicePricingMode(pricing_mode)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid pricing_mode")

    applies_all_parcels = applies_to_all_parcels == "on"
    applies_all_members = applies_to_all_members == "on"
    item.order_number = order_number
    item.name = name.strip()
    item.description = description.strip() or None
    item.pricing_mode = mode
    item.unit_price = parse_decimal(unit_price) if mode not in _AUTOMATIC_PRICING_MODES else None
    item.applies_to_all_parcels = applies_all_parcels
    item.applies_to_all_members = applies_all_members
    item.category_id = category_id.strip() or None

    # Always resync scopes to what was actually submitted -- cleared
    # when applies_all, replaced with the new selection otherwise, so
    # stale choices never linger if scope changes back and forth
    # before finalize.
    #
    # The flush() right after each delete loop is required, not
    # cosmetic: SQLAlchemy's unit of work flushes INSERTs before
    # DELETEs for a given table within a single flush, so re-adding a
    # scope row that's unchanged from before (same parcel/member kept
    # selected) would otherwise try to INSERT the new row while the
    # identical old row is still physically present, tripping the
    # (definition_id, parcel_id)/(definition_id, member_id) unique
    # constraint -- found via a real 500 on re-saving an item whose
    # scope didn't change.
    for scope in list(item.parcel_scopes):
        await db.delete(scope)
    await db.flush()
    if not applies_all_parcels:
        for parcel_id in _dedupe_ids(parcel_ids):
            db.add(InvoiceItemDefinitionParcel(invoice_item_definition_id=item.id, parcel_id=parcel_id))
    for scope in list(item.member_scopes):
        await db.delete(scope)
    await db.flush()
    if not applies_all_members:
        for member_id in _dedupe_ids(member_ids):
            db.add(InvoiceItemDefinitionMember(invoice_item_definition_id=item.id, member_id=member_id))

    await db.commit()
    return RedirectResponse(f"/finances/runs/{run_id}", status_code=302)


@router.post("/runs/{run_id}/items/{item_id}/delete")
async def item_delete(run_id: str, item_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    await require_permission(request, db, "finances", "delete")

    result = await db.execute(
        select(InvoiceItemDefinition).where(
            InvoiceItemDefinition.id == item_id, InvoiceItemDefinition.invoice_run_id == run_id,
        )
    )
    item = result.scalar_one_or_none()
    if item:
        await db.delete(item)
        await db.commit()
    return RedirectResponse(f"/finances/runs/{run_id}", status_code=302)


# ---------------------------------------------------------------------------
# Preview and finalization
# ---------------------------------------------------------------------------

@router.get("/runs/{run_id}/preview", response_class=HTMLResponse)
async def run_preview(run_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_permission(request, db, "finances", "read")

    run = await _get_run_or_404(db, run_id)
    computed = await compute_invoices_for_run(db, run)

    return templates.TemplateResponse(request, "finances/run_preview.html", {
        "request": request, "user": user, "run": run, "computed": computed,
    })


@router.get("/runs/{run_id}/preview/{parcel_id}/pdf")
async def run_preview_pdf(run_id: str, parcel_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    await require_permission(request, db, "finances", "read")

    run = await _get_run_or_404(db, run_id)
    computed = await compute_invoices_for_run(db, run)
    match = next((c for c in computed if c.parcel and c.parcel.id == parcel_id), None)
    if not match:
        raise HTTPException(status_code=404)

    ctx = await pdf_context(db)
    data = InvoicePdfData(
        invoice_number=t_for(request, "finances.run_preview.pdf_placeholder_number"),
        issued_date=run.issued_date, due_date=run.due_date, subject=run.subject,
        recipient_names=match.recipient_names, recipient_address=match.recipient_address,
        parcel_plot_number=match.parcel.plot_number, parcel_area_sqm=match.parcel.area_sqm,
        line_items=[
            InvoicePdfLineItem(
                order_number=li.order_number, name=li.name, description=li.description,
                quantity=li.quantity, unit_price=li.unit_price, line_total=li.line_total,
            ) for li in match.line_items
        ],
        subtotal=match.subtotal, footer_text=run.footer_text, is_preview=True,
    )
    pdf_bytes = render_invoice_pdf(data, **ctx)
    return Response(content=pdf_bytes, media_type="application/pdf")


@router.get("/runs/{run_id}/preview/member/{member_id}/pdf")
async def run_preview_member_pdf(run_id: str, member_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    """Same as run_preview_pdf, but for a computed member invoice --
    a club member billed directly by a fixed_per_person item's own
    applies_to_all_members/member_scopes, regardless of parcel status
    (see app/invoice_generation.py)."""
    await require_permission(request, db, "finances", "read")

    run = await _get_run_or_404(db, run_id)
    computed = await compute_invoices_for_run(db, run)
    match = next((c for c in computed if c.member and c.member.id == member_id), None)
    if not match:
        raise HTTPException(status_code=404)

    ctx = await pdf_context(db)
    data = InvoicePdfData(
        invoice_number=t_for(request, "finances.run_preview.pdf_placeholder_number"),
        issued_date=run.issued_date, due_date=run.due_date, subject=run.subject,
        recipient_names=match.recipient_names, recipient_address=match.recipient_address,
        parcel_plot_number=None, parcel_area_sqm=None,
        line_items=[
            InvoicePdfLineItem(
                order_number=li.order_number, name=li.name, description=li.description,
                quantity=li.quantity, unit_price=li.unit_price, line_total=li.line_total,
            ) for li in match.line_items
        ],
        subtotal=match.subtotal, footer_text=run.footer_text, is_preview=True,
    )
    pdf_bytes = render_invoice_pdf(data, **ctx)
    return Response(content=pdf_bytes, media_type="application/pdf")


@router.post("/runs/{run_id}/finalize")
async def run_finalize(run_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    await require_permission(request, db, "finances", "write")

    run = await _get_run_or_404(db, run_id)
    if run.status != InvoiceRunStatus.DRAFT:
        return RedirectResponse(f"/finances/runs/{run_id}", status_code=302)
    if not run.item_definitions:
        return RedirectResponse(
            f"/finances/runs/{run_id}?error={t_for(request, 'finances.errors.no_item_definitions')}",
            status_code=302,
        )

    try:
        await finalize_run(db, run)
    except SequenceCollisionError as e:
        await db.rollback()
        return RedirectResponse(f"/finances/runs/{run_id}?error={e}", status_code=302)
    await db.commit()
    return RedirectResponse(f"/finances/runs/{run_id}?success=1", status_code=302)


@router.post("/runs/{run_id}/deliver")
async def run_deliver(run_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    """Emails every not-yet-emailed invoice in the run (to whichever
    invoice-address resident has email_notifications=True and a
    stored email -- see app/invoice_delivery.py), and uploads every
    not-yet-uploaded one to its parcel's cloud folder if configured.
    Members without email stay for the print bundle (see
    run_print_bundle below) -- this action never marks anything
    printed."""
    await require_permission(request, db, "finances", "write")

    run = await _get_run_or_404(db, run_id)
    if run.status != InvoiceRunStatus.FINALIZED:
        raise HTTPException(status_code=400)

    invoices = await run_invoices(db, run_id)
    ctx = await pdf_context(db)
    provider = await get_cloud_storage_provider(db)

    emailed_count = 0
    uploaded_count = 0
    for invoice in invoices:
        if invoice.emailed_at is None and await send_invoice_email(request, db, invoice, run, ctx):
            emailed_count += 1
        if invoice.uploaded_to_cloud_at is None and await upload_invoice_to_cloud(db, invoice, run, ctx, provider):
            uploaded_count += 1

    await db.commit()
    return RedirectResponse(
        f"/finances/runs/{run_id}?success=1&emailed={emailed_count}&uploaded={uploaded_count}",
        status_code=302,
    )


@router.get("/runs/{run_id}/print-bundle")
async def run_print_bundle(run_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    """Merges the printed letters of the run into one print-ready PDF
    and marks those invoices printed: per address, one letter for the
    people there who don't get email (email notifications on and an
    address on file -- see app/invoice_delivery.py's _split_copy), even
    when someone they live with or a co-tenant elsewhere was emailed
    (issue #396). Filtered by recipient eligibility rather than
    emailed_at so the bundle is correct regardless of whether /deliver
    has run yet -- people eligible for email must never end up printed."""
    await require_permission(request, db, "finances", "write")

    run = await _get_run_or_404(db, run_id)
    items = [
        (invoice, copy)
        for invoice in await run_invoices(db, run_id)
        for copy in await copies_to_print(db, invoice)
    ]
    if not items:
        raise HTTPException(status_code=404, detail=t_for(request, "finances.errors.no_print_invoices"))

    ctx = await pdf_context(db)
    pdf_bytes = await build_print_bundle(db, items, run, ctx)
    await db.commit()

    return Response(
        content=pdf_bytes, media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="invoices_{run.year}_print_bundle.pdf"'},
    )
