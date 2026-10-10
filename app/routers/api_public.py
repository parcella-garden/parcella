"""
Public signup API: lets an external CMS (WordPress, TYPO3, Contao, or
anything else) create work-session signups without a Parcella login.

Read endpoints (upcoming sessions, parcel list) are intentionally
unauthenticated -- the same posture as the public community ICS feed in
app/ics_utils.py, and for the same reason: an external site's frontend
can't send this app's session cookie, and the data exposed (session
dates/times, plot numbers) isn't sensitive on its own.

The write endpoint (signup) requires the shared API token (see
app/public_api_auth.py) plus a lightweight honeypot and per-IP rate
limit, since -- unlike the read endpoints -- it creates data and is a
much more attractive target for abuse.

Design note (this is the important part): the public form only ever
collects a PARCEL NUMBER, never a member name selected from a list --
the club's public website must not expose which members live on which
parcel. So a signup here creates real SessionParticipation rows
directly (status REGISTERED), matched by an optionally-submitted free-
text name against the parcel's current residents where that's
unambiguous, and falling back to registering EVERY current resident of
the parcel when it isn't (no name given, no match, or more than one
plausible match) -- overregistering and letting the board delete the
wrong ones from the normal participants table is safer than silently
registering nobody, or guessing wrong without a trace. See
docs/module-public-api.md for the full rationale and the reference
WordPress connector under integrations/wordpress/.
"""
import re
import logging
from typing import List, Optional
from urllib.parse import urlsplit, urlunsplit

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse, RedirectResponse, Response
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db, current_tenant_filter
from app.models import (
    WorkSession, Parcel, ParcelStatus, MemberParcel, Member,
    SessionParticipation, ParticipationStatus, SessionType,
)
from app.module_flags import require_module
from app.public_api_auth import allowed_form_origins, normalize_origin, require_public_api_token
from app.rate_limit import check_and_record, client_ip_key
from app.schemas import (
    PublicWorkSessionOut, PublicParcelOut, PublicSignupCreate,
    PublicSignupResult, PublicSignupSessionResult,
    PublicContactCreate, PublicContactResult,
)
from app.form_altcha import altcha_required, new_challenge, verify as verify_altcha
from app.freescout_client import FreeScoutError, get_freescout_client
from app.services.work_hours import notify_new_participations_digest
from app.i18n import DEFAULT_LANGUAGE, translate


def _lang(request: Request) -> str:
    return getattr(request.state, "language", DEFAULT_LANGUAGE)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/public",
    tags=["Public Signup API"],
)

# ---------------------------------------------------------------------------
# Sliding-window rate limit for the write endpoint, keyed by client IP.
# The implementation moved to app/rate_limit.py when login got a limiter
# too -- see that module for why it's in-memory and what that implies.
# ---------------------------------------------------------------------------
_RATE_LIMIT_WINDOW_SECONDS = 3600
_RATE_LIMIT_MAX_REQUESTS = 20

# Separate window/key namespace for the contact-form endpoint below --
# same shape as the signup limiter, kept independent so a burst on one
# endpoint doesn't consume the other's budget for the same visitor.
_CONTACT_RATE_LIMIT_WINDOW_SECONDS = 3600
_CONTACT_RATE_LIMIT_MAX_REQUESTS = 10


def _check_rate_limit(request: Request) -> None:
    key = client_ip_key(request, "public_signup")
    if not check_and_record(key, _RATE_LIMIT_MAX_REQUESTS, _RATE_LIMIT_WINDOW_SECONDS):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many signup requests from this address, please try again later",
        )


def _check_contact_rate_limit(request: Request) -> None:
    key = client_ip_key(request, "public_contact")
    if not check_and_record(key, _CONTACT_RATE_LIMIT_MAX_REQUESTS, _CONTACT_RATE_LIMIT_WINDOW_SECONDS):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many contact requests from this address, please try again later",
        )


