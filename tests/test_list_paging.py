"""
Issue #425 (ADR 0145): the member and parcel lists are paged, 100 rows a
page. "Select all" ticks one page; "all N matching" sends the list's
filter instead of ids, so a big club's selection never becomes a URL
the server or proxy rejects.
"""
from datetime import date

from app.database import AsyncSessionLocal
from app.models import Member, Parcel, ParcelStatus
from app.paging import PAGE_SIZE, page_of, with_page
from tests.conftest import auth_header, login
from tests.test_announcements import _enable_module, web_login


def _rows(html: str, css_class: str) -> int:
    return html.count(f'class="form-check-input {css_class}"')


async def _members(n: int) -> list:
    async with AsyncSessionLocal() as db:
        members = [Member(first_name="Vera", last_name=f"Nachname{i:03d}", member_since=date(2010, 1, 1))
                   for i in range(n)]
        db.add_all(members)
        await db.commit()
        return [m.id for m in members]


async def _parcels(n: int, terminated: int = 0) -> list:
    async with AsyncSessionLocal() as db:
        parcels = [Parcel(plot_number=f"P{i:03d}", area_sqm=100,
                          status=ParcelStatus.TERMINATED if i < terminated else ParcelStatus.ACTIVE)
                   for i in range(n)]
        db.add_all(parcels)
        await db.commit()
        return [p.id for p in parcels]


def test_helpers():
    assert PAGE_SIZE == 100
    assert (page_of(0), page_of(99), page_of(100)) == (1, 1, 2)
    assert with_page("", 1) == "" and with_page("", 2) == "?page=2"
    assert with_page("tag=x", 1) == "?tag=x" and with_page("tag=x", 3) == "?tag=x&page=3"


async def test_member_list_is_paged(client, admin_user):
    await web_login(client, "admin@example.com")
    ids = await _members(105)

    first = await client.get("/members/")
    assert first.status_code == 200
    assert _rows(first.text, "pick-member") == 100
    assert "Showing 1–100 of 105" in first.text and "Page 1 of 2" in first.text
    assert 'href="/members/?page=2"' in first.text
    assert "Select all 105 matching the filter" in first.text
    assert "105 members" in first.text  # footer counts the whole filter, not the page

    second = await client.get("/members/?page=2")
    assert _rows(second.text, "pick-member") == 5 and "Nachname104" in second.text
    # A page past the end shows the last page, not an empty list.
    assert _rows((await client.get("/members/?page=99")).text, "pick-member") == 5

    # The filter survives paging.
    filtered = await client.get("/members/?search=Nachname&page=2")
    assert 'href="/members/?search=Nachname"' in filtered.text  # Previous = page 1, filter kept

    # "All matching" = the filter without ids: the export has all 105.
    export = await client.get("/members/export/csv", params={"search": "Nachname"})
    assert all(f"Nachname{i:03d}" in export.text for i in range(105))

    # Back to the list from member #101 lands on page 2.
    detail = await client.get(f"/members/{ids[100]}")
    assert 'href="/members/?page=2"' in detail.text


async def test_short_list_has_no_pager(client, admin_user):
    await web_login(client, "admin@example.com")
    await _members(3)
    page = await client.get("/members/")
    assert _rows(page.text, "pick-member") == 3
    assert "Page 1 of" not in page.text and "matching the filter" not in page.text


async def test_parcel_list_is_paged_and_all_matching_uses_the_filter(client, admin_user):
    await _enable_module(client, auth_header(await login(client, "admin@example.com")))
    await web_login(client, "admin@example.com")
    ids = await _parcels(105, terminated=3)

    first = await client.get("/parcels/")
    assert _rows(first.text, "pick-parcel") == 100 and "Page 1 of 2" in first.text
    assert "Select all 105 matching the filter" in first.text
    assert "Total area: 10500 sqm" in first.text  # total area of the whole list, not the page

    assert _rows((await client.get("/parcels/?page=2")).text, "pick-parcel") == 5
    assert 'href="/parcels/?page=2"' in (await client.get(f"/parcels/{ids[104]}")).text

    # The export follows the list's filter now.
    export = await client.get("/parcels/export/csv", params={"status_filter": "TERMINATED"})
    assert "P000" in export.text and "P002" in export.text and "P003" not in export.text

    # A notice to all parcels matching the filter resolves them server-side.
    preview = await client.get("/announcements/new", params={
        "audience_kind": "parcels", "all_matching": "1", "status_filter": "TERMINATED",
    })
    assert preview.status_code == 200 and "Notice to the leaseholders of 3 parcel(s)" in preview.text
    everything = await client.get("/announcements/new", params={"audience_kind": "parcels", "all_matching": "1"})
    assert "Notice to the leaseholders of 105 parcel(s)" in everything.text

    # Without all_matching, an empty selection is still refused.
    assert (await client.get("/announcements/new", params={"audience_kind": "parcels"})).status_code == 400
