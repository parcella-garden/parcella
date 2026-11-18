# The compose popup writes and sends a message in one step

**Context:** Issue #345: writing to members (from `/members/`, a member's
page, `/applicants/`, `/announcements/`) loaded a full page, and sending
took a second one. "New message" saved a draft, then the message's own
page offered a test email and one button per channel. kermie asked for
a popup instead of page loads, and then why sending needs two steps at
all.

The second step exists for a reason: every channel works on a *saved*
message and keeps its own delivery state (ADR 0087). That is what makes
the later actions possible: retrying a failed channel, "update website
draft" after an edit (the same post, not a second one), printing again
once the website post exists, and refusing a second email. None of that
needs a separate page for the *first* send, though.

**Decision:**

1. **One popup, opened from every place a message can start.** Any link
   or submit button with `data-compose` opens
   `announcements/_compose_modal.html`, which `base.html` includes once
   for board/admin when the announcements module is on. A link passes
   its own query string, a submit button its form's fields: the same
   parameters as `/announcements/new`, so the audience logic
   (`_targeted_audience_query`, `_picked_applicant_ids`) is shared.
   Without JavaScript the link or button still opens the full page.
2. **An ordinary Bootstrap popup, like the others in Parcella, not a
   frame.** The form is fetched as an HTML fragment from
   `GET /announcements/compose` and posted with `fetch()` to
   `POST /announcements/compose` (CSRF header from the meta tag). An
   `<iframe>` would have kept the existing two pages inside the popup,
   but it needs `frame-ancestors`/`X-Frame-Options` relaxed (ADR 0064).
   Doing this the way the existing popups work keeps those headers as
   they are.
3. **"Save & send" saves the message and runs the ticked channels**
   through the same helpers as the send page (`start_email_channel`,
   `push_website_draft`, `generate_print_channel`,
   `generate_letter_channel`). So ADR 0087's rules apply unchanged: a
   channel without anything new is skipped, and the email goes out once.
   Generated PDFs (notice, letters) come back base64-encoded in the JSON
   and the browser saves them. The letters are still never stored.
4. **Offered channels follow the message kind:**
   - club news: email, website draft (only when a website is set up) and print;
   - filtered/picked members: email and letters;
   - applicants: email.

   **Email is ticked by default** whenever anyone gets one (kermie's
   call). Letters are ticked instead when nobody has an email address.
   The server ignores a ticked channel it didn't offer.
5. **A test email saves a draft first**, because the test renders a
   saved message. The popup then keeps editing that draft
   (`announcement_id`), **but only while nothing has been delivered from
   it**: a 409 otherwise. Once something has gone out, the message's own
   page is the place to continue.
6. **The message's page stays** for everything after the first send:
   retries, website updates, printing again, the print text and QR code
   switch, and deleting. The full-page `/announcements/new` stays as the
   no-JavaScript fallback.

**Rejected alternatives:**

- *Frame the existing pages in the popup.* This needs the clickjacking
  headers relaxed, and the two-step flow stays.
- *Drop the per-channel state and send everything at once from one
  form.* That loses retries, website updates and the once-only email
  guard (ADR 0087).
- *Pick the channels in the popup but send from the message page.*
  That still takes two steps, which is what #345 was about.

**Consequences:** One more route pair and a fragment template. The
channel code moved into helpers shared by both paths, so they can't drift
apart. The popup's editor is a smaller EasyMDE toolbar (no full-screen or
side-by-side mode, which don't work inside a popup). The print text
override and the QR code switch stay on the message's page.