def _normalize_name(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip().lower()


def _find_matching_members(submitted_name: str, current_tenants: List[Member]) -> List[Member]:
    """Tries to match a free-text submitted name against the parcel's
    current residents. Only returns a match if exactly one tenant fits
    -- anything else (zero or multiple plausible matches) is the
    caller's cue to fall back to registering everyone, rather than
    guess."""
    if not submitted_name:
        return []
    target = _normalize_name(submitted_name)
    matches = []
    for member in current_tenants:
        forms = {
            _normalize_name(member.full_name),
            _normalize_name(f"{member.last_name} {member.first_name}"),
        }
        if target in forms:
            matches.append(member)
    return matches if len(matches) == 1 else []


def _build_note(parcel_number: str, payload: PublicSignupCreate, was_matched: bool, tenant_count: int) -> str:
    parts = []
    if was_matched:
        parts.append(f"Public signup, matched by name (parcel {parcel_number})")
    elif tenant_count > 1:
        parts.append(
            f"Public signup (parcel {parcel_number}) -- could not confidently match a "
            f"submitted name to one resident, so all {tenant_count} current residents of "
            f"this parcel were registered. Please verify and remove whoever didn't actually sign up."
        )
    else:
        parts.append(f"Public signup (parcel {parcel_number})")
    if payload.name:
        parts.append(f"Name given: {payload.name}")
    if payload.phone:
        parts.append(f"Phone: {payload.phone}")
    if payload.email:
        parts.append(f"Email: {payload.email}")
    if payload.remarks:
        parts.append(f"Remarks: {payload.remarks}")
    return " | ".join(parts)


@router.get(
    "/work-sessions/upcoming", response_model=list[PublicWorkSessionOut],
    dependencies=[Depends(require_module("public_signup_api"))],
)
async def list_upcoming_sessions(db: AsyncSession = Depends(get_db)):
    from datetime import date as date_cls

    result = await db.execute(
        select(WorkSession)
        # SPECIAL sessions (spontaneous/unplanned) never appear on the
        # public website -- same rule the community calendar already
        # enforces (docs/module-calendar.md), just never applied here.
        .where(WorkSession.date >= date_cls.today(), WorkSession.type == SessionType.STANDARD)
        .options(selectinload(WorkSession.participations))
        .order_by(WorkSession.date, WorkSession.time_from)
    )
    sessions = result.scalars().all()
    return [
        PublicWorkSessionOut(
            id=s.id, title=s.title, date=s.date,
            time_from=s.time_from, time_until=s.time_until,
            spots_left=s.available_spots,
        )
        for s in sessions
        # Hide sessions that are already full or past their signup
        # deadline, rather than showing a dead-end option a visitor
        # could still try to check.
        if (s.available_spots is None or s.available_spots > 0) and s.public_signup_open
    ]


@router.get(
    "/parcels", response_model=list[PublicParcelOut],
    dependencies=[Depends(require_module("public_signup_api"))],
)
async def list_parcels(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Parcel).where(Parcel.status == ParcelStatus.ACTIVE).order_by(Parcel.plot_number)
    )
    return result.scalars().all()


