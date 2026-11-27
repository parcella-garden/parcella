"""Admin router: user management, invitations, club settings.

Split into one sub-router per area (issue #416, ADR 0146); they share
this router's prefix and module guard.
"""
from fastapi import APIRouter

from app.routers.admin import users, integrations, system, settings, api_tokens

router = APIRouter(prefix="/admin", tags=["admin"])

for _sub in (users, integrations, system, settings, api_tokens,):
    router.include_router(_sub.router)
