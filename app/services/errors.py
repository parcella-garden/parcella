"""
Shared exception type for app/services/* business-rule violations.

Formalizes the (translation_key, params) shape app/meter_utils.py's
check_monotonicity() already used informally into one reusable type.
A service raises this instead of an HTTPException directly, so it stays
framework-agnostic (no FastAPI/Jinja2 concerns) -- each router (HTML or
API) resolves the message via its own means (t_for(request, ...) for
both, since request_context_middleware runs for API requests too) and applies
its own status-code convention (HTML: 400, API: 422 -- deliberately not
unified, see ADR 0070).
"""
from typing import Any, Dict


class ServiceError(Exception):
    def __init__(self, key: str, http_status: int = 400, **params: Any):
        self.key = key
        self.params: Dict[str, Any] = params
        self.http_status = http_status
        super().__init__(key)
