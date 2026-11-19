# Club settings

The settings page holds your club's master data and the switches that
apply to the whole installation: language, logo, e-mail server, finance
details and more.

!!! info "Who can use this"
    Administrators only. Open **Administration → Settings**.

![Club settings](../assets/screenshots/administration/settings.png)

## How the page works

The page is a column of cards. Each card is folded shut; click its
heading to open it. Opening one card folds the others away.

| Element | What it does |
|---|---|
| **Search settings...** | Type a word, for example "logo" or "IBAN". Cards that contain it open and the word is highlighted; all other cards are hidden. If nothing matches you see **No settings match your search.** |
| **Save settings** | At the top and at the bottom of the page. Saves **every card at once**, whichever one you changed. You see **Settings saved.** |

!!! warning "One save button for everything"
    Changes are only stored when you click **Save settings**. If you
    leave the page first, they are lost.

The cards, from top to bottom:

## Language

The language of the whole installation: menus, buttons, messages, the
sign-in page, and the e-mails and PDFs Parcella produces. Everybody
sees the same language; there is no personal language setting.

Choose between **Deutsch**, **English**, **Polski**, **Čeština**,
**Slovenčina**, **Français** and **Nederlands**. A new installation
starts in English.

Where a text hasn't been translated into the chosen language yet,
Parcella shows the English text instead.

The language doesn't change how numbers, dates and money look -- that
is the **Region & Currency** card.

## Branding

| Field | What it does |
|---|---|
| **Club Logo** | Shows your current logo (or the Parcella icon). Choose a new file -- PNG, JPEG, WebP or SVG, at most 2 MB -- to replace it. The logo appears on the sign-in page, at the top of the sidebar and in the header of generated PDFs. |
| **Remove logo (revert to the default icon)** | Only shown when a logo is uploaded. Tick it and save to go back to the Parcella icon. |

A wrong file type or a too-large file is rejected with a message; the
rest of the page is still saved.

## Region & Currency

| Field | What it does |
|---|---|
| **Region** | How numbers and addresses are written -- thousands separator, decimal comma or point, whether the postal code comes before or after the city. Also decides the time zone for calendar feeds. Choices: Germany, United Kingdom, France, Netherlands, Poland, Czech Republic, Slovakia. Default: Germany. |
| **Currency** | The currency symbol and where it goes ("19,99 €" or "£19.99"). Choices: Euro (€), British Pound (£), Polish Złoty (zł), Czech Koruna (Kč). Default: Euro. |

Both are independent of the language: a Dutch-speaking club can use
Dutch menus with euro amounts, an English-language installation can
use German number formats.

## Feature areas

The switches that turn modules on and off. Described in detail in
[Turning modules on and off](modules.md).

## Navigation order

Decides the order of the entries in everybody's sidebar. Each entry
has a number field: **Dashboard**, **Members**, **Parcels**,
**Support**, **Purchase Requests**, **Work Sessions**, **Water**,
**Electricity**, **Insurance**, **Calendar**, **Announcements**,
**Inventory**, **Task Board**, **Finances**, **Applicants**, **External
contacts**, **Reporting**, **Notes**, **Processes**.

Lower numbers come first. Out of the box the numbers are 100, 200,
300 ... in the order listed above, so you can move an entry between two
others by giving it, say, 150. Empty fields fall back to the default
number; anything that isn't a whole number is ignored.

**Administration** isn't in the list: it is always last.

## Updates

| Field | What it does |
|---|---|
| **Check for updates automatically** | On by default. Parcella then asks GitHub every few hours whether a newer version has been released, and shows a notice on the [System](system.md) page. Nothing about your club is sent. Switch it off if your server must not contact the internet; the System page then shows no update information at all. |

## Applicants

Only relevant when you use the [Applicants](../modules/applicants.md)
module.

| Field | What it does |
|---|---|
| **Delete applications after (months)** | Every application whose status hasn't changed for this many months is **deleted for good**, whatever its status, without telling anyone. Counted from the last status change, or from the application date if the status never changed. Leave empty or enter 0 to keep applications until you delete them by hand. Useful for data protection. |
| **Text of the email to new applicants** | The text used by **Contact applicant** on a new application; it can still be changed before each sending. `{name}` becomes the applicant's name, `{club}` the club's name. Leave empty to use the built-in text, shown in grey. |

