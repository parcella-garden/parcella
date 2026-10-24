# Support module (helpdesk)

Parcella doesn't implement its own ticket system ([ADR 0080](./ADR/0080-remove-builtin-ticket-module-freescout-conversation-bridge.md)).
Support conversations live in the club's helpdesk, chosen from a
dropdown on Admin -> Integrations -> Support / helpdesk, one at a time
([ADR 0107](./ADR/0107-helpdesk-providers-and-capabilities.md)):
FreeScout, Zammad, Znuny / OTRS, osTicket, Zendesk or Freshdesk. This
module is a thin layer on top of it.

The module flag is still called `freescout_bridge` (and the Group
permission too): nav order, settings and permissions hang off that key,
so only its label changed.

What the module provides:

1. A **"Support" nav link** for every logged-in user: a plain member
   links straight to the helpdesk's web address; a staff member with
   `freescout_bridge` read permission links to Parcella's own
   `/support/` view instead (see 2).
2. A **staff-facing conversation list/detail view**, gated by Group-based
   `freescout_bridge` read/write permission (ADMIN/BOARD bypass as
   always): which conversation belongs to which member/parcel, the
   transcript (fetched live, not stored), and promoting a conversation
   onto the task board. Answering the customer happens in the helpdesk
   itself, never from Parcella (ADR 0111).
3. The **public contact form** (`POST /api/v1/public/contact`, its own
   `public_contact_api` flag) creates a new conversation in the helpdesk.

## Capabilities: what each helpdesk can do

Not every helpdesk API offers everything. Each provider class in
`app/helpdesk/` declares its `capabilities`, and every caller checks
before using a feature -- a missing capability is hidden or explained,
never a broken button or a 500:

| | inbox (list, sync, badge) | read | create (contact form) | customer_sync |
|---|---|---|---|---|
| FreeScout | ✅ | ✅ | ✅ | ✅ |
| Zammad | ✅ | ✅ | ✅ | ✅ |
| Znuny / OTRS | ✅ | ✅ | ✅ | – (no web-service operation for customer users) |
| osTicket | – | – | ✅ (its API can only create tickets) | – |
| Zendesk | ✅ | ✅ | ✅ | ✅ |
| Freshdesk | ✅ | ✅ | ✅ | ✅ |

There is deliberately no "reply" capability: see ADR 0111.

With osTicket, `/support/` says that requests are answered in osTicket and
links there; the sync loop does nothing.

