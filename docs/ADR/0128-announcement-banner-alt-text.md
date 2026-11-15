# Announcement banner alt text: own field, title fallback, alt-only updates

**Context:** issue #318. The banner image of an announcement had no alt
text anywhere: Parcella's own pages, the email and the print PDF used
`alt=""`, the WordPress connector set none, and the CMS plugins
(Drupal, Joomla, TYPO3, Contao) used the announcement's title. That's
poor for screen-reader users and for search engines.

## Decision

- **One optional field, `Announcement.image_alt`** (max 255 characters,
  one line: whitespace and newlines are flattened when saving). It only
  exists while there is an image: removing the image clears it, and
  without an image the form value is ignored.
- **Fallback to the title on the websites only.** When no alt text is
  given, the website channels get the title, which is what the plugins
  did before. Parcella's own list thumbnail stays `alt=""`, since the
  title sits right next to it. The email and the PDF use the alt text
  when there is one.
- **An alt-only edit counts as a content change** (ADR 0087).
  `AnnouncementDelivery.image_alt` records what each channel got, just
  like `image_filename`, so `channel_fingerprint()` and its copy in
  migration 0092 stay untouched.
- **An alt-only change doesn't upload the image again.** Connectors get
  `update_post(..., alt_changed=True)`:
  - WordPress reads the post's `featured_media` and sets that media
    item's `alt_text`. A new upload also sets `alt_text`, with a second
    request, because a binary media upload can't carry fields.
  - Markdown folder: an owned front-matter line `image_alt:` next to
    `image:`.
  - Website Plugin Protocol: an optional top-level `image_alt` field,
    still `parcella-website/1`, because the change is purely additive.
    Like `image`, it is absent when it didn't change, so an alt text a
    human edited in the CMS survives every other update. Receivers set
    it on a new image (falling back to the title, so older Parcella
    versions behave as before) and on the existing image when only the
    alt text changed. Plugins 1.1.0 implement this.

## Rejected

- **Putting the alt text into the fingerprint.** This would have
  changed every existing fingerprint (and needed migration 0092's copy
  updated), marking every announcement ever delivered as "changed".
- **Re-uploading the image on an alt change.** That's simpler, but it
  leaves a duplicate in WordPress's media library and every CMS's file
  storage each time.
- **Always sending the alt text on updates.** It would overwrite alt
  texts that people improved directly in the CMS.
