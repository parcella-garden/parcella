"""Helpers shared by several work-hours sub-routers."""
from fastapi import Request
from app.i18n import DEFAULT_LANGUAGE


def _lang(request: Request) -> str:
    return getattr(request.state, "language", DEFAULT_LANGUAGE)
