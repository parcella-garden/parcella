# Task board: modal editing with a real, unique URL per card

**Context:** kermie wanted card create/edit presented as a modal popup
over the board instead of navigating to a separate page, but still
wanted every card reachable at its own unique, bookmarkable, refreshable
URL. Before this, `/tasks/new` and `/tasks/{id}/edit` rendered a
standalone page (`app/templates/tasks/form.html`) -- a deliberate
choice, for consistency with Members/Parcels/Work Hours, but never
backed by its own ADR (just prose in `docs/module-tasks.md`).

**Decision:** `/tasks/new` and `/tasks/{id}/edit` now render the *board*
itself (`app/routers/tasks.py::_render_board()`, shared by `board()`,
`task_new_page()`, and `task_edit_page()`) with a `#taskModal` already
open on top of it, instead of a separate page. `form.html` is deleted.

This is **reload-based**, not a client-side-routed modal: clicking a
card is a normal browser navigation to `/tasks/{id}/edit`. The route is
real (backed by `_get_task_or_404`'s 404, admin-gated like every other
route in the module), so the URL is genuinely unique, bookmarkable, and
survives a refresh -- there's no client-side state the URL is faking.
Closing the modal (X, backdrop click, Esc, or the Cancel button's
`data-bs-dismiss="modal"`) all funnel through Bootstrap's single
`hidden.bs.modal` event, whose one listener sends the browser back to
`/tasks/` -- no per-control navigation logic needed.

**Alternative considered and rejected (for now): a true AJAX/pushState
modal.** Clicking a card could instead `fetch()` the edit route in the
background, swap the modal's content in without a page reload, and use
`history.pushState`/a `popstate` handler to keep the URL in sync. This
would feel smoother (no reload per card), but this codebase has **no
existing client-side routing anywhere** -- introducing one is a real new
architectural surface (failed-fetch handling, back/forward behavior, a
no-JS fallback) for a kanban board a club's board members open a few
times a week, not a high-traffic app where the reload cost matters.
Reload-based delivers both of kermie's actual asks (modal presentation,
real unique URL) with a much smaller, lower-risk change, reusing the
same server-renders-a-Bootstrap-modal approach already used for the
Add/Rename/Delete-list modals on this same page. Revisit if the board
UI grows enough interactions that a full reload per card open becomes
genuinely annoying.

**Consequence:** `board()`'s query (lists + tasks + assignees + comments)
now also runs for `/tasks/new`/`/tasks/{id}/edit`, and `active_users`/
`priorities` are fetched additionally whenever a modal is being opened.
Slightly more work per "open a card" request than the old standalone
page did, but negligible at this app's scale, and it means the board
and the modal's dropdowns (list, assignees) can never disagree about
what's on the board -- they're the same query.
