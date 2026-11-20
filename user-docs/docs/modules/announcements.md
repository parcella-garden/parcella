# Announcements

Write a piece of club news once and send it out on up to three channels:
an e-mail to your members, a draft post on the club website, and a
one-page notice to print and pin up in the garden. The same module also
sends messages to a selection of members or applicants.

!!! info "Who can use this"
    - The module switch is **Announcements** under **Administration →
      Turning modules on and off**. It is **off** by default, because
      it can e-mail every member and stores the login for your website.
    - Only the **Board** and **Administrator** roles, and members of a
      group with **Full access to every module**, see **Announcements**
      in the menu and can use it. There is no group permission to give
      other users access.
    - The website channel needs a website connection under
      **Administration → Integrations → Website (drafts from
      announcements)**. See [Integrations](../administration/integrations.md).

## Three kinds of announcement

| Kind | How you start it | Channels |
|---|---|---|
| Club news | **New Announcement** on the announcement list. | Member e-mail, website draft, printable PDF |
| Message to filtered members | **Write to these {count} members** on a filtered [member list](members.md), or tick members and click **Write to selected**. | Member e-mail, letters |
| Notice to the leaseholders of picked parcels | Tick parcels on the [parcel list](parcels.md#picking-parcels) and click **Write to their leaseholders**. About the lease, not the membership: one notice per parcel, naming it; e-mail only to leaseholders who allow it, one letter per address for the others. | E-mail, letters |
| Message to selected applicants | Tick applicants on the [applicant list](applicants.md) and click **Write to the selected applicants**. | E-mail only |

All three are written in the same form and listed on the same page.

## Announcement list

![Announcement list](../assets/screenshots/announcements/list.png)

Open **Announcements** in the menu. The list shows all announcements,
newest first.

| Column / button | What it shows |
|---|---|
| **New Announcement** | Opens an empty form for club news. |
| Picture | The announcement's image as a thumbnail, or a megaphone icon if it has none. |
| **Title** | The title, linked to the edit page. A badge marks **Filtered members** or **Applicants** messages. |
| **Channels** | One icon per channel: envelope (e-mail), globe (website), printer (PDF) for club news; envelope and mailbox (letters) for member messages. Green means **done**, red **failed**, blue **sending**, grey **not yet**. Hover over an icon to read its state. |
| **Created** | The date the announcement was created. |
| Pencil | Opens the edit page. |

With no announcements yet the list says **No announcements yet.**

There is no overall "draft / published" status. What went out where is
tracked per channel only.

## Writing an announcement

![New announcement](../assets/screenshots/announcements/form-new.png)

The form is the same for new and existing announcements.

| Field / button | What it does |
|---|---|
| **Title** | Required. Used as the e-mail subject, the post title and the heading of the printed notice. |
| **Summary** | Optional, plain text, up to 300 characters. Shown as the preview line under the email subject and as the excerpt on the website. A counter shows how many characters you've used; it turns orange above 160, which is about what search engines show. |
| **Image** | Optional. PNG, JPEG, or WebP, up to 5 MB. Used as the website post's image, shown in the e-mail and on the printed notice. A larger file is refused straight away and **Save** is disabled until you choose another one. |
| **Remove image** | Only shown once an image is saved. Tick and save to remove it. |
| **Image description (alt text)** | Optional, up to 255 characters. Describe what the picture shows, for people using screen readers and for search engines. Left empty, websites get the title. |
| **Body text** | Required. Written in Markdown. This same text is used for both the website draft and the member email. |
| **Print version (optional)** | Only on an announcement that has been saved once, and only for club news. See [The printed notice](#the-printed-notice). |
| **QR code to the website post** | Same place as the print version. See [The printed notice](#the-printed-notice). |
| **Save** | Saves your changes and opens the edit page. Saving only stores your changes -- it doesn't send or publish anything. |
| **Cancel** | Back to the list without saving. |

If the title or body is missing, the form shows **Please provide both a
title and a body text.** and keeps what you typed.

### The text editor

The **Body text** box is a Markdown editor with a toolbar: bold,
italic, strikethrough, heading, code, quote, bulleted and numbered
lists, link, image, table and horizontal line. The eye icon switches to
a preview, the split icon shows text and preview side by side, and the
arrows open a full-screen editor. The question mark opens a short
Markdown guide in a new tab.

The image button inserts a picture *by its web address*; it doesn't
upload a file. For the main picture of the announcement use the
**Image** field.

## The edit page

![Editing an announcement](../assets/screenshots/announcements/form-edit.png)

After the first save you land on the edit page. It has the form from
above, and below it three more cards.

### Send a test email

Sends the current content to one address for review. Never counted as a
real send and never goes to members. Enter an address and click
**Send test**. The test e-mail carries a visible note that it is a test.

The page then shows **Test email sent successfully** with the address,
or **Could not send the test email -- check the SMTP configuration
under Admin -> Settings.**

!!! tip
    Save first. The test uses the saved content, not what is still in
    the form.

### Delivery channels

Each channel has a line with its status and, when there is something to
do, one button. Each channel is done once. After you change the content
and save, the website post and the PDF can be updated; the email is
only sent once.

| Status | Meaning |
|---|---|
| **Not sent yet** | Nothing has happened on this channel. |
| **Sent** / **PDF generated** | Done, with date and time. |
| **Sending...** | The e-mail is going out right now. |
| **Failed** / **Too long for one page** | The last attempt didn't work. The reason is shown underneath, and the button is offered again to retry. |
| **Content changed since then.** | You edited the announcement after this channel was done. |

#### Member email

**Send now** sends the announcement to all current members who have
e-mail notifications switched on (the "email info" setting on the
member). Members whose membership is still running get it, whether they
hold a plot or not. Members without an e-mail address are skipped.

You confirm first: **Send this announcement by email to all current
members with email notifications enabled? This can only be done once.**

- The e-mails go out in small batches with a pause between them, so
  your mail server isn't flooded. For a few hundred members this takes
  tens of minutes. You can leave the page; the sending carries on.
- While it runs, the line shows **Sending...** and a running count.
  Reload the page to see the latest count.
- If some addresses fail, the channel still shows **Sent**, with the
  number of failures noted. If not a single e-mail could be sent, it
  shows **Failed** and you can try again.
- Once sent, the button never comes back, not even after an edit. If you
  change the text afterwards, the page says **The content was changed
  after the email went out. Members received the earlier version.**

#### Website draft

Next to **Website draft** you see which website is connected:
**WordPress**, **Markdown folder (cloud storage)** or **Parcella plugin
(TYPO3, Contao, Drupal, Joomla, ...)**.

- **Create draft** sends title, text, summary and image to the website
  as an unpublished draft. Parcella never publishes anything; that stays
  a decision you make in your website's own admin.
- After a successful send, **Open draft** links to the draft in your
  website's editor (WordPress, plugins). For a Markdown folder the file
  path is shown instead; you publish by removing the `draft: true` line
  from the file.
- After you change title, text, summary or image and save, the button
  becomes **Update website draft**. It overwrites the same post instead
  of creating a second one, and keeps its publish status, so a published
  post stays published. You confirm first, because text edits made
  directly on the website will be lost.
- If the post was deleted on the website in the meantime, a new draft is
  created.
- Without a website connection the attempt fails with "No website is set
  up yet -- choose one under Admin -> Integrations -> Website."

#### Printable PDF

**Generate PDF** creates the one-page notice and downloads it. See
[The printed notice](#the-printed-notice). Afterwards the line offers
**Download** for the stored PDF. **Generate PDF** comes back when you
change title, text, print version, QR setting or image, or when the
notice was shortened without a QR code and the website post may since
have gone online.

### Delete announcement

Permanently removes this announcement, whatever has already been sent.
You confirm first: **Really delete this announcement? This cannot be
undone.** The image and the stored print PDF are deleted with it. Mails
already sent and website posts already created are not affected.

## The printed notice

The **Printable PDF** channel makes a single A4 page for the notice
board, with your club letterhead, the image, the title, a line
"Published on <date> by <name>" (the date you generate the PDF, and the
author's name) and the text.

| Field | What it does |
|---|---|
| **Print version (optional)** | Leave empty to print the full text above. If it doesn't fit on one page, a shortened version will be suggested here -- feel free to edit it. Below it the form says **Fits on one printed page.** or **Likely too long for one printed page -- consider shortening.** The editor is the same as for the body, without the image button. |
| **QR code to the website post** | Prints a QR code to the website post even if the text fits on one page, for a print text that's only a teaser. Off by default. |

What happens on **Generate PDF**:

1. Parcella tries the print version, or the full text if it is empty.
2. If that fits on one page, done.
3. If not, it drops paragraphs from the end until it fits, and adds a QR
   code with "Read the full announcement online:". The shortened text is
   saved into **Print version (optional)**, so you can check and adjust
   it.
4. If even one paragraph doesn't fit next to the image and letterhead,
   no PDF is made. The channel shows **Too long for one page** and you
   need to shorten the print version yourself.

The QR code leads to a short link in Parcella, not straight to the post.
As soon as the post is published on your website, the link forwards
there. Until then, anyone who scans it sees a small page saying
**This announcement isn't on the website yet. Please try again later.**
-- without the title or any other detail. So you can print and pin up
the notice before the post goes live. Without a website connection there
is no QR code at all.

If a shortened notice was printed while the post was still a draft, the
page notes **The text was shortened without a QR code because the website
post wasn't public yet. Once it's published, create the PDF again to add
the QR code.**

!!! tip "Saving the PDF to the cloud"
    With the cloud storage module on and a **Folder for printed
    announcements** set under **Administration → Integrations**, every
    generated PDF is also saved there, named after the title and date.
    A second PDF on the same day replaces that day's file. If the upload
    fails, you still get the download; the failure is noted on the
    channel.

## Messages to filtered members

![Message to filtered members](../assets/screenshots/announcements/form-audience.png)

Use this for operational messages to part of the club: "everyone tagged
*water responsible*", "all pending members".

1. On the [member list](members.md), filter the list (search, tag,
   checkboxes). Then click **Write to these {count} members**, or tick
   individual members and click **Write to selected**.
2. The announcement form opens with a card **Message to {count}
   member(s)** above it.

The card shows:

| Item | What it shows |
|---|---|
| **Selection:** | The filter the message is based on, as badges: tag, search text, **Show inactive only**, **Confirmed active only**, **Email info = yes only**, "{count} picked by hand". |
| **Show these members** | Opens the member list with this filter. |
| "{count} by email" | Members who allow information by e-mail (**May receive information by email**) and have an address. |
| "{count} by letter" | Letters for the other members with a postal address -- one per address, so members who live together share one. Their names follow. |
| "{count} can't be reached (no email consent or address, no postal address)" | Shown in red, with links to the members so you can fix their records. |
| **Also send a letter to members who get the email** | Tick to send a letter to every member with a postal address, not only to those without e-mail. |

Recipients are worked out again when you send, from the member list
filter shown above. Someone who gets the tag tomorrow is included in
tomorrow's letters. Hand-picked members who no longer match the filter
drop out.

!!! note "E-mail only with consent"
    A message to members goes by e-mail only to members who allow
    information by e-mail. Everyone else with a postal address gets a
    letter -- also when someone they live with got the e-mail, because
    every member is invited personally. Members without consent who
    share an address get **one** letter naming all of them. Starting
    from an unfiltered member list creates ordinary club news instead.

The channels are **Member email** (sent once, same as above, after the
confirmation **Send this message by email to {count} member(s) now?
This can't be undone.**) and **Letters**:

- **Generate {count} letter(s)** creates one PDF with a letter per
  postal address, laid out for window envelopes (DIN 5008 Form B, with fold marks), with title and body as in
  the e-mail. No salutation is added, and no image.
- The letters are generated when you click and never stored, because
  they contain names and addresses. You can generate them again any time.

Website and print channels are not offered for these messages.

## Messages to selected applicants

On the [applicant list](applicants.md), tick applicants and click
**Write to the selected applicants**. The form shows a card **Message to
{count} applicant address(es)** with the applicants' names (linked) and
**Show applicants**.

- If several selected applications share an e-mail address, that
  address gets the message only once; the card says how many were merged.
- Email only. The selection is fixed: applicants you tick later are not
  added.
- You need access to the applicants module as well.
- **Send now** asks **Send this message by email to {count} applicant
  address(es) now? This can't be undone.**

## The "not online yet" page

![Not online yet](../assets/screenshots/announcements/not-online.png)

This is the public page people see when they scan a QR code from a
printed notice before the post is published, or when the link is
unknown. It shows only your club's logo and name and the sentence
**This announcement isn't on the website yet. Please try again later.**

## Related

- [Integrations](../administration/integrations.md) -- connecting the
  website and the cloud folder for printed notices.
- [Members](members.md) -- the "email info" setting, tags, and starting
  a message to filtered members.
- [Applicants](applicants.md) -- writing to selected applicants.
- [E-mail log](../administration/email-log.md)
- [Turning modules on and off](../administration/modules.md)
