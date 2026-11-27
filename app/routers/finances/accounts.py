"""Bank/cash accounts, their bookings, bank-statement import, manual bookings."""
from fastapi import APIRouter
import base64
import csv
import io
from datetime import date
from urllib.parse import quote as urlquote
from fastapi import Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from app.database import get_db
from app.csv_utils import (
    csv_safe,
    decode_csv_upload,
    guess_column_mapping,
    parse_column_mapping,
    sniff_csv_delimiter,
)
from app.i18n import t_for
from app.security_headers import content_disposition
from app.models import (
    AccountTransaction,
    FinanceAccount,
    FinanceAccountType,
    InvoicePayment,
    Member,
)
from app.permissions import require_permission
from app.l10n import parse_decimal
from app.invoice_matching import best_match_option, find_matching_invoices
from app.templating import templates
from app.services.finances import (
    account_booking_counts,
    account_bookings_filtered,
    create_matched_or_generic_transaction,
    duplicate_flags,
    existing_booking_keys,
    invoice_choice_settled,
    parse_date_flexible,
    parse_finances_mapped_rows,
)

router = APIRouter()


# ---------------------------------------------------------------------------
# Accounts (issue #156): a club's real bank/cash accounts. Purely a tag
# on InvoicePayment (see FinanceAccount's docstring) -- not a ledger.
# ---------------------------------------------------------------------------

