"""
Shared insurance business logic, called by both app/routers/insurance.py
(HTML) and app/routers/api_insurance.py (API) -- see ADR 0070.

Pure CRUD/query duplication here, no audit trail or notifications
involved (neither side had either before this extraction) -- unlike
tickets/parcels, there's no hidden data-integrity bug being closed,
just one code path for the same queries and upsert rules instead of two.
"""
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.insurance_utils import household_grouping
from app.models import (
    AccidentInsuranceAdditionalPerson, AccidentInsuranceHouseholdMember, InsuranceConfiguration,
    MemberParcel, ParcelInsurance, PropertyInsurancePackage,
)

# Shared eager-load options for ParcelInsurance, used everywhere a
# calculate_insurance_cost()/insurance_cost_line_items() call needs
# household_members/additional_persons already loaded (both feed the
# accident-insurance cost calc). One place to extend if a relationship
# is ever added, instead of the same tuple duplicated at every call
# site -- missing one is a MissingGreenlet crash under the async
# driver, this module's own recurring pitfall (see docs/module-insurance.md).
PARCEL_INSURANCE_LOAD_OPTIONS = (
    selectinload(ParcelInsurance.property_package),
    selectinload(ParcelInsurance.household_members),
    selectinload(ParcelInsurance.additional_persons),
)


def normalize_insurance_type(insurance_type: Optional[str]) -> str:
    """"property"/"accident" (any case) pass through; anything else --
    None, "", a typo, a hand-edited querystring -- normalizes to "" (both
    types), so the filter condition and the report's <select> always
    agree on what's active instead of silently drifting apart."""
    value = (insurance_type or "").strip().lower()
    return value if value in ("property", "accident") else ""


def insurance_type_condition(insurance_type: Optional[str]):
    """Row filter shared by the evaluation report's HTML view, CSV export,
    and REST endpoint (issue #215). See `normalize_insurance_type`."""
    value = normalize_insurance_type(insurance_type)
    if value == "property":
        return ParcelInsurance.has_property_insurance == True
    if value == "accident":
        return ParcelInsurance.has_accident_insurance == True
    return (
        (ParcelInsurance.has_property_insurance == True) |
        (ParcelInsurance.has_accident_insurance == True)
    )


def normalize_accident_additional_persons_filter(value: Optional[str]) -> str:
    """"with"/"without" (any case) pass through; anything else normalizes
    to "" (no filter) -- same drift-proofing as `normalize_insurance_type`."""
    value = (value or "").strip().lower()
    return value if value in ("with", "without") else ""


async def get_evaluation_parcel_insurances(
    db: AsyncSession, year: int, insurance_type: Optional[str] = None,
    property_package_id: Optional[str] = None, accident_additional_persons: Optional[str] = None,
    *, with_parcel: bool = False,
) -> List[ParcelInsurance]:
    """ParcelInsurance rows for the evaluation report, for a year and
    optional filters:
    - `insurance_type`: "property" or "accident", see `insurance_type_condition`.
    - `property_package_id`: only rows on that exact property package --
      implies property insurance, since `save_parcel_insurance` always
      clears `property_package_id` when property insurance is off.
    - `accident_additional_persons`: "with"/"without" a named additional
      person beyond the household. Applied in Python, not SQL, after the
      fetch -- same "load then filter in memory" precedent as
      `/insurance/parcels`' property_filter/accident_filter, since a
      year's insured-parcel count is small and additional_persons is
      already eager-loaded for cost calculation regardless.

    With `with_parcel` (the HTML view and CSV export, which display/link
    the plot number), also eager-loads `parcel` and sorts by its plot
    number -- the API's plain cost list doesn't need the relationship at
    all, so it's skipped there rather than loaded just to sort.
    """
    options = list(PARCEL_INSURANCE_LOAD_OPTIONS)
    if with_parcel:
        options.append(selectinload(ParcelInsurance.parcel))
    conditions = [ParcelInsurance.year == year, insurance_type_condition(insurance_type)]
    if property_package_id:
        conditions.append(ParcelInsurance.property_package_id == property_package_id)
    result = await db.execute(
        select(ParcelInsurance).options(*options).where(*conditions)
    )
    rows = result.scalars().all()

    additional_persons_filter = normalize_accident_additional_persons_filter(accident_additional_persons)
    if additional_persons_filter == "with":
        rows = [pi for pi in rows if pi.additional_persons]
    elif additional_persons_filter == "without":
        rows = [pi for pi in rows if pi.has_accident_insurance and not pi.additional_persons]

    if with_parcel:
        rows = sorted(rows, key=lambda pi: pi.parcel.plot_number if pi.parcel else "")
    return rows


async def get_configuration(db: AsyncSession, year: int) -> Optional[InsuranceConfiguration]:
    result = await db.execute(
        select(InsuranceConfiguration).where(InsuranceConfiguration.year == year)
    )
    return result.scalar_one_or_none()


