# E-mail log

The e-mail log lists every e-mail Parcella has tried to send --
invitations, notifications, announcements, invoices, sign-up
confirmations -- and what the mail server answered. Look here when
someone says "I never got that e-mail".

!!! info "Who can use this"
    Administrators only. Open **Administration → Email log**.

![Email log](../assets/screenshots/administration/email-log.png)

## Reading the log

At the top a short note explains the page and how many days entries
are kept, with a link **Change** to the
[setting](settings.md#email-log).

The card **Outgoing emails** shows the number of entries found and a
table, newest first, 50 per page:

| Column | What it shows |
|---|---|
| **Date/time** | When Parcella handed the e-mail to the mail server, in your club's time zone. |
| **Recipient** | The address it went to. |
| **Subject** | The subject line. A paperclip means it had attachments; hover over it to see how many. |
| **Status** | **Sent** or **Failed**. Under **Failed** you see the mail server's error message. |

**Newer** and **Older** at the bottom page through the log (**Page ...
of ...**).

### What "Sent" and "Failed" mean

- **Sent** means your mail server **accepted** the e-mail. It doesn't
  prove it arrived: if the mailbox is full or the address no longer
  exists, the bounce message goes to your club's sending mailbox, not
  into this log.
- **Failed** means the mail server refused it straight away or
  couldn't be reached -- for example a wrong password, an unknown
  recipient, or no mail server set up at all.

If many e-mails fail with the same error, check the mail server
settings under [Club settings](settings.md#email-smtp).

## Searching and filtering

| Element | What it does |
|---|---|
| **Search recipient…** | Shows only e-mails whose recipient address contains what you type. |
| Status list | **All statuses**, **Sent** or **Failed**. Changing it filters immediately. |
| **Filter** | Applies the search. |
| **Reset** | Appears while a filter is active; shows everything again. |

**No emails logged yet.** appears when nothing matches.

## How long entries are kept

Recipient addresses are personal data, so entries are deleted
automatically after the number of days set under
[Club settings → Email log](settings.md#email-log) -- 90 days unless
you change it. The log stores only the recipient, subject, status and
error and the number of attachments -- not the text of the e-mail.

## Related

- [Club settings](settings.md#email-smtp)
- [Users and invitations](users.md)
