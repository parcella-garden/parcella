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
- `status` -- `NEW` → `CONTACTED` → `OFFERED` → `ACCEPTED`, or
  `WITHDRAWN` / `REJECTED`. `NEW`/`CONTACTED`/`OFFERED` count as open
  (`APPLICANT_OPEN_STATUSES`, the list page's default filter).
- `source` -- `WEBSITE` (any public form or connector) or `MANUAL`
  (entered by the board, e.g. after a phone call).
- `board_note` -- internal, never shown to the applicant.
- `consent_at` -- when the applicant ticked the data-protection box.
  Set for every public submission (consent is required there); empty
  for manual entries.
- `applied_at`, `status_changed_at`, `updated_at`, `created_by_id`
  (manual entries).

Status changes go to the generic `change_history` table
(`entity_type="Applicant"`) and show up on the detail page. Contact data
and the board note aren't tracked -- they're edited freely and would only
add noise.

## Key decisions

**Its own table, not Member.** Most applicants never get a plot, and
their data must not mingle with the member list (member counts, invoices,
work hours, mailings all read `members`). When someone does get a plot,
the board creates the member the usual way and sets the application to
`ACCEPTED`.

**Hard delete, deliberately** ([ADR 0091](./ADR/0091-applicants-hard-delete-gdpr-exception.md)).
The one place in Parcella that removes rows instead of historizing them
(ADR 0005): an applicant's data is held only for the application, so the
board must be able to remove it for good -- on request, or once the
process is over. Needs the `delete` permission; the applicant's
`change_history` rows go with it.

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
number and the list it opens always match (ADR 0019).

## Where the form lives

- **Static website** (kgv-goldene-hoehe.de): `::: parcella applicant` in a
  page's Markdown renders the form (`templates/_form_applicant.html` and
  `build.py` in that repository).
- **WordPress**: the `[parcella_applicant_form]` shortcode of the
  Parcella Connector plugin (`integrations/wordpress/`).
- **Anything else**: a plain HTML form following the contract above.

## Known gaps

- No "create member from applicant" button -- the board creates the
  member by hand.
- No email to the board on a new application; the dashboard card and the
  nav entry are the signal.
- No email to the applicant either (confirmation, status updates).
- No automatic deletion of closed applications after some time -- delete
  them by hand.
