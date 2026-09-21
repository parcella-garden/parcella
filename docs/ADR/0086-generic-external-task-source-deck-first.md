# Generic external task-source sync, Nextcloud Deck as the first provider

**Context:** kermie wanted tasks imported from a club's existing
Nextcloud "Deck" board into Parcella's task board, kept in sync on an
ongoing basis ("for a while" -- a migration aid while the club
transitions off Deck, not necessarily forever), explicitly built as a
generic, pluggable concept rather than a Deck-hardcoded feature, with
the admin setup UX matching the existing cloud-storage integration's
pattern.

**Decision:**

1. **A real provider interface, not just a Deck client.**
   `app/task_sync.py`'s `TaskSyncProvider` (`test_connection()`,
   `fetch_board(board_id)`) mirrors `app/cloud_storage.py`'s
   `CloudStorageProvider`/`NextcloudProvider` split exactly:
   `DeckTaskProvider` is the only implementation today, a future second
   source is a new class implementing the same interface, not a change
   to this one. The genericity that actually matters lives in this
   interface and in `ExternalTaskLink.source` (a column, not a table
   name) -- **not** in the sync orchestration
   (`app/deck_sync.py::sync_deck_tasks`), which stays Deck-specific for
   now since there's nothing else to dispatch to yet. Building a
   generic multi-source sync orchestrator before a second source exists
   would be speculative abstraction for a case that doesn't exist.

2. **Deck sync gets its own `ClubSetting` credentials
   (`deck_base_url`/`deck_username`/`deck_app_password`), never
   cloud storage's `nextcloud_*` ones**, even though a club's Deck board
   and their cloud storage will almost always live on the same
   Nextcloud instance in practice. Cloud storage's whole point
   (`docs/module-cloud-storage.md`) is staying backend-agnostic so
   Seafile/Google Drive/S3 remain viable alternatives. Wiring Deck sync
   to reuse cloud storage's stored credentials would quietly couple
   that abstraction to a Nextcloud-specific feature: a club on Seafile
   could never use Deck sync, and swapping cloud storage backends would
   silently break Deck sync too. The cost is a small, accepted
   redundancy -- the same URL/username typed twice for a Nextcloud-based
   club -- in exchange for keeping the two features fully decoupled.

3. **One-way, read-only mirror, not two-way sync.** Deck owns a synced
   card's title/description/due date/list; editing those in Parcella
   isn't offered (the modal renders them `readonly`/`disabled`) rather
   than allowed-and-then-silently-overwritten on the next sync. Tags,
   priority, assignees, and comments are Parcella-only concepts Deck
   has no equivalent for, so they're never touched by sync and always
   editable regardless of link status. Two-way sync was considered and
   rejected for this version: it needs conflict resolution (what if
   both sides changed the same card since the last sync?) and write
   access to Deck, not just read -- meaningfully more scope than
   kermie's actual ask ("have these tasks synchronized for a while").
   An explicit **"Adopt into Parcella"** action (`POST
   /tasks/{id}/adopt`) lets a card graduate out of the mirror
   permanently once the club is ready to stop tracking it against Deck,
   without needing two-way sync to get there.

4. **Detach, never delete, on disappearance.** When a previously-synced
   card is deleted or archived in Deck, the next sync removes only its
   `ExternalTaskLink` row -- the `Task` itself is left alone, exactly as
   if it had been manually adopted. This follows
   [ADR 0005](./0005-historization-ending-instead-of-deleting.md)'s existing
   historize-over-delete principle: a sync run should never be the
   reason board content silently disappears from Parcella, even if the
   external source it came from stopped tracking it.

5. **Single configured board for v1**, not a multi-board picker. Matches
   "import all desk[sic] tasks" as one club-wide board -- the simplest
   shape to reason about, and to map onto Parcella's own single task
   board. A club with several Deck boards worth pulling in is a real
   but unaddressed case, left as a follow-up rather than building a
   board-picker UI nothing yet asked for.

6. **Board id is a plain text field, not a live-fetched dropdown.**
   Matches `freescout_mailbox_id`'s existing precedent (a numeric/string
   ID field with a hint pointing at where to find it in the source
   system's own UI) rather than inventing a new "test connection, then
   populate a picker from the response" UI pattern this app has nowhere
   else. Reuse over invention.

**Consequences:** no migration needed for the sync mechanism's
genericity itself (`ExternalTaskLink.source` already allows a second
provider without a schema change) -- only the one new table needed for
Deck-linking at all. The activity-report export
(`app/task_report.py`) and the change-history display do not yet call
out "this change came from Deck sync" specially; a `list_id` history
entry written by a sync run looks identical to one written by a human
move except for its blank "changed by" -- acceptable for v1, a labeled
"via Deck sync" distinction is a reasonable follow-up.
