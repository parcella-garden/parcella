"""
Tests for the announcements module foundation (see
docs/module-announcements.md): authoring an Announcement (Markdown body,
image, optional print override) and its module-flag gating. Sending to
channels (blog/email/PDF) and when each channel's action is offered
again (ADR 0087) are covered further down.

Uses the web UI's cookie-based session login, since the announcements
router is a traditional web-form router (same reasoning as
tests/test_calendar.py), plus the JWT API to toggle the module flag
(same pattern as tests/test_public_api.py, since "announcements" also
defaults to False).
"""
import pytest

from tests.conftest import login, auth_header


@pytest.fixture(autouse=True)
def _print_pdfs_in_tmp(monkeypatch, tmp_path):
    # Generated print PDFs are stored on disk now (ADR 0087); keep them
    # out of the real, shared app/static/uploads/ directory.
    monkeypatch.setattr("app.routers.announcements.PRINT_PDF_DIR", tmp_path / "print")


async def web_login(client, email: str, password: str = "testpasswort123") -> None:
    response = await client.post("/auth/login", data={"email": email, "password": password})
    assert response.status_code in (302, 303)


async def _enable_module(client, headers):
    response = await client.put(
        "/api/v1/club-settings/modul_announcements",
        json={"value": "true"},
        headers=headers,
    )
    assert response.status_code == 200, response.text


async def test_module_disabled_by_default(client, admin_user):
    # No flag flip here -- confirms the security-relevant default is
    # actually False, matching MODULE_DEFAULTS in app/module_flags.py.
    await web_login(client, "admin@example.com")
    response = await client.get("/announcements/")
    assert response.status_code == 404


async def test_create_and_edit_announcement(client, admin_user):
    token = await login(client, "admin@example.com")
    await _enable_module(client, auth_header(token))
    await web_login(client, "admin@example.com")

    create = await client.post(
        "/announcements/new",
        data={
            "title": "Autumn work session",
            "body_markdown": "Please join us **Saturday** for leaf clearing.",
        },
    )
    assert create.status_code == 303
    edit_url = create.headers["location"]
    assert edit_url.startswith("/announcements/") and edit_url.endswith("/edit")
    announcement_id = edit_url.split("/")[2]

    edit_page = await client.get(edit_url)
    assert edit_page.status_code == 200
    assert "Autumn work session" in edit_page.text

    # body_html must be derived from body_markdown (bold -> <strong>),
    # not just stored/echoed verbatim.
    from app.database import AsyncSessionLocal
    from app.models import Announcement
    from sqlalchemy import select

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Announcement).where(Announcement.id == announcement_id))
        announcement = result.scalar_one()
        assert "<strong>Saturday</strong>" in announcement.body_html

    update = await client.post(
        edit_url,
        data={
            "title": "Autumn work session (updated)",
            "body_markdown": "Please join us **Saturday** for leaf clearing.",
            "print_text_override": "Join us Saturday for leaf clearing.",
        },
    )
    assert update.status_code == 303

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Announcement).where(Announcement.id == announcement_id))
        announcement = result.scalar_one()
        assert announcement.title == "Autumn work session (updated)"
        assert announcement.print_text_override == "Join us Saturday for leaf clearing."


async def test_missing_title_or_body_is_rejected(client, admin_user):
    token = await login(client, "admin@example.com")
    await _enable_module(client, auth_header(token))
    await web_login(client, "admin@example.com")

    response = await client.post("/announcements/new", data={"title": "", "body_markdown": ""})
    assert response.status_code == 400

    from app.database import AsyncSessionLocal
    from app.models import Announcement
    from sqlalchemy import select

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Announcement))
        assert result.scalars().all() == []


async def test_delete_announcement(client, admin_user):
    token = await login(client, "admin@example.com")
    await _enable_module(client, auth_header(token))
    await web_login(client, "admin@example.com")

    create = await client.post(
        "/announcements/new",
        data={"title": "To be deleted", "body_markdown": "Temporary content."},
    )
    announcement_id = create.headers["location"].split("/")[2]

    delete = await client.post(f"/announcements/{announcement_id}/delete")
    assert delete.status_code == 303

    from app.database import AsyncSessionLocal
    from app.models import Announcement
    from sqlalchemy import select

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Announcement).where(Announcement.id == announcement_id))
        assert result.scalar_one_or_none() is None


async def test_readonly_role_cannot_access_announcements(client, admin_user):
    """require_admin permits ADMIN and BOARD (board_user in conftest is
    already covered implicitly by the other tests, which all use
    admin_user); READONLY is the role that should actually be refused,
    same boundary as the Integrations page."""
    from app.database import AsyncSessionLocal
    from app.models import User, UserRole, ClubSetting
    from app.auth import hash_password

    async with AsyncSessionLocal() as session:
        session.add(ClubSetting(key="modul_announcements", value="true", description="test"))
        session.add(User(
            email="readonly@example.com", name="Test-Readonly",
            password_hash=hash_password("testpasswort123"), role=UserRole.READONLY,
        ))
        await session.commit()

    await web_login(client, "readonly@example.com")
    response = await client.get("/announcements/")
    assert response.status_code == 403


# ---------------------------------------------------------------------------
# Email channel
# ---------------------------------------------------------------------------

async def _create_resident_with_email(
    session, *, plot_number: str, email: str, email_notifications: bool = True,
) -> None:
    """Creates a Parcel + current-resident Member + email address --
    a parcel is no longer required for get_active_recipient_emails() to
    pick a member up (issue #236), but most of these tests still model
    a typical resident, parcel included."""
    from app.models import Member, MemberEmail, Parcel, MemberParcel

    member = Member(first_name="Gerd", last_name="Mustergärtner", email_notifications=email_notifications)
    parcel = Parcel(plot_number=plot_number)
    session.add_all([member, parcel])
    await session.flush()
    session.add(MemberEmail(member_id=member.id, address=email, is_primary=True))
    session.add(MemberParcel(member_id=member.id, parcel_id=parcel.id))
    await session.commit()