@router.post(
    "/work-sessions/signup",
    response_model=PublicSignupResult,
    dependencies=[Depends(require_module("public_signup_api")), Depends(require_public_api_token)],
)
async def submit_signup(
    payload: PublicSignupCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    result, _codes = await _process_signup(payload, request, db)
    return result


async def _process_signup(
    payload: PublicSignupCreate, request: Request, db: AsyncSession,
) -> tuple[PublicSignupResult, list[Optional[str]]]:
    """The signup logic shared by the JSON endpoint above and the
    plain-HTML-form endpoint further down. Besides the API response it
    returns one reason code per session (None = accepted) -- the same
    suffixes as the public_api.signup.* translation keys, which the form
    endpoint puts into its redirect instead of the translated text.
    Raises HTTPException for an unknown parcel (404) and for the rate
    limit (429), exactly as before."""
    # Honeypot: a real visitor never fills this field. Return a
    # believable-looking success without creating anything, so the bot
    # doesn't learn its submission was rejected.
    if payload.website:
        logger.info("Public signup honeypot triggered, silently ignoring submission")
        return PublicSignupResult(results=[
            PublicSignupSessionResult(session_id=sid, accepted=True) for sid in payload.session_ids
        ]), [None] * len(payload.session_ids)

    _check_rate_limit(request)
    lang = _lang(request)

    parcel_result = await db.execute(
        select(Parcel).where(Parcel.plot_number == payload.parcel_number)
    )
    parcel = parcel_result.scalar_one_or_none()
    if not parcel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown parcel number")

    tenants_result = await db.execute(
        select(MemberParcel)
        .options(selectinload(MemberParcel.member))
        .where(MemberParcel.parcel_id == parcel.id, current_tenant_filter())
    )
    current_tenants = [
        mp.member for mp in tenants_result.scalars().all()
        if mp.member and mp.member.deleted_at is None
    ]

    matched = _find_matching_members(payload.name, current_tenants)
    was_matched = bool(matched)
    members_to_register = matched if was_matched else current_tenants

    sessions_result = await db.execute(
        select(WorkSession)
        .where(WorkSession.id.in_(payload.session_ids))
        .options(selectinload(WorkSession.participations))
    )
    sessions_by_id = {s.id: s for s in sessions_result.scalars().all()}

    results: list[PublicSignupSessionResult] = []
    codes: list[Optional[str]] = []
    created_count = 0

    def reject(session_id: str, code: str) -> None:
        results.append(PublicSignupSessionResult(
            session_id=session_id, accepted=False,
            reason=translate(f"public_api.signup.{code}", lang),
        ))
        codes.append(code)

    if not members_to_register:
        for session_id in payload.session_ids:
            reject(session_id, "no_members_for_parcel")
        return PublicSignupResult(results=results), codes

    note = _build_note(parcel.plot_number, payload, was_matched, len(current_tenants))

    for session_id in payload.session_ids:
        session = sessions_by_id.get(session_id)
        # A SPECIAL session is invisible to the public API entirely --
        # treat it exactly like "not found" rather than a distinct
        # reason, since as far as this endpoint is concerned it isn't
        # a signup-eligible session at all.
        if not session or session.type != SessionType.STANDARD:
            reject(session_id, "session_not_found")
            continue

        if not session.public_signup_open:
            reject(session_id, "registration_closed")
            continue

        already_registered_member_ids = {p.member_id for p in session.participations}
        to_create = [m for m in members_to_register if m.id not in already_registered_member_ids]

        if session.available_spots is not None and session.available_spots < len(to_create):
            reject(session_id, "session_full")
            continue

        for member in to_create:
            db.add(SessionParticipation(
                session_id=session.id, member_id=member.id,
                status=ParticipationStatus.REGISTERED, note=note,
            ))
            created_count += 1

        results.append(PublicSignupSessionResult(session_id=session_id, accepted=True))
        codes.append(None)

    if created_count > 0:
        await db.commit()
        # Issue #217: one digest email for the whole call rather than
        # one per row -- this path is actorless and can create several
        # rows in one request (multiple sessions x a whole household on
        # an ambiguous name match), see docs/ADR/0079.
        await notify_new_participations_digest(db, created_count, _lang(request))
    else:
        await db.rollback()

    return PublicSignupResult(results=results), codes


_CONTACT_SUBJECT = "Contact form inquiry"


@router.post(
    "/contact",
    response_model=PublicContactResult,
    dependencies=[Depends(require_module("public_contact_api")), Depends(require_public_api_token)],
)
async def submit_contact(
    payload: PublicContactCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Creates a FreeScout conversation directly from an external contact
    form (e.g. the parcella-connector WordPress plugin's
    [parcella_contact_form] shortcode) via the FreeScout API, instead of
    creating a local Parcella ticket (the ticket module was removed --
    see docs/module-freescout-bridge.md and the ADR on that decision).
    Going through the API rather than sending a plain email sets the
    correct customer/mailbox metadata directly, with no ambiguity about
    which address FreeScout treats as the customer. Gated by its own
    module flag (public_contact_api), independent of public_signup_api
    and freescout_bridge -- a club must have FreeScout configured
    (Admin -> Integrations) for this to do anything, but doesn't need
    the freescout_bridge module itself enabled just to accept inbound
    contact-form messages."""
    result, _code = await _process_contact(payload, request, db)
    return result


async def _process_contact(
    payload: PublicContactCreate, request: Request, db: AsyncSession,
) -> tuple[PublicContactResult, Optional[str]]:
    """Shared by the JSON endpoint above and the plain-HTML-form endpoint
    below, same split as _process_signup. The second value is a reason
    code for a rejection (None = accepted); raises HTTPException 429 for
    the rate limit."""
    # Honeypot: a real visitor never fills this field. Return a
    # believable-looking success without creating anything, same as the
    # signup endpoint's honeypot handling above.
    if payload.website:
        logger.info("Public contact-form honeypot triggered, silently ignoring submission")
        return PublicContactResult(accepted=True), None

    _check_contact_rate_limit(request)

    if not payload.consent:
        return PublicContactResult(
            accepted=False, reason="Data-protection consent is required to submit this form",
        ), "consent_missing"

    client = await get_freescout_client(db)
    if client is None:
        logger.error("Public contact form submitted but FreeScout is not configured")
        return PublicContactResult(
            accepted=False, reason="Support system is not configured -- please try again later",
        ), "unavailable"

    try:
        await client.create_conversation(
            subject=_CONTACT_SUBJECT, customer_email=payload.email, customer_name=payload.name,
            message=f"{payload.message}\n\n[Data protection consent given at submission]",
        )
    except FreeScoutError as e:
        logger.error(f"FreeScout API request failed for public contact form: {e}")
        return PublicContactResult(accepted=False, reason="Could not submit your message -- please try again later"), "unavailable"

    return PublicContactResult(accepted=True), None


# ---------------------------------------------------------------------------
# Plain HTML forms (static websites). The endpoints above expect a server-
# side connector that holds the shared API token -- a static site has none,
# and a token written into its HTML would be public. These two accept a
# browser's own form POST instead and answer with a 303 redirect back to
# the site, gated by an allowlist of website origins rather than the
# token. See docs/ADR/0088-plain-html-form-endpoints-origin-allowlist.md.
# ---------------------------------------------------------------------------

def _request_origin(request: Request) -> Optional[str]:
    """Where the form was submitted from. Browsers send Origin on every
    cross-origin POST; Referer is the fallback for the rare one that
    doesn't (or sends the literal "null")."""
    origin = request.headers.get("origin")
    if origin and origin != "null":
        return normalize_origin(origin)
    return normalize_origin(request.headers.get("referer", ""))


def _redirect_target(requested: Optional[str], request: Request, allowed: set[str], fragment: str) -> str:
    """The form's own success_url/error_url if it points at an allowed
    origin -- otherwise the submitting page, otherwise that site's root.
    Never anywhere else: an unchecked target would turn this endpoint
    into an open redirect. The outcome travels as the URL fragment, so a
    static page can show the matching message with CSS :target alone."""
    referer = request.headers.get("referer", "")
    for candidate in (requested, referer):
        if candidate and normalize_origin(candidate) in allowed:
            parts = urlsplit(candidate.strip())
            return urlunsplit((parts.scheme, parts.netloc, parts.path or "/", parts.query, fragment))
    return f"{_request_origin(request)}/#{fragment}"


async def _check_form_origin(request: Request, db: AsyncSession) -> set[str]:
    allowed = await allowed_form_origins(db)
    if not allowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Public forms are not enabled")
    if _request_origin(request) not in allowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Form submitted from a website that isn't allowed")
    return allowed


def _cors_headers(origin: str) -> dict:
    return {
        "Access-Control-Allow-Origin": origin,
        "Access-Control-Allow-Methods": "GET",
        "Access-Control-Max-Age": "600",
        "Vary": "Origin",
        "Cache-Control": "no-store",
    }


@router.get("/forms/challenge")
async def form_challenge(request: Request, db: AsyncSession = Depends(get_db)):
    """A fresh ALTCHA challenge for the website's form widget (ADR 0089).
    Fetched by the visitor's browser with fetch(), so -- unlike the form
    POSTs -- it needs CORS: answered only for the allowed origins, the
    same allowlist the form endpoints use."""
    await _check_form_origin(request, db)
    return JSONResponse(new_challenge(), headers=_cors_headers(_request_origin(request)))


@router.options("/forms/challenge")
async def form_challenge_preflight(request: Request, db: AsyncSession = Depends(get_db)):
    """CORS preflight, in case a browser sends one for the GET above."""
    await _check_form_origin(request, db)
    headers = _cors_headers(_request_origin(request))
    requested = request.headers.get("access-control-request-headers")
    if requested:
        headers["Access-Control-Allow-Headers"] = requested
    return Response(status_code=status.HTTP_204_NO_CONTENT, headers=headers)


async def _altcha_failed(form, db: AsyncSession) -> bool:
    """True if the admin switch requires ALTCHA and the submission's
    solution (field `altcha`) is missing, wrong, expired or reused."""
    return await altcha_required(db) and not verify_altcha(_form_text(form, "altcha"))


def _form_text(form, name: str) -> Optional[str]:
    value = form.get(name)
    return value if isinstance(value, str) else None


def _is_checked(form, name: str) -> bool:
    return (_form_text(form, name) or "").strip().lower() in ("on", "true", "1", "yes")


def _http_error_code(error: HTTPException) -> str:
    return {404: "unknown_parcel", 429: "rate_limited"}.get(error.status_code, "error")


@router.post(
    "/forms/work-session-signup",
    dependencies=[Depends(require_module("public_signup_api"))],
)
async def submit_signup_form(request: Request, db: AsyncSession = Depends(get_db)):
    """Plain-HTML-form variant of POST /work-sessions/signup. Fields as in
    PublicSignupCreate (session_ids repeated, one per ticked checkbox),
    plus optional success_url/error_url. Every session accepted ->
    success_url#ok; some -> success_url#partial; none -> error_url#<code>."""
    allowed = await _check_form_origin(request, db)
    form = await request.form()
    success_url, error_url = _form_text(form, "success_url"), _form_text(form, "error_url")

    def redirect(url: Optional[str], fragment: str) -> RedirectResponse:
        return RedirectResponse(_redirect_target(url, request, allowed, fragment), status_code=status.HTTP_303_SEE_OTHER)

    if await _altcha_failed(form, db):
        return redirect(error_url, "captcha")

    try:
        payload = PublicSignupCreate(
            parcel_number=_form_text(form, "parcel_number") or "",
            name=_form_text(form, "name"), phone=_form_text(form, "phone"),
            email=_form_text(form, "email"), remarks=_form_text(form, "remarks"),
            session_ids=[v for v in form.getlist("session_ids") if isinstance(v, str) and v],
            website=_form_text(form, "website"),
        )
    except ValidationError as e:
        fields = {str(err["loc"][0]) for err in e.errors() if err.get("loc")}
        return redirect(error_url, "no_session_selected" if "session_ids" in fields else "invalid")
    if not payload.parcel_number.strip():
        return redirect(error_url, "invalid")

    try:
        _result, codes = await _process_signup(payload, request, db)
    except HTTPException as e:
        return redirect(error_url, _http_error_code(e))

    rejected = [code for code in codes if code]
    if not rejected:
        return redirect(success_url, "ok")
    if len(rejected) < len(codes):
        return redirect(success_url, "partial")
    return redirect(error_url, rejected[0])


@router.post(
    "/forms/contact",
    dependencies=[Depends(require_module("public_contact_api"))],
)
async def submit_contact_form(request: Request, db: AsyncSession = Depends(get_db)):
    """Plain-HTML-form variant of POST /contact: name, email, message, a
    consent checkbox, the honeypot, plus optional success_url/error_url.
    Redirects to success_url#ok or error_url#<code>."""
    allowed = await _check_form_origin(request, db)
    form = await request.form()
    success_url, error_url = _form_text(form, "success_url"), _form_text(form, "error_url")

    def redirect(url: Optional[str], fragment: str) -> RedirectResponse:
        return RedirectResponse(_redirect_target(url, request, allowed, fragment), status_code=status.HTTP_303_SEE_OTHER)

    if await _altcha_failed(form, db):
        return redirect(error_url, "captcha")

    try:
        payload = PublicContactCreate(
            name=(_form_text(form, "name") or "").strip(), email=(_form_text(form, "email") or "").strip(),
            message=(_form_text(form, "message") or "").strip(), consent=_is_checked(form, "consent"),
            website=_form_text(form, "website"),
        )
    except ValidationError:
        return redirect(error_url, "invalid")

    try:
        _result, code = await _process_contact(payload, request, db)
    except HTTPException as e:
        return redirect(error_url, _http_error_code(e))

    return redirect(error_url, code) if code else redirect(success_url, "ok")
