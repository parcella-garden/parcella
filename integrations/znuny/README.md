# Znuny / OTRS web service for Parcella

Parcella talks to Znuny (and OTRS 6) through Znuny's GenericInterface.
That interface is off until a web service is set up, which takes one
import:

1. In Znuny: **Admin → Web Services → Add Web Service → Import web
   service**, choose `ParcellaTicketConnector.yml` from this folder, and
   name it `ParcellaTicketConnector`.
2. Create (or pick) an **agent** for Parcella with read and write rights
   on the queue that new contact-form requests should land in.
3. In Parcella: **Admin → Integrations → Support / helpdesk**, choose
   **Znuny / OTRS** and enter:
   - Web service address:
     `https://<your Znuny>/otrs/nph-genericinterface.pl/Webservice/ParcellaTicketConnector`
     (Znuny 7: `/znuny/` instead of `/otrs/`)
   - the agent's login name and password
   - the queue for new requests (default `Raw`)
   - optionally the agent interface address
     (`https://<your Znuny>/otrs/index.pl`), so Parcella can link to
     tickets
4. **Test connection**, then save.

What Parcella does with it: logs in with `SessionCreate` (the password is
only ever sent once, in a request body), lists recently changed tickets
(`TicketSearch` + `TicketGet`), shows their customer-visible articles,
sends replies as email articles (`TicketUpdate`), and creates tickets
from the website contact form (`TicketCreate`). Znuny has no web-service
operation for editing customer users, so Parcella can't rename customers
there.

Note: Znuny checks every new customer address (syntax, its built-in
blocklist such as `example.*`, and by default the domain's mail server).
A contact-form request from an address Znuny refuses is reported back to
the visitor as "currently unavailable", and Parcella logs Znuny's reason.

This file is licensed GPL-2.0-or-later, like the other CMS and helpdesk
integrations in `integrations/`.
