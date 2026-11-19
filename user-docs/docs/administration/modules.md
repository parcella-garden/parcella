# Turning modules on and off

Not every club uses every part of Parcella. A club without its own
water supply doesn't need meter readings; a club that doesn't require
work hours doesn't need work sessions. You decide which modules your
club uses.

!!! info "Who can use this"
    Administrators only. Open **Administration → Settings** and unfold
    the card **Feature areas**.

Each module has a switch, its name and a short description. Flip the
switches you want to change and click **Save settings**.

## What happens when you switch a module off

- It **disappears from the sidebar and the dashboard** for everybody,
  administrators included. (Exception: the *Birthdays this week* tile
  stays on the dashboard even with Calendar switched off.)
- Its pages can't be opened any more, not even from a bookmark.
- **Nothing is deleted.** All its data stays in the database and is
  back, unchanged, as soon as you switch the module on again.
- Group permissions for the module stay as they are, so the same people
  have access again after switching it back on.

Switching a module on makes it visible to everybody with full access
straight away. Other people only see it in the sidebar once a group grants them
**Read** for it -- see [Groups](groups.md).

## The switches

They appear on the card in this order.

| Switch | What it does | On by default |
|---|---|---|
| **Work-hours management** | Work sessions, sponsorships, club roles and the annual work-hours report. See [Work hours](../modules/work-hours.md). | Yes |
| **Water management** | Water meters, readings and consumption reports. See [Water and electricity](../modules/metering.md). | Yes |
| **Electricity management** | Electricity meters, readings and consumption reports. | Yes |
| **Insurance management** | Property and accident insurance per parcel, with annual report. See [Insurance](../modules/insurance.md). | Yes |
| **Support (helpdesk)** | Links your helpdesk's conversations to members and the task board. Choose the helpdesk under [Integrations](integrations.md#support-helpdesk) first. See [Support](../modules/support.md). | No |
| **Purchase requests** | Club expenses with two-person approval. See [Purchase requests](../modules/purchase-requests.md). | Yes |
| **Calendar** | Community calendar, birthdays, board presence and absence, each with a calendar feed. See [Calendar](../modules/calendar.md). | Yes |
| **Inventory** | Everything the club owns, with categories and lending. See [Inventory](../modules/inventory.md). | Yes |
| **Task board** | A To Do / In Progress / Done board for club business. Full-access users only (board, administrators and full-access groups). See [Task board](../modules/tasks.md). | Yes |
| **Applicants** | People who applied for a free plot. See [Applicants](../modules/applicants.md). | Yes |
| **External contacts** | Suppliers, craftsmen, authorities. See [External contacts](../modules/external-contacts.md). | Yes |
| **Reporting** | Club figures over time as charts, read-only. See [Reporting](../modules/reporting.md). | Yes |
| **Notes** | Notes with categories and tags, optionally stored as files in the cloud. See [Notes](../modules/notes.md). | Yes |
| **Processes** | Your own step-by-step processes. See [Processes](../modules/processes.md). | Yes |
| **MCP connector for AI clients** | Lets an AI assistant (Claude, ChatGPT, ...) search, read and write **only those notes you have released for AI**, nothing else. Needs an [API token](api-tokens.md) of the kind **MCP connector only**. | No |
| **Public signup API** | Lets the club website's form sign gardeners up for work sessions without a login. See [Integrations](integrations.md#public-signup-api) and [For gardeners](../gardeners/index.md). | No |
| **Public contact-form API** | Lets the club website's contact form create a new request in your helpdesk instead of sending an e-mail. | No |
| **Public applicant-form API** | Lets the club website's plot application form create applicants directly. The **Applicants** module can be used without it, for applications you enter by hand. | No |
| **Announcements** | Write club news once and prepare it for the website, member e-mail and a printable notice. See [Announcements](../modules/announcements.md). | No |
| **Cloud storage** | A cloud folder per parcel for lease agreements and paperwork; also needed for incoming invoice attachments, contact documents, note files and cloud backups. Choose the storage under [Integrations](integrations.md#cloud-storage) first. | No |
| **Finances** | Annual invoices per parcel, payments and bookkeeping. Fill in the [finance settings](settings.md#finance-settings) first. See [Finances](../modules/finances/index.md). | No |
| **Nextcloud Deck Sync** | Copies the cards of one Nextcloud Deck board onto the task board, kept up to date automatically. Set up the connection under [Integrations](integrations.md#nextcloud-deck) first. | No |

**Members** and **Parcels** have no switch: they are the core of
Parcella and always on.

## Why some switches start off

The switches that are off on a new installation do one of these:

- **They open a door to the public internet.** The three *Public ...
  API* switches let anybody who visits your website send data into
  Parcella. Turn one on only when your website really has the matching
  form, and only the one you need.
- **They store passwords for other services**, or let Parcella act in
  them: cloud storage, helpdesk, Nextcloud Deck, the website connection
  of announcements.
- **They handle money or reach every member at once:** finances and
  announcements.
- **They hand data to an outside company:** the MCP connector gives an
  AI service access to the notes you release.

Nothing breaks if you leave them off. Turn them on deliberately, once
you know you need them.

## Related

- [Modules](../modules/index.md) -- what each module does
- [Groups](groups.md) -- who may use a switched-on module
- [Integrations](integrations.md) -- connections several modules need
