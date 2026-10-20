"""
Localization (l10n): number, currency, and address formats per club.

Architecture decision: deliberately SEPARATE from app/i18n.py (UI
language). Language and regional formatting conventions are two
independent things -- e.g. "English as the UI language" says nothing
about whether numbers are shown as "1,234.50" or "1.234,50", or
whether amounts are in £, €, or zł. A club therefore picks a region
(ClubSetting "region", e.g. "de_DE") and a currency (ClubSetting
"currency", e.g. "EUR") independently of its language (ClubSetting
"language") and of each other.

Number and currency formatting uses the Babel library instead of
hand-rolled regex/string hacks (the previous ".replace(',', '.')" in
the dashboard template was exactly that kind of hack, and only correct
for German). Babel knows the correct thousands/decimal separators AND
the correct currency-symbol position per locale (e.g. "€ 1.234,50" in
the Netherlands vs. "1.234,50 €" in Germany vs. "£1,234.50" in the UK).

Address format is more complex than numbers (different field order,
not just different separators) and is therefore deliberately NOT
handled via an external library (e.g. Google libaddressinput would be
overkill for this project's scope), but via a simple template per
region (see ADDRESS_FORMATS below). For the 7 currently supported
countries, a single distinction suffices: postal code before the city
(continental Europe) vs. after (UK).
"""
import logging
from typing import Optional

from fastapi import Request
from jinja2 import pass_context
from markupsafe import Markup, escape
from babel.numbers import format_currency, format_decimal, get_currency_symbol
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import ClubSetting

logger = logging.getLogger(__name__)

DEFAULT_REGION = "de_DE"
DEFAULT_CURRENCY = "EUR"

# Region choices for /admin/settings. Names deliberately kept as the
# English country name (same as the currency codes), to avoid needing
# 7 more translation keys per language -- country and currency codes
# are generally understandable enough on their own.
AVAILABLE_REGIONS = {
    "de_DE": "Germany",
    "en_GB": "United Kingdom",
    "fr_FR": "France",
    "nl_NL": "Netherlands",
    "pl_PL": "Poland",
    "cs_CZ": "Czech Republic",
    "sk_SK": "Slovakia",
}

# IANA time zone per region -- every supported country has exactly one.
# Used by the ICS feeds: an event's "HH:MM" is the club's local
# wall-clock time, so a calendar app in another zone still shows it right.
REGION_TIMEZONES = {
    "de_DE": "Europe/Berlin",
    "en_GB": "Europe/London",
    "fr_FR": "Europe/Paris",
    "nl_NL": "Europe/Amsterdam",
    "pl_PL": "Europe/Warsaw",
    "cs_CZ": "Europe/Prague",
    "sk_SK": "Europe/Bratislava",
}

# Currency choices. Deliberately not coupled 1:1 to AVAILABLE_REGIONS --
# e.g. a French-speaking club in Switzerland might use CHF. Both
# settings stay independently selectable.
AVAILABLE_CURRENCIES = {
    "EUR": "Euro (\u20ac)",
    "GBP": "British Pound (\u00a3)",
    "PLN": "Polish Z\u0142oty (z\u0142)",
    "CZK": "Czech Koruna (K\u010d)",
}

# {street} and {postal_code} and {city} -- order per region.
# Continental Europe: postal code before city, second line.
# UK: city before postcode, postcode on its own last line.
ADDRESS_FORMATS = {
    "de_DE": "{street}\n{postal_code} {city}",
    "fr_FR": "{street}\n{postal_code} {city}",
    "nl_NL": "{street}\n{postal_code} {city}",
    "pl_PL": "{street}\n{postal_code} {city}",
    "cs_CZ": "{street}\n{postal_code} {city}",
    "sk_SK": "{street}\n{postal_code} {city}",
    "en_GB": "{street}\n{city}\n{postal_code}",
}


async def load_current_region(db: AsyncSession) -> str:
    """Reads the currently configured region from ClubSetting (default: Germany)."""
    result = await db.execute(select(ClubSetting).where(ClubSetting.key == "region"))
    entry = result.scalar_one_or_none()
    if entry and entry.value in AVAILABLE_REGIONS:
        return entry.value
    return DEFAULT_REGION


async def load_current_currency(db: AsyncSession) -> str:
    """Reads the currently configured currency from ClubSetting (default: EUR)."""
    result = await db.execute(select(ClubSetting).where(ClubSetting.key == "currency"))
    entry = result.scalar_one_or_none()
    if entry and entry.value in AVAILABLE_CURRENCIES:
        return entry.value
    return DEFAULT_CURRENCY


