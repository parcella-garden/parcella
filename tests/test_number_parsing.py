"""
Issue #350: amounts of 1,000 or more in German format ("1.234,56") were
invalid, so the bank CSV import silently skipped every big booking.
app.l10n.parse_decimal is now the one parser behind the finances,
metering and processes inputs.
"""
from decimal import Decimal

import pytest

from app.l10n import parse_decimal
from app.routers.metering import _parse_number


@pytest.mark.parametrize("text, expected", [
    ("1.234,56", "1234.56"),       # German bank export, the bug
    ("-1.234,56", "-1234.56"),
    ("1,234.56", "1234.56"),       # English export
    ("+1,234.56", "1234.56"),
    ("1 234,56", "1234.56"),       # space / narrow no-break space as thousands separator
    ("1 234,56", "1234.56"),
    ("1.234.567", "1234567"),      # several of one kind: thousands
    ("1,234,567.89", "1234567.89"),
    # Unchanged: one separator is the decimal point.
    ("1234,56", "1234.56"),
    ("1234.56", "1234.56"),
    ("-15.50", "-15.50"),
    ("1,5", "1.5"),
    ("1.234", "1.234"),
])
def test_parse_decimal_reads_both_formats(text, expected):
    assert parse_decimal(text) == Decimal(expected)


@pytest.mark.parametrize("text", ["", "  ", None, "abc", "NaN", "Infinity", "12.34,56", "1.234.56", "1,234,567,8"])
def test_parse_decimal_rejects_invalid_and_does_not_guess(text):
    assert parse_decimal(text) is None


def test_meter_readings_in_german_format():
    assert _parse_number("12.345,6", 1) == Decimal("12345.6")
    assert _parse_number("12,5", 1) == Decimal("12.5")
