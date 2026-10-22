# Cloud storage: one dropdown, one provider at a time

**Context:** Cloud storage was built behind a `CloudStorageProvider`
interface from the start (ADR 0033), but only `NextcloudProvider`
existed, every feature asked for `get_nextcloud_provider()`, and the
settings were three `nextcloud_*` keys on a Nextcloud-only card. Clubs
without a Nextcloud could not use parcel folders, invoice storage,
contact documents, cloud backups or the Markdown website at all. After
the website got its one-CMS dropdown (ADR 0104), kermie asked for the
same behaviour wherever a provider was hard-wired.

## Decision

1. **The same pattern as the website, sharing its code.** The
   registry from ADR 0104 moved into `app/provider_registry.py`
   (`ProviderRegistry`, `ConfigField`, value validation, encrypted
   secrets, "blank secret = keep"). The website and cloud storage are
   two instances of it, so are their admin cards
   (`admin/_provider_form.html`), their save/test routes, and their REST
   settings endpoints (`app/routers/api_provider_settings.py`). The
   helpdesk will be the third.

2. **Three backends:**
   - **WebDAV**, generic, because it covers the most hosted offerings
     clubs actually use (ownCloud, Seafile, Strato HiDrive, Hetzner
     Storage Box, MagentaCLOUD).
   - **Nextcloud**, now a thin `WebDAVProvider` subclass that only knows
     the per-user root URL. The folder-listing parser no longer relies
     on Nextcloud's `/remote.php/dav/` path; it compares decoded URL
     paths, which works for any server.
   - **S3-compatible**, path-style, SigV4 signed with the standard
     library instead of a new dependency (boto3/aiobotocore would pull in
     a large tree for five calls). The signer is tested against AWS's
     documented example, and the provider was checked live against a
     signature-verifying SeaweedFS server.

3. **Folders on S3:** S3 has only key prefixes. `create_folder` writes an
   empty `<folder>/` marker (as most S3 tools do), and a prefix with
   neither marker nor content raises "folder not found", so every
   feature keeps the WebDAV semantics it was built on ("the folder must
   already exist").

4. **Migration 0106** renames `nextcloud_*` to `cloud_storage_nextcloud_*`
   without touching the values and makes Nextcloud active if it was
   configured. Nextcloud Deck sync keeps its separate `deck_*` settings
   on purpose (ADR 0086): it's a task-board integration, not storage.

## Not done

- **Google Drive, OneDrive, Dropbox:** they need an OAuth consent flow
  and token refresh instead of stored credentials. The interface doesn't
  prevent them, but the admin card would need a "Connect" button and a
  callback route. That's its own piece of work.
- **Several storages at once:** one active storage keeps every stored
  folder path unambiguous. Switching storage does not move any files.