async def save_configuration(
    db: AsyncSession, year: int, *, accident_base_amount_eur: Decimal, accident_additional_amount_eur: Decimal,
) -> InsuranceConfiguration:
    configuration = await get_configuration(db, year)
    if configuration:
        configuration.accident_base_amount_eur = accident_base_amount_eur
        configuration.accident_additional_amount_eur = accident_additional_amount_eur
    else:
        configuration = InsuranceConfiguration(
            year=year, accident_base_amount_eur=accident_base_amount_eur,
            accident_additional_amount_eur=accident_additional_amount_eur,
        )
        db.add(configuration)
    await db.flush()
    return configuration


async def get_packages_for_year(db: AsyncSession, year: int) -> List[PropertyInsurancePackage]:
    result = await db.execute(
        select(PropertyInsurancePackage)
        .where(PropertyInsurancePackage.year == year)
        .order_by(PropertyInsurancePackage.sort_order, PropertyInsurancePackage.amount_eur)
    )
    return result.scalars().all()


async def create_package(
    db: AsyncSession, *, year: int, name: str, amount_eur: Decimal, sort_order: int = 0,
) -> PropertyInsurancePackage:
    package = PropertyInsurancePackage(year=year, name=name.strip(), amount_eur=amount_eur, sort_order=sort_order)
    db.add(package)
    await db.flush()
    return package


async def update_package(
    db: AsyncSession, package: PropertyInsurancePackage, *,
    name: str, amount_eur: Optional[Decimal], sort_order: int, year: Optional[int] = None,
) -> PropertyInsurancePackage:
    """`year` is optional and left untouched by default -- the HTML form
    never lets a package's year be edited, only the API's PUT (which
    submits every field) does; preserved as-is rather than unified,
    since it wasn't flagged as drifted business logic, just a
    difference in what each surface exposes."""
    package.name = name.strip()
    package.amount_eur = amount_eur if amount_eur is not None else package.amount_eur
    package.sort_order = sort_order
    if year is not None:
        package.year = year
    await db.flush()
    return package


async def delete_package(db: AsyncSession, package_id: str) -> Optional[PropertyInsurancePackage]:
    result = await db.execute(select(PropertyInsurancePackage).where(PropertyInsurancePackage.id == package_id))
    package = result.scalar_one_or_none()
    if package:
        await db.delete(package)
        await db.flush()
    return package


async def get_parcel_insurance(db: AsyncSession, parcel_id: str, year: int) -> Optional[ParcelInsurance]:
    result = await db.execute(
        select(ParcelInsurance)
        .options(*PARCEL_INSURANCE_LOAD_OPTIONS)
        .where(ParcelInsurance.parcel_id == parcel_id, ParcelInsurance.year == year)
    )
    return result.scalar_one_or_none()


async def get_or_create_parcel_insurance(db: AsyncSession, parcel_id: str, year: int) -> ParcelInsurance:
    pi = await get_parcel_insurance(db, parcel_id, year)
    if pi:
        return pi
    pi = ParcelInsurance(parcel_id=parcel_id, year=year)
    db.add(pi)
    await db.flush()

    # Seed household_members with the parcel's currently-detected
    # household (issue #204): new records default to "whole household
    # covered", individually uncheckable from there instead of the
    # removed all-or-nothing covers_household toggle.
    assignments_result = await db.execute(
        select(MemberParcel).options(selectinload(MemberParcel.member)).where(MemberParcel.parcel_id == parcel_id)
    )
    grouping = household_grouping(assignments_result.scalars().all())
    for member in grouping["household"]:
        db.add(AccidentInsuranceHouseholdMember(parcel_insurance_id=pi.id, member_id=member.id))
    await db.flush()

    # Reload with eagerly-loaded relationships -- without this, a later
    # access to pi.property_package/pi.household_members/pi.additional_persons
    # triggers a synchronous lazy load, which raises "MissingGreenlet"
    # with the async database driver.
    return await get_parcel_insurance(db, parcel_id, year)


async def save_parcel_insurance(
    db: AsyncSession, pi: ParcelInsurance, *,
    has_property_insurance: bool, property_package_id: Optional[str],
    has_accident_insurance: bool, household_member_ids: List[str], additional_person_member_ids: List[str],
) -> ParcelInsurance:
    """Upserts a parcel's insurance status for one year. Fully replaces
    both the household-members and additional-persons lists (simpler
    than diffing, data volume is small) -- same rule for both."""
    pi.has_property_insurance = has_property_insurance
    pi.property_package_id = property_package_id if has_property_insurance else None
    pi.has_accident_insurance = has_accident_insurance

    for hm in list(pi.household_members):
        await db.delete(hm)
    for ap in list(pi.additional_persons):
        await db.delete(ap)
    await db.flush()

    if has_accident_insurance:
        for member_id in household_member_ids:
            db.add(AccidentInsuranceHouseholdMember(parcel_insurance_id=pi.id, member_id=member_id))
        for member_id in additional_person_member_ids:
            db.add(AccidentInsuranceAdditionalPerson(parcel_insurance_id=pi.id, member_id=member_id))

    await db.flush()
    return pi
