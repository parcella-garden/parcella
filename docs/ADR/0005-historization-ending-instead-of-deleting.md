# Historization: ending instead of deleting

A recurring pattern throughout the project: tenant assignments, water
meters, club-role memberships are not deleted when they "end", but ended
via an "until" date (or an `is_active` flag + removal date). This keeps
the history searchable ("who was the tenant of G042 in 2019?") without
needing a separate archive table.


**Exception:** applicants (people applying for a free plot) can be hard-deleted -- personal data of non-members held for one purpose only, see [ADR 0091](./0091-applicants-hard-delete-gdpr-exception.md).
