# Module: Purchase Requests (Two-Person Approval)

A control mechanism for club expenses: a request must be approved by two
different board members before a purchase may be made. Created because
members previously bought things freely and settled up afterwards --
"completely against the rules".

Module flag: `purchase_requests`

## Data model

```
purchase_requests          – the request: title, justification, link, cost, status
purchase_request_approvals – individual approvals (who, when) -- needs 2 per request
```

`purchase_requests.external_contact_id` is an optional supplier from
the external contacts module (docs/module-external-contacts.md, ADR
0096). It isn't part of the approval and stays editable in every status.

## Key decisions

**Who can do what.** Any logged-in user can create a purchase request --
only approving/rejecting is reserved for board/admin (`require_admin` in
`app/auth.py`, which despite its name also covers the BOARD role). This
mirrors real practice: many people submit requests, but a clearly defined
group decides.

**Self-approval excluded.** Neither the requester (`requested_by_id`) nor
the person who entered the request into the system (`created_by_id`,
relevant when created on someone else's behalf) may give either of the
two required approvals themselves. Without this restriction, the two-
person principle would be meaningless -- whoever files the request could
otherwise approve it themselves.

**Rejection needs only one person (veto principle), approval needs two.**
Deliberately asymmetric: approving money should require the consensus of
two people (protection against bad decisions), but any single board member
should be able to stop a request without having to convince a second
person. A veto is a safeguard, not a power tool that should deliberately
be made harder to use.

**Deep-link confirmation for requesters without a login.** When the board
creates a request on someone's behalf (e.g. because that person has no
app access, or only voiced the request verbally/by phone), a confirmation
token is generated (`itsdangerous` serializer, the same pattern as the
invitation tokens in `app/auth.py`) and sent by email. The link leads to a
**public** page (no login required) where the person can confirm the
details. This confirmation is purely informational for the board ("did
this person really mean it this way?") -- it is not a prerequisite for
the board's own approval, just added transparency.

If the requester has their own app access and creates the request
themselves, the confirmation step is skipped entirely -- they already
entered the details into the system themselves.

**Cost field optional, but planned for.** `estimated_cost_eur` is not a
required field (some purchases don't have a known price yet), but it's an
obvious fit for an expense-approval process -- hence built into the data
model from the start instead of retrofitted later.

**Nav badge counts `OPEN` requests** -- the same number as the
dashboard's "Open purchase requests" tile (`app/nav_counts.py`, ADR
0100). It counts every open request, including ones the current user
has already approved and that are waiting for a second approver.

## REST API

Complete from the start (`/api/v1/purchase-requests`), following the same
pattern as the other modules. `approve` and `reject` use
`require_api_full_access` (`app/api_auth.py`) instead of the per-module
`require_api_permission` other write endpoints in this module use --
approval authority here is deliberately narrower than ordinary module
write access, mirroring the HTML side's `require_admin`.

**Implementation note (ADR 0070):** request creation, the four-eyes
approval/rejection rules, and the confirmation email now live in
`app/services/purchase_requests.py`, called by both
`app/routers/purchase_requests.py` and
`app/routers/api_purchase_requests.py`. Two real divergences were found
and fixed:
- The API's `require_vorstand_api` (role-only ADMIN/BOARD) was
  *stricter* than HTML's `require_admin` (Group-aware: ADMIN/BOARD role,
  or a `grants_full_access`/`grants_system_admin` group) -- the
  reverse-direction version of ADR 0071's TREASURER bug. Replaced with
  `require_api_full_access`, the Group-aware API counterpart.
- The API's confirmation email for an external (no-login) requester
  never actually included the confirmation link/button -- it told the
  requester to "log in", which they have no account to do. Both
  surfaces now share the same email content, including the real link.

What's deliberately NOT shared: the "already handled" short-circuits
(status no longer OPEN, this user already approved) -- HTML redirects
silently for both, the API 409s for both, and that difference predates
this change and wasn't identified as a bug, so it wasn't unified. Only
the two rules that must hold regardless of caller (self-approval block,
the 2-distinct-approvals threshold) are shared. The unauthenticated
deep-link confirmation flow (`/purchase-requests/confirm/{token}`) has
no API equivalent and stays entirely HTML-side.
