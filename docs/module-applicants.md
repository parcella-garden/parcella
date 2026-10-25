# Module: Applicants (free garden plots)

People who applied for a free garden plot. Most clubs have a waiting
list of some kind; until now it lived in an inbox or a spreadsheet.
Applications usually come in through a form on the club website (for
kgv-goldene-hoehe.de: the "Freie Gärten" page), and the board keeps
track of who it got in touch with and who got a plot.

Module flags:
- `applicants` -- the board's list, detail page and REST API. On by
  default: by itself it opens nothing to the public.
- `public_applicant_api` -- the public submit endpoints the website form
  posts to. Off by default, like every public write endpoint
  (`public_signup_api`, `public_contact_api`). A club can use the list
  for manual entries only.

Permission module: `applicants` (`app/permissions.py`) -- read to see
the list, write to add/edit applicants and change their status, delete
to remove an applicant for good. ADMIN/BOARD have all three; a group
can grant them to e.g. whoever handles plot allocation.

## Data model

```
applicants   – one row per application: contact data, status, board note, timestamps
```

- `email` -- required, the only required field. First and last name,
  phone and `message` (the applicant's free text) are optional.
- `status` -- `NEW` → `CONTACTED` → `OFFERED` → `ACCEPTED` → `CLOSED`,
  or `REJECTED` ([ADR 0114](./ADR/0114-applicant-workflow-and-retention.md)).
  `ACCEPTED` means the applicant wants the offered plot and the handover
  is still being negotiated; `CLOSED` is set by "Assign a parcel". An
  applicant who turns a plot down goes to `REJECTED` (no further offers)
  or back to `CONTACTED` (stays on the waiting list) -- there's no
  "withdrawn". `NEW` to `ACCEPTED` count as open
  (`APPLICANT_OPEN_STATUSES`).
- `source` -- `WEBSITE` (any public form or connector) or `MANUAL`
  (entered by the board, e.g. after a phone call).
- `board_note` -- internal, never shown to the applicant.
- `consent_at` -- when the applicant ticked the data-protection box,
  shown as "Privacy consent (applicant)". Set for every public
  submission (consent is required there); empty for manual entries. Not
  a board approval (issue #251). The detail page shows this and the
  other dates without a time of day.
- `applied_at` -- decides the waiting-list order. Set to "now" on
  creation, but the board can set or correct it by hand (issue #240),
  both on the "new" form and on the detail page, and through the API --
  needed to enter older applications from a paper waiting list. The
  HTML form only carries a date: re-saving the same day keeps the
  original time of a web application, a different day is stored as
  midnight UTC (the zone every `applied_at` is displayed in). Future
  dates are refused. Logic in `parse_applied_at()`,
  `app/services/applicants.py`.
- `status_changed_at`, `updated_at`, `created_by_id` (manual entries).

Status and application-date changes go to the generic `change_history`
table (`entity_type="Applicant"`) and show up on the detail page -- the
date because it moves someone up or down the queue. Contact data and the
board note aren't tracked -- they're edited freely and would only add
noise.

## Key decisions

**Its own table, not Member.** Most applicants never get a plot, and
their data must not mingle with the member list (member counts, invoices,
work hours, mailings all read `members`). An applicant only becomes a
member once they actually get a plot -- see "Assigning a parcel" below.

**Assigning a parcel** ([ADR 0101](./ADR/0101-hand-terminated-parcel-over-to-applicants.md)).
The "Assign a parcel" button on an open application (`ACCEPTED`
included, issue #252)
(`/applicants/{id}/assign-parcel`, needs write on `applicants` *and*
`members_parcels`) hands a `TERMINATED` parcel over in one step. You
pick the parcel, the handover date (also in the future -- the switch
then happens on that day, ADR 0102), optionally co-applicants and the
new tenants' cloud folder, check
the preview, then confirm. The old tenants become former tenants and
leave the club unless they hold another parcel. The applicants become
members (or an existing member with the same email is reused), tenants
and invoice recipients. The parcel turns `ACTIVE` and the applications
`CLOSED`. Logic: `app/services/parcel_handover.py`; API:
`POST /api/v1/applicants/{id}/assign-parcel`.

**Hard delete, deliberately** ([ADR 0091](./ADR/0091-applicants-hard-delete-gdpr-exception.md)).
The one place in Parcella that removes rows instead of historizing them
(ADR 0005): an applicant's data is held only for the application, so the
board must be able to remove it for good -- on request, or once the
process is over. Needs the `delete` permission; the applicant's
`change_history` rows go with it.

**Automatic deletion after a retention period** ([ADR 0114](./ADR/0114-applicant-workflow-and-retention.md), issue #255).
Admin settings → "Applicants" → "Delete applications after (months)"
(`applicant_retention_months`, blank/0 = never, the default). Every
application whose last status change -- or its application date, if the
status never changed -- is older than that is deleted the same way,
**whatever its status**. No cron job and no notice to anyone: logged-in
page views trigger it, at most once an hour
(`maybe_purge_expired_applicants()`, `app/services/applicants.py`).

**Same form contract as every other public form** ([ADR 0090](./ADR/0090-one-form-contract-wordpress-via-plain-forms.md)).
`POST /api/v1/public/forms/applicant` (website forms, origin allowlist)
and `POST /api/v1/public/applicants` (server-side connectors, API token)
share `_process_applicant` in `app/routers/api_public.py`: honeypot,
ALTCHA (when required), its own rate-limit bucket (10/hour per visitor),
required consent. Fields: `email` (required), `first_name`, `last_name`,
`phone`, `message`, `consent`, `website`, `altcha`. Codes: `ok`,
`consent_missing`, `invalid`, `rate_limited`, `captcha`, `error`.

**No deduplication.** Applying twice creates two rows. The list marks an
address that has applied more than once, and the detail page links the
other applications -- the board decides what to do; silently merging
would lose the second message.

**Dashboard card counts `NEW` only** and links to `?filter=new`, so the
number and the list it opens always match (ADR 0019). On `/applicants/`
the "New" filter comes first and is the default while there are new
applications; without any it's hidden and the page opens on "Open"
(issue #254). The Applicants nav
entry shows the same count as a badge (`app/nav_counts.py`, ADR 0100),
which disappears once every new application has been moved on.

## Search and red flag

- **Search** on `/applicants/` covers name, email, phone, message and the
  board note, so a FreeScout ticket number noted there finds the
  applicant. It combines with the status filter buttons.
- **Red flag** (ADR 0098): if the applicant's name (first + last),
  email or phone (digits only) matches an external contact that carries
  the tag chosen on `/contacts/tags`, the list shows a red badge and the
  detail page a warning linking that contact (the link only for users
  who may read external contacts). `find_red_flags()` in
  `app/services/applicants.py` computes it live on every view; nothing
  is stored on the applicant. There are no flags while the external
  contacts module is off.

## Where the form lives

- **Static website** (kgv-goldene-hoehe.de): `::: parcella applicant` in a
  page's Markdown renders the form (`templates/_form_applicant.html` and
  `build.py` in that repository).
- **WordPress**: the `[parcella_applicant_form]` shortcode of the
  Parcella Connector plugin (`integrations/wordpress/`).
- **Anything else**: a plain HTML form following the contract above.

## Writing to applicants (issues #246/#247, ADR 0112)

With the announcements module on, board/full-access users get a
checkbox per row on `/applicants/` plus "Select all" / "Select none"
(on the rows the current filter and search show). "Write to the
selected applicants" opens `/announcements/new` with the ticked ids; the
message goes out by email only, through the announcements module's paced
sending, once per address (two applications from the same address get
one email). See "Messages to picked applicants" in
[module-announcements.md](./module-announcements.md).

## Known gaps

- Handing over a parcel copies only name, email and phone. Address, IBAN
  and the email-notification consent are filled in on the member page
  afterwards (ADR 0101).
- No email to the board on a new application; the dashboard card and the
  nav entry are the signal.
- No automatic email to the applicant (confirmation, status updates);
  the board can write to picked applicants by hand (see above).
