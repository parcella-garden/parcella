# Administration

The administration area is where your installation of Parcella is set
up and looked after: who may log in, what they may do, the club's
master data, connections to other services, and backups.

!!! info "Who can use this"
    Only **administrators**: accounts with the older **Administrator**
    role, or in a group with **Can access the administration panel**.
    Board members with full access to the modules don't see it unless
    they are also administrators. See
    [Roles, groups and permissions](../getting-started/roles-and-permissions.md).

You find it at the bottom of the sidebar under **Administration**.

## The pages

| Sidebar entry | Page | What you do there |
|---|---|---|
| **System** | [System information and updates](system.md) | See your version and whether an update exists; download a backup. |
| | [Backup and restore](backup.md) | Restore from a backup; schedule automatic backups to the cloud. |
| **Users** | [Users and invitations](users.md) | Invite people, edit, deactivate and delete accounts, reset passwords. |
| **Groups** | [Groups](groups.md) | Decide who may read, write and delete what. |
| **API tokens** | [API tokens](api-tokens.md) | See and revoke everybody's tokens; create tokens for integration accounts. |
| **Settings** | [Club settings](settings.md) | Club name and address, logo, language, region and currency, e-mail server, finance details, navigation order and more. |
| | [Turning modules on and off](modules.md) | The **Feature areas** card on the settings page. |
| **Integrations** | [Integrations](integrations.md) | Website forms, website drafts, cloud storage, helpdesk, Nextcloud Deck, calendar feed links. |
| **Email log** | [E-mail log](email-log.md) | Check whether an e-mail went out. |
| **Sample data** | [Sample data](sample-data.md) | Fill a fresh installation with demo data to try things out, and remove it again. |
| **API Documentation (Swagger)** | -- | The technical description of the programming interface, for developers. |

## Setting up a new installation

A sensible order for a brand-new installation:

1. Sign in with the built-in administrator account and change its
   password -- see [First login](../getting-started/first-login.md#the-very-first-login-after-installation).
2. Under [Club settings](settings.md): language, region and currency,
   club data, logo, and the e-mail server (without it Parcella can't
   send invitations).
3. Under [Turning modules on and off](modules.md): switch off what you
   don't need, switch on what you do.
4. Create [groups](groups.md) for the jobs in your club.
5. [Invite](users.md) the other board members into those groups.
6. Set up [backups](backup.md).

The task guide [Setting up a new club](../guides/new-club-setup.md)
walks through this together with entering members and parcels.

Installing Parcella itself (the server, Docker, the web address) is
described in the
[developer documentation](https://github.com/parcella-garden/parcella#install-self-hosting).