async def test_send_email_reaches_current_residents_with_notifications_enabled(client, admin_user, monkeypatch):
    token = await login(client, "admin@example.com")
    await _enable_module(client, auth_header(token))
    await web_login(client, "admin@example.com")

    from app.database import AsyncSessionLocal

    async with AsyncSessionLocal() as session:
        await _create_resident_with_email(session, plot_number="G1", email="wants-mail@example.com")
        await _create_resident_with_email(
            session, plot_number="G2", email="opted-out@example.com", email_notifications=False,
        )

    create = await client.post(
        "/announcements/new",
        data={"title": "Autumn work session", "body_markdown": "Please join us Saturday."},
    )
    announcement_id = create.headers["location"].split("/")[2]

    sent_to = []

    async def fake_send_email(empfaenger, betreff, html_body, text_body=None, db=None):
        sent_to.append(empfaenger)
        return True

    monkeypatch.setattr("app.announcement_mailer.send_email", fake_send_email)

    send = await client.post(f"/announcements/{announcement_id}/send/email")
    assert send.status_code == 303

    # Only the member with email_notifications=True should have been mailed.
    assert sent_to == ["wants-mail@example.com"]

    from app.models import Announcement, AnnouncementChannel
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Announcement).where(Announcement.id == announcement_id)
            .options(selectinload(Announcement.deliveries))
        )
        announcement = result.scalar_one()
        delivery = announcement.delivery_for(AnnouncementChannel.EMAIL)
        assert delivery.status.value == "SENT"
        assert delivery.error_message is None


async def test_send_email_reaches_member_without_current_parcel(client, admin_user, monkeypatch):
    """issue #236: a member still within their membership period but
    with no current (or no) parcel lease must still receive
    announcements -- club membership, not parcel tenancy, is what
    governs eligibility."""
    token = await login(client, "admin@example.com")
    await _enable_module(client, auth_header(token))
    await web_login(client, "admin@example.com")

    from datetime import date, timedelta
    from app.database import AsyncSessionLocal
    from app.models import Member, MemberEmail, Parcel, MemberParcel

    async with AsyncSessionLocal() as session:
        member = Member(
            first_name="Daniel", last_name="Ohne-Parzelle", email_notifications=True,
            member_until=date.today() + timedelta(days=90),
        )
        parcel = Parcel(plot_number="G016")
        session.add_all([member, parcel])
        await session.flush()
        session.add(MemberEmail(member_id=member.id, address="lease-ended@example.com", is_primary=True))
        # Lease ended in the past -- no current MemberParcel row.
        session.add(MemberParcel(
            member_id=member.id, parcel_id=parcel.id,
            assigned_from=date.today() - timedelta(days=365),
            assigned_until=date.today() - timedelta(days=30),
        ))
        await session.commit()

    create = await client.post(
        "/announcements/new",
        data={"title": "Club news", "body_markdown": "Content."},
    )
    announcement_id = create.headers["location"].split("/")[2]

    sent_to = []

    async def fake_send_email(empfaenger, betreff, html_body, text_body=None, db=None):
        sent_to.append(empfaenger)
        return True

    monkeypatch.setattr("app.announcement_mailer.send_email", fake_send_email)

    send = await client.post(f"/announcements/{announcement_id}/send/email")
    assert send.status_code == 303
    assert sent_to == ["lease-ended@example.com"]


async def test_send_email_with_no_recipients_is_marked_failed(client, admin_user, monkeypatch):
    token = await login(client, "admin@example.com")
    await _enable_module(client, auth_header(token))
    await web_login(client, "admin@example.com")

    create = await client.post(
        "/announcements/new",
        data={"title": "Nobody to tell", "body_markdown": "Content."},
    )
    announcement_id = create.headers["location"].split("/")[2]

    async def fake_send_email(*args, **kwargs):
        raise AssertionError("should not attempt to send with zero recipients")

    monkeypatch.setattr("app.announcement_mailer.send_email", fake_send_email)

    send = await client.post(f"/announcements/{announcement_id}/send/email")
    assert send.status_code == 303

    from app.database import AsyncSessionLocal
    from app.models import Announcement, AnnouncementChannel
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Announcement).where(Announcement.id == announcement_id)
            .options(selectinload(Announcement.deliveries))
        )
        announcement = result.scalar_one()
        delivery = announcement.delivery_for(AnnouncementChannel.EMAIL)
        assert delivery.status.value == "FAILED"
        assert "no recipients" in delivery.error_message.lower()


async def test_send_email_partial_failure_still_counts_as_sent(client, admin_user, monkeypatch):
    token = await login(client, "admin@example.com")
    await _enable_module(client, auth_header(token))
    await web_login(client, "admin@example.com")

    from app.database import AsyncSessionLocal

    async with AsyncSessionLocal() as session:
        await _create_resident_with_email(session, plot_number="G1", email="ok@example.com")
        await _create_resident_with_email(session, plot_number="G2", email="bounces@example.com")

    create = await client.post(
        "/announcements/new",
        data={"title": "Partial send", "body_markdown": "Content."},
    )
    announcement_id = create.headers["location"].split("/")[2]

    async def flaky_send_email(empfaenger, betreff, html_body, text_body=None, db=None):
        return empfaenger != "bounces@example.com"

    monkeypatch.setattr("app.announcement_mailer.send_email", flaky_send_email)

    send = await client.post(f"/announcements/{announcement_id}/send/email")
    assert send.status_code == 303

    from app.models import Announcement, AnnouncementChannel
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Announcement).where(Announcement.id == announcement_id)
            .options(selectinload(Announcement.deliveries))
        )
        announcement = result.scalar_one()
        delivery = announcement.delivery_for(AnnouncementChannel.EMAIL)
        assert delivery.status.value == "SENT"
        assert "1 of 2" in delivery.error_message


