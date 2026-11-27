"""Finances module router: annual invoices (issues #55/#56/#57/#58),
bookkeeping categories (issue #67).

Phase 1 (#56): creating an InvoiceRun and configuring its
InvoiceItemDefinitions. Phase 2 (#57): preview (renders a PDF from
app.invoice_generation's in-memory computation, no DB writes) and
finalize (persists real Invoice/InvoiceLineItem rows with permanent
numbers -- see app/invoice_generation.py's module docstring for why
this is a one-way action). Phase 3 (#58): delivery (email with the PDF
attached, upload to the parcel's cloud folder, a merged print bundle
for anyone not reachable by email -- see app/invoice_delivery.py) and
payment tracking across every finalized run. Categories (#67): optional
bookkeeping codes an item definition can be tagged with, manageable by
hand or via CSV import -- see FinanceCategory's docstring in
app/models/finances.py for why this app doesn't ship real SKR42 codes itself.
Accounts (#156): a club's real bank/cash accounts, a reporting tag on
InvoicePayment with the same "no effect on invoice generation" role as
categories -- see FinanceAccount's docstring.

Split into one sub-router per area (issue #416, ADR 0146); they share
this router's prefix and module guard.
"""
from fastapi import APIRouter, Depends
from app.module_flags import require_module

from app.routers.finances import dashboard, runs, reminders, incoming, bookkeeping, invoices, accounts, item_templates

router = APIRouter(
    prefix="/finances",
    tags=["finances"],
    dependencies=[Depends(require_module("finances"))],
)

for _sub in (dashboard, runs, reminders, incoming, bookkeeping, invoices, accounts, item_templates,):
    router.include_router(_sub.router)