def format_money(amount, region: str, currency: str) -> str:
    """Formats a money amount to match the region and currency (via Babel)."""
    try:
        return format_currency(amount, currency, locale=region)
    except Exception:
        logger.warning(f"format_money failed for region={region} currency={currency}")
        return f"{amount} {currency}"


def format_number(value, region: str, decimals: int = 0) -> str:
    """Formats a number (thousands/decimal separators) to match the region."""
    try:
        return format_decimal(value, locale=region, format=f"#,##0.{'0' * decimals}" if decimals else "#,##0")
    except Exception:
        logger.warning(f"format_number failed for region={region}")
        return str(value)


def format_address(street: str, postal_code: str, city: str, region: str) -> str:
    """Formats an address (field order) to match the region."""
    template = ADDRESS_FORMATS.get(region, ADDRESS_FORMATS[DEFAULT_REGION])
    return template.format(street=street or "", postal_code=postal_code or "", city=city or "")


def format_address_lines(street: str, postal_code: str, city: str, region: str) -> list:
    """Like format_address, but as a list of lines, with fully empty
    lines (e.g. when neither postal code nor city is set) skipped.
    Intended for HTML rendering with <br> between the lines."""
    raw = format_address(street, postal_code, city, region)
    return [line.strip() for line in raw.split("\n") if line.strip()]


def _get_state(request: Optional[Request]):
    region = getattr(request.state, "region", DEFAULT_REGION) if request else DEFAULT_REGION
    currency = getattr(request.state, "currency", DEFAULT_CURRENCY) if request else DEFAULT_CURRENCY
    return region, currency


@pass_context
def jinja_money(context, amount, currency: Optional[str] = None) -> str:
    """Registered as a Jinja filter: {{ amount|money }}. Automatically
    uses request.state.region/currency of the current request unless a
    differing currency parameter is passed."""
    request = context.get("request")
    region, default_currency = _get_state(request)
    return format_money(amount, region, currency or default_currency)


@pass_context
def jinja_number(context, value, decimals: int = 0) -> str:
    """Registered as a Jinja filter: {{ value|number }} or {{ value|number(2) }}."""
    request = context.get("request")
    region, _ = _get_state(request)
    return format_number(value, region, decimals)


@pass_context
def jinja_address(context, street: str, postal_code: str, city: str) -> str:
    """Registered as a Jinja global: {{ address(street, postal_code, city) }}."""
    request = context.get("request")
    region, _ = _get_state(request)
    return format_address(street, postal_code, city, region)


@pass_context
def jinja_address_lines(context, street: str, postal_code: str, city: str) -> list:
    """Registered as a Jinja global: {{ address_lines(street, postal_code, city) }}
    -- a list of PLAIN (unescaped) lines, empty lines already removed.

    Do NOT render these into a template with `|join('<br>')|safe`: Jinja's
    `join` returns a plain str when both the items and the separator are
    plain strs, so `|safe` then marks the raw member data as trusted --
    which is exactly how a member address containing HTML became a stored
    XSS vector. Use `address_html(...)` below for HTML output; this global
    is for non-HTML consumers (PDF generators, CSV export)."""
    request = context.get("request")
    region, _ = _get_state(request)
    return format_address_lines(street, postal_code, city, region)


@pass_context
def jinja_address_html(context, street: str, postal_code: str, city: str) -> Markup:
    """Registered as a Jinja global: {{ address_html(street, postal_code, city) }}
    -- the address as ready-to-render HTML with <br> between the lines.

    Escapes every line itself and joins with a Markup separator, so the
    result can be emitted WITHOUT `|safe` (Markup is rendered as-is by
    Jinja). Returns an empty Markup when there's no address at all, so
    templates can still branch on truthiness for their "–" fallback."""
    lines = jinja_address_lines(context, street, postal_code, city)
    return Markup("<br>").join(escape(line) for line in lines)


@pass_context
def jinja_currency_symbol(context) -> str:
    """Registered as a Jinja global: {{ currency_symbol() }} -- for input
    field hints (e.g. an input-group-text next to an <input>), where
    only the symbol of the currently configured currency is needed, not
    a fully formatted amount."""
    request = context.get("request")
    region, currency = _get_state(request)
    try:
        return get_currency_symbol(currency, locale=region)
    except Exception:
        return currency
