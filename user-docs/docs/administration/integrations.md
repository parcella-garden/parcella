# Integrations

Integrations connect Parcella to the other systems your club uses: the
club website, a cloud storage, a helpdesk, Nextcloud Deck, and calendar
apps.

!!! info "Who can use this"
    Administrators only. Open **Administration → Integrations**.

![Integrations](../assets/screenshots/administration/integrations.png)

The page is a column of cards, each folded shut; click a heading to
open it. Every card saves on its own with its own button.

Most integrations also need a module switched on under
[Turning modules on and off](modules.md). The cards tell you when that
is missing.

!!! note "The e-mail server is elsewhere"
    The outgoing mail server (SMTP) is set under
    [Club settings](settings.md#email-smtp), not here.

## Private calendar feeds

The calendar module offers subscription links (calendar feeds) for the
birthday list and for board presence and absence, so board members can
see them in their phone's calendar app. These links contain one shared
secret and never expire.

| Button | What it does |
|---|---|
| **Regenerate** | After confirming, creates a new secret. **Every existing subscription of these feeds stops working**; subscribers must copy the new link from the calendar pages. You see **Calendar feed token regenerated.** |

Do this when a link may have got into the wrong hands, or when someone
who had it leaves the board. See [Calendar](../modules/calendar.md).

## Public Signup API

This card lets your club website talk to Parcella: gardeners sign up
for work sessions, send a contact message or apply for a plot through
forms on the website, without a Parcella login.

If the **Public signup API** module is off, a notice at the top of the
page says so, with a link **Enable it in Settings**. A similar notice
appears inside the card while the **Public contact-form API** is off.
The plot application form additionally needs the **Public
applicant-form API** switch.

There are two ways a website can send its forms, and you can use both.

### With the API token (website plugin on the server)

For a website with a server-side plugin -- a "connector" -- that sends
the form data to Parcella itself.

| Element | What it does |
|---|---|
| **API token** | The secret the plugin needs. Click into the field to select it, then copy it into the plugin's settings. |
| **Regenerate** | After confirming, creates a new token. **Every plugin still using the old one stops working at once**; enter the new one everywhere. You see *A new API token has been generated ...* |
| **Endpoints** | A table of the web addresses the plugins use, each with **Method**, **URL** and **Authentication** (**None (public read)**, the API token, or **Allowed website origins**). Your website's technical contact needs this; you don't. |

The card ends with a note that a ready-made WordPress plugin is part of
the Parcella project.

### Website forms (plain HTML, WordPress plugin)

For websites whose forms send straight from the visitor's browser to
Parcella: plain HTML pages on any website system, and the WordPress
plugin from version 3.0. No token is involved, so Parcella only
accepts forms coming from the websites you list here. While the list
is empty, these forms are closed.

| Field / button | What it does |
|---|---|
| **Allowed website origins** | One web address per line, just the scheme and host, e.g. `https://example.org`. List every address your club website can be reached at, including the WordPress site's own address. Entries that aren't web addresses are dropped and listed in a warning. |
| **Require ALTCHA (proof of work against spam bots)** | The visitor's browser has to solve a small puzzle before a form is accepted -- no cookies, no outside company, nothing for the visitor to click. This applies to **every** way of sending, including plugins using the API token. Only tick this once all your website's forms include the ALTCHA widget, or every submission is rejected. |
| **Save origins** | Saves both. You see **Allowed website origins saved.** |

What gardeners see and receive is described in
[For gardeners](../gardeners/index.md).

## Website (drafts from announcements)

Lets the [Announcements](../modules/announcements.md) module create a
draft post on your club website with one click. Parcella only ever
creates **drafts**; publishing stays a decision you make in your
website system.

| Field / button | What it does |
|---|---|
| **Website type** | **None (no website drafts)**, **WordPress**, **Markdown folder (cloud storage)** or **Parcella plugin (TYPO3, Contao, Drupal, Joomla, ...)**. Choosing one shows its fields. Only one type is active at a time; switching keeps the other type's settings for later. |
| **Save** | Saves the type and its fields. You see **Website settings saved**, or an error explaining what is missing. |
| **Test connection** | Tries the connection with what is in the form right now, without saving. Shows **Connection successful** or the error. |

Fields marked * are required. Password fields show whether something
is stored; leave them empty to keep it.

**WordPress**

| Field | What to enter |
|---|---|
| **WordPress site URL** * | Your website's address. |
| **WordPress username** * | The WordPress user the drafts are created as. |
| **Application Password** * | Not the normal WordPress password: create an application password in WordPress under *Users → Profile → Application Passwords*. |

**Markdown folder (cloud storage)** -- for websites built from text
files (Hugo, Jekyll, Eleventy, Astro and similar). Each draft becomes a
file marked as draft in a folder on your [cloud storage](#cloud-storage);
removing the draft line publishes it.

| Field | What to enter |
|---|---|
| **Posts folder** * | Folder on the cloud storage for the posts, e.g. `website/content/posts`. It must exist already. |
| **Images folder** | Where images go, in subfolders by year and month. Empty: posts without images. |
| **Web path of the images folder** | How the website addresses the images folder, e.g. `/media`. |
| **Website address** | Used for the QR code on the printed notice once a post is published. |
| **File name pattern** | `{date}` becomes YYYYMMDD, `{slug}` the title without umlauts or spaces. |
| **Post address pattern** | The post's web address, written into the file. Leave empty if your website works it out itself. |
| **Author** | Written into each post. |
| **Categories** | Comma-separated, as your website names them. |

**Parcella plugin** -- for TYPO3, Contao, Drupal, Joomla and other
systems with the Parcella plugin installed. The plugin's own settings
show both values.

| Field | What to enter |
|---|---|
| **Plugin address** * | E.g. `https://example.org/parcella/v1`. |
| **Shared secret** * | Generated by the plugin. |

## Cloud storage

The heading reads **Cloud storage (parcel documents, invoices, backups)**.
It decides where Parcella keeps files: a folder per parcel (leases,
paperwork), incoming invoices, contact documents, notes, process files,
backups and the Markdown website. Who else can see a folder is managed
in the storage itself, not in Parcella.

| Field / button | What it does |
|---|---|
| **Storage type** | **None (no cloud storage)**, **Nextcloud**, **WebDAV (ownCloud, Seafile, HiDrive, Storage Box, ...)** or **S3-compatible (AWS, Hetzner, MinIO, Wasabi, ...)**. Only one is active at a time. Folder paths entered elsewhere in Parcella are relative to the chosen storage. |
| **Save**, **Test connection** | As on the website card. |

| Storage | Fields |
|---|---|
| **Nextcloud** | **Nextcloud URL** *, **Nextcloud username** *, **App password** * -- create an app password in Nextcloud under *Settings → Security → Devices & sessions*; don't use the normal password. |
| **WebDAV** | **WebDAV address** * (the full address of the folder Parcella should work in, as your provider documents it), **Username** *, **Password** *. |
| **S3-compatible** | **Endpoint** *, **Region** * (leave `us-east-1` if your provider has no regions), **Bucket** *, **Access key ID** *, **Secret access key** *, **Path inside the bucket** (optional sub-folder for all of Parcella's files). |

The storage is only used once the **Cloud storage** module is switched
on. Then the card also shows the folders below. Each has a path field
(relative to the storage) and a **Save** button; leave a path empty to
switch that use off.

| Folder | Used for |
|---|---|
| **Incoming invoices folder** | Attachments of [incoming invoices](../modules/finances/incoming-invoices.md) go into this one shared folder. |
| **Folder for external contacts' documents** | A base folder with one sub-folder per [external contact](../modules/external-contacts.md), created by you in the storage. Each contact then picks its sub-folder. Empty: the documents section is hidden. |
| **Folder for printed announcements** | Every print PDF of an [announcement](../modules/announcements.md) is also saved here. **Browse** lets you click through the storage and **use** a folder. Empty: download only. |
| **Notes folder** | [Notes](../modules/notes.md) are kept here as text files, and changes made to those files in the cloud show up in Parcella. Sub-folders become note categories. Empty: notes live only in Parcella. |
| **Folder for process files** | Files uploaded to a [process](../modules/processes.md), one sub-folder per process. Empty: kept inside Parcella. Files already uploaded stay where they are. |

The folder for automatic backups is set on the
[Cloud backups](backup.md#cloud-backups) page.

## Support / helpdesk

Connects the helpdesk your club answers requests in. Parcella then
links its conversations to members, parcels and the task board (see
[Support](../modules/support.md)), and the website contact form creates
new requests there.

| Field / button | What it does |
|---|---|
| **Helpdesk** | **None (no helpdesk)**, **FreeScout**, **Zammad**, **Znuny / OTRS**, **osTicket**, **Zendesk** or **Freshdesk**. Only one is active at a time; if you switch back later, its conversations come back too. Each choice shows a short note on what works with it. |
| **Save**, **Test connection** | As on the website card. |

| Helpdesk | Fields | Notes |
|---|---|---|
| **FreeScout** | **FreeScout address** *, **API key** *, **Mailbox ID** (default 1) | Everything works. Needs FreeScout's *API & Webhooks* module. |
| **Zammad** | **Zammad address** *, **Access token** *, **Group for new requests** * | Everything works. |
| **Znuny / OTRS** | **Web service address** *, **Agent login** *, **Password** *, **Queue for new requests** *, **Agent interface address** | No renaming of customers. A Parcella web service has to be imported into Znuny once. |
| **osTicket** | **osTicket address** *, **API key** * | Only the website contact form works; reading and answering happen in osTicket. |
| **Zendesk** | **Zendesk address** *, **Agent email address** *, **API token** * | Everything works. |
| **Freshdesk** | **Freshdesk address** *, **API key** * | Everything works. |

The hint under each field says where to find the key or token in your
helpdesk. Also switch on the **Support (helpdesk)** module.

## Nextcloud Deck

Copies the cards of one Nextcloud Deck board onto Parcella's
[task board](../modules/tasks.md) -- one way only, read-only, kept up
to date automatically. This is a separate connection from the cloud
storage above, even when both use the same Nextcloud.

| Field / button | What it does |
|---|---|
| **Nextcloud server URL** | E.g. `https://cloud.example.com`. |
| **Nextcloud username** | |
| **Nextcloud Application Password** | Create one in Nextcloud under *Personal Settings → Security*. Leave empty to keep the stored one. |
| **Deck board ID** | The number at the end of the board's web address (`.../apps/deck/board/3` → `3`). Pasting the whole address works too. |
| **Save** | Saves the connection (**Deck settings saved**). |
| **Test connection** | Checks the connection with what is in the form. |
| **Sync now** | Shown once a board ID is saved. Copies the cards right away instead of waiting. Next to it: how many tasks were synced and when, or **Not synced yet**. |

Also switch on the **Nextcloud Deck Sync** module.

## Related

- [Turning modules on and off](modules.md)
- [Backup and restore](backup.md)
- [For gardeners](../gardeners/index.md) -- what the website forms look like from the other side
