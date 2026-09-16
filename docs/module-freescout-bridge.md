# FreeScout bridge module

Parcella doesn't implement its own ticket/helpdesk system. FreeScout
(https://github.com/freescout-help-desk/freescout, or any similarly
API-shaped helpdesk) is the sole, canonical system for support
conversations and email communication. This module is a thin bridge on
top of it -- see [ADR 0080](./ADR/0080-remove-builtin-ticket-module-freescout-conversation-bridge.md)
for why the previous built-in ticket module was removed in favor of
this design.

Two independent things this module provides, both behind the single
`freescout_bridge` module flag:

1. A **"Support" nav link**, visible to every logged-in Parcella user
   regardless of Group permission -- a plain member links straight to
   the configured FreeScout instance; a staff member with
   `freescout_bridge` read permission links to Parcella's own
   `/freescout/` view instead (see 2).
2. A **staff-facing conversation list/detail view** inside Parcella,
   gated by Group-based `freescout_bridge` read/write permission (same
   model the old ticket module used, ADMIN/BOARD bypass as always) --
   which conversation belongs to which member/parcel, the full message
   transcript (fetched live, not stored), reply-to-customer, and
   promoting a conversation onto the task board.

## Data model

```
freescout_conversation_links  -- cross-reference only, not a message mirror
members.freescout_customer_id -- persistent identity mapping (new column)
```

**`FreescoutConversationLink`** (`app/models.py`) is a lightweight
cross-reference to one FreeScout conversation: `freescout_conversation_id`
(unique), `freescout_mailbox_id`, `subject`, `customer_email`,
`customer_name`, `freescout_status` (FreeScout's own status string,
stored as-is -- deliberately not mapped onto any Parcella enum),
`message_count` (a hint for staff deciding which conversations are
worth promoting to a task, not an automatic trigger), `member_id`
(nullable), `parcel_id` (nullable), `task_id` (nullable), and sync
bookkeeping (`freescout_updated_at`, `last_synced_at`). It is explicitly
**not** a mirror of FreeScout's messages or attachments -- the actual
transcript is fetched live from FreeScout's API every time a
conversation's detail page is opened (`app/routers/freescout.py`), never
duplicated into Parcella's database. This keeps FreeScout the single
canonical store for conversation content and avoids unnecessarily
duplicating personal data (email content) across two systems.

**`Member.freescout_customer_id`** (nullable, unique) is the persistent
identity mapping: once a FreeScout customer has been resolved to a
Parcella member, future conversations from that same customer resolve
directly via this column rather than re-matching by email every time.

## Member/customer matching hierarchy

Applied by the poll loop (`app/freescout_sync.py`) for every conversation:

1. `Member.freescout_customer_id == conversation.customer.id` -- exact,
   persisted, no ambiguity possible.
2. Otherwise, `find_members_by_email()` (`app/member_matching.py`,
   case-insensitive against `MemberEmail`):
   - Exactly one match -> auto-associate, and backfill
     `Member.freescout_customer_id` so step 1 short-circuits next time.
   - More than one match (e.g. a couple sharing an inbox) -> leave
     `member_id` NULL, surfaced in the staff UI as "needs association"
     with the candidate members to choose from.
   - No match -> leave unassociated (a non-member inquiry -- normal and
     expected, e.g. a neighbor or vendor).

Once staff has manually associated (or the automation has auto-matched)
a conversation, a later re-poll never re-runs this matching for that row
-- it would otherwise be possible for a staff correction to be silently
overwritten by the next poll cycle.

Parcel association is auto-set only when the resolved member has
exactly one *current* parcel (`MemberParcel.is_current` /
`current_tenant_filter()`, `app/database.py`); left NULL and shown as a
selector in the UI when the member has more than one. Never guessed.

## Customer identity sync (Parcella -> FreeScout)

Parcella pushes to FreeScout, not just reads from it: once a member is
matched to a conversation, `app/services/members.py`'s `update_member()`
keeps that member's FreeScout customer record's name in sync whenever
their name changes (via `FreeScoutClient.update_customer()`), silently
skipped if FreeScout is unreachable/unconfigured -- a member edit must
never fail because of an external service outage.

**Deliberately lazy, not eager**: a FreeScout customer is only ever
created/linked the first time a member is actually matched to an
inbound conversation, not proactively for every member on creation.
Pushing every club member's personal data into a third-party system
before they've ever contacted support would be unnecessary duplication.
If a club wants proactive sync instead, that's a small, explicit change
to make (call `FreeScoutClient.create_customer()`/`find_customer_by_email()`
from the member-creation path too) -- not done here as a documented,
deliberate scope cut, not an oversight.

