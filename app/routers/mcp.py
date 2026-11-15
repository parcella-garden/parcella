"""
MCP endpoint for the notes knowledge base (issue #307, ADR 0132).

A deliberately small, hand-written MCP server: JSON-RPC 2.0 over the
"Streamable HTTP" transport, stateless, answering every POST with a
plain JSON response (no SSE stream, no sessions) -- which the spec
allows, and which keeps the whole surface in this one file instead of a
framework dependency. The tools and the "released for AI only" rule
live in app/services/notes_mcp.py.

Authentication: `Authorization: Bearer pct_...` with an MCP-only API
token (ADR 0132). Ordinary tokens are refused here, MCP-only tokens are
refused everywhere else. The token's user also needs the notes module's
read (and, for create/update, write) permission. Off unless the club
enables the `mcp` module.
"""
import json
import logging
from typing import Any, Dict, Optional
from urllib.parse import urlsplit

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.module_flags import require_module
from app.permissions import get_user_permissions, has_permission
from app.services import api_tokens
from app.services.notes_mcp import TOOLS, McpToolError, call_tool

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/mcp",
    tags=["mcp"],
    dependencies=[Depends(require_module("mcp")), Depends(require_module("notes"))],
)

SUPPORTED_PROTOCOL_VERSIONS = ("2025-06-18", "2025-03-26")
MAX_BODY_BYTES = 1_000_000

INSTRUCTIONS = (
    "Knowledge base of a garden club. You only see notes that people released for AI. "
    "Answer with sources: name the note's title and date. Never write personal data "
    "(member names, parcel numbers, contact details) into notes. Notes you create or "
    "change are marked for human review. There is no delete."
)


def _rpc_error(request_id: Any, code: int, message: str, status_code: int = 200) -> JSONResponse:
    return JSONResponse(
        {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}},
        status_code=status_code,
    )


def _rpc_result(request_id: Any, result: Dict[str, Any]) -> JSONResponse:
    return JSONResponse({"jsonrpc": "2.0", "id": request_id, "result": result})


def _unauthorized() -> JSONResponse:
    return JSONResponse(
        {"error": "Invalid or missing MCP token"}, status_code=401,
        headers={"WWW-Authenticate": 'Bearer realm="parcella-mcp"'},
    )


def _origin_ok(request: Request) -> bool:
    """DNS-rebinding protection the MCP spec asks for: a browser sending
    an Origin must be this server itself. Non-browser clients send none."""
    origin = request.headers.get("origin")
    if not origin:
        return True
    host = urlsplit(origin).netloc.lower()
    return host == (request.headers.get("host") or "").lower()


@router.get("")
async def mcp_get() -> Response:
    # No server-to-client SSE stream (stateless server, see module docstring).
    return Response(status_code=405, headers={"Allow": "POST"})


@router.post("")
async def mcp_post(request: Request, db: AsyncSession = Depends(get_db)) -> Response:
    if not _origin_ok(request):
        return JSONResponse({"error": "Origin not allowed"}, status_code=403)

    auth = request.headers.get("authorization") or ""
    raw = auth[7:].strip() if auth.lower().startswith("bearer ") else ""
    user = await api_tokens.authenticate(db, raw, mcp=True) if raw else None
    if user is None:
        return _unauthorized()
    permissions = await get_user_permissions(db, user)
    if not has_permission(permissions, "notes", "read"):
        return JSONResponse({"error": "This token's user may not read notes"}, status_code=403)

    body = await request.body()
    if len(body) > MAX_BODY_BYTES:
        return _rpc_error(None, -32600, "Request too large", status_code=413)
    try:
        message = json.loads(body)
    except ValueError:
        return _rpc_error(None, -32700, "Parse error", status_code=400)
    if not isinstance(message, dict) or message.get("jsonrpc") != "2.0" or not isinstance(message.get("method"), str):
        # Batches (a JSON array) were dropped from the protocol in 2025-06-18.
        return _rpc_error(None, -32600, "Invalid request", status_code=400)

    method: str = message["method"]
    request_id = message.get("id")
    params = message.get("params") or {}
    if not isinstance(params, dict):
        return _rpc_error(request_id, -32602, "Invalid params")

    # Notifications (no id) and responses get 202 and no body.
    if "id" not in message:
        return Response(status_code=202)

    if method == "initialize":
        requested = params.get("protocolVersion")
        version = requested if requested in SUPPORTED_PROTOCOL_VERSIONS else SUPPORTED_PROTOCOL_VERSIONS[0]
        return _rpc_result(request_id, {
            "protocolVersion": version,
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": {"name": "parcella-notes", "title": "Parcella notes", "version": settings.app_version},
            "instructions": INSTRUCTIONS,
        })
    if method == "ping":
        return _rpc_result(request_id, {})
    if method == "tools/list":
        can_write = has_permission(permissions, "notes", "write")
        tools = [
            {
                "name": name, "description": spec["description"], "inputSchema": spec["inputSchema"],
                "annotations": {"readOnlyHint": spec["read_only"], "destructiveHint": False},
            }
            for name, spec in TOOLS.items() if spec["read_only"] or can_write
        ]
        return _rpc_result(request_id, {"tools": tools})
    if method == "tools/call":
        name = params.get("name")
        args = params.get("arguments") or {}
        if not isinstance(name, str) or name not in TOOLS or not isinstance(args, dict):
            return _rpc_error(request_id, -32602, "Unknown tool or invalid arguments")
        if not TOOLS[name]["read_only"] and not has_permission(permissions, "notes", "write"):
            return _rpc_result(request_id, _tool_error("This token's user may not change notes."))
        try:
            result = await call_tool(db, name, args, user)
        except McpToolError as e:
            return _rpc_result(request_id, _tool_error(str(e)))
        except Exception:
            logger.exception("MCP tool %s failed", name)
            await db.rollback()
            return _rpc_result(request_id, _tool_error("Internal error."))
        return _rpc_result(request_id, {
            "content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}],
            "structuredContent": result,
            "isError": False,
        })
    return _rpc_error(request_id, -32601, "Method not found")


def _tool_error(message: str) -> Dict[str, Any]:
    return {"content": [{"type": "text", "text": message}], "isError": True}
