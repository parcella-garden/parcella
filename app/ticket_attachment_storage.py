"""
Local disk fallback for ticket attachments (app/ticket_mailer.py) when
Nextcloud isn't configured -- see docs/module-tickets.md and the ADR on
this fallback. Deliberately outside app/static/: ticket access is
permission-gated (GET /tickets/{id}/attachments/{attachment_id}), unlike
the club logo/avatars/announcement images under app/static/uploads/,
which are intentionally public (app/main.py mounts app/static/ at
/static). Also covered by app/backup.py's backup/restore zip, under its
own ticket_attachments/ prefix, since there's no volume mount for this
directory in docker-compose.prod.yml -- without that, a redeploy would
silently lose every locally-stored attachment.

Filenames on disk are the attachment's own id (a UUID, generated
server-side) -- the sender-supplied original filename never touches a
filesystem path, only TicketAttachment.original_filename for the
Content-Disposition header at download time.
"""
from pathlib import Path

TICKET_ATTACHMENT_STORAGE_DIR = Path("app/private_uploads/ticket_attachments")


def save_local(attachment_id: str, content: bytes) -> str:
    """Writes `content` to disk, returning the filename to store in
    TicketAttachment.local_filename."""
    TICKET_ATTACHMENT_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    with open(TICKET_ATTACHMENT_STORAGE_DIR / attachment_id, "wb") as f:
        f.write(content)
    return attachment_id


def read_local(filename: str) -> bytes:
    base = TICKET_ATTACHMENT_STORAGE_DIR.resolve()
    target = (TICKET_ATTACHMENT_STORAGE_DIR / filename).resolve()
    if target != base and base not in target.parents:
        raise FileNotFoundError(f"path escapes ticket attachment storage: {filename!r}")
    with open(target, "rb") as f:
        return f.read()
