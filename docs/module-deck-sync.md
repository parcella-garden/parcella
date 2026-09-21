# Nextcloud Deck sync module

Pulls cards from a club's existing Nextcloud Deck board into Parcella's
own task board (see `docs/module-tasks.md`), kept up to date
automatically -- meant as a migration aid for a club moving off Deck
onto Parcella's own board, not a permanent two-way integration. Off by
default (`deck_sync` module flag defaults to `False`), since it stores
outbound credentials and, once configured, pulls external content into
the task board automatically via a background poller.

One-way, read-only mirror: Deck is the source of truth for a synced
card's title/description/due date/list. Priority, tags, assignees, and
comments are Parcella-only concepts Deck has no equivalent for, so
they're always freely editable, sync or no sync. See
[ADR 0086](./ADR/0086-generic-external-task-source-deck-first.md) for
the full reasoning, including why this reuses a generic provider
interface (Deck is the first implementation, not the only one this was
designed for) and why it deliberately does **not** share cloud
storage's Nextcloud credentials even though they usually point at the
same server.

## Data model

```
external_task_links  -- one row per synced Task, ON DELETE CASCADE
                         from tasks.id
```

**`ExternalTaskLink`** (`app/models.py`) is the cross-reference: `source`
(`"deck"` today -- a column, not a table name, so a second source never
needs a schema change), `external_board_id`/`external_stack_id`/
`external_card_id`, `external_updated_at` (Deck's own last-modified
timestamp for the card -- the incremental-sync high-water-mark), and
`last_synced_at`. Unique on `(source, external_card_id)`. `ON DELETE
CASCADE` is the reverse of most FKs in this app (which prefer `SET
NULL`, see `docs/module-freescout-bridge.md`'s `FreescoutConversationLink.task_id`)
-- a link has no meaning without the Task it points at, so deleting the
Task should delete the link, not leave it dangling.

**Presence of this row is what makes a card "synced".** Removing it --
via the admin "Adopt into Parcella" action or automatically when a card
disappears from Deck (see Reconciliation below) -- turns the Task into
a normal, fully-independent, fully-editable one from then on. The `Task`
row itself is never touched by either path; only the link is removed.

No changes to `Task` itself beyond one new relationship
(`Task.external_link`, one-to-one).

## The connector: `app/task_sync.py`

Structured like `app/cloud_storage.py`: a small `TaskSyncProvider`
interface (`test_connection()`, `fetch_board(board_id)`) with one
concrete implementation, `DeckTaskProvider`, talking to Deck's REST API
(`{base_url}/index.php/apps/deck/api/v1.0/...`, `OCS-APIRequest: true`
header, HTTP Basic auth with a Nextcloud Application Password -- same
auth *shape* as cloud storage's WebDAV connector, different base path
and credentials). A future second task source would be a new class
implementing the same interface, not a change to this one.

**Not yet verified against a live Deck instance** (none was reachable
while building this): `fetch_board()` assumes `GET
/boards/{id}/stacks` returns each stack with its cards already nested,
per Deck's documented API shape, and defensively parses a card's own
"last modified" timestamp as either a Unix epoch integer or an ISO-8601
string, falling back to `now()` if neither parses (same defensive
convention as `app/freescout_sync.py`'s `_parse_datetime`). Worth a
real-instance smoke test before relying on it.

Every failure mode raises `DeckError` with a message meant to be shown
directly to the admin who triggered the action (Admin -> Integrations'
flash message, or a logged warning from the background poller).

## Credentials, deliberately separate from cloud storage's

`ClubSetting` rows `deck_base_url`/`deck_username`/`deck_app_password`
(Fernet-encrypted, `app.crypto_utils`) plus `deck_board_id` (the single
Deck board to sync from -- plain text, not encrypted, matching how
`freescout_mailbox_id` is stored). Configured on Admin -> Integrations,
same page as every other outbound connector, with the same "blank app
password field on save = leave the existing one unchanged" convention.

Even though a club's Deck board and their cloud storage almost always
live on the same Nextcloud instance, these are **not** the same
`ClubSetting` keys as cloud storage's `nextcloud_*` ones. Reusing them
would couple cloud storage's deliberately backend-agnostic abstraction
(`docs/module-cloud-storage.md`) to a Nextcloud-specific feature -- a
club on Seafile/Google Drive/S3 could never use Deck sync, and swapping
cloud storage backends would silently break it too.

## Sync algorithm: `app/deck_sync.py`

`sync_deck_tasks(db)` -- no-ops (returns 0) if Deck isn't configured or
no board is chosen. Otherwise:

1. Fetches the configured board's stacks (each with its cards).
2. **Stack -> list mapping**: each stack is matched to a `TaskList` by
   name, created (at the end of the board, in Deck's own stack order)
   if none matches yet.
3. **Card -> task upsert**, by `(source="deck", external_card_id)`:
   - Archived Deck cards are **never created**, and are treated
     identically to a card that has disappeared entirely for
     reconciliation purposes (below) -- excluded from the "seen" set
     regardless of whether Deck's own API happens to still return them.
   - An already-linked card whose `external_updated_at` hasn't advanced
     since the last sync is skipped (the incremental-sync check).
   - Otherwise title/description/due_date are overwritten from Deck,
     and if the card's stack changed, the linked `Task` is moved to the
     new list via `app/task_board.py`'s `move_task()` -- the same
     function drag-and-drop and the edit form use, so a Deck-driven
     move renumbers positions correctly and writes a `list_id`
     `ChangeHistory` entry (see `docs/module-tasks.md`'s change-history
     section) just like a human-driven move would, just attributed to
     no user (`changed_by_id=None`) since none made this specific
     change.
4. **Reconciliation**: any `ExternalTaskLink` for this board whose card
   wasn't in this run's "seen" set (deleted or archived in Deck) has
   its link row removed -- the `Task` itself is untouched (this repo
   historizes over deletes, ADR 0005), it just stops being tracked as
   synced. Same end state as the manual Adopt action.

## Task board UI

A linked task shows a small cloud badge on its kanban card and in the
edit modal (`app/templates/tasks/board.html`, `#taskModal` from ADR
0084). In the modal, title/description/due date render `readonly` and
the list dropdown `disabled` (with a hidden input carrying its current
value through, since a disabled `<select>` submits nothing but
`task_update()`'s form still expects the field) -- Deck owns those
fields. Priority/tags/assignees/comments stay fully editable. An
"Adopt into Parcella" button (`POST /tasks/{id}/adopt`, admin-only)
deletes the link.

## Background poller and manual sync

`app/main.py`'s `_deck_sync_polling_loop()` ticks every 15 minutes,
same `asyncio.create_task`-in-`lifespan` pattern as the other three
periodic jobs in this app (FreeScout polling, the update check, cloud
backups -- no Celery, no separate worker). Unlike the FreeScout loop,
this one also checks the `deck_sync` module flag itself, not just
whether credentials are present -- pausing an already-configured sync
doesn't require clearing the credentials. A "Sync now" button on Admin
-> Integrations (`POST /admin/integrations/deck/sync-now`) calls the
exact same `sync_deck_tasks()` function on demand, same precedent as
`POST /admin/backup/cloud/run-now`.

## Scope, deliberately narrow for v1

- **One configured board.** Not a board picker, not multiple boards
  synced at once -- a club with several Deck boards worth pulling in is
  a real but unaddressed case, left as a follow-up.
- **Assignee sync**: not implemented. `Task.assigned_to_ids` is a
  derived property over the `TaskAssignee` join table, not a plain
  column -- syncing Deck's `assignedUsers` would need matching Deck
  users to Parcella `User`s by some identity and a bespoke diff, not a
  good fit for the simple field-copy this sync otherwise does. A
  reasonable follow-up, not done here.
- **The task-board activity report** (`docs/module-tasks.md`'s Markdown
  export) does not yet read `external_task_links` or call out synced
  cards specially -- a synced card's history/comments still export
  normally, it's just not flagged as Deck-sourced in that report.

## Testing

`tests/test_deck_sync.py`: `DeckTaskProvider` against a mocked
`httpx.AsyncClient` (`httpx.MockTransport`, same technique
`app/cloud_storage.py`'s tests use -- no real Nextcloud/Deck instance is
reachable from this project's test/CI environment); `sync_deck_tasks()`
end to end (create, incremental skip, update + list move, archived-card
exclusion, reconciliation-on-disappearance); the admin save/test/
sync-now routes and their admin-only permission boundary; the task
board's locked-fields rendering and the Adopt action.
