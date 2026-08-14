"""
Ticket mailbox integration (stage 2): IMAP fetch of incoming emails and
SMTP send of outgoing replies -- via the SAME mailbox also used for
general system emails (invitations). There's deliberately only ONE set
of SMTP credentials (see app/email_service.py); this file just adds the
extra IMAP fields needed for receiving.

Design decisions (see also docs/module-tickets.md):
- Operational data (last processed UID, errors) lives in the existing
  `club_settings` table instead of its own table -- consistent with
  the rest of the project, no extra migration needed.
- IMAP fetching runs synchronously (Python's built-in `imaplib`/`email`),
  but in a thread executor (`asyncio.to_thread`) so it doesn't block the
  event loop.
- Threading: incoming replies are matched to an existing ticket via the
  `In-Reply-To`/`References` headers (compared against the stored
  `message_id` values of previous messages). If that fails, it falls
  back to searching open tickets by sender address + similar subject.
  With no match, a new ticket is created.
"""
import asyncio
import email
import imaplib
import logging
import re
from datetime import datetime, timezone
from email.header import decode_header
from email.mime.text import MIMEText
from email.utils import parseaddr, make_msgid
from typing import Optional, List, Dict, Any

import aiosmtplib
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import (
    ClubSetting, Ticket, TicketMessage, TicketAttachment, TicketStatus, MessageDirection,
    AttachmentStorageBackend, new_uuid,
)
from app.ticket_attachment_storage import save_local
from app.email_service import load_smtp_configuration
from app.ticket_utils import find_members_by_email
from app.spam_filter import check_for_spam
from app.html_sanitizer import sanitize_email_html
from app.module_flags import load_module_flags
from app.cloud_storage import get_nextcloud_provider, CloudStorageError

logger = logging.getLogger(__name__)

# Operational data keys in the club_settings table
_KEY_LAST_UID = "ticket_imap_letzte_uid"
_KEY_LAST_FETCH = "ticket_imap_letzter_abruf"
_KEY_LAST_ERROR = "ticket_imap_letzter_fehler"

# Shared Nextcloud folder for all ticket attachments, same "one shared
# folder" pattern as IncomingInvoice (see docs/module-finances.md).
# Must match app/routers/tickets.py and app/routers/admin.py.
TICKET_ATTACHMENTS_FOLDER_SETTING = "ticket_attachments_cloud_folder"

MAX_TICKET_ATTACHMENT_SIZE_BYTES = 15 * 1024 * 1024  # 15 MB -- scanned forms/photos, bounded
MAX_TICKET_ATTACHMENTS_PER_MESSAGE = 10  # defensive cap, same spirit as RESCAN_SPAM_BATCH_LIMIT


async def get_ticket_attachments_folder(db: AsyncSession) -> Optional[str]:
    result = await db.execute(select(ClubSetting).where(ClubSetting.key == TICKET_ATTACHMENTS_FOLDER_SETTING))
    entry = result.scalar_one_or_none()
    return entry.value if entry and entry.value else None


async def _read_setting(db: AsyncSession, key: str) -> Optional[str]:
    result = await db.execute(select(ClubSetting).where(ClubSetting.key == key))
    entry = result.scalar_one_or_none()
    return entry.value if entry else None


async def _write_setting(db: AsyncSession, key: str, value: Optional[str]) -> None:
    result = await db.execute(select(ClubSetting).where(ClubSetting.key == key))
    entry = result.scalar_one_or_none()
    if entry:
        entry.value = value
    else:
        db.add(ClubSetting(key=key, value=value))