async def test_email_send_is_paced_in_batches(client, admin_user, monkeypatch):
    """With more recipients than fit in one batch, sending must pause
    between batches rather than firing everything at once -- this is
    the actual point of pacing (avoiding an SMTP relay's rate limit on
    a large roster)."""
    import app.announcement_mailer as mailer

    monkeypatch.setattr(mailer, "EMAIL_BATCH_SIZE", 2)

    token = await login(client, "admin@example.com")
    await _enable_module(client, auth_header(token))
    await web_login(client, "admin@example.com")

    from app.database import AsyncSessionLocal

    async with AsyncSessionLocal() as session:
        for i in range(5):
            await _create_resident_with_email(session, plot_number=f"P{i}", email=f"member{i}@example.com")

    create = await client.post(
        "/announcements/new",
        data={"title": "Big batch", "body_markdown": "Content."},
    )
    announcement_id = create.headers["location"].split("/")[2]

    sent_to = []
    sleep_calls = []

    async def fake_send_email(empfaenger, betreff, html_body, text_body=None, db=None):
        sent_to.append(empfaenger)
        return True

    async def fake_sleep(seconds):
        sleep_calls.append(seconds)

    monkeypatch.setattr(mailer, "send_email", fake_send_email)
    monkeypatch.setattr(mailer.asyncio, "sleep", fake_sleep)

    send = await client.post(f"/announcements/{announcement_id}/send/email")
    assert send.status_code == 303

    # 5 recipients at batch size 2 -> batches of 2, 2, 1 -> 2 pauses
    # between batches, none after the last one.
    assert len(sent_to) == 5
    assert sleep_calls == [mailer.EMAIL_BATCH_PAUSE_SECONDS, mailer.EMAIL_BATCH_PAUSE_SECONDS]

    from app.models import Announcement, AnnouncementChannel
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Announcement).where(Announcement.id == announcement_id)
            .options(selectinload(Announcement.deliveries))
        )
        announcement = result.scalar_one()
        delivery = announcement.delivery_for(AnnouncementChannel.EMAIL)
        assert delivery.status.value == "SENT"


async def test_cannot_start_second_send_while_one_is_in_progress(client, admin_user, monkeypatch):
    import app.announcement_mailer as mailer

    token = await login(client, "admin@example.com")
    await _enable_module(client, auth_header(token))
    await web_login(client, "admin@example.com")

    from app.database import AsyncSessionLocal

    async with AsyncSessionLocal() as session:
        await _create_resident_with_email(session, plot_number="G1", email="one@example.com")

    create = await client.post(
        "/announcements/new",
        data={"title": "In progress", "body_markdown": "Content."},
    )
    announcement_id = create.headers["location"].split("/")[2]

    # Manually put the delivery into SENDING, as if a background send
    # were already underway (rather than racing the real background
    # task, which -- with the in-process ASGI test transport -- would
    # already have finished by the time client.post() returns).
    from app.models import AnnouncementDelivery, AnnouncementChannel, AnnouncementDeliveryStatus

    async with AsyncSessionLocal() as session:
        session.add(AnnouncementDelivery(
            announcement_id=announcement_id, channel=AnnouncementChannel.EMAIL,
            status=AnnouncementDeliveryStatus.SENDING, error_message="0 of 1 sent so far.",
        ))
        await session.commit()

    async def should_not_be_called(*args, **kwargs):
        raise AssertionError("should not attempt to send while already in progress")

    monkeypatch.setattr(mailer, "send_email", should_not_be_called)

    send = await client.post(f"/announcements/{announcement_id}/send/email")
    assert send.status_code == 409


# ---------------------------------------------------------------------------
# Test email (single address, upfront review)
# ---------------------------------------------------------------------------

async def test_send_test_email_to_specific_address(client, admin_user, monkeypatch):
    token = await login(client, "admin@example.com")
    await _enable_module(client, auth_header(token))
    await web_login(client, "admin@example.com")

    create = await client.post(
        "/announcements/new",
        data={"title": "Preview me", "body_markdown": "Some **content**."},
    )
    announcement_id = create.headers["location"].split("/")[2]

    calls = []

    async def fake_send_email(empfaenger, betreff, html_body, text_body=None, db=None):
        calls.append((empfaenger, betreff, html_body))
        return True

    monkeypatch.setattr("app.announcement_mailer.send_email", fake_send_email)

    response = await client.post(
        f"/announcements/{announcement_id}/send/test-email",
        data={"test_email": "reviewer@example.com"},
    )
    assert response.status_code == 303
    assert "test_email_result=success" in response.headers["location"]

    assert len(calls) == 1
    address, subject, html_body = calls[0]
    assert address == "reviewer@example.com"
    assert "Test" in subject
    assert "<strong>content</strong>" in html_body
    assert "test send" in html_body.lower()

    # A test send must not touch AnnouncementDelivery at all.
    from app.database import AsyncSessionLocal
    from app.models import Announcement, AnnouncementChannel
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Announcement).where(Announcement.id == announcement_id)
            .options(selectinload(Announcement.deliveries))
        )
        announcement = result.scalar_one()
        assert announcement.delivery_for(AnnouncementChannel.EMAIL) is None


async def test_send_test_email_failure_is_reported(client, admin_user, monkeypatch):
    token = await login(client, "admin@example.com")
    await _enable_module(client, auth_header(token))
    await web_login(client, "admin@example.com")

    create = await client.post(
        "/announcements/new",
        data={"title": "Preview me", "body_markdown": "Content."},
    )
    announcement_id = create.headers["location"].split("/")[2]

    async def failing_send_email(*args, **kwargs):
        return False

    monkeypatch.setattr("app.announcement_mailer.send_email", failing_send_email)

    response = await client.post(
        f"/announcements/{announcement_id}/send/test-email",
        data={"test_email": "reviewer@example.com"},
    )
    assert response.status_code == 303
    assert "test_email_result=failed" in response.headers["location"]


# ---------------------------------------------------------------------------
# Image upload (regression: image_url must match where the file is
# actually saved, not just parse without error -- a mismatch here
# silently 404s in both the edit page and the email, which looks
# exactly like "the image was never saved" from the outside)
# ---------------------------------------------------------------------------

# Smallest possible valid PNG (1x1 transparent pixel).
_TINY_PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01"
    b"\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
)


