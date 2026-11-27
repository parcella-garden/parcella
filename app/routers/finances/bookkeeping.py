"""Accounting statement, budget plan, all bookings, bookkeeping categories."""
from fastapi import APIRouter
import csv
import io
import re
from datetime import date
from typing import Optional
from fastapi import Depends, File, Form, HTTPException, Query, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.i18n import t_for
from app.models import FinanceCategory, FinanceCategoryGroup
from app.permissions import require_permission
from app.l10n import parse_decimal
from app.accounting_statement import available_statement_years, compute_cash_accounting_statement
from app.accounting_statement_pdf import render_accounting_statement_pdf
from app.budget_plan import compute_budget_plan, parse_budget_amount, save_budget
from app.bookings import list_bookings
from app.templating import templates
from app.services.finances import budget_year, parse_date_flexible, pdf_context

router = APIRouter()


@router.get("/accounting-statement", response_class=HTMLResponse)
async def accounting_statement_page(
    request: Request, year: Optional[int] = Query(None), db: AsyncSession = Depends(get_db),
):
    user = await require_permission(request, db, "finances", "read")

    available_years = await available_statement_years(db)
    target_year = year if year in available_years else (available_years[0] if available_years else date.today().year)

    statement = await compute_cash_accounting_statement(db, target_year)

    return templates.TemplateResponse(request, "finances/accounting_statement.html", {
        "request": request, "user": user, "statement": statement,
        "available_years": available_years, "year": target_year,
    })


async def _budget_page(request, db, user, year: int, error: Optional[str] = None, entered=None, status_code=200):
    return templates.TemplateResponse(request, "finances/budget.html", {
        "request": request, "user": user, "plan": await compute_budget_plan(db, year),
        "current_year": date.today().year, "error": error, "entered": entered or {},
    }, status_code=status_code)


@router.get("/budget", response_class=HTMLResponse)
async def budget_page(request: Request, year: Optional[int] = Query(None), db: AsyncSession = Depends(get_db)):
    user = await require_permission(request, db, "finances", "read")
    return await _budget_page(request, db, user, budget_year(year))


