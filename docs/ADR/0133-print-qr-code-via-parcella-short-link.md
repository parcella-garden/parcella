# Printed QR code: optional for a teaser, and pointing to a Parcella short link

**Context:** the printed notice (PRINT channel) got a QR code to the
website post only when its text had to be shortened to fit one page, and
only once the post was published, since there's nothing public to link
to before then (see docs/module-announcements.md, "Print channel").
kermie wants to print a short teaser that sends readers to the full post,
and to print it without waiting for the post to go live. He also wanted
the same Markdown editor for the print text as for the body.

## Decision

- **A switch per announcement, `Announcement.print_qr_code`** (default
  off): "QR code to the website post". When it's on, the QR code and the
  "read the full announcement online" note are part of the very first
  render, so a teaser that fits gets them too, and the paragraph-dropping
  fallback already leaves room for them. When it's off, nothing changes:
  the QR code still only appears when the text had to be shortened.
- **The QR code points to Parcella, not to the website:** to
  `<parcella>/a/<token>`. That short link asks the website connector live
  and redirects (302) to the post once it's public. Until then it shows a
  plain "not on the website yet" page. So:
  - the notice can be printed while the post is still a draft;
  - a slug changed in WordPress, or a date-based permalink that is only
    fixed at publication, doesn't break a code already on paper;
  - it works the same for every connector (WordPress, Markdown folder,
    CMS plugins), because they all answer `get_public_url_if_published`.
- **The token** (`Announcement.public_link_token`, `secrets.token_urlsafe(16)`,
  unique) is created on the first print with a website connector and never
  changes, so every PDF of an announcement carries the same link. The
  short link is used for the automatic shortening QR code too, so that one
  no longer waits for publication either. Without any website connector
  there is no post to point to, so there's no QR code, as before.
- **The public page says nothing.** No title, no hint whether the token
  exists: an unknown token gets the same page as a draft. Targeted
  messages (issue #242) never forward. It's rate-limited per IP (30 a
  minute), because each hit asks the website. Only `http(s)` URLs from
  the connector are followed.
- **Change tracking:** the switch is part of the PRINT fingerprint, but
  appended only when it's on (the same rule as the summary in ADR 0129),
  so fingerprints stored before it existed still match and migration
  0092's frozen copy stays valid. Toggling it offers a new PDF and leaves
  email and website alone.
- **The print text gets the EasyMDE editor** of the body, without
  "Insert image": the PDF only embeds the banner, never images from the
  text.
- The note under the QR code is now translated (`announcements.print.read_online`);
  it used to be English only.

## Rejected

- **Predicting the website URL from a slug made up front.** WordPress
  puts the publication date into many permalink structures, turns a
  taken slug into `slug-2`, and serves a 404 for a draft. A printed code
  can't be corrected afterwards; a redirect can.
- **Linking straight to the website and leaving the QR code out until
  publication** (the old behaviour): it forces a second print run after
  publishing, which is exactly what a teaser notice should avoid.

## Consequences

- Parcella gets one more public, unauthenticated URL (`/a/<token>`),
  behind the announcements module flag. It only ever reveals the public
  URL of a published post, which is public anyway.
- A printed code depends on Parcella staying reachable at the same
  address. That's the price for a code that works before the post exists.
