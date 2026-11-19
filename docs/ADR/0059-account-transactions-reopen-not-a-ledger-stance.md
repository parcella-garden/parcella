# FinanceAccount becomes a real (light) ledger: AccountTransaction

**Context:** [ADR](../module-finances.md#accounts) (issue #156) deliberately
kept `FinanceAccount` minimal: "not a ledger -- no manual transactions,
no opening balance," purely a reporting tag on `InvoicePayment`. The
account list just summed the payments recorded against each account.

Issue #174 asked for a per-account list of "financial bookings" --
sortable, searchable, CSV-exportable, and importable from a CSV (e.g. a
bank statement). Confirmed directly with the reporter: this means real
transactions that don't correspond to any invoice at all (a refund, a
purchase, a bank fee, interest) should be recordable against an
account, not just a read-only view of existing invoice payments. That
is a genuine, deliberate reopening of issue #156's "not a ledger"
stance, not an oversight.

**Decision: add `AccountTransaction`, a parallel row type to
`InvoicePayment`, both feeding one unified per-account "bookings"
list.**

- New model `AccountTransaction` (`app/models.py`, migration `0070`):
  `account_id` (`ON DELETE CASCADE` -- unlike `InvoicePayment.account_id`'s
  `SET NULL`, a transaction only exists *for* its account, so deleting
  the account correctly deletes it too; **update, issue #353:** that
  made the account's delete button wipe its whole ledger, so the web UI
  now refuses to delete an account that has any booking -- transactions
  or payments -- and points to unticking "Active" instead. The schema
  rule itself is unchanged), `booking_date`, `amount`
  (signed: positive = credit, negative = debit -- matching how a bank
  statement CSV represents it, so there's no separate "type" field to
  keep in sync with the sign), `description`, `source`
  (`"manual"`/`"csv_import"`, purely informational), `recorded_by_id`.
- `InvoicePayment` is unchanged -- still always tied to a specific
  invoice, still the only way a payment against an invoice gets
  recorded. `AccountTransaction` is for everything else.
- The per-account bookings list (`/finances/accounts/{id}/bookings`)
  is a `UNION ALL` of both row shapes, normalized to
  `(id, booking_date, amount, description, source)`, ordered by date
  descending, with search (description/invoice number) and date/amount
  filters applied to the unified result -- because from the club's
  point of view, both are just "money that moved through this
  account," and a list that only showed one half would look broken.
- CSV import only ever creates `AccountTransaction` rows -- it never
  auto-creates `InvoicePayment`s (matching an uploaded row against an
  invoice number to record a real payment is a different, harder
  problem -- reconciliation -- explicitly out of scope here; the
  reporter asked for bookings, not invoice matching).

**Consequence, accepted:** an account's "balance" (sum of everything
booked against it) is now a mix of two tables rather than one, and
`AccountTransaction` has no relationship to any invoice at all -- it is
a genuinely free-form ledger row, same shape as any plain bookkeeping
tool's transaction list. This is intentional: the reporter's actual
need (refunds, bank fees, purchases -- money movements with no invoice
behind them) cannot be expressed as an `InvoicePayment` no matter how
that model is bent, so a second row type was the correct fix rather
than making `InvoicePayment.invoice_id` nullable and overloading its
meaning.
