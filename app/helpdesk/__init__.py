"""Helpdesk providers for the support module -- see app/helpdesk/base.py
and docs/ADR/0107."""
from app.helpdesk.base import (  # noqa: F401
    ALL_CAPABILITIES, CREATE, CUSTOMER_SYNC, HIDDEN_STATUSES, INBOX, READ,
    CapabilityMissing, HelpdeskConversation, HelpdeskError, HelpdeskMessage, HelpdeskProvider,
)
from app.helpdesk.registry import (  # noqa: F401
    HELPDESK, active_capabilities, get_active_helpdesk_type, get_helpdesk, load_helpdesk_web_url,
)
