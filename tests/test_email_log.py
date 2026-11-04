"""
Issue #270: every outgoing email is logged with date/time, recipient,
subject and the SMTP result (ADR 0120). The admin page and the API list
it; entries past the retention period (default 90 days) are deleted.
"""
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models import ClubSetting, EmailLog, EmailLogStatus
from tests.conftest import auth_header, login


async def _configure_smtp():
    async with AsyncSessionLocal() as session:
        session.add_all([
            ClubSetting(key="smtp_host", value="smtp.example.org"),
            ClubSetting(key="smtp_user", value="club@example.org"),
            ClubSetting(key="smtp_from", value="club@example.org"),
        ])
        await session.commit()


async def _logs():
    async with AsyncSessionLocal() as session:
        return (await session.scalars(select(EmailLog).order_by(EmailLog.recipient))).all()


async def test_send_email_logs_success_failure_and_missing_config(client, monkeypatch):
    from app import email_service

    # No SMTP configured at all: logged as failed with the reason.
    monkeypatch.setattr(email_service.settings, "smtp_host", "")
    async with AsyncSessionLocal() as session:
        assert await email_service.send_email("nobody@example.org", "Unsent", "<p>x</p>", db=session) is False

    await _configure_smtp()

    async def fake_send(msg, **kwargs):
        if msg["To"] == "bad@example.org":
            raise RuntimeError("550 5.1.1 User unknown")

    monkeypatch.setattr(email_service.aiosmtplib, "send", fake_send)
    async with AsyncSessionLocal() as session:
        assert await email_service.send_email(
            "good@example.org", "Invoice 2026-1", "<p>x</p>", db=session,
            attachments=[("invoice.pdf", b"%PDF", "application/pdf")],
        ) is True
        assert await email_service.send_email("bad@example.org", "Hello", "<p>x</p>", db=session) is False

    bad, good, nobody = await _logs()
    assert (good.status, good.subject, good.attachment_count, good.error) == (EmailLogStatus.SENT, "Invoice 2026-1", 1, None)
    assert bad.status == EmailLogStatus.FAILED and "550 5.1.1 User unknown" in bad.error
    assert nobody.status == EmailLogStatus.FAILED and nobody.error == "SMTP not configured"


async def test_send_email_still_works_when_logging_fails(client, monkeypatch):
    from app import email_service

    await _configure_smtp()

    async def fake_send(msg, **kwargs):
        return None

    class BrokenSession:
        def __call__(self):
            raise RuntimeError("database down")

    monkeypatch.setattr(email_service.aiosmtplib, "send", fake_send)
    monkeypatch.setattr("app.database.AsyncSessionLocal", BrokenSession())
    # This module's own AsyncSessionLocal binding is unaffected by the patch.
    async with AsyncSessionLocal() as session:
        assert await email_service.send_email("x@example.org", "Hi", "<p>x</p>", db=session) is True


async def test_admin_page_filters_and_escapes(client, admin_user):
    async with AsyncSessionLocal() as session:
        session.add_all([
            EmailLog(recipient="alice@example.org", subject="<b>Welcome</b>", status=EmailLogStatus.SENT),
            EmailLog(recipient="bob@example.org", subject="Reminder", status=EmailLogStatus.FAILED,
                     error="SMTPRecipientsRefused: <script>x</script>"),
        ])
        await session.commit()

    await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})
    page = await client.get("/admin/email-log")
    assert page.status_code == 200
    assert "alice@example.org" in page.text and "bob@example.org" in page.text
    assert "<b>Welcome</b>" not in page.text and "&lt;b&gt;Welcome&lt;/b&gt;" in page.text
    assert "<script>x</script>" not in page.text
    assert 'href="/admin/email-log"' in page.text  # nav entry

    failed_only = (await client.get("/admin/email-log?status=FAILED")).text
    assert "bob@example.org" in failed_only and "alice@example.org" not in failed_only
    search = (await client.get("/admin/email-log?q=ALICE")).text
    assert "alice@example.org" in search and "bob@example.org" not in search
    # LIKE wildcards in the search are literal, not "match everything".
    assert "alice@example.org" not in (await client.get("/admin/email-log?q=%25")).text


async def test_admin_page_is_system_admin_only(client, board_user):
    await client.post("/auth/login", data={"email": "vorstand@example.com", "password": "testpasswort123"})
    response = await client.get("/admin/email-log", follow_redirects=False)
    assert response.status_code in (302, 303, 403)


async def test_retention_setting_and_purge(client, admin_user):
    from app.email_log import purge_expired_email_logs

    now = datetime.now(timezone.utc)
    async with AsyncSessionLocal() as session:
        session.add_all([
            EmailLog(recipient="old@example.org", subject="a", status=EmailLogStatus.SENT, sent_at=now - timedelta(days=95)),
            EmailLog(recipient="mid@example.org", subject="b", status=EmailLogStatus.SENT, sent_at=now - timedelta(days=40)),
            EmailLog(recipient="new@example.org", subject="c", status=EmailLogStatus.SENT, sent_at=now - timedelta(days=1)),
        ])
        await session.commit()
        assert await purge_expired_email_logs(session) == 1  # default 90 days
    assert [r.recipient for r in await _logs()] == ["mid@example.org", "new@example.org"]

    await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})
    settings_page = (await client.get("/admin/settings")).text
    assert 'name="email_log_retention_days"' in settings_page and 'value="90"' in settings_page
    await client.post("/admin/settings", data={"email_log_retention_days": "30"})
    async with AsyncSessionLocal() as session:
        stored = await session.scalar(select(ClubSetting.value).where(ClubSetting.key == "email_log_retention_days"))
        assert stored == "30"
        assert await purge_expired_email_logs(session) == 1
    assert [r.recipient for r in await _logs()] == ["new@example.org"]


async def test_email_log_api_admin_only(client, admin_user, board_user):
    async with AsyncSessionLocal() as session:
        session.add_all([
            EmailLog(recipient="a@example.org", subject="One", status=EmailLogStatus.SENT),
            EmailLog(recipient="b@example.org", subject="Two", status=EmailLogStatus.FAILED, error="boom"),
        ])
        await session.commit()

    token = await login(client, "admin@example.com")
    r = await client.get("/api/v1/email-log?status=FAILED", headers=auth_header(token))
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["total"] == 1 and body["items"][0]["recipient"] == "b@example.org"
    assert body["items"][0]["status"] == "FAILED" and body["items"][0]["error"] == "boom"
    assert (await client.get("/api/v1/email-log?status=nope", headers=auth_header(token))).status_code == 422

    board_token = await login(client, "vorstand@example.com")
    assert (await client.get("/api/v1/email-log", headers=auth_header(board_token))).status_code == 403