async def test_uploaded_image_is_saved_and_actually_servable(client, admin_user):
    """This test deliberately writes a real file under the real, git-
    tracked app/static/uploads/announcements/ (not a monkeypatched temp
    dir), since its whole point is to prove the image_url the app hands
    out actually resolves through the real StaticFiles mount. It must
    therefore delete the announcement (and assert the file is gone) at
    the end, rather than leaving orphaned image files behind on disk --
    that exact leak was previously happening here across every test
    run, since the ephemeral test DB gets torn down but this bind-
    mounted directory doesn't."""
    token = await login(client, "admin@example.com")
    await _enable_module(client, auth_header(token))
    await web_login(client, "admin@example.com")

    create = await client.post(
        "/announcements/new",
        data={"title": "With a picture", "body_markdown": "Content."},
        files={"image": ("garden.png", _TINY_PNG_BYTES, "image/png")},
    )
    assert create.status_code == 303
    announcement_id = create.headers["location"].split("/")[2]

    from pathlib import Path
    from app.database import AsyncSessionLocal
    from app.models import Announcement
    from sqlalchemy import select

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Announcement).where(Announcement.id == announcement_id))
        announcement = result.scalar_one()
        assert announcement.image_filename is not None
        image_url = announcement.image_url
        assert image_url is not None
        image_path = Path("app/static/uploads/announcements") / announcement.image_filename

    # The real assertion: the URL the app hands out for the image must
    # actually resolve through the StaticFiles mount, not just look
    # plausible as a string.
    image_response = await client.get(image_url)
    assert image_response.status_code == 200
    assert image_response.content == _TINY_PNG_BYTES

    # Deleting the announcement must remove the uploaded image file too
    # -- not just the DB row -- so it never orphans on disk.
    delete = await client.post(f"/announcements/{announcement_id}/delete")
    assert delete.status_code == 303
    assert not image_path.exists()


# ---------------------------------------------------------------------------
# Blog channel (WordPress)
#
# No real WordPress site is reachable from this test environment, so
# WordPressPublisher is exercised against an httpx.MockTransport
# standing in for wp-json -- no extra mocking dependency needed since
# MockTransport ships with httpx itself.
# ---------------------------------------------------------------------------

async def _configure_wordpress(client, headers):
    """Writes WordPress ClubSettings directly rather than POSTing the
    full Admin -> Settings form: that form treats an absent module
    checkbox as "turn it off" (browsers don't submit unchecked
    checkboxes), so posting only the WordPress fields would silently
    disable modul_announcements along the way."""
    from app.database import AsyncSessionLocal
    from app.models import ClubSetting
    from app.crypto_utils import encrypt

    async with AsyncSessionLocal() as session:
        session.add(ClubSetting(key="wordpress_site_url", value="https://blog.example.com", description="test"))
        session.add(ClubSetting(key="wordpress_username", value="board", description="test"))
        session.add(ClubSetting(
            key="wordpress_app_password", value=encrypt("abcd 1234 efgh 5678"), description="test",
        ))
        await session.commit()


def _wordpress_mock_transport(*, media_status=201, post_status=201, users_me_status=200):
    import httpx as httpx_module
    import json as json_module

    def handler(request: httpx_module.Request) -> httpx_module.Response:
        if request.url.path == "/wp-json/wp/v2/users/me":
            return httpx_module.Response(users_me_status, json={"id": 1})
        if request.url.path == "/wp-json/wp/v2/media":
            if media_status not in (200, 201):
                return httpx_module.Response(media_status, text="media upload failed")
            return httpx_module.Response(media_status, json={"id": 42})
        if request.url.path == "/wp-json/wp/v2/posts":
            if post_status not in (200, 201):
                return httpx_module.Response(post_status, text="draft rejected")
            body = json_module.loads(request.content)
            assert body["status"] == "draft"
            return httpx_module.Response(post_status, json={"id": 99, "title": {"raw": body["title"]}})
        return httpx_module.Response(404, text="not found")

    return httpx_module.MockTransport(handler)


async def test_send_blog_creates_wordpress_draft(client, admin_user, monkeypatch, tmp_path):
    # Doesn't need the real, git-tracked uploads directory (unlike
    # test_uploaded_image_is_saved_and_actually_servable above, this test
    # never asserts the image is servable via the real StaticFiles
    # mount) -- redirect it to a temp dir so this test never leaves an
    # orphaned image file on disk.
    monkeypatch.setattr("app.routers.announcements.UPLOAD_DIR", tmp_path)

    token = await login(client, "admin@example.com")
    await _enable_module(client, auth_header(token))
    await web_login(client, "admin@example.com")
    await _configure_wordpress(client, auth_header(token))

    import httpx as httpx_module
    mock_client = httpx_module.AsyncClient(transport=_wordpress_mock_transport())

    async def fake_get_wordpress_publisher(db, client=None):
        from app.blog_publisher import WordPressPublisher
        return WordPressPublisher(
            site_url="https://blog.example.com", username="board",
            application_password="abcd 1234 efgh 5678", client=mock_client,
        )

    monkeypatch.setattr("app.routers.announcements.get_wordpress_publisher", fake_get_wordpress_publisher)

    create = await client.post(
        "/announcements/new",
        data={"title": "New compost bins", "body_markdown": "We installed **new** bins."},
        files={"image": ("bins.png", _TINY_PNG_BYTES, "image/png")},
    )
    announcement_id = create.headers["location"].split("/")[2]

    send = await client.post(f"/announcements/{announcement_id}/send/blog")
    assert send.status_code == 303

    from app.database import AsyncSessionLocal
    from app.models import Announcement, AnnouncementChannel
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Announcement).where(Announcement.id == announcement_id)
            .options(selectinload(Announcement.deliveries))
        )
        announcement = result.scalar_one()
        delivery = announcement.delivery_for(AnnouncementChannel.BLOG)
        assert delivery.status.value == "SENT"
        assert "post=99" in delivery.external_reference
        assert delivery.error_message is None

    await mock_client.aclose()


async def test_send_blog_without_wordpress_configured_is_marked_failed(client, admin_user):
    token = await login(client, "admin@example.com")
    await _enable_module(client, auth_header(token))
    await web_login(client, "admin@example.com")
    # Deliberately not configuring WordPress credentials.

    create = await client.post(
        "/announcements/new",
        data={"title": "Not configured yet", "body_markdown": "Content."},
    )
    announcement_id = create.headers["location"].split("/")[2]

    send = await client.post(f"/announcements/{announcement_id}/send/blog")
    assert send.status_code == 303

    from app.database import AsyncSessionLocal
    from app.models import Announcement, AnnouncementChannel
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Announcement).where(Announcement.id == announcement_id)
            .options(selectinload(Announcement.deliveries))
        )
        announcement = result.scalar_one()
        delivery = announcement.delivery_for(AnnouncementChannel.BLOG)
        assert delivery.status.value == "FAILED"
        assert "isn't configured" in delivery.error_message.lower()


