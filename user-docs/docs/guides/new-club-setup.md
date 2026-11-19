# Setting up a new club

Parcella is installed and running. This guide takes you from the very
first login to an installation the whole board can work with: a safe
admin password, your club's details and logo, the right language, only
the modules you need, accounts for the other board members, and -- if
you like -- a round of practice with sample data first.

Plan about an hour. You need the administrator account that came with
the installation.

!!! info "Who can do this"
    Everything here happens in **Administration**, which only
    administrators (and groups with **Can access the administration
    panel**) can open. See
    [Roles, groups and permissions](../getting-started/roles-and-permissions.md).

## 1. Log in and change the admin password

1. Open Parcella in your browser and log in with the administrator
   account from the installation.
   <!-- TODO(verify): the default login (admin@parcella.local / admin1234) is documented for developers; confirm whether self-hosters get the same default or set their own during installation before naming it here. -->
2. If the account still uses the default password from the setup,
   Parcella opens **Change password** right away and shows: *"This
   account still uses the default password from the initial setup.
   Please choose a new one -- the rest of the application stays locked
   until you do."*
3. Enter the **Current password**, then a **New password** and
   **Confirm new password**, and click **Change password**.

You can change your password again at any time from the user menu at
the bottom of the sidebar: **Change password**.

!!! warning
    Don't skip this on an installation that can be reached from the
    internet. Anyone who knows the default password could otherwise log
    in as administrator.

More: [First login and your account](../getting-started/first-login.md).

## 2. Enter your club's details

1. In the sidebar, open **Administration → Settings**. The page is
   called **Club settings**.
2. In the **Club data** card, fill in **Club name**, **Street**,
   **Postal code**, **City**, **Club registration number** and
   **Register court**. The name appears in page titles; the rest goes
   into the footer of letters and invoices.
3. In **Board members**, search for and tick the members who are
   currently on the board. You can only pick people who already exist
   as members -- come back to this after step 9 or after your
   [import](csv-import.md).
4. Under **Areas (sqm)**, enter the **Total area (sqm)** of the
   grounds and the **Area C (municipal, sqm)** if you have one.
   **Area A (parcels, sqm)** and **Area B (communal, sqm)** are worked
   out by Parcella from your parcels.
5. Click **Save settings**. You see *"Settings saved."*

!!! tip
    The settings page is long. Use the **Search settings...** box at
    the top to jump to a field by name.

## 3. Add your logo

1. Still on **Administration → Settings**, find the **Branding** card.
2. Under **Club Logo**, choose a PNG, JPEG, WebP or SVG file of at most
   2 MB.
3. Click **Save settings**.

The logo replaces the Parcella logo on the login page and in the
sidebar. To go back to the default, tick **Remove logo (revert to the
default icon)** and save.

## 4. Choose language, region and currency

These are three separate settings on purpose: a club can use the
English interface but German number and address formats, for example.

1. **Language** -- the language of the whole installation. Every user
   sees the same one.
2. **Region** -- number and address format (thousands separator, order
   of postal code and city).
3. **Currency** -- the symbol and where it goes ("19,99 €" or
   "£19.99").
4. Click **Save settings**.

## 5. Set up outgoing email

Parcella sends invitations, notifications, announcements and invoices
by email. Without a mail server, invitations in step 9 can't be sent.

1. On **Administration → Settings**, find the **Email (SMTP)** card.
2. Fill in **SMTP server**, **SMTP port**, **SMTP user**, **SMTP
   password** and **Sender email** -- your mail provider tells you
   these values.
3. Click **Save settings**.

After saving, the password field only shows that a password is set; to
change it, type a new one.

## 6. Turn modules on and off

Not every club uses every feature area. Switching one off hides it from
the navigation; its data stays and comes back when you switch it on
again.

1. On **Administration → Settings**, find the **Feature areas** card.
2. Tick the modules your club uses and untick the rest. Each one has a
   short description underneath.
3. Click **Save settings**.

A few modules are **off** on a new installation because they send
data out or open something to the public: **Finances**,
**Announcements**, **Cloud storage**, **Support (helpdesk)**,
**Nextcloud Deck Sync**, **MCP connector for AI clients** and the three
public website APIs. Switch them on only once you need them.

More: [Turning modules on and off](../administration/modules.md).

## 7. Try things out with sample data (optional)

Before you enter real data, you can fill the empty installation with
made-up members, parcels, meters, work sessions and more, click around,
and remove all of it again.

