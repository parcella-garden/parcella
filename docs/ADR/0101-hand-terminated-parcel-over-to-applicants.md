# Handing a terminated parcel over to applicants: one step, from the application

**Context:** until now, giving an applicant a plot was a manual
checklist spread over three modules: create the member by hand, end the
old tenancies on the parcel, assign the new member, switch the invoice
recipient, set the parcel back to active, and set the application to
`ACCEPTED`. kermie asked for one action on the applicant's page that
assigns a **terminated** parcel. With it, the old tenants become former
tenants, and the applicants become the new tenants and invoice
recipients. Several applicants can take a parcel over together (e.g. a
couple). Old tenants also leave the club, unless they still hold
another parcel.

## Decision

`/applicants/{id}/assign-parcel` (HTML) and
`POST /api/v1/applicants/{id}/assign-parcel` (API) both go through
`app/services/parcel_handover.py`:

- `plan_handover()` validates everything and works out what will happen,
  without writing anything. The HTML page shows the result as a preview
  before the actual POST. Checks: the parcel is `TERMINATED`, every
  applicant is still open (`APPLICANT_OPEN_STATUSES`) and has a first and
  last name (`Member` requires both).
- `hand_over_parcel()` carries the plan out in **one transaction**.
  Half a handover (old tenants gone, no new ones) would be worse than
  none.

For a handover date **D** (defaults to today; past and future both work --
see below and ADR 0102):

| Who | What changes |
|---|---|
| Old tenants (still current on D) | `assigned_until = D`, `is_invoice_address = False` |
| …holding no other parcel after D | also `member_until = D − 1` (their last day as member) |
| …still holding another parcel | membership untouched |
| Each applicant | becomes a `Member` (`member_since = D`, email + phone copied from the application), tenant from D, invoice recipient |
| Parcel | `TERMINATED` → `ACTIVE` (via `update_parcel()`, so it's in `change_history`) |
| Applications | `CLOSED` (in `change_history`; `ACCEPTED` until ADR 0114) |

**Why D − 1 for the membership and D for the tenancy:** the two date
fields have different boundary semantics that already exist.
`MemberParcel.is_current` uses a strict `>` (a tenancy is former *on* its
`assigned_until`, ADR 0052), while `Member.is_active` uses `>=`
(`member_until` is the last day *as* a member). D − 1 makes both turn
over on the same day.

**Future handover dates (amended by ADR 0102):** the first version
refused them, because `MemberParcel.is_current` ignored `assigned_from`.
With a future D, old and new tenants would both have counted as current
and both been billed. ADR 0102 made `is_current` respect the start date.
Now the old tenants stay current tenants, members and invoice recipients
until D (their flag is kept, ADR 0058), the new ones are *upcoming*
until then, and from D on only the new ones count. A pending membership
(`member_since = D`) works the same way through `Member.is_active`. The
parcel's cloud folder switches on D too (ADR 0102).

**An applicant who is already an active member** (matched by email
address, ignoring case) is reused instead of duplicated, e.g. a member
applying for a bigger plot. The preview says so and links the member.
If that member already holds *this* parcel, their tenancy simply stays
and any pending notice is withdrawn.

**Only `TERMINATED` parcels.** That's what "cancelled" means in the
request, and it means someone has deliberately ended the old tenancy. A
vacant `ACTIVE` parcel is assigned the usual way on the parcel page.

## Not done (on purpose)

- **No link from the member back to the application.** Applicants can be
  hard-deleted for GDPR reasons (ADR 0091), so a foreign key would only
  dangle. The application's status history and the member's
  `member_since` are the trace.
- **`email_notifications` stays off** for the new member (same default
  as the "new member" form). It's the member's consent to emails, and
  agreeing to the application isn't that consent. Until the board ticks
  it, the member gets no invoices or announcements by email.
- **No address or IBAN** -- the application form doesn't ask for them.
  The board adds them on the member page.
- **The parcel's metering points and insurance** belong to the parcel
  and are left as they are. The cloud folder is not: see ADR 0102.