async def load_inbox_configuration(db: AsyncSession) -> Dict[str, Any]:
    """
    Loads the mailbox configuration: SMTP credentials come from the
    already-existing general email configuration (the same mailbox
    used for invitations) -- only IMAP host/port/SSL are ticket-
    specific, since the general configuration is only meant for
    sending.
    """
    smtp_config = await load_smtp_configuration(db)

    result = await db.execute(
        select(ClubSetting).where(
            ClubSetting.key.in_(["imap_host", "imap_port", "imap_ssl"])
        )
    )
    stored = {e.key: e.value for e in result.scalars().all() if e.value}

    def _bool(value, default=True) -> bool:
        if value is None:
            return default
        return str(value).strip().lower() in ("true", "1", "ja", "an")

    return {
        "imap_host": stored.get("imap_host", ""),
        "imap_port": int(stored.get("imap_port") or 993),
        "imap_user": smtp_config["user"],       # same mailbox as SMTP
        "imap_password": smtp_config["password"],
        "imap_ssl": _bool(stored.get("imap_ssl"), True),
        "smtp_host": smtp_config["host"],
        "smtp_port": smtp_config["port"],
        "smtp_user": smtp_config["user"],
        "smtp_password": smtp_config["password"],
        "smtp_tls": smtp_config["tls"],
        "smtp_from": smtp_config["from"],
    }


def is_inbox_configured(config: Dict[str, Any]) -> bool:
    return bool(config["imap_host"] and config["smtp_host"] and config["smtp_user"])


def _safe_decode(payload: bytes, charset: Optional[str]) -> str:
    """
    Decodes bytes using the given charset, but safely falls back to
    UTF-8 if the charset is unknown to Python.

    Some mail servers/clients declare non-standard charset names like
    "unknown-8bit" -- that raises a LookupError before even a single
    byte is decoded. errors="replace" alone does NOT help here, since
    it only catches malformed bytes within a KNOWN charset, not an
    unknown charset name itself.
    """
    try:
        return payload.decode(charset or "utf-8", errors="replace")
    except LookupError:
        return payload.decode("utf-8", errors="replace")


def _decode_header(value: Optional[str]) -> str:
    if not value:
        return ""
    parts = decode_header(value)
    result = ""
    for text, encoding in parts:
        if isinstance(text, bytes):
            result += _safe_decode(text, encoding)
        else:
            result += text
    return result


def _extract_text(msg) -> str:
    """Prefers text/plain, falls back to roughly-stripped text/html."""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain" and not part.get("Content-Disposition"):
                payload = part.get_payload(decode=True)
                if payload:
                    return _safe_decode(payload, part.get_content_charset())
        for part in msg.walk():
            if part.get_content_type() == "text/html" and not part.get("Content-Disposition"):
                payload = part.get_payload(decode=True)
                if payload:
                    html = _safe_decode(payload, part.get_content_charset())
                    # Remove <script>/<style> content entirely first (not just
                    # the tags) -- otherwise e.g. CSS code ends up visible in the fallback text.
                    html = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", html, flags=re.IGNORECASE | re.DOTALL)
                    return re.sub(r"<[^>]+>", "", html).strip()
        return ""
    else:
        payload = msg.get_payload(decode=True)
        if not payload:
            return ""
        text = _safe_decode(payload, msg.get_content_charset())
        if msg.get_content_type() == "text/html":
            # Single-part (non-multipart) HTML mail -- same tag
            # stripping as in the multipart case above, otherwise raw
            # markup ends up in the plain-text fallback (e.g. CSV
            # export, search index, or as a last resort if content_html
            # is ever empty).
            text = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", text, flags=re.IGNORECASE | re.DOTALL)
            text = re.sub(r"<[^>]+>", "", text).strip()
        return text


def _extract_html(msg) -> Optional[str]:
    """Returns an email's raw (NOT YET sanitized) text/html part, if
    any -- otherwise None. The caller is responsible for sanitizing the
    result via sanitize_email_html() BEFORE it's stored or rendered
    (see app/html_sanitizer.py)."""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/html" and not part.get("Content-Disposition"):
                payload = part.get_payload(decode=True)
                if payload:
                    return _safe_decode(payload, part.get_content_charset())
        return None
    else:
        if msg.get_content_type() == "text/html":
            payload = msg.get_payload(decode=True)
            if payload:
                return _safe_decode(payload, msg.get_content_charset())
        return None


