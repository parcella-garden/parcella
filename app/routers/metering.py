"""
Generic metering module: covers water AND electricity meters via the
same codebase. A MeteringPoint has a "medium" (WATER/ELECTRICITY); the
entire logic (consumption calculation, plausibility checking, readings,
evaluation) is identical regardless of medium.

create_metering_router() is a factory function: it produces a fully
configured router for ONE medium. main.py instantiates it twice (for
/water and /electricity) -- so the logic stays maintained in a single
place instead of being duplicated per medium.
"""
import base64
import csv
import io
import urllib.parse
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Optional, List

from fastapi import APIRouter, Request, Form, Depends, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.csv_utils import (
    csv_safe,
    decode_csv_upload,
    sniff_csv_delimiter,
    guess_column_mapping,
    parse_column_mapping,
    parse_mapped_csv_rows,
)
from app.models import (
    MeteringPoint, MeteringPointType, MeteringMedium, Meter,
    Parcel, ParcelStatus, MeteringPriceConfiguration,
)
from app.permissions import require_permission
from app.i18n import t_for, translate, DEFAULT_LANGUAGE
from app.module_flags import require_module
from app.meter_utils import (
    calculate_consumption, total_consumption_for_type, reading_before_year
)
from app.services.errors import ServiceError
from app.services.metering import (
    create_metering_point, update_metering_point, delete_metering_point, exchange_meter, update_meter,
    record_reading, delete_reading, get_price_configuration_for_year, save_price_configuration_for_year,
)

from app.templating import templates
templates.env.filters["fmt"] = lambda value, places: f"{float(value):.{places}f}"


def _parse_number(value: str, decimal_places: int) -> Optional[Decimal]:
    value = value.strip().replace(",", ".")
    if not value:
        return None
    try:
        parsed_value = Decimal(value)
    except InvalidOperation:
        return None
    quant = Decimal("1") if decimal_places == 0 else Decimal("1." + "0" * decimal_places)
    return parsed_value.quantize(quant)


def _parse_date_flexible(value: str) -> Optional[date]:
    """Accepts ISO (2026-09-18) and the German-locale dotted format
    (18.09.2026) a self-hoster's own spreadsheet is more likely to use
    (see app/routers/finances.py's _parse_date_flexible for the same
    shape, used there for bank-statement CSV import)."""
    value = value.strip()
    if not value:
        return None
    for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d.%m.%y"):
        try:
            return date.fromisoformat(value) if fmt == "%Y-%m-%d" else datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


CSV_IMPORT_PREVIEW_ROWS = 5

POINTS_IMPORT_TARGET_FIELDS = [
    "type", "parcel_number", "label", "meter_number",
    "installed_on", "calibrated_until", "initial_reading",
]
POINTS_IMPORT_FIELD_ALIASES = {
    # Deliberately NOT "art" -- a real export's "Art" column is at least
    # as likely to mean "reading kind" (Jahresablesung/Zwischenablesung,
    # see READINGS_IMPORT_FIELD_ALIASES) as "metering point type", and a
    # wrong guess here isn't cosmetic: every row's Type would fail
    # validation and get skipped. "Typ" is unambiguous, "Art" isn't.
    "type": {"type", "typ"},
    "parcel_number": {"parcel number", "plot number", "parzelle", "parzellennummer", "gartennummer"},
    "label": {"label", "bezeichnung", "name"},
    "meter_number": {"meter number", "zählernummer", "zähler-nr", "zähler nr", "zaehlernummer"},
    "installed_on": {"installed on", "eingebaut am", "installationsdatum"},
    "calibrated_until": {"calibrated until", "geeicht bis", "eichdatum"},
    "initial_reading": {"initial reading", "anfangszählerstand", "anfangsstand", "anfangszaehlerstand"},
}

READINGS_IMPORT_TARGET_FIELDS = [
    "type", "parcel_number", "label", "meter_number",
    "year", "date", "reading", "note",
]
READINGS_IMPORT_FIELD_ALIASES = {
    "type": {"type", "typ"},
    "parcel_number": {"parcel number", "plot number", "parzelle", "parzellennummer", "gartennummer"},
    "label": {"label", "bezeichnung", "name"},
    "meter_number": {"meter number", "zählernummer", "zähler-nr", "zähler nr", "zaehlernummer"},
    "year": {"year", "jahr"},
    "date": {"date", "datum", "ablesedatum"},
    "reading": {"reading", "zählerstand", "zaehlerstand", "stand", "ablesewert"},
    "note": {"note", "notiz", "bemerkung", "kommentar"},
}


