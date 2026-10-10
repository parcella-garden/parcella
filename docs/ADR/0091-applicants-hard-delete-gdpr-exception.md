# Applicants: hard delete as a deliberate GDPR exception to historization

**Context:** ADR 0005 makes historization the rule: ending something
(a tenancy, a role) sets an end date or a status, rows are never deleted.
That keeps club history traceable. The new applicants module
(docs/module-applicants.md) stores people who applied for a free garden
plot -- non-members, most of whom never get one. Their data is collected
for one purpose, the application, with their consent; under the GDPR it
has to go once that purpose is over or when they ask for it. A status
like `WITHDRAWN` doesn't remove anything.

**Decision:** Applicants can be hard-deleted.

- `DELETE /api/v1/applicants/{id}` and the "Delete" button on the detail
  page remove the row, and the applicant's rows in `change_history` with
  it (they'd point at nothing).
- It needs the `delete` level of the `applicants` permission module --
  ADMIN/BOARD, or a group that grants it explicitly. Read and write
  don't include it.
- Ending an application without deleting it is still the normal path:
  set the status (`ACCEPTED`, `WITHDRAWN`, `REJECTED`). Deleting is for
  when the data itself has to go.
- No automatic deletion after a retention period for now (kermie's
  call); the board deletes by hand.

**Consequences:** The applicants table holds no history beyond what's
still in it -- there's no record that a deleted applicant ever applied.
That's the point. Anything that must outlive the application (a new
member, a lease) lives in the tables that historize. Don't copy this
exception to other modules without the same reason: data about
non-members, held only for one purpose.
