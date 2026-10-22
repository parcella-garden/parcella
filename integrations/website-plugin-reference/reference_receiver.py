#!/usr/bin/env python3
"""
Reference receiver for the Parcella Website Plugin Protocol v1
(docs/website-plugin-protocol.md). Standard library only, on purpose:
it's meant to be read and translated into a CMS plugin (PHP for TYPO3,
Contao, Drupal, Joomla, ...), not deployed.

It keeps drafts in a JSON file instead of a CMS database. Run it, point
a "Parcella plugin" website in Parcella at it, and create a draft from an
announcement to see the whole round trip.

    PARCELLA_SHARED_SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))") \\
        python3 reference_receiver.py 8091

Endpoint URL to enter in Parcella: http://<host>:8091/parcella/v1
"""
import hashlib
import hmac
import json
import os
import sys
import time
import uuid
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

PROTOCOL = "parcella-website/1"
BASE_PATH = "/parcella/v1"
MAX_CLOCK_SKEW_SECONDS = 300
MAX_BODY_BYTES = 10 * 1024 * 1024

SECRET = os.environ.get("PARCELLA_SHARED_SECRET", "")
STORE = Path(os.environ.get("REFERENCE_STORE", "reference_drafts.json"))


def load_store() -> dict:
    return json.loads(STORE.read_text()) if STORE.exists() else {}


def save_store(drafts: dict) -> None:
    STORE.write_text(json.dumps(drafts, indent=2, ensure_ascii=False))


def signature_is_valid(timestamp: str, method: str, path: str, body: bytes, provided: str) -> bool:
    try:
        if abs(int(timestamp) - time.time()) > MAX_CLOCK_SKEW_SECONDS:
            return False
    except ValueError:
        return False
    message = f"{timestamp}\n{method}\n{path}\n".encode("utf-8") + body
    expected = "sha256=" + hmac.new(SECRET.encode("utf-8"), message, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, provided or "")


def public_draft(draft_id: str, draft: dict) -> dict:
    # A real plugin returns the CMS's own edit link here.
    return {"id": draft_id, "edit_url": None}


class Handler(BaseHTTPRequestHandler):
    def _respond(self, status: int, body: dict) -> None:
        data = json.dumps(body).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _authenticated_body(self):
        """The request body if the signature checks out, else None (a
        401 has then already been sent)."""
        length = int(self.headers.get("Content-Length") or 0)
        if length > MAX_BODY_BYTES:
            self._respond(413, {"error": "too large"})
            return None
        body = self.rfile.read(length) if length else b""
        path = self.path.split("?", 1)[0]
        if not signature_is_valid(
            self.headers.get("X-Parcella-Timestamp", ""), self.command, path, body,
            self.headers.get("X-Parcella-Signature", ""),
        ):
            self._respond(401, {"error": "unauthorized"})
            return None
        return body

    def _route(self):
        path = self.path.split("?", 1)[0]
        if not path.startswith(BASE_PATH + "/"):
            return None, None
        parts = path[len(BASE_PATH) + 1:].split("/")
        return parts[0], (parts[1] if len(parts) > 1 else None)

    def do_GET(self):
        resource, draft_id = self._route()
        if resource is None:
            return self._respond(404, {"error": "not found"})
        if self._authenticated_body() is None:
            return
        if resource == "ping":
            return self._respond(200, {"protocol": PROTOCOL, "name": "Parcella reference receiver", "version": "1.0.0"})
        if resource == "drafts" and draft_id:
            draft = load_store().get(draft_id)
            if draft is None:
                return self._respond(404, {"error": "not found"})
            return self._respond(200, {"status": draft["status"], "public_url": draft.get("public_url")})
        self._respond(404, {"error": "not found"})

    def do_POST(self):
        resource, draft_id = self._route()
        if resource != "drafts" or draft_id:
            return self._respond(404, {"error": "not found"})
        body = self._authenticated_body()
        if body is None:
            return
        payload = json.loads(body)
        drafts = load_store()
        # Idempotent on source_id: a retried request returns the same draft.
        for existing_id, draft in drafts.items():
            if payload.get("source_id") and draft.get("source_id") == payload["source_id"]:
                return self._respond(201, public_draft(existing_id, draft))
        new_id = uuid.uuid4().hex[:12]
        drafts[new_id] = {
            "status": "draft",  # always unpublished -- a human publishes in the CMS
            "title": payload["title"], "markdown": payload["markdown"], "html": payload["html"],
            "source_id": payload.get("source_id"), "image": payload.get("image"),
        }
        save_store(drafts)
        self._respond(201, public_draft(new_id, drafts[new_id]))

    def do_PUT(self):
        resource, draft_id = self._route()
        if resource != "drafts" or not draft_id:
            return self._respond(404, {"error": "not found"})
        body = self._authenticated_body()
        if body is None:
            return
        payload = json.loads(body)
        drafts = load_store()
        draft = drafts.get(draft_id)
        if draft is None:
            return self._respond(404, {"error": "not found"})
        draft.update(title=payload["title"], markdown=payload["markdown"], html=payload["html"])
        if "image" in payload:  # absent = unchanged, null = remove, object = replace
            draft["image"] = payload["image"]
        # draft["status"] is deliberately left alone.
        save_store(drafts)
        self._respond(200, public_draft(draft_id, draft))

    def log_message(self, format, *args):
        sys.stderr.write("%s - %s\n" % (self.command, self.path))


if __name__ == "__main__":
    if len(SECRET) < 32:
        sys.exit("Set PARCELLA_SHARED_SECRET to at least 32 characters (see the docstring).")
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8091
    print(f"Reference receiver on http://0.0.0.0:{port}{BASE_PATH} (drafts in {STORE})")
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()
