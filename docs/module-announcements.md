# Announcements module

Lets a board member write a single piece of club news once and push it
out to up to three channels: a draft on the club's website (WordPress,
a Markdown-based static site, or any CMS with a Parcella plugin), a
member email, and a printable one-page PDF notice for the
allotment area. All three channels are built (see below).

## Data model

```
announcements             -- one row per piece of club news
announcement_deliveries   -- one row per (announcement, channel) send attempt
```

`Announcement` fields worth calling out:

- `audience_applicant_ids` -- set only for a message to picked
  applicants (issue #247); see "Messages to picked applicants" below.
- `audience_filter` / `letters_for_all` -- set only for a message to
  filtered members (issue #242); see "Messages to filtered members"
  below. NULL means classic club news.

- `body_markdown` is the single canonical source text. It is used
  as-is for **both** the blog draft and the email -- there is
  deliberately no separate per-channel text override for those two,
  since the product requirement was "same container" for blog and
  email.
- `body_html` is derived from `body_markdown` (Markdown -> HTML ->
  sanitized) and cached at save time, so it isn't re-rendered on every
  read. It is never hand-edited directly; editing always happens on
  `body_markdown`.
- `print_text_override` is the one deliberate exception to "same
  container everywhere". It starts empty (meaning: print the full
  text). Once the PDF channel is built, it will be auto-filled with a
  shortened version whenever the full text doesn't fit on one printed
  page (plus a QR code linking back to the blog post) -- but it always
  remains a real, freely hand-editable field afterward, not just a
  computed preview.
- `image_filename` is a single header/featured image, reused across
  all three channels (WordPress featured image, inline in the email,
  and in the PDF's layout).

`AnnouncementDelivery` tracks channel state rather than duplicating
content per channel: one row per (announcement, channel), upserted
rather than appended, so retrying a failed send updates the existing
row instead of creating a growing history of attempts.

There is **no announcement-level status** (a `DRAFT`/`PUBLISHED`/
`ARCHIVED` column existed until migration 0092 but never left "draft"
-- see docs/ADR/0087). What went out where is per channel only. Each
successful delivery also records what it delivered
(`content_fingerprint`, `image_filename`), and PRINT keeps the
generated file (`pdf_filename`) plus `qr_pending`, which is used to decide
whether a channel's action is offered again. See "One action per channel" below.
`external_reference` holds whatever pointer a later phase needs back
from the channel -- currently only meaningful for BLOG, which will
store the published post's public URL once the blog channel exists (the
PRINT channel needs that URL for its QR code, which is why blog is
expected to run before print, though this isn't enforced).

## Key decisions

**Markdown as the authoring format, not a WYSIWYG rich-text editor.**
Both were viable (WYSIWYG/Quill or TipTap, both permissively licensed
and AGPL-compatible) but Markdown was chosen: lighter dependency
footprint, diff-friendly, portable if the club ever migrates off
Parcella, and it keeps `body_html` genuinely *derived* data rather than
canonical markup. The editor is EasyMDE (MIT-licensed), loaded via CDN
only on the announcement form page, with live preview.

**EasyMDE's toolbar needs an explicit `toolbar:` config, not the
library default (issue #228).** EasyMDE's built-in toolbar buttons are
hardcoded to Font Awesome icon classes (`fa fa-bold`, etc.), which this
project never loads (it uses Bootstrap Icons everywhere else, see
`app/templates/base.html`) -- the default toolbar rendered with every
button blank. `app/templates/announcements/form.html`'s `EasyMDE({...})`
call now passes its own `toolbar:` array mapping each button to its
`bi bi-*` equivalent. That in turn exposed a second, separate issue:
EasyMDE names each button's own DOM class after its internal name
(`createToolbarButton()` in EasyMDE's source), so the table button's
`class="table"` collides with Bootstrap 5's global `.table` class
(`width: 100%`, forcing it onto its own line) -- fixed with a scoped
CSS reset in the same template's `extra_head` block. Any future EasyMDE
upgrade should re-check both: a new default toolbar entry needs its own
`bi-*` mapping, and any other button name that happens to match a
Bootstrap utility/component class would hit the same collision.

**A separate sanitizer profile from the ticket-email sanitizer.**
`app/html_sanitizer.py`'s `sanitize_email_html()` strips all images,
because that content comes from an arbitrary external sender (anyone
can email a ticket inbox) and images there are a tracking-pixel/XSS
risk. Announcements are authored by a logged-in board member and images
are a first-class part of the content, so `app/announcement_utils.py`
uses its own allow-list (`render_markdown_to_html()`) that permits
`<img>` and a couple of extra formatting tags, while still stripping
script/style content and any `on*` handlers -- the rendered HTML is
pushed to WordPress and to every member's inbox, so it still can't be
trusted blindly just because the author is internal.

**Module flag defaults to `False`.** Same reasoning as
`public_signup_api`: this module will eventually hold outbound
credentials (a WordPress application password) and, once the email
channel is built, can send a message to every member with
`email_info = true`. A club must opt in deliberately.

**Restricted to admin/board (`require_admin`), not a general
member-facing feature.** Authoring content that gets pushed to a public
blog and to every member's inbox isn't something every logged-in member
should be able to trigger.

**No REST API for this module (so far).** Unlike most data-bearing
modules in this project, there's no `api_announcements.py` yet. This
isn't a scope decision the way Calendar's is -- it's simply not needed
until an external system needs to read/write announcements
programmatically, which so far only the (not-yet-built) WordPress
publisher will, and that's an outbound call Parcella makes, not an
inbound API surface.

## One action per channel (ADR 0087)

Each channel's button on the edit page is only shown while it has
something new to do. The server enforces the same rule with a 409, via
`_channel_action_available()` in `app/routers/announcements.py`:

- **Email**: once sent successfully, never again, not even after an
  edit. The page notes when the content changed after sending. A
  FAILED send can be retried.
- **Blog / website**: after a change to title/body/image, the button
  becomes "Update website draft". It updates the **same** post
  (`WebsiteConnector.update_post`) and never touches its publish
  status, so a published post stays published. If the post was deleted
  on the website, a new draft is created instead.
- **Print**: the PDF is stored and offered as "Download" (no
  regeneration). "Generate PDF" comes back after a change to
  title/body/print text/image, or when the last PDF was shortened
  without a QR code and a blog post now exists.

"Changed" means the channel's content fingerprint differs from the
current content. It is not a timestamp, so saving unchanged text does
not re-enable anything, and a print-text-only change re-enables only
the PDF.

## Email channel (built)

`app/announcement_mailer.py` sends the announcement to current club
members (`active_member_filter()` -- the same canonical "active"
definition `/members/`'s own list and API use, see ADR-adjacent note
in `app/services/members.py`) who have `email_notifications = True`
-- the "e-mail info = yes" flag from the original request. **Not**
scoped to current parcel residents: an earlier version required an
active `MemberParcel` too, matching the original feature request's
literal wording, but that silently excluded members who are still
within their membership period yet no longer hold a parcel lease
(issue #236) -- club communications should reach anyone who's still a
member, lease or no lease. Members with no stored email address are
silently skipped (a Members-admin data-completeness issue, not a
sending failure). The email body is the announcement's `body_html` wrapped in
a minimal branded shell (club name + header image + the same content
that would go to the blog) -- reusing `app/email_service.py`'s
existing `sende_email()`.

**Sending is paced, not all-at-once.** `EMAIL_BATCH_SIZE` (default 8)
emails go out, then a pause of `EMAIL_BATCH_PAUSE_SECONDS` (default 60)
before the next batch, repeating until everyone's been sent to. For a
roster of a few hundred, that's realistically tens of minutes -- too
long to hold an HTTP request open -- so the actual sending runs as a
FastAPI `BackgroundTasks` job (`run_paced_email_send`), started from
the request but continuing after the response has already gone back to
the browser. Because the request's DB session closes once the response
is sent, the background task opens its own (`AsyncSessionLocal`),
mirroring the existing pattern in `app.main`'s ticket-inbox polling
loop.

To make an in-progress send visible without adding new columns, a
`SENDING` status was added to `AnnouncementDeliveryStatus` (migration
`0030`). While sending, `error_message` is repurposed to hold a running
progress note ("140 of 800 sent so far") rather than an error --
see the field's docstring in `app/models.py`. The edit page shows this
with a spinner and disables the "Send now" button while a send is
`SENDING`; the router also rejects a second `POST .../send/email` with
409 if one is already in progress, as a server-side backstop against
double-sends (e.g. a double click or a stale tab).

`AnnouncementDelivery` stays channel-level, not per-recipient (see the
model docstring), so a partial failure -- some recipients unreachable
-- is still recorded as `SENT` with the failure count noted in
`error_message`; a *total* failure (zero successful sends, or zero
qualifying recipients at all) is recorded as `FAILED` so it's visually
distinct and invites a retry.

**Test send.** Before committing to the real send, a board member can
send the exact current content to one address of their choosing via
`POST /announcements/{id}/send/test-email`. This is deliberately
separate machinery from the real send: it isn't paced (it's one
email), it doesn't touch `AnnouncementDelivery` at all, and the email
itself carries a visible "this is a test" banner so it's never
mistaken for the real thing if it lands in the same inbox as a
previous real send.

## Website channel (built, ADR 0104/0105)

The channel is still called BLOG in the data model, but it isn't tied to
one CMS. `push_website_draft()` in `app/routers/announcements.py` sends
the draft through whichever **website connector** is active on Admin ->
Integrations -> Website: a dropdown, one CMS at a time. Choosing another
one switches the previous one off but keeps its settings.

The connectors live in `app/website_connectors/` and all implement
`WebsiteConnector` (`base.py`):

- **WordPress** (`wordpress.py`): WordPress's own REST API
  (`wp-json/wp/v2/posts`, `.../media`) with an Application Password
  (WP 5.6+). No plugin is needed on the WordPress side for this
  direction; the parcella-connector plugin in `integrations/wordpress/`
  handles the other direction (forms posting INTO Parcella).
  `external_reference` is the post's edit URL.
- **Markdown folder** (`markdown_folder.py`): for static sites built from
  Markdown (Hugo, Jekyll, Eleventy, Astro, kgv-goldene-hoehe's own
  generator). Writes `{date}-{slug}.md` with a YAML header (title, date,
  url, author, categories, summary, image, `parcella_announcement`,
  `draft: true`) into a folder on cloud storage, and the image into
  `<media>/YYYY/MM/<uuid>.<ext>`. A human publishes by deleting
  `draft: true`. Updates rewrite only title, summary, the body and (if it
  changed) the image line; every other header line is kept as the human
  left it, and `draft: true` is never added back. `external_id` is the
  file name; `external_reference` is the folder path shown on the page.
- **Parcella plugin** (`parcella_plugin.py`): any CMS running a plugin
  that implements docs/website-plugin-protocol.md (TYPO3, Contao, Drupal,
  Joomla, ...). Requests are HMAC-signed with a secret the plugin
  generates.

Settings are ClubSettings: `website_connector` holds the active type,
fields are `website_<type>_<field>`, secrets are encrypted with
`app.crypto_utils` and a blank secret on save keeps the stored one.
"Test connection" checks the typed values (blanks fall back to the saved
ones) without saving.

Every connector only creates **drafts**. Whether and when a post goes
public stays a human decision in the CMS, which is also why the print
channel asks the website live whether a post is published before it adds
a QR code.

REST API (`app/routers/api_website.py`): `GET /api/v1/website/connectors`
(types and their fields), `GET`/`PUT /api/v1/website` (active type and
non-secret fields; ADMIN only; secrets are never accepted or returned,
same rule as `/api/v1/club-settings`), `POST /api/v1/website/test`, and
`POST /api/v1/announcements/{id}/website-draft` (full access, same
409 "nothing new" rule as the button).

If the image can't be found on disk (unlikely, but possible if it was
manually deleted outside the app), the draft is still created without
an image rather than failing outright.

## Print channel (built)

`app/print_publisher.py` renders a one-page, branded PDF via
WeasyPrint (HTML/CSS -> PDF), sharing the exact same page chrome as
every other PDF in the app (`app/pdf_chrome.py`'s `wrap_document()` --
DIN-style fixed header, the three-column organization/register-court/
bank footer, "Page X of Y") rather than its own bespoke
`@top-center`/`@bottom-center` header/footer, which is how it worked
originally (see docs/ADR/0045 for why it was brought in line -- it was
deliberately left out of the initial shared-chrome extraction in ADR
0043 as a differently-shaped single-page document, then asked to match
anyway). It keeps its own larger body font (`extra_css`) since a
pin-up notice still reads better with more generous type than the
denser tabular documents sharing this chrome. Still always exactly one
page -- adopting the shared chrome didn't change the fitting
algorithm below, it just means the page now also shows "Page 1 of 1"
and the full org/bank footer instead of just the club name.

**The auto-shorten loop, exactly as originally scoped:**
1. Render with the full text (the manual `print_text_override` if the
   admin already set one, otherwise the full `body_markdown`).
2. If that's one page, done -- no QR code, `print_text_override` is
   left untouched.
3. If not, shorten paragraph-by-paragraph (dropping from the end,
   most content kept first) and re-render each attempt until one fits.
   The QR code and "read the rest online" note are added starting from
   the first shortened attempt -- untouched text never gets a QR code.
4. The shortened text that fits gets written back onto
   `print_text_override` (persisted, freely editable afterward,
   consistent with the field's original design) so the admin can
   review/adjust it, and so regenerating later doesn't repeat the
   search.
5. If even a single paragraph still doesn't fit alongside the
   header/footer/image, generation stops (`PrintTooLongError`) and asks
   a human to shorten manually, rather than silently truncating
   mid-sentence or producing a multi-page "one-pager".

**The QR code only appears once, and only if, there's a genuinely
public website post to point at.** Since drafts aren't public, the
active connector's `get_public_url_if_published()` is called live, at
print-generation time, using the BLOG delivery's stored `external_id`
(WordPress post ID, Markdown file name, or plugin draft id) -- not a
cached URL. WordPress is asked for the post's `status`/`link`, the
Markdown connector checks the file for `draft: true` and builds the URL
from the site address plus the header's `url`, a plugin answers
`GET /drafts/{id}`. If the post is still a draft (or was never sent),
the QR code is simply omitted; nothing blocks generating the PDF anyway.

**Images and the logo are embedded as base64 data URIs**, not
filesystem paths or HTTP URLs, so the PDF doesn't depend on WeasyPrint
resolving relative paths correctly or on the app's own HTTP server
being reachable from itself at render time.

**Delivery tracking**: like the other channels, `AnnouncementDelivery`
for PRINT is channel-level. A successful generation is `SENT` with
`error_message` repurposed (same convention as SENDING for email) to
note whether shortening happened and whether a QR code was included --
useful context for an admin glancing at the delivery panel without
having to open the PDF. A `PrintTooLongError` is recorded as `FAILED`
with the reason, and no PDF is returned for that request (the
"Generate PDF" button, an ordinary HTML form POST, either downloads a
PDF or redirects back to the same page showing the failure -- both are
valid outcomes for the same button).

**System dependencies**: WeasyPrint needs Pango/Cairo/GDK-Pixbuf at the
OS level (added to `Dockerfile`), not just the `weasyprint` Python
package -- see `requirements.txt` / `Dockerfile` for the exact
packages.

## Messages to filtered members (issue #242, ADR 0095)

The same authoring and email machinery, aimed at exactly the members on
a filtered `/members/` list -- "everyone tagged *water responsible*",
"all pending members" -- instead of the whole club.

- **Start**: the "Write to these N members" button on a *filtered*
  `/members/` list (announcements module on, board/admin only) opens
  `/announcements/new?audience=1&audience_query=<the list's filter>`.
  The new announcement stores that filter as
  `Announcement.audience_filter` (a `MemberListFilter.to_dict()`, see
  `app/member_filters.py`); `audience_filter IS NULL` is classic club
  news, unchanged. An empty filter (the unfiltered list) is refused as a
  targeted message and becomes club news: otherwise one click would
  mail every member while bypassing the email-info opt-out.
- **Who gets what** -- `resolve_audience()` in
  `app/announcement_mailer.py`, re-run every time the page is shown and
  at send time (the filter is stored, not a frozen list): email to each
  member with an address, **ignoring the email-info opt-out** (an
  operational message to the water team isn't a newsletter); a letter
  to each member without one who has a postal address -- or to every
  member with an address when "letters for everyone" is ticked;
  members with neither are listed by name as unreachable so the board
  can fix the record. The page shows all three groups.
- **Channels**: EMAIL (unchanged paced send, once) and LETTER. BLOG and
  PRINT are hidden and refused with 409 -- a message to some members is
  no blog post and no notice-board page. Classic announcements never
  get LETTER.
- **Letters** (`app/announcement_letters.py`): one PDF, one DIN 5008
  letter per recipient (address window shared with invoices via
  `app/pdf_chrome.py`'s `ADDRESS_WINDOW_CSS`/`sender_line`), title and
  body as in the email, no added salutation, no image, no "Page X of Y"
  (it would count across the bundle). **Generated on click and never
  stored**: unlike the print notice it holds names and addresses, and
  `app/static/uploads/` is publicly served. So the LETTER action is
  always available; its delivery row records only when, how many and
  for which content (no names), so the page can say "changed since".
- Download file names (print and letters) are ASCII-only slugs of the
  title -- a quote or a non-latin-1 character in a Content-Disposition
  header breaks the response.

Known gaps: no per-recipient delivery log (channel-level, as for club
news); the audience isn't frozen at send time -- someone tagged between
sending the email and generating the letters is included in the
letters; no attachment support.

## Messages to picked applicants (issues #246/#247, ADR 0112)

The third kind of announcement, next to club news and filtered members.

- **Start**: tick applicants on `/applicants/` (checkbox per row,
  "Select all" / "Select none"), then "Write to the selected
  applicants" -- a GET to
  `/announcements/new?audience_kind=applicants&applicant_ids=...`.
  Needs the applicants module and applicants read permission on top of
  the usual board/full access. Unknown ids are dropped; an empty or
  entirely unknown selection is a 400, never club news.
- **Stored** as `Announcement.audience_applicant_ids`, a list fixed at
  creation (`is_applicant_message`; `is_targeted` is true as well).
- **Who gets what** -- `resolve_audience()` returns one
  `(Applicant, address)` pair per distinct address (ignoring case and
  surrounding blanks, oldest application first) and counts the merged
  duplicates; the page shows both. The paced sender is unchanged.
- **Channels**: EMAIL only. BLOG, PRINT and LETTER are hidden and
  refused with 409.

## What's not built yet

Nothing -- all three channels (email, blog, print) are now built. Any
further refinement (e.g. admin-configurable pacing numbers for email,
sending one announcement to several websites at once, a "publish and
print" one-click flow) would be
a new, separate piece of work rather than something left over from the
original scope.
