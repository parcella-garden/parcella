"""
API router: Insurance -- property insurance packages, configuration,
parcel insurance status, evaluation.

Business logic shared with app/routers/insurance.py (HTML) lives in
app/services/insurance.py (ADR 0070) -- this router owns bearer-token
authentication, the fine-grained permission check (require_api_permission,
Group-based like the HTML side), Pydantic body parsing, and JSON
response serialization.
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import PropertyInsurancePackage, InsuranceConfiguration, ParcelInsurance, Parcel, User
from app.api_auth import require_api_permission
from app.module_flags import require_module
from app.insurance_utils import calculate_insurance_cost
from app.services.insurance import (
    get_configuration, save_configuration, create_package, update_package, delete_package,
    get_parcel_insurance, get_or_create_parcel_insurance, save_parcel_insurance,
    get_evaluation_parcel_insurances,
)
from app.schemas import (
    PropertyInsurancePackageOut, PropertyInsurancePackageCreate,
    InsuranceConfigurationOut, InsuranceConfigurationCreate,
    ParcelInsuranceOut, ParcelInsuranceUpdate, ParcelInsuranceCostOut,
)

router = APIRouter(
    prefix="/api/v1/insurance",
    tags=["API: Insurance"],
    dependencies=[Depends(require_module("insurance"))],
)


# ---------------------------------------------------------------------------
# Property insurance packages
# ---------------------------------------------------------------------------

@router.get("/packages", response_model=List[PropertyInsurancePackageOut], summary="List packages")
async def packages_list(
    year: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission("insurance", "read")),
):
    query = select(PropertyInsurancePackage).order_by(PropertyInsurancePackage.year.desc(), PropertyInsurancePackage.sort_order)
    if year:
        query = query.where(PropertyInsurancePackage.year == year)
    result = await db.execute(query)
    return result.scalars().all()


@router.post(
    "/packages", response_model=PropertyInsurancePackageOut, status_code=status.HTTP_201_CREATED,
    summary="Create package",
)
async def package_create(
    daten: PropertyInsurancePackageCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission("insurance", "write")),
):
    package = await create_package(db, **daten.model_dump())
    await db.commit()
    await db.refresh(package)
    return package


@router.put("/packages/{package_id}", response_model=PropertyInsurancePackageOut, summary="Update package")
async def package_update(
    package_id: str,
    daten: PropertyInsurancePackageCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission("insurance", "write")),
):
    result = await db.execute(select(PropertyInsurancePackage).where(PropertyInsurancePackage.id == package_id))
    package = result.scalar_one_or_none()
    if not package:
        raise HTTPException(status_code=404, detail="Package not found")

    await update_package(
        db, package, name=daten.name, amount_eur=daten.amount_eur,
        sort_order=daten.sort_order, year=daten.year,
    )
    await db.commit()
    await db.refresh(package)
    return package


@router.delete("/packages/{package_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete package")
async def package_delete(
    package_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission("insurance", "delete")),
):
    await delete_package(db, package_id)
    await db.commit()


# ---------------------------------------------------------------------------
# Configuration (accident insurance amounts)
# ---------------------------------------------------------------------------

@router.get(
    "/configuration/{year}", response_model=InsuranceConfigurationOut,
    summary="Retrieve configuration for a year",
)
async def configuration_get(
    year: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission("insurance", "read")),
):
    config = await get_configuration(db, year)
    if not config:
        raise HTTPException(status_code=404, detail=f"No configuration for {year}")
    return config


@router.put(
    "/configuration/{year}", response_model=InsuranceConfigurationOut,
    summary="Set configuration (upsert)",
)
async def configuration_set(
    year: int,
    daten: InsuranceConfigurationCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission("insurance", "write")),
):
    config = await save_configuration(
        db, year,
        accident_base_amount_eur=daten.accident_base_amount_eur,
        accident_additional_amount_eur=daten.accident_additional_amount_eur,
    )
    await db.commit()
    await db.refresh(config)
    return config


# ---------------------------------------------------------------------------
# Parcel insurance status
# ---------------------------------------------------------------------------

def _to_cost_schema(pi: ParcelInsurance, config: Optional[InsuranceConfiguration]) -> ParcelInsuranceCostOut:
    cost = calculate_insurance_cost(pi, config)
    # Validate the base schema first (only real ORM columns), then add
    # the calculated fields -- calling model_validate(pi) directly on
    # the target schema would fail, since property_cost_eur/
    # accident_cost_eur/total_cost_eur aren't real attributes on pi,
    # they have to be calculated first.
    base = ParcelInsuranceOut.model_validate(pi)
    return ParcelInsuranceCostOut(
        **base.model_dump(),
        household_member_ids=[h.member_id for h in pi.household_members],
        additional_person_member_ids=[a.member_id for a in pi.additional_persons],
        property_cost_eur=cost["property_cost"],
        accident_cost_eur=cost["accident_cost"],
        total_cost_eur=cost["total"],
    )


@router.get(
    "/parcels/{parcel_id}/{year}", response_model=ParcelInsuranceCostOut,
    summary="Retrieve insurance status for a parcel",
    description="Returns 404 if no status exists yet for this parcel/year "
                "(unlike the web UI, the API does not create one automatically).",
)
async def insurance_get(
    parcel_id: str,
    year: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission("insurance", "read")),
):
    pi = await get_parcel_insurance(db, parcel_id, year)
    if not pi:
        raise HTTPException(status_code=404, detail="No insurance status for this parcel/year")

    config = await get_configuration(db, year)
    return _to_cost_schema(pi, config)


@router.put(
    "/parcels/{parcel_id}/{year}", response_model=ParcelInsuranceCostOut,
    summary="Set insurance status (upsert)",
    description="Creates the status if it doesn't exist yet, and completely replaces the list of additional persons.",
)
async def insurance_set(
    parcel_id: str,
    year: int,
    daten: ParcelInsuranceUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission("insurance", "write")),
):
    parcel_result = await db.execute(select(Parcel).where(Parcel.id == parcel_id))
    if not parcel_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Parcel not found")

    pi = await get_or_create_parcel_insurance(db, parcel_id, year)
    await save_parcel_insurance(
        db, pi,
        has_property_insurance=daten.has_property_insurance,
        property_package_id=(daten.property_package_id if daten.has_property_insurance else None),
        has_accident_insurance=daten.has_accident_insurance,
        household_member_ids=daten.household_member_ids,
        additional_person_member_ids=daten.additional_person_member_ids,
    )
    await db.commit()

    # Important: pi.property_package may already have been loaded
    # BEFORE property_package_id was set (e.g. during creation above,
    # when the value was still None). Querying again via
    # get_parcel_insurance would, because of SQLAlchemy's identity map,
    # return the same (already "loaded", but now stale) object WITHOUT
    # re-fetching the relationship -- since expire_on_commit=False is
    # set. db.refresh() forces exactly these relationships to be
    # reloaded.
    await db.refresh(pi, attribute_names=["property_package", "household_members", "additional_persons"])

    config = await get_configuration(db, year)
    return _to_cost_schema(pi, config)


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------

@router.get(
    "/evaluation/{year}", response_model=List[ParcelInsuranceCostOut],
    summary="Annual report: all insured parcels with costs",
)
async def evaluation(
    year: int,
    insurance_type: Optional[str] = Query(None, description="Narrow to 'property' or 'accident'; omit for either type"),
    property_package_id: Optional[str] = Query(None, description="Narrow to one property insurance package variant"),
    accident_additional_persons: Optional[str] = Query(None, description="'with' or 'without' a named additional person beyond the household"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_permission("insurance", "read")),
):
    config = await get_configuration(db, year)
    rows = await get_evaluation_parcel_insurances(
        db, year, insurance_type, property_package_id, accident_additional_persons,
    )
    return [_to_cost_schema(pi, config) for pi in rows]
