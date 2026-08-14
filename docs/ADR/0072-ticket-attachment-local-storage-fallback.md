# Ticket attachments: local-storage fallback when Nextcloud isn't configured

**Context:** ADR-level decision from `docs/module-tickets.md`'s
"Incoming attachments" section: incoming ticket email attachments are
stored in the shared Nextcloud folder, never locally, "same pattern as
`IncomingInvoice`" -- and if `cloud_storage` isn't enabled or the folder
isn't configured, the attachment is simply discarded (logged, not
stored), matching the stage-3 spam filter's "an unconfigured integration
must never block ticket creation" philosophy.

That philosophy is right for *ticket creation* but too destructive as a
default for the *attachment* itself: a club that never sets up Nextcloud
-- or, as happened for real on the association's first production
deployment, one whose stored Nextcloud app password stopped decrypting
after `SECRET_KEY` was rotated for the move off `localhost` -- loses
every incoming attachment permanently, with no way to recover it
(confirmed live: the original email is still sitting in the mailbox,
since Parcella never expunges after fetching, but the attachment bytes
themselves were never written anywhere).

**Decision: local disk becomes a fallback, not a replacement.** Nextcloud
stays the preferred backend whenever it's configured and working --
nothing changes about that path. Only when `provider`/`folder_path` are
unavailable at save time does `_save_ticket_attachments()`
(`app/ticket_mailer.py`) now write the bytes to
`app/private_uploads/ticket_attachments/`
(`app/ticket_attachment_storage.py`) instead of just logging and
discarding. `TicketAttachment` gained a `storage_backend`
(`CLOUD`/`LOCAL`) column plus a nullable `local_filename` so the
download route (`GET /tickets/{id}/attachments/{attachment_id}`) knows
which backend to read from per row; every attachment stored before this
change is backfilled to `CLOUD`, matching its actual (and only, until
now) storage.

**Why a new private directory, not `app/static/uploads/`:** ticket
attachments are permission-gated (`require_permission(..., "tickets",
"read")` on the download route) -- `app/static/uploads/` is mounted
publicly at `/static` (`app/main.py`), which is fine for the branding
logo/avatars/announcement images that deliberately want to be public,
but would turn every locally-stored attachment into a guessable public
URL. `app/private_uploads/ticket_attachments/` sits outside `app/static/`
entirely; the only way to reach a file in it is through the existing
gated download route.

**Why the download route's `require_module("cloud_storage")` dependency
moved from the router to inline, CLOUD-only logic:** the whole route
used to be gated by that module flag, which made sense when every
attachment necessarily lived in Nextcloud -- but a LOCAL-backend
attachment has nothing to do with that module and must stay downloadable
even when it's disabled. The CLOUD branch keeps the identical check
(inline now, same `MODULE_DEFAULTS`-aware lookup `require_module` used),
so existing behavior for Nextcloud-backed attachments is unchanged; only
LOCAL-backend downloads are newly exempt from it.

**Why this also had to touch `app/backup.py`:** `docker-compose.prod.yml`
has no volume mount for the `web` container's filesystem at all -- the
*only* thing making any local upload in this app durable across a
redeploy is the admin backup zip (`app/backup.py`, ADR 0053/0054/0055),
which previously hardcoded `UPLOAD_DIR` (`app/static/uploads/`) as the
one directory it walks. Without extending it, locally-stored ticket
attachments would survive right up until the next `docker compose pull
&& up -d`, then vanish silently -- a materially worse outcome than the
Nextcloud-configured case. `build_backup_zip()` /
`_validate_restore_zip()` / the restore mirror-replace step now handle
`app/private_uploads/ticket_attachments/` under its own
`ticket_attachments/` zip prefix, alongside the existing `uploads/`
prefix -- covered by every existing backup path (on-demand download,
scheduled cloud backups, restore) with no new infrastructure.

**Deliberately not done:** no volume mount was added to
`docker-compose.prod.yml` as an alternative fix. That would be a bigger,
more disruptive change than this issue asked for, and would leave the
*existing* `app/static/uploads/` gap (branding logo, avatars,
announcement images -- already only backup-covered, not volume-mounted)
inconsistent with the new directory if only the new one got a volume.
The backup-based durability model is accepted as this app's existing
answer to "how do local uploads survive a redeploy," not something this
change should quietly diverge from for one directory only.