## Sync mechanism: polling, not webhooks

A background asyncio loop (`app/main.py`'s lifespan, same pattern as the
old ticket-IMAP poller, the GitHub update-check, and the cloud-backup
scheduler -- no Celery, no Redis, no separate worker container) polls
FreeScout's `GET /api/conversations` every 5 minutes for the configured
mailbox, filtered by `updatedSince` the last successful sync. This was a
deliberate choice over FreeScout's supported webhooks (`X-FreeScout-Signature`
HMAC-SHA1): polling needs no new inbound-webhook infrastructure (this
codebase has never received one), and works even when a self-hosted
Parcella instance isn't reachable from the FreeScout instance -- polling
only needs outbound access from Parcella to FreeScout, which every
self-hosted club already needs for other integrations (WordPress,
Nextcloud).

Upserts are idempotent by `freescout_conversation_id` (find-or-create,
never a blind insert) -- a duplicate/overlapping poll never creates two
rows for the same conversation.

**Closed and deleted conversations are still synced, but hidden from
display.** `app/freescout_sync.py`'s `HIDDEN_STATUSES` (`"closed"`,
`"deleted"`) is excluded from the `/freescout/` list, the
`/api/v1/freescout/conversations` list, and the dashboard's "needs
association" stat -- but the poller keeps updating those rows normally,
so a conversation that gets reopened in FreeScout still has an accurate,
already-matched `member_id` waiting for it rather than a stale row
nobody bothered to keep in sync.

## FreeScout API client

`app/freescout_client.py`'s `FreeScoutClient` follows the same shape as
`app/blog_publisher.py`'s `WordPressPublisher` and `app/cloud_storage.py`'s
`NextcloudProvider`: an injectable `httpx.AsyncClient` (tests use
`httpx.MockTransport`), a domain-specific `FreeScoutError`, and a
`load_freescout_configuration()`/`get_freescout_client()` factory pair
returning `None` when unconfigured. Auth is FreeScout's documented
`X-FreeScout-API-Key` header. Credentials (base URL, API key, mailbox
ID -- default `1`) are configured on Admin -> Integrations, alongside
WordPress/Nextcloud, with the API key Fernet-encrypted
(`app/crypto_utils.py`) and "empty field on save = leave unchanged."

## Task board bridge

Reuses `app/task_board.py`'s `create_task()` helper (shared with
`app/routers/tasks.py`/`api_tasks.py`) rather than a separate
construction path. A conversation can be **promoted to a new task**
(pre-filled title/description, admin/board-only -- matching the task
board's own existing gating, not the finer `freescout_bridge`
permission) or **linked to an existing one**. The link is a loose,
nullable `FreescoutConversationLink.task_id` (`SET NULL` on task
deletion) -- deleting a task never breaks the conversation link, it just
becomes unlinked again.

## Reply-to-customer

A conversation's detail page has a reply box; its POST handler calls
`FreeScoutClient.create_thread()`, which FreeScout emails out. Kept
entirely separate from Parcella's internal task comments (`TaskComment`,
purely internal, used once a conversation is promoted to a task) -- there
is no shared "notes" widget that could accidentally send an internal
remark to the customer.

## Public contact-form bridge

`POST /api/v1/public/contact` (`app/routers/api_public.py`, its own
`public_contact_api` module flag, independent of `freescout_bridge`) --
used by the parcella-connector WordPress plugin's contact form -- calls
`FreeScoutClient.create_conversation()` directly rather than sending a
plain email, so the customer's email/name are attributed correctly by
FreeScout from the start (no ambiguity about which address FreeScout
treats as the customer, the way a plain email through a club's own SMTP
account would have).

External, non-member senders reach FreeScout by emailing the mailbox's
address directly -- nothing to build for that path; FreeScout ingests it
the normal way and the next poll picks up the resulting conversation
like any other.

## Known gaps / deliberate v1 scope cuts

- No attachment support -- a conversation's attachments are only visible
  by opening it in FreeScout itself.
- The message transcript is fetched live on every detail-page view, not
  cached -- acceptable at a small club's traffic volume; worth revisiting
  if FreeScout's API becomes a latency bottleneck.
- Customer sync is name-only and lazy (see above) -- no phone/address
  sync, no proactive creation.
- Single mailbox only (`freescout_mailbox_id`, default `1`) -- multiple
  mailboxes would need a per-mailbox configuration, not built here.
- No automatic task-creation rules -- promoting a conversation to a task
  is always a manual staff action; `message_count` is shown as a hint,
  never a trigger.