@router.post("/budget")
async def budget_save(request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_permission(request, db, "finances", "write")
    form = await request.form()
    try:
        year = budget_year(int(form.get("year") or 0))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid year")

    entered = {key[len("amount_"):]: value for key, value in form.items() if key.startswith("amount_")}
    amounts = {}
    for category_id, raw in entered.items():
        try:
            amounts[category_id] = parse_budget_amount(raw)
        except ValueError:
            return await _budget_page(request, db, user, year, error="invalid_amount", entered=entered, status_code=400)
    await save_budget(db, year, amounts)
    await db.commit()
    return RedirectResponse(f"/finances/budget?year={year}&saved=1", status_code=303)


@router.get("/accounting-statement/pdf")
async def accounting_statement_pdf(
    request: Request, year: int = Query(...), db: AsyncSession = Depends(get_db),
):
    await require_permission(request, db, "finances", "read")

    statement = await compute_cash_accounting_statement(db, year)
    ctx = await pdf_context(db)
    pdf_bytes = render_accounting_statement_pdf(statement, **ctx)

    return Response(
        content=pdf_bytes, media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="accounting_statement_{year}.pdf"'},
    )


@router.get("/bookings", response_class=HTMLResponse)
async def bookings_list(request: Request, db: AsyncSession = Depends(get_db)):
    """Issue #180: every invoice payment across the club (incoming and
    outgoing), sorted by date descending, filterable by time frame,
    counterparty, category, description/amount -- see app/bookings.py
    for why this is club-wide rather than the per-account bookings
    list from issue #174."""
    user = await require_permission(request, db, "finances", "read")

    q = request.query_params
    search = q.get("search", "")
    date_from_str = q.get("date_from", "")
    date_to_str = q.get("date_to", "")
    amount_min_str = q.get("amount_min", "")
    amount_max_str = q.get("amount_max", "")
    direction = q.get("direction", "")
    category_id = q.get("category_id", "")

    rows = await list_bookings(
        db,
        date_from=parse_date_flexible(date_from_str) if date_from_str.strip() else None,
        date_to=parse_date_flexible(date_to_str) if date_to_str.strip() else None,
        category_id=category_id.strip() or None,
        search=search,
        amount_min=float(parse_decimal(amount_min_str)) if amount_min_str.strip() and parse_decimal(amount_min_str) is not None else None,
        amount_max=float(parse_decimal(amount_max_str)) if amount_max_str.strip() and parse_decimal(amount_max_str) is not None else None,
        direction=direction.strip() or None,
    )

    categories_result = await db.execute(select(FinanceCategory).order_by(FinanceCategory.code))
    categories = list(categories_result.scalars().all())

    return templates.TemplateResponse(request, "finances/bookings_list.html", {
        "request": request, "user": user, "rows": rows, "categories": categories,
        "search": search, "date_from": date_from_str, "date_to": date_to_str,
        "amount_min": amount_min_str, "amount_max": amount_max_str,
        "direction": direction, "category_id": category_id,
    })


# ---------------------------------------------------------------------------
# Bookkeeping categories (issue #67)
# ---------------------------------------------------------------------------

_CATEGORY_CODE_RE = re.compile(r"^\d{5}$")


def _valid_category_group(value: str) -> Optional[FinanceCategoryGroup]:
    try:
        return FinanceCategoryGroup(value.strip().upper())
    except ValueError:
        return None


@router.get("/categories", response_class=HTMLResponse)
async def category_list(request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_permission(request, db, "finances", "read")

    result = await db.execute(select(FinanceCategory).order_by(FinanceCategory.code))
    categories = list(result.scalars().all())

    return templates.TemplateResponse(request, "finances/category_list.html", {
        "request": request, "user": user, "categories": categories,
        "groups": list(FinanceCategoryGroup),
    })


@router.post("/categories")
async def category_create(
    request: Request,
    code: str = Form(...),
    title: str = Form(...),
    group: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    await require_permission(request, db, "finances", "write")

    code = code.strip()
    parsed_group = _valid_category_group(group)
    if not _CATEGORY_CODE_RE.match(code) or not parsed_group or not title.strip():
        return RedirectResponse(
            f"/finances/categories?error={t_for(request, 'finances.errors.invalid_category')}", status_code=302,
        )

    existing = await db.execute(select(FinanceCategory).where(FinanceCategory.code == code))
    if existing.scalar_one_or_none():
        return RedirectResponse(
            f"/finances/categories?error={t_for(request, 'finances.errors.duplicate_category_code')}", status_code=302,
        )

    db.add(FinanceCategory(code=code, title=title.strip(), group=parsed_group))
    await db.commit()
    return RedirectResponse("/finances/categories?success=1", status_code=302)


@router.post("/categories/{category_id}/edit")
async def category_update(
    category_id: str,
    request: Request,
    code: str = Form(...),
    title: str = Form(...),
    group: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    await require_permission(request, db, "finances", "write")

    result = await db.execute(select(FinanceCategory).where(FinanceCategory.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404)

    code = code.strip()
    parsed_group = _valid_category_group(group)
    if not _CATEGORY_CODE_RE.match(code) or not parsed_group or not title.strip():
        return RedirectResponse(
            f"/finances/categories?error={t_for(request, 'finances.errors.invalid_category')}", status_code=302,
        )

    duplicate = await db.execute(
        select(FinanceCategory).where(FinanceCategory.code == code, FinanceCategory.id != category_id)
    )
    if duplicate.scalar_one_or_none():
        return RedirectResponse(
            f"/finances/categories?error={t_for(request, 'finances.errors.duplicate_category_code')}", status_code=302,
        )

    category.code = code
    category.title = title.strip()
    category.group = parsed_group
    await db.commit()
    return RedirectResponse("/finances/categories?success=1", status_code=302)


@router.post("/categories/{category_id}/delete")
async def category_delete(category_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    await require_permission(request, db, "finances", "delete")

    result = await db.execute(select(FinanceCategory).where(FinanceCategory.id == category_id))
    category = result.scalar_one_or_none()
    if category:
        await db.delete(category)
        await db.commit()
    return RedirectResponse("/finances/categories?success=1", status_code=302)


@router.post("/categories/import")
async def category_import(request: Request, file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    """Bulk-imports categories from a CSV file with a header row
    "code,title,group" -- e.g. a club's own real SKR42-derived chart
    exported from their accounting software. This app never ships
    SKR42 codes itself, see FinanceCategory's docstring."""
    await require_permission(request, db, "finances", "write")

    raw = (await file.read()).decode("utf-8-sig", errors="replace")
    reader = csv.DictReader(io.StringIO(raw))

    existing_result = await db.execute(select(FinanceCategory.code))
    existing_codes = {row[0] for row in existing_result.all()}

    imported = 0
    skipped = 0
    for row in reader:
        code = (row.get("code") or "").strip()
        title = (row.get("title") or "").strip()
        group_value = row.get("group") or ""
        parsed_group = _valid_category_group(group_value)

        if not _CATEGORY_CODE_RE.match(code) or not parsed_group or not title or code in existing_codes:
            skipped += 1
            continue

        db.add(FinanceCategory(code=code, title=title, group=parsed_group))
        existing_codes.add(code)
        imported += 1

    await db.commit()
    return RedirectResponse(
        f"/finances/categories?success=1&imported={imported}&skipped={skipped}", status_code=302,
    )
