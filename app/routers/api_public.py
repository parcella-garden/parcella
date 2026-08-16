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
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db, current_tenant_filter
from app.models import (
    WorkSession, Parcel, ParcelStatus, MemberParcel, Member,
    SessionParticipation, ParticipationStatus,
)
from app.module_flags import require_module
from app.public_api_auth import require_public_api_token
from app.rate_limit import check_and_record, client_ip_key
from app.schemas import (
    PublicWorkSessionOut, PublicParcelOut, PublicSignupCreate,
    PublicSignupResult, PublicSignupSessionResult,
    PublicContactCreate, PublicContactResult,
)
from app.spam_filter import check_for_spam
from app.services.tickets import create_ticket

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
        .where(WorkSession.date >= date_cls.today())
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
        # Hide sessions that are already full, rather than showing a
        # dead-end option a visitor could still try to check.
        if s.available_spots is None or s.available_spots > 0
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
    # Honeypot: a real visitor never fills this field. Return a
    # believable-looking success without creating anything, so the bot
    # doesn't learn its submission was rejected.
    if payload.website:
        logger.info("Public signup honeypot triggered, silently ignoring submission")
        return PublicSignupResult(results=[
            PublicSignupSessionResult(session_id=sid, accepted=True) for sid in payload.session_ids
        ])

    _check_rate_limit(request)

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
    any_created = False

    if not members_to_register:
        for session_id in payload.session_ids:
            results.append(PublicSignupSessionResult(
                session_id=session_id, accepted=False,
                reason="No members are currently assigned to this parcel",
            ))
        return PublicSignupResult(results=results)

    note = _build_note(parcel.plot_number, payload, was_matched, len(current_tenants))

    for session_id in payload.session_ids:
        session = sessions_by_id.get(session_id)
        if not session:
            results.append(PublicSignupSessionResult(session_id=session_id, accepted=False, reason="Session not found"))
            continue

        already_registered_member_ids = {p.member_id for p in session.participations}
        to_create = [m for m in members_to_register if m.id not in already_registered_member_ids]

        if session.available_spots is not None and session.available_spots < len(to_create):
            results.append(PublicSignupSessionResult(session_id=session_id, accepted=False, reason="Session is full"))
            continue

        for member in to_create:
            db.add(SessionParticipation(
                session_id=session.id, member_id=member.id,
                status=ParticipationStatus.REGISTERED, note=note,
            ))
            any_created = True

        results.append(PublicSignupSessionResult(session_id=session_id, accepted=True))

    if any_created:
        await db.commit()
    else:
        await db.rollback()

    return PublicSignupResult(results=results)


_CONTACT_TICKET_SUBJECT = "Contact form inquiry"


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
    """Creates a Parcella ticket directly from an external contact form
    (e.g. the parcella-connector WordPress plugin's [parcella_contact_form]
    shortcode) instead of that form sending a plain email that then has
    to be re-ingested via the ticket mailbox. Gated by its own module
    flag (public_contact_api), independent of public_signup_api -- a
    club should be able to enable one bridge without the other."""
    # Honeypot: a real visitor never fills this field. Return a
    # believable-looking success without creating anything, same as the
    # signup endpoint's honeypot handling above.
    if payload.website:
        logger.info("Public contact-form honeypot triggered, silently ignoring submission")
        return PublicContactResult(accepted=True)

    _check_contact_rate_limit(request)

    if not payload.consent:
        return PublicContactResult(
            accepted=False, reason="Data-protection consent is required to submit this form",
        )

    spam_result = await check_for_spam(payload.email, _CONTACT_TICKET_SUBJECT, payload.message, db)

    ticket = await create_ticket(
        db, subject=_CONTACT_TICKET_SUBJECT, sender_email=payload.email, sender_name=payload.name,
        message=f"{payload.message}\n\n[Data protection consent given at submission]",
    )
    ticket.spam_suspected = spam_result.is_spam_suspected
    ticket.spam_score = spam_result.score
    ticket.spam_reasoning = spam_result.reasoning
    await db.commit()

    return PublicContactResult(accepted=True)
