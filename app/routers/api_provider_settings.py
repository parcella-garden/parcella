"""
REST API for a "one dropdown, one provider at a time" integration
(app/provider_registry.py): list the provider types and their fields,
read and set the active one, and test it. Used for the website (ADR
0104) and cloud storage (ADR 0106).

ADMIN only, matching Admin -> Integrations being system-admin-only on
the web side. Secrets are never accepted or returned (same rule as
/api/v1/club-settings): they can only be entered on the admin page.
"""
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api_auth import require_api_role
from app.database import get_db
from app.i18n import t_for
from app.models import User, UserRole
from app.provider_registry import InvalidConnectorConfig, ProviderRegistry
from app.schemas import (
    ProviderFieldOut, ProviderSettingsOut, ProviderSettingsUpdate, ProviderTestResult, ProviderTypeOut,
)

require_api_system_admin = require_api_role(UserRole.ADMIN)


def create_provider_settings_router(
    registry: ProviderRegistry, *, prefix: str, tag: str, types_path: str, errors: tuple,
) -> APIRouter:
    router = APIRouter(prefix=prefix, tags=[tag])

    async def _settings(db: AsyncSession) -> ProviderSettingsOut:
        values, secrets_set = {}, {}
        for provider_type, cls in registry.providers.items():
            stored = await registry.load_stored_values(db, provider_type)
            values[provider_type] = {f.key: stored.get(f.key) for f in cls.config_fields if f.kind != "secret"}
            secrets_set[provider_type] = {f.key: bool(stored.get(f.key)) for f in cls.config_fields if f.kind == "secret"}
        return ProviderSettingsOut(active=await registry.get_active_type(db), values=values, secrets_set=secrets_set)

    @router.get(f"/{types_path}", response_model=list[ProviderTypeOut], summary=f"Available {registry.label} types")
    async def provider_types(request: Request, user: User = Depends(require_api_system_admin)):
        prefix_ = registry.i18n_prefix
        return [
            ProviderTypeOut(
                type=provider_type,
                name=t_for(request, f"{prefix_}.{provider_type}.name"),
                description=t_for(request, f"{prefix_}.{provider_type}.desc"),
                fields=[
                    ProviderFieldOut(
                        key=f.key, kind=f.kind, required=f.required, default=f.default,
                        label=t_for(request, f"{prefix_}.{provider_type}.fields.{f.key}"),
                    )
                    for f in cls.config_fields
                ],
            )
            for provider_type, cls in registry.providers.items()
        ]

    @router.get("", response_model=ProviderSettingsOut, summary=f"Active {registry.label} and its settings")
    async def provider_settings(db: AsyncSession = Depends(get_db), user: User = Depends(require_api_system_admin)):
        return await _settings(db)

    @router.put("", response_model=ProviderSettingsOut, summary=f"Choose the active {registry.label} and set its fields")
    async def provider_settings_update(
        data: ProviderSettingsUpdate, db: AsyncSession = Depends(get_db),
        user: User = Depends(require_api_system_admin),
    ):
        if data.active is not None and data.active not in registry.providers:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Unknown type {data.active!r}")
        if data.active is not None:
            secret_keys = {f.key for f in registry.providers[data.active].config_fields if f.kind == "secret"}
            if secret_keys & {k for k, v in data.values.items() if v}:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Credentials and tokens can only be set on the admin pages",
                )
        try:
            await registry.save_config(db, data.active, data.values if data.active else {}, allow_secrets=False)
        except InvalidConnectorConfig as e:
            await db.rollback()
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
        await db.commit()
        return await _settings(db)

    @router.post("/test", response_model=ProviderTestResult, summary=f"Test the active {registry.label}'s saved settings")
    async def provider_test(db: AsyncSession = Depends(get_db), user: User = Depends(require_api_system_admin)):
        provider_type = await registry.get_active_type(db)
        if provider_type is None:
            return ProviderTestResult(ok=False, message="Nothing is set up.")
        config = await registry.load_config(db, provider_type)
        if config is None:
            return ProviderTestResult(ok=False, message="Required fields are missing.")
        provider = None
        try:
            provider = await registry.build(db, provider_type, config)
            await provider.test_connection()
            return ProviderTestResult(ok=True)
        except errors as e:
            return ProviderTestResult(ok=False, message=str(e))
        finally:
            if provider is not None:
                await provider.aclose()

    return router
