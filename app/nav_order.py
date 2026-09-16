"""
Sidebar navigation ordering (issue #60): lets each club reorder its own
nav instead of living with a fixed, hardcoded sequence.

Concept:
- Every orderable nav entry has a key "nav_order_<name>" in the
  ClubSettings table, storing an integer position -- lower sorts first.
- NAV_ORDER_DEFAULTS below spaces the defaults by 100 (100, 200, 300, ...)
  so an admin can slot a new entry between two existing ones (e.g. 150)
  without renumbering everything else, matching the scheme the issue
  itself proposed.
- The default order matches the sidebar's pre-#60 fixed order, so an
  existing install sees no visual change until an admin deliberately
  reorders something.
- Loaded once per request in a middleware, same pattern as module flags
  (app/module_flags.py), and stored under request.state.nav_order -- a
  plain {key: int} dict. base.html sorts its nav-item macros by this
  instead of rendering them in source order.
- The Administration nav (system-admin only) is deliberately NOT part
  of this list: it isn't a club-configurable module, it's the fixed
  system area, and always renders last regardless of nav_order.

Adding a new orderable nav entry:
1. Entry in NAV_ORDER_DEFAULTS with the next free hundred.
2. Entry in NAV_ORDER_FIELDS (admin.py) for the settings page.
3. A `nav_<name>(request)` macro in base.html, dispatched from the
   ordered loop in the sidebar.
"""
from typing import Dict

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import ClubSetting

NAV_ORDER_DEFAULTS: Dict[str, int] = {
    "dashboard": 100,
    "members": 200,
    "parcels": 300,
    "freescout_bridge": 400,
    "purchase_requests": 500,
    "work_hours": 600,
    "water": 700,
    "electricity": 800,
    "insurance": 900,
    "calendar": 1000,
    "announcements": 1100,
    "inventory": 1200,
    "tasks": 1300,
    "finances": 1400,
}


async def load_nav_order(db: AsyncSession) -> Dict[str, int]:
    """Loads all nav-order values from the database, filled in with defaults."""
    result = await db.execute(
        select(ClubSetting).where(ClubSetting.key.like("nav_order_%"))
    )
    stored = {e.key: e.value for e in result.scalars().all()}

    order = dict(NAV_ORDER_DEFAULTS)
    for name in NAV_ORDER_DEFAULTS:
        value = stored.get(f"nav_order_{name}")
        if value is not None:
            try:
                order[name] = int(value)
            except ValueError:
                pass
    return order
