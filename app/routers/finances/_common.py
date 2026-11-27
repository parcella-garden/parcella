"""Helpers shared by several finances sub-routers."""
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models import (
    Invoice,
    InvoiceItemDefinition,
    InvoicePayment,
    InvoicePricingMode,
    InvoiceRun,
)


# Pricing modes computed entirely from another module -- unit_price is
# never stored for these (INSURANCE_COST/WORK_HOURS_SHORTFALL pull
# their amount from the insurance/work-hours modules;
# WATER_USAGE/ELECTRICITY_USAGE pull their price from
# MeteringPriceConfiguration, per medium/year -- see
# app/invoice_generation.py's item_quantity_and_price).
_AUTOMATIC_PRICING_MODES = (
    InvoicePricingMode.INSURANCE_COST, InvoicePricingMode.WORK_HOURS_SHORTFALL,
    InvoicePricingMode.WATER_USAGE, InvoicePricingMode.ELECTRICITY_USAGE,
)


def _dedupe_ids(ids: list[str]) -> list[str]:
    """De-duplicates a submitted scope-picker id list while preserving
    order. A resubmitted/retried form (e.g. after a network hiccup, or
    a double form-resubmission on browser back/forward) can otherwise
    include the same parcel/member id twice, which crashes the
    subsequent INSERT with a UniqueViolationError on the
    (definition_id, parcel_id)/(definition_id, member_id) constraint --
    found via a real 500 on /finances/item-templates."""
    return list(dict.fromkeys(ids))


async def _get_run_or_404(db: AsyncSession, run_id: str) -> InvoiceRun:
    result = await db.execute(
        select(InvoiceRun)
        .options(
            selectinload(InvoiceRun.item_definitions).selectinload(InvoiceItemDefinition.parcel_scopes),
            selectinload(InvoiceRun.item_definitions).selectinload(InvoiceItemDefinition.member_scopes),
            selectinload(InvoiceRun.item_definitions).selectinload(InvoiceItemDefinition.category),
        )
        .where(InvoiceRun.id == run_id)
    )
    run = result.scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=404)
    return run


# ---------------------------------------------------------------------------
# Cross-run invoice list, detail, payments (issue #58)
# ---------------------------------------------------------------------------

async def _get_invoice_or_404(db: AsyncSession, invoice_id: str) -> Invoice:
    result = await db.execute(
        select(Invoice)
        .options(
            selectinload(Invoice.line_items), selectinload(Invoice.parcel), selectinload(Invoice.member),
            selectinload(Invoice.payments).selectinload(InvoicePayment.account),
            selectinload(Invoice.reminders),
        )
        .where(Invoice.id == invoice_id)
    )
    invoice = result.scalar_one_or_none()
    if not invoice:
        raise HTTPException(status_code=404)
    return invoice