def create_metering_router(
    medium: MeteringMedium,
    url_prefix: str,
    modul_name: str,
    medium_label_key: str,
    unit: str,
    icon: str,
    decimal_places: int,
) -> APIRouter:
    """
    Produces a complete router for a metering medium.

    Args:
        medium: MeteringMedium.WATER or MeteringMedium.ELECTRICITY
        url_prefix: e.g. "/water" or "/electricity"
        modul_name: key for the module flag, e.g. "water"/"electricity"
        medium_label_key: translation key for the display name, e.g.
            "metering.medium.water"/"metering.medium.electricity" -- a
            key instead of a ready-made string, because the router is
            instantiated once at startup, but the display language can
            change per request (see app/i18n.py). The (deliberately
            still German) CSV export nonetheless uses a fixed German
            text, see medium_label_de further below.
        unit: e.g. "m³"/"kWh"
        icon: Bootstrap icon class, e.g. "bi-droplet"/"bi-lightning-charge"
        decimal_places: number of decimal places for display/input
    """
    router = APIRouter(
        prefix=url_prefix,
        tags=[modul_name],
        dependencies=[Depends(require_module(modul_name))],
    )

    # German display name, exclusively for the (still German) CSV
    # export -- see medium_label_key above for why the translated
    # display name is NOT resolved here, but per request instead.
    medium_label_de = translate(medium_label_key, DEFAULT_LANGUAGE)

    def medium_label(request: Request) -> str:
        return t_for(request, medium_label_key)

    base_context_without_label = {
        "medium": medium.value,
        "modul_name": modul_name,
        "unit": unit,
        "icon": icon,
        "url_prefix": url_prefix,
        "decimal_places": decimal_places,
    }

    def base_context(request: Request) -> dict:
        return {**base_context_without_label, "medium_label": medium_label(request)}

    async def _load_metering_point_with_details(db: AsyncSession, metering_point_id: str) -> Optional[MeteringPoint]:
        result = await db.execute(
            select(MeteringPoint)
            .options(
                selectinload(MeteringPoint.parcel),
                selectinload(MeteringPoint.meters).selectinload(Meter.readings),
            )
            .where(MeteringPoint.id == metering_point_id, MeteringPoint.medium == medium)
        )
        return result.scalar_one_or_none()

    async def _load_all_metering_points(db: AsyncSession) -> List[MeteringPoint]:
        result = await db.execute(
            select(MeteringPoint)
            .options(
                selectinload(MeteringPoint.parcel),
                selectinload(MeteringPoint.meters).selectinload(Meter.readings),
            )
            .where(MeteringPoint.medium == medium)
        )
        return result.scalars().all()

    async def _load_parcels_without_metering_point(db: AsyncSession, all_points: List[MeteringPoint]) -> List[Parcel]:
        """ACTIVE/TERMINATED parcels with no PARCEL-type metering point for
        this medium (issue #223) -- a TERMINATED parcel can still need one
        (#219), DELETED stays excluded, same convention as the "new
        metering point" form's own parcel dropdown. Shared by the overview
        stat tile and the metering-points list's `?missing=1` filter so
        the two can't drift apart."""
        parcel_ids_with_point = [
            p.parcel_id for p in all_points if p.type == MeteringPointType.PARCEL and p.parcel_id
        ]
        query = select(Parcel).where(Parcel.status.in_([ParcelStatus.ACTIVE, ParcelStatus.TERMINATED]))
        if parcel_ids_with_point:
            query = query.where(~Parcel.id.in_(parcel_ids_with_point))
        result = await db.execute(query.order_by(Parcel.plot_number))
        return result.scalars().all()

    def _metering_point_sort_key(a: MeteringPoint):
        # Same ordering as the metering-points list page (issue #212's
        # Previous/Next walks that same order, mirroring the
        # members/parcels detail pages -- ADR 0075).
        if a.type == MeteringPointType.MAIN_METER:
            return (0, "")
        if a.type == MeteringPointType.PARCEL:
            return (1, a.parcel.plot_number if a.parcel else "")
        return (2, a.label or "")

    # -----------------------------------------------------------------
    # Overview
    # -----------------------------------------------------------------

    @router.get("/", response_class=HTMLResponse)
    async def overview(
        request: Request,
        year: Optional[int] = None,
        db: AsyncSession = Depends(get_db),
    ):
        user = await require_permission(request, db, modul_name, "read")
        if not year:
            year = date.today().year

        all_points = await _load_all_metering_points(db)
        main_meters = [a for a in all_points if a.type == MeteringPointType.MAIN_METER]
        parcels = [a for a in all_points if a.type == MeteringPointType.PARCEL]
        club_points = [a for a in all_points if a.type == MeteringPointType.CLUB]

        main_consumption = total_consumption_for_type(main_meters, year)
        parcel_consumption = total_consumption_for_type(parcels, year)
        club_consumption = total_consumption_for_type(club_points, year)

        warning = None
        if main_consumption > 0 and (parcel_consumption + club_consumption) > main_consumption:
            warning = t_for(
                request, "metering.errors.overall_plausibility_overview",
                parcels=parcel_consumption, club=club_consumption, main=main_consumption, unit=unit, year=year,
            )

        open_readings_count = 0
        for a in all_points:
            z = a.current_meter
            if z and not any(zs.year == year for zs in z.readings):
                open_readings_count += 1

        available_years = sorted({
            zs.year for a in all_points for z in a.meters for zs in z.readings
        }, reverse=True)
        if year not in available_years:
            available_years.insert(0, year)

        parcels_without_metering_point = await _load_parcels_without_metering_point(db, all_points)

        return templates.TemplateResponse("metering/overview.html", {
            **base_context(request),
            "request": request, "user": user, "year": year,
            "available_years": available_years,
            "main_meter_count": len(main_meters),
            "parcel_count": len(parcels),
            "club_count": len(club_points),
            "main_consumption": main_consumption,
            "parcel_consumption": parcel_consumption,
            "club_consumption": club_consumption,
            "warning": warning,
            "open_readings": open_readings_count,
            "parcels_without_metering_point": parcels_without_metering_point,
        })

    # -----------------------------------------------------------------
    # MeteringPoints: list, create, detail, edit, delete
    # -----------------------------------------------------------------

    @router.get("/metering-points", response_class=HTMLResponse)
    async def metering_points_list(
        request: Request, type: Optional[str] = None, missing: Optional[str] = None,
        db: AsyncSession = Depends(get_db),
    ):
        user = await require_permission(request, db, modul_name, "read")
        all_points = await _load_all_metering_points(db)

        parcels_without_metering_point = None
        if missing:
            parcels_without_metering_point = await _load_parcels_without_metering_point(db, all_points)
            filtered_points = []
        else:
            filtered_points = all_points
            if type in {t.value for t in MeteringPointType}:
                filtered_points = [p for p in filtered_points if p.type.value == type]
            filtered_points.sort(key=_metering_point_sort_key)

        return templates.TemplateResponse("metering/metering_points_list.html", {
            **base_context(request),
            "request": request, "user": user,
            "metering_points": filtered_points, "MeteringPointType": MeteringPointType,
            "year": date.today().year,
            # Overview stat tiles link here with a filter (issue #224) --
            # `type_filter` narrows to one MeteringPointType, `missing`
            # switches the page to the parcels-without-a-point view
            # instead (there's no MeteringPoint row to filter to for those).
            "type_filter": None if missing else type,
            "missing_filter": bool(missing),
            "parcels_without_metering_point": parcels_without_metering_point,
        })

    @router.get("/metering-points/new", response_class=HTMLResponse)
    async def metering_point_new_page(
        request: Request, parcel_id: Optional[str] = None, db: AsyncSession = Depends(get_db),
    ):
        user = await require_permission(request, db, modul_name, "write")
        result = await db.execute(
            select(Parcel)
            .where(Parcel.status.in_([ParcelStatus.ACTIVE, ParcelStatus.TERMINATED]))
            .order_by(Parcel.plot_number)
        )
        all_parcels = result.scalars().all()

        return templates.TemplateResponse("metering/metering_point_form.html", {
            **base_context(request),
            "request": request, "user": user,
            "all_parcels": all_parcels, "today": date.today().isoformat(),
            # Pre-selects the parcel when linked from the metering-points
            # list's "missing" filter (issue #224) -- otherwise that list
            # is a dead end that just repeats what staff already knows.
            "preselected_parcel_id": parcel_id,
        })

    @router.post("/metering-points/new")
    async def metering_point_create(
        request: Request,
        type: str = Form(...),
        parcel_id: str = Form(""),
        label: str = Form(""),
        notes: str = Form(""),
        number: str = Form(...),
        calibrated_until: str = Form(""),
        installed_at: str = Form(""),
        initial_reading: str = Form("0"),
        db: AsyncSession = Depends(get_db),
    ):
        await require_permission(request, db, modul_name, "write")

        metering_point = await create_metering_point(
            db, medium,
            type=type, parcel_id=(parcel_id.strip() or None), label=(label.strip() or None),
            notes=(notes.strip() or None), number=number.strip(),
            calibrated_until=(int(calibrated_until) if calibrated_until.strip() else None),
            installed_at=(date.fromisoformat(installed_at) if installed_at.strip() else None),
            initial_reading=(_parse_number(initial_reading, decimal_places) or Decimal("0")),
        )
        await db.commit()
        return RedirectResponse(f"{url_prefix}/metering-points/{metering_point.id}", status_code=302)

    @router.get("/metering-points/{metering_point_id}", response_class=HTMLResponse)
    async def metering_point_detail(
        metering_point_id: str,
        request: Request,
        db: AsyncSession = Depends(get_db),
    ):
        user = await require_permission(request, db, modul_name, "read")
        metering_point = await _load_metering_point_with_details(db, metering_point_id)
        if not metering_point:
            raise HTTPException(status_code=404, detail=t_for(request, "metering.errors.point_not_found", medium=medium_label(request)))

        current_meter = metering_point.current_meter
        former_meters = sorted(
            [z for z in metering_point.meters if not z.is_active],
            key=lambda z: z.removed_at or date.min,
            reverse=True,
        )

        readings_with_consumption = []
        if current_meter:
            for z in sorted(current_meter.readings, key=lambda z: z.year, reverse=True):
                readings_with_consumption.append({
                    "reading": z,
                    "consumption": calculate_consumption(current_meter, z.year),
                })

        # Previous/Next buttons (issue #212): walk the same order the
        # metering-points list page shows, mirroring members/parcels
        # detail pages (ADR 0075). The list has no search/filter, so
        # unlike members/parcels there's no query string to preserve.
        all_points = await _load_all_metering_points(db)
        ordered_ids = [a.id for a in sorted(all_points, key=_metering_point_sort_key)]
        prev_metering_point_id = None
        next_metering_point_id = None
        if metering_point_id in ordered_ids:
            idx = ordered_ids.index(metering_point_id)
            if idx > 0:
                prev_metering_point_id = ordered_ids[idx - 1]
            if idx < len(ordered_ids) - 1:
                next_metering_point_id = ordered_ids[idx + 1]

        return templates.TemplateResponse("metering/metering_point_detail.html", {
            **base_context(request),
            "request": request, "user": user,
            "metering_point": metering_point,
            "current_meter": current_meter,
            "former_meters": former_meters,
            "readings_with_consumption": readings_with_consumption,
            "today": date.today().isoformat(),
            "current_year": date.today().year,
            "MeteringPointType": MeteringPointType,
            "prev_metering_point_id": prev_metering_point_id,
            "next_metering_point_id": next_metering_point_id,
        })

    @router.post("/metering-points/{metering_point_id}/edit")
    async def metering_point_update(
        metering_point_id: str,
        request: Request,
        label: str = Form(""),
        notes: str = Form(""),
        db: AsyncSession = Depends(get_db),
    ):
        await require_permission(request, db, modul_name, "write")
        result = await db.execute(
            select(MeteringPoint).where(MeteringPoint.id == metering_point_id, MeteringPoint.medium == medium)
        )
        metering_point = result.scalar_one_or_none()
        if not metering_point:
            raise HTTPException(status_code=404)

        await update_metering_point(db, metering_point, label=(label.strip() or None), notes=(notes.strip() or None))
        await db.commit()
        return RedirectResponse(f"{url_prefix}/metering-points/{metering_point_id}", status_code=302)

    @router.post("/metering-points/{metering_point_id}/delete")
    async def metering_point_delete(
        metering_point_id: str,
        request: Request,
        db: AsyncSession = Depends(get_db),
    ):
        await require_permission(request, db, modul_name, "delete")
        result = await db.execute(
            select(MeteringPoint).where(MeteringPoint.id == metering_point_id, MeteringPoint.medium == medium)
        )
        metering_point = result.scalar_one_or_none()
        if metering_point:
            await delete_metering_point(db, metering_point)
            await db.commit()
        return RedirectResponse(f"{url_prefix}/metering-points", status_code=302)

    # -----------------------------------------------------------------
    # MeteringPoints: CSV export/import (issue #225) -- covers the
    # metering point's and its current meter's static attributes
    # (type, parcel number, meter number, installed on, calibrated
    # until, initial reading), not readings -- see the readings
    # export/import further below for those, scoped by year.
    # -----------------------------------------------------------------

    @router.get("/metering-points/export/csv")
    async def metering_points_export_csv(request: Request, db: AsyncSession = Depends(get_db)):
        await require_permission(request, db, modul_name, "read")
        all_points = await _load_all_metering_points(db)

        output = io.StringIO()
        writer = csv.writer(output, delimiter=";")
        writer.writerow([
            "Type", "Parcel number", "Label", "Meter number",
            "Installed on", "Calibrated until", "Initial reading",
        ])

        for a in sorted(all_points, key=_metering_point_sort_key):
            z = a.current_meter
            writer.writerow([
                a.type.value,
                a.parcel.plot_number if a.parcel else "",
                csv_safe(a.label or ""),
                csv_safe(z.number if z else ""),
                z.installed_at.isoformat() if z and z.installed_at else "",
                z.calibrated_until if z and z.calibrated_until else "",
                f"{z.initial_reading:.{decimal_places}f}".replace(".", ",") if z else "",
            ])

        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={modul_name}_metering_points.csv"},
        )

    @router.post("/metering-points/import/preview", response_class=HTMLResponse)
    async def metering_points_import_preview(
        request: Request,
        file: UploadFile = File(...),
        db: AsyncSession = Depends(get_db),
    ):
        """Step 1 of the column-mapping wizard (ADR 0062's pattern,
        generalized here -- see docs/ADR/0083): detects the header row
        and lets the user map each column to a Parcella field before
        anything is written. The raw CSV round-trips to step 2 as a
        hidden base64 field, not server-side session state."""
        await require_permission(request, db, modul_name, "write")

        content = await file.read()
        text = decode_csv_upload(content)
        delimiter = sniff_csv_delimiter(text)

        reader = csv.reader(io.StringIO(text), delimiter=delimiter)
        rows = list(reader)
        if not rows:
            message = t_for(request, "metering.points_list.csv_empty_error")
            return RedirectResponse(
                f"{url_prefix}/metering-points?error={urllib.parse.quote(message)}",
                status_code=303,
            )
        headers = [h.strip() for h in rows[0]]
        preview_rows = rows[1:1 + CSV_IMPORT_PREVIEW_ROWS]
        default_mapping = guess_column_mapping(headers, POINTS_IMPORT_FIELD_ALIASES)

        return templates.TemplateResponse("metering/metering_points_import_preview.html", {
            "request": request, **base_context(request),
            "headers": headers, "preview_rows": preview_rows,
            "default_mapping": default_mapping, "target_fields": POINTS_IMPORT_TARGET_FIELDS,
            "csv_content_b64": base64.b64encode(content).decode("ascii"), "delimiter": delimiter,
        })

    @router.post("/metering-points/import/finalize")
    async def metering_points_import_finalize(
        request: Request,
        csv_content_b64: str = Form(...), delimiter: str = Form(";"),
        db: AsyncSession = Depends(get_db),
    ):
        """Step 2: applies the confirmed column mapping and runs the
        same row logic the old fixed-header importer used -- dedup key,
        parcel lookup, date/number parsing are unchanged, just fed from
        the mapped dict instead of a literal DictReader header lookup."""
        await require_permission(request, db, modul_name, "write")

        form = await request.form()
        column_mapping = parse_column_mapping(form, POINTS_IMPORT_TARGET_FIELDS)
        if not column_mapping:
            message = t_for(request, "metering.points_list.csv_mapping_required_error")
            return RedirectResponse(
                f"{url_prefix}/metering-points?error={urllib.parse.quote(message)}",
                status_code=303,
            )
        # Type isn't required to be mapped -- most real-world exports for
        # a single medium are entirely PARCEL rows and don't carry a Type
        # column at all (issue #227's motivating file: just parcel
        # number/meter number/calibrated until/initial reading). Only a
        # row where Type *is* mapped but left blank counts as invalid.
        type_mapped = "type" in column_mapping.values()
        rows = parse_mapped_csv_rows(csv_content_b64, delimiter, column_mapping)

        all_points = await _load_all_metering_points(db)
        # Same identity used on export: (type, parcel number) for PARCEL
        # rows, (type, label) for MAIN_METER/CLUB -- lets a re-import of
        # an unchanged export be a no-op instead of creating duplicates.
        existing_keys = set()
        for a in all_points:
            if a.type == MeteringPointType.PARCEL and a.parcel:
                existing_keys.add((a.type.value, a.parcel.plot_number.strip().upper()))
            elif a.label:
                existing_keys.add((a.type.value, a.label.strip().upper()))

        created = 0
        skipped = 0
        invalid_type = 0
        parcel_not_found = 0
        skip_details = []
        reason_exists = t_for(request, "metering.points_list.csv_import_skip_reason_exists")
        reason_invalid_type = t_for(request, "metering.points_list.csv_import_skip_reason_invalid_type")
        reason_parcel_not_found = t_for(request, "metering.points_list.csv_import_skip_reason_parcel_not_found")

        for row_number, values in enumerate(rows, start=2):
            parcel_number = (values.get("parcel_number") or "").strip().upper()
            label = (values.get("label") or "").strip()
            identifier = parcel_number or label or f"#{row_number}"

            type_str = (values.get("type") or "").strip().upper()
            if not type_str and not type_mapped:
                type_str = MeteringPointType.PARCEL.value
            if type_str not in {t.value for t in MeteringPointType}:
                invalid_type += 1
                skip_details.append(f"{identifier}: {reason_invalid_type}")
                continue
            point_type = MeteringPointType(type_str)

            parcel_id = None
            if point_type == MeteringPointType.PARCEL:
                if not parcel_number:
                    parcel_not_found += 1
                    skip_details.append(f"{identifier}: {reason_parcel_not_found}")
                    continue
                result = await db.execute(select(Parcel).where(Parcel.plot_number == parcel_number))
                parcel = result.scalar_one_or_none()
                if not parcel:
                    parcel_not_found += 1
                    skip_details.append(f"{identifier}: {reason_parcel_not_found}")
                    continue
                parcel_id = parcel.id
                key = (point_type.value, parcel_number)
            else:
                key = (point_type.value, label.strip().upper())

            if key in existing_keys and (point_type == MeteringPointType.PARCEL or label):
                skipped += 1
                skip_details.append(f"{identifier}: {reason_exists}")
                continue

            calibrated_until_str = (values.get("calibrated_until") or "").strip()
            installed_at = _parse_date_flexible(values.get("installed_on") or "")
            initial_reading = _parse_number(values.get("initial_reading") or "", decimal_places) or Decimal("0")

            await create_metering_point(
                db, medium,
                type=point_type.value, parcel_id=parcel_id, label=(label or None),
                number=(values.get("meter_number") or "").strip(),
                calibrated_until=(int(calibrated_until_str) if calibrated_until_str else None),
                installed_at=installed_at, initial_reading=initial_reading,
            )
            existing_keys.add(key)
            created += 1

        await db.commit()

        message = t_for(
            request, "metering.points_list.csv_import_summary",
            created=created, skipped=skipped,
        )
        if invalid_type:
            message += t_for(request, "metering.points_list.csv_import_invalid_type", count=invalid_type)
        if parcel_not_found:
            message += t_for(request, "metering.points_list.csv_import_parcel_not_found", count=parcel_not_found)
        if skip_details:
            message += " – " + " | ".join(skip_details[:3])
            if len(skip_details) > 3:
                message += t_for(request, "metering.points_list.csv_import_more_skipped", count=len(skip_details) - 3)

        return RedirectResponse(
            f"{url_prefix}/metering-points?message={urllib.parse.quote(message)}",
            status_code=302,
        )

    # -----------------------------------------------------------------
    # Edit current meter (in place -- correcting a data-entry mistake,
    # not a physical swap; see "Swap meter" below for that)
    # -----------------------------------------------------------------

    @router.post("/metering-points/{metering_point_id}/meter/edit")
    async def meter_edit(
        metering_point_id: str,
        request: Request,
        number: str = Form(...),
        installed_at: str = Form(""),
        calibrated_until: str = Form(""),
        initial_reading: str = Form("0"),
        db: AsyncSession = Depends(get_db),
    ):
        await require_permission(request, db, modul_name, "write")
        metering_point = await _load_metering_point_with_details(db, metering_point_id)
        if not metering_point:
            raise HTTPException(status_code=404)

        current_meter = metering_point.current_meter
        if not current_meter:
            raise HTTPException(status_code=404, detail=t_for(request, "metering.errors.no_active_meter"))

        await update_meter(
            db, current_meter,
            number=number.strip(),
            installed_at=(date.fromisoformat(installed_at) if installed_at.strip() else None),
            calibrated_until=(int(calibrated_until) if calibrated_until.strip() else None),
            initial_reading=(_parse_number(initial_reading, decimal_places) or Decimal("0")),
        )
        await db.commit()
        return RedirectResponse(f"{url_prefix}/metering-points/{metering_point_id}", status_code=302)

    # -----------------------------------------------------------------
    # Swap meter
    # -----------------------------------------------------------------

    @router.post("/metering-points/{metering_point_id}/meter/exchange")
    async def meter_exchange(
        metering_point_id: str,
        request: Request,
        new_number: str = Form(...),
        removed_at: str = Form(...),
        installed_at: str = Form(...),
        calibrated_until: str = Form(""),
        initial_reading: str = Form("0"),
        db: AsyncSession = Depends(get_db),
    ):
        await require_permission(request, db, modul_name, "write")
        metering_point = await _load_metering_point_with_details(db, metering_point_id)
        if not metering_point:
            raise HTTPException(status_code=404)

        await exchange_meter(
            db, metering_point,
            new_number=new_number.strip(), removed_at=date.fromisoformat(removed_at),
            installed_at=date.fromisoformat(installed_at),
            calibrated_until=(int(calibrated_until) if calibrated_until.strip() else None),
            initial_reading=(_parse_number(initial_reading, decimal_places) or Decimal("0")),
        )
        await db.commit()
        return RedirectResponse(f"{url_prefix}/metering-points/{metering_point_id}", status_code=302)

    # -----------------------------------------------------------------
    # Meter readings: create, delete
    # -----------------------------------------------------------------

    @router.post("/metering-points/{metering_point_id}/readings/new")
    async def reading_create(
        metering_point_id: str,
        request: Request,
        year: int = Form(...),
        date_value: str = Form(..., alias="date"),
        reading: str = Form(...),
        note: str = Form(""),
        return_url: str = Form(f"{url_prefix}/readings"),
        db: AsyncSession = Depends(get_db),
    ):
        user = await require_permission(request, db, modul_name, "write")
        metering_point = await _load_metering_point_with_details(db, metering_point_id)
        if not metering_point:
            raise HTTPException(status_code=404)

        meter = metering_point.current_meter
        if not meter:
            raise HTTPException(status_code=400, detail=t_for(request, "metering.errors.no_active_meter"))

        new_reading = _parse_number(reading, decimal_places)
        if new_reading is None:
            message = urllib.parse.quote(t_for(request, "metering.errors.invalid_reading"))
            return RedirectResponse(f"{return_url}?error={message}", status_code=302)

        try:
            await record_reading(
                db, meter, year=year, reading_date=date.fromisoformat(date_value),
                reading=new_reading, note=(note.strip() or None), recorded_by_id=user.id,
            )
        except ServiceError as e:
            error = t_for(request, e.key, **e.params)
            return RedirectResponse(f"{return_url}?error={urllib.parse.quote(error)}", status_code=302)

        await db.commit()
        return RedirectResponse(return_url, status_code=302)

    @router.post("/readings/{reading_id}/delete")
    async def reading_delete(
        reading_id: str,
        request: Request,
        db: AsyncSession = Depends(get_db),
    ):
        await require_permission(request, db, modul_name, "delete")
        metering_point_id = await delete_reading(db, reading_id)
        if metering_point_id:
            await db.commit()

        if metering_point_id:
            return RedirectResponse(f"{url_prefix}/metering-points/{metering_point_id}", status_code=302)
        return RedirectResponse(f"{url_prefix}/metering-points", status_code=302)

    # -----------------------------------------------------------------
    # Readings (mobile-friendly bulk entry)
    # -----------------------------------------------------------------

    @router.get("/readings", response_class=HTMLResponse)
    async def readings_list(
        request: Request,
        year: Optional[int] = None,
        error: Optional[str] = None,
        db: AsyncSession = Depends(get_db),
    ):
        user = await require_permission(request, db, modul_name, "read")
        if not year:
            year = date.today().year

        all_points = await _load_all_metering_points(db)

        def prepare_rows(type):
            filtered = [a for a in all_points if a.type == type]
            rows = []
            for a in filtered:
                z = a.current_meter
                if not z:
                    continue
                current_reading = next((zs for zs in z.readings if zs.year == year), None)
                rows.append({
                    "metering_point": a,
                    "meter": z,
                    "previous_year_value": reading_before_year(
                        z, year, exclude_id=current_reading.id if current_reading else None
                    ),
                    "entry": current_reading,
                })
            return rows

        main_meter_rows = prepare_rows(MeteringPointType.MAIN_METER)
        parcel_rows = sorted(
            prepare_rows(MeteringPointType.PARCEL),
            key=lambda z: z["metering_point"].parcel.plot_number if z["metering_point"].parcel else ""
        )
        club_rows = prepare_rows(MeteringPointType.CLUB)

        return templates.TemplateResponse("metering/readings_list.html", {
            **base_context(request),
            "request": request, "user": user, "year": year,
            "main_meter_rows": main_meter_rows,
            "parcel_rows": parcel_rows,
            "club_rows": club_rows,
            "error": error,
            "today": date.today().isoformat(),
        })

    # -----------------------------------------------------------------
    # Readings: CSV export/import (issue #225) -- scoped by year, one
    # row per metering point's current meter, same shape as the
    # existing /readings page and /evaluation/csv export. Import goes
    # through record_reading() so a bulk-loaded reading is subject to
    # the exact same monotonicity check as one entered by hand.
    # -----------------------------------------------------------------

    @router.get("/readings/export/csv")
    async def readings_export_csv(
        request: Request,
        year: Optional[int] = None,
        db: AsyncSession = Depends(get_db),
    ):
        await require_permission(request, db, modul_name, "read")
        if not year:
            year = date.today().year

        all_points = await _load_all_metering_points(db)

        output = io.StringIO()
        writer = csv.writer(output, delimiter=";")
        writer.writerow([
            "Type", "Parcel number", "Label", "Meter number",
            "Year", "Date", "Reading", "Note",
        ])

        for a in sorted(all_points, key=_metering_point_sort_key):
            z = a.current_meter
            if not z:
                continue
            entry = next((zs for zs in z.readings if zs.year == year), None)
            writer.writerow([
                a.type.value,
                a.parcel.plot_number if a.parcel else "",
                csv_safe(a.label or ""),
                csv_safe(z.number),
                year,
                entry.date.isoformat() if entry else "",
                f"{entry.reading:.{decimal_places}f}".replace(".", ",") if entry else "",
                csv_safe(entry.note or "") if entry else "",
            ])

        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={modul_name}_readings_{year}.csv"},
        )

    @router.post("/readings/import/preview", response_class=HTMLResponse)
    async def readings_import_preview(
        request: Request,
        file: UploadFile = File(...),
        db: AsyncSession = Depends(get_db),
    ):
        await require_permission(request, db, modul_name, "write")

        content = await file.read()
        text = decode_csv_upload(content)
        delimiter = sniff_csv_delimiter(text)

        reader = csv.reader(io.StringIO(text), delimiter=delimiter)
        rows = list(reader)
        if not rows:
            message = t_for(request, "metering.readings_list.csv_empty_error")
            return RedirectResponse(
                f"{url_prefix}/readings?error={urllib.parse.quote(message)}",
                status_code=303,
            )
        headers = [h.strip() for h in rows[0]]
        preview_rows = rows[1:1 + CSV_IMPORT_PREVIEW_ROWS]
        default_mapping = guess_column_mapping(headers, READINGS_IMPORT_FIELD_ALIASES)

        return templates.TemplateResponse("metering/readings_import_preview.html", {
            "request": request, **base_context(request),
            "headers": headers, "preview_rows": preview_rows,
            "default_mapping": default_mapping, "target_fields": READINGS_IMPORT_TARGET_FIELDS,
            "csv_content_b64": base64.b64encode(content).decode("ascii"), "delimiter": delimiter,
        })

    @router.post("/readings/import/finalize")
    async def readings_import_finalize(
        request: Request,
        csv_content_b64: str = Form(...), delimiter: str = Form(";"), default_year: str = Form(""),
        db: AsyncSession = Depends(get_db),
    ):
        user = await require_permission(request, db, modul_name, "write")

        form = await request.form()
        column_mapping = parse_column_mapping(form, READINGS_IMPORT_TARGET_FIELDS)
        if not column_mapping:
            message = t_for(request, "metering.readings_list.csv_mapping_required_error")
            return RedirectResponse(
                f"{url_prefix}/readings?error={urllib.parse.quote(message)}",
                status_code=303,
            )
        # Same relaxation as the points importer: Type needn't be mapped
        # for a single-medium, all-PARCEL export.
        type_mapped = "type" in column_mapping.values()
        rows = parse_mapped_csv_rows(csv_content_b64, delimiter, column_mapping)

        all_points = await _load_all_metering_points(db)
        # Same lookup key as the metering-points import: (type, parcel
        # number) for PARCEL rows, (type, label) for MAIN_METER/CLUB --
        # readings are attached to an already-existing metering point,
        # never create one.
        points_by_key = {}
        for a in all_points:
            if a.type == MeteringPointType.PARCEL and a.parcel:
                points_by_key[(a.type.value, a.parcel.plot_number.strip().upper())] = a
            elif a.label:
                points_by_key[(a.type.value, a.label.strip().upper())] = a

        recorded = 0
        skipped_no_point = 0
        skipped_no_meter = 0
        skipped_invalid = 0
        skipped_implausible = 0
        skipped_meter_mismatch = 0
        skip_details = []
        reason_invalid_type = t_for(request, "metering.readings_list.csv_import_skip_reason_invalid_type")
        reason_no_point = t_for(request, "metering.readings_list.csv_import_skip_reason_no_point")
        reason_no_meter = t_for(request, "metering.readings_list.csv_import_skip_reason_no_meter")
        reason_invalid_row = t_for(request, "metering.readings_list.csv_import_skip_reason_invalid")
        reason_implausible = t_for(request, "metering.readings_list.csv_import_skip_reason_implausible")
        reason_meter_mismatch = t_for(request, "metering.readings_list.csv_import_skip_reason_meter_mismatch")

        for row_number, values in enumerate(rows, start=2):
            parcel_number = (values.get("parcel_number") or "").strip().upper()
            label = (values.get("label") or "").strip().upper()
            identifier = parcel_number or label or f"#{row_number}"

            type_str = (values.get("type") or "").strip().upper()
            if not type_str and not type_mapped:
                type_str = MeteringPointType.PARCEL.value
            if type_str not in {t.value for t in MeteringPointType}:
                skipped_invalid += 1
                skip_details.append(f"{identifier}: {reason_invalid_type}")
                continue

            key = (type_str, parcel_number if type_str == MeteringPointType.PARCEL.value else label)

            metering_point = points_by_key.get(key)
            if not metering_point:
                skipped_no_point += 1
                skip_details.append(f"{identifier}: {reason_no_point}")
                continue

            meter = metering_point.current_meter
            if not meter:
                skipped_no_meter += 1
                skip_details.append(f"{identifier}: {reason_no_meter}")
                continue

            # If the row names a meter number and it doesn't match the
            # point's *current* meter, the reading may actually belong
            # to a since-replaced meter (exchange_meter() deactivates
            # the old one rather than deleting it, but there is no path
            # -- CSV import or manual entry -- to attach a reading to a
            # non-current meter). Skip rather than silently misattribute
            # a historical reading to the wrong physical meter.
            row_meter_number = (values.get("meter_number") or "").strip()
            if row_meter_number and row_meter_number.upper() != (meter.number or "").strip().upper():
                skipped_meter_mismatch += 1
                skip_details.append(f"{identifier}: {reason_meter_mismatch}")
                continue

            # A per-row Year column (if mapped and non-blank) always wins;
            # `default_year` is an explicit, human-stated fallback for the
            # whole import run ("this batch is 2025's readings"), never an
            # automatic guess from the date -- see the Year note above for
            # why guessing from Date specifically was rejected.
            year_str = (values.get("year") or "").strip() or default_year.strip()
            reading_value = _parse_number(values.get("reading") or "", decimal_places)
            reading_date = _parse_date_flexible(values.get("date") or "")
            if not year_str.isdigit() or reading_value is None or reading_date is None:
                skipped_invalid += 1
                skip_details.append(f"{identifier}: {reason_invalid_row}")
                continue

            year_int = int(year_str)
            already_had_year = any(r.year == year_int for r in meter.readings)
            try:
                new_reading = await record_reading(
                    db, meter, year=year_int, reading_date=reading_date, reading=reading_value,
                    note=((values.get("note") or "").strip() or None), recorded_by_id=user.id,
                )
            except ServiceError:
                skipped_implausible += 1
                skip_details.append(f"{identifier}: {reason_implausible}")
                continue

            if not already_had_year:
                # record_reading() sets meter_id on the new row directly
                # rather than through the relationship, so meter.readings
                # (already eagerly loaded above) wouldn't otherwise pick
                # it up in-memory -- and a later row in this same import
                # for the same meter needs it visible for its own
                # monotonicity check (see docs/module-metering.md's
                # identity-map pitfall).
                meter.readings.append(new_reading)

            recorded += 1

        await db.commit()

        message = t_for(request, "metering.readings_list.csv_import_summary", recorded=recorded)
        for count, key in (
            (skipped_no_point, "metering.readings_list.csv_import_skipped_no_point"),
            (skipped_no_meter, "metering.readings_list.csv_import_skipped_no_meter"),
            (skipped_invalid, "metering.readings_list.csv_import_skipped_invalid"),
            (skipped_implausible, "metering.readings_list.csv_import_skipped_implausible"),
            (skipped_meter_mismatch, "metering.readings_list.csv_import_skipped_meter_mismatch"),
        ):
            if count:
                message += t_for(request, key, count=count)
        if skip_details:
            message += " – " + " | ".join(skip_details[:3])
            if len(skip_details) > 3:
                message += t_for(request, "metering.readings_list.csv_import_more_skipped", count=len(skip_details) - 3)

        return RedirectResponse(
            f"{url_prefix}/readings?message={urllib.parse.quote(message)}",
            status_code=302,
        )

    # -----------------------------------------------------------------
    # Evaluation
    # -----------------------------------------------------------------

    @router.get("/evaluation", response_class=HTMLResponse)
    async def evaluation(
        request: Request,
        year: Optional[int] = None,
        db: AsyncSession = Depends(get_db),
    ):
        user = await require_permission(request, db, modul_name, "read")
        if not year:
            year = date.today().year

        all_points = await _load_all_metering_points(db)

        def rows_for_type(type):
            filtered = [a for a in all_points if a.type == type]
            rows = []
            for a in filtered:
                z = a.current_meter
                consumption = calculate_consumption(z, year) if z else None
                rows.append({"metering_point": a, "meter": z, "consumption": consumption})
            return rows

        main_meter_rows = rows_for_type(MeteringPointType.MAIN_METER)
        parcel_rows = sorted(
            rows_for_type(MeteringPointType.PARCEL),
            key=lambda z: z["metering_point"].parcel.plot_number if z["metering_point"].parcel else ""
        )
        club_rows = rows_for_type(MeteringPointType.CLUB)

        main_total = sum((z["consumption"] for z in main_meter_rows if z["consumption"] is not None), Decimal("0"))
        parcel_total = sum((z["consumption"] for z in parcel_rows if z["consumption"] is not None), Decimal("0"))
        club_total = sum((z["consumption"] for z in club_rows if z["consumption"] is not None), Decimal("0"))

        warning = None
        if main_total > 0 and (parcel_total + club_total) > main_total:
            warning = t_for(
                request, "metering.errors.overall_plausibility_evaluation",
                total=parcel_total + club_total, main=main_total, unit=unit,
            )

        available_years = sorted({
            zs.year for a in all_points for z in a.meters for zs in z.readings
        }, reverse=True)
        if year not in available_years:
            available_years.insert(0, year)

        return templates.TemplateResponse("metering/evaluation.html", {
            **base_context(request),
            "request": request, "user": user, "year": year,
            "available_years": available_years,
            "main_meter_rows": main_meter_rows,
            "parcel_rows": parcel_rows,
            "club_rows": club_rows,
            "main_total": main_total,
            "parcel_total": parcel_total,
            "club_total": club_total,
            "warning": warning,
        })

    @router.get("/evaluation/csv")
    async def evaluation_csv(
        request: Request,
        year: Optional[int] = None,
        db: AsyncSession = Depends(get_db),
    ):
        await require_permission(request, db, modul_name, "read")
        if not year:
            year = date.today().year

        all_points = await _load_all_metering_points(db)

        output = io.StringIO()
        writer = csv.writer(output, delimiter=";")
        writer.writerow(["Typ", "Zählpunkt", f"{medium_label_de}zähler-Nr.", "Zählerstand", f"Verbrauch ({unit})"])

        type_label = {
            MeteringPointType.MAIN_METER: "Hauptzähler",
            MeteringPointType.PARCEL: "Parcel",
            MeteringPointType.CLUB: "Verein",
        }

        for a in sorted(all_points, key=lambda a: (a.type.value, a.display_name)):
            z = a.current_meter
            if not z:
                continue
            entry = next((zs for zs in z.readings if zs.year == year), None)
            consumption = calculate_consumption(z, year)
            writer.writerow([
                type_label.get(a.type, a.type.value),
                a.display_name,
                z.number,
                f"{entry.reading:.{decimal_places}f}".replace(".", ",") if entry else "",
                f"{consumption:.{decimal_places}f}".replace(".", ",") if consumption is not None else "",
            ])

        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={modul_name}verbrauch_{year}.csv"},
        )

    # -----------------------------------------------------------------
    # Price configuration -- annual price per unit, drives the
    # water_usage/electricity_usage invoice pricing modes
    # (app/invoice_generation.py). Same "computed automatically"
    # pattern as work_hours' rate_per_hour_eur -- see
    # app/routers/work_hours.py's configuration_* routes, mirrored here.
    # -----------------------------------------------------------------

    @router.get("/configuration", response_class=HTMLResponse)
    async def price_configuration_page(request: Request, db: AsyncSession = Depends(get_db)):
        user = await require_permission(request, db, modul_name, "read")

        result = await db.execute(
            select(MeteringPriceConfiguration)
            .where(MeteringPriceConfiguration.medium == medium)
            .order_by(MeteringPriceConfiguration.year.desc())
        )
        configurations = result.scalars().all()

        return templates.TemplateResponse(
            "metering/configuration.html",
            {
                **base_context(request),
                "request": request, "user": user, "configurations": configurations,
                "current_year": date.today().year,
            },
        )

    @router.post("/configuration/new")
    async def price_configuration_create(
        request: Request,
        year: int = Form(...),
        price_per_unit: str = Form(...),
        note: str = Form(""),
        db: AsyncSession = Depends(get_db),
    ):
        await require_permission(request, db, modul_name, "write")

        parsed_price = float(price_per_unit.strip().replace(",", "."))
        await save_price_configuration_for_year(
            db, medium, year, price_per_unit=parsed_price, note=(note.strip() or None),
        )
        await db.commit()
        return RedirectResponse(f"{url_prefix}/configuration", status_code=302)

    @router.get("/configuration/{configuration_id}/edit", response_class=HTMLResponse)
    async def price_configuration_edit_page(
        configuration_id: str, request: Request, db: AsyncSession = Depends(get_db),
    ):
        user = await require_permission(request, db, modul_name, "write")

        result = await db.execute(
            select(MeteringPriceConfiguration).where(
                MeteringPriceConfiguration.id == configuration_id, MeteringPriceConfiguration.medium == medium,
            )
        )
        configuration = result.scalar_one_or_none()
        if not configuration:
            raise HTTPException(status_code=404, detail=t_for(request, "metering.errors.configuration_not_found"))

        return templates.TemplateResponse(
            "metering/configuration_form.html",
            {**base_context(request), "request": request, "user": user, "configuration": configuration},
        )

    @router.post("/configuration/{configuration_id}/edit")
    async def price_configuration_update(
        configuration_id: str,
        request: Request,
        year: int = Form(...),
        price_per_unit: str = Form(...),
        note: str = Form(""),
        db: AsyncSession = Depends(get_db),
    ):
        await require_permission(request, db, modul_name, "write")

        result = await db.execute(
            select(MeteringPriceConfiguration).where(
                MeteringPriceConfiguration.id == configuration_id, MeteringPriceConfiguration.medium == medium,
            )
        )
        configuration = result.scalar_one_or_none()
        if not configuration:
            raise HTTPException(status_code=404, detail=t_for(request, "metering.errors.configuration_not_found"))

        if year != configuration.year:
            collision = await get_price_configuration_for_year(db, medium, year)
            if collision and collision.id != configuration_id:
                raise HTTPException(
                    status_code=400,
                    detail=t_for(request, "metering.errors.configuration_year_exists", year=year),
                )

        configuration.year = year
        configuration.price_per_unit = float(price_per_unit.strip().replace(",", "."))
        configuration.note = note.strip() or None

        await db.commit()
        return RedirectResponse(f"{url_prefix}/configuration", status_code=302)

    @router.post("/configuration/{configuration_id}/delete")
    async def price_configuration_delete(
        configuration_id: str, request: Request, db: AsyncSession = Depends(get_db),
    ):
        await require_permission(request, db, modul_name, "delete")

        result = await db.execute(
            select(MeteringPriceConfiguration).where(
                MeteringPriceConfiguration.id == configuration_id, MeteringPriceConfiguration.medium == medium,
            )
        )
        configuration = result.scalar_one_or_none()
        if configuration:
            await db.delete(configuration)
            await db.commit()

        return RedirectResponse(f"{url_prefix}/configuration", status_code=302)

    return router
