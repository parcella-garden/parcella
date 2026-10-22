"""
API router: website connectors (ADR 0104) -- which CMS the announcements
module's website channel sends drafts to, plus creating/updating an
announcement's website draft.

Configuring the connector is ADMIN-only, matching Admin -> Integrations
being system-admin-only on the web side. Secrets are write-only on the
web page and never accepted or returned here (same rule as
/api/v1/club-settings). Creating a draft needs full access, like the
"Create website draft" button.
"""
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api_auth import require_api_full_access, require_api_role
from app.database import get_db
from app.i18n import t_for
from app.models import User, UserRole
from app.module_flags import require_module
from app.routers.announcements import _get_announcement_or_404, push_website_draft
from app.schemas import (
    WebsiteConnectorFieldOut, WebsiteConnectorTypeOut, WebsiteDraftOut, WebsiteSettingsOut,
    WebsiteSettingsUpdate, WebsiteTestResult,
)
from app.website_connectors import BlogPublishError, CONNECTORS, InvalidConnectorConfig, get_active_type
from app.website_connectors.registry import build_connector, load_config, load_stored_values, save_config

router = APIRouter(prefix="/api/v1/website", tags=["API: Website"])

require_api_system_admin = require_api_role(UserRole.ADMIN)


@router.get("/connectors", response_model=list[WebsiteConnectorTypeOut], summary="Available website types")
async def website_connectors(request: Request, user: User = Depends(require_api_system_admin)):
    return [
        WebsiteConnectorTypeOut(
            type=connector_type,
            name=t_for(request, f"website.connectors.{connector_type}.name"),
            description=t_for(request, f"website.connectors.{connector_type}.desc"),
            fields=[
                WebsiteConnectorFieldOut(
                    key=f.key, kind=f.kind, required=f.required, default=f.default,
                    label=t_for(request, f"website.connectors.{connector_type}.fields.{f.key}"),
                )
                for f in cls.config_fields
            ],
        )
        for connector_type, cls in CONNECTORS.items()
    ]


@router.get("", response_model=WebsiteSettingsOut, summary="Active website and its settings")
async def website_settings(db: AsyncSession = Depends(get_db), user: User = Depends(require_api_system_admin)):
    values, secrets_set = {}, {}
    for connector_type, cls in CONNECTORS.items():
        stored = await load_stored_values(db, connector_type)
        values[connector_type] = {f.key: stored.get(f.key) for f in cls.config_fields if f.kind != "secret"}
        secrets_set[connector_type] = {f.key: bool(stored.get(f.key)) for f in cls.config_fields if f.kind == "secret"}
    return WebsiteSettingsOut(active=await get_active_type(db), values=values, secrets_set=secrets_set)


@router.put("", response_model=WebsiteSettingsOut, summary="Choose the active website and set its fields")
async def website_settings_update(
    data: WebsiteSettingsUpdate, db: AsyncSession = Depends(get_db),
    user: User = Depends(require_api_system_admin),
):
    if data.active is not None and data.active not in CONNECTORS:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Unknown website type {data.active!r}")
    if data.active is not None:
        secret_keys = {f.key for f in CONNECTORS[data.active].config_fields if f.kind == "secret"}
        if secret_keys & {k for k, v in data.values.items() if v}:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Credentials and tokens can only be set on the admin pages",
            )
    try:
        await save_config(db, data.active, data.values if data.active else {}, allow_secrets=False)
    except InvalidConnectorConfig as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    await db.commit()
    return await website_settings(db, user)


@router.post("/test", response_model=WebsiteTestResult, summary="Test the active website's saved settings")
async def website_test(db: AsyncSession = Depends(get_db), user: User = Depends(require_api_system_admin)):
    connector_type = await get_active_type(db)
    if connector_type is None:
        return WebsiteTestResult(ok=False, message="No website is set up.")
    config = await load_config(db, connector_type)
    if config is None:
        return WebsiteTestResult(ok=False, message="Required fields are missing.")
    connector = None
    try:
        connector = await build_connector(db, connector_type, config)
        await connector.test_connection()
        return WebsiteTestResult(ok=True)
    except BlogPublishError as e:
        return WebsiteTestResult(ok=False, message=str(e))
    finally:
        if connector is not None:
            await connector.aclose()


announcement_router = APIRouter(
    prefix="/api/v1/announcements",
    tags=["API: Website"],
    dependencies=[Depends(require_module("announcements"))],
)


@announcement_router.post(
    "/{announcement_id}/website-draft", response_model=WebsiteDraftOut,
    summary="Create or update the announcement's website draft",
)
async def announcement_website_draft(
    announcement_id: str, db: AsyncSession = Depends(get_db), user: User = Depends(require_api_full_access),
):
    announcement = await _get_announcement_or_404(db, announcement_id)
    delivery = await push_website_draft(db, announcement)
    return WebsiteDraftOut(
        status=delivery.status.value, external_id=delivery.external_id,
        external_reference=delivery.external_reference, error_message=delivery.error_message,
    )
