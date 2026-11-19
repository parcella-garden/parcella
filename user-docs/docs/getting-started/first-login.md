# First login and your account

This page covers everything about your own account: how you get one,
how you sign in, and how you change your password and picture.

!!! info "Who can use this"
    Everyone with a Parcella account. There is no public sign-up: an
    account only exists after an administrator has invited you.

## Getting an account: the invitation

An administrator of your installation invites you by e-mail (see
[Users and invitations](../administration/users.md)). You receive an
e-mail with the subject **Invitation to Parcella** and a button
**Accept invitation**. The link in it is valid for **7 days**.

!!! tip "No e-mail arrived?"
    Look in your spam folder first. If it isn't there, ask the
    administrator to check the [E-mail log](../administration/email-log.md)
    and, if needed, to resend the invitation. Resending gives the link
    another 7 days; the link in the first e-mail keeps working.

### Accept invitation

<!-- TODO(verify): no screenshot of "Set up your account" -- it needs a valid invitation link, which the screenshot tool can't produce from the sample data. -->

Clicking the link opens the page **Set up your account**. Below the
heading you see the address the invitation was sent to
(**Invitation for** ...). That address becomes your login; you can't
change it here.

| Field / button | What it does |
|---|---|
| **Name** | Your first and last name. Other board members see it in lists, on tasks, approvals and the change history. |
| **Password** | At least 8 characters. |
| **Confirm password** | Type the same password again. If the two don't match you see **Passwords do not match.** |
| **Create account** | Creates your account and signs you in straight away. You land on the [Dashboard](dashboard.md). |

What you can see afterwards depends on the groups the administrator
picked when inviting you. If they picked none, you can only look up
members and parcels -- ask them to add you to a group. See
[Roles, groups and permissions](roles-and-permissions.md).

### Invitation expired

![Invitation expired](../assets/screenshots/getting-started/invitation-expired.png)

You see **Invitation expired** -- *This invitation link is no longer
valid or has already been used.* -- when:

- more than 7 days have passed since the invitation was sent (or last
  resent),
- you already created your account with this link, or
- the administrator deleted the invitation, or invited the same
  address again (only the newest invitation works).

Ask an administrator to invite you again. **Back to login** takes you
to the sign-in page, which only helps if you already have an account.

## Signing in

![Sign-in page](../assets/screenshots/getting-started/login.png)

Open your club's Parcella address in a web browser. The sign-in page
shows your club's logo and name (both set by an administrator under
[Club settings](../administration/settings.md)).

| Field / button | What it does |
|---|---|
| **Email** | The address your invitation was sent to. Upper and lower case don't matter. |
| **Password** | Your password. |
| **Sign in** | Signs you in and opens the [Dashboard](dashboard.md). |

The messages you may see:

| Message | Meaning |
|---|---|
| **Email or password is incorrect.** | One of the two is wrong. For your protection Parcella doesn't say which. |
| **Your account has been deactivated.** | An administrator has switched your account off. Your data is still there; ask them to activate it again. |
| **Too many failed login attempts. Please wait a few minutes and try again.** | After repeated wrong passwords Parcella pauses sign-in attempts for this account for about 15 minutes. |

You stay signed in for **8 hours** (unless whoever hosts your
installation has changed that). After that Parcella asks you to sign in
again, even if you were working the whole time.

To sign out, click **Log Out** at the bottom of the sidebar. Do this
on any shared or public computer.

!!! note "Forgot your password?"
    There is no "forgot password" link, on purpose. Ask an
    administrator: they can reset your password and give you a
    temporary one (see
    [Users and invitations](../administration/users.md#reset-password)).
    You then have to choose a new password at your next sign-in.

## The very first login after installation

When Parcella starts for the first time, it creates one administrator
account by itself:

- **Email:** `admin@parcella.local`
- **Password:** `admin1234`

These details are published in Parcella's installation instructions and
are the same on every new installation, so anybody could use them.
That's why this account is locked until its password is changed: after
signing in you land directly on **Change password**, with the notice

> This account still uses the default password from the initial setup.
> Please choose a new one -- the rest of the application stays locked
> until you do.

Every other page sends you back here until you have saved a new
password.

!!! warning "Do this before anything else"
    Change the password immediately, even on a test installation that
    is reachable from the internet. Then, under
    [Users and invitations](../administration/users.md), change the
    account's name and e-mail address to a real person's, or invite
    the real administrators and work with their own accounts.

The same forced change happens after an administrator has reset your
password: the temporary password only gets you to the **Change
password** page.

## Change password

![Change password](../assets/screenshots/getting-started/change-password.png)

Open it with **Change password** at the bottom of the sidebar. The
page is your personal profile: it also holds your avatar and a link to
your API tokens.

### Avatar

Your avatar is the small round picture shown next to your name in the
sidebar, in user lists and on tasks. Without one, Parcella shows a
plain person icon.

| Field / button | What it does |
|---|---|
| File field | Choose a picture: PNG, JPEG or WebP, at most 2 MB. |
| **Upload** | Saves the picture. You see **Avatar uploaded successfully.** A wrong file type or a too-large file is rejected with a message. |
| **Remove avatar** | Only shown when you have one. Removes it again. |

### API tokens for integrations

**Manage** opens **My API tokens**. You only need this if you want to
connect another program (for example an AI assistant) to Parcella. See
[API tokens](../administration/api-tokens.md).

### Changing the password

| Field / button | What it does |
|---|---|
| **Current password** | Your present password, so nobody can change it on a computer you left signed in. |
| **New password** | At least 8 characters, and different from the current one. |
| **Confirm new password** | The new password again. |
| **Change password** | Saves the new password. You see **Password changed successfully.** |

Possible errors: **Current password is incorrect.**, **Passwords do not
match.**, **Password must be at least 8 characters.** and **The new
password must be different from the current one.**

What happens when you save:

- You stay signed in in this browser.
- **Every other place you were signed in is signed out** -- another
  computer, your phone, or a browser someone else is using with your
  account. Use this if you suspect someone knows your password.
- All your **API tokens stop working** (they show as **ended**). Create
  new ones if you still need them.

## Language

Parcella shows the same language to everybody in your club. There is
no language switch for individual users. An administrator chooses the
language under [Club settings](../administration/settings.md#language)
-- English, Deutsch, Polski, Čeština, Slovenčina, Français or
Nederlands. The sign-in page and the invitation pages use that language
too.

Number, date and currency formats are a separate setting (**Region**
and **Currency**), so a club can, for example, use English menus with
German number formats.

## Related

- [Finding your way around](navigation.md)
- [Roles, groups and permissions](roles-and-permissions.md)
- [Users and invitations](../administration/users.md) -- for administrators
