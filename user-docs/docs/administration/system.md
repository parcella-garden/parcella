# System information and updates

The System page shows which version of Parcella you are running,
whether a newer one is available, and is the starting point for
backups.

!!! info "Who can use this"
    Administrators only. Open **Administration → System**.

![System](../assets/screenshots/administration/system.png)

## Update notice

Parcella regularly asks GitHub, where it is published, whether a newer
version has been released. Nothing about your club is sent. You can
switch this off under
[Club settings → Updates](settings.md#updates); the update notice then
disappears from this page.

**When you're up to date** you see

> Running v1.2.3 -- up to date (last checked 18.11.2026 14:05)

or **... not checked for updates yet** right after installation.

**When a newer version exists** a highlighted box shows **Update
available:** with the new version number, the version you are running,
and the four commands that install the update on the server.

| Button | What it does |
|---|---|
| **Check now** | Asks GitHub right away instead of waiting for the next automatic check (every six hours). |

!!! note "Updating is done on the server"
    The update itself isn't a button in Parcella. Whoever runs the
    server types the commands shown in the box. Pass them on if that
    isn't you. Download a [backup](backup.md) first.

    The box also warns that the first command replaces the server's
    configuration file with the current one. Changes the server admin
    made to that file are lost unless they keep them in a separate
    override file, as the installation instructions explain.

Read the release notes on GitHub before updating, to see what has
changed.

## Backup

The **Backup** card has three buttons:

| Button | What it does |
|---|---|
| **Cloud backups** | Opens the schedule for automatic backups to your cloud storage. |
| **Restore from backup** | Opens the restore page. |
| **Download backup** | Downloads a complete backup right away. |

All three are described in [Backup and restore](backup.md).

## Related

- [Backup and restore](backup.md)
- [Club settings](settings.md#updates)
