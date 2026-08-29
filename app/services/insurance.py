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

from app.models import (
    AccidentInsuranceAdditionalPerson, InsuranceConfiguration, ParcelInsurance,
    PropertyInsurancePackage,
)


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
        .options(
            selectinload(ParcelInsurance.property_package),
            selectinload(ParcelInsurance.additional_persons),
        )
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
    # Reload with eagerly-loaded relationships -- without this, a later
    # access to pi.property_package/pi.additional_persons triggers a
    # synchronous lazy load, which raises "MissingGreenlet" with the
    # async database driver.
    return await get_parcel_insurance(db, parcel_id, year)


async def save_parcel_insurance(
    db: AsyncSession, pi: ParcelInsurance, *,
    has_property_insurance: bool, property_package_id: Optional[str],
    has_accident_insurance: bool, covers_household: bool, additional_person_member_ids: List[str],
) -> ParcelInsurance:
    """Upserts a parcel's insurance status for one year. Fully replaces
    the additional-persons list (simpler than diffing, data volume is
    small) -- same rule on both sides."""
    pi.has_property_insurance = has_property_insurance
    pi.property_package_id = property_package_id if has_property_insurance else None
    pi.has_accident_insurance = has_accident_insurance
    pi.covers_household = covers_household

    for ap in list(pi.additional_persons):
        await db.delete(ap)
    await db.flush()

    if has_accident_insurance:
        for member_id in additional_person_member_ids:
            db.add(AccidentInsuranceAdditionalPerson(parcel_insurance_id=pi.id, member_id=member_id))

    await db.flush()
    return pi
