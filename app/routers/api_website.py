"""
API router: website connectors (ADR 0104) -- which CMS the announcements
module's website channel sends drafts to (shared settings endpoints, see
app/routers/api_provider_settings.py), plus creating/updating an
announcement's website draft.

Creating a draft needs full access, like the "Create website draft"
button.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api_auth import require_api_full_access
from app.database import get_db
from app.models import User
from app.module_flags import require_module
from app.routers.announcements import _get_announcement_or_404, push_website_draft
from app.routers.api_provider_settings import create_provider_settings_router
from app.schemas import WebsiteDraftOut
from app.website_connectors import BlogPublishError
from app.website_connectors.registry import WEBSITE

router = create_provider_settings_router(
    WEBSITE, prefix="/api/v1/website", tag="API: Website", types_path="connectors", errors=(BlogPublishError,),
)


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
