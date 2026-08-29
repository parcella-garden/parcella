"""
Insurance module router: configuration (packages, amounts), parcel
management, evaluation.
"""
import csv
import io
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Optional

from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.i18n import t_for
from app.models import (
    PropertyInsurancePackage, InsuranceConfiguration, ParcelInsurance,
    Parcel, ParcelStatus, MemberParcel,
)
from app.permissions import require_permission
from app.module_flags import require_module
from app.insurance_utils import household_grouping, calculate_insurance_cost
from app.services.insurance import (
    get_configuration, save_configuration, get_packages_for_year,
    create_package, update_package, delete_package,
    get_or_create_parcel_insurance, save_parcel_insurance,
    PARCEL_INSURANCE_LOAD_OPTIONS,
)

router = APIRouter(
    prefix="/insurance",
    tags=["insurance"],
    dependencies=[Depends(require_module("insurance"))],
)
from app.templating import templates


def _parse_decimal(value: str) -> Optional[Decimal]:
    value = value.strip().replace(",", ".")
    if not value:
        return None
    try:
        return Decimal(value)
    except InvalidOperation:
        return None


# ---------------------------------------------------------------------------
# Overview
# ---------------------------------------------------------------------------

@router.get("/", response_class=HTMLResponse)
async def insurance_overview(
    request: Request,
    year: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
):
    user = await require_permission(request, db, "insurance", "read")
    if not year:
        year = date.today().year

    configuration = await get_configuration(db, year)
    packages = await get_packages_for_year(db, year)

    pi_result = await db.execute(
        select(ParcelInsurance)
        .options(*PARCEL_INSURANCE_LOAD_OPTIONS)
        .where(ParcelInsurance.year == year)
    )
    all_pi = pi_result.scalars().all()

    count_property = sum(1 for pi in all_pi if pi.has_property_insurance)
    count_accident = sum(1 for pi in all_pi if pi.has_accident_insurance)

    total_property = Decimal("0")
    total_accident = Decimal("0")
    for pi in all_pi:
        cost = calculate_insurance_cost(pi, configuration)
        total_property += cost["property_cost"]
        total_accident += cost["accident_cost"]

    years_result = await db.execute(
        select(InsuranceConfiguration.year).order_by(InsuranceConfiguration.year.desc())
    )
    available_years = [r[0] for r in years_result.all()]
    if year not in available_years:
        available_years.insert(0, year)

    return templates.TemplateResponse("insurance/overview.html", {
        "request": request, "user": user, "year": year,
        "available_years": available_years,
        "configuration": configuration, "packages": packages,
        "count_property": count_property, "count_accident": count_accident,
        "total_property": total_property, "total_accident": total_accident,
        "total_overall": total_property + total_accident,
    })


# ---------------------------------------------------------------------------
# Configuration: accident amounts + property insurance packages
# ---------------------------------------------------------------------------

@router.get("/configuration", response_class=HTMLResponse)
async def configuration_page(
    request: Request,
    year: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
):
    user = await require_permission(request, db, "insurance", "read")
    if not year:
        year = date.today().year

    configuration = await get_configuration(db, year)
    packages = await get_packages_for_year(db, year)

    all_years_result = await db.execute(
        select(InsuranceConfiguration.year).order_by(InsuranceConfiguration.year.desc())
    )
    available_years = [r[0] for r in all_years_result.all()]
    if year not in available_years:
        available_years.insert(0, year)

    return templates.TemplateResponse("insurance/configuration.html", {
        "request": request, "user": user, "year": year,
        "available_years": available_years,
        "configuration": configuration, "packages": packages,
        "current_year": date.today().year,
    })


