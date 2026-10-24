# Helpdesk providers: one dropdown, and capabilities instead of assumptions

**Context:** After the built-in ticket system was removed (ADR 0080),
the support module was a bridge to FreeScout only: `app/freescout_client.py`,
a `freescout_conversation_links` table with FreeScout's integer ids,
`members.freescout_customer_id`, FreeScout settings on their own card.
Clubs on another helpdesk couldn't use any of it. After the website
(ADR 0104) and cloud storage (ADR 0106) got their "one dropdown, one
provider" switch, kermie asked for the same here, explicitly including
Zammad and osTicket.

## Decision

1. **Same pattern, third instance.** The shared `ProviderRegistry`
   (`app/provider_registry.py`), admin card macro, save/test routes and
   REST settings endpoints, now for `helpdesk_provider`. Six providers in
   `app/helpdesk/`: FreeScout (moved, same HTTP calls), Zammad, Znuny /
   OTRS, osTicket, Zendesk, Freshdesk.

2. **Capabilities.** The helpdesk APIs differ a lot: osTicket's official
   API can only create tickets; Znuny's web service has no operation for
   editing customer users. Instead of a lowest common denominator, or
   pretending, each provider declares what it can do (`inbox`, `read`,
   `create`, `customer_sync`; `reply` was dropped again by ADR 0111),
   and every caller checks first.
   Missing features are hidden or explained (osTicket: "answer requests
   in osTicket" plus a link), never a broken button.

3. **A neutral data model.** `helpdesk_conversation_links` with
   `provider` + `external_id` (a string -- not every helpdesk uses
   integers), unique together, and one normalized status set (active,
   pending, closed, spam, deleted). Customer ids moved into
   `helpdesk_customer_ids` (member, provider, id), because a member has a
   different customer number in every helpdesk. Rows of an inactive
   helpdesk are filtered out, never deleted, so switching back loses
   nothing.

4. **Nothing breaks for existing users.** Migration 0107 converts the
   data (dev: 377 conversations and 31 customer ids, checked up, down and
   up again byte-identical) and keeps a configured FreeScout active.
   `/freescout/...` redirects to `/support/...`. The REST endpoints
   moved to `/api/v1/helpdesk/...`; `/api/v1/freescout/...` stays,
   marked deprecated, with the old field names served by read-only model
   properties. That keeps the change backward compatible (MINOR). The
   module key `modul_freescout_bridge` and its permission stay, since
   permissions and nav order hang off them; only the label changed.

5. **Znuny ships with its web service.** Znuny's REST interface is off
   until a web service is configured, so `integrations/znuny/` contains
   the import file and a guide. The provider logs in with
   `SessionCreate`, so the password never appears in a URL (GET
   parameters end up in web server logs).

6. **Live-tested where possible.** FreeScout against the club's real
   mailbox (read only -- creating a test conversation there could email a
   real address). Zammad 6.5, osTicket and OTRS 6 (Znuny's base) in
   temporary Docker containers, removed afterwards. That found and fixed
   four real problems: Zammad's `guess:` creating nameless customers, its
   field-syntax search needing Elasticsearch, its bare 500 when a group
   has no sending address, and Znuny's "NotAuthorized" being misreported
   as wrong credentials. Zendesk and Freshdesk are tested against
   simulated answers only; a live check needs trial accounts.

## Rejected

- **Keeping FreeScout-shaped tables and storing other helpdesks' ids in
  them:** integer ids and one customer column can't represent a second
  helpdesk, and switching would have overwritten customer mappings.
- **Webhooks instead of polling:** every helpdesk signs them differently,
  and they need Parcella to be reachable from outside; polling needs
  only outbound access (ADR 0080's reasoning, unchanged).
- **Dropping osTicket because it can't do everything:** the contact form
  is the part many small clubs need most, and the capability model shows
  honestly what's missing. An osTicket plugin can close the gap later.
