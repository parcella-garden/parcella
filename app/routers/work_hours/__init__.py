"""Work hours router: work sessions, sponsorships, club roles, configuration.

Split into one sub-router per area (issue #416, ADR 0146); they share
this router's prefix and module guard.
"""
from fastapi import APIRouter, Depends
from app.module_flags import require_module

from app.routers.work_hours import configuration, sessions, club_roles, sponsorships, transfers, evaluation, tasks

router = APIRouter(
    prefix="/work-hours",
    tags=["work-hours"],
    dependencies=[Depends(require_module("work_hours"))],
)

for _sub in (configuration, sessions, club_roles, sponsorships, transfers, evaluation, tasks,):
    router.include_router(_sub.router)