@router.get("/accounts", response_class=HTMLResponse)
async def account_list(request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_permission(request, db, "finances", "read")

    result = await db.execute(select(FinanceAccount).order_by(FinanceAccount.name))
    accounts = list(result.scalars().all())

    payment_sums_result = await db.execute(
        select(InvoicePayment.account_id, func.sum(InvoicePayment.amount))
        .where(InvoicePayment.account_id.is_not(None))
        .group_by(InvoicePayment.account_id)
    )
    payment_sums = {account_id: total for account_id, total in payment_sums_result.all()}

    return templates.TemplateResponse(request, "finances/account_list.html", {
        "request": request, "user": user, "accounts": accounts,
        "account_types": list(FinanceAccountType), "payment_sums": payment_sums,
        "booking_counts": await account_booking_counts(db),
    })


@router.post("/accounts")
async def account_create(
    request: Request,
    name: str = Form(...),
    account_type: str = Form(...),
    account_number: str = Form(""),
    note: str = Form(""),
    is_active: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    await require_permission(request, db, "finances", "write")

    if not name.strip():
        return RedirectResponse(
            f"/finances/accounts?error={t_for(request, 'errors.name_required')}", status_code=302,
        )
    try:
        parsed_type = FinanceAccountType(account_type)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid account_type")

    db.add(FinanceAccount(
        name=name.strip(), account_type=parsed_type,
        account_number=account_number.strip() or None, note=note.strip() or None,
        is_active=is_active == "on",
    ))
    await db.commit()
    return RedirectResponse("/finances/accounts?success=1", status_code=302)


@router.post("/accounts/{account_id}/edit")
async def account_update(
    account_id: str,
    request: Request,
    name: str = Form(...),
    account_type: str = Form(...),
    account_number: str = Form(""),
    note: str = Form(""),
    is_active: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    await require_permission(request, db, "finances", "write")

    result = await db.execute(select(FinanceAccount).where(FinanceAccount.id == account_id))
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404)

    if not name.strip():
        return RedirectResponse(
            f"/finances/accounts?error={t_for(request, 'errors.name_required')}", status_code=302,
        )
    try:
        parsed_type = FinanceAccountType(account_type)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid account_type")

    account.name = name.strip()
    account.account_type = parsed_type
    account.account_number = account_number.strip() or None
    account.note = note.strip() or None
    account.is_active = is_active == "on"
    await db.commit()
    return RedirectResponse("/finances/accounts?success=1", status_code=302)


@router.post("/accounts/{account_id}/delete")
async def account_delete(account_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    await require_permission(request, db, "finances", "delete")

    result = await db.execute(select(FinanceAccount).where(FinanceAccount.id == account_id))
    account = result.scalar_one_or_none()
    if account:
        bookings = (await account_booking_counts(db, account.id)).get(account.id, 0)
        if bookings:
            message = t_for(request, "finances.account_list.delete_blocked", name=account.name, count=bookings)
            return RedirectResponse(f"/finances/accounts?error={urlquote(message)}", status_code=303)
        await db.delete(account)
        await db.commit()
    return RedirectResponse("/finances/accounts?success=1", status_code=302)


# ---------------------------------------------------------------------------
# Account bookings (issue #174): a unified, filterable list of
# everything ever booked against one account -- InvoicePayment and
# IncomingInvoicePayment rows (always tied to an invoice) UNION ALL'd
# with AccountTransaction rows (anything else: refunds, purchases,
# bank fees, CSV-imported), see ADR 0059. issue #189: IncomingInvoicePayment
# was missing from this union entirely -- since issue #181 gave it an
# account_id, and issue #188 started actively creating tagged rows via
# invoice matching, any expense payment tagged to an account had been
# silently invisible on that account's own bookings page. All three are
# normalized to the same (id, booking_date, amount, reference,
# description, source, counterparty, invoice_id, incoming_invoice_id)
# shape so search/filtering/pagination only has to be written once,
# against the combined result. counterparty (issue #185) is
# Invoice.recipient_names / IncomingInvoice.sender for invoice rows,
# AccountTransaction.counterparty (manual/CSV, optional) otherwise.
# source is kept internally (it decides whether a row is deletable
# here, and now also drives the "assigned" filter, issue #189) but is
# no longer shown directly in the UI (issue #184).
# ---------------------------------------------------------------------------

BOOKINGS_PAGE_SIZE = 50


def _bookings_filter_params(request: Request) -> dict:
    q = request.query_params
    return {
        "search": q.get("search", ""), "date_from": q.get("date_from", ""), "date_to": q.get("date_to", ""),
        "amount_min": q.get("amount_min", ""), "amount_max": q.get("amount_max", ""),
        "assigned": q.get("assigned", ""),
    }


@router.get("/accounts/{account_id}/bookings", response_class=HTMLResponse)
async def account_bookings(account_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_permission(request, db, "finances", "read")

    result = await db.execute(select(FinanceAccount).where(FinanceAccount.id == account_id))
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404)

    filters = _bookings_filter_params(request)
    bookings, query = account_bookings_filtered(account_id, **filters)
    query = query.order_by(bookings.c.booking_date.desc(), bookings.c.id.desc()).limit(BOOKINGS_PAGE_SIZE)
    rows = (await db.execute(query)).all()

    return templates.TemplateResponse(request, "finances/account_bookings.html", {
        "request": request, "user": user, "account": account, "rows": rows,
        "filters": filters, "page_size": BOOKINGS_PAGE_SIZE,
        "has_more": len(rows) == BOOKINGS_PAGE_SIZE,
        "today": date.today().isoformat(),
    })


@router.get("/accounts/{account_id}/bookings.json")
async def account_bookings_json(
    account_id: str, request: Request, offset: int = 0, db: AsyncSession = Depends(get_db),
):
    """Fetched by the bookings page's infinite scroll for every page
    after the first (which the HTML route above already renders)."""
    await require_permission(request, db, "finances", "read")

    filters = _bookings_filter_params(request)
    bookings, query = account_bookings_filtered(account_id, **filters)
    query = (
        query.order_by(bookings.c.booking_date.desc(), bookings.c.id.desc())
        .limit(BOOKINGS_PAGE_SIZE).offset(offset)
    )
    rows = (await db.execute(query)).all()

    return {
        "rows": [
            {
                "id": r.id,
                "booking_date": r.booking_date.strftime("%d.%m.%Y"),
                "amount": float(r.amount),
                "reference": r.reference,
                "description": r.description,
                "counterparty": r.counterparty,
                "invoice_url": (
                    f"/finances/invoices/{r.invoice_id}" if r.invoice_id
                    else f"/finances/incoming-invoices/{r.incoming_invoice_id}" if r.incoming_invoice_id
                    else None
                ),
            }
            for r in rows
        ],
        "has_more": len(rows) == BOOKINGS_PAGE_SIZE,
    }


@router.get("/accounts/{account_id}/bookings/export.csv")
async def account_bookings_export_csv(account_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    await require_permission(request, db, "finances", "read")

    result = await db.execute(select(FinanceAccount).where(FinanceAccount.id == account_id))
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404)

    filters = _bookings_filter_params(request)
    bookings, query = account_bookings_filtered(account_id, **filters)
    query = query.order_by(bookings.c.booking_date.desc(), bookings.c.id.desc())
    rows = (await db.execute(query)).all()

    output = io.StringIO()
    writer = csv.writer(output, delimiter=";")
    writer.writerow(["Date", "Amount", "Reference", "Description", "Counterparty"])
    for r in rows:
        writer.writerow([
            r.booking_date.strftime("%Y-%m-%d"), f"{float(r.amount):.2f}",
            csv_safe(r.reference or ""), csv_safe(r.description or ""), csv_safe(r.counterparty or ""),
        ])

    filename = f"{account.name.replace(' ', '_')}_bookings.csv"
    return Response(
        content=output.getvalue(), media_type="text/csv",
        headers={"Content-Disposition": content_disposition(filename)},
    )


CSV_IMPORT_TARGET_FIELDS = ["date", "amount", "description", "counterparty", "iban"]
CSV_IMPORT_PREVIEW_ROWS = 5


FINANCES_IMPORT_FIELD_ALIASES = {
    "date": {"date", "datum", "buchungsdatum"},
    "amount": {"amount", "betrag"},
    "description": {"description", "beschreibung", "verwendungszweck", "note"},
    "counterparty": {"counterparty", "sender", "recipient", "empfänger", "auftraggeber", "name"},
    "iban": {"iban"},
}


@router.post(
    "/accounts/{account_id}/bookings/import/preview",
    response_class=HTMLResponse,
)
async def account_bookings_import_preview(
    account_id: str, request: Request,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """Issue #186: "import any CSV of any structure" -- step 1 just
    detects the header row and lets the user map each column to a
    Parcella field (or ignore it) before anything is written. The raw
    CSV is round-tripped to step 2 as a hidden base64 field rather than
    kept in server-side session state, matching this app's stateless-
    request style elsewhere."""
    user = await require_permission(request, db, "finances", "write")

    result = await db.execute(select(FinanceAccount).where(FinanceAccount.id == account_id))
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404)

    content = await file.read()
    text = decode_csv_upload(content)
    delimiter = sniff_csv_delimiter(text)

    reader = csv.reader(io.StringIO(text), delimiter=delimiter)
    rows = list(reader)
    if not rows:
        return RedirectResponse(
            f"/finances/accounts/{account_id}/bookings?error={urlquote(t_for(request, 'finances.account_bookings.csv_empty_error'))}",
            status_code=303,
        )
    headers = [h.strip() for h in rows[0]]
    preview_rows = rows[1:1 + CSV_IMPORT_PREVIEW_ROWS]
    default_mapping = guess_column_mapping(headers, FINANCES_IMPORT_FIELD_ALIASES)

    return templates.TemplateResponse(request, "finances/account_bookings_import_preview.html", {
        "request": request, "user": user, "account": account,
        "headers": headers, "preview_rows": preview_rows,
        "default_mapping": default_mapping, "target_fields": CSV_IMPORT_TARGET_FIELDS,
        "csv_content_b64": base64.b64encode(content).decode("ascii"), "delimiter": delimiter,
    })


@router.post(
    "/accounts/{account_id}/bookings/import/match",
    response_class=HTMLResponse,
)
async def account_bookings_import_match(
    account_id: str, request: Request,
    csv_content_b64: str = Form(...), delimiter: str = Form(";"),
    db: AsyncSession = Depends(get_db),
):
    """Step 2 (issue #188): before creating anything, show each row's
    possible open-invoice matches (by amount, then counterparty name)
    so the user can turn a row into a real payment instead of a
    generic booking."""
    user = await require_permission(request, db, "finances", "write")

    result = await db.execute(select(FinanceAccount).where(FinanceAccount.id == account_id))
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404)

    form = await request.form()
    column_mapping = parse_column_mapping(form, CSV_IMPORT_TARGET_FIELDS)
    if "date" not in column_mapping.values() or "amount" not in column_mapping.values():
        return RedirectResponse(
            f"/finances/accounts/{account_id}/bookings?error={urlquote(t_for(request, 'finances.account_bookings.csv_mapping_required_error'))}",
            status_code=303,
        )

    parsed_rows = parse_finances_mapped_rows(csv_content_b64, delimiter, column_mapping)

    duplicates = duplicate_flags(parsed_rows, await existing_booking_keys(db, account_id))
    row_matches = []
    for row, duplicate in zip(parsed_rows, duplicates):
        matches = await find_matching_invoices(db, row["amount"], row["counterparty"]) if row["valid"] else []
        row_matches.append({
            "row": row, "matches": matches, "duplicate": duplicate,
            # Issue #356: a row that's already on the account is preset to "skip".
            "best": "skip" if duplicate else best_match_option(matches),
        })

    return templates.TemplateResponse(request, "finances/account_bookings_import_match.html", {
        "request": request, "user": user, "account": account, "row_matches": row_matches,
        "csv_content_b64": csv_content_b64, "delimiter": delimiter, "column_mapping": column_mapping,
    })


@router.post("/accounts/{account_id}/bookings/import/finalize")
async def account_bookings_import_finalize(
    account_id: str, request: Request,
    csv_content_b64: str = Form(...), delimiter: str = Form(";"),
    db: AsyncSession = Depends(get_db),
):
    """Step 3: applies each row's chosen match (a real InvoicePayment/
    IncomingInvoicePayment) or creates a generic AccountTransaction
    otherwise -- never auto-matches, only what the user picked in step
    2 (issue #174/ADR 0059's reconciliation-is-out-of-scope stance
    still holds for anything not explicitly confirmed). Also backfills
    a matched member's IBAN (issue #187) when "counterparty" and
    "iban" columns were both mapped."""
    user = await require_permission(request, db, "finances", "write")

    result = await db.execute(select(FinanceAccount).where(FinanceAccount.id == account_id))
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404)

    form = await request.form()
    column_mapping = parse_column_mapping(form, CSV_IMPORT_TARGET_FIELDS)
    if "date" not in column_mapping.values() or "amount" not in column_mapping.values():
        return RedirectResponse(
            f"/finances/accounts/{account_id}/bookings?error={urlquote(t_for(request, 'finances.account_bookings.csv_mapping_required_error'))}",
            status_code=303,
        )
    parsed_rows = parse_finances_mapped_rows(csv_content_b64, delimiter, column_mapping)

    members_by_name: dict = {}
    if "iban" in column_mapping.values() and "counterparty" in column_mapping.values():
        members_result = await db.execute(select(Member))
        for member in members_result.scalars().all():
            forward = f"{member.first_name} {member.last_name}".strip().lower()
            reverse = f"{member.last_name} {member.first_name}".strip().lower()
            members_by_name[forward] = member
            members_by_name[reverse] = member

    # Issue #356: checked again here, not only on the match page. A row
    # that wasn't a duplicate there but is now (a double click, the back
    # button, a second tab) is always skipped; one that already was and
    # the user still chose to import goes in.
    duplicates_now = duplicate_flags(parsed_rows, await existing_booking_keys(db, account_id))

    imported = 0
    skipped = 0
    iban_updated = 0
    matched = 0
    duplicates = 0
    already_paid = 0
    for i, row in enumerate(parsed_rows):
        if not row["valid"]:
            skipped += 1
            continue

        match_choice = form.get(f"match_{i}", "none")
        if duplicates_now[i] and (match_choice == "skip" or not form.get(f"duplicate_{i}")):
            duplicates += 1
            continue
        if match_choice == "skip":  # "Don't import" on a row that isn't a duplicate
            skipped += 1
            continue
        if await invoice_choice_settled(db, match_choice):
            already_paid += 1
            continue
        did_match = await create_matched_or_generic_transaction(
            db, account_id, user.id, row["date"], row["amount"], row["description"], row["counterparty"], match_choice,
            source="csv_import",
        )
        imported += 1
        if did_match:
            matched += 1

        if row["iban"] and row["counterparty"]:
            member = members_by_name.get(row["counterparty"].lower())
            if member and not member.iban:
                member.iban = row["iban"]
                iban_updated += 1

    await db.commit()
    return RedirectResponse(
        f"/finances/accounts/{account_id}/bookings?imported={imported}&skipped={skipped}"
        f"&iban_updated={iban_updated}&matched={matched}&duplicates={duplicates}&already_paid={already_paid}",
        status_code=302,
    )


@router.post("/accounts/{account_id}/bookings/manual/preview", response_class=HTMLResponse)
async def account_bookings_manual_preview(
    account_id: str, request: Request,
    booking_date: str = Form(...), amount: str = Form(...), description: str = Form(""),
    counterparty: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    """Issue #188: before creating a generic booking, show any open
    invoices whose amount (and ideally counterparty name) matches, so
    the user can record this as a real payment instead."""
    user = await require_permission(request, db, "finances", "write")

    result = await db.execute(select(FinanceAccount).where(FinanceAccount.id == account_id))
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404)

    parsed_date = parse_date_flexible(booking_date)
    parsed_amount = parse_decimal(amount)
    if parsed_date is None or parsed_amount is None:
        raise HTTPException(status_code=400)

    matches = await find_matching_invoices(db, parsed_amount, counterparty)

    return templates.TemplateResponse(request, "finances/account_bookings_manual_match.html", {
        "request": request, "user": user, "account": account, "matches": matches,
        "best_match": best_match_option(matches),
        "booking_date": booking_date, "amount": amount, "description": description, "counterparty": counterparty,
    })


@router.post("/accounts/{account_id}/bookings/manual/confirm")
async def account_bookings_manual_confirm(
    account_id: str, request: Request,
    booking_date: str = Form(...), amount: str = Form(...), description: str = Form(""),
    counterparty: str = Form(""), match_choice: str = Form("none"),
    db: AsyncSession = Depends(get_db),
):
    user = await require_permission(request, db, "finances", "write")

    result = await db.execute(select(FinanceAccount).where(FinanceAccount.id == account_id))
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404)

    parsed_date = parse_date_flexible(booking_date)
    parsed_amount = parse_decimal(amount)
    if parsed_date is None or parsed_amount is None:
        raise HTTPException(status_code=400)

    did_match = await create_matched_or_generic_transaction(
        db, account_id, user.id, parsed_date, parsed_amount,
        description.strip(), counterparty.strip(), match_choice,
    )
    await db.commit()
    suffix = "?matched=1" if did_match else ""
    return RedirectResponse(f"/finances/accounts/{account_id}/bookings{suffix}", status_code=302)


@router.post("/accounts/{account_id}/bookings/{transaction_id}/delete")
async def account_bookings_delete_manual(
    account_id: str, transaction_id: str, request: Request, db: AsyncSession = Depends(get_db),
):
    """Only AccountTransaction rows can be deleted here -- an
    InvoicePayment must be removed via its own invoice's payment-delete
    route, since that's the only place that still makes sense as the
    single source of truth for a real invoice payment."""
    await require_permission(request, db, "finances", "delete")

    result = await db.execute(
        select(AccountTransaction).where(
            AccountTransaction.id == transaction_id, AccountTransaction.account_id == account_id,
        )
    )
    transaction = result.scalar_one_or_none()
    if transaction:
        await db.delete(transaction)
        await db.commit()
    return RedirectResponse(f"/finances/accounts/{account_id}/bookings", status_code=302)
