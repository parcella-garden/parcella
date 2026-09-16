# 80. Remove the built-in ticket module; add a FreeScout conversation bridge

## Status

Accepted.

## Context

Parcella's ticket module (`Ticket`/`TicketMessage`/`TicketAttachment`,
IMAP polling, a two-layer spam filter) was explicitly designed as a
lightweight FreeScout-alike (see the removed `docs/module-tickets.md`:
"modeled loosely after Freescout"). The club now runs a real FreeScout
instance for support communication, making the built-in module a second,
less-capable implementation of the same thing.

An initial design pass scoped a much deeper integration (persistent
member <-> FreeScout-customer identity mapping via a generic
`external_identity` table, full bidirectional customer sync, webhook-driven
sync, an embedded conversation view, task-board linking, reply-from-Parcella)
against FreeScout's actual REST/webhook API. Before implementation, this
was deliberately cut back twice in conversation with the person
requesting the feature:

1. First cut: replace the ticket module with nothing more than a plain
   external link to FreeScout. Rejected as too little -- conversations
   needed to be visible inside Parcella (with member/parcel context) and
   promotable to the task board, not just a link out.
2. Final scope (this ADR): a real API integration, but intentionally
   smaller than the original full design in specific, deliberate ways
   (see Decisions below).

There is also prior, never-merged work in this exact direction: a parked
git stash ("WIP: freescout bridge") had already started a
`FreescoutConversationLink` cross-reference model, a `freescout_bridge`
module flag, and a `task_board.py` refactor extracting a shared
`create_task()` helper specifically for this bridge. That design's
naming and shape are reused directly rather than reinvented.

## Decisions

- **The ticket module is removed entirely, including its database
  tables** (`tickets`, `ticket_messages`, `ticket_attachments`) --
  migration `0087_remove_ticket_module`. This is a deliberate,
  destructive choice, explicitly confirmed by the project owner,
  overriding this project's usual "historization over deletion"/"never
  destroy data" defaults. Shipped as a MAJOR version bump with release
  notes calling out the destructive migration and instructing a database
  backup first. Local-disk ticket attachment files and the
  `data/ticket_attachments/` bind mount are not touched/removed by the
  migration itself (a migration shouldn't do filesystem I/O) -- left for
  manual cleanup, called out in release notes.
- **FreeScout is the sole ticket system** -- Parcella never re-implements
  IMAP polling, spam filtering, or local message storage again.
  `FreescoutConversationLink` is a cross-reference only; the actual
  message transcript is always fetched live from FreeScout's API, never
  duplicated into Parcella's database (`docs/module-freescout-bridge.md`).
- **Identity mapping is a single column, not a generic table.** The
  original design's `external_identity(provider, external_id)` table
  anticipated multiple future external systems. With exactly one real
  system in play, `Member.freescout_customer_id` (a plain nullable
  unique column) is the right amount of structure -- a second provider,
  if one ever actually appears, is a rename/migration away. Building the
  generic version now would be a premature abstraction with no second
  consumer to validate it against.
- **Customer sync is lazy and name-only**, not the originally-scoped
  eager bidirectional sync of every member on creation. A FreeScout
  customer is only created/linked the first time a member is actually
  matched to a conversation; only the name is kept in sync afterward.
  Avoids pushing every club member's personal data into a third-party
  system before they've ever contacted support.
- **Polling, not webhooks**, despite FreeScout supporting the latter
  (`X-FreeScout-Signature`, HMAC-SHA1). This codebase has never received
  an inbound webhook and has a stated "no Celery, no Redis, no separate
  container" philosophy for background work -- polling fits the existing
  asyncio-loop-in-lifespan pattern used by the old ticket-IMAP poller,
  the GitHub update-check, and the cloud-backup scheduler. Polling also
  sidesteps a real deployment constraint a webhook would introduce: a
  self-hosted Parcella instance behind NAT/no public IP couldn't receive
  one, whereas polling only needs Parcella to reach FreeScout, which
  every self-hosted club already needs for its other integrations.
- **The public contact-form bridge** (`POST /api/v1/public/contact`,
  ADR 0074) is rewritten to call `FreeScoutClient.create_conversation()`
  directly instead of creating a local `Ticket`. This is strictly better
  than the "send a plain email to the shared inbox" alternative
  considered in discussion: going through the API sets the correct
  customer/mailbox metadata directly, with no ambiguity about which
  address FreeScout would otherwise treat as the customer (a plain email
  sent through the club's own SMTP account would appear to come from the
  club, not the actual visitor).
- **A plain "Support" nav link is visible to every logged-in Parcella
  user**, independent of the finer `freescout_bridge` Group permission
  gating the staff-facing conversation view -- addressing the explicit
  requirement that every member, not just staff, has a way to reach
  support from inside Parcella.

## Consequences

- Self-hosted clubs must configure FreeScout under Admin -> Integrations
  to get any support-conversation visibility inside Parcella after
  upgrading; the plain nav link still works with just a base URL
  configured, independent of full API credentials.
- `docs/module-tickets.md` and this ADR's several ticket-specific
  predecessors (0016, 0017, 0038/0066 spam filter, 0067, 0072, 0074's
  original ticket-creation behavior) describe a module that no longer
  exists -- they remain as historical record (ADRs are never rewritten),
  but a reader should not assume any of that code is still present.
- The parked git stash this design builds on should be considered
  superseded -- this ADR and `docs/module-freescout-bridge.md` are now
  the authoritative design, not the stash.
