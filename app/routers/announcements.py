"""
Announcements module router.

Authoring an Announcement (title, Markdown body, optional image,
optional print override), plus all three delivery channels. There is
no announcement-level status: each channel's AnnouncementDelivery says
what went out, and a channel's action is only offered while it has
something new to do (see _channel_action_available, ADR 0087):
- email: a paced real send to current members
  (app.announcement_mailer.run_paced_email_send, run as a background
  task so a large roster doesn't hold the request open) and a one-off
  test send to a single address for review before committing to the
  real thing.
- blog: creates a draft on the club's website through the active
  website connector (app.website_connectors, ADR 0104),
  using whatever credentials are configured under Admin -> Integrations;
  after a content change, updates that same post instead of creating
  a second one.
- print: renders a one-page branded PDF (app.print_publisher),
  auto-shortening the text and adding a QR code if it doesn't fit as-is
  -- see app.print_publisher's module docstring for the full logic.
- letter (messages to filtered members only, issue #242): one addressed
  letter per member who can't be reached by email
  (app.announcement_letters). Generated on demand and never stored --
  unlike the print notice it holds names and addresses, and the only
  persisted upload directory is publicly served under /static.

A message to filtered members (Announcement.audience_filter, started
from /members/ -- see ADR 0095) uses EMAIL and LETTER only; club news
uses EMAIL, BLOG and PRINT.

Restricted to board/admin (require_admin), same reasoning as the
public_signup_api's Integrations page: this creates content that will
be pushed to a public blog and to every member's inbox, so authoring
it isn't a general member-facing feature.
"""
import base64
from dataclasses import dataclass
import re
import secrets
import urllib.parse
import uuid
from datetime import date, datetime, timezone
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Request, Depends, HTTPException, UploadFile, BackgroundTasks, Response
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import (
    Announcement, AnnouncementDelivery, AnnouncementChannel, AnnouncementDeliveryStatus, Applicant, MemberTag,
    Parcel, User,
)
from app.member_filters import MemberListFilter
from app.auth import require_admin
from app.permissions import require_permission
from app.module_flags import require_module
from app.rate_limit import check_and_record, client_ip_key
from app.announcement_utils import render_markdown_to_html, likely_fits_one_print_page, channel_fingerprint
from app.announcement_mailer import start_paced_email_send, run_paced_email_send, send_test_email, resolve_audience
from app.announcement_letters import render_announcement_letters_pdf
from app.website_connectors import (
    BlogPostNotFoundError, BlogPublishError, DraftContent, get_active_connector, get_active_type,
)
from app.print_publisher import render_announcement_print_pdf, PrintTooLongError, load_print_cloud_folder
from app.cloud_storage import CloudStorageError, get_cloud_storage_provider
from app.branding import load_branding
from app.pdf_chrome import load_org_footer_context
from app.i18n import load_current_language, translate
from app.l10n import load_current_region
from app.templating import templates

router = APIRouter(
    prefix="/announcements",
    tags=["announcements"],
    dependencies=[Depends(require_module("announcements"))],
)

# The short link a printed QR code points to (ADR 0133). Public: whoever
# scans the notice has no account. Separate router because of the prefix.
link_router = APIRouter(
    prefix="/a",
    tags=["announcements"],
    dependencies=[Depends(require_module("announcements"))],
)

_LINK_RATE_LIMIT_MAX = 30
_LINK_RATE_LIMIT_WINDOW_SECONDS = 60

UPLOAD_DIR = Path("app/static/uploads/announcements")
ALLOWED_IMAGE_TYPES = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/webp": ".webp",
}
MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB
# The form checks the size in the browser too, so an oversized image is
# flagged as soon as it's picked instead of after a full upload.
templates.env.globals["announcement_max_image_bytes"] = MAX_IMAGE_SIZE_BYTES
# Stored copies of generated print PDFs (download again without
# regenerating). Under static/uploads/ because that's the one persisted
# data directory (ADR 0077); names are random uuids, and the content is
# a notice meant for the club's notice board anyway.
PRINT_PDF_DIR = Path("app/static/uploads/announcements/print")


async def _save_announcement_image(file: UploadFile) -> str:
    """Validates and saves an uploaded announcement image, returning the
    filename to store on the Announcement. Unlike the singleton club
    logo (app/branding.py), each announcement can have its own image, so
    filenames are unique (uuid-based) rather than fixed."""
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise ValueError("invalid_image_type")

    contents = await file.read()
    if len(contents) > MAX_IMAGE_SIZE_BYTES:
        raise ValueError("image_too_large")

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    extension = ALLOWED_IMAGE_TYPES[file.content_type]
    filename = f"{uuid.uuid4()}{extension}"
    with open(UPLOAD_DIR / filename, "wb") as f:
        f.write(contents)
    return filename


def _delete_announcement_image(filename: Optional[str]) -> None:
    if not filename:
        return
    path = UPLOAD_DIR / filename
    if path.exists():
        try:
            path.unlink()
        except OSError:
            pass


def _delete_print_pdf(filename: Optional[str]) -> None:
    if not filename:
        return
    path = PRINT_PDF_DIR / filename
    if path.exists():
        try:
            path.unlink()
        except OSError:
            pass


def _current_fingerprint(announcement: Announcement, channel: AnnouncementChannel) -> str:
    return channel_fingerprint(
        channel.name, announcement.title, announcement.body_markdown, announcement.print_text_override,
        summary=announcement.summary, print_qr_code=announcement.print_qr_code,
    )


def _content_changed_since(announcement: Announcement, delivery: AnnouncementDelivery) -> bool:
    return (
        delivery.content_fingerprint != _current_fingerprint(announcement, delivery.channel)
        or delivery.image_filename != announcement.image_filename
        or delivery.image_alt != announcement.image_alt
    )


def _record_delivered_content(announcement: Announcement, delivery: AnnouncementDelivery) -> None:
    delivery.content_fingerprint = _current_fingerprint(announcement, delivery.channel)
    delivery.image_filename = announcement.image_filename
    delivery.image_alt = announcement.image_alt


