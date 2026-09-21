"""
Nextcloud Deck sync: fetches the configured board from Deck and upserts
app.models.ExternalTaskLink + Task rows, one-way (Deck -> Parcella,
read-only mirror -- see docs/ADR/0086 and docs/module-deck-sync.md).
Called every 15 minutes from app/main.py's lifespan (same
asyncio-loop-in-lifespan pattern as the FreeScout/update-check/cloud-
backup loops -- no Celery, no separate worker), and on demand from the
admin integrations page's "Sync now" button.

Deck-specific orchestration for now, not a generic multi-source
dispatcher -- there's only one TaskSyncProvider implementation
(app/task_sync.py's DeckTaskProvider) today. Genericity lives in the
provider interface and the ExternalTaskLink.source column, not in
speculative dispatch code for sources that don't exist yet.

Mapping: a Deck stack <-> a Parcella TaskList, matched by name (created
if missing, in Deck's own stack order). A Deck card <-> a Task, upserted
by (source="deck", external_card_id) via ExternalTaskLink. Archived Deck
cards are treated exactly like cards that have disappeared entirely (see
_reconcile below) -- never created, and detached if already linked.
"""
import logging
from typing import Dict, Set

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ExternalTaskLink, Task, TaskList
from app.task_board import create_task, move_task, next_list_position, next_position
from app.task_sync import DeckTaskProvider, ExternalCard, ExternalStack, get_deck_client, load_deck_board_id

logger = logging.getLogger(__name__)

SOURCE = "deck"


async def _lists_by_name(db: AsyncSession) -> Dict[str, TaskList]:
    result = await db.execute(select(TaskList))
    return {task_list.name: task_list for task_list in result.scalars().all()}


async def _get_or_create_list(db: AsyncSession, lists_by_name: Dict[str, TaskList], name: str) -> TaskList:
    existing = lists_by_name.get(name)
    if existing is not None:
        return existing
    task_list = TaskList(name=name, position=await next_list_position(db))
    db.add(task_list)
    await db.flush()
    lists_by_name[name] = task_list
    return task_list


async def _upsert_card(
    db: AsyncSession, card: ExternalCard, board_id: str, stack: ExternalStack, target_list: TaskList,
) -> bool:
    """Returns True if this card was created or updated, False if it was
    already up to date and skipped."""
    result = await db.execute(
        select(ExternalTaskLink)
        .where(ExternalTaskLink.source == SOURCE, ExternalTaskLink.external_card_id == card.id)
    )
    link = result.scalar_one_or_none()

    if link is not None and card.updated_at <= link.external_updated_at:
        return False  # Incremental skip: Deck's own timestamp hasn't advanced.

    if link is None:
        task = await create_task(
            db,
            title=card.title, description=card.description, due_date=card.due_date,
            priority=None, tags=[], list_id=target_list.id, assigned_to_ids=[],
        )
        db.add(ExternalTaskLink(
            task_id=task.id, source=SOURCE,
            external_board_id=board_id, external_stack_id=stack.id, external_card_id=card.id,
            external_updated_at=card.updated_at,
        ))
        return True

    task = await db.get(Task, link.task_id)
    if task is None:
        # Shouldn't happen -- Task.external_link cascades on delete --
        # but a sync loop must never crash on a single bad row.
        logger.warning(f"ExternalTaskLink {link.id} points at a missing task; skipping.")
        await db.delete(link)
        return False
    task.title = card.title
    task.description = card.description
    task.due_date = card.due_date
    if task.list_id != target_list.id:
        # move_task() also writes the card's list_id change to
        # ChangeHistory (app/task_board.py), attributed to no user
        # (changed_by_id=None) -- an honest representation, since no
        # human made this specific change.
        await move_task(db, task, target_list.id, await next_position(db, target_list.id))
    link.external_stack_id = stack.id
    link.external_updated_at = card.updated_at
    return True


async def _reconcile(db: AsyncSession, board_id: str, seen_card_ids: Set[str]) -> None:
    """Any link for this board whose card wasn't in this run's fetch
    (deleted or archived in Deck -- both are excluded from
    seen_card_ids, see sync_deck_tasks) is removed. The Task itself is
    left untouched -- this repo historizes over deletes (ADR 0005) -- it
    just stops being tracked as synced, same end state as the manual
    "Adopt into Parcella" action (POST /tasks/{id}/adopt)."""
    result = await db.execute(
        select(ExternalTaskLink)
        .where(ExternalTaskLink.source == SOURCE, ExternalTaskLink.external_board_id == board_id)
    )
    orphaned = [link for link in result.scalars().all() if link.external_card_id not in seen_card_ids]
    for link in orphaned:
        await db.delete(link)
    if orphaned:
        await db.commit()


async def sync_deck_tasks(db: AsyncSession) -> int:
    """No-ops (returns 0) if Deck isn't configured or no board is
    chosen yet. Returns the number of cards created or updated this run
    (a link removed by reconciliation doesn't count -- that's a
    correction, not new activity, same convention as
    app/freescout_sync.py's sync_freescout_conversations)."""
    client = await get_deck_client(db)
    if client is None:
        return 0
    board_id = await load_deck_board_id(db)
    if not board_id:
        await client.aclose()
        return 0

    try:
        stacks = await client.fetch_board(board_id)
    finally:
        await client.aclose()

    lists_by_name = await _lists_by_name(db)
    seen_card_ids: Set[str] = set()
    count = 0

    for stack in sorted(stacks, key=lambda s: s.order):
        target_list = await _get_or_create_list(db, lists_by_name, stack.title)
        for card in stack.cards:
            if card.archived:
                continue  # Never created; detached below if already linked.
            seen_card_ids.add(card.id)
            if await _upsert_card(db, card, board_id, stack, target_list):
                count += 1

    if count:
        await db.commit()

    await _reconcile(db, board_id, seen_card_ids)
    return count
