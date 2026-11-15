# Inventory module

An asset register for what the club owns -- and what members store
personally on club property -- grouped into freely-configurable
categories, plus a lending system for borrowable items. Built from a
council member's request: "full control over all things we own,"
grouping by type, tracking purchase price/current value/replacement
cost, distinguishing club vs. personal ownership, and letting members
borrow certain items for a small fee.

## Data model

```
inventory_categories  -- freely created by the club (name + description)
inventory_items       -- one row per thing (or group of identical things,
                          via quantity_total)
item_loans            -- one row per borrowing (quantity-aware)
```

**`InventoryCategory`** is deliberately not a fixed enum. The original
request was explicit that groupings ("Playground," "Fences," "Locks &
Keys," "Water Infrastructure," etc.) need to be configurable by the
club itself, not by a code change -- same lookup-table shape as
`ClubRole`. Deleting a category never deletes its items; `category_id`
is just cleared (`ON DELETE SET NULL`).

**`InventoryItem`** covers both club-owned assets and personally-owned
items members store on club property (`owner_type`: `CLUB` or
`MEMBER`, with `owner_member_id` set only for the latter) -- both get
the same financial fields, per explicit product decision: personal
items are still useful to have on record for insurance/liability
purposes.

- `quantity_total` is how many physical units exist as one entry (3
  wheelbarrows tracked as one row with quantity 3, not three separate
  rows) -- see "Key decisions" below for why.
- `current_value` is manually entered/updated, with an optional
  `current_value_updated_at` so staleness is visible -- deliberately
  no automatic depreciation calculation (see "Key decisions").
- `is_borrowable` + `default_loan_fee` opt an item into the lending
  system; most items (an office printer, the water infrastructure)
  simply aren't borrowable and skip this entirely.
- `retired_at` marks an item as no longer owned/in service without
  deleting it -- financial and loan history for a real asset register
  needs to survive disposal. A genuine data-entry mistake can still be
  hard-deleted (which cascades to its loan history); retiring an item
  that was real and is now sold/scrapped/lost keeps its record intact
  and just excludes it from the default list view.

**`ItemLoan`** is one borrowing: `quantity` (how many units this loan
covers), `borrowed_date`, `returned_date` (`NULL` = still out),
`fee_charged` (defaults to the item's `default_loan_fee` if not given
explicitly). Two computed properties on `InventoryItem` --
`quantity_on_loan` (sum of `quantity` across loans with no
`returned_date`) and `available_quantity` (`quantity_total` minus
that) -- are what checkout validation checks against, and what the UI
shows as "3 of 5 available."

## Key decisions

**Quantity-per-item, not one row per physical unit.** The alternative
(a separate `InventoryItem` row for each of 5 identical wheelbarrows)
would make "how many do we have" a count query instead of a field, and
would need N nearly-identical rows to edit if the purchase price or
category changes for the whole batch. A `quantity_total` field plus
quantity-aware loans covers the actual need (partial availability,
"3 of 5 out right now") without that duplication.

**`current_value` is manually maintained, not computed via a
depreciation formula.** A straight-line or declining-balance
depreciation calculator would need a useful-life assumption per item
category, and would produce a number that looks precise but is really
just a guess dressed up as a formula. Manual entry, with a visible
"last checked on" date, is more honest about what it actually is: the
board's current best estimate, updated when someone bothers to check.

**Personally-owned items get the same financial fields as club-owned
ones.** The instinct might be "why would we track a member's private
tent's purchase price" -- but insurance and liability records are the
actual reason: if something stored on club property is damaged, lost,
or involved in an incident, having its value on record already (not
reconstructed after the fact) is the whole point of tracking it here
at all, per explicit product decision.

**A full REST API alongside the web UI, from the start.** Per this
project's established rule (see Architecture Decisions), every new
data-bearing module gets both web UI and API together, not API added
later. `app/routers/api_inventory.py` covers categories, items
(including retire, distinct from delete), and loans (checkout/return,
plus a cross-item "all active loans" endpoint for the board-wide
view).

**Viewing is open to any logged-in member; mutating requires
admin/board.** Same permission split as the member list: knowing what
the club owns is basic transparency, not a privileged view. Creating/
editing/retiring items, managing categories, and checking items in/out
needs `require_admin` (which, per this project's convention, permits
ADMIN and BOARD roles).

## A route-ordering bug found while building this

`app/routers/inventory.py`'s single-segment `GET /{item_id}` is a
catch-all for viewing any item by ID. It was initially registered
*before* `GET /categories/`, `GET /new`, and `GET /loans/active` --
since FastAPI/Starlette matches routes in registration order (not by
specificity), a request to `/inventory/categories/` would have matched
`/{item_id}` first, treated `"categories"` as an item ID, and 404'd
instead of ever reaching the actual categories page. Fixed by
registering every literal-path route (`/new`, `/categories/*`,
`/loans/*`) before the `/{item_id}` catch-all. Caught by three
regression tests (`test_web_categories_page_is_not_shadowed_by_item_detail_route`
and two siblings) that specifically hit those literal paths and assert
they don't 404 -- worth keeping in mind if a future route is added to
this router: it needs to go before `/{item_id}`, not after.

## A lazy-load bug found while building this

The API's `create_item`/`update_item`/`retire_item` originally called
`await db.refresh(item, attribute_names=["loans"])` after each commit,
intending to reload just the relationship needed for the response
schema. But a commit expires *every* attribute on the object, not just
the ones named in `refresh()` -- so a later access of a plain column
(`updated_at`, touched by `onupdate=func.now()`) still triggered an
async-unsafe lazy load, surfacing as a `MissingGreenlet` error from
inside Pydantic's `model_validate()`. This is the exact "lazy-load
crash" risk already documented elsewhere in this project (see the
work-hours module's own notes on the same class of bug). Fixed with
`_reload_item()`: a full re-query with `selectinload(InventoryItem.loans)`
after every commit, rather than a partial `refresh()`.

## Implementation note (ADR 0070)

Category CRUD, owner-type validation, item create/update, and the
loan checkout/return rules now live in `app/services/inventory.py`,
called by both `app/routers/inventory.py` and
`app/routers/api_inventory.py`. The API router also now checks
permissions the same fine-grained, `Group`-based way the HTML side
does (`require_api_permission`), not the coarser role-only check most
other API routers still use. `update_category` (API-only, no HTML
counterpart exists) stays router-local.

## Form input parsing (issue #315)

The web forms parse amounts, dates and quantities themselves:
`_parse_decimal()`, `_parse_date()` and `_parse_quantity()` in
`app/routers/inventory.py`. Until issue #315 they called `float()`,
`date.fromisoformat()` and `int()` bare, so text in the loan fee field
("5 €") raised a `ValueError`, and the user saw an Internal Server
Error. Now they raise a `ServiceError` (`inventory.errors.invalid_amount`,
`invalid_date`, `invalid_quantity`), and amounts accept `5`, `2,50` or
`2.50`. NaN, Infinity and negative values are refused.

- The item form shows the message in its error alert.
- A failed checkout re-renders the item page with the message and keeps
  what was typed, instead of returning a bare JSON error.
- The fee field explains the format and, when the item has a default
  fee, says that an empty field charges that fee.

There's deliberately no `db.rollback()` on a failed checkout:
`checkout_loan()` validates before it changes anything, and a rollback
would expire the item's eagerly loaded relationships right before the
template reads them (`MissingGreenlet`). This is the same lazy-load
trap as described above.

The REST API isn't affected, because Pydantic validates its numbers
(422).
