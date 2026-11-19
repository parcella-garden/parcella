# API tokens

An API token is a key that lets another program use Parcella on
someone's behalf, without their password -- for example a script that
exports data, or an AI assistant that reads the club's notes. Most
clubs never need one.

!!! info "Who can use this"
    Every user can manage **their own** tokens: **Change password** in
    the sidebar → **API tokens for integrations** → **Manage**
    (page **My API tokens**). Administrators also see **everybody's**
    tokens under **Administration → API tokens**.

![API tokens](../assets/screenshots/administration/api-tokens.png)

## How a token behaves

- It acts **with exactly the permissions of the account it belongs
  to**. A token of a meter reader can only do what the meter reader
  can do.
- It is shown **only once**, right after it is created. Copy it then;
  it can't be looked up later.
- It stops working when it expires, when it is revoked, or when the
  account's password is changed or reset. Deactivating the account
  stops it too.

Treat a token like a password. If it may have leaked, revoke it.

## New token

| Field / button | What it does |
|---|---|
| **User** | *Administrators' page only.* Whose account the token acts as. You can create tokens for yourself and for accounts **without** full access -- typically a dedicated account for an integration that never logs in itself. Tokens for other full-access accounts aren't possible, because a token would act silently in that person's name. |
| **Name** | Required, up to 100 characters. Say what it is for, e.g. "Claude knowledge base". |
| **Expires** | **after 30 days**, **after 90 days**, **after 365 days** (default) or **never**. Prefer an expiry. |
| **MCP connector only (for an AI client)** | Only shown when the **MCP connector for AI clients** module is on. Such a token works only for the AI connection and only with notes released for AI; every other use is refused. Always use this kind for an AI assistant. |
| **Create token** | Creates the token and shows it in a green box: *Copy it now: it is shown only this once ...* |

## The token list

| Column / button | What it shows or does |
|---|---|
| **Name** | The name, the first characters of the token (to recognise it), and a badge **MCP only** where applicable. |
| **User** | *Administrators' page only.* Whose token it is. |
| **Created** | Date created. |
| **Last used** | When a program last used it, or **never**. |
| **Expires** | Expiry date or **never**. |
| **Status** | **active**, **expired**, **revoked**, or **ended** (the password was changed after the token was created). |
| **Revoke** | Only for active tokens. After confirming, the token stops working immediately. |

**No API tokens yet.** appears when there are none.

## Connecting an AI assistant to the notes

With the **MCP connector for AI clients** module, an AI assistant such
as Claude can search and read -- and if you allow it, write -- the
[notes](../modules/notes.md) you have released for it, and nothing
else. In short:

1. Switch on **MCP connector for AI clients** (and **Notes**) under
   [Turning modules on and off](modules.md).
2. [Invite](users.md) a separate account for the assistant and put it
   in a [group](groups.md) that grants only **Notes** read (and write,
   if wanted).
3. Here, create a token for that account with **MCP connector only**
   ticked.
4. Release notes for the AI by giving them the release tag described
   in the notes chapter.

Only release notes that contain no personal data: they go to an
outside AI service. The step-by-step setup for each AI client is in the
[MCP setup guide](https://github.com/parcella-garden/parcella/blob/main/docs/mcp-setup.md).

## For developers

The REST API itself -- endpoints, authentication, examples -- is
described in the
[developer documentation](https://github.com/parcella-garden/parcella#rest-api),
and interactively under **Administration → API Documentation
(Swagger)**.

## Related

- [First login and your account](../getting-started/first-login.md#change-password)
- [Users and invitations](users.md)