@router.post("/configuration/save")
async def configuration_save(
    request: Request,
    year: int = Form(...),
    accident_base_amount_eur: str = Form(...),
    accident_additional_amount_eur: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    await require_permission(request, db, "insurance", "write")

    base = _parse_decimal(accident_base_amount_eur) or Decimal("0")
    additional = _parse_decimal(accident_additional_amount_eur) or Decimal("0")
    await save_configuration(db, year, accident_base_amount_eur=base, accident_additional_amount_eur=additional)
    await db.commit()
    return RedirectResponse(f"/insurance/configuration?year={year}", status_code=302)


@router.post("/configuration/packages/new")
async def package_create(
    request: Request,
    year: int = Form(...),
    name: str = Form(...),
    amount_eur: str = Form(...),
    sort_order: int = Form(0),
    db: AsyncSession = Depends(get_db),
):
    await require_permission(request, db, "insurance", "write")

    amount = _parse_decimal(amount_eur) or Decimal("0")
    await create_package(db, year=year, name=name, amount_eur=amount, sort_order=sort_order)
    await db.commit()
    return RedirectResponse(f"/insurance/configuration?year={year}", status_code=302)


@router.post("/configuration/packages/{package_id}/edit")
async def package_update(
    package_id: str,
    request: Request,
    name: str = Form(...),
    amount_eur: str = Form(...),
    sort_order: int = Form(0),
    db: AsyncSession = Depends(get_db),
):
    await require_permission(request, db, "insurance", "write")

    result = await db.execute(select(PropertyInsurancePackage).where(PropertyInsurancePackage.id == package_id))
    package = result.scalar_one_or_none()
    if not package:
        raise HTTPException(status_code=404)

    await update_package(
        db, package, name=name, amount_eur=_parse_decimal(amount_eur), sort_order=sort_order,
    )
    await db.commit()
    return RedirectResponse(f"/insurance/configuration?year={package.year}", status_code=302)


@router.post("/configuration/packages/{package_id}/delete")
async def package_delete(
    package_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    await require_permission(request, db, "insurance", "delete")

    package = await delete_package(db, package_id)
    year = package.year if package else date.today().year
    await db.commit()

    return RedirectResponse(f"/insurance/configuration?year={year}", status_code=302)


# ---------------------------------------------------------------------------
# Parcels: list, detail/edit
# ---------------------------------------------------------------------------

def _insurance_parcels_query():
    """WHERE/ORDER BY for the insurance parcels list, shared with the
    detail page's Previous/Next lookup (issue #203) so the two can't
    drift apart -- same reasoning as _filtered_parcels_query in
    app/routers/parcels.py."""
    return select(Parcel).where(Parcel.status == ParcelStatus.ACTIVE).order_by(Parcel.plot_number)


@router.get("/parcels", response_class=HTMLResponse)
async def insurance_parcels_list(
    request: Request,
    year: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
):
    user = await require_permission(request, db, "insurance", "read")
    if not year:
        year = date.today().year

    configuration = await get_configuration(db, year)

    parcels_result = await db.execute(_insurance_parcels_query())
    parcels = parcels_result.scalars().all()

    pi_result = await db.execute(
        select(ParcelInsurance)
        .options(*PARCEL_INSURANCE_LOAD_OPTIONS)
        .where(ParcelInsurance.year == year)
    )
    pi_by_parcel = {pi.parcel_id: pi for pi in pi_result.scalars().all()}

    rows = []
    for p in parcels:
        pi = pi_by_parcel.get(p.id)
        cost = calculate_insurance_cost(pi, configuration) if pi else {
            "property_cost": Decimal("0"), "accident_cost": Decimal("0"), "total": Decimal("0")
        }
        rows.append({"parcel": p, "pi": pi, "cost": cost})

    return templates.TemplateResponse("insurance/parcels_list.html", {
        "request": request, "user": user, "year": year,
        "rows": rows,
    })


@router.get("/parcels/{parcel_id}", response_class=HTMLResponse)
async def insurance_detail(
    parcel_id: str,
    request: Request,
    year: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
):
    user = await require_permission(request, db, "insurance", "read")
    if not year:
        year = date.today().year

    parcel_result = await db.execute(
        select(Parcel)
        .options(selectinload(Parcel.member_assignments).selectinload(MemberParcel.member))
        .where(Parcel.id == parcel_id)
    )
    parcel = parcel_result.scalar_one_or_none()
    if not parcel:
        raise HTTPException(status_code=404, detail=t_for(request, "insurance.errors.parcel_not_found"))

    configuration = await get_configuration(db, year)
    packages = await get_packages_for_year(db, year)
    pi = await get_or_create_parcel_insurance(db, parcel_id, year)

    grouping = household_grouping(parcel.member_assignments)
    household_ids = {h.member_id for h in pi.household_members}
    additional_ids = {a.member_id for a in pi.additional_persons}
    cost = calculate_insurance_cost(pi, configuration)

    # Previous/Next buttons (issue #203): see the identical comment in
    # app/routers/parcels.py's parcel_detail for the reasoning.
    ordered_ids = (await db.scalars(_insurance_parcels_query().with_only_columns(Parcel.id))).all()
    prev_parcel_id = None
    next_parcel_id = None
    if parcel_id in ordered_ids:
        idx = ordered_ids.index(parcel_id)
        if idx > 0:
            prev_parcel_id = ordered_ids[idx - 1]
        if idx < len(ordered_ids) - 1:
            next_parcel_id = ordered_ids[idx + 1]

    return templates.TemplateResponse("insurance/detail.html", {
        "request": request, "user": user, "year": year,
        "parcel": parcel, "pi": pi, "configuration": configuration, "packages": packages,
        "household": grouping["household"], "external": grouping["external"],
        "household_ids": household_ids, "additional_ids": additional_ids, "cost": cost,
        "prev_parcel_id": prev_parcel_id,
        "next_parcel_id": next_parcel_id,
    })


@router.post("/parcels/{parcel_id}/save")
async def insurance_save(
    parcel_id: str,
    request: Request,
    year: int = Form(...),
    has_property_insurance: bool = Form(False),
    property_package_id: str = Form(""),
    has_accident_insurance: bool = Form(False),
    household_members: list[str] = Form([]),
    additional_persons: list[str] = Form([]),
    db: AsyncSession = Depends(get_db),
):
    await require_permission(request, db, "insurance", "write")

    pi = await get_or_create_parcel_insurance(db, parcel_id, year)
    await save_parcel_insurance(
        db, pi,
        has_property_insurance=has_property_insurance,
        property_package_id=(property_package_id.strip() or None),
        has_accident_insurance=has_accident_insurance,
        household_member_ids=household_members,
        additional_person_member_ids=additional_persons,
    )
    await db.commit()
    return RedirectResponse(f"/insurance/parcels/{parcel_id}?year={year}", status_code=302)


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------

@router.get("/evaluation", response_class=HTMLResponse)
async def insurance_evaluation(
    request: Request,
    year: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
):
    user = await require_permission(request, db, "insurance", "read")
    if not year:
        year = date.today().year

    configuration = await get_configuration(db, year)

    pi_result = await db.execute(
        select(ParcelInsurance)
        .options(
            selectinload(ParcelInsurance.parcel),
            *PARCEL_INSURANCE_LOAD_OPTIONS,
        )
        .where(
            ParcelInsurance.year == year,
            (ParcelInsurance.has_property_insurance == True) |
            (ParcelInsurance.has_accident_insurance == True)
        )
    )
    all_pi = pi_result.scalars().all()
    all_pi.sort(key=lambda pi: pi.parcel.plot_number if pi.parcel else "")

    rows = []
    total_overall = Decimal("0")
    for pi in all_pi:
        cost = calculate_insurance_cost(pi, configuration)
        total_overall += cost["total"]
        rows.append({"pi": pi, "cost": cost})

    available_years_result = await db.execute(
        select(InsuranceConfiguration.year).order_by(InsuranceConfiguration.year.desc())
    )
    available_years = [r[0] for r in available_years_result.all()]
    if year not in available_years:
        available_years.insert(0, year)

    return templates.TemplateResponse("insurance/evaluation.html", {
        "request": request, "user": user, "year": year,
        "available_years": available_years,
        "rows": rows, "total_overall": total_overall,
    })


@router.get("/evaluation/csv")
async def insurance_evaluation_csv(
    request: Request,
    year: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
):
    await require_permission(request, db, "insurance", "read")
    if not year:
        year = date.today().year

    configuration = await get_configuration(db, year)

    pi_result = await db.execute(
        select(ParcelInsurance)
        .options(
            selectinload(ParcelInsurance.parcel),
            *PARCEL_INSURANCE_LOAD_OPTIONS,
        )
        .where(
            ParcelInsurance.year == year,
            (ParcelInsurance.has_property_insurance == True) |
            (ParcelInsurance.has_accident_insurance == True)
        )
    )
    all_pi = pi_result.scalars().all()
    all_pi.sort(key=lambda pi: pi.parcel.plot_number if pi.parcel else "")

    output = io.StringIO()
    writer = csv.writer(output, delimiter=";")
    writer.writerow([
        "Parcel", "Sachversicherung", "Sach-Paket", "Sach-Kosten (EUR)",
        "Unfallversicherung", "Zusatzpersonen", "Unfall-Kosten (EUR)", "Gesamt (EUR)"
    ])

    for entry in all_pi:
        pi = entry
        cost = calculate_insurance_cost(pi, configuration)
        writer.writerow([
            pi.parcel.plot_number if pi.parcel else "",
            "Ja" if pi.has_property_insurance else "Nein",
            pi.property_package.name if pi.property_package else "",
            f"{cost['property_cost']:.2f}".replace(".", ","),
            "Ja" if pi.has_accident_insurance else "Nein",
            len(pi.additional_persons),
            f"{cost['accident_cost']:.2f}".replace(".", ","),
            f"{cost['total']:.2f}".replace(".", ","),
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=insurance_{year}.csv"},
    )
