# External contacts' documents: one picked subfolder of a shared cloud base folder

**Context:** Letters, offers, contracts and invoices exchanged with an
external contact (ADR 0096) already live in the club's Nextcloud, under
`kgv_dokumente/extern`, with one folder per institution. The board wants
to see and add those documents from the contact's page. The folders are
created by hand in the cloud.

**Decision:**

- **One club-wide base folder plus one picked subfolder per contact.**
  The base folder is a `ClubSetting` (`external_contacts_cloud_folder`),
  set on the admin integrations page next to the incoming-invoices
  folder. `ExternalContact.cloud_folder` stores only the subfolder's
  name. A writer picks it from a dropdown of the folders that actually
  exist in the base folder (one PROPFIND), so there are no typos and no
  paths outside the base folder. It also follows the project's
  preference for one global setting over per-object overrides, so
  moving the base folder later is a one-field change. Unlike parcel folders
  (`ParcelCloudFolder`), there's no history table: a contact doesn't
  change hands the way a parcel does, so there's nothing a new owner
  must not inherit.
- **Not auto-matched by company name.** Folder names and company names
  drift ("Gartenbau Müller" vs. "Müller GmbH"), and a silent mismatch
  would hide documents. Optional names (migration 0098) would leave
  nothing to match on anyway.
- **Received vs. sent is the club's own folder structure.** The card
  browses whatever subfolders exist inside the contact's folder (e.g.
  `Eingang`/`Ausgang`), and an upload goes into the folder being viewed.
  No fixed subfolder names are imposed.
- **Contacts permissions, not admin-only.** Read lists and downloads;
  write picks the folder and uploads. This differs from parcel
  documents (full access only), which hold members' personal
  paperwork. Contact documents are club business correspondence, and
  the module already has its own permission row. Deleting or moving
  files stays in the cloud, like everywhere else in Parcella (ADR 0033).
- **Backend-agnostic.** Everything goes through `CloudStorageProvider`
  (`app/contact_documents.py`, `app/routers/external_contacts.py`).
  Nothing uses Nextcloud-only features such as share links or the
  viewer, so another backend could be swapped in later.

**Safety:**

- The subfolder name is a single path segment
  (`sanitize_folder_name`).
- The browse path drops `..` (`sanitize_browse_subpath`).
- An uploaded file's client-side directory part is stripped
  (`upload_filename`).
- `_join_dav_path` still rejects `..` defensively.
- The download's `Content-Disposition` uses a percent-encoded
  `filename*`, so a cloud file name with CR/LF or quotes can't inject
  headers (CLAUDE.md, ticket attachments).

**Consequences:** If a folder is renamed in the cloud, the contact's
link breaks: the card shows the cloud error until someone re-picks the
folder. That's accepted as the price of not storing paths that move by
themselves.
