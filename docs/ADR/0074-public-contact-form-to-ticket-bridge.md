# Public contact form → ticket bridge

**Context:** [ADR 0030](./0030-wordpress-connector-plugin-consolidated-into-one-plugin.md)
flagged "a contact-form-to-tickets bridge" as planned work for
`parcella-connector`, alongside signup (done) and calendar display
(done, [ADR 0073](./0073-community-calendar-json-endpoint-for-widget-rendering.md)).
The association's own `/kontakt` page was sending a plain email that
then had to round-trip through the ticket mailbox's IMAP polling to
become a ticket -- confirmed live: an existing ticket titled
"Kontaktanfrage von Website" matched no Parcella translation key,
i.e. it was a literal string from whatever WordPress contact-form
plugin generated the email, not anything Parcella produced. kermie
wanted this replaced with a direct API call, same fields (name, email,
message, data-protection consent), skipping the email round-trip.

**Decision: a second, independent public-write endpoint and module
flag, not folded into `public_signup_api`.**
`POST /api/v1/public/contact` (`app/routers/api_public.py`) lives in
the same router as the signup endpoints (same shared API token, one
credential per the plugin's whole design) but is gated by its own
`public_contact_api` module flag, defaulting `False` per the same
reasoning as every other flag that opens a public write endpoint (ADR
0024): a club should be able to enable one bridge without the other --
wanting public work-session signup says nothing about whether a club
also wants a public contact form creating tickets, or vice versa.

**Consent is a submission-time gate, not stored data.** `consent: bool`
must be `true` or the submission is rejected (`accepted: false`, with a
`reason`) -- enforced server-side, not just via the WordPress form's
`required` checkbox, since a bridge that only checks consent
client-side isn't actually enforcing anything. This uses the same
"HTTP 200 with a rejection flag" convention the signup endpoint already
established for per-session `accepted`/`reason` -- missing consent is
an expected, normal outcome (a visitor hasn't ticked the box yet), not
a server error deserving a 4xx/5xx status. No new DB column tracks that
consent was given -- it isn't something the board needs to query later;
the created ticket's own message body notes it, for anyone reviewing
the ticket by hand.

**Runs through the same spam check as incoming emails.**
`check_for_spam()` (`app/spam_filter.py`) -- the function
`app/ticket_mailer.py` already applies to every incoming ticket email --
now also runs here, setting `spam_suspected`/`spam_score`/
`spam_reasoning` on the created ticket. This endpoint is exactly as
public-facing as the ticket inbox itself (anyone can submit, same as
anyone can email the inbox), so it gets the same treatment rather than
being treated as a trusted internal path. Reuses `create_ticket()`
(`app/services/tickets.py`, already shared between the HTML and
JWT-authenticated API surfaces per ADR 0070) for the actual
ticket/message creation, rather than duplicating that logic a third
time (`ticket_mailer.py`'s inline construction is the second, already
existing, copy -- not touched by this change).

**WordPress side: `contact.php`, deliberately self-contained CSS.**
`[parcella_contact_form]` (`includes/modules/contact.php`) uses its own
`.parcella-contact-*` class names rather than reusing `signup.php`'s
`.parcella-signup-*` ones, even though the two forms look visually
identical (same green submit button, same message/honeypot styling).
Sharing classes would mean the contact form's styling silently
disappears on any page that doesn't also render `[parcella_work_signup]`
-- since `/kontakt` only has the contact form, this isn't a hypothetical
edge case. Each shortcode module now ships its own complete inline
`<style>` block, independent of which other modules happen to render on
the same page.
