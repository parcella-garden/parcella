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
- blog: publishes a draft post to WordPress (app.blog_publisher),
  using whatever credentials are configured under Admin -> Integrations;
  after a content change, updates that same post instead of creating
  a second one.
- print: renders a one-page branded PDF (app.print_publisher),
  auto-shortening the text and adding a QR code if it doesn't fit as-is
  -- see app.print_publisher's module docstring for the full logic.

Restricted to board/admin (require_admin), same reasoning as the
public_signup_api's Integrations page: this creates content that will
be pushed to a public blog and to every member's inbox, so authoring
it isn't a general member-facing feature.
"""
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Request, Depends, HTTPException, UploadFile, BackgroundTasks, Response
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import Announcement, AnnouncementDelivery, AnnouncementChannel, AnnouncementDeliveryStatus
from app.auth import require_admin
from app.module_flags import require_module
from app.announcement_utils import render_markdown_to_html, likely_fits_one_print_page, channel_fingerprint
from app.announcement_mailer import start_paced_email_send, run_paced_email_send, send_test_email
from app.blog_publisher import get_wordpress_publisher, BlogPublishError, BlogPostNotFoundError
from app.print_publisher import render_announcement_print_pdf, PrintTooLongError
from app.branding import load_branding
from app.pdf_chrome import load_org_footer_context
from app.i18n import load_current_language
from app.templating import templates

router = APIRouter(
    prefix="/announcements",
    tags=["announcements"],
    dependencies=[Depends(require_module("announcements"))],
)

UPLOAD_DIR = Path("app/static/uploads/announcements")
ALLOWED_IMAGE_TYPES = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/webp": ".webp",
}
MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB
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
    )


def _content_changed_since(announcement: Announcement, delivery: AnnouncementDelivery) -> bool:
    return (
        delivery.content_fingerprint != _current_fingerprint(announcement, delivery.channel)
        or delivery.image_filename != announcement.image_filename
    )


def _record_delivered_content(announcement: Announcement, delivery: AnnouncementDelivery) -> None:
    delivery.content_fingerprint = _current_fingerprint(announcement, delivery.channel)
    delivery.image_filename = announcement.image_filename


def _channel_action_available(announcement: Announcement, channel: AnnouncementChannel) -> bool:
    """Whether a channel's action button (send email / create-or-update
    blog post / create PDF) makes sense right now -- enforced here on
    the server too, not just by hiding the button (ADR 0087):

    - never attempted, or last attempt FAILED -> yes (first try / retry)
    - SENDING -> no
    - EMAIL, SENT -> never again: every member already has it, and a
      second full send is not something to offer after an edit.
    - BLOG, SENT -> only once title/body/image changed since.
    - PRINT, SENT -> once title/body/print text/image changed since,
      when the stored PDF is gone, or when it was shortened without a
      QR code and a blog post exists that may since have been published.
    """
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


def _form_context(announcement: Optional[Announcement]) -> dict:
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
        "fits_one_page": likely_fits_one_print_page(
            announcement.print_text_override or announcement.body_markdown
        ),
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

@router.get("/new", response_class=HTMLResponse)
async def announcement_new_form(request: Request, db: AsyncSession = Depends(get_db)):
    user = await require_admin(request, db)
    return templates.TemplateResponse("announcements/form.html", {
        "request": request, "user": user, "announcement": None, "error": None,
    })


@router.post("/new")
async def announcement_create(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user = await require_admin(request, db)
    form = await request.form()

    title = (form.get("title") or "").strip()
    body_markdown = (form.get("body_markdown") or "").strip()
    image_upload = form.get("image")

    if not title or not body_markdown:
        return templates.TemplateResponse("announcements/form.html", {
            "request": request, "user": user, "announcement": None,
            "error": "missing_fields",
        }, status_code=400)

    image_filename = None
    if image_upload is not None and getattr(image_upload, "filename", ""):
        try:
            image_filename = await _save_announcement_image(image_upload)
        except ValueError as e:
            return templates.TemplateResponse("announcements/form.html", {
                "request": request, "user": user, "announcement": None,
                "error": str(e),
            }, status_code=400)

    announcement = Announcement(
        title=title,
        body_markdown=body_markdown,
        body_html=render_markdown_to_html(body_markdown),
        image_filename=image_filename,
        created_by_id=user.id,
    )
    db.add(announcement)
    await db.commit()

    return RedirectResponse(url=f"/announcements/{announcement.id}/edit", status_code=303)


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
        **_form_context(announcement),
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

    if not title or not body_markdown:
        return templates.TemplateResponse("announcements/form.html", {
            "request": request, "user": user, "announcement": announcement,
            "error": "missing_fields", **_form_context(announcement),
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
                "request": request, "user": user, "announcement": announcement,
                "error": str(e), **_form_context(announcement),
            }, status_code=400)

    announcement.title = title
    announcement.body_markdown = body_markdown
    announcement.body_html = render_markdown_to_html(body_markdown)
    announcement.print_text_override = print_text_override

    await db.commit()
    return RedirectResponse(url=f"/announcements/{announcement.id}/edit", status_code=303)


# ---------------------------------------------------------------------------
# Channel: email
# ---------------------------------------------------------------------------

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

    delivery, recipient_count = await start_paced_email_send(announcement, db)
    _record_delivered_content(announcement, delivery)
    await db.commit()

    if recipient_count > 0:
        base_url = str(request.base_url).rstrip("/")
        background_tasks.add_task(run_paced_email_send, announcement.id, base_url)

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
# Channel: blog (WordPress)
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


@router.post("/{announcement_id}/send/blog")
async def announcement_send_blog(
    announcement_id: str, request: Request, db: AsyncSession = Depends(get_db),
):
    await require_admin(request, db)
    announcement = await _get_announcement_or_404(db, announcement_id)
    _require_channel_action_available(announcement, AnnouncementChannel.BLOG)

    delivery = announcement.delivery_for(AnnouncementChannel.BLOG)
    if delivery is None:
        delivery = AnnouncementDelivery(announcement_id=announcement.id, channel=AnnouncementChannel.BLOG)
        db.add(delivery)

    publisher = await get_wordpress_publisher(db)
    if publisher is None:
        delivery.status = AnnouncementDeliveryStatus.FAILED
        delivery.error_message = "WordPress isn't configured yet -- add the site URL, username, and Application Password under Admin -> Settings."
        delivery.sent_at = datetime.now(timezone.utc)
        await db.commit()
        return RedirectResponse(url=f"/announcements/{announcement.id}/edit", status_code=303)

    image_bytes, image_filename, image_mime = _read_announcement_image(announcement)

    try:
        result = None
        if delivery.external_id:
            # A post already exists: update it in place rather than
            # leaving a duplicate behind in WordPress. The image is only
            # re-uploaded if it changed, so an unchanged one doesn't pile
            # up copies in the WordPress media library.
            image_changed = delivery.image_filename != announcement.image_filename
            try:
                result = await publisher.update_post(
                    delivery.external_id, title=announcement.title, html_content=announcement.body_html,
                    image_bytes=image_bytes if image_changed else None,
                    image_filename=image_filename, image_mime=image_mime,
                    clear_image=image_changed and image_bytes is None,
                )
            except BlogPostNotFoundError:
                result = None  # deleted in WordPress by hand -- start over below
        if result is None:
            result = await publisher.publish_draft(
                title=announcement.title, html_content=announcement.body_html,
                image_bytes=image_bytes, image_filename=image_filename, image_mime=image_mime,
            )
        delivery.status = AnnouncementDeliveryStatus.SENT
        delivery.external_reference = result.edit_url
        delivery.external_id = str(result.post_id)
        delivery.error_message = None
        _record_delivered_content(announcement, delivery)
    except BlogPublishError as e:
        delivery.status = AnnouncementDeliveryStatus.FAILED
        delivery.error_message = str(e)
    finally:
        await publisher.aclose()

    delivery.sent_at = datetime.now(timezone.utc)
    await db.commit()
    return RedirectResponse(url=f"/announcements/{announcement.id}/edit", status_code=303)


# ---------------------------------------------------------------------------
# Channel: print
# ---------------------------------------------------------------------------

async def _get_public_blog_url(db: AsyncSession, announcement: Announcement) -> Optional[str]:
    """Returns the announcement's blog post's current public URL, or
    None if there isn't one yet (never published to WordPress, or
    published as a draft that hasn't since been made public). Always
    asks WordPress live rather than trusting anything cached -- see
    app.blog_publisher.WordPressPublisher.get_public_url_if_published."""
    blog_delivery = announcement.delivery_for(AnnouncementChannel.BLOG)
    if blog_delivery is None or blog_delivery.status != AnnouncementDeliveryStatus.SENT or not blog_delivery.external_id:
        return None

    publisher = await get_wordpress_publisher(db)
    if publisher is None:
        return None
    try:
        return await publisher.get_public_url_if_published(blog_delivery.external_id)
    finally:
        await publisher.aclose()


@router.post("/{announcement_id}/print")
async def announcement_generate_print_pdf(
    announcement_id: str, request: Request, db: AsyncSession = Depends(get_db),
):
    await require_admin(request, db)
    announcement = await _get_announcement_or_404(db, announcement_id)
    _require_channel_action_available(announcement, AnnouncementChannel.PRINT)

    delivery = announcement.delivery_for(AnnouncementChannel.PRINT)
    if delivery is None:
        delivery = AnnouncementDelivery(announcement_id=announcement.id, channel=AnnouncementChannel.PRINT)
        db.add(delivery)

    branding = await load_branding(db)
    logo_path = Path("app" + branding["logo_url"]) if branding["logo_url"] else None
    image_path = UPLOAD_DIR / announcement.image_filename if announcement.image_filename else None
    public_blog_url = await _get_public_blog_url(db, announcement)
    footer_context = await load_org_footer_context(db, branding["club_name"])
    language = await load_current_language(db)

    try:
        result = render_announcement_print_pdf(
            announcement, footer_context, logo_path, image_path, public_blog_url, language,
        )
    except PrintTooLongError as e:
        delivery.status = AnnouncementDeliveryStatus.FAILED
        delivery.error_message = str(e)
        delivery.sent_at = datetime.now(timezone.utc)
        await db.commit()
        return RedirectResponse(url=f"/announcements/{announcement.id}/edit", status_code=303)

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
    delivery.qr_pending = result.was_shortened and not result.qr_included
    if result.was_shortened and result.qr_included:
        delivery.error_message = "Text was shortened automatically to fit one page; a QR code linking to the published blog post was added."
    elif result.was_shortened:
        delivery.error_message = "Text was shortened automatically to fit one page. No QR code was added since the blog post isn't published yet."
    else:
        delivery.error_message = None
    await db.commit()

    return Response(
        content=result.pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{_print_pdf_download_name(announcement)}"'},
    )


def _print_pdf_download_name(announcement: Announcement) -> str:
    return f"{announcement.title[:50].strip().replace(' ', '_') or 'announcement'}.pdf"


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
