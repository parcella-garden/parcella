# Announcements module

Lets a board member write a single piece of club news once and push it
out to up to three channels: a blog draft on the club's CMS (e.g.
WordPress), a member email, and a printable one-page PDF notice for the
allotment area. This first delivery covers only the **foundation** --
authoring the content and its data model. The three delivery channels
are built in later phases on top of this.

## Data model

```
announcements             -- one row per piece of club news
announcement_deliveries   -- one row per (announcement, channel) send attempt
```

`Announcement` fields worth calling out:

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

## Email channel (built)

`app/announcement_mailer.py` sends the announcement to current parcel
residents (`MemberParcel.assigned_until IS NULL`) who aren't
soft-deleted, whose membership hasn't lapsed, and who have
`email_notifications = True` -- the "e-mail info = yes" flag from the
original request. Members with no stored email address are silently
skipped (a Members-admin data-completeness issue, not a sending
failure). The email body is the announcement's `body_html` wrapped in
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

## Blog channel (built)

`app/blog_publisher.py` defines a small `BlogPublisher` interface with
one implementation so far, `WordPressPublisher`, using WordPress's own
built-in REST API (`wp-json/wp/v2/posts`, `wp-json/wp/v2/media`) and
its own built-in authentication (an Application Password, WP 5.6+) --
no custom plugin needed on the WordPress side for this direction. This
is the opposite direction from the public-signup connector: there, a
WordPress plugin pushes data INTO Parcella; here, Parcella pushes a
draft OUT to WordPress.

Credentials (site URL, username, Application Password) are configured
under Admin -> Integrations (alongside the public-signup API token --
Integrations is the page for "how Parcella connects to other
systems," in either direction), with the same encryption
(`app.crypto_utils`) and "blank = keep existing" convention used
elsewhere for secrets, hand-rolled for this page rather than reusing
the generic Settings-field mechanism. A "Test connection" button calls
`wp-json/wp/v2/users/me` to verify the credentials before you commit
to using them for a real send.

Every post is created with `status="draft"` -- the publisher never
decides to actually publish. Whether and when to make it public stays
a human decision in the WordPress admin, which is also why
`AnnouncementDelivery.external_reference` stores the **edit** URL
(`wp-admin/post.php?post={id}&action=edit`), not a public post URL --
there isn't a public one yet. This matters for the not-yet-built print
channel: its QR code needs a URL that's actually public, so it can
only be generated once a board member has published the WordPress
draft themselves; nothing in Parcella currently blocks running print
before that happens, since the QR code is just omitted if there's no
public URL to point at yet (see "What's not built yet" below).

If the image can't be found on disk (unlikely, but possible if it was
manually deleted outside the app), the draft is still created without
a featured image rather than failing outright.

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
public blog post to point at.** Since drafts aren't public,
`app.blog_publisher.WordPressPublisher.get_public_url_if_published()`
is called live, at print-generation time, using the BLOG delivery's
stored `external_id` (the WordPress post ID) -- not a cached URL --
and asks WordPress directly whether the post's `status` is now
`publish` and, if so, what its current `link` is. If the post is still
a draft (or was never sent to the blog at all), the QR code is simply
omitted; nothing blocks generating the PDF anyway.

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

## What's not built yet

Nothing -- all three channels (email, blog, print) are now built. Any
further refinement (e.g. admin-configurable pacing numbers for email,
multi-CMS blog support, a "publish and print" one-click flow) would be
a new, separate piece of work rather than something left over from the
original scope.