def sanitize_attachment_filename(name: str) -> str:
    """Strips control characters (CR, LF, tab, etc.) and collapses the
    resulting whitespace. A sender's mail client can fold/wrap a
    filename across an unencoded header continuation line -- Python's
    email.message.Message.get_filename() then returns the raw folded
    text, literal '\\r\\n ' and all. That string later gets embedded
    directly in an HTTP Content-Disposition response header (see
    app/routers/tickets.py's download route) -- a raw CR/LF there isn't
    just a display glitch, it's a header-injection vector, and even
    without malicious intent it crashes the response outright
    (uvicorn's RuntimeError: Invalid HTTP header value). Also escapes a
    literal '"' (would otherwise prematurely close the header's quoted
    filename value). Applied once at ingestion AND again defensively
    where the header is built, same "sanitize at ingestion + a second
    defensive pass at render time" pattern as sanitize_email_html."""
    if not name:
        return "attachment"
    cleaned = re.sub(r"[\x00-\x1f\x7f\s]+", " ", name).replace('"', "'").strip()
    return cleaned or "attachment"


def _extract_attachments(msg) -> List[Dict[str, Any]]:
    """Returns real attachments only -- parts with
    Content-Disposition: attachment. Deliberately NOT "any part with a
    filename": inline signature images/logos are typically marked
    Content-Disposition: inline and have a filename too, but aren't
    attachments a sender meant to send."""
    attachments: List[Dict[str, Any]] = []
    if not msg.is_multipart():
        return attachments
    for part in msg.walk():
        if part.get_content_disposition() != "attachment":
            continue
        payload = part.get_payload(decode=True)
        if not payload:
            continue
        attachments.append({
            "filename": sanitize_attachment_filename(part.get_filename()),
            "content_type": part.get_content_type(),
            "content": payload,
        })
    return attachments


def _fetch_highest_uid_sync(config: Dict[str, Any]) -> int:
    """
    Determines only the highest currently existing UID, WITHOUT
    fetching a single message. Used for the initial sync (see
    process_incoming_mails) -- prevents thousands of existing old
    emails from being imported as tickets all at once on the very
    first fetch.
    """
    if config["imap_ssl"]:
        connection = imaplib.IMAP4_SSL(config["imap_host"], config["imap_port"])
    else:
        connection = imaplib.IMAP4(config["imap_host"], config["imap_port"])

    try:
        connection.login(config["imap_user"], config["imap_password"])
        # readonly=True: this only ever SEARCHes, never FETCHes a body, so
        # nothing here could mark a message \Seen either way -- but opening
        # read-only keeps the invariant obvious and matches
        # _fetch_new_mails_sync below.
        connection.select("INBOX", readonly=True)
        status, data = connection.uid("search", None, "ALL")
        if status != "OK" or not data or not data[0]:
            return 0
        all_uids = [int(u) for u in data[0].split()]
        return max(all_uids) if all_uids else 0
    finally:
        try:
            connection.close()
        except Exception:
            pass
        try:
            connection.logout()
        except Exception:
            pass