## Email log

| Field | What it does |
|---|---|
| **Keep email log entries for (days)** | How long the [E-mail log](email-log.md) keeps its entries. Older ones are deleted automatically because recipient addresses are personal data. Default 90 days, possible 1 to 3650. |

## Club data

| Field | Used for |
|---|---|
| **Club name** | Shown at the top of the sidebar, on the sign-in page and on printed documents. Empty: "Parcella". |
| **Street**, **Postal code**, **City** | The club's address in the footer of generated PDFs (invoices, notices, lists). |
| **Club registration number**, **Register court** | Also printed in PDF footers, as associations registered in Germany must state them. |

## Board members

Which members are currently on the board. Their names are printed in
the footer of generated documents.

| Element | What it does |
|---|---|
| **Board members** / **Show list** | Unfolds the list of all current members, each with a checkbox. **Hide list** folds it away again. |
| **Search…** | Narrows the list to matching names. **No matches** if none fit. |
| **Select all** / **Select none** | Tick or untick every visible member. |

A member who leaves the club automatically drops off the printed list.

## Areas (sqm)

The club's land, split the way German allotment associations usually
report it.

| Field | What it does |
|---|---|
| **Total area (sqm)** | The club's whole site. Enter it yourself. |
| **Area A (parcels, sqm)** | Calculated, can't be edited: the sum of all parcel areas, leased or terminated. Deleted parcels and common areas don't count. Same figure as **Total Area (sqm)** on the [Dashboard](../getting-started/dashboard.md). |
| **Area B (communal, sqm)** | Calculated: total area minus Area A minus Area C. |
| **Area C (municipal, sqm)** | Enter it yourself. |

These figures are used when an [invoice run](../modules/finances/invoice-runs.md)
splits costs by each parcel's share of the communal area.

## Finance settings

Used by the [Finances](../modules/finances/index.md) module.

| Field | What it does |
|---|---|
| **Bank name**, **IBAN**, **BIC**, **Account holder** | Printed in the footer of every invoice, so members know where to pay. |
| **Next invoice number (override)** | Usually empty: numbers simply continue. Enter a number to make the very next invoice run -- in any year -- start there instead. Parcella only checks that the number isn't taken when that run is finalised. The field empties itself once used. |
| **Invoice number format** | How invoice numbers look. `{number}` is required, `{year}` optional; any other text is used as written, e.g. `R-{year}-{number}`. Below the field you see **Currently used:** with an example; **(default, nothing custom saved)** means the default `{year}/{number}` applies. The field suggests a few examples. |

The format only affects invoices created from now on. Numbers already
given out never change. An invalid format isn't saved; you see
**Invalid invoice number format -- it must contain {number} exactly
once (optionally {year} too), and no other placeholders.**

## Email (SMTP)

Every e-mail Parcella sends -- invitations, notifications,
announcements, invoices -- goes out through this mail server. Parcella
doesn't read any mailbox.

| Field | What it does |
|---|---|
| **SMTP server** | The mail server's address, from your e-mail provider. |
| **SMTP port** | Usually 587 (or what your provider says). |
| **SMTP user** | The login for the mail server, often the e-mail address. |
| **SMTP password** | Shown as **Not set yet** or **•••••••• (set -- re-enter to change)**. Leave it empty to keep the stored password; type a new one to replace it. Stored encrypted. |
| **Sender email** | The address e-mails come from. |

!!! tip "Check that it works"
    After saving, invite yourself with a second address or send any
    e-mail, then look at the [E-mail log](email-log.md). **Failed**
    with an error tells you what the mail server didn't like.

If these fields are empty, Parcella uses the mail settings the person
who installed it may have put into the server configuration.

Parcella encrypts the connection to the mail server with STARTTLS, the
method normally used on port 587. There is no switch for this on the
settings page; it can only be changed in the server configuration.
<!-- TODO(verify): whether mail servers that only offer implicit TLS on port 465 work at all. -->

## Related

- [Turning modules on and off](modules.md)
- [Integrations](integrations.md)
- [Setting up a new club](../guides/new-club-setup.md)
