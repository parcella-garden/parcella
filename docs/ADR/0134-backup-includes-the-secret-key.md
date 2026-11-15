# The backup includes the encryption key; a restore re-encrypts

**Context:** issue #327. A Docker install keeps everything under `./data/`:
`postgres/` (the database files), `uploads/` and `secrets/secret_key`. kermie
expects the whole folder to be in Parcella's backups. The backup zip already
held the database (as a `pg_dump`) and all of `uploads/`, but left out the
key on purpose (ADR 0121, docs/operations.md): it decrypts the
SMTP/website/cloud passwords stored in the same zip, and cloud backups end up
in a Nextcloud folder. Without the key, a restore on a new server left those
passwords unreadable and they had to be typed in again.

## Decision

- **The zip mirrors `./data/`** (kermie's call after a first version kept the
  old flat names): `data/postgres/parcella.sql`, `data/uploads/…`,
  `data/secrets/secret_key`. Restore accepts this layout and the older flat
  one (top-level `*.sql`, `uploads/`, `secrets/secret_key`), so existing
  backups stay restorable.
- **Every backup carries the key in use** as `data/secrets/secret_key`: the manual
  download and the scheduled cloud backups alike (kermie's call, over an
  opt-in checkbox and over leaving it out). It's the effective key, whether it
  came from `.env` or from `data/secrets/secret_key`.
- **`data/postgres/` holds a dump, not the raw files.** The web container that
  builds the backup can't see the database container's files, and copying a
  running database's files gives an inconsistent copy; the `pg_dump` is the
  safe form of the same data.
- **A restore doesn't switch keys, it re-encrypts.** If the zip's key differs
  from the running instance's, the restored settings that decrypt with the
  backup's key are re-encrypted with the instance's own key
  (`secret_bootstrap.rekey_database` with an `old_key`, the same code that
  moves installs off the public default key). So:
  - no restart: the key is read at startup, so swapping it would only take
    effect later and leave a window with unreadable settings;
  - nobody is logged out (sessions are signed with the key);
  - a key set in `.env` keeps winning, as everywhere else.
  If re-encrypting fails, the restore reports it rather than claiming success.
- **The UI says what the zip holds.** The download text and the cloud-backup
  folder field now say that a backup contains the key to the stored
  passwords, so the file and the folder need the same care as those
  passwords.

## Consequences

- Whoever gets a backup zip can read the stored SMTP/website/cloud
  passwords. Before, they could read the members' personal data in the
  dump, but not those passwords. Accepted: the zip was already highly
  sensitive, and a backup that can't be restored on a new server without
  re-entering credentials is a worse failure for a small club.
- The restore validation accepts exactly one key member (either layout), at
  most 1 KB of text, and exactly one dump directly in `data/postgres/` (or at
  the top level in the old layout). Older zips without a key restore as
  before.
- Supersedes the "deliberately not part of the backup" note on the key in
  ADR 0121 and docs/operations.md.
