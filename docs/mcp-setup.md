# Connecting an AI client to the notes (MCP)

Parcella offers the notes knowledge base to AI clients through the
Model Context Protocol (issue #307, ADR 0132). The AI sees **only notes
released for it** and never anything else in Parcella.

## 1. In Parcella (an administrator)

1. **Admin → Settings → Modules:** switch on "MCP connector for AI
   clients" (off by default). The notes module must be on too.
2. **Create the AI's own user**, e.g. "KI-Assistent", and a group that
   grants **notes read/write and nothing else**. Leave out write if the
   AI should only read. Put the user in that group.
3. **Admin → API tokens:** create a token for that user and tick **"MCP
   connector only"**. Copy it; it's shown once. This token works on the
   MCP endpoint only, so even if it leaks it can't read anything else.
4. **Release notes for the AI** by giving them the tag
   **`ki-freigegeben`**. Check the content first: whoever releases a
   note is responsible that it holds no personal data. There's no
   automatic redaction. Notes the AI writes get `ki-erstellt` as well;
   review those.

The tag names can be changed with the club settings `mcp_release_tag`
and `mcp_created_tag` (`PUT /api/v1/club-settings/<key>`).

Endpoint: `https://<your-parcella>/api/v1/mcp`, with the header
`Authorization: Bearer <token>`.

## 2a. Claude

- **claude.ai** (Settings → Connectors → Add custom connector): URL as
  above. Leave OAuth empty, and under **Request headers** add
  `Authorization` = `Bearer <token>`. Claude sends it on every request.
  Connector settings can't be edited later: to change the token, remove
  the connector and add it again.
- **Claude Code:**

  ```bash
  claude mcp add --transport http parcella https://<your-parcella>/api/v1/mcp \
    --header "Authorization: Bearer <token>"
  ```

## 2b. ChatGPT

ChatGPT's connectors (developer mode) only offer OAuth or no
authentication, as of 2026-11. "No authentication" is not acceptable
for club data, so ChatGPT can't connect yet. That needs an OAuth layer,
which is a follow-up.

## What the AI can do

- `search_notes`
- `get_note`
- `list_categories`
- `list_tags`
- `create_note`
- `update_note`

There is no delete. Mistakes are undone through the cloud folder's
file versions.

Typical uses:
- Answer questions with the note's title and date as the source.
- Open a bookmark note's `source` URL itself, summarise the page, and
  write the summary into the note. Parcella never fetches external
  pages.

## Prompt injection

Web pages the AI reads can contain hidden instructions. The narrow
token (notes only), the release tag and the missing delete tool limit
what such an instruction could do. Review `ki-erstellt` notes anyway.
