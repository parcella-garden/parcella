"""Users, API tokens, invitations, groups and their permissions."""

import enum
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Integer, Boolean, DateTime, Text, ForeignKey, Enum as SAEnum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base
from app.models._common import new_uuid


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    BOARD = "board"
    TREASURER = "treasurer"
    READONLY = "readonly"


class InvitationStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    EXPIRED = "expired"


# ---------------------------------------------------------------------------
# System users (app users, not club members)
# ---------------------------------------------------------------------------

class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole), default=UserRole.READONLY, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    # Set on the bootstrap admin created at first startup (app/main.py),
    # whose password is the documented, identical-everywhere default. As
    # long as it's True the account can't use the app: the web UI
    # redirects every page to /auth/change-password and the REST API
    # refuses to issue a token. Cleared by a successful password change.
    must_change_password: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false", nullable=False
    )
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    # Baked into the session cookie (app/auth.py); bumping it ends every
    # session issued before -- done on a password change, so a stolen
    # cookie dies with the old password (security audit 2026-10-19).
    session_version: Mapped[int] = mapped_column(Integer, default=0, server_default="0", nullable=False)
    # Just the filename under app/static/uploads/avatars/, not the image
    # itself -- same "store filename, not URL" convention as ClubSetting's
    # logo_filename (app/branding.py). See app/avatars.py.
    avatar_filename: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    invitations: Mapped[List["Invitation"]] = relationship("Invitation", back_populates="invited_by")

    def __repr__(self) -> str:
        return f"<User {self.email} ({self.role})>"


class ApiToken(Base):
    """A personal API token (issue #306, ADR 0126): long-lived, revocable,
    for integrations such as the MCP connector (#307) that can't log in
    with a password every day.

    Only the SHA-256 of the token is stored; the token itself is shown
    once, on creation. It acts with exactly its user's permissions --
    there are no scopes; a narrower token means a narrower user.

    `session_version` is the user's session_version when the token was
    made. A password change or an admin password reset bumps the user's
    value, which ends every token issued before, the same way it ends the
    session cookies. Revoking sets `revoked_at` (historization, ADR 0005);
    the row stays so the list shows what existed and when it was used.
    """
    __tablename__ = "api_tokens"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    # The first characters of the token, to tell tokens apart in the list.
    token_prefix: Mapped[str] = mapped_column(String(16), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    session_version: Mapped[int] = mapped_column(Integer, nullable=False)
    created_by_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    # Issue #307 (ADR 0132, the one exception to "no scopes"): an
    # MCP-only token works ONLY on the MCP endpoint, which shows notes
    # released for AI and nothing else. The REST API rejects it, so an AI
    # client's token can't read unreleased notes through GET /api/v1/notes.
    # The MCP endpoint accepts nothing but these.
    mcp_only: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")

    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])
    created_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[created_by_id])


class Invitation(Base):
    __tablename__ = "invitations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    token: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole), default=UserRole.READONLY, nullable=False
    )
    status: Mapped[InvitationStatus] = mapped_column(
        SAEnum(InvitationStatus), default=InvitationStatus.PENDING, nullable=False
    )
    invited_by_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    invited_by: Mapped[Optional["User"]] = relationship("User", back_populates="invitations")
    target_groups: Mapped[List["InvitationGroupTarget"]] = relationship(
        "InvitationGroupTarget", back_populates="invitation", cascade="all, delete-orphan"
    )


# ---------------------------------------------------------------------------
# Groups: a simple ACL layer governing what TREASURER/READONLY users can
# read/write/delete per module. ADMIN/BOARD always bypass this entirely
# (unchanged from their existing behavior) -- see app/permissions.py for
# the module list and permission-check helpers, and ADR 0038 for why.
#
# grants_full_access / grants_system_admin (ADR 0041): a group can now
# ALSO grant the same effective access a role used to be the only way
# to get -- full module access, and/or the admin panel -- so new users
# are assigned to groups instead of a role. This is additive: ADMIN and
# BOARD roles keep working exactly as before for whoever already has
# them (the seeded bootstrap Administrator account above all).
# ---------------------------------------------------------------------------

class Group(Base):
    """
    A named group of users (e.g. "Work Hours Coordinators"). A user can
    belong to several groups at once (see GroupMembership); their
    effective permission on a module is the most permissive value
    across every group they're in (see app/permissions.py).
    """
    __tablename__ = "groups"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    grants_full_access: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    grants_system_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    permissions: Mapped[List["GroupModulePermission"]] = relationship(
        "GroupModulePermission", back_populates="group", cascade="all, delete-orphan"
    )
    memberships: Mapped[List["GroupMembership"]] = relationship(
        "GroupMembership", back_populates="group", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Group {self.name!r}>"


class GroupMembership(Base):
    """A user's membership in a group (m:n -- see Group docstring)."""
    __tablename__ = "group_memberships"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    group_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("groups.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship("User")
    group: Mapped["Group"] = relationship("Group", back_populates="memberships")

    __table_args__ = (
        UniqueConstraint("user_id", "group_id", name="uq_group_membership"),
    )


class InvitationGroupTarget(Base):
    """Which group(s) a pending invitation will place the user into once
    accepted (see routers/auth.py's accept-invitation route) -- mirrors
    GroupMembership's shape exactly, just for an Invitation instead of
    a User. ADR 0041: invites assign groups now, not a role."""
    __tablename__ = "invitation_group_targets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    invitation_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("invitations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    group_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("groups.id", ondelete="CASCADE"), nullable=False, index=True
    )

    invitation: Mapped["Invitation"] = relationship("Invitation", back_populates="target_groups")
    group: Mapped["Group"] = relationship("Group")

    __table_args__ = (
        UniqueConstraint("invitation_id", "group_id", name="uq_invitation_group_target"),
    )


class GroupModulePermission(Base):
    """
    What a group can do in one module: read, write, delete -- each
    independent (a group could in principle have delete without write,
    though the admin UI doesn't offer that combination since it isn't
    a meaningful real-world scenario). `module` is a key from
    app/permissions.py's MODULES list, not a DB-enforced enum, so
    adding a new governed module never needs a migration.
    """
    __tablename__ = "group_module_permissions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    group_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("groups.id", ondelete="CASCADE"), nullable=False, index=True
    )
    module: Mapped[str] = mapped_column(String(50), nullable=False)
    can_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    can_write: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    can_delete: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    group: Mapped["Group"] = relationship("Group", back_populates="permissions")

    __table_args__ = (
        UniqueConstraint("group_id", "module", name="uq_group_module_permission"),
    )