def _fetch_new_mails_sync(config: Dict[str, Any], last_uid: Optional[int]) -> List[Dict[str, Any]]:
    """
    Synchronous IMAP query (runs in a thread executor). Returns a list
    of parsed messages, each with uid, message_id, in_reply_to,
    references, from_email, from_name, subject, text.
    """
    results: List[Dict[str, Any]] = []

    if config["imap_ssl"]:
        connection = imaplib.IMAP4_SSL(config["imap_host"], config["imap_port"])
    else:
        connection = imaplib.IMAP4(config["imap_host"], config["imap_port"])

    try:
        connection.login(config["imap_user"], config["imap_password"])
        # readonly=True + BODY.PEEK[] below (instead of RFC822, which is a
        # deprecated alias for BODY[]): a plain BODY[]/RFC822 fetch marks
        # the message \Seen as a side effect on most IMAP servers -- the
        # association wants fetched mail to stay showing as unread in
        # their own mail client, on top of Parcella already never
        # expunging/deleting after fetching (see docs/module-tickets.md).
        connection.select("INBOX", readonly=True)

        status, data = connection.uid("search", None, "ALL")
        if status != "OK" or not data or not data[0]:
            return results

        all_uids = [int(u) for u in data[0].split()]
        new_uids = [u for u in all_uids if last_uid is None or u > last_uid]

        for uid in new_uids:
            status, msg_data = connection.uid("fetch", str(uid), "(BODY.PEEK[])")
            if status != "OK" or not msg_data or not msg_data[0]:
                continue

            raw = msg_data[0][1]
            msg = email.message_from_bytes(raw)

            from_name, from_email = parseaddr(_decode_header(msg.get("From", "")))
            subject = _decode_header(msg.get("Subject", "(ohne Betreff)"))
            message_id = (msg.get("Message-ID") or "").strip()
            in_reply_to = (msg.get("In-Reply-To") or "").strip()
            references = (msg.get("References") or "").strip()

            results.append({
                "uid": uid,
                "message_id": message_id,
                "in_reply_to": in_reply_to,
                "references": references,
                "from_email": from_email.strip().lower(),
                "from_name": from_name.strip(),
                "subject": subject.strip() or "(ohne Betreff)",
                "text": _extract_text(msg).strip(),
                "html": _extract_html(msg),
                "attachments": _extract_attachments(msg),
            })

        return results
    finally:
        try:
            connection.close()
        except Exception:
            pass
        try:
            connection.logout()
        except Exception:
            pass


def _normalize_subject(subject: str) -> str:
    """Strips reply/forward prefixes for the fallback subject comparison."""
    return re.sub(r"^(re|aw|fwd?)\s*:\s*", "", subject.strip(), flags=re.IGNORECASE).strip().lower()


async def _find_matching_ticket(db: AsyncSession, mail: Dict[str, Any]) -> Optional[Ticket]:
    """Looks up an existing ticket for an incoming reply."""
    # 1. Via message-ID threading (In-Reply-To or References)
    candidate_ids = []
    if mail["in_reply_to"]:
        candidate_ids.append(mail["in_reply_to"])
    if mail["references"]:
        candidate_ids.extend(mail["references"].split())

    if candidate_ids:
        result = await db.execute(
            select(TicketMessage).where(TicketMessage.message_id.in_(candidate_ids))
        )
        match = result.scalars().first()
        if match:
            ticket_result = await db.execute(select(Ticket).where(Ticket.id == match.ticket_id))
            ticket = ticket_result.scalar_one_or_none()
            if ticket:
                return ticket

    # 2. Fallback: same sender + similar subject, not closed
    normalized = _normalize_subject(mail["subject"])
    result = await db.execute(
        select(Ticket).where(
            Ticket.sender_email == mail["from_email"],
            Ticket.status != TicketStatus.CLOSED,
        )
    )
    for ticket in result.scalars().all():
        if _normalize_subject(ticket.subject) == normalized:
            return ticket

    return None


