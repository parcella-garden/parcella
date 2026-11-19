"""
Issue #351: the preview step of every CSV import decodes with a Latin-1
fallback (decode_csv_upload), but the final step decoded UTF-8 only -- an
Excel/ANSI file with an umlaut passed the preview and the mapping, then
crashed the import with a 500. Members, parcels, external contacts,
metering and finances all go through parse_mapped_csv_rows.
"""
import base64

from app.csv_utils import parse_mapped_csv_rows

MAPPING = {0: "first_name", 1: "city"}
TEXT = "Vorname;Ort\nJürgen;Köln\nÉva;Düsseldorf\n"


def _rows(raw: bytes):
    return parse_mapped_csv_rows(base64.b64encode(raw).decode("ascii"), ";", MAPPING)


def test_final_step_reads_latin1_files_like_the_preview():
    assert _rows(TEXT.encode("latin-1")) == [
        {"first_name": "Jürgen", "city": "Köln"}, {"first_name": "Éva", "city": "Düsseldorf"},
    ]


def test_utf8_with_and_without_bom_unchanged():
    expected = [{"first_name": "Jürgen", "city": "Köln"}, {"first_name": "Éva", "city": "Düsseldorf"}]
    assert _rows(TEXT.encode("utf-8")) == expected
    assert _rows(TEXT.encode("utf-8-sig")) == expected
