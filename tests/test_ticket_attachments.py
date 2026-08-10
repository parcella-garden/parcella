"""
Tests for ticket attachments (Nextcloud-backed, see docs/module-tickets.md
"Incoming attachments"). Real IMAP fetch is out of scope here (see
tests/test_tickets.py's module docstring) -- _extract_attachments() and
_save_ticket_attachments() are tested directly instead of via
process_incoming_mails(), same boundary the rest of this module respects.
NextcloudProvider is exercised against an httpx.MockTransport, same
approach as tests/test_cloud_storage.py.
"""
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage

from tests.conftest import login, auth_header
from app.database import AsyncSessionLocal
from app.models import Ticket, TicketMessage, TicketAttachment, MessageDirection


async def web_login(client, email: str = "admin@example.com", password: str = "testpasswort123") -> None:
    response = await client.post("/auth/login", data={"email": email, "password": password})
    assert response.status_code in (302, 303)


def _nextcloud_mock_transport(put_status=201, get_status=200, get_body=b"file bytes"):
    import httpx as httpx_module

    def handler(request: httpx_module.Request) -> httpx_module.Response:
        if request.method == "PUT":
            return httpx_module.Response(put_status)
        if request.method == "GET":
            return httpx_module.Response(get_status, content=get_body)
        return httpx_module.Response(404)

    return httpx_module.MockTransport(handler)


async def _create_ticket_and_message(sender_email: str = "gaertner@example.com") -> tuple[str, str]:
    async with AsyncSessionLocal() as db:
        ticket = Ticket(subject="Formular und Termine", sender_email=sender_email)
        db.add(ticket)
        await db.flush()
        message = TicketMessage(
            ticket_id=ticket.id, direction=MessageDirection.INCOMING, content="Anbei das Formular.",
        )
        db.add(message)
        await db.commit()
        return ticket.id, message.id


# ---------------------------------------------------------------------------
# _extract_attachments()
# ---------------------------------------------------------------------------

def test_extract_attachments_ignores_body_and_inline_images():
    from app.ticket_mailer import _extract_attachments

    msg = MIMEMultipart()
    msg.attach(MIMEText("Hallo, siehe Anhang.", "plain"))

    inline_image = MIMEImage(b"fake-logo-bytes", _subtype="png")
    inline_image.add_header("Content-Disposition", "inline", filename="signature-logo.png")
    msg.attach(inline_image)

    real_attachment = MIMEApplication(b"%PDF-1.4 fake pdf bytes", _subtype="pdf")
    real_attachment.add_header("Content-Disposition", "attachment", filename="formular.pdf")
    msg.attach(real_attachment)

    attachments = _extract_attachments(msg)

    assert len(attachments) == 1
    assert attachments[0]["filename"] == "formular.pdf"
    assert attachments[0]["content_type"] == "application/pdf"
    assert attachments[0]["content"] == b"%PDF-1.4 fake pdf bytes"


def test_extract_attachments_empty_for_plain_non_multipart_message():
    from app.ticket_mailer import _extract_attachments

    msg = MIMEText("Just plain text, no attachments.", "plain")
    assert _extract_attachments(msg) == []


# ---------------------------------------------------------------------------
# sanitize_attachment_filename() -- regression coverage for a real incident:
# a sender's mail client folded a filename across an unencoded header
# continuation line, so Message.get_filename() returned the raw
# "Screenshot from 2026-08-10\r\n 20-18-40.png". That string, stored as
# TicketAttachment.original_filename, then embedded raw in the download
# route's Content-Disposition response header, crashed uvicorn outright
# (RuntimeError: Invalid HTTP header value) -- a header-injection-shaped
# bug, not just a display glitch.
# ---------------------------------------------------------------------------

def test_sanitize_attachment_filename_strips_folded_crlf():
    from app.ticket_mailer import sanitize_attachment_filename

    assert (
        sanitize_attachment_filename("Screenshot from 2026-08-10\r\n 20-18-40.png")
        == "Screenshot from 2026-08-10 20-18-40.png"
    )


def test_sanitize_attachment_filename_escapes_embedded_quote():
    from app.ticket_mailer import sanitize_attachment_filename

    assert '"' not in sanitize_attachment_filename('evil"; filename="other.exe')


def test_sanitize_attachment_filename_falls_back_for_empty_input():
    from app.ticket_mailer import sanitize_attachment_filename

    assert sanitize_attachment_filename("") == "attachment"
    assert sanitize_attachment_filename("\r\n\t") == "attachment"