async def _save_ticket_attachments(
    db: AsyncSession, message: TicketMessage, attachments: List[Dict[str, Any]],
    provider, folder_path: Optional[str],
) -> None:
    """Uploads an incoming message's attachments to the shared Nextcloud
    folder (preferred) and records one TicketAttachment row per
    successful upload. If Nextcloud isn't configured, falls back to
    local disk storage (app/ticket_attachment_storage.py) rather than
    discarding the attachment -- see docs/module-tickets.md. Never
    raises -- a failed upload just means that one attachment is skipped
    (logged), since a mailbox hiccup or an unconfigured integration must
    never lose the ticket/message itself (same "must never block"
    philosophy as the spam filter's external-API fallback)."""
    cloud_available = bool(provider and folder_path)
    if not cloud_available and attachments:
        logger.info(f"Cloud storage not configured, falling back to local storage for {len(attachments)} ticket attachment(s)")

    for att in attachments[:MAX_TICKET_ATTACHMENTS_PER_MESSAGE]:
        content = att["content"]
        if not content or len(content) > MAX_TICKET_ATTACHMENT_SIZE_BYTES:
            logger.warning(f"Skipped ticket attachment '{att['filename']}': empty or over size limit")
            continue
        attachment_id = new_uuid()

        if cloud_available:
            stored_filename = f"{attachment_id}_{att['filename']}"
            try:
                await provider.upload_file(folder_path, stored_filename, content)
            except CloudStorageError as e:
                logger.warning(f"Failed to upload ticket attachment '{att['filename']}': {e}")
                continue
            db.add(TicketAttachment(
                id=attachment_id, ticket_message_id=message.id,
                original_filename=att["filename"], storage_backend=AttachmentStorageBackend.CLOUD,
                cloud_filename=stored_filename,
                content_type=att["content_type"], size_bytes=len(content),
            ))
        else:
            try:
                local_filename = save_local(attachment_id, content)
            except OSError as e:
                logger.warning(f"Failed to save ticket attachment '{att['filename']}' locally: {e}")
                continue
            db.add(TicketAttachment(
                id=attachment_id, ticket_message_id=message.id,
                original_filename=att["filename"], storage_backend=AttachmentStorageBackend.LOCAL,
                local_filename=local_filename,
                content_type=att["content_type"], size_bytes=len(content),
            ))


async def process_incoming_mails(db: AsyncSession) -> int:
    """
    Fetches new emails and processes them into tickets/messages.
    Returns the number of newly processed emails. Errors are caught and
    recorded in the database instead of crashing the background job.
    """
    config = await load_inbox_configuration(db)
    if not is_inbox_configured(config):
        return 0

    last_uid_str = await _read_setting(db, _KEY_LAST_UID)
    first_run = last_uid_str is None
    last_uid = int(last_uid_str) if last_uid_str else None

    if first_run:
        # On the very first fetch, existing emails are NOT imported --
        # only the current highest UID is remembered as the starting
        # point. Otherwise a mailbox with thousands of old emails would
        # get imported all at once (very slowly, possibly with a
        # dropped connection).
        try:
            highest_uid = await asyncio.to_thread(_fetch_highest_uid_sync, config)
        except Exception as e:
            logger.error(f"IMAP initial sync failed: {e}")
            await _write_setting(db, _KEY_LAST_ERROR, str(e))
            await db.commit()
            return 0

        await _write_setting(db, _KEY_LAST_UID, str(highest_uid))
        await _write_setting(db, _KEY_LAST_FETCH, datetime.now(timezone.utc).isoformat())
        await _write_setting(db, _KEY_LAST_ERROR, None)
        await db.commit()
        logger.info(
            f"Ticket mailbox: initial sync complete (UID {highest_uid}). "
            f"Existing emails were skipped, only new emails will be processed from now on."
        )
        return 0

    try:
        mails = await asyncio.to_thread(_fetch_new_mails_sync, config, last_uid)
    except Exception as e:
        logger.error(f"IMAP fetch failed: {e}")
        await _write_setting(db, _KEY_LAST_ERROR, str(e))
        await db.commit()
        return 0

    processed = 0
    highest_uid = last_uid or 0

    module_flags = await load_module_flags(db)
    attachments_folder = await get_ticket_attachments_folder(db) if module_flags.get("cloud_storage") else None
    provider = await get_nextcloud_provider(db) if attachments_folder else None

    try:
        for mail in mails:
            highest_uid = max(highest_uid, mail["uid"])

            if not mail["from_email"]:
                continue  # unusable message (no sender address parsed)

            ticket = await _find_matching_ticket(db, mail)

            if ticket:
                # Automatically reactivate a closed, postponed, or
                # waiting-for-reply ticket on a new reply -- a reply from
                # the sender ends any form of "we're waiting".
                if ticket.status in (TicketStatus.CLOSED, TicketStatus.POSTPONED, TicketStatus.WAITING):
                    ticket.status = TicketStatus.ASSIGNED if ticket.assigned_to_id else TicketStatus.ACTIVE
                    ticket.closed_at = None
                    ticket.postponed_until = None
            else:
                # Spam check only for new tickets, not for replies to
                # existing ones -- avoids unnecessary (possibly paid) external calls.
                spam_result = await check_for_spam(mail["from_email"], mail["subject"], mail["text"], db)

                matches = await find_members_by_email(db, mail["from_email"])
                member_id = matches[0].id if len(matches) == 1 else None

                ticket = Ticket(
                    subject=mail["subject"],
                    sender_email=mail["from_email"],
                    sender_name=mail["from_name"] or None,
                    member_id=member_id,
                    spam_suspected=spam_result.is_spam_suspected,
                    spam_score=spam_result.score,
                    spam_reasoning=spam_result.reasoning,
                )
                db.add(ticket)
                await db.flush()

            message = TicketMessage(
                ticket_id=ticket.id,
                direction=MessageDirection.INCOMING,
                content=mail["text"] or "(kein Textinhalt)",
                content_html=sanitize_email_html(mail["html"]) if mail.get("html") else None,
                message_id=mail["message_id"] or None,
                in_reply_to=mail["in_reply_to"] or None,
            )
            db.add(message)
            processed += 1

            if mail.get("attachments"):
                await db.flush()  # need message.id as the attachments' FK
                await _save_ticket_attachments(db, message, mail["attachments"], provider, attachments_folder)
    finally:
        if provider:
            await provider.aclose()

    await _write_setting(db, _KEY_LAST_UID, str(highest_uid) if highest_uid else None)
    await _write_setting(db, _KEY_LAST_FETCH, datetime.now(timezone.utc).isoformat())
    await _write_setting(db, _KEY_LAST_ERROR, None)
    await db.commit()

    return processed


