"""
API router: which cloud storage Parcella uses (ADR 0106) -- the shared
"one provider at a time" settings endpoints, see
app/routers/api_provider_settings.py.
"""
from app.cloud_storage import CLOUD_STORAGE, CloudStorageError
from app.routers.api_provider_settings import create_provider_settings_router

router = create_provider_settings_router(
    CLOUD_STORAGE, prefix="/api/v1/cloud-storage", tag="API: Cloud storage", types_path="providers",
    errors=(CloudStorageError,),
)