def test_extract_attachments_sanitizes_folded_filename():
    from app.ticket_mailer import _extract_attachments

    msg = MIMEMultipart()
    msg.attach(MIMEText("Anbei ein Screenshot.", "plain"))
    real_attachment = MIMEApplication(b"fake-png-bytes", _subtype="png")
    # Simulates a mail client's unencoded header fold: get_filename()
    # returns the raw continuation, literal CRLF included.
    real_attachment.add_header("Content-Disposition", "attachment", filename="Screenshot from 2026-08-10\r\n 20-18-40.png")
    msg.attach(real_attachment)

    attachments = _extract_attachments(msg)
    assert len(attachments) == 1
    assert attachments[0]["filename"] == "Screenshot from 2026-08-10 20-18-40.png"


async def test_download_ticket_attachment_survives_bad_stored_filename(client, admin_user, monkeypatch):
    """Defense-in-depth regression: even if a bad (control-character-laden)
    filename already made it into the database -- e.g. from before this
    fix, or any other future insertion path -- the download route must
    still sanitize at render time rather than crash building the
    Content-Disposition header."""
    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _enable_cloud_storage_and_folder(client, headers)

    ticket_id, message_id = await _create_ticket_and_message()
    async with AsyncSessionLocal() as db:
        attachment = TicketAttachment(
            ticket_message_id=message_id,
            original_filename="Screenshot from 2026-08-10\r\n 20-18-40.png",
            cloud_filename="abc123_Screenshot from 2026-08-10\r\n 20-18-40.png",
            content_type="image/png", size_bytes=9,
        )
        db.add(attachment)
        await db.commit()
        attachment_id = attachment.id

    import httpx as httpx_module
    from app.cloud_storage import NextcloudProvider as RealNextcloudProvider

    mock_client = httpx_module.AsyncClient(transport=_nextcloud_mock_transport(get_body=b"png bytes"))

    async def fake_get_nextcloud_provider(db, client=None):
        return RealNextcloudProvider(
            base_url="https://cloud.example.org", username="board", app_password="secret", client=mock_client,
        )

    monkeypatch.setattr("app.routers.tickets.get_nextcloud_provider", fake_get_nextcloud_provider)

    response = await client.get(f"/tickets/{ticket_id}/attachments/{attachment_id}")
    assert response.status_code == 200
    assert response.content == b"png bytes"
    assert "\r" not in response.headers["content-disposition"]
    assert "\n" not in response.headers["content-disposition"]
    assert 'filename="Screenshot from 2026-08-10 20-18-40.png"' in response.headers["content-disposition"]


# ---------------------------------------------------------------------------
# _save_ticket_attachments()
# ---------------------------------------------------------------------------

async def test_save_ticket_attachments_skipped_when_cloud_storage_not_configured():
    """Must never raise or block message creation -- same "must never
    block" philosophy as the spam filter's external-API fallback."""
    from app.ticket_mailer import _save_ticket_attachments

    ticket_id, message_id = await _create_ticket_and_message()

    async with AsyncSessionLocal() as db:
        message = (await db.get(TicketMessage, message_id))
        await _save_ticket_attachments(
            db, message, [{"filename": "formular.pdf", "content_type": "application/pdf", "content": b"data"}],
            provider=None, folder_path=None,
        )
        await db.commit()

    async with AsyncSessionLocal() as db:
        from sqlalchemy import select
        result = await db.execute(select(TicketAttachment).where(TicketAttachment.ticket_message_id == message_id))
        assert result.scalars().all() == []


async def test_save_ticket_attachments_uploads_and_records_row():
    import httpx as httpx_module
    from app.cloud_storage import NextcloudProvider
    from app.ticket_mailer import _save_ticket_attachments

    ticket_id, message_id = await _create_ticket_and_message()
    mock_client = httpx_module.AsyncClient(transport=_nextcloud_mock_transport())
    provider = NextcloudProvider(
        base_url="https://cloud.example.org", username="board", app_password="secret", client=mock_client,
    )

    async with AsyncSessionLocal() as db:
        message = await db.get(TicketMessage, message_id)
        await _save_ticket_attachments(
            db, message, [{"filename": "formular.pdf", "content_type": "application/pdf", "content": b"pdf-bytes"}],
            provider=provider, folder_path="Tickets/Anhaenge",
        )
        await db.commit()
    await provider.aclose()

    async with AsyncSessionLocal() as db:
        from sqlalchemy import select
        result = await db.execute(select(TicketAttachment).where(TicketAttachment.ticket_message_id == message_id))
        attachments = result.scalars().all()
    assert len(attachments) == 1
    assert attachments[0].original_filename == "formular.pdf"
    assert attachments[0].content_type == "application/pdf"
    assert attachments[0].size_bytes == len(b"pdf-bytes")
    assert attachments[0].cloud_filename.endswith("_formular.pdf")
    assert attachments[0].cloud_filename.startswith(attachments[0].id)


