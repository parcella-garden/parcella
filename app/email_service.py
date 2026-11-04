"""
Email sending via SMTP (aiosmtplib).

The SMTP configuration primarily comes from the database (ClubSettings,
editable under /admin/settings). If a value is missing there (e.g. on a
fresh install, before anyone has used the UI), it falls back to the
.env file -- so sending still works without any admin interaction, as
long as the environment variables are set.
"""
import logging
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from typing import List, Optional, Tuple

import aiosmtplib
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.models import ClubSetting, EmailLogStatus
from app.crypto_utils import decrypt, DecryptionError
from app.branding import DEFAULT_CLUB_NAME
from app.email_log import record_email

logger = logging.getLogger(__name__)


async def load_smtp_configuration(db: AsyncSession) -> dict:
    """
    Loads the SMTP configuration: database values take precedence,
    missing values are filled in from the .env file (app.config.settings).
    "from_name" is the club's display name (ClubSetting "verein_name",
    same one shown in the sidebar -- see app/branding.py), used as the
    From header's display name so recipients see the club's name
    rather than the mailbox's local part (e.g. "info").
    """
    result = await db.execute(
        select(ClubSetting).where(
            ClubSetting.key.in_(
                ["smtp_host", "smtp_port", "smtp_user", "smtp_password", "smtp_from", "smtp_tls", "verein_name"]
            )
        )
    )
    stored = {e.key: e.value for e in result.scalars().all() if e.value}

    def _bool(value) -> bool:
        if isinstance(value, bool):
            return value
        return str(value).strip().lower() in ("true", "1", "ja", "an")

    port_value = stored.get("smtp_port")
    try:
        port = int(port_value) if port_value else settings.smtp_port
    except ValueError:
        port = settings.smtp_port

    try:
        smtp_password = decrypt(stored.get("smtp_password")) or settings.smtp_password
    except DecryptionError:
        logger.error(
            "Could not decrypt the stored SMTP password -- did SECRET_KEY change? "
            "Falling back to the .env SMTP password (may also be unset)."
        )
        smtp_password = settings.smtp_password

    return {
        "host": stored.get("smtp_host") or settings.smtp_host,
        "port": port,
        "user": stored.get("smtp_user") or settings.smtp_user,
        "password": smtp_password,
        "from": stored.get("smtp_from") or settings.smtp_from,
        "from_name": stored.get("verein_name") or DEFAULT_CLUB_NAME,
        "tls": _bool(stored.get("smtp_tls")) if "smtp_tls" in stored else settings.smtp_tls,
    }


async def send_email(
    recipient: str,
    subject: str,
    html_body: str,
    text_body: Optional[str] = None,
    db: Optional[AsyncSession] = None,
    attachments: Optional[List[Tuple[str, bytes, str]]] = None,
) -> bool:
    """
    Sends an email. Returns True on success.

    If `db` is passed, the SMTP configuration comes from the database
    (with .env fallback). Without `db`, only the .env configuration is
    used (backwards compatibility).

    attachments: optional list of (filename, content_bytes, mime_type)
    -- e.g. [("invoice_2026-1.pdf", pdf_bytes, "application/pdf")], used
    by the Finances module (see app/invoice_delivery.py) to email an
    invoice's PDF. When present, the message becomes "mixed" with the
    text/html alternative nested inside, rather than "alternative" at
    the top level -- the correct MIME structure for attachments to
    survive alongside a text/html body.

    Every attempt is written to the email log (issue #270, ADR 0120)
    with the SMTP result -- SENT means the server accepted it, not that
    it arrived.
    """
    attachment_count = len(attachments or [])
    if db is not None:
        config = await load_smtp_configuration(db)
    else:
        config = {
            "host": settings.smtp_host,
            "port": settings.smtp_port,
            "user": settings.smtp_user,
            "password": settings.smtp_password,
            "from": settings.smtp_from,
            "from_name": DEFAULT_CLUB_NAME,
            "tls": settings.smtp_tls,
        }

    if not config["host"] or not config["user"]:
        logger.warning("SMTP not configured -- email will not be sent.")
        logger.info(f"[DEV] To: {recipient} | Subject: {subject}")
        await record_email(recipient, subject, EmailLogStatus.FAILED, "SMTP not configured", attachment_count)
        return False

    if attachments:
        msg = MIMEMultipart("mixed")
        alt = MIMEMultipart("alternative")
        if text_body:
            alt.attach(MIMEText(text_body, "plain", "utf-8"))
        alt.attach(MIMEText(html_body, "html", "utf-8"))
        msg.attach(alt)
        for filename, content, mime_type in attachments:
            _maintype, _, subtype = mime_type.partition("/")
            part = MIMEApplication(content, _subtype=subtype or "octet-stream")
            part.add_header("Content-Disposition", "attachment", filename=filename)
            msg.attach(part)
    else:
        msg = MIMEMultipart("alternative")
        if text_body:
            msg.attach(MIMEText(text_body, "plain", "utf-8"))
        msg.attach(MIMEText(html_body, "html", "utf-8"))

    msg["Subject"] = subject
    msg["From"] = formataddr((config["from_name"], config["from"]), charset="utf-8")
    msg["To"] = recipient

    try:
        await aiosmtplib.send(
            msg,
            hostname=config["host"],
            port=config["port"],
            username=config["user"],
            password=config["password"],
            start_tls=config["tls"],
        )
        logger.info(f"Email sent to {recipient}")
    except Exception as e:
        logger.error(f"Email error sending to {recipient}: {e}")
        await record_email(recipient, subject, EmailLogStatus.FAILED, f"{type(e).__name__}: {e}", attachment_count)
        return False
    await record_email(recipient, subject, EmailLogStatus.SENT, attachment_count=attachment_count)
    return True
