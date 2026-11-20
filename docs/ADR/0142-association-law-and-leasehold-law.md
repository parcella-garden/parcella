# 0142: Association law and leasehold law are separate audiences

**Status:** accepted (issue #397, kermie, 2026-11-20)

## Context

An allotment club deals with its people under two different legal
relationships, and they must not be mixed up:

- **Association law (Vereinsrecht):** the **members** of the club. A
  general meeting, club news, an invitation: every member is addressed
  **personally**.
- **Leasehold law (Pachtrecht):** the **leaseholders of a parcel**. The
  annual invoice, a reminder, a legal notice about the plot: addressed to
  the leaseholders of that parcel **together**, who are jointly and
  severally liable (Gesamtschuldner) under the lease.

kermie: respecting this difference is why Parcella exists at all; other
club software treats everyone as one mailing list.

The first version of #397 ("write to the people on these parcels") was
built as a member-list filter. That turned a lease matter into a member
message: wrong wording ("message to N members"), wrong list ("show these
members"), and letters merged across parcels.

## Decision

1. **Two kinds of audience, kept apart in the data model and the UI.**
   Member messages store a member filter (`audience_filter`, ADR 0095,
   0137). Notices to parcels store parcel ids
   (`Announcement.audience_parcel_ids`) -- never a member filter -- and
   say "Notice to the leaseholders of N parcel(s)", linking back to the
   parcel list.
2. **Leasehold rule (parcels, invoices):**
   - **one notice per parcel**, naming it. A couple holding two parcels
     (a "double garden") gets two notices, one per lease -- the board may
     split such a pair again when the leaseholders leave, so each lease
     stays on its own (kermie). Invoices already work this way: one
     invoice per parcel;
   - **email** to every leaseholder who consented (email notifications
     on and an address);
   - **one letter per postal address** for the leaseholders without
     consent -- also when someone they live with got the email; one
     leaseholder's email doesn't cover the household.
   Implemented for invoices in ADR 0141 (#396) and for notices to parcels
   here (#397).
3. **Association rule (members):** email only with consent, otherwise a
   letter; non-consenting members at the same address share one letter.
   This replaces ADR 0095's decision to ignore the email opt-out for
   targeted member messages. It is its own change (separate ticket).

## Consequences

- Each new kind of communication has to say which side it is on. A
  general meeting invitation is association law; a notice about a plot
  is leasehold law.
- The same person can be on both sides (a member who also leases a
  parcel) and is addressed under the rule of the message, not merged
  across the two.