Every provider maps its own states onto five: `active`, `pending`,
`closed`, `spam`, `deleted`. `closed`/`deleted`/`spam` are synced but
hidden from the lists, the nav badge and the dashboard card (issue
#230), so a reopened conversation still has its member waiting for it.

## Data model

```
helpdesk_conversation_links  -- cross-reference only, not a message mirror
helpdesk_customer_ids        -- member <-> customer id, per helpdesk
```

**`HelpdeskConversationLink`** (`app/models.py`): `provider` (registry
type, e.g. `freescout`) + `external_id` (string; unique together),
`mailbox_id` (mailbox/group/queue as the helpdesk names it), `subject`,
`customer_email`, `customer_name`, `status` (one of the five above),
`message_count` (a hint for staff, never a trigger), `member_id`,
`parcel_id`, `task_id` (all nullable), `external_updated_at`,
`last_synced_at`. Never a copy of the messages: the transcript is fetched
live on every detail-page view (`app/routers/support.py`), so the
helpdesk stays the only store of conversation content.

Rows of a helpdesk that isn't active anymore stay in the table and are
filtered out by `provider`; switching back shows them again. Switching
never deletes anything.

**`HelpdeskCustomerId`**: the persistent identity mapping, one row per
member and helpdesk (unique per helpdesk on both the member and the
customer id), since every helpdesk numbers its customers differently.
Migration 0107 moved the old `members.freescout_customer_id` values here.

## Member/customer matching hierarchy

Applied by the poll loop (`app/helpdesk/sync.py`) for every conversation:

1. A stored `HelpdeskCustomerId` for this helpdesk and customer id --
   exact, no ambiguity possible.
2. Otherwise `find_members_by_email()` (`app/member_matching.py`):
   exactly one match auto-associates and stores the customer id; more
   than one (a couple sharing an inbox) or none (a neighbor, a vendor)
   leaves the conversation unassociated. Unassociated conversations are
   not flagged anywhere (issue #231).

A conversation staff has associated (or the automation auto-matched) is
never re-matched by a later poll. The parcel is auto-set only when the
member has exactly one *current* parcel.

## Customer identity sync (Parcella -> helpdesk)

`app/services/members.py`'s `update_member()` renames the member's
customer record in the active helpdesk when their name changes -- only
if that helpdesk has `customer_sync` and a `HelpdeskCustomerId` exists,
and never blocking the member edit if the helpdesk is unreachable.
Deliberately lazy: a customer is only linked the first time a member
writes in, never pushed proactively.

## Sync: polling, not webhooks

`app/main.py`'s lifespan runs `sync_helpdesk_conversations()` every 5
minutes for the active helpdesk (inbox capability only). Polling needs
no inbound webhook endpoint and works when Parcella isn't reachable from
the helpdesk. Upserts are idempotent on `(provider, external_id)`. The
`updated_since` cursor is the newest `external_updated_at` of that
helpdesk's rows.

**Deletions need a reconciliation pass**: most helpdesks just stop
returning a deleted conversation instead of reporting it as changed, so
`_reconcile_deletions()` re-checks every visible row of the helpdesk by
id (`get_status()`, `None` = gone) on every poll -- bounded by what
Parcella has synced, not by the helpdesk's history.

## Provider notes

- **FreeScout** (`freescout.py`): `X-FreeScout-API-Key`. Its
  `GET /api/conversations` defaults to status "active" and returns one
  page, so the provider loops every status (`active`/`pending`/`closed`/
  `spam`) and every page (hit for real: issue #222). A deleted
  conversation is a 404 *or* a normal answer with `state: "deleted"`
  while `status` still reads "active" (hit for real). Single mailbox
  (`mailbox_id`, default 1).
- **Zammad** (`zammad.py`): `Authorization: Token token=...`. Lists via
  `/api/v1/tickets?expand=true` and filters by `updated_at`, because
  `/tickets/search` needs Elasticsearch. Finds customers by searching
  the plain address (the `email:"..."` syntax also needs Elasticsearch)
  and creates them with the visitor's name -- `guess:<email>` would
  create a nameless customer. Internal notes are left out of the
  transcript.
- **Znuny / OTRS** (`znuny.py`): the GenericInterface web service from
  `integrations/znuny/` must be imported first. Logs in with
  `SessionCreate` so the password never appears in a URL. Errors often
  come as HTTP 200 with an `Error` object. Times are server-local with no
  time zone, so the incremental sync looks back one extra day. Only
  customer-visible articles are shown. Znuny refuses customer addresses
  it considers invalid (its `example.*` blocklist, MX check).
- **osTicket** (`osticket.py`): `X-API-Key`, bound to Parcella's server
  IP in osTicket. "Test connection" posts an empty ticket: 400 = key
  works (nothing created), 401 = wrong key or IP. osTicket also refuses
  addresses with invalid domains.
- **Zendesk** (`zendesk.py`): `<email>/token` basic auth. Incremental
  cursor export with side-loaded users; wrong credentials come back as
  an anonymous user, not a 401. Public comments only.
- **Freshdesk** (`freshdesk.py`): API key as basic-auth user. Without
  `updated_since` its list only covers 30 days, so the first sync asks
  from 2000 on. Statuses are numbers (2 open, 3 pending, 4 resolved,
  5 closed) plus a `spam` flag. Private notes are left out.

Live-tested on 2026-10-22: FreeScout against the club's real mailbox
(read only), Zammad 6.5, osTicket (devinsolutions image) and OTRS 6 (as
Znuny's base) in temporary containers. Zendesk and Freshdesk only
against simulated answers.

## Routes and API

- Web: `/support/`, `/support/{id}` (+ member, parcel, task POSTs). `/freescout/...` redirects there (301).
- REST: `/api/v1/helpdesk/conversations...` with neutral field names;
  `/api/v1/freescout/conversations...` is the same, marked deprecated,
  with the old field names (`freescout_conversation_id` etc., read-only
  properties on the model), so existing API clients keep working.
- Settings: `/api/v1/helpdesk` (GET/PUT), `/providers`, `/test` --
  ADMIN only, secrets never accepted or returned (shared with the website
  and cloud storage settings, `app/routers/api_provider_settings.py`).

## Task board, and no replies

A conversation can be promoted to a new task (admin/board only, matching
the task board's own gating) or linked to an existing one; `task_id` is a
loose `SET NULL` link.

Parcella doesn't reply to customers -- not in the web UI, not through the
REST API (removed 2026-10-24, ADR 0111). The detail page links to the
conversation in the helpdesk, where answers are written.

## Known gaps / deliberate scope cuts

- No attachments -- open the conversation in the helpdesk for those.
- The transcript is fetched live on every view, not cached.
- Customer sync is name-only and lazy.
- One mailbox/group/queue per helpdesk.
- No automatic task-creation rules.
- osTicket can't be listed, read or answered from Parcella; a small
  osTicket plugin could add that later (the same ecosystem idea as the
  website plugins, ADR 0105).
