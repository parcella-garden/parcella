# Task board

A shared to-do board for the board's own business that isn't tied to a
work session: "renew the insurance policy", "call the electrician",
"follow up with the roofer". Tasks are cards in columns that you drag
from left to right as the work moves on.

!!! info "Who can use this"
    - The module switch is **Task board** under **Administration →
      Turning modules on and off**. It is **on** by default.
    - Only the **Board** and **Administrator** roles, and members of a
      group with **Full access to every module**, see **Task Board** in
      the menu. There is no group permission to open it to other users,
      for reading or writing.
    - Optionally, cards can be pulled in from a Nextcloud Deck board
      (module switch **Nextcloud Deck Sync**, off by default). See
      [Cards from Nextcloud Deck](#cards-from-nextcloud-deck).

!!! note "Not the same as work-session tasks"
    The jobs members do during a work session ("cut the hedge") live in
    the [work hours](work-hours.md) module under **Tasks**. The task
    board is for the board's own to-do list.

## The board

![Task board](../assets/screenshots/tasks/board.png)

The board shows all lists (columns) side by side; scroll sideways if
there are more than fit on the screen. New installations start with
three lists, "To Do", "In Progress" and "Done". You can rename, add,
reorder and delete lists as you like.

The **Task Board** menu entry shows a red number when tasks are
overdue. The dashboard has an **Overdue Tasks** card with the same
number; its **Show all** button opens the board with **Overdue only**
already ticked.

### Buttons at the top

| Button | What it does |
|---|---|
| **Add list** | Opens a small window to add a list. Enter a **Name** (up to 100 characters) and click **Add**. The new list goes to the right end of the board. |
| **Manage tags** | Opens [Task tags](#task-tags). |
| **Export report** | Opens [Export activity report](#export-activity-report). |
| **New task** | Opens the [task window](#the-task-window) for a new card. |

### A list (column)

Each column header shows the list's name, a green tick icon if it is a
[done list](#done-lists), and the number of cards in it.

| Action | What it does |
|---|---|
| Drag the header | Moves the whole list to a new position on the board. |
| **⋮** → **Rename** | Opens **Rename list**; change the **Name** and click **Save changes**. |
| **⋮** → **Mark as done list** / **Unmark as done list** | Turns the done-list function on or off for this list. See [Done lists](#done-lists). |
| **⋮** → **Delete** | Opens **Delete list**. Not possible for the last remaining list. |

When you delete a list that still has cards, the window says **This list
still has cards. Choose another list to move them to before deleting
it.** Pick the target in **Move its cards to** and click **Delete
list**. The cards are added at the end of that list, in their current
order -- no card is ever deleted along with a list. An empty list asks
**Delete the list "{name}"? This cannot be undone.**

### A card

Each card shows:

- the **priority** badge (**High**, **Medium** or **Low**), if one is set;
- a cloud icon if the card comes from Nextcloud Deck;
- the **title** -- click it to open the [task window](#the-task-window);
- who it's assigned to, and the **due date**. An overdue due date is
  shown in red;
- **Done {date}** in green for finished cards, which are also shown
  faded and crossed out;
- its **tags** as coloured labels.

An empty list shows **No tasks**.

**Drag a card** to another list, or up and down within a list, to
change its place. The order is saved straight away. If saving fails,
the page reloads to show the real state.

!!! note "When dragging is switched off"
    While a search, a filter or a sort other than **Manual (drag order)**
    is active, cards can't be dragged, because the board then isn't
    showing every card in its real order. Click **Clear filters** and
    set the sort back to **Manual (drag order)**. Moving whole lists
    still works.

### Search, filters and sort

The bar above the board narrows down what you see. It all happens
instantly in your browser and changes nothing on the board itself.

| Field / button | What it does |
|---|---|
| Search box | Searches title, description, tags and comments. |
| **Any priority** | Shows only cards with **High**, **Medium** or **Low** priority. |
| **Any tag** | Shows only cards with this tag. Only tags used on the board are offered. |
| **Any owner** | Shows only cards assigned to this person. Only people with cards are offered. |
| **Any due month** | Shows only cards due in this month (e.g. "July 2026"). Only months that occur are offered. |
| **Overdue only** | Shows only overdue cards: a due date in the past and not done. |
| **Clear filters** | Resets search and filters. |
| Sort (**Manual (drag order)**, **Due date**, **Priority**) | Re-orders the cards within each list for viewing: by due month, or High → Medium → Low with unprioritised cards last. **Manual (drag order)** shows your own order again. The sort is never saved. |

If nothing matches: **No tasks match your search/filters.**

## The task window

![Task window](../assets/screenshots/tasks/task-modal.png)

Clicking **New task** or a card's title opens a window over the board,
headed **New task** or **Edit task**. Each card has its own web address,
so you can bookmark it or send the link to another board member.
Closing the window (X, **Cancel**, Esc or clicking beside it) takes you
back to the board without saving.

| Field / button | What it does |
|---|---|
| **Title** | Required. |
| **Description** | Optional free text. |
| **Due date** | Optional. A card whose due date has passed counts as overdue until it is done. |
| **Priority** | **No priority** (default), **Low**, **Medium** or **High**. Priority doesn't change the order of the cards; it only shows a badge and can be filtered and sorted on. |
| **Tags** | Tick any of the club's [task tags](#task-tags). If none exist yet: **No tags defined yet.** with a link to **Manage tags**. You can't type new tags here. |
| **List** | Which list the card is in. A new card goes into the first list unless you pick another; it is added at the end. |
| **Done** | Marks the card done (with the date and time it was done). Done tasks are never shown as overdue. Moving a card into a done list marks it done automatically. Untick to reopen. |
| **Assigned to** | Tick any number of people. Only active user accounts are listed. |
| **Create** / **Save changes** | Saves the card and returns to the board. |
| **Delete task** | Only on existing cards. Deletes the card with its comments after **Delete this task? This cannot be undone.** |

### Comments

Existing cards have a **Comments** section: a running log of notes for
whoever picks the task up next. Each comment shows its author and time.

- Type into **New comment** and click **Add comment**.
- Every comment has a small red **Delete comment** link under it, which removes that
  comment after **Delete this comment? This cannot be undone.** Any
  board member can delete any comment. Comments can't be edited.


### Change history

Below the comments, **Change history** lists every recorded change,
newest first: **Timestamp**, **Field**, **Old value**, **New value** and
**Changed by**. Recorded are changes to the title, description, due
date, priority, tags, list (shown by list name) and the done mark.
Changes to who the card is assigned to are not recorded. If there are
none yet: **No changes recorded yet.**

## Done lists

A card is only "done" when it is marked done -- never just because it
sits in a column called "Done". To make moving a card into a column
mark it done, flag that column as a done list:

1. Open the **⋮** menu of the list you use for finished tasks.
2. Choose **Mark as done list**. A green tick appears next to its name.

From then on:

- moving a card **into** a done list marks it done (dragging, changing
  **List** in the task window, or creating it there);
- moving it **out** into a normal list reopens it;
- moving between two normal lists changes nothing;
- the **Done** checkbox marks or reopens a card in any list.

Flagging a list marks the cards already in it as done. Unmarking a list
leaves its cards as they are.

While no list is flagged, the board shows a blue notice explaining this.

## Task tags

![Task tags](../assets/screenshots/tasks/tags.png)

**Manage tags** on the board opens **Task tags**: the fixed list of tags
cards can carry. Cards can only carry the tags defined here.
**Back to the board** returns to the board.

| Field / button | What it does |
|---|---|
| **Name** + colour + **Add tag** | Creates a tag. The name is required, up to 100 characters, and must be unique (upper/lower case doesn't count). Colours: **Grey** (default), **Red**, **Orange**, **Yellow**, **Green**, **Teal**, **Blue**, **Purple**. |
| Name and colour of an existing tag + tick button | Renames or recolours the tag. The change shows on every card at once. |
| "{count} task(s)" | How many cards carry the tag. |
| Bin button | Deletes the tag after **Delete the tag "{name}"? It is removed from every task.** The cards stay. |

Possible errors: **A tag needs a name.**, **A tag with this name already
exists.**, **Unknown colour.** With no tags yet: **No tags yet.**

## Export activity report

![Export activity report](../assets/screenshots/tasks/export.png)

**Export report** downloads a Markdown text file about the board's
activity, for example to draft the board minutes or a monthly summary
(also with the help of an AI assistant).

| Field / button | What it does |
|---|---|
| **From** | Start of the period. Defaults to 30 days ago. |
| **To** | End of the period. Defaults to today. |
| **Download** | Downloads the report. |

The report has three parts: the cards created or changed in the period,
the comments written in the period, and a snapshot of every card on the
board right now (done cards with their done date).

!!! warning "What 'changed in the period' means"
    A card counts as touched if it was created or edited in the period.
    The report can't tell exactly when a card was moved to its current
    list. The file says so itself, so whoever reads it doesn't invent a
    timeline.

## Cards from Nextcloud Deck

If your club used to plan in Nextcloud Deck, Parcella can copy one Deck
board onto the task board and keep it up to date. This is a one-way
mirror, meant to help you move over.

Set up by an administrator: switch on **Nextcloud Deck Sync** under
**Turning modules on and off**, then enter the server, user, app password
and **Deck board ID** under **Administration → Integrations → Nextcloud
Deck** (see [Integrations](../administration/integrations.md)). Parcella
then checks Deck every 15 minutes; **Sync now** there does it right away.

What you see on the board:

- Each Deck column becomes a list with the same name (created if needed).
- Synced cards have a cloud icon (**Synced from Nextcloud Deck**).
- In the task window, a grey notice says: **This card is synced from
  Nextcloud Deck -- title, description, due date, and list are managed
  there and update automatically. Priority, tags, assignees, and comments
  are only in Parcella and always editable.** Title, description, due
  date and list can't be changed in Parcella.
- **Adopt into Parcella** cuts the link: from then on the card is an
  ordinary Parcella card, fully editable, and Deck no longer changes it.
- A card deleted or archived in Deck is never deleted in Parcella. It
  simply stops being synced, as if you had adopted it.
- Archived Deck cards are not copied at all.

## Related

- [Dashboard](../getting-started/dashboard.md) -- the **Overdue Tasks**
  card.
- [Work hours](work-hours.md) -- tasks for work sessions.
- [Integrations](../administration/integrations.md) -- the Nextcloud Deck
  connection.
- [Turning modules on and off](../administration/modules.md)
