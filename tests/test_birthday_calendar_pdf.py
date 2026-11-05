"""
The printable birthday list (/calendar/birthdays/pdf): renders with no
data, and carries the shared org/register/bank footer (ADR 0045) that
every PDF shows. Its content -- the web list's window and order (default 3 months)
(issue #272, which replaced issue #99's whole-year calendar) -- is
tested in tests/test_birthday_list.py.

Uses the web UI's cookie-based session login, like the other PDF-sheet
tests, since this route returns a PDF file rather than JSON.
"""
import io
from datetime import date, timedelta

from pypdf import PdfReader

from app.database import AsyncSessionLocal
from app.models import Member, ClubBoardMember
from tests.conftest import login, auth_header


async def web_login(client, email: str, password: str = "testpasswort123") -> None:
    response = await client.post("/auth/login", data={"email": email, "password": password})
    assert response.status_code in (302, 303)


def _pdf_text(pdf_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(pdf_bytes))
    return "\n".join(page.extract_text() for page in reader.pages)


def _normalized(text: str) -> str:
    """WeasyPrint's font subsetting can make pypdf's text extraction
    insert stray spaces around certain letter pairs (see
    tests/test_members_signin_sheet.py)."""
    return "".join(text.split())


async def test_birthday_calendar_pdf_handles_empty(client, admin_user):
    await web_login(client, "admin@example.com")

    response = await client.get("/calendar/birthdays/pdf")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    # No members with a birth date on file at all -- must render
    # without erroring rather than crash on an empty entries list.


async def test_birthday_calendar_pdf_shows_the_universal_org_bank_footer(client, admin_user):
    """The org/register/bank footer (docs/ADR/0045) is no longer
    invoice-only -- a non-invoice, non-finances PDF must show it too,
    proving load_org_footer_context() works independently of the
    finances module."""
    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    for key, value in [
        ("bank_iban", "DE89370400440532013000"),
        ("registergericht", "Amtsgericht Musterstadt"),
        ("vereinsnummer", "VR 12345"),
    ]:
        response = await client.put(f"/api/v1/club-settings/{key}", json={"value": value}, headers=headers)
        assert response.status_code == 200, response.text

    await web_login(client, "admin@example.com")

    response = await client.get("/calendar/birthdays/pdf")
    assert response.status_code == 200

    normalized = _normalized(_pdf_text(response.content))
    assert _normalized("IBAN DE89370400440532013000") in normalized
    assert _normalized("Amtsgericht Musterstadt") in normalized
    assert _normalized("VR 12345") in normalized


async def test_pdf_footer_lists_board_members_under_register_info(client, admin_user):
    """Issue #121: board members picked on admin -> settings -> club
    settings (issue #111) must show up in the second footer column,
    right under the registration court line, on every generated PDF --
    checked here via the birthday calendar as a representative non-
    finances generator, since the footer is built once in
    app/pdf_chrome.py and shared by all of them."""
    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    response = await client.put(
        "/api/v1/club-settings/registergericht", json={"value": "Amtsgericht Musterstadt"}, headers=headers,
    )
    assert response.status_code == 200, response.text

    async with AsyncSessionLocal() as session:
        alice = Member(first_name="Alice", last_name="Chairperson")
        bob = Member(first_name="Bob", last_name="Treasurer")
        former = Member(
            first_name="Carla", last_name="Former",
            member_until=date.today() - timedelta(days=1),
        )
        session.add_all([alice, bob, former])
        await session.flush()
        session.add_all([
            ClubBoardMember(member_id=alice.id),
            ClubBoardMember(member_id=bob.id),
            ClubBoardMember(member_id=former.id),
        ])
        await session.commit()

    await web_login(client, "admin@example.com")
    response = await client.get("/calendar/birthdays/pdf")
    assert response.status_code == 200

    normalized = _normalized(_pdf_text(response.content))
    assert _normalized("Alice Chairperson") in normalized
    assert _normalized("Bob Treasurer") in normalized
    # A member whose membership has since lapsed must not keep showing
    # up as a board member on freshly generated documents.
    assert _normalized("Carla Former") not in normalized


async def test_pdf_footer_omits_board_members_line_when_none_are_set(client, admin_user):
    await web_login(client, "admin@example.com")
    response = await client.get("/calendar/birthdays/pdf")
    assert response.status_code == 200
    # No assertion on absence of a specific name is meaningful here
    # (nothing was ever added) -- this just guards against a crash
    # when board_members is empty, matching every other blank-field
    # footer line's "just omit it" behavior.
