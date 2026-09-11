"""
Shared Jinja2Templates instance.

Previously every router had its own Jinja2Templates(...) instance with
its own environment -- which would have meant registering the `t`
translation function (see app/i18n.py) separately in every single
router. Instead: ONE environment, configured centrally here, imported
by every router.
"""
from fastapi.templating import Jinja2Templates

from app.i18n import jinja_t
from app.l10n import (
    jinja_money, jinja_number, jinja_address, jinja_address_lines,
    jinja_address_html, jinja_currency_symbol,
)
from app.html_sanitizer import sanitize_email_html
from app.permissions import jinja_has_perm, jinja_is_full_access, jinja_is_system_admin
from app.services.work_hours import jinja_new_participations_count
from app.avatars import avatar_url
from app.csrf import jinja_csrf_field, jinja_csrf_token

templates = Jinja2Templates(directory="app/templates")
templates.env.globals["t"] = jinja_t
templates.env.globals["address"] = jinja_address
templates.env.globals["address_lines"] = jinja_address_lines
templates.env.globals["address_html"] = jinja_address_html
templates.env.globals["currency_symbol"] = jinja_currency_symbol
templates.env.globals["has_perm"] = jinja_has_perm
templates.env.globals["is_full_access"] = jinja_is_full_access
templates.env.globals["is_system_admin"] = jinja_is_system_admin
templates.env.globals["new_participations_count"] = jinja_new_participations_count
templates.env.globals["avatar_url"] = avatar_url
# Every state-changing <form> needs {{ csrf_field() }}; the fetch()-based
# actions read {{ csrf_token() }} from the <meta> tag in base.html.
templates.env.globals["csrf_field"] = jinja_csrf_field
templates.env.globals["csrf_token"] = jinja_csrf_token
templates.env.filters["money"] = jinja_money
templates.env.filters["number"] = jinja_number
# Second sanitization layer at render time (see app/html_sanitizer.py) --
# cheap and harmless on already-clean HTML, but a safety net in case
# some future code path lets unchecked content reach a template.
templates.env.filters["sanitize_html"] = sanitize_email_html