1. Open **Administration → Sample data**.
2. Read **What this adds**, then click **Add sample data** and confirm.
3. Explore the modules. Try an invoice run, record a meter reading,
   hand over a parcel.
4. When you're done, go back to **Administration → Sample data** and
   click **Remove all sample data**, then confirm.

!!! warning "Remove the sample data before you start for real"
    - Sample data can only be **added** to a fresh installation. As soon
      as one real member or parcel exists, the button is blocked.
    - **Remove all sample data** deletes exactly what the generator
      created and nothing you typed in yourself. Anything you attach
      *to* a sample record while practising (a reading on a sample
      meter, a payment on a sample invoice) may not come out cleanly.
      Remove the sample data first, then enter your real data.
      <!-- TODO(verify): what happens on removal if a real record references a sample record (e.g. a finalized invoice run built from sample parcels)? -->
    - No user accounts are created or changed by sample data.

More: [Sample data](../administration/sample-data.md).

## 8. Create groups

New user accounts get their access from **groups**, not from a fixed
role. Create the groups first, then invite people into them.

1. Open **Administration → Groups**.
2. Under **Create group**, enter a **Name** (for example "Board") and a
   **Description**.
3. For the board, tick **Full access to every module**. Tick **Can
   access the administration panel** only for people who should also
   manage users and settings.
4. Click **Create group**.
5. For narrower jobs, create more groups and, in the permission table,
   tick **Read**, **Write** and **Delete** per **Module** -- for
   example "Water team" with read and write on **Water**, or
   "Treasurer" with full rights on **Finances**. Click **Save**.

!!! tip
    Everyone who can log in can always *look up* members and parcels.
    Groups widen access from there; they never take that away.

More: [Groups](../administration/groups.md) and
[Roles, groups and permissions](../getting-started/roles-and-permissions.md).

## 9. Invite the other board members

1. Open **Administration → Users** (the page is called **User
   management**).
2. In **Invite user**, enter the person's **Email address** and tick
   their **Groups**.
3. Click **Send invitation**.
4. The person gets an email with a link. On **Set up your account** they
   enter their **Name** and a **Password** (at least 8 characters) and
   click **Create account**.

The invitation is valid for 7 days and appears under **Pending
invitations** until it is accepted. From there you can **Resend
invitation** (which also extends it) or **Delete invitation**.

!!! warning
    The invitation goes out by email, so set up **Email (SMTP)** first
    (step 5). If it can't be sent, the page says so; fix the mail
    settings and use **Resend invitation**.

More: [Users and invitations](../administration/users.md).

## 10. Connect cloud storage (optional)

If your club keeps lease contracts and other paperwork in Nextcloud (or
another supported storage), Parcella can show a documents folder on each
parcel page.

1. Open **Administration → Integrations** and find **Cloud storage
   (parcel documents, invoices, backups)**.
2. Choose the **Storage type** and enter the connection details it
   asks for. Click **Save**, then **Test connection**.
3. Optionally set the shared folders further down: **Incoming invoices
   folder**, **Folder for external contacts' documents**, **Notes
   folder**, **Folder for process files**, **Folder for printed
   announcements**.
4. Go to **Administration → Settings → Feature areas**, tick **Cloud
   storage** and click **Save settings**.
5. On each parcel's page, set the **Folder path** in **Documents (cloud
   storage)** -- type it or use **Browse…** -- and click **Save**.

Paths are always relative to the storage you chose. Parcella doesn't
create or share the folders for you; do that in your cloud first.

More: [Integrations](../administration/integrations.md).

## 11. Enter or import your real data

Now add your parcels and members -- by hand under **Parcels → New
parcel** and **Members → New member**, or in one go from a spreadsheet:
see [Importing members and parcels](csv-import.md). Then assign each
member to their parcel (see [Welcoming a new member](new-member.md),
step 6).

## 12. Make your first backup

1. Open **Administration → Users** and find the **Backup** card.
2. Click **Download backup** and keep the zip file somewhere safe.

The backup contains the database, uploaded files and the encryption
key. Treat it like the member list itself.

More: [Backup and restore](../administration/backup.md).

## Related

- [Club settings](../administration/settings.md)
- [Turning modules on and off](../administration/modules.md)
- [Users and invitations](../administration/users.md)
- [Groups](../administration/groups.md)
- [Integrations](../administration/integrations.md)
- [Sample data](../administration/sample-data.md)
- [Backup and restore](../administration/backup.md)
- [Importing members and parcels](csv-import.md)
