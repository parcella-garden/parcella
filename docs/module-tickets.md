# Module: Ticket System

Support ticket system, modeled loosely after
[Freescout](https://github.com/freescout-help-desk/freescout).
Built in three stages -- this page describes **stage 1**
(data model + manual ticket management) plus the two stages that
followed.

Module flag: `tickets`

## Stage overview

1. **Data model + manual ticket management** (done) -- tickets, history,
   assignment, status, member matching. No automatic email fetching yet.
2. **Email integration** (done) -- IMAP inbox configuration,
   background polling (every 2 min.), incoming mail becomes
   tickets/messages, outgoing replies are sent via SMTP.
3. **Spam interface** (done) -- built-in heuristics plus an optional
   external API, configurable under `/admin/settings`.

## Stage 3: spam filter

**Two combined layers.** Built-in heuristics run immediately, with no
external service: sender-domain blocklist, keyword blocklist, number of
links in the text. An optional external API (`app/spam_filter.py`,
`_external_check()`) is only used if a URL is configured under Admin ->
Settings -- Parcella POSTs `{"sender_email", "subject", "content"}` as
JSON and expects back `{"spam_score": 0.0-1.0}`, a generic contract any
service can be connected to via a thin adapter, without touching caller
code (see `integrations/spam-check-adapter/` for a runnable reference
implementation). The final score is the maximum of the heuristic and
the external score; if the external call fails or its response doesn't
match the contract, it silently falls back to the heuristics -- an
outage or misconfiguration of the external service must never block
ticket creation. This contract briefly detoured to being hard-wired to
one specific commercial vendor (apilayer.com) and back -- see
[ADR 0038](./ADR/0038-spam-filter-external-api-tied-to-apilayer-for-now.md)
and [ADR 0066](./ADR/0066-spam-filter-external-api-back-to-a-generic-contract.md)
for why.

**Transparency instead of silently sorting things out.** Tickets marked
as spam are not deleted, only hidden from the default "Active" filter. A
dedicated "Suspected" filter tab (with a count badge) still shows them,
including the score and a traceable justification (`spam_reasoning`, e.g.
"keywords found: casino, prize"). Every ticket can be cleared as
"not spam" (false positive) with a single click -- important because
heuristics are never perfect, and an association should never accidentally
lose a genuine inquiry forever.

**Marking is also manual, not just automatic.** The check
(`app/spam_filter.py`) only ever runs once, on arrival -- anything it
misses stays unflagged forever with no automated second chance. Staff
can flag a ticket the filter missed via a "Mark as spam" button on the
ticket detail page, or in bulk from the overview's multi-select
toolbar (`POST /tickets/{id}/mark-spam`, `POST /tickets/bulk/mark-spam`
-- symmetric to the existing `.../not-spam` clear-the-flag routes). A
manually-flagged ticket is indistinguishable from an automatically-
flagged one afterward except that `spam_score`/`spam_reasoning` stay
empty -- there's no score to show for a human judgment call.

**A backlog re-scan catches tickets the filter never saw.** Because the
check only ever runs once, on arrival, a ticket created before the
filter was configured (or before a later configuration change, e.g.
adding an external API) never gets a second chance automatically.
"Re-scan for spam" in the overview's topbar (`POST
/tickets/rescan-spam`) runs the check against every ticket that's
still open (not `CLOSED`/`DELETED`), not already `spam_suspected`, and
-- critically -- that no human has ever made a spam call on. That last
condition is `tickets.spam_reviewed_by_id`/`spam_reviewed_at`, set by
every human-driven path (the mark/not-spam buttons, their bulk
equivalents, and the API's `PUT /spam-status`) but never by the
automated check itself. Without it, re-running the scan could
re-flag a ticket a board member deliberately cleared as a false
positive, using the same heuristics/API that were wrong about it the
first time. Capped at `RESCAN_SPAM_BATCH_LIMIT` (200) tickets per run
to keep the request bounded when an external API is configured (each
call has its own 5s timeout) -- run it again for the next batch if the
result message suggests there's more backlog left.

**Spam checking only runs on new tickets, not replies.** If someone
replies to an already-existing (thread-matched) ticket, no new spam check
runs -- this avoids unnecessary (potentially paid) external calls and is
also correct in substance: a conversation already recognized as
legitimate does not need to be re-evaluated with every reply.

**New dependency:** `httpx` (for the optional external API) was added to
`requirements.txt` -- requires `docker compose build`, not just
`restart`.

## Stage 2: email integration

**One inbox for both IMAP fetching and SMTP sending**, separate from the
general club SMTP configuration (which is only used for invitation
emails). Configured under `/admin/settings`, in the "Ticket inbox
(IMAP/SMTP)" card. Both passwords are stored encrypted (see
`app/crypto_utils.py`) -- the special-case handling for passwords on save
(empty = leave unchanged) was generalized for this
(`if key.endswith("_password")` instead of one hard-coded special case).

**Background polling without a new service.** An `asyncio` task, started
in the `lifespan` function of `main.py`, calls `process_incoming_mails()`
every 2 minutes. No Celery, no Redis, no separate container -- fits the
project's "small and robust" philosophy. There is also a manual
"Fetch inbox now" button for immediate testing, without waiting for the
next cycle.

**A single inbox for everything -- at the association's request.**
Originally, the ticket-inbox configuration was completely separate from
the general SMTP configuration (its own host/port/user/password fields).
The association deliberately simplified this: "If I want to use a ticket
system sensibly, it only needs a single email address, a single inbox.
Anything else I'd handle on the server and set up forwarding if needed."
The SMTP credentials (host, port, user, password) are therefore now
maintained **once** (`app/email_service.py`, `lade_smtp_konfiguration()`)
and reused for both invitations **and** ticket replies
(`app/ticket_mailer.py` imports that function directly instead of
duplicating its own SMTP fields). Only for IMAP fetching (receiving) are
there additional fields (`imap_host`, `imap_port`, `imap_ssl`) -- the IMAP
user/password are identical to the SMTP credentials, since it's the same
inbox.

**Initial sync skips existing emails.** An inbox that has been in use for
a long time can contain thousands of emails. Without special handling, the
very first fetch would try to retrieve **all** of them individually via
`UID FETCH` -- in practice this caused a `socket error: EOF` (connection
dropped by the mail server due to too many commands in one session). The
fix: if `ticket_imap_letzte_uid` is not yet set, the first fetch only
**determines the current highest UID** (a single `SEARCH`, no `FETCH`)
and stores it as the starting point -- without processing a single email.
From the next cycle onward, only newly arriving emails are processed.
This also matches the expected behavior: nobody wants a years-old mail
archive to suddenly show up in full as tickets in the system.

**Lesson:** for any kind of "since last time" processing (IMAP, but this
also applies to other polling scenarios), explicitly handle the special
case of "there has never been a 'last time'" instead of implicitly
interpreting it as "everything since the beginning of time".

**IMAP runs synchronously in a thread, not async.** There is no mature
async IMAP library among the standard dependencies. Instead of adding a
new one, `app/ticket_mailer.py` uses Python's built-in tools (`imaplib`,
`email`) synchronously, executed via `asyncio.to_thread(...)` so the
event loop isn't blocked in the meantime.

**Fetching never mutates the mailbox.** The inbox is opened
`readonly=True`, and messages are retrieved via `BODY.PEEK[]` rather
than the deprecated `RFC822`/`BODY[]` alias -- a plain (non-peek) body
fetch marks a message `\Seen` on most IMAP servers as a side effect,
which would make mail fetched by Parcella show as already-read in the
association's own mail client. Combined with never issuing
`STORE \Deleted`/`EXPUNGE` (see below), a fetch has zero observable
effect on the mailbox itself.

**Operational data lives in the existing club-settings table.** The most
recently processed IMAP UID and the last error end up as
`ticket_imap_letzte_uid` / `ticket_imap_letzter_fehler` in the same
key-value table that also stores module flags and SMTP settings -- no
additional table/migration just for this purpose.

**Threading via message ID, with a fallback.** Incoming replies are first
matched via the `In-Reply-To`/`References` headers against stored
`message_id` values of previous `TicketMessage` entries. If that fails
(e.g. because the customer writes a new email instead of replying, but
with the same subject), the fallback is to search open tickets by sender
address + normalized subject (with the "Re:"/"Fwd:" prefix stripped). If
no match is found, a new ticket is created.

**Any incoming reply reactivates the ticket** -- CLOSED, POSTPONED, or
WAITING all jump back to `ASSIGNED` (if still assigned) or `ACTIVE`. A
reply from the sender ends whatever "we're waiting" state the ticket was
in, regardless of which one it was (see the ticket-status ADR entry for
the full status set).

**Spam checking is already called, even though it's still a no-op.**
`check_for_spam()` from stage 1 is already called for every incoming
email, and the result is stored in `spam_suspected`/`spam_score` -- only
the actual check logic is still empty. In stage 3, therefore, only this
one function needs to be swapped out, with no changes to callers.

**HTML emails are sanitized and rendered properly, not just stripped
to plain text.** `TicketMessage.content` stays plain text (search,
notifications, and the fallback display for emails with no HTML part).
For emails that do have a `text/html` part, that HTML is additionally
sanitized (see `app/html_sanitizer.py`) and stored in
`TicketMessage.content_html`, then rendered directly on the ticket
detail page. This matters because the content comes from an arbitrary
external sender -- anyone can email the ticket inbox -- so this is a
textbook stored-XSS surface if handled carelessly. The sanitizer:
strips `<script>`/`<style>` tags **and their content** (bleach's own
tag-stripping keeps inner text, which is wrong specifically for these
two), allows only a small set of formatting tags (no `<img>`, to avoid
both tracking pixels and the `onerror=` attack vector), strips all
`style=`/`class=` attributes entirely (no CSS-based tricks like hidden
text), restricts link protocols to `http`/`https`/`mailto` (blocks
`javascript:` URLs), and forces external links to
`target="_blank" rel="noopener noreferrer"`. Sanitization happens once
at ingestion (before anything is written to the database), plus a
second pass via a `sanitize_html` Jinja filter at render time as a cheap
defense-in-depth safety net, in case a future code path ever renders
this content without going through the same ingestion path. Historical
messages received before this feature only have `content` (plain text)
-- there was no way to recover the original HTML after the fact, since
it was never stored.

**Incoming attachments are stored in Nextcloud when configured, with a
local-disk fallback otherwise -- see [ADR
0072](./ADR/0072-ticket-attachment-local-storage-fallback.md).** Until
this feature, any part of an incoming email with `Content-Disposition:
attachment` was silently discarded during MIME parsing
(`_extract_text`/`_extract_html` only ever read `text/plain`/`text/html`
parts). `_extract_attachments()` (`app/ticket_mailer.py`) now also
collects those parts, and `TicketAttachment` (child of `TicketMessage`,
`ON DELETE CASCADE`) records one row per upload. Inline signature
images/logos (typically `Content-Disposition: inline`) are deliberately
excluded -- only parts explicitly marked `attachment` are collected.

**Two backends, tracked per row via `storage_backend`
(`CLOUD`/`LOCAL`).** Preferred: exactly like `IncomingInvoice.cloud_filename`
(see `docs/module-finances.md`), the file bytes never touch Parcella's
own database or filesystem -- `cloud_filename` just names a file inside
**one shared** Nextcloud folder configured for all ticket attachments
(`ClubSetting` key `ticket_attachments_cloud_folder`, set on
`/admin/integrations`' Nextcloud card, next to the incoming-invoices
folder setting), reusing the same `get_nextcloud_provider()` connection
(`app/cloud_storage.py`). Fallback: if `cloud_storage` isn't enabled, or
the folder/credentials aren't configured (or can't be decrypted -- e.g.
after a `SECRET_KEY` rotation), the attachment is written to
`app/private_uploads/ticket_attachments/`
(`app/ticket_attachment_storage.py`) instead of being discarded. Either
way, ticket/message creation itself must never fail because of an
attachment problem, same "must never block" philosophy as the stage-3
spam filter's external-API fallback -- a single attachment over
`MAX_TICKET_ATTACHMENT_SIZE_BYTES` (15 MB), or a failed upload/write, is
skipped individually rather than aborting the whole incoming-mail batch.

Attachments are downloaded through a permission-gated Parcella route
(`GET /tickets/{id}/attachments/{attachment_id}`, `require_permission
"tickets" "read"`) that branches on `storage_backend` -- proxies the
file from Nextcloud for `CLOUD` rows (module-flag-gated the same as
before), reads it from local disk for `LOCAL` rows (not gated by the
`cloud_storage` module, since it never touches Nextcloud). Neither path
goes through the public `/static` mount, since ticket access is
permission-gated (unlike the club logo/avatars, which are intentionally
public) -- `app/private_uploads/` sits outside `app/static/` entirely
for the same reason. Both directories lack a volume mount in
`docker-compose.prod.yml`, so both are included in the admin backup zip
(`app/backup.py`, `docs/operations.md`) to survive a redeploy.

**Filenames from the sender's mail client are never trusted raw.**
`Message.get_filename()` can return a filename with a literal `\r\n`
still embedded, if the sender's mail client folded it across an
unencoded header continuation line -- hit for real with a screenshot
attachment (issue: ticket attachment download crashed with uvicorn's
`RuntimeError: Invalid HTTP header value` instead of downloading,
since the raw string went straight into the `Content-Disposition`
response header). `sanitize_attachment_filename()`
(`app/ticket_mailer.py`) strips control characters and escapes
embedded `"`, applied both at ingestion (`_extract_attachments()`) and
again defensively where the header is built
(`app/routers/tickets.py`'s download route) -- the same "sanitize at
ingestion + a second defensive pass at render time" split already used
for ticket HTML content (`sanitize_email_html`/the `sanitize_html`
Jinja filter). See also CLAUDE.md's "Sharp edges" section.

**Deliberately not built: attachments on outgoing replies.** Staff
composing a reply can already paste any URL -- including a Nextcloud
share link they copied themselves -- into the free-text reply body;
it goes out as plain text in the email like any other link. Building
a picker/upload UI for the outgoing side, or generating Nextcloud
public share links automatically (which would need the separate OCS
Sharing API, not just the WebDAV calls this connector already makes),
was scoped out as more surface than the actual request needed.

**Attachments on tickets received before this feature shipped are
unrecoverable.** The bytes were never stored anywhere during ingestion
of those older emails, so there's nothing in Parcella to retroactively
attach. The original email (attachment included) is almost certainly
still sitting in the mailbox itself, though, since Parcella never
deletes/expunges after fetching -- recoverable by hand via a regular
mail client, just not something Parcella can backfill automatically.

## Overview pagination

The ticket list (`GET /tickets/`) renders the first `TICKETS_PAGE_SIZE`
(50) matching tickets and loads the rest via infinite scroll against
`GET /tickets/list.json`, same pattern as the finance account-bookings
page (`app/routers/finances.py`). Both routes share
`_tickets_filtered_query()` so the HTML page and the JSON continuation
always agree on which tickets match the current filter/search, ordered
by `created_at` with `id` as a tiebreaker (needed for stable offset
paging -- without it, two tickets created in the same instant could be
skipped or duplicated across pages). Previously the list had no limit
at all and rendered every matching row in one table.

## Data model (stage 1)

```
tickets            – a request: subject, status, assignment, sender,
                      optional member link
ticket_messages     – the conversation history of a ticket (incoming/
                      outgoing/internal)
ticket_attachments  – files on an incoming message (stage 2 follow-up);
                      only a Nextcloud filename, never the bytes -- see
                      "Incoming attachments" above
```

## Key decisions

**Access rights via the existing `UserRole`**, not a new, independent
permission system -- the association plans to extend the roles later
anyway (e.g. with a real "extended board" role). A separate ticket
permission system would only have complicated that extension.

**Status as an explicit state machine**, not implicitly derived from the
assignment. Originally just four states
(`UNASSIGNED -> ASSIGNED -> CLOSED`, with `DEFERRED` as a side branch);
redesigned later into six (`ACTIVE`, `ASSIGNED`, `WAITING`, `POSTPONED`,
`CLOSED`, `DELETED`) at the association's request -- see the ticket-status
ADR entry in `docs/ADR/0016-ticket-status-redesign-six-explicit-states-plus-bulk-actions.md` for the full reasoning
(why `WAITING` exists as a distinct state from `POSTPONED`, why
`DELETED` is a status rather than a `deleted_at` column here, and the
bulk-actions UI that came with it). When a ticket is assigned, the
status automatically jumps to `ASSIGNED`; when the assignment is
cleared, it goes back to `ACTIVE`.

**`ASSIGNED` is the one exception to "explicit state machine": it's not
manually selectable.** Both status dropdowns (`tickets/detail.html`,
the bulk-status picker in `tickets/overview.html`) omit it from their
options, and `_apply_status()` / the `PUT /api/v1/tickets/{id}/status`
endpoint reject it outright (400/422) if a client tries anyway --
`ASSIGNED` only ever makes sense with a real `assigned_to_id`, so it's
exclusively set as a side effect of `PUT .../assignment`, never picked
directly. When a ticket's current status is `ASSIGNED`, `detail.html`
shows a read-only badge instead of the dropdown; unassigning (which
reverts to `ACTIVE`) is the only way out short of picking one of the
other five.

**"Postponed until" is a real status flip, not just a computed
display.** Earlier, `DEFERRED` was purely computed on every view
(`status == DEFERRED and deferred_until <= today`) without ever writing
anything back -- meaning a "deferred" ticket stayed visible in the active
list the whole time, just with a badge once overdue. That didn't match
what the association actually wanted (invisible until the date, then
genuinely active again), so a `POSTPONED` ticket is now lazily flipped
to `ACTIVE`/`ASSIGNED` for real -- writing to the database -- the next
time anyone loads the ticket list or that ticket's detail page (see
`_reaktiviere_faellige_tickets()` in `app/routers/tickets.py`). Still no
background job -- just triggered by normal page loads instead of a
purely computed property, which is enough in practice since staff check
the ticket list regularly anyway.

**Member matching by email address is deliberately cautious.** Similar to
the accident-insurance logic: if the sender address can be **uniquely**
matched to a member, that happens automatically. If multiple members
share the same address (e.g. couples), the automation makes **no
decision** -- the UI shows all candidates for manual selection
(`find_members_by_email()` in `app/ticket_utils.py`).

**Assignment notifications use the existing SMTP infrastructure**, not
the ticket inbox that only arrives in stage 2. The general club SMTP
configuration (see the water/electricity-spanning `app/email_service.py`)
is already sufficient for this -- another example of earlier
infrastructure decisions paying off.

**Spam fields already exist in the database** (`spam_suspected`,
`spam_score`), even though the actual check (`app/spam_filter.py`) is
still a pure no-op. This avoids another migration in stage 3 -- only the
check function itself needs to be swapped out.

**Change history is reused.** Status and assignment changes are logged
via the existing generic `ChangeTracker` (`entity_type="Ticket"`) -- no
dedicated history table needed.

## REST API

Complete API from the start (`/api/v1/tickets`), following the "API-first
is now mandatory" rule (see Architecture Decisions). Creating tickets,
changing status/assignment, adding messages -- all also possible
programmatically, e.g. for a later automation of the email import in
stage 2 (which would then likely reuse the same functions internally as
the API, rather than duplicating its own logic).

**Implementation note:** that reuse now exists. Status transitions,
assignment (+ its notification email), member linking, spam-status
changes, and message creation all live in `app/services/tickets.py`,
called by both `app/routers/tickets.py` and `app/routers/api_tickets.py`
-- see ADR 0070 for why and how. The API router also now checks
permissions the same fine-grained, `Group`-based way the HTML side does
(`require_api_permission`, ADR 0070), not the coarser role-only check
most other API routers still use.
