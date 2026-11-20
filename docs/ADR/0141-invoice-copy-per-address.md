# 0141: One invoice per parcel, one copy per address

**Status:** accepted (issue #396, 2026-11-20)

## Context

A parcel's invoice had exactly one recipient. The invoice-address tenants
were grouped by postal address, and only the **largest** group was named
on the invoice (`_group_recipient`). Email went to the **first** reachable
invoice-address tenant only, and an invoice with any email recipient was
never printed. A co-tenant at another address, without email, got neither
an email nor a letter, even though every tenant of a parcel is equally
liable (see `household_grouping` in `app/insurance_utils.py`).

## Decision

1. **Still one invoice per parcel**: one number, one amount, one debt.
   Splitting the amount across addresses was not wanted (kermie, #396).
2. **One copy per address.** `Invoice.recipient_copies` snapshots
   `[{"names", "address", "member_ids"}]` at finalization: tenants grouped
   by normalized address, people sorted by name, largest group first. A
   tenant without any address gets a copy of their own. The copies are
   identical apart from the address window -- no "copy" marking.
3. **Delivery per person, letters per address.** Everyone who gets
   email (consent plus an address on file) receives their address's
   copy by email. The people at an address without email get **one
   printed letter** naming just them -- also when someone they live
   with was emailed: one member's email doesn't cover the household
   (kermie, #396). Reminders follow the same rule and record "both"
   when some went by email and others need printing.
4. **The people on a copy are the snapshot**, not the parcel's tenants at
   send time: they are who the invoice is addressed to. Only their email
   addresses and consent are read live.
5. **Old invoices keep working**: NULL `recipient_copies` means one copy
   from `recipient_names`/`recipient_address`, with the recipients resolved
   live as before (now all reachable ones, not only the first).

## Consequences

- `recipient_names` lists everyone on the invoice, so the lists, the
  recipient search and payment matching see every tenant.
- The invoice download and the cloud upload hold all copies in one PDF.
- Messages to picked parcels (#397) reuse the same address grouping for
  letters.
