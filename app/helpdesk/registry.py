"""
Which helpdesk is active (ADR 0107) -- one at a time, through the shared
ProviderRegistry (app/provider_registry.py): the ClubSetting
`helpdesk_provider` holds the type, fields live in
`helpdesk_<type>_<field>`.

Adding a helpdesk: a HelpdeskProvider subclass in app/helpdesk/, one
entry below, and its `helpdesk.providers.<type>.*` translations.
"""
from typing import FrozenSet, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.helpdesk.base import HelpdeskProvider
from app.helpdesk.freescout import FreeScoutProvider
from app.helpdesk.freshdesk import FreshdeskProvider
from app.helpdesk.osticket import OsTicketProvider
from app.helpdesk.zammad import ZammadProvider
from app.helpdesk.zendesk import ZendeskProvider
from app.helpdesk.znuny import ZnunyProvider
from app.models import ClubSetting
from app.provider_registry import ProviderRegistry

HELPDESK = ProviderRegistry(
    active_key="helpdesk_provider", setting_prefix="helpdesk", i18n_prefix="helpdesk.providers",
    providers=(FreeScoutProvider, ZammadProvider, ZnunyProvider, OsTicketProvider, ZendeskProvider, FreshdeskProvider),
    label="helpdesk",
)


async def get_helpdesk(db: AsyncSession) -> Optional[HelpdeskProvider]:
    """The active, fully configured helpdesk, or None if none is set up --
    callers check for None (and for the capability they need) rather
    than catching an exception for "not set up"."""
    return await HELPDESK.get_active(db)


async def get_active_helpdesk_type(db: AsyncSession) -> Optional[str]:
    return await HELPDESK.get_active_type(db)


async def active_capabilities(db: AsyncSession) -> FrozenSet[str]:
    """What the active helpdesk can do, without building a client."""
    cls = HELPDESK.get_class(await HELPDESK.get_active_type(db))
    return cls.capabilities if cls else frozenset()


async def load_helpdesk_web_url(db: AsyncSession) -> Optional[str]:
    """Just the address staff open in a browser (not the credentials) --
    cheap enough for every request's "Support" nav link."""
    provider_type = await HELPDESK.get_active_type(db)
    cls = HELPDESK.get_class(provider_type)
    if cls is None:
        return None
    value = await db.scalar(
        select(ClubSetting.value).where(ClubSetting.key == HELPDESK.setting_key(provider_type, cls.web_url_field))
    )
    return (value or "").rstrip("/") or None