async def test_send_blog_reports_wordpress_rejection(client, admin_user, monkeypatch):
    token = await login(client, "admin@example.com")
    await _enable_module(client, auth_header(token))
    await web_login(client, "admin@example.com")
    await _configure_wordpress(client, auth_header(token))

    import httpx as httpx_module
    mock_client = httpx_module.AsyncClient(transport=_wordpress_mock_transport(post_status=401))

    async def fake_get_wordpress_publisher(db, client=None):
        from app.blog_publisher import WordPressPublisher
        return WordPressPublisher(
            site_url="https://blog.example.com", username="board",
            application_password="wrong", client=mock_client,
        )

    monkeypatch.setattr("app.routers.announcements.get_wordpress_publisher", fake_get_wordpress_publisher)

    create = await client.post(
        "/announcements/new",
        data={"title": "Rejected draft", "body_markdown": "Content."},
    )
    announcement_id = create.headers["location"].split("/")[2]

    send = await client.post(f"/announcements/{announcement_id}/send/blog")
    assert send.status_code == 303

    from app.database import AsyncSessionLocal
    from app.models import Announcement, AnnouncementChannel
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Announcement).where(Announcement.id == announcement_id)
            .options(selectinload(Announcement.deliveries))
        )
        announcement = result.scalar_one()
        delivery = announcement.delivery_for(AnnouncementChannel.BLOG)
        assert delivery.status.value == "FAILED"

    await mock_client.aclose()


async def test_wordpress_test_connection_endpoint(client, admin_user, monkeypatch):
    await web_login(client, "admin@example.com")

    import httpx as httpx_module
    mock_client = httpx_module.AsyncClient(transport=_wordpress_mock_transport(users_me_status=200))

    from app.blog_publisher import WordPressPublisher as RealWordPressPublisher

    class MockedWordPressPublisher(RealWordPressPublisher):
        def __init__(self, site_url, username, application_password, client=None):
            super().__init__(site_url, username, application_password, client=mock_client)

    monkeypatch.setattr("app.routers.admin.WordPressPublisher", MockedWordPressPublisher)

    response = await client.post(
        "/admin/integrations/wordpress/test",
        data={
            "wordpress_site_url": "https://blog.example.com",
            "wordpress_username": "board",
            "wordpress_app_password": "abcd 1234 efgh 5678",
        },
    )
    assert response.status_code == 303
    assert "wordpress_test=success" in response.headers["location"]

    await mock_client.aclose()


async def test_wordpress_test_connection_reports_bad_credentials(client, admin_user, monkeypatch):
    await web_login(client, "admin@example.com")

    import httpx as httpx_module
    mock_client = httpx_module.AsyncClient(transport=_wordpress_mock_transport(users_me_status=401))

    from app.blog_publisher import WordPressPublisher as RealWordPressPublisher

    class MockedWordPressPublisher(RealWordPressPublisher):
        def __init__(self, site_url, username, application_password, client=None):
            super().__init__(site_url, username, application_password, client=mock_client)

    monkeypatch.setattr("app.routers.admin.WordPressPublisher", MockedWordPressPublisher)

    response = await client.post(
        "/admin/integrations/wordpress/test",
        data={
            "wordpress_site_url": "https://blog.example.com",
            "wordpress_username": "board",
            "wordpress_app_password": "wrong-password",
        },
    )
    assert response.status_code == 303
    assert "wordpress_test=failed" in response.headers["location"]

    await mock_client.aclose()


# ---------------------------------------------------------------------------
# WordPress credentials live on the Integrations page, not Settings --
# this is where they're saved (not just tested).
# ---------------------------------------------------------------------------

async def test_integrations_page_saves_wordpress_credentials(client, admin_user):
    await web_login(client, "admin@example.com")

    response = await client.post(
        "/admin/integrations/wordpress",
        data={
            "wordpress_site_url": "https://blog.example.com",
            "wordpress_username": "board",
            "wordpress_app_password": "abcd 1234 efgh 5678",
        },
    )
    assert response.status_code == 303
    assert "wordpress_saved=1" in response.headers["location"]

    from app.database import AsyncSessionLocal
    from app.blog_publisher import load_wordpress_configuration

    async with AsyncSessionLocal() as session:
        config = await load_wordpress_configuration(session)
        assert config == {
            "site_url": "https://blog.example.com",
            "username": "board",
            "app_password": "abcd 1234 efgh 5678",
        }


async def test_integrations_page_blank_password_leaves_existing_one_unchanged(client, admin_user):
    await web_login(client, "admin@example.com")

    await client.post(
        "/admin/integrations/wordpress",
        data={
            "wordpress_site_url": "https://blog.example.com",
            "wordpress_username": "board",
            "wordpress_app_password": "original-secret",
        },
    )

    # Re-save with a new username but a blank Application Password
    # field -- the existing password must survive, same "blank = leave
    # unchanged" convention used for SMTP.
    response = await client.post(
        "/admin/integrations/wordpress",
        data={
            "wordpress_site_url": "https://blog.example.com",
            "wordpress_username": "new-board-username",
            "wordpress_app_password": "",
        },
    )
    assert response.status_code == 303

    from app.database import AsyncSessionLocal
    from app.blog_publisher import load_wordpress_configuration

    async with AsyncSessionLocal() as session:
        config = await load_wordpress_configuration(session)
        assert config["username"] == "new-board-username"
        assert config["app_password"] == "original-secret"


async def test_integrations_page_shows_wordpress_prefill_without_exposing_password(client, admin_user):
    await web_login(client, "admin@example.com")

    await client.post(
        "/admin/integrations/wordpress",
        data={
            "wordpress_site_url": "https://blog.example.com",
            "wordpress_username": "board",
            "wordpress_app_password": "super-secret-value",
        },
    )

    page = await client.get("/admin/integrations")
    assert page.status_code == 200
    assert "https://blog.example.com" in page.text
    assert "board" in page.text
    # The actual secret must never be echoed back into the page.
    assert "super-secret-value" not in page.text


# ---------------------------------------------------------------------------
# Print channel (one-page branded PDF)
# ---------------------------------------------------------------------------

def _pdf_page_count(pdf_bytes: bytes) -> int:
    import io
    from pypdf import PdfReader
    return len(PdfReader(io.BytesIO(pdf_bytes)).pages)


def _pdf_text(pdf_bytes: bytes) -> str:
    import io
    from pypdf import PdfReader
    reader = PdfReader(io.BytesIO(pdf_bytes))
    return "\n".join(page.extract_text() for page in reader.pages)


