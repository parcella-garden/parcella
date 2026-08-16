"""
Module flags: showing/hiding optional feature areas.

Concept:
- Every optional module has a key "modul_<name>" in the ClubSettings
  table (e.g. "modul_work_hours").
- If the key is missing (e.g. on existing installations without an
  explicit setting), the default in MODULE_DEFAULTS applies
  (deliberately True, so existing users don't lose anything).
- The flags are loaded once per request in a middleware and stored
  under request.state.module_flags -- templates and router
  dependencies read from there without querying the DB again.

Adding a new module:
1. Entry in MODULE_DEFAULTS with a descriptive name and default value.
2. Entry in MODULE_FIELDS (admin.py) for the settings page.
3. Guard the router with `dependencies=[Depends(require_module("<name>"))]`.
4. Wrap the nav entry in base.html with `{% if request.state.module_flags.<name> %}`.
"""
from typing import Dict

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import ClubSetting

# Default state per module, if no explicit value is set in the DB.
# Deliberately True for existing modules, so an update doesn't "break" anything.
MODULE_DEFAULTS: Dict[str, bool] = {
    "work_hours": True,
    "water": True,
    "electricity": True,
    "insurance": True,
    "tickets": True,
    "purchase_requests": True,
    "calendar": True,
    "inventory": True,
    "tasks": True,
    # Unlike the modules above, this defaults to False: it opens a public,
    # unauthenticated-write HTTP endpoint (see app/routers/api_public.py),
    # which is a deliberate security-relevant choice a club must opt into,
    # not something that should silently turn on for existing installs.
    "public_signup_api": False,
    # Same reasoning, kept as its own separate flag rather than folded into
    # public_signup_api above: it opens a second, independent public write
    # endpoint (a contact-form-to-ticket bridge), and a club should be able
    # to enable one bridge without the other.
    "public_contact_api": False,
    # Also defaults to False: it stores outbound credentials (a
    # Nextcloud/cloud storage app password) and, once configured, lets
    # board members upload and download real member paperwork. A club
    # must opt in deliberately rather than have this silently available.
    "cloud_storage": False,
    # Also defaults to False, for the same reason: it stores outbound
    # credentials (WordPress application password) and, once used, can
    # send an email to every member with email_info=True. A club should
    # opt in deliberately rather than have this silently available.
    "announcements": False,
    # Also defaults to False: it handles member financial data and sends
    # bulk documents (annual invoices, see docs/ADR and issue #55) --
    # a club must opt in deliberately, same reasoning as cloud_storage/
    # announcements above.
    "finances": False,
}


def _value_to_bool(value: str) -> bool:
    return value.strip().lower() in ("true", "1", "ja", "an")


async def load_module_flags(db: AsyncSession) -> Dict[str, bool]:
    """Loads all module flags from the database, filled in with defaults."""
    result = await db.execute(
        select(ClubSetting).where(ClubSetting.key.like("modul_%"))
    )
    stored = {e.key: e.value for e in result.scalars().all()}

    flags = dict(MODULE_DEFAULTS)
    for name in MODULE_DEFAULTS:
        value = stored.get(f"modul_{name}")
        if value is not None:
            flags[name] = _value_to_bool(value)
    return flags


def require_module(module_name: str):
    """
    Dependency factory for routers: locks every endpoint of a router if
    the module is disabled. Reads from request.state.module_flags (set
    by the middleware), does NOT query the database again.
    """

    async def checker(request: Request):
        flags = getattr(request.state, "module_flags", {})
        if not flags.get(module_name, MODULE_DEFAULTS.get(module_name, True)):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dieser Funktionsbereich ist in diesem Verein deaktiviert.",
            )

    return checker