async def test_save_ticket_attachments_skips_oversized_file():
    from app.ticket_mailer import _save_ticket_attachments, MAX_TICKET_ATTACHMENT_SIZE_BYTES

    ticket_id, message_id = await _create_ticket_and_message()
    async with AsyncSessionLocal() as db:
        message = await db.get(TicketMessage, message_id)
        oversized = b"x" * (MAX_TICKET_ATTACHMENT_SIZE_BYTES + 1)
        await _save_ticket_attachments(
            db, message, [{"filename": "huge.zip", "content_type": "application/zip", "content": oversized}],
            provider="unused-should-never-be-called", folder_path="Tickets/Anhaenge",
        )
        await db.commit()

    async with AsyncSessionLocal() as db:
        from sqlalchemy import select
        result = await db.execute(select(TicketAttachment).where(TicketAttachment.ticket_message_id == message_id))
        assert result.scalars().all() == []


# ---------------------------------------------------------------------------
# Download route
# ---------------------------------------------------------------------------

async def _enable_cloud_storage_and_folder(client, headers):
    response = await client.put(
        "/api/v1/club-settings/modul_cloud_storage", json={"value": "true"}, headers=headers,
    )
    assert response.status_code == 200, response.text
    await web_login(client)
    response = await client.post(
        "/admin/integrations/nextcloud/ticket-attachments-folder",
        data={"relative_path": "Tickets/Anhaenge"},
    )
    assert response.status_code in (302, 303)


async def test_download_ticket_attachment_returns_file_bytes(client, admin_user, monkeypatch):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _enable_cloud_storage_and_folder(client, headers)

    ticket_id, message_id = await _create_ticket_and_message()
    async with AsyncSessionLocal() as db:
        attachment = TicketAttachment(
            ticket_message_id=message_id, original_filename="formular.pdf",
            cloud_filename="abc123_formular.pdf", content_type="application/pdf", size_bytes=9,
        )
        db.add(attachment)
        await db.commit()
        attachment_id = attachment.id

    import httpx as httpx_module
    from app.cloud_storage import NextcloudProvider as RealNextcloudProvider

    mock_client = httpx_module.AsyncClient(transport=_nextcloud_mock_transport(get_body=b"pdf contents"))

    async def fake_get_nextcloud_provider(db, client=None):
        return RealNextcloudProvider(
            base_url="https://cloud.example.org", username="board", app_password="secret", client=mock_client,
        )

    monkeypatch.setattr("app.routers.tickets.get_nextcloud_provider", fake_get_nextcloud_provider)

    response = await client.get(f"/tickets/{ticket_id}/attachments/{attachment_id}")
    assert response.status_code == 200
    assert response.content == b"pdf contents"
    assert 'filename="formular.pdf"' in response.headers["content-disposition"]


async def test_download_ticket_attachment_404_for_mismatched_ticket(client, admin_user, monkeypatch):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await _enable_cloud_storage_and_folder(client, headers)

    _, message_id = await _create_ticket_and_message()
    other_ticket_id, _ = await _create_ticket_and_message(sender_email="andere@example.com")
    async with AsyncSessionLocal() as db:
        attachment = TicketAttachment(
            ticket_message_id=message_id, original_filename="formular.pdf",
            cloud_filename="abc123_formular.pdf", content_type="application/pdf", size_bytes=9,
        )
        db.add(attachment)
        await db.commit()
        attachment_id = attachment.id

    response = await client.get(f"/tickets/{other_ticket_id}/attachments/{attachment_id}")
    assert response.status_code == 404


async def test_download_ticket_attachment_blocked_without_ticket_read_permission(client, admin_user):
    from app.models import User, UserRole
    from app.auth import hash_password

    ticket_id, message_id = await _create_ticket_and_message()
    async with AsyncSessionLocal() as db:
        attachment = TicketAttachment(
            ticket_message_id=message_id, original_filename="formular.pdf",
            cloud_filename="abc123_formular.pdf", content_type="application/pdf", size_bytes=9,
        )
        db.add(attachment)
        db.add(User(
            email="treasurer-no-group@example.com", name="Treasurer No Group",
            password_hash=hash_password("testpasswort123"), role=UserRole.TREASURER,
        ))
        await db.commit()
        attachment_id = attachment.id

    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    await client.put("/api/v1/club-settings/modul_cloud_storage", json={"value": "true"}, headers=headers)

    await web_login(client, "treasurer-no-group@example.com")
    response = await client.get(f"/tickets/{ticket_id}/attachments/{attachment_id}")
    assert response.status_code == 403


async def test_download_ticket_attachment_404_when_cloud_storage_module_disabled(client, admin_user):
    ticket_id, message_id = await _create_ticket_and_message()
    async with AsyncSessionLocal() as db:
        attachment = TicketAttachment(
            ticket_message_id=message_id, original_filename="formular.pdf",
            cloud_filename="abc123_formular.pdf", content_type="application/pdf", size_bytes=9,
        )
        db.add(attachment)
        await db.commit()
        attachment_id = attachment.id

    await web_login(client, "admin@example.com")
    response = await client.get(f"/tickets/{ticket_id}/attachments/{attachment_id}")
    assert response.status_code == 404