async def send_ticket_reply(ticket: Ticket, content: str, db: AsyncSession) -> Optional[str]:
    """
    Sends a reply to a ticket by email to the sender, via the
    configured ticket mailbox. Returns the generated message ID (to
    store on the TicketMessage, for future threading), or None if the
    mailbox isn't configured or sending failed.
    """
    config = await load_inbox_configuration(db)
    if not is_inbox_configured(config):
        logger.warning("Ticket mailbox not configured -- reply will not be sent by email.")
        return None

    last_incoming = next(
        (m for m in reversed(ticket.messages) if m.direction == MessageDirection.INCOMING and m.message_id),
        None
    )

    new_message_id = make_msgid()

    subject = ticket.subject
    if not subject.lower().startswith("re:"):
        subject = f"Re: {subject}"

    msg = MIMEText(content, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = config["smtp_from"]
    msg["To"] = ticket.sender_email
    msg["Message-ID"] = new_message_id
    if last_incoming:
        msg["In-Reply-To"] = last_incoming.message_id
        msg["References"] = last_incoming.message_id

    try:
        await aiosmtplib.send(
            msg,
            hostname=config["smtp_host"],
            port=config["smtp_port"],
            username=config["smtp_user"],
            password=config["smtp_password"],
            start_tls=config["smtp_tls"],
        )
        return new_message_id
    except Exception as e:
        logger.error(f"Ticket reply could not be sent: {e}")
        return None


async def inbox_status(db: AsyncSession) -> Dict[str, Optional[str]]:
    """Operational status for display in the UI (last fetch, last error)."""
    return {
        "letzter_abruf": await _read_setting(db, _KEY_LAST_FETCH),
        "letzter_fehler": await _read_setting(db, _KEY_LAST_ERROR),
    }