def _normalized(text: str) -> str:
    """WeasyPrint's font subsetting can make pypdf's text extraction
    insert stray spaces around certain letter pairs (see
    tests/test_members_signin_sheet.py)."""
    return "".join(text.split())


async def test_generate_print_pdf_shows_the_universal_org_bank_footer(client, admin_user):
    """The flyer now shares app/pdf_chrome.py's chrome like every other
    PDF (docs/ADR/0045) -- it must show the same org/register/bank
    footer, not just the club name."""
    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _enable_module(client, headers)
    for key, value in [
        ("bank_iban", "DE89370400440532013000"),
        ("vereinsnummer", "VR 12345"),
    ]:
        response = await client.put(f"/api/v1/club-settings/{key}", json={"value": value}, headers=headers)
        assert response.status_code == 200, response.text

    await web_login(client, "admin@example.com")

    create = await client.post(
        "/announcements/new",
        data={"title": "Kurze Mitteilung", "body_markdown": "Bitte am Samstag zum Arbeitseinsatz kommen."},
    )
    announcement_id = create.headers["location"].split("/")[2]

    response = await client.post(f"/announcements/{announcement_id}/print")
    assert response.status_code == 200
    assert _pdf_page_count(response.content) == 1

    normalized = _normalized(_pdf_text(response.content))
    assert _normalized("IBAN DE89370400440532013000") in normalized
    assert _normalized("VR 12345") in normalized


async def test_generate_print_pdf_short_content_fits_without_shortening(client, admin_user):
    token = await login(client, "admin@example.com")
    await _enable_module(client, auth_header(token))
    await web_login(client, "admin@example.com")

    create = await client.post(
        "/announcements/new",
        data={"title": "Kurze Mitteilung", "body_markdown": "Bitte am Samstag zum Arbeitseinsatz kommen."},
    )
    announcement_id = create.headers["location"].split("/")[2]

    response = await client.post(f"/announcements/{announcement_id}/print")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert _pdf_page_count(response.content) == 1

    from app.database import AsyncSessionLocal
    from app.models import Announcement, AnnouncementChannel
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Announcement).where(Announcement.id == announcement_id)
            .options(selectinload(Announcement.deliveries))
        )
        announcement = result.scalar_one()
        delivery = announcement.delivery_for(AnnouncementChannel.PRINT)
        assert delivery.status.value == "SENT"
        assert delivery.error_message is None
        # Short content shouldn't have touched the print override.
        assert announcement.print_text_override is None


async def test_generate_print_pdf_shortens_long_content_and_persists_override(client, admin_user):
    token = await login(client, "admin@example.com")
    await _enable_module(client, auth_header(token))
    await web_login(client, "admin@example.com")

    long_body = "\n\n".join(f"Absatz Nummer {i}. " * 30 for i in range(1, 20))
    create = await client.post(
        "/announcements/new",
        data={"title": "Lange Mitteilung", "body_markdown": long_body},
    )
    announcement_id = create.headers["location"].split("/")[2]

    response = await client.post(f"/announcements/{announcement_id}/print")
    assert response.status_code == 200
    assert _pdf_page_count(response.content) == 1

    from app.database import AsyncSessionLocal
    from app.models import Announcement, AnnouncementChannel
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Announcement).where(Announcement.id == announcement_id)
            .options(selectinload(Announcement.deliveries))
        )
        announcement = result.scalar_one()
        delivery = announcement.delivery_for(AnnouncementChannel.PRINT)
        assert delivery.status.value == "SENT"
        assert "shortened" in delivery.error_message.lower()
        # No blog post exists for this announcement, so no QR/online note.
        assert "no qr code" in delivery.error_message.lower()
        # The shortened text must actually be persisted, not just used
        # in-memory for this one render.
        assert announcement.print_text_override is not None
        assert announcement.print_text_override != long_body
        assert len(announcement.print_text_override) < len(long_body)


async def test_generate_print_pdf_includes_qr_when_blog_post_is_published(client, admin_user, monkeypatch):
    token = await login(client, "admin@example.com")
    await _enable_module(client, auth_header(token))
    await web_login(client, "admin@example.com")
    await _configure_wordpress(client, auth_header(token))

    long_body = "\n\n".join(f"Absatz Nummer {i}. " * 30 for i in range(1, 20))
    create = await client.post(
        "/announcements/new",
        data={"title": "Mit veroeffentlichtem Blogpost", "body_markdown": long_body},
    )
    announcement_id = create.headers["location"].split("/")[2]

    # Simulate an already-created, already-published WordPress draft.
    from app.database import AsyncSessionLocal
    from app.models import AnnouncementDelivery, AnnouncementChannel, AnnouncementDeliveryStatus

    async with AsyncSessionLocal() as session:
        session.add(AnnouncementDelivery(
            announcement_id=announcement_id, channel=AnnouncementChannel.BLOG,
            status=AnnouncementDeliveryStatus.SENT, external_id="42",
            external_reference="https://blog.example.com/wp-admin/post.php?post=42&action=edit",
        ))
        await session.commit()

    import httpx as httpx_module

    def handler(request: httpx_module.Request) -> httpx_module.Response:
        if request.url.path == "/wp-json/wp/v2/posts/42":
            return httpx_module.Response(200, json={"status": "publish", "link": "https://blog.example.com/2026/herbst"})
        return httpx_module.Response(404)

    mock_client = httpx_module.AsyncClient(transport=httpx_module.MockTransport(handler))

    async def fake_get_wordpress_publisher(db, client=None):
        from app.blog_publisher import WordPressPublisher
        return WordPressPublisher(
            site_url="https://blog.example.com", username="board",
            application_password="abcd 1234 efgh 5678", client=mock_client,
        )

    monkeypatch.setattr("app.routers.announcements.get_wordpress_publisher", fake_get_wordpress_publisher)

    response = await client.post(f"/announcements/{announcement_id}/print")
    assert response.status_code == 200
    assert _pdf_page_count(response.content) == 1

    from app.models import Announcement
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Announcement).where(Announcement.id == announcement_id)
            .options(selectinload(Announcement.deliveries))
        )
        announcement = result.scalar_one()
        delivery = announcement.delivery_for(AnnouncementChannel.PRINT)
        assert delivery.status.value == "SENT"
        assert "qr code" in delivery.error_message.lower()
        assert "was added" in delivery.error_message.lower()

    await mock_client.aclose()


