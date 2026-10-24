# Support: no customer replies from Parcella

**Context:** Since the FreeScout bridge (ADR 0080) and the provider
layer (ADR 0107), a support conversation's detail page in Parcella had
a "Reply to customer" box, and the REST API had a matching
`POST /api/v1/helpdesk/conversations/{id}/reply` (and the deprecated
`/api/v1/freescout/...` twin). The reply went out through the
helpdesk's API as a customer-facing email. In practice that made
Parcella a second, thinner place to answer customers. It had no
signature, no templates, no attachments, no drafts and no collision
detection with an agent answering in the helpdesk at the same time. A
reply could also be sent to automated mails (newsletter
notifications) that nobody should answer. The club decided that
answers are written in the helpdesk only.

**Decision:** Parcella never sends anything to a customer through the
helpdesk.

- The reply box on `/support/{id}` is gone, and so are the web route
  `POST /support/{id}/reply` and both REST endpoints.
- The `reply` capability and every provider's `reply()` method are
  removed from `app/helpdesk/`, so nothing can call them by accident
  again. The detail page keeps its link to the conversation in the
  helpdesk (`conversation_url`), which is where answering happens.
- What stays: reading the transcript, matching member and parcel,
  promoting to a task, and *creating* conversations from the public
  contact form. That is a visitor writing in, not the club answering.

**Consequences:**

- Removing the REST endpoints is a breaking API change, so the next
  release is a MAJOR version.
- A test (`test_no_way_to_reply_to_the_customer_from_parcella`) checks
  that the detail page has no reply form, that the routes are gone and
  that providers have no `reply()`. Re-adding a reply path means
  revisiting this ADR first.
