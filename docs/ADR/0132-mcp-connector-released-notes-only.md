# MCP connector: released notes only, MCP-only tokens, hand-written server

**Context:** issue #307 (step 3 of #285). An external AI client (Claude,
ChatGPT, any MCP client) should search, read and write the club's notes.
Hard rule (kermie, 2026-11-08): **no personal data goes to any AI.**
Notes contain member names, parcel numbers and private matters.

## Decision

- **Deny by default: the AI sees only notes released with a tag**
  (ClubSetting `mcp_release_tag`, default `ki-freigegeben`). Since ADR
  0127 tags live in Parcella, not in the file. Every tool starts from
  one filter (`_released()` in `app/services/notes_mcp.py`):
  - search never matches an unreleased note;
  - by id, an unreleased note gets the same "not found" as a
    non-existent one;
  - the category and tag lists only show terms used on released notes;
  - naming a hidden category is answered like an unknown one;
  - **the AI can only attach tags it can already see**, matched by exact
    base name. The notes service's own lookup would also match tag
    *translations* across all tags, so a translation of a tag used
    only on unreleased notes would attach that tag and reveal its base
    name (security review finding). Any other name gets one refusal,
    whether it exists or not, so the refusal can't be used to probe.
    New tags are made by people.
- **What goes out is minimal:** title, date, category, tags, body,
  source, plus the note id and an opaque version for the conflict
  check. No author/user fields, no cloud file name, no member or
  parcel ids.
- **Notes the AI creates or changes get `ki-erstellt`** (`mcp_created_tag`)
  so people see what to review. The release tag can't be dropped through
  MCP. There is **no delete tool** (kermie): mistakes are undone via the
  cloud's file versions. `update_note` uses the notes service's conflict
  check.
- **MCP-only tokens (amends ADR 0126's "no scopes", by exactly this
  one exception).** An ordinary API token of the AI user would also
  open `GET /api/v1/notes`, i.e. every unreleased note. So
  `ApiToken.mcp_only`:
  - such a token works only on `/api/v1/mcp`;
  - every other API route treats it like an unknown token (401);
  - the MCP endpoint accepts nothing else;
  - a test walks every parameterless GET route under `/api/v1` with
    the AI's token.
- **The AI account is a dedicated user** in a group with notes
  read/write only. The endpoint checks the notes permission, and
  read-only users get no write tools.
- **Module flag `mcp`, off by default:** it hands club data to a third
  party. A club opts in deliberately.
- **A small hand-written server rather than the MCP SDK:**
  - JSON-RPC 2.0 over Streamable HTTP, stateless, and every POST
    answered with plain JSON (allowed by the spec);
  - GET answers 405 (no SSE stream);
  - batches are rejected (dropped from the protocol in 2025-06-18);
  - a browser `Origin` must match the host (DNS-rebinding protection,
    as the spec asks).

  About 200 lines in one file are easier to review than a framework
  dependency, and the server needs nothing beyond tools.
- **No name redaction.** It can't be done reliably, so it would only
  give a false sense of safety. Whoever releases a note is responsible
  for its content; the release is a deliberate act (adding a tag).

## Clients

- **Claude** (claude.ai custom connector, Claude Desktop, Claude Code)
  can send a fixed `Authorization: Bearer` header, so it works with an
  MCP-only token as is (docs/mcp-setup.md).
- **ChatGPT** connectors (developer mode) support only OAuth or no
  authentication, as of 2026-11. "No authentication" is not an option
  for club data, so ChatGPT needs an OAuth authorization server on top
  of the tokens. That's a follow-up, as the issue foresaw.

## Rejected

- **A flag on the AI user instead of on the token.** kermie chose the
  token type.
- **Releasing per category or folder.** It's too coarse: one meeting
  folder mixes public and private notes.
- **The official `mcp` Python SDK.** It's a dependency and a framework
  for capabilities (sessions, SSE, resources, prompts) this endpoint
  doesn't need.