def _channel_action_available(announcement: Announcement, channel: AnnouncementChannel) -> bool:
    """Whether a channel's action button (send email / create-or-update
    blog post / create PDF) makes sense right now -- enforced here on
    the server too, not just by hiding the button (ADR 0087):

    - never attempted, or last attempt FAILED -> yes (first try / retry)
    - SENDING -> no
    - EMAIL, SENT -> never again: every member already has it, and a
      second full send is not something to offer after an edit.
    - BLOG, SENT -> only once title/body/image changed since.
    - PRINT, SENT -> once title/body/print text/QR switch/image changed since,
      when the stored PDF is gone, or when it was shortened without a
      QR code and a blog post exists that may since have been published.
    """
    # Issue #242: a message to filtered members is no blog post or
    # notice-board page; letters exist only for those messages.
    if announcement.is_targeted and channel in (AnnouncementChannel.BLOG, AnnouncementChannel.PRINT):
        return False
    if channel == AnnouncementChannel.LETTER:
        # Generated on demand, never stored (names and addresses) --
        # so it can always be generated again. Not for applicants
        # (issue #247): they have no postal address on file.
        return announcement.is_targeted and not announcement.is_applicant_message

    delivery = announcement.delivery_for(channel)
    if delivery is None or delivery.status == AnnouncementDeliveryStatus.FAILED:
        return True
    if delivery.status != AnnouncementDeliveryStatus.SENT:
        return False
    if channel == AnnouncementChannel.EMAIL:
        return False
    if _content_changed_since(announcement, delivery):
        return True
    if channel == AnnouncementChannel.PRINT:
        if not delivery.pdf_filename or not (PRINT_PDF_DIR / delivery.pdf_filename).exists():
            return True
        blog_delivery = announcement.delivery_for(AnnouncementChannel.BLOG)
        if delivery.qr_pending and blog_delivery is not None and blog_delivery.status == AnnouncementDeliveryStatus.SENT:
            return True
    return False


def _require_channel_action_available(announcement: Announcement, channel: AnnouncementChannel) -> None:
    if not _channel_action_available(announcement, channel):
        raise HTTPException(status_code=409, detail="Nothing new to deliver on this channel")


async def _form_context(db: AsyncSession, announcement: Optional[Announcement]) -> dict:
    """Template context for the edit form's channel section. Also used
    when re-rendering the form after a validation error, so the page
    looks the same either way."""
    if announcement is None:
        return {}
    channels = {}
    for channel in AnnouncementChannel:
        delivery = announcement.delivery_for(channel)
        channels[channel.name] = {
            "delivery": delivery,
            "available": _channel_action_available(announcement, channel),
            "changed": delivery is not None and delivery.status == AnnouncementDeliveryStatus.SENT
                       and _content_changed_since(announcement, delivery),
        }
    return {
        "channels": channels,
        "website_connector_type": await get_active_type(db),
        "fits_one_page": likely_fits_one_print_page(
            announcement.print_text_override or announcement.body_markdown
        ),
    }


def _filter_from_query_string(query_string: str) -> MemberListFilter:
    """The /members/ filter as carried over in a query string (the list
    page's own MemberListFilter.query_string())."""
    parsed = urllib.parse.parse_qs(query_string or "")
    params = {k: v[-1] for k, v in parsed.items()}
    return MemberListFilter.from_query(
        search=params.get("search", ""),
        include_inactive=params.get("include_inactive") == "true",
        active_only=params.get("active_only") == "true",
        email_info_only=params.get("email_info_only") == "true",
        tag=params.get("tag", ""),
        ids=parsed.get("ids", []),
    )


async def _audience_context(db: AsyncSession, announcement: Announcement) -> dict:
    """Template context for a message to filtered members: who it
    reaches by email/letter, who not at all, and a link back to the
    member list showing the same filter. Empty for club news."""
    if not announcement.is_targeted:
        return {}
    if announcement.is_parcel_message:
        return {
            "audience": await resolve_audience(db, announcement),
            "parcel_audience": True,
            "audience_parcel_ids": announcement.audience_parcel_ids,
            "audience_list_url": "/parcels/",
        }
    if announcement.is_applicant_message:
        return {
            "audience": await resolve_audience(db, announcement),
            "applicant_audience": True,
            "audience_applicant_ids": announcement.audience_applicant_ids,
            "audience_list_url": "/applicants/?filter=all",
        }
    audience_filter = MemberListFilter.from_dict(announcement.audience_filter)
    tag = await db.get(MemberTag, audience_filter.tag) if audience_filter.tag else None
    query_string = audience_filter.query_string()
    return {
        "audience": await resolve_audience(db, announcement),
        "audience_filter": audience_filter,
        "audience_tag": tag,
        "audience_query": query_string,
        "audience_list_url": "/members/" + (f"?{query_string}" if query_string else ""),
    }


async def _get_announcement_or_404(db: AsyncSession, announcement_id: str) -> Announcement:
    result = await db.execute(
        select(Announcement)
        .where(Announcement.id == announcement_id)
        .options(selectinload(Announcement.deliveries))
    )
    announcement = result.scalar_one_or_none()
    if announcement is None:
        raise HTTPException(status_code=404, detail="Announcement not found")
    return announcement


# ---------------------------------------------------------------------------
# List
# ---------------------------------------------------------------------------

