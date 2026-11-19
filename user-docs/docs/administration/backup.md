# Backup and restore

A backup is a complete copy of your club's Parcella data in one file.
With it you can get everything back after a broken server, a mistake,
or a move to a new host. Make backups regularly, and keep them
somewhere other than the Parcella server.

!!! info "Who can use this"
    Administrators only. Everything starts from **Administration →
    System**.

## What a backup contains

One `.zip` file with:

- the whole database -- every member, parcel, reading, invoice, setting
  and user account,
- uploaded files kept inside Parcella: the logo, announcement images,
  avatars and process files,
- the key Parcella uses to encrypt stored passwords (mail server,
  website, cloud storage, helpdesk).

!!! warning "Treat a backup like a password"
    Because it contains that key and all your members' personal data,
    anyone with the file can read everything. Store it where only the
    board can get at it.

Files kept in your cloud storage (parcel folders, invoice attachments,
note files) are **not** part of the backup -- they already live in the
cloud, which has its own backup.

## Download a backup

On **Administration → System**, the card **Backup** has the button
**Download backup**. Your browser downloads the zip file straight away.
Nothing is stored on the server, so this file is the only copy: save
it somewhere safe.

If something goes wrong you see **Backup failed:** followed by the
reason.

## Restore from backup

![Restore from backup](../assets/screenshots/administration/backup-restore.png)

Open it with **Restore from backup** on the System page.

!!! danger "This overwrites all current data"
    Restoring replaces the **entire** database and all uploaded files
    with the contents of the backup. Everything entered since that
    backup is gone, including user accounts and passwords created
    since. This can't be undone. If you might want to go back, first
    **download a backup of the current state**.

| Field / button | What it does |
|---|---|
| **Backup file (.zip)** | Choose a backup file downloaded from Parcella (at most 200 MB). |
| **Type RESTORE to confirm** | Type the word `RESTORE` in capitals. This guards against restoring by accident. |
| **Cancel** | Back to the System page. |
| **Restore** | Asks once more, then restores. This can take a little while. |

Afterwards you see **Restore completed successfully.** Everybody --
you included -- is now working with the data as it was when the backup
was made; you may have to sign in again with the password valid back
then.

Possible messages:

| Message | Meaning |
|---|---|
| **Confirmation phrase did not match -- nothing was changed.** | The word wasn't exactly `RESTORE`. |
| **File is too large.** | Over 200 MB. |
| **The backup file has an unexpected structure: ...** | Not a Parcella backup, or a damaged file. Nothing was changed. |
| **Restore failed, nothing was changed: ...** | The database restore failed and your data is as before. |
| **Database restored successfully, but restoring uploaded files failed: ...** | The data is restored but some files aren't. Running the restore again is safe. |

Backups from an older Parcella version can be restored into a newer
one; the person who looks after the server may need to run the
database update afterwards.
<!-- TODO(verify): whether the app applies pending database migrations by itself after a restore of an older backup, or whether the server admin must always run them (developer docs say a restore doesn't run them). -->

## Cloud backups

![Cloud backups](../assets/screenshots/administration/backup-cloud.png)

Open it with **Cloud backups** on the System page. Parcella can make
the same backup automatically and upload it to your cloud storage.

This needs the **Cloud storage** module switched on and a storage set
up under [Integrations](integrations.md#cloud-storage). Otherwise the
page tells you what is missing, with a link.

### Schedule

| Field / button | What it does |
|---|---|
| **Automatically back up to the cloud** | Switches automatic backups on or off. |
| **Destination folder** | Folder in the cloud storage, e.g. `backups/parcella`. Created if it doesn't exist. Choose a folder only the board can open -- every backup contains the key to the stored passwords. |
| **Frequency** | **Hourly**, **Daily** (default), **Weekly** or **Monthly**. |
| **Keep this many backups** | How many backups to keep, at least 1 (default 10). When a new one is added, the oldest beyond this number are deleted. Only Parcella's own backup files are touched. |
| **Save** | Saves the schedule (**Saved.**). |
| **Back up to cloud now** | Makes and uploads a backup right away, whether or not automatic backups are on. |

Below the fields you see the result of the last run: **Last cloud
backup: ... (success).**, **... -- failed:** with the reason, or **No
cloud backup has run yet.** Check it now and then -- a backup that
silently fails for weeks is no backup.

### Backups in the cloud

A list of the backups in the destination folder, newest first, with
**Name**, **Size** and **Last modified**. **No backups in this folder
yet.** if there are none.

To restore one, type `RESTORE` into the field in its row and click
**Restore**. The same warning applies as above: it overwrites all
current data.

## Good practice

- Download a backup before big changes: an update, a large import, an
  invoice run.
- Keep at least one copy outside the cloud storage too, e.g. on an
  encrypted USB stick in the club's safe.
- Now and then, test a backup by restoring it on a spare test
  installation. A backup you have never restored is only a hope.

## Related

- [System information and updates](system.md)
- [Integrations](integrations.md#cloud-storage)
