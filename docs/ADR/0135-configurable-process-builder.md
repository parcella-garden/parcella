# Processes: a configurable process builder instead of a hard-coded plot handover

**Context:** issue #331 asked for a plot handover workflow: a terminated
plot on its way to the next tenant, from inspection through valuation,
listing, choosing the new tenant, contract and deposit to the closing
meeting. A first version built exactly that inside the applicants module:
a hand-written state machine with a status enum, one guard per
transition, candidates offered to the whole waiting list (first to
accept wins), a deposit with generated payment references, and signer
tracking. It worked, but every step, rule and field was our club's. Other
associations hand over plots differently (or call in an external
appraiser, or have no deposit), and they have other processes that look
the same: welcoming a new member, approving a garden shed, collecting a
work-hours exemption. kermie stopped it before it was pushed.

## Decision

- **A toggleable "Processes" module where the club builds its own
  process templates.** A template is an ordered list of stages, and each
  stage has its own field set. The field types are text, long text,
  number, amount of money, date, checkbox, choice from a list, files
  (PDF/photos), and a link to a member, an applicant or a plot. A field
  can be required. A template can be about a plot, a member, an
  applicant, or nothing. The process is then shown on that page.
- **One generic rule replaces the per-transition guards:** a process
  moves forward one stage at a time, and only once every required field
  of the current stage is filled. It can go back to any earlier stage
  with a reason (values are kept), and be aborted with a reason. Every
  change is written to `process_events`.
- **A running process is a snapshot of its template.** Starting one copies
  the stages and fields into `process_stages`/`process_fields`. Editing a
  template (renaming a field, adding a stage, deleting one) never changes
  or breaks a process already running. The alternative, live templates
  with versioning, was rejected as far more machinery for a club-sized
  tool. The cost is that a fix to a template doesn't reach running
  processes, and the editor says so.
- **Field definition and value in one row** (`process_fields`), with one
  typed value column per kind (`value_text`, `value_number`,
  `value_date`, `value_bool`, and FKs to members/applicants/plots). This
  is instead of a classic EAV split into a definition table plus a value
  table, or a JSON blob. Since the snapshot copies the definition
  anyway, the split buys nothing. Typed columns keep dates and amounts
  queryable and FK integrity real (an applicant hard-deleted under ADR
  0091 just nulls the link).
- **Templates are edited with full access only** (ADMIN/BOARD), like
  the task board's lists (ADR 0044). Working on processes uses the
  normal permission matrix on `processes`: read to look, write to start
  and fill in, delete to abort or delete one.
- **The plot handover ships as an example**, next to a member
  onboarding example. "Use" creates an ordinary template in the user's
  language from `processes.examples.*`, which the club then changes
  freely. Nothing is seeded by the migration, so clubs that don't want
  it never see it.
- **Files are private.** They go to the club's cloud folder
  (`processes_cloud_folder`, one subfolder per process) when the cloud
  storage module is on and the folder is set. Otherwise they go to
  `uploads/private/processes/<id>/` on the persisted uploads volume, so
  they survive a redeploy and are in every backup. A middleware answers
  404 for `/static/uploads/private/*`, after normalizing the path:
  collapsing `//` and resolving `./` and `../`, because a literal prefix
  check is sidestepped by `/static/uploads//private/...` (found in the
  security review of the first version). The only way to a file is the
  permission-checked download route. The file type is sniffed from its
  magic bytes (PDF, JPEG, PNG, WebP), the stored name is generated, and
  the download header uses `content_disposition()`.

## Dropped from the first version (possible "stage actions" later)

- Offering a plot to the whole waiting list, first to accept wins, the
  others marked "taken", and reopening them when the winner backs out.
- Generated, never-reused deposit payment references, and the
  treasurer-only deposit confirmation (per-field permissions).
- Signer tracking.
- Any automatic change to an applicant's status.

If clubs need these, the shape would be a small catalogue of built-in
actions a stage can switch on, not a return to one club's hard-coded
workflow.

## Consequences

- A field type can't be changed meaningfully on a running process, only
  in the template.
- The member/applicant/plot pickers are plain `<select>`s, fine for a
  few hundred entries. A large association may want a search box later.
- The REST API covers templates (read-only), listing, reading, starting
  and working on processes. File upload and download are web-only for now.