@router.get("/", response_class=HTMLResponse)
async def announcement_list(request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_admin(request, db)
    result = await db.execute(
        select(Announcement).options(selectinload(Announcement.deliveries))
        .order_by(Announcement.created_at.desc())
    )
    announcements = result.scalars().all()
    return templates.TemplateResponse("announcements/list.html", {
        "request": request, "user": user, "announcements": announcements,
    })


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------

def _targeted_audience_query(params) -> Optional[str]:
    """The /members/ filter a new message was started from, or None for
    club news. An *empty* filter (the unfiltered list) is club news too:
    as a targeted message it would reach every active member while
    ignoring their email-info opt-out (review finding on issue #242)."""
    if params.get("audience") != "1":
        return None
    query = params.get("audience_query", "") or ""
    picked = params.getlist("ids") if hasattr(params, "getlist") else []
    if picked:
        # Issue #337: members ticked on /members/ come as separate ids
        # next to the list's filter; fold them into one filter.
        query = _filter_from_query_string(query).without_ids().query_string()
        query = "&".join(q for q in (query, urllib.parse.urlencode({"ids": picked}, doseq=True)) if q)
    audience_filter = _filter_from_query_string(query)
    return None if audience_filter.is_empty() else audience_filter.query_string()


# A sanity cap on one hand-picked selection, not a product limit.
MAX_PICKED_APPLICANTS = 2000


async def _picked_applicant_ids(request: Request, db: AsyncSession, params) -> Optional[List[str]]:
    """The applicants ticked on /applicants/ (issues #246/#247), or None
    when this isn't a message to applicants. Only ids of applicants that
    exist are kept, in the order given; an empty or entirely unknown
    selection is refused rather than quietly becoming club news."""
    if params.get("audience_kind") != "applicants":
        return None
    if not request.state.module_flags.get("applicants"):
        raise HTTPException(status_code=404, detail="Applicants module is disabled")
    await require_permission(request, db, "applicants", "read")
    requested = list(dict.fromkeys(i for i in params.getlist("applicant_ids") if i and len(i) <= 36))
    if len(requested) > MAX_PICKED_APPLICANTS:
        raise HTTPException(status_code=400, detail="Too many applicants selected")
    existing = set((await db.scalars(select(Applicant.id).where(Applicant.id.in_(requested)))).all()) if requested else set()
    picked = [i for i in requested if i in existing]
    if not picked:
        raise HTTPException(status_code=400, detail="No applicants selected")
    return picked


async def _picked_parcel_ids(request: Request, db: AsyncSession, params) -> Optional[List[str]]:
    """The parcels ticked on /parcels/ (issue #397, a notice to their
    leaseholders), or None when this isn't one. Same rules as for
    applicants: only existing parcels, in the order given; an empty
    selection is refused."""
    if params.get("audience_kind") != "parcels":
        return None
    await require_permission(request, db, "members_parcels", "read")
    requested = list(dict.fromkeys(i for i in params.getlist("parcel_ids") if i and len(i) <= 36))
    if len(requested) > MAX_PICKED_APPLICANTS:
        raise HTTPException(status_code=400, detail="Too many parcels selected")
    existing = set((await db.scalars(select(Parcel.id).where(Parcel.id.in_(requested)))).all()) if requested else set()
    picked = [i for i in requested if i in existing]
    if not picked:
        raise HTTPException(status_code=400, detail="No parcels selected")
    return picked


@dataclass
class _Picked:
    """A hand-picked audience: applicants (#247) or parcels (#397)."""
    kind: str
    ids: List[str]

    def apply(self, announcement: Announcement) -> None:
        if self.kind == "parcels":
            announcement.audience_parcel_ids = self.ids
        else:
            announcement.audience_applicant_ids = self.ids


async def _picked_audience(request: Request, db: AsyncSession, params) -> Optional[_Picked]:
    applicant_ids = await _picked_applicant_ids(request, db, params)
    if applicant_ids is not None:
        return _Picked("applicants", applicant_ids)
    parcel_ids = await _picked_parcel_ids(request, db, params)
    if parcel_ids is not None:
        return _Picked("parcels", parcel_ids)
    return None


async def _new_form_context(
    db: AsyncSession, audience_query: Optional[str], picked: Optional[_Picked] = None,
) -> dict:
    """For "write to these members" (issue #242): audience_query is the
    /members/ filter it was started from, None for club news; for
    "write to the selected applicants" (issue #247) or "write to their
    leaseholders" (issue #397) the picked ids. The
    preview uses a transient Announcement that's never added to the
    session."""
    if picked is not None:
        preview = Announcement()
        picked.apply(preview)
        return await _audience_context(db, preview)
    if audience_query is None:
        return {}
    preview = Announcement(audience_filter=_filter_from_query_string(audience_query).to_dict())
    return await _audience_context(db, preview)


IMAGE_ALT_MAX_LENGTH = 255


SUMMARY_MAX_LENGTH = 300


def _clean_summary(value) -> Optional[str]:
    """The announcement's summary (issue #317): plain text, one line, at
    most 300 characters, None when empty. It goes into an email preheader
    and website excerpts/meta descriptions, so it's flattened once here;
    escaping stays each renderer's job."""
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    return text[:SUMMARY_MAX_LENGTH] or None


def _clean_image_alt(value) -> Optional[str]:
    """The banner's alt text (issue #318): one line, at most 255
    characters, None when empty. It ends up in HTML attributes, email,
    PDF and other systems' fields, so newlines/tabs are flattened here
    once; escaping is still each renderer's job."""
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    return text[:IMAGE_ALT_MAX_LENGTH] or None


def _entered_values(form) -> dict:
    """What the user typed, for re-rendering the form after a validation
    error. Without it a rejected save (e.g. an oversized image) showed
    an empty form -- or, when editing, the stored text -- and the typed
    text was gone."""
    return {
        "title": form.get("title") or "",
        "body_markdown": form.get("body_markdown") or "",
        "print_text_override": form.get("print_text_override") or "",
        "print_qr_code": form.get("print_qr_code") == "true",
        "image_alt": form.get("image_alt") or "",
        "summary": form.get("summary") or "",
        "letters_for_all": form.get("letters_for_all") == "true",
    }


@router.get("/new", response_class=HTMLResponse)
async def announcement_new_form(request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_admin(request, db)
    picked = await _picked_audience(request, db, request.query_params)
    audience_query = None if picked is not None else _targeted_audience_query(request.query_params)
    return templates.TemplateResponse("announcements/form.html", {
        "request": request, "user": user, "announcement": None, "error": None,
        **await _new_form_context(db, audience_query, picked),
    })


class _FormRejected(Exception):
    """A new message's form failed validation; `error` is the code the
    form template turns into a message."""
    def __init__(self, error: str):
        super().__init__(error)
        self.error = error


async def _announcement_from_form(form, user, picked, audience_query) -> Announcement:
    """A new Announcement from the "new message" form (the page and the
    compose popup, issue #345), not yet added to the session. Raises
    _FormRejected for a missing title/text or a refused image."""
    title = (form.get("title") or "").strip()
    body_markdown = (form.get("body_markdown") or "").strip()
    if not title or not body_markdown:
        raise _FormRejected("missing_fields")

    image_filename = None
    image_upload = form.get("image")
    if image_upload is not None and getattr(image_upload, "filename", ""):
        try:
            image_filename = await _save_announcement_image(image_upload)
        except ValueError as e:
            raise _FormRejected(str(e))

    announcement = Announcement(
        title=title,
        body_markdown=body_markdown,
        body_html=render_markdown_to_html(body_markdown),
        image_filename=image_filename,
        image_alt=_clean_image_alt(form.get("image_alt")) if image_filename else None,
        summary=_clean_summary(form.get("summary")),
        created_by_id=user.id,
    )
    if picked is not None:
        picked.apply(announcement)
        if picked.kind == "parcels":
            announcement.letters_for_all = form.get("letters_for_all") == "true"
    elif audience_query is not None:
        announcement.audience_filter = _filter_from_query_string(audience_query).to_dict()
        announcement.letters_for_all = form.get("letters_for_all") == "true"
    return announcement


@router.post("/new")
async def announcement_create(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user = await require_admin(request, db)
    form = await request.form()
    picked = await _picked_audience(request, db, form)
    audience_query = None if picked is not None else _targeted_audience_query(form)

    try:
        announcement = await _announcement_from_form(form, user, picked, audience_query)
    except _FormRejected as e:
        return templates.TemplateResponse("announcements/form.html", {
            "request": request, "user": user, "announcement": None, "entered": _entered_values(form),
            "error": e.error, **await _new_form_context(db, audience_query, picked),
        }, status_code=400)
    db.add(announcement)
    await db.commit()

    return RedirectResponse(url=f"/announcements/{announcement.id}/edit", status_code=303)


# ---------------------------------------------------------------------------
# Compose popup (issue #345): write and send in one step
# ---------------------------------------------------------------------------
#
# The popup opens wherever a message can be started (/members/, a member's
# page, /applicants/, /announcements/) and does the normal case in one
# step: text plus ticked channels, "Save & send". It runs the very same
# channel helpers as the send page, so ADR 0087's rules hold unchanged
# (the email goes out once, a channel without anything new is skipped).
# The send page stays for everything later: retries, "update website
# draft", printing again. A test email saves a draft first; the popup then
# keeps working on that draft (announcement_id), but only while nothing
# has been delivered from it. See ADR 0139.

COMPOSE_ORDER = (
    AnnouncementChannel.EMAIL, AnnouncementChannel.BLOG, AnnouncementChannel.PRINT, AnnouncementChannel.LETTER,
)


def _compose_channels(announcement: Announcement, website_type: Optional[str], audience) -> List[dict]:
    """The channels the popup offers for this kind of message, each with
    whether it's ticked by default: email when anyone gets one (kermie's
    call on #345); letters instead when nobody has an email address."""
    if announcement.is_applicant_message:
        offered = [AnnouncementChannel.EMAIL]
    elif announcement.is_targeted:
        offered = [AnnouncementChannel.EMAIL, AnnouncementChannel.LETTER]
    else:
        offered = [AnnouncementChannel.EMAIL, AnnouncementChannel.PRINT]
        if website_type:
            offered.insert(1, AnnouncementChannel.BLOG)
    email_count = len(audience.email) if audience is not None else 0
    letter_count = len(audience.letter_groups) if audience is not None else 0
    channels = []
    for channel in offered:
        if channel == AnnouncementChannel.EMAIL:
            checked, count = email_count > 0, email_count
        elif channel == AnnouncementChannel.LETTER:
            checked, count = email_count == 0 and letter_count > 0, letter_count
        else:
            checked, count = False, None
        channels.append({"name": channel.name, "checked": checked, "count": count,
                         "disabled": count == 0})
    return channels


async def _compose_context(
    request: Request, db: AsyncSession, user, announcement: Announcement,
) -> dict:
    audience = await resolve_audience(db, announcement)
    context = await _audience_context(db, announcement) if announcement.is_targeted else {}
    context.update({
        "request": request, "user": user, "draft": announcement if announcement.id else None,
        "preview": announcement, "audience": audience,
        "compose_channels": _compose_channels(announcement, await get_active_type(db), audience),
    })
    return context


def _render_fragment(name: str, context: dict) -> str:
    return templates.get_template(name).render(context)


def _compose_form_response(context: dict, status_code: int = 200, **extra) -> JSONResponse:
    context.update(extra)
    return JSONResponse(
        {"state": "form", "html": _render_fragment("announcements/_compose_form.html", context)},
        status_code=status_code,
    )


@router.get("/compose")
async def announcement_compose_form(request: Request, db: AsyncSession = Depends(get_db)):
    """The popup's form, for the same audience parameters as /new."""
    user = await require_admin(request, db)
    picked = await _picked_audience(request, db, request.query_params)
    audience_query = None if picked is not None else _targeted_audience_query(request.query_params)
    preview = Announcement()
    if picked is not None:
        picked.apply(preview)
    elif audience_query is not None:
        preview.audience_filter = _filter_from_query_string(audience_query).to_dict()
    context = await _compose_context(request, db, user, preview)
    context["test_email_value"] = user.email
    return _compose_form_response(context)


async def _update_compose_draft(announcement: Announcement, form) -> None:
    """The popup's form applied to the draft it saved for a test email.
    Same fields as creating; the audience was fixed when it was saved."""
    title = (form.get("title") or "").strip()
    body_markdown = (form.get("body_markdown") or "").strip()
    if not title or not body_markdown:
        raise _FormRejected("missing_fields")
    image_upload = form.get("image")
    if image_upload is not None and getattr(image_upload, "filename", ""):
        try:
            new_filename = await _save_announcement_image(image_upload)
        except ValueError as e:
            raise _FormRejected(str(e))
        _delete_announcement_image(announcement.image_filename)
        announcement.image_filename = new_filename
    announcement.title = title
    announcement.body_markdown = body_markdown
    announcement.body_html = render_markdown_to_html(body_markdown)
    announcement.summary = _clean_summary(form.get("summary"))
    announcement.image_alt = _clean_image_alt(form.get("image_alt")) if announcement.image_filename else None
    if announcement.is_targeted:
        announcement.letters_for_all = form.get("letters_for_all") == "true"


async def _run_compose_channel(
    request: Request, db: AsyncSession, background_tasks: BackgroundTasks,
    announcement: Announcement, channel: AnnouncementChannel, downloads: List[dict],
) -> dict:
    """Runs one ticked channel and describes the outcome for the popup."""
    await db.refresh(announcement, attribute_names=["deliveries"])
    result = {"channel": channel.name, "ok": False, "count": None, "detail": None, "link": None, "skipped": False}
    if not _channel_action_available(announcement, channel):
        result["skipped"] = True
        return result

    if channel == AnnouncementChannel.EMAIL:
        result["count"] = await start_email_channel(request, db, background_tasks, announcement)
        result["ok"] = result["count"] > 0
    elif channel == AnnouncementChannel.BLOG:
        delivery = await push_website_draft(db, announcement)
        result["ok"] = delivery.status == AnnouncementDeliveryStatus.SENT
        if result["ok"] and (delivery.external_reference or "").startswith(("https://", "http://")):
            result["link"] = delivery.external_reference
    elif channel == AnnouncementChannel.PRINT:
        pdf_bytes = await generate_print_channel(request, db, announcement)
        if pdf_bytes is not None:
            result["ok"] = True
            result["link"] = f"/announcements/{announcement.id}/print/download"
            downloads.append({"filename": _print_pdf_download_name(announcement),
                              "data": base64.b64encode(pdf_bytes).decode("ascii")})
    elif channel == AnnouncementChannel.LETTER:
        result["count"] = len((await resolve_audience(db, announcement)).letter_groups)
        pdf_bytes = await generate_letter_channel(db, announcement)
        if pdf_bytes is not None:
            result["ok"] = True
            downloads.append({"filename": _download_name(announcement, "_letters"),
                              "data": base64.b64encode(pdf_bytes).decode("ascii")})

    if not result["ok"] or channel == AnnouncementChannel.PRINT:
        await db.refresh(announcement, attribute_names=["deliveries"])
        delivery = announcement.delivery_for(channel)
        result["detail"] = delivery.error_message if delivery is not None else None
    return result


@router.post("/compose")
async def announcement_compose(
    request: Request, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db),
):
    """Saves the popup's message and, depending on the button, sends a
    test email, stops there (draft), or runs the ticked channels."""
    user = await require_admin(request, db)
    form = await request.form()
    action = form.get("action")
    if action not in ("send", "draft", "test"):
        raise HTTPException(status_code=400, detail="Unknown action")

    draft_id = (form.get("announcement_id") or "").strip()
    if draft_id:
        announcement = await _get_announcement_or_404(db, draft_id)
        if announcement.deliveries:
            # Something already went out: from here on it's the send
            # page's job (ADR 0087), not a fresh message's.
            raise HTTPException(status_code=409, detail="This message was already sent; open it to continue")
        try:
            await _update_compose_draft(announcement, form)
        except _FormRejected as e:
            await db.rollback()
            announcement = await _get_announcement_or_404(db, draft_id)
            context = await _compose_context(request, db, user, announcement)
            return _compose_form_response(context, 400, error=e.error, entered=_entered_values(form),
                                          test_email_value=form.get("test_email") or user.email)
    else:
        picked = await _picked_audience(request, db, form)
        audience_query = None if picked is not None else _targeted_audience_query(form)
        try:
            announcement = await _announcement_from_form(form, user, picked, audience_query)
        except _FormRejected as e:
            preview = Announcement()
            if picked is not None:
                picked.apply(preview)
            elif audience_query is not None:
                preview.audience_filter = _filter_from_query_string(audience_query).to_dict()
            context = await _compose_context(request, db, user, preview)
            return _compose_form_response(context, 400, error=e.error, entered=_entered_values(form),
                                          test_email_value=form.get("test_email") or user.email)
        db.add(announcement)
    await db.commit()
    announcement = await _get_announcement_or_404(db, announcement.id)

    if action == "test":
        address = (form.get("test_email") or "").strip()
        test_result = "missing_address"
        if address:
            test_result = "success" if await send_test_email(announcement, db, request, address) else "failed"
        context = await _compose_context(request, db, user, announcement)
        return _compose_form_response(context, test_email_result=test_result,
                                      test_email_value=address or user.email)

    offered = {c["name"] for c in _compose_channels(announcement, await get_active_type(db),
                                                     await resolve_audience(db, announcement))}
    ticked = [c for c in COMPOSE_ORDER if c.name in offered and c.name in form.getlist("channels")]
    results, downloads = [], []
    if action == "send":
        for channel in ticked:
            results.append(await _run_compose_channel(request, db, background_tasks, announcement, channel, downloads))
    html = _render_fragment("announcements/_compose_result.html", {
        "request": request, "user": user, "announcement": announcement, "results": results,
        "draft_only": action == "draft" or not ticked,
    })
    return JSONResponse({"state": "done", "html": html, "downloads": downloads,
                         "edit_url": f"/announcements/{announcement.id}/edit"})


# ---------------------------------------------------------------------------
# Edit
# ---------------------------------------------------------------------------

@router.get("/{announcement_id}/edit", response_class=HTMLResponse)
async def announcement_edit_form(
    announcement_id: str, request: Request, db: AsyncSession = Depends(get_db),
):
    user = await require_admin(request, db)
    announcement = await _get_announcement_or_404(db, announcement_id)
    return templates.TemplateResponse("announcements/form.html", {
        "request": request, "user": user, "announcement": announcement, "error": None,
        **await _form_context(db, announcement), **await _audience_context(db, announcement),
        "test_email_result": request.query_params.get("test_email_result"),
        "test_email_address": request.query_params.get("test_email_address"),
    })


@router.post("/{announcement_id}/edit")
async def announcement_update(
    announcement_id: str, request: Request, db: AsyncSession = Depends(get_db),
):
    user = await require_admin(request, db)
    announcement = await _get_announcement_or_404(db, announcement_id)
    form = await request.form()

    title = (form.get("title") or "").strip()
    body_markdown = (form.get("body_markdown") or "").strip()
    print_text_override = (form.get("print_text_override") or "").strip() or None
    remove_image = form.get("remove_image", "") == "true"
    image_upload = form.get("image")
    entered = _entered_values(form)

    if not title or not body_markdown:
        return templates.TemplateResponse("announcements/form.html", {
            "request": request, "user": user, "announcement": announcement, "entered": entered,
            "error": "missing_fields", **await _form_context(db, announcement), **await _audience_context(db, announcement),
        }, status_code=400)

    if remove_image:
        _delete_announcement_image(announcement.image_filename)
        announcement.image_filename = None
    elif image_upload is not None and getattr(image_upload, "filename", ""):
        try:
            new_filename = await _save_announcement_image(image_upload)
            _delete_announcement_image(announcement.image_filename)
            announcement.image_filename = new_filename
        except ValueError as e:
            return templates.TemplateResponse("announcements/form.html", {
                "request": request, "user": user, "announcement": announcement, "entered": entered,
                "error": str(e), **await _form_context(db, announcement), **await _audience_context(db, announcement),
            }, status_code=400)

    announcement.title = title
    announcement.body_markdown = body_markdown
    announcement.body_html = render_markdown_to_html(body_markdown)
    announcement.print_text_override = print_text_override
    if not announcement.is_targeted:
        announcement.print_qr_code = form.get("print_qr_code") == "true"
    announcement.summary = _clean_summary(form.get("summary"))
    # No image, no alt text: a stale one would otherwise resurface on the
    # next upload.
    announcement.image_alt = _clean_image_alt(form.get("image_alt")) if announcement.image_filename else None
    if announcement.is_targeted:
        announcement.letters_for_all = form.get("letters_for_all") == "true"

    await db.commit()
    return RedirectResponse(url=f"/announcements/{announcement.id}/edit", status_code=303)


# ---------------------------------------------------------------------------
# Channel: email
# ---------------------------------------------------------------------------

async def start_email_channel(
    request: Request, db: AsyncSession, background_tasks: BackgroundTasks, announcement: Announcement,
) -> int:
    """Marks the EMAIL delivery SENDING (or FAILED with nobody to send
    to), commits, and schedules the paced send. Returns the recipient
    count. Shared by the send page and the compose popup (issue #345);
    the caller has checked the channel is available."""
    delivery, recipient_count = await start_paced_email_send(announcement, db)
    _record_delivered_content(announcement, delivery)
    await db.commit()
    if recipient_count > 0:
        base_url = str(request.base_url).rstrip("/")
        background_tasks.add_task(run_paced_email_send, announcement.id, base_url)
    return recipient_count


@router.post("/{announcement_id}/send/email")
async def announcement_send_email(
    announcement_id: str, request: Request, background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    await require_admin(request, db)
    announcement = await _get_announcement_or_404(db, announcement_id)

    # 409 both while a send is in progress and after a successful one --
    # the email goes out once (ADR 0087); only a FAILED send can be retried.
    _require_channel_action_available(announcement, AnnouncementChannel.EMAIL)
    await start_email_channel(request, db, background_tasks, announcement)
    return RedirectResponse(url=f"/announcements/{announcement.id}/edit", status_code=303)


@router.post("/{announcement_id}/send/test-email")
async def announcement_send_test_email(
    announcement_id: str, request: Request, db: AsyncSession = Depends(get_db),
):
    """Sends the current content to a single address for review. Does
    not touch AnnouncementDelivery -- a test send is never mistaken for
    (or counted as) a real one."""
    await require_admin(request, db)
    announcement = await _get_announcement_or_404(db, announcement_id)
    form = await request.form()
    address = (form.get("test_email") or "").strip()

    result = "missing_address"
    if address:
        sent = await send_test_email(announcement, db, request, address)
        result = "success" if sent else "failed"

    return RedirectResponse(
        url=f"/announcements/{announcement.id}/edit?test_email_result={result}&test_email_address={address}",
        status_code=303,
    )


# ---------------------------------------------------------------------------
# Channel: blog (the club's website, through the active connector)
# ---------------------------------------------------------------------------

_IMAGE_MIME_BY_EXTENSION = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}


def _read_announcement_image(announcement: Announcement) -> tuple:
    """Returns (bytes, filename, mime) for the announcement's image, or
    (None, None, None) if it has none / the file is missing on disk."""
    if not announcement.image_filename:
        return None, None, None
    path = UPLOAD_DIR / announcement.image_filename
    if not path.exists():
        return None, None, None
    extension = path.suffix.lower()
    mime = _IMAGE_MIME_BY_EXTENSION.get(extension, "application/octet-stream")
    return path.read_bytes(), announcement.image_filename, mime


async def push_website_draft(db: AsyncSession, announcement: Announcement) -> AnnouncementDelivery:
    """Creates the announcement's website draft, or updates the existing
    one in place, through whichever connector is active on Admin ->
    Integrations -> Website. Records the outcome on the BLOG delivery
    and commits. Shared by the web button and the REST API."""
    _require_channel_action_available(announcement, AnnouncementChannel.BLOG)

    delivery = announcement.delivery_for(AnnouncementChannel.BLOG)
    if delivery is None:
        delivery = AnnouncementDelivery(announcement_id=announcement.id, channel=AnnouncementChannel.BLOG)
        db.add(delivery)

    try:
        connector = await get_active_connector(db)
    except BlogPublishError as e:
        connector, setup_error = None, str(e)
    else:
        setup_error = "No website is set up yet -- choose one under Admin -> Integrations -> Website."
    if connector is None:
        delivery.status = AnnouncementDeliveryStatus.FAILED
        delivery.error_message = setup_error
        delivery.sent_at = datetime.now(timezone.utc)
        await db.commit()
        return delivery

    image_bytes, image_filename, image_mime = _read_announcement_image(announcement)
    content = DraftContent(
        title=announcement.title, markdown=announcement.body_markdown, html=announcement.body_html,
        image_bytes=image_bytes, image_filename=image_filename, image_mime=image_mime,
        image_alt=(announcement.image_alt or announcement.title) if image_bytes else "",
        summary=announcement.summary or "",
        language=await load_current_language(db), source_id=announcement.id,
    )

    try:
        result = None
        if delivery.external_id:
            # A draft already exists: update it in place rather than
            # leaving a duplicate behind on the website. The image is
            # only re-sent if it changed, so an unchanged one doesn't
            # pile up copies in the website's media library.
            try:
                result = await connector.update_post(
                    delivery.external_id, content,
                    image_changed=delivery.image_filename != announcement.image_filename,
                    alt_changed=delivery.image_alt != announcement.image_alt,
                )
            except BlogPostNotFoundError:
                result = None  # deleted on the website by hand -- start over below
        if result is None:
            result = await connector.publish_draft(content)
        delivery.status = AnnouncementDeliveryStatus.SENT
        delivery.external_reference = result.edit_url or result.location
        delivery.external_id = result.post_id
        delivery.error_message = None
        _record_delivered_content(announcement, delivery)
    except BlogPublishError as e:
        delivery.status = AnnouncementDeliveryStatus.FAILED
        delivery.error_message = str(e)
    finally:
        await connector.aclose()

    delivery.sent_at = datetime.now(timezone.utc)
    await db.commit()
    return delivery


@router.post("/{announcement_id}/send/blog")
async def announcement_send_blog(
    announcement_id: str, request: Request, db: AsyncSession = Depends(get_db),
):
    await require_admin(request, db)
    announcement = await _get_announcement_or_404(db, announcement_id)
    await push_website_draft(db, announcement)
    return RedirectResponse(url=f"/announcements/{announcement.id}/edit", status_code=303)


# ---------------------------------------------------------------------------
# Channel: print
# ---------------------------------------------------------------------------

async def _get_public_blog_url(db: AsyncSession, announcement: Announcement) -> Optional[str]:
    """Returns the public URL of the announcement's website post, or
    None if there isn't one yet (never sent, or still a draft). Always
    asks the website live through the active connector rather than
    trusting anything cached -- see
    WebsiteConnector.get_public_url_if_published."""
    blog_delivery = announcement.delivery_for(AnnouncementChannel.BLOG)
    if blog_delivery is None or blog_delivery.status != AnnouncementDeliveryStatus.SENT or not blog_delivery.external_id:
        return None

    try:
        connector = await get_active_connector(db)
    except BlogPublishError:
        return None
    if connector is None:
        return None
    try:
        return await connector.get_public_url_if_published(blog_delivery.external_id)
    finally:
        await connector.aclose()


async def _print_qr_url(request: Request, db: AsyncSession, announcement: Announcement) -> Optional[str]:
    """What the printed QR code points to (ADR 0133): the announcement's
    own short link /a/<token>, which forwards to the website post once
    that's public. So the notice can be printed while the post is still
    a draft, and a slug changed on the website doesn't break the code.
    None without a website connector: then there's no post to point to.
    The token is created on first use and never changes, so every PDF of
    the announcement carries the same link."""
    if await get_active_type(db) is None:
        return None
    if not announcement.public_link_token:
        announcement.public_link_token = secrets.token_urlsafe(16)
    return f"{str(request.base_url).rstrip('/')}/a/{announcement.public_link_token}"


@link_router.get("/{token}", response_class=HTMLResponse)
async def announcement_short_link(token: str, request: Request, db: AsyncSession = Depends(get_db)):
    """Public. Forwards to the website post once it's published (asked
    live, like everything about the post's URL), else a short "not online
    yet" page. Says nothing about the announcement itself: not its
    title, not whether the token belongs to one -- an unknown token gets
    the same page as a draft. Rate-limited because each hit asks the
    website."""
    key = client_ip_key(request, "announcement_link")
    if not check_and_record(key, _LINK_RATE_LIMIT_MAX, _LINK_RATE_LIMIT_WINDOW_SECONDS):
        raise HTTPException(status_code=429, detail="Too many requests, please try again later")

    announcement = None
    if 16 <= len(token) <= 43:
        announcement = (await db.execute(
            select(Announcement).where(Announcement.public_link_token == token)
            .options(selectinload(Announcement.deliveries))
        )).scalar_one_or_none()
    if announcement is not None and not announcement.is_targeted:
        url = await _get_public_blog_url(db, announcement)
        if url and urllib.parse.urlsplit(url).scheme in ("http", "https"):
            return RedirectResponse(url=url, status_code=302)
    return templates.TemplateResponse(
        "announcements/not_online.html", {"request": request, "user": None},
        headers={"Cache-Control": "no-store"},
    )


async def _print_byline(db: AsyncSession, announcement: Announcement, language: str) -> str:
    """Issue #261: "Published on <date> by <name>" under the print
    notice's title. The date is the day the PDF is generated, not the
    announcement's creation date (kermie's call): the notice says when
    it went up on the board. The author is the creating user's real
    name only -- their groups were tried and dropped as too much.
    Without an author (account deleted), just the date."""
    today = date.today().strftime("%d.%m.%Y")
    author = await db.get(User, announcement.created_by_id) if announcement.created_by_id else None
    if author is None:
        return translate("announcements.print.byline_date_only", language, date=today)
    return translate("announcements.print.byline", language, date=today, author=author.name)


async def _save_print_pdf_to_cloud(
    request: Request, db: AsyncSession, announcement: Announcement, pdf_bytes: bytes,
) -> Optional[str]:
    """Issue #262: also put the generated PDF into the cloud folder
    chosen on the integrations page. The browser download happens
    either way -- a failed upload never costs the admin the PDF, it's
    only noted on the print delivery. Returns that note, or None when no
    folder is set up (cloud storage module off, or no folder chosen).
    The date in the file name keeps earlier notices; regenerating on
    the same day replaces that day's file."""
    if not request.state.module_flags.get("cloud_storage"):
        return None
    folder = await load_print_cloud_folder(db)
    if not folder:
        return None
    filename = _download_name(announcement, suffix=f"_{date.today().isoformat()}")
    provider = await get_cloud_storage_provider(db)
    if provider is None:
        return "Not saved to the cloud: no cloud storage is configured."
    try:
        await provider.upload_file(folder, filename, pdf_bytes)
    except CloudStorageError as e:
        return f"Not saved to the cloud folder '{folder}': {e}"
    finally:
        await provider.aclose()
    return f"Saved to the cloud as {folder}/{filename}."


async def generate_print_channel(request: Request, db: AsyncSession, announcement: Announcement) -> Optional[bytes]:
    """Renders the one-page notice, stores it (and copies it to the cloud
    folder if one is set), records the PRINT delivery and commits.
    Returns the PDF, or None when the text can't be made to fit (the
    delivery is FAILED then). Shared by the send page and the compose
    popup (issue #345); the caller has checked the channel is available."""
    delivery = announcement.delivery_for(AnnouncementChannel.PRINT)
    if delivery is None:
        delivery = AnnouncementDelivery(announcement_id=announcement.id, channel=AnnouncementChannel.PRINT)
        db.add(delivery)

    branding = await load_branding(db)
    logo_path = Path("app" + branding["logo_url"]) if branding["logo_url"] else None
    image_path = UPLOAD_DIR / announcement.image_filename if announcement.image_filename else None
    qr_url = await _print_qr_url(request, db, announcement)
    footer_context = await load_org_footer_context(db, branding["club_name"])
    language = await load_current_language(db)
    byline = await _print_byline(db, announcement, language)

    try:
        result = render_announcement_print_pdf(
            announcement, footer_context, logo_path, image_path, qr_url, language, byline,
        )
    except PrintTooLongError as e:
        delivery.status = AnnouncementDeliveryStatus.FAILED
        delivery.error_message = str(e)
        delivery.sent_at = datetime.now(timezone.utc)
        await db.commit()
        return None

    PRINT_PDF_DIR.mkdir(parents=True, exist_ok=True)
    pdf_filename = f"{uuid.uuid4()}.pdf"
    (PRINT_PDF_DIR / pdf_filename).write_bytes(result.pdf_bytes)
    _delete_print_pdf(delivery.pdf_filename)
    delivery.pdf_filename = pdf_filename

    delivery.status = AnnouncementDeliveryStatus.SENT
    delivery.sent_at = datetime.now(timezone.utc)
    # Recorded after rendering: a render that had to shorten the text
    # has just auto-filled print_text_override, and that shortened
    # version is what this PDF actually contains.
    _record_delivered_content(announcement, delivery)
    wants_qr = result.was_shortened or announcement.print_qr_code
    delivery.qr_pending = wants_qr and not result.qr_included
    if result.was_shortened and result.qr_included:
        delivery.error_message = "Text was shortened automatically to fit one page; a QR code linking to the website post was added."
    elif result.was_shortened:
        delivery.error_message = "Text was shortened automatically to fit one page. No QR code was added since there is no website to link to."
    elif wants_qr and not result.qr_included:
        delivery.error_message = "No QR code was added since there is no website to link to."
    else:
        delivery.error_message = None
    cloud_note = await _save_print_pdf_to_cloud(request, db, announcement, result.pdf_bytes)
    if cloud_note:
        delivery.error_message = f"{delivery.error_message} {cloud_note}" if delivery.error_message else cloud_note
    await db.commit()

    return result.pdf_bytes


@router.post("/{announcement_id}/print")
async def announcement_generate_print_pdf(
    announcement_id: str, request: Request, db: AsyncSession = Depends(get_db),
):
    await require_admin(request, db)
    announcement = await _get_announcement_or_404(db, announcement_id)
    _require_channel_action_available(announcement, AnnouncementChannel.PRINT)
    pdf_bytes = await generate_print_channel(request, db, announcement)
    if pdf_bytes is None:
        return RedirectResponse(url=f"/announcements/{announcement.id}/edit", status_code=303)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{_print_pdf_download_name(announcement)}"'},
    )


def _download_name(announcement: Announcement, suffix: str = "") -> str:
    """ASCII-only file name from the title: it goes into a
    Content-Disposition header, where a quote, CR/LF or a character
    outside latin-1 ("—", "€") breaks the response (see the header
    sharp edge in CLAUDE.md)."""
    slug = re.sub(r"[^A-Za-z0-9._-]+", "_", announcement.title[:50]).strip("._") or "announcement"
    return f"{slug}{suffix}.pdf"


def _print_pdf_download_name(announcement: Announcement) -> str:
    return _download_name(announcement)


@router.get("/{announcement_id}/print/download")
async def announcement_download_print_pdf(
    announcement_id: str, request: Request, db: AsyncSession = Depends(get_db),
):
    """The last generated PDF, as stored -- no regeneration, so it's
    byte-identical to what was printed."""
    await require_admin(request, db)
    announcement = await _get_announcement_or_404(db, announcement_id)
    delivery = announcement.delivery_for(AnnouncementChannel.PRINT)
    if delivery is None or not delivery.pdf_filename or not (PRINT_PDF_DIR / delivery.pdf_filename).exists():
        raise HTTPException(status_code=404, detail="No stored PDF for this announcement")
    return FileResponse(
        PRINT_PDF_DIR / delivery.pdf_filename, media_type="application/pdf",
        filename=_print_pdf_download_name(announcement),
    )


# ---------------------------------------------------------------------------
# Channel: letter (messages to filtered members only, issue #242)
# ---------------------------------------------------------------------------

async def generate_letter_channel(db: AsyncSession, announcement: Announcement) -> Optional[bytes]:
    """One PDF with an addressed letter per member who gets one (no
    email address, or everyone with letters_for_all). Not stored (see
    the module docstring); the LETTER delivery row only records when,
    for how many, and which content. Returns None (delivery FAILED) when
    nobody gets a letter. Commits. Shared by the send page and the
    compose popup (issue #345)."""
    delivery = announcement.delivery_for(AnnouncementChannel.LETTER)
    if delivery is None:
        delivery = AnnouncementDelivery(announcement_id=announcement.id, channel=AnnouncementChannel.LETTER)
        db.add(delivery)

    audience = await resolve_audience(db, announcement)
    recipients = audience.letter_groups
    delivery.sent_at = datetime.now(timezone.utc)
    if not recipients:
        delivery.status = AnnouncementDeliveryStatus.FAILED
        delivery.error_message = "No letters to generate: nobody in the selection both lacks an email address and has a postal address."
        await db.commit()
        return None

    branding = await load_branding(db)
    logo_path = Path("app" + branding["logo_url"]) if branding["logo_url"] else None
    language = await load_current_language(db)
    references = [translate("announcements.parcels.reference", language, plot=plot) for plot in audience.letter_refs]
    pdf_bytes = render_announcement_letters_pdf(
        announcement, recipients, await load_org_footer_context(db, branding["club_name"]),
        logo_path, await load_current_region(db), language, references=references or None,
    )
    delivery.status = AnnouncementDeliveryStatus.SENT
    # Only the count -- names stay out of the database like the PDF itself.
    delivery.error_message = f"{len(recipients)} letter(s) generated."
    _record_delivered_content(announcement, delivery)
    await db.commit()
    return pdf_bytes


@router.post("/{announcement_id}/letters")
async def announcement_generate_letters(
    announcement_id: str, request: Request, db: AsyncSession = Depends(get_db),
):
    await require_admin(request, db)
    announcement = await _get_announcement_or_404(db, announcement_id)
    _require_channel_action_available(announcement, AnnouncementChannel.LETTER)
    pdf_bytes = await generate_letter_channel(db, announcement)
    if pdf_bytes is None:
        return RedirectResponse(url=f"/announcements/{announcement.id}/edit", status_code=303)
    return Response(
        content=pdf_bytes, media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{_download_name(announcement, "_letters")}"'},
    )


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------

@router.post("/{announcement_id}/delete")
async def announcement_delete(
    announcement_id: str, request: Request, db: AsyncSession = Depends(get_db),
):
    await require_admin(request, db)
    announcement = await _get_announcement_or_404(db, announcement_id)
    _delete_announcement_image(announcement.image_filename)
    print_delivery = announcement.delivery_for(AnnouncementChannel.PRINT)
    if print_delivery is not None:
        _delete_print_pdf(print_delivery.pdf_filename)
    await db.delete(announcement)
    await db.commit()
    return RedirectResponse(url="/announcements/", status_code=303)