async def test_generate_print_pdf_too_long_is_marked_failed_without_pdf(client, admin_user):
    token = await login(client, "admin@example.com")
    await _enable_module(client, auth_header(token))
    await web_login(client, "admin@example.com")

    unshortenable_body = "Ein einziger enorm langer Absatz ohne Leerzeilen. " * 400
    create = await client.post(
        "/announcements/new",
        data={"title": "Viel zu lang", "body_markdown": unshortenable_body},
    )
    announcement_id = create.headers["location"].split("/")[2]

    response = await client.post(f"/announcements/{announcement_id}/print")
    # No PDF -- redirected back to the edit page instead.
    assert response.status_code == 303

    from app.database import AsyncSessionLocal
    from app.models import Announcement, AnnouncementChannel
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Announcement).where(Announcement.id == announcement_id)
            .options(selectinload(Announcement.deliveries))
        )
        announcement = result.scalar_one()
        delivery = announcement.delivery_for(AnnouncementChannel.PRINT)
        assert delivery.status.value == "FAILED"
        assert "shorten" in delivery.error_message.lower()


# ---------------------------------------------------------------------------
# One action per channel, offered again only when there's something new
# to deliver (ADR 0087 -- replaces the old draft/published/archived
# status, which never left "draft").
# ---------------------------------------------------------------------------

async def _load_announcement(announcement_id):
    from app.database import AsyncSessionLocal
    from app.models import Announcement
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Announcement).where(Announcement.id == announcement_id)
            .options(selectinload(Announcement.deliveries))
        )
        return result.scalar_one()


async def _setup_announcement(client, title="Channel test", body="Content."):
    token = await login(client, "admin@example.com")
    await _enable_module(client, auth_header(token))
    await web_login(client, "admin@example.com")
    create = await client.post("/announcements/new", data={"title": title, "body_markdown": body})
    return token, create.headers["location"].split("/")[2]


def _recording_wordpress_transport(requests_seen, *, existing_post_status=200):
    """Like _wordpress_mock_transport, but also handles updates to an
    existing post (/posts/<id>) and records every request made."""
    import httpx as httpx_module
    import json as json_module

    def handler(request: httpx_module.Request) -> httpx_module.Response:
        body = json_module.loads(request.content) if request.headers.get("content-type") == "application/json" else None
        requests_seen.append((request.method, request.url.path, body))
        if request.url.path == "/wp-json/wp/v2/media":
            return httpx_module.Response(201, json={"id": 42})
        if request.url.path == "/wp-json/wp/v2/posts":
            return httpx_module.Response(201, json={"id": 99})
        if request.url.path.startswith("/wp-json/wp/v2/posts/"):
            post_id = int(request.url.path.rsplit("/", 1)[1])
            if existing_post_status != 200:
                return httpx_module.Response(existing_post_status, json={"code": "rest_post_invalid_id"})
            return httpx_module.Response(200, json={"id": post_id})
        return httpx_module.Response(404, text="not found")

    return httpx_module.MockTransport(handler)


def _patch_wordpress(monkeypatch, transport):
    import httpx as httpx_module
    mock_client = httpx_module.AsyncClient(transport=transport)

    async def fake_get_wordpress_publisher(db, client=None):
        from app.blog_publisher import WordPressPublisher
        return WordPressPublisher(
            site_url="https://blog.example.com", username="board",
            application_password="abcd 1234 efgh 5678", client=mock_client,
        )

    monkeypatch.setattr("app.routers.announcements.get_wordpress_publisher", fake_get_wordpress_publisher)
    return mock_client


async def test_email_is_sent_only_once_even_after_an_edit(client, admin_user, monkeypatch):
    _token, announcement_id = await _setup_announcement(client)

    from app.database import AsyncSessionLocal
    async with AsyncSessionLocal() as session:
        await _create_resident_with_email(session, plot_number="E1", email="once@example.com")

    sent_to = []

    async def fake_send_email(empfaenger, betreff, html_body, text_body=None, db=None):
        sent_to.append(empfaenger)
        return True

    monkeypatch.setattr("app.announcement_mailer.send_email", fake_send_email)

    assert (await client.post(f"/announcements/{announcement_id}/send/email")).status_code == 303
    assert sent_to == ["once@example.com"]

    page = await client.get(f"/announcements/{announcement_id}/edit")
    assert f"/announcements/{announcement_id}/send/email" not in page.text

    # Changing the content does not bring the email back.
    await client.post(f"/announcements/{announcement_id}/edit", data={"title": "Channel test", "body_markdown": "Changed."})
    page = await client.get(f"/announcements/{announcement_id}/edit")
    assert f"/announcements/{announcement_id}/send/email" not in page.text

    second = await client.post(f"/announcements/{announcement_id}/send/email")
    assert second.status_code == 409
    assert sent_to == ["once@example.com"]


async def test_failed_email_send_can_be_retried(client, admin_user, monkeypatch):
    _token, announcement_id = await _setup_announcement(client)

    # No recipients yet -> FAILED.
    assert (await client.post(f"/announcements/{announcement_id}/send/email")).status_code == 303
    announcement = await _load_announcement(announcement_id)
    from app.models import AnnouncementChannel
    assert announcement.delivery_for(AnnouncementChannel.EMAIL).status.value == "FAILED"

    page = await client.get(f"/announcements/{announcement_id}/edit")
    assert f"/announcements/{announcement_id}/send/email" in page.text


