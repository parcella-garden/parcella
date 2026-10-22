# Spam filter and IMAP leftovers removed

**Context:** the spam filter (`app/spam_filter.py`, ADRs 0038, 0066
and 0067) was part of the built-in ticket module. ADR 0080 removed
that module in v3.0.0 and handed support conversations to FreeScout,
which does its own spam handling. Parcella only reads FreeScout's
`spam` status and hides those conversations
(docs/module-freescout-bridge.md).

The removal was incomplete. Several pieces stayed behind:

- an empty "Spam filter (ticket system)" card on Admin -> Settings,
  with help text about heuristics and an external API that no longer
  existed
- the `spam_*` translation keys in all 7 catalogs
- the reference adapter in `integrations/spam-check-adapter/`
- five `ClubSetting` rows (`spam_domain_blocklist`,
  `spam_keyword_blocklist`, `spam_schwellenwert`, `spam_api_url`,
  `spam_api_key`), the last one holding an encrypted third-party key

## Decision

Remove all of it. Migration `0103_drop_spam_settings` deletes the
setting rows. Its downgrade does nothing, because no code reads those
keys and the values can't be rebuilt.

ADRs 0038, 0066 and 0067 stay as they are, as the record of how the
filter was designed. Treat all three as retired.

## What stays

Bot protection on the public forms (work-session signup, contact
form, applicant form) is separate from this and stays: the hidden
`website` honeypot field and optional ALTCHA (`app/form_altcha.py`).
Signups and applications create records directly in Parcella and never
pass through FreeScout, so FreeScout's spam handling doesn't cover
them.

## If spam filtering comes back

Anything that lands in FreeScout should be filtered in FreeScout. If a
Parcella-side public form needs more than honeypot plus ALTCHA, add
that protection to the form itself. Don't bring back a general spam
filter in Parcella.

## Follow-up: IMAP settings

The same incomplete removal left the IMAP side of the ticket inbox
behind. Parcella reads no mailbox at all anymore; it only sends mail
over SMTP. Migration `0104_drop_imap_settings` deletes `imap_host`,
`imap_port`, `imap_ssl`, the old poller's state rows
(`ticket_imap_letzte_uid`, `ticket_imap_letzter_abruf`,
`ticket_imap_letzter_fehler`) and `ticket_attachments_cloud_folder`.
The `imap_*` labels are gone from all 7 catalogs, and the settings card
is now "Email (SMTP)", with help text that describes sending only.
