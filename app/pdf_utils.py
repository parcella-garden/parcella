"""
Small shared helper for the two PDF generators in this codebase
(app.print_publisher for announcement flyers, app.meeting_signin_sheet
for the general-meeting sign-in sheet). Both embed local images (the
club logo, an announcement's header image) as base64 data URIs rather
than filesystem paths or HTTP URLs, so PDF rendering doesn't depend on
WeasyPrint resolving relative paths correctly or on the app being able
to reach its own HTTP server to fetch its own uploaded files.
"""
import base64
from pathlib import Path
from typing import Optional

from weasyprint import URLFetcher

IMAGE_MIME_BY_EXTENSION = {
    ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp",
}


def image_mime_for(path: Path) -> str:
    return IMAGE_MIME_BY_EXTENSION.get(path.suffix.lower(), "application/octet-stream")


def file_to_data_uri(path: Optional[Path], mime: Optional[str] = None) -> Optional[str]:
    """Reads a local file and returns it as a data: URI, or None if the
    path is missing/doesn't exist. mime is inferred from the file
    extension if not given."""
    if path is None or not path.exists():
        return None
    resolved_mime = mime or image_mime_for(path)
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{resolved_mime};base64,{encoded}"



def data_uri_only_fetcher() -> URLFetcher:
    """url_fetcher for every WeasyPrint render: everything the app puts
    into a PDF is a data: URI (see file_to_data_uri), so anything else
    can only come from user-written HTML -- an announcement's
    <img src="http://..."> would otherwise make the server fetch
    arbitrary URLs, internal ones included (blind SSRF, security audit
    2026-10-19). WeasyPrint logs the refusal and skips the resource."""
    return URLFetcher(allowed_protocols=["data"])