async def test_blog_is_updated_in_place_only_after_a_content_change(client, admin_user, monkeypatch, tmp_path):
    monkeypatch.setattr("app.routers.announcements.UPLOAD_DIR", tmp_path)
    token, _ = await _setup_announcement(client)
    await _configure_wordpress(client, auth_header(token))

    create = await client.post(
        "/announcements/new",
        data={"title": "Compost", "body_markdown": "Old text."},
        files={"image": ("bins.png", _TINY_PNG_BYTES, "image/png")},
    )
    announcement_id = create.headers["location"].split("/")[2]

    requests_seen = []
    mock_client = _patch_wordpress(monkeypatch, _recording_wordpress_transport(requests_seen))

    assert (await client.post(f"/announcements/{announcement_id}/send/blog")).status_code == 303
    assert [(m, p) for m, p, _ in requests_seen] == [("POST", "/wp-json/wp/v2/media"), ("POST", "/wp-json/wp/v2/posts")]

    # Nothing changed -> no button, and the server refuses too.
    page = await client.get(f"/announcements/{announcement_id}/edit")
    assert f"/announcements/{announcement_id}/send/blog" not in page.text
    assert (await client.post(f"/announcements/{announcement_id}/send/blog")).status_code == 409

    # Saving without any change doesn't count as a change either.
    await client.post(f"/announcements/{announcement_id}/edit", data={"title": "Compost", "body_markdown": "Old text."})
    assert (await client.post(f"/announcements/{announcement_id}/send/blog")).status_code == 409

    await client.post(f"/announcements/{announcement_id}/edit", data={"title": "Compost", "body_markdown": "New text."})
    page = await client.get(f"/announcements/{announcement_id}/edit")
    assert f"/announcements/{announcement_id}/send/blog" in page.text

    requests_seen.clear()
    assert (await client.post(f"/announcements/{announcement_id}/send/blog")).status_code == 303
    # Same post updated, image not re-uploaded, publish status untouched.
    assert [(m, p) for m, p, _ in requests_seen] == [("POST", "/wp-json/wp/v2/posts/99")]
    payload = requests_seen[0][2]
    assert "New text." in payload["content"]
    assert "status" not in payload
    assert "featured_media" not in payload

    announcement = await _load_announcement(announcement_id)
    from app.models import AnnouncementChannel
    delivery = announcement.delivery_for(AnnouncementChannel.BLOG)
    assert delivery.status.value == "SENT"
    assert delivery.external_id == "99"

    await mock_client.aclose()


async def test_blog_update_creates_new_draft_if_post_was_deleted_in_wordpress(client, admin_user, monkeypatch):
    token, announcement_id = await _setup_announcement(client)
    await _configure_wordpress(client, auth_header(token))

    from app.database import AsyncSessionLocal
    from app.models import AnnouncementDelivery, AnnouncementChannel, AnnouncementDeliveryStatus
    async with AsyncSessionLocal() as session:
        session.add(AnnouncementDelivery(
            announcement_id=announcement_id, channel=AnnouncementChannel.BLOG,
            status=AnnouncementDeliveryStatus.SENT, external_id="7", content_fingerprint="outdated",
        ))
        await session.commit()

    requests_seen = []
    mock_client = _patch_wordpress(monkeypatch, _recording_wordpress_transport(requests_seen, existing_post_status=404))

    assert (await client.post(f"/announcements/{announcement_id}/send/blog")).status_code == 303
    assert [(m, p) for m, p, _ in requests_seen] == [
        ("POST", "/wp-json/wp/v2/posts/7"), ("POST", "/wp-json/wp/v2/posts"),
    ]
    announcement = await _load_announcement(announcement_id)
    assert announcement.delivery_for(AnnouncementChannel.BLOG).external_id == "99"

    await mock_client.aclose()


async def test_print_pdf_is_stored_downloadable_and_only_regenerated_after_a_change(client, admin_user):
    _token, announcement_id = await _setup_announcement(client, title="Aushang", body="Kurzer Text.")

    generated = await client.post(f"/announcements/{announcement_id}/print")
    assert generated.status_code == 200

    download = await client.get(f"/announcements/{announcement_id}/print/download")
    assert download.status_code == 200
    assert download.headers["content-type"] == "application/pdf"
    assert download.content == generated.content

    page = await client.get(f"/announcements/{announcement_id}/edit")
    assert f'action="/announcements/{announcement_id}/print"' not in page.text
    assert f"/announcements/{announcement_id}/print/download" in page.text
    assert (await client.post(f"/announcements/{announcement_id}/print")).status_code == 409

    # A print-text-only change re-enables the PDF...
    from app.routers import announcements as router_module
    from app.models import AnnouncementChannel
    old_pdf = (await _load_announcement(announcement_id)).delivery_for(AnnouncementChannel.PRINT).pdf_filename
    await client.post(
        f"/announcements/{announcement_id}/edit",
        data={"title": "Aushang", "body_markdown": "Kurzer Text.", "print_text_override": "Noch kürzer."},
    )
    assert (await client.post(f"/announcements/{announcement_id}/print")).status_code == 200
    new_pdf = (await _load_announcement(announcement_id)).delivery_for(AnnouncementChannel.PRINT).pdf_filename
    assert new_pdf != old_pdf
    assert not (router_module.PRINT_PDF_DIR / old_pdf).exists()

    # ...and deleting the announcement removes the stored PDF.
    await client.post(f"/announcements/{announcement_id}/delete")
    assert not (router_module.PRINT_PDF_DIR / new_pdf).exists()


async def test_print_pdf_offered_again_for_qr_code_once_a_blog_post_exists(client, admin_user):
    long_body = "\n\n".join(f"Absatz Nummer {i}. " * 30 for i in range(1, 20))
    _token, announcement_id = await _setup_announcement(client, title="Lang", body=long_body)

    assert (await client.post(f"/announcements/{announcement_id}/print")).status_code == 200
    from app.models import AnnouncementDelivery, AnnouncementChannel, AnnouncementDeliveryStatus
    assert (await _load_announcement(announcement_id)).delivery_for(AnnouncementChannel.PRINT).qr_pending is True

    # Shortened without QR, but no blog post at all -> nothing to gain.
    assert (await client.post(f"/announcements/{announcement_id}/print")).status_code == 409

    from app.database import AsyncSessionLocal
    async with AsyncSessionLocal() as session:
        session.add(AnnouncementDelivery(
            announcement_id=announcement_id, channel=AnnouncementChannel.BLOG,
            status=AnnouncementDeliveryStatus.SENT, external_id="42",
        ))
        await session.commit()

    page = await client.get(f"/announcements/{announcement_id}/edit")
    assert f'action="/announcements/{announcement_id}/print"' in page.text


def test_print_text_change_only_affects_the_print_fingerprint():
    from app.announcement_utils import channel_fingerprint

    for channel in ("EMAIL", "BLOG"):
        assert channel_fingerprint(channel, "T", "Body", None) == channel_fingerprint(channel, "T", "Body", "Short")
    assert channel_fingerprint("PRINT", "T", "Body", None) != channel_fingerprint("PRINT", "T", "Body", "Short")
    assert channel_fingerprint("BLOG", "T", "Body", None) != channel_fingerprint("BLOG", "T", "Body 2", None)
