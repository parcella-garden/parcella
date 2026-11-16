# Module: Processes

Club-defined, step-by-step processes (issue #331, [ADR 0135](./ADR/0135-configurable-process-builder.md)).
A **template** describes a process as ordered **stages**, each with its
own **fields**. A **process** is one run of a template, optionally about a
plot, a member or an applicant.

- Module flag: `modul_processes` (default on: no public endpoint).
- Permission module: `processes`. Read to look, write to start and work
  on processes, delete to abort or delete one. Templates need full access
  (ADMIN/BOARD). Picking or seeing applicants also needs read on
  `applicants`.
- Web: `/processes/` (list), `/processes/new`, `/processes/{id}`,
  `/processes/templates/` (editor). The plot, member and applicant pages
  show a "Processes" card with a start link.
- API: `/api/v1/process-templates` (read), `/api/v1/processes` (list,
  start, read, set a field, advance, back, abort).
- Code: `app/services/processes.py` (all rules), `app/routers/processes.py`,
  `app/routers/api_processes.py`, templates in `app/templates/processes/`.

## Data model

| Table | What |
|---|---|
| `process_templates` | name, description, `subject_kind` (NONE/PARCEL/MEMBER/APPLICANT), `is_active` (archive instead of delete) |
| `process_template_stages` | ordered stages of a template |
| `process_template_fields` | ordered fields of a stage: `label`, `kind`, `required`, `help_text`, `options` (CHOICE) |
| `processes` | one run: `template_id` (SET NULL) + `template_name`, `title`, subject FK, `status` (OPEN/COMPLETED/ABORTED), `current_position`, `abort_reason`, `closed_at` |
| `process_stages` | snapshot of the template's stages, plus `completed_at`/`_by` |
| `process_fields` | snapshot of the field definition **plus** its value: `value_text`, `value_number`, `value_date`, `value_bool`, `value_member_id`/`value_applicant_id`/`value_parcel_id` |
| `process_files` | files of a FILE field: LOCAL or CLOUD, generated `stored_name`, sniffed `content_type` |
| `process_events` | audit trail: CREATED, ADVANCED, REVERTED, COMPLETED, ABORTED, FIELD_CHANGED (old → new), FILE_ADDED, FILE_REMOVED |

Field kinds: TEXT, LONG_TEXT, NUMBER, MONEY, DATE, CHECKBOX, CHOICE, FILE,
MEMBER, APPLICANT, PARCEL.

## Key decisions

- **Snapshot on start.** Editing a template only affects processes
  started afterwards. The template editor says so and shows how many
  processes use the template.
- **One rule for moving on:** all required fields of the current stage
  must be filled. A checkbox counts when ticked, a file field when it has
  at least one file. Back to any earlier stage needs a reason and keeps
  the values. Abort needs a reason. A closed process is read-only.
- **Editable fields:** those of the current and earlier stages of an
  open process. Later stages show their field labels only.
- **Numbers and amounts** accept a comma or a point as the decimal
  separator (`1.234,50` and `1,234.50` both work). They are stored as
  `Numeric(14, 2)`.
- **Examples** (`EXAMPLES` in the service): "Plot handover" and "Member
  onboarding" are created on demand in the user's language from
  `processes.examples.*`. They are not seeded by the migration.
- **Deleting:** a template only while no process was started from it
  (otherwise archive it). A process only with delete permission, meant
  for one started by mistake. Its local files are removed; cloud files
  stay in the cloud.
- **Subjects are SET NULL.** An applicant hard-deleted for GDPR reasons
  (ADR 0091) leaves the process with "(removed)".

## Files

Where an upload goes is decided per upload (`_cloud_folder`), in this
order, and shown under each upload form:

1. **The subject's own folder:** `<plot folder>/<template-slug>_<date>_<id8>/`
   when the cloud storage module is on and the process is about a plot
   with an active cloud folder (parcel page), or about a member with
   exactly **one** current plot that has one. Several current plots are
   ambiguous, so they fall through to 2; applicants have no folder. The
   subfolder is named after the template, not the title, which may name
   a person. Plot folders are usually shared with the tenants in the
   cloud, so they see these files too -- **intended**: official
   documents about a plot are open to its tenants for transparency
   (decided 2026-11-17). A club that wants board-only files leaves the
   plot folder unset or uses the processes folder instead.
2. **Cloud:** `<processes_cloud_folder>/<subject-or-title>_<date>_<id8>/`
   when Admin → Integrations → Nextcloud → "Folder for process files"
   is set.
3. **Local:** otherwise they go to `app/static/uploads/private/processes/<process_id>/`.
  That is the persisted `./data/uploads` volume in production, so they
  are in every backup. `app/main.py` blocks `/static/uploads/private/*`
  after normalizing the path.
- Only PDF, JPEG, PNG and WebP are accepted, checked by magic bytes, up
  to 20 MB. Downloads go through `/processes/{id}/files/{file_id}` with
  `Cache-Control: private, no-store`.
- Removing a file removes a local file, but only unlinks a cloud file.
- Cloud files get a readable, still unique name
  (`20261117-zaun-arger-1a2b3c4d.png`), since people browse these
  folders in the cloud too; local files keep a bare uuid.
- Each file stores its own `cloud_path`, so a later folder change (a
  handover switching the plot's folder, ADR 0102) doesn't break
  downloads of earlier files.

## Template builder (UI)

`app/templates/processes/template_edit.html`: stages on the left (drag to
reorder), the selected stage's fields on the right, a "Preview" tab that
renders the stage through the same `_field_input.html` a running process
uses (inputs disabled), and one side panel per field with only the
settings its type needs (options only for a choice). New fields are
added by typing a label and pressing Enter; a choice field opens the side
panel first, since it can't be saved without options.

- Every change is still an ordinary form post to the template routes.
  The builder sends it with `fetch` and `X-Requested-With: fetch`, which
  makes `_template_action` answer JSON (`{"ok": true, "id": ...}` or
  `{"error": "<translated>"}`) instead of a redirect; then it re-renders
  `#pb-root` from a fresh GET of the editor page, so the HTML comes from
  one place (the Jinja template), never built in JS. Without JavaScript
  the same forms post and redirect back to `?stage=<id>`.
- Drag and drop uses SortableJS from jsDelivr (touch support; the CSP
  already allows that CDN). The order is sent as the full list of ids;
  `reorder_stages`/`reorder_fields` refuse a list that isn't exactly the
  current ids (409 `stale_order`, e.g. a second tab deleted a field) and
  the page re-renders with the real order. Up/down stays available in
  the stage menu and the side panel for keyboard users.
- `/stages/order` is declared before `/stages/{stage_id}`, or "order"
  would be taken for a stage id.
- Moving a field to another stage appends it there; duplicating inserts
  the copy right below the original.

## Known gaps / ideas

- **Stage actions:** e.g. offer a plot to the waiting list (first to
  accept wins), generate a payment reference, change an applicant's
  status. These were in the first, hard-coded handover version and were
  dropped (ADR 0135).
- **Per-stage or per-field permissions** (e.g. only the treasurer
  confirms the deposit).
- Due dates and reminders, notifications.
- Template import/export as a file, to share templates between clubs.
- Repeating field groups (e.g. one row per defect, each with photos).
- The member/applicant/plot pickers are plain selects with no search.
- File upload and download aren't in the REST API yet.
