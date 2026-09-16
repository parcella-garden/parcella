"""
Group-based permission matrix. ADMIN and BOARD always bypass this
entirely and get full read/write/delete on every module (see
app/auth.py's require_admin) -- the administration panel itself is a
separate, narrower check (require_system_admin, ADMIN only). Everyone
else (TREASURER/READONLY) starts from a small baseline -- read-only on
members_parcels, nothing else -- and a group narrowly WIDENS that,
e.g. "handles work-hours sessions but shouldn't be able to edit the
member list." See ADR 0039.

Deliberately does NOT cover: tasks, announcements, cloud_storage,
public_signup_api, or the admin section itself. All of those are
already admin/board-only (see app/module_flags.py's off-by-default
modules and ADR 0034 for tasks) and stay that way regardless of group
configuration -- this system only ever widens what a TREASURER/READONLY
user can do beyond the baseline, it never touches anything currently
locked to admin/board. Also out of scope for this pass: the REST API
(app/api_auth.py) -- a separate JWT-based role system with its own
require_write_access, untouched here. See ADR 0038.

is_system_admin_user / is_full_access_user (ADR 0041): a Group can now
ALSO grant the same effective access a role used to be the only way to
get -- full module access (Group.grants_full_access, today's BOARD)
and/or the admin panel (Group.grants_system_admin, today's ADMIN).
Additive, not a replacement: ADMIN/BOARD roles keep working exactly as
before for whoever already has them. New users are assigned to groups
instead of a role going forward.
"""
from typing import Dict, Optional

from fastapi import HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import ColumnElement

from app.i18n import t_for

from app.models import Group, GroupModulePermission, GroupMembership, User, UserRole

MODULES = [
    "members_parcels", "work_hours", "water", "electricity",
    "insurance", "purchase_requests", "calendar", "inventory",
    "finances", "freescout_bridge",
]

_EMPTY_PERMISSION = {"read": False, "write": False, "delete": False}
_FULL_PERMISSION = {"read": True, "write": True, "delete": True}


async def _member_of_group_with_flag(db: AsyncSession, user_id: str, flag_column: ColumnElement) -> bool:
    result = await db.execute(
        select(Group.id)
        .join(GroupMembership, GroupMembership.group_id == Group.id)
        .where(GroupMembership.user_id == user_id, flag_column == True)  # noqa: E712
        .limit(1)
    )
    return result.scalar_one_or_none() is not None


async def is_system_admin_user(db: AsyncSession, user: Optional[User]) -> bool:
    """True for the bootstrap/legacy ADMIN role, or membership in a
    grants_system_admin group (ADR 0041) -- reaches the admin panel."""
    if user is None:
        return False
    if user.role == UserRole.ADMIN:
        return True
    return await _member_of_group_with_flag(db, user.id, Group.grants_system_admin)


async def is_full_access_user(db: AsyncSession, user: Optional[User]) -> bool:
    """True for ADMIN/BOARD roles, or membership in a grants_full_access
    group -- or grants_system_admin, which implies full module access
    too (ADR 0041)."""
    if user is None:
        return False
    if user.role in (UserRole.ADMIN, UserRole.BOARD):
        return True
    if await is_system_admin_user(db, user):
        return True
    return await _member_of_group_with_flag(db, user.id, Group.grants_full_access)


async def is_last_admin(db: AsyncSession, user_id: str) -> bool:
    """True if no other active account -- via ADMIN role, or membership
    in a grants_system_admin group (ADR 0041) -- exists besides
    `user_id` that can reach require_system_admin (the admin panel).
    Used by app/routers/admin.py (deactivating/editing/deleting a user)
    and app/routers/admin_groups.py (removing the last member of a
    grants_system_admin group) -- with at least one such account left,
    they can always fix any other access problem via the panel
    BOARD-equivalent access can't reach."""
    role_based = await db.execute(
        select(User.id)
        .where(User.id != user_id, User.is_active == True, User.role == UserRole.ADMIN)  # noqa: E712
        .limit(1)
    )
    if role_based.scalar_one_or_none() is not None:
        return False

    group_based = await db.execute(
        select(User.id)
        .join(GroupMembership, GroupMembership.user_id == User.id)
        .join(Group, Group.id == GroupMembership.group_id)
        .where(User.id != user_id, User.is_active == True, Group.grants_system_admin == True)  # noqa: E712
        .limit(1)
    )
    return group_based.scalar_one_or_none() is None


async def get_user_permissions(db: AsyncSession, user: Optional[User]) -> Dict[str, Dict[str, bool]]:
    """
    Effective read/write/delete per module for `user`. ADMIN/BOARD (or
    an equivalent grants_full_access/grants_system_admin group) get
    full access to every module unconditionally. Anyone else: union
    across every group they belong to (most permissive group wins per
    module, per permission level).
    """
    if user is None:
        return {module: dict(_EMPTY_PERMISSION) for module in MODULES}
    if await is_full_access_user(db, user):
        return {module: dict(_FULL_PERMISSION) for module in MODULES}

    permissions = {module: dict(_EMPTY_PERMISSION) for module in MODULES}
    if "members_parcels" in permissions:
        permissions["members_parcels"]["read"] = True  # baseline: everyone can look up who's who / which parcel

    result = await db.execute(
        select(GroupModulePermission)
        .join(GroupMembership, GroupMembership.group_id == GroupModulePermission.group_id)
        .where(GroupMembership.user_id == user.id)
    )
    for row in result.scalars().all():
        if row.module not in permissions:
            continue  # a module removed from MODULES since this row was created
        p = permissions[row.module]
        p["read"] = p["read"] or row.can_read
        p["write"] = p["write"] or row.can_write
        p["delete"] = p["delete"] or row.can_delete
    return permissions


def has_permission(permissions: Dict[str, Dict[str, bool]], module: str, level: str) -> bool:
    return permissions.get(module, {}).get(level, False)


async def require_permission(request: Request, db: AsyncSession, module: str, level: str) -> User:
    """
    Same calling convention as require_user/require_admin in app/auth.py
    -- call inline as the first line of a route body, e.g.
    `user = await require_permission(request, db, "members_parcels", "write")`.
    Reads the per-request cache the permissions_middleware already
    computed (see app/main.py) instead of re-querying when possible.
    """
    from app.auth import require_user  # local import: auth.py doesn't need to know about permissions.py

    user = await require_user(request, db)
    permissions = getattr(request.state, "permissions", None)
    if permissions is None:
        permissions = await get_user_permissions(db, user)
    if not has_permission(permissions, module, level):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=t_for(request, "errors.no_permission"))
    return user


def jinja_has_perm(request: Request, module: str, level: str = "read") -> bool:
    """Jinja global (see app/templating.py): `{% if has_perm(request, 'work_hours') %}`."""
    permissions = getattr(request.state, "permissions", {})
    return has_permission(permissions, module, level)


def jinja_is_full_access(request: Request) -> bool:
    """Jinja global: `{% if is_full_access(request) %}` -- true for
    ADMIN/BOARD role or an equivalent grants_full_access group (ADR 0041).
    Reads the per-request cache permissions_middleware computed."""
    return bool(getattr(request.state, "is_full_access", False))


def jinja_is_system_admin(request: Request) -> bool:
    """Jinja global: `{% if is_system_admin(request) %}` -- true for
    ADMIN role or an equivalent grants_system_admin group (ADR 0041).
    Reads the per-request cache permissions_middleware computed."""
    return bool(getattr(request.state, "is_system_admin", False))
