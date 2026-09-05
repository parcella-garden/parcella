"""
Issue #202: Previous/Next buttons on /members/{id} and /parcels/{id} so
a board member working through a list one record at a time doesn't have
to keep going back to the list and re-finding their place.

Prev/Next walk the *same filtered, ordered* list the board member was
actually looking at (search / include_inactive / pending_only /
active_only for members; search / status_filter for parcels) -- not
always the full unfiltered list -- via _filtered_members_query() /
_filtered_parcels_query(), the same helpers the list pages and CSV
exports already share. The filter is carried in the URL's query string
end to end: list row links include it, and the Previous/Next buttons on
the detail page pass it along again.
"""
from datetime import date, timedelta

from app.database import AsyncSessionLocal
from app.models import Member, MeteringMedium, MeteringPoint, MeteringPointType, Parcel


async def web_login(client, email: str, password: str = "testpasswort123") -> None:
    response = await client.post("/auth/login", data={"email": email, "password": password})
    assert response.status_code in (302, 303)


# ---------------------------------------------------------------------------
# Members
# ---------------------------------------------------------------------------

async def test_member_detail_prev_next_follow_default_sort_order(client, admin_user):
    await web_login(client, "admin@example.com")

    async with AsyncSessionLocal() as session:
        a = Member(first_name="Ada", last_name="Anders")
        b = Member(first_name="Bruno", last_name="Bergmann")
        c = Member(first_name="Clara", last_name="Cichon")
        session.add_all([a, b, c])
        await session.commit()
        a_id, b_id, c_id = a.id, b.id, c.id

    # Default list order is last_name, first_name -- Bruno (the middle
    # one alphabetically) must see Ada as previous and Clara as next.
    response = await client.get(f"/members/{b_id}")
    assert response.status_code == 200
    assert f"/members/{a_id}" in response.text
    assert f"/members/{c_id}" in response.text


async def test_member_detail_first_and_last_have_no_prev_or_next(client, admin_user):
    await web_login(client, "admin@example.com")

    async with AsyncSessionLocal() as session:
        a = Member(first_name="Ada", last_name="Anders")
        b = Member(first_name="Bruno", last_name="Bergmann")
        session.add_all([a, b])
        await session.commit()
        a_id, b_id = a.id, b.id

    first_response = await client.get(f"/members/{a_id}")
    assert 'aria-disabled="true"' in first_response.text
    assert f"/members/{b_id}" in first_response.text  # next still works

    last_response = await client.get(f"/members/{b_id}")
    assert f"/members/{a_id}" in last_response.text  # previous still works


async def test_member_detail_prev_next_respect_active_only_filter(client, admin_user):
    """The pending (blank member_since) member must be skipped over by
    Previous/Next when browsing the active_only-filtered list -- same
    set /members/?active_only=true itself would show (issue #200)."""
    await web_login(client, "admin@example.com")

    since = date.today() - timedelta(days=30)
    async with AsyncSessionLocal() as session:
        a = Member(first_name="Ada", last_name="Anders", member_since=since)
        pending = Member(first_name="Ben", last_name="Blank", member_since=None)
        c = Member(first_name="Clara", last_name="Cichon", member_since=since)
        session.add_all([a, pending, c])
        await session.commit()
        a_id, c_id = a.id, c.id

    response = await client.get(f"/members/{a_id}", params={"active_only": "true"})
    assert response.status_code == 200
    assert f"/members/{c_id}?active_only=true" in response.text
    assert 'aria-disabled="true"' in response.text  # no previous -- Ada is first among active_only


async def test_member_not_in_current_filter_shows_no_prev_next(client, admin_user):
    """A member that doesn't match the filter carried in the query
    string (e.g. a stale bookmarked link, or edited out of the filtered
    set) must not produce a guessed/incorrect prev or next."""
    await web_login(client, "admin@example.com")

    async with AsyncSessionLocal() as session:
        pending = Member(first_name="Ben", last_name="Blank", member_since=None)
        session.add(pending)
        await session.commit()
        pending_id = pending.id

    response = await client.get(f"/members/{pending_id}", params={"active_only": "true"})
    assert response.status_code == 200
    assert response.text.count('aria-disabled="true"') == 2  # both Previous and Next disabled


async def test_member_list_row_links_carry_current_filter(client, admin_user):
    await web_login(client, "admin@example.com")

    async with AsyncSessionLocal() as session:
        session.add(Member(first_name="Ben", last_name="Blank", member_since=None))
        await session.commit()

    response = await client.get("/members/", params={"active_only": "true"})
    assert response.status_code == 200
    assert "active_only=true" in response.text


# ---------------------------------------------------------------------------
# Parcels
# ---------------------------------------------------------------------------

async def test_parcel_detail_prev_next_follow_plot_number_order(client, admin_user):
    await web_login(client, "admin@example.com")

    async with AsyncSessionLocal() as session:
        g1 = Parcel(plot_number="G001")
        g2 = Parcel(plot_number="G002")
        g3 = Parcel(plot_number="G003")
        session.add_all([g1, g2, g3])
        await session.commit()
        g1_id, g2_id, g3_id = g1.id, g2.id, g3.id

    response = await client.get(f"/parcels/{g2_id}")
    assert response.status_code == 200
    assert f"/parcels/{g1_id}" in response.text
    assert f"/parcels/{g3_id}" in response.text


async def test_parcel_detail_prev_next_respect_status_filter(client, admin_user):
    from app.models import ParcelStatus

    await web_login(client, "admin@example.com")

    async with AsyncSessionLocal() as session:
        g1 = Parcel(plot_number="G001", status=ParcelStatus.TERMINATED)
        g2 = Parcel(plot_number="G002", status=ParcelStatus.ACTIVE)
        g3 = Parcel(plot_number="G003", status=ParcelStatus.TERMINATED)
        session.add_all([g1, g2, g3])
        await session.commit()
        g1_id, g3_id = g1.id, g3.id

    response = await client.get(
        f"/parcels/{g1_id}", params={"status_filter": "TERMINATED"},
    )
    assert response.status_code == 200
    assert f"/parcels/{g3_id}?status_filter=TERMINATED" in response.text
    assert 'aria-disabled="true"' in response.text  # G001 is first among TERMINATED


async def test_parcel_list_row_links_carry_current_filter(client, admin_user):
    await web_login(client, "admin@example.com")

    async with AsyncSessionLocal() as session:
        session.add(Parcel(plot_number="G001"))
        await session.commit()

    response = await client.get("/parcels/", params={"search": "G001"})
    assert response.status_code == 200
    assert "search=G001" in response.text


# ---------------------------------------------------------------------------
# Alt+Left/Alt+Right keyboard shortcut (issue #202 follow-up): the
# base.html handler looks these ids up by id, so a template refactor
# that renames or drops them would silently break the shortcut with no
# other test catching it.
# ---------------------------------------------------------------------------

async def test_member_detail_exposes_keyboard_nav_link_ids(client, admin_user):
    await web_login(client, "admin@example.com")

    async with AsyncSessionLocal() as session:
        member = Member(first_name="Ada", last_name="Anders")
        session.add(member)
        await session.commit()
        member_id = member.id

    response = await client.get(f"/members/{member_id}")
    assert 'id="nav-prev-link"' in response.text
    assert 'id="nav-next-link"' in response.text


async def test_parcel_detail_exposes_keyboard_nav_link_ids(client, admin_user):
    await web_login(client, "admin@example.com")

    async with AsyncSessionLocal() as session:
        parcel = Parcel(plot_number="G001")
        session.add(parcel)
        await session.commit()
        parcel_id = parcel.id

    response = await client.get(f"/parcels/{parcel_id}")
    assert 'id="nav-prev-link"' in response.text
    assert 'id="nav-next-link"' in response.text


# ---------------------------------------------------------------------------
# Metering points (issue #212): same Previous/Next pattern as
# members/parcels above, walking the metering-points list page's own
# order (MAIN_METER, then PARCEL by plot number, then CLUB by label --
# see _metering_point_sort_key() in app/routers/metering.py). No
# search/filter exists on that list, so there's no query string to
# carry along, unlike members/parcels.
# ---------------------------------------------------------------------------

async def test_metering_point_detail_prev_next_follow_list_order(client, admin_user):
    await web_login(client, "admin@example.com")

    async with AsyncSessionLocal() as session:
        a = MeteringPoint(medium=MeteringMedium.WATER, type=MeteringPointType.CLUB, label="Alpha")
        b = MeteringPoint(medium=MeteringMedium.WATER, type=MeteringPointType.CLUB, label="Bravo")
        c = MeteringPoint(medium=MeteringMedium.WATER, type=MeteringPointType.CLUB, label="Charlie")
        session.add_all([a, b, c])
        await session.commit()
        a_id, b_id, c_id = a.id, b.id, c.id

    response = await client.get(f"/water/metering-points/{b_id}")
    assert response.status_code == 200
    assert f"/water/metering-points/{a_id}" in response.text
    assert f"/water/metering-points/{c_id}" in response.text


async def test_metering_point_detail_first_and_last_have_no_prev_or_next(client, admin_user):
    await web_login(client, "admin@example.com")

    async with AsyncSessionLocal() as session:
        a = MeteringPoint(medium=MeteringMedium.WATER, type=MeteringPointType.CLUB, label="Alpha")
        b = MeteringPoint(medium=MeteringMedium.WATER, type=MeteringPointType.CLUB, label="Bravo")
        session.add_all([a, b])
        await session.commit()
        a_id, b_id = a.id, b.id

    first_response = await client.get(f"/water/metering-points/{a_id}")
    assert 'aria-disabled="true"' in first_response.text
    assert f"/water/metering-points/{b_id}" in first_response.text  # next still works

    last_response = await client.get(f"/water/metering-points/{b_id}")
    assert f"/water/metering-points/{a_id}" in last_response.text  # previous still works


async def test_metering_point_detail_exposes_keyboard_nav_link_ids(client, admin_user):
    await web_login(client, "admin@example.com")

    async with AsyncSessionLocal() as session:
        point = MeteringPoint(medium=MeteringMedium.WATER, type=MeteringPointType.CLUB, label="Alpha")
        session.add(point)
        await session.commit()
        point_id = point.id

    response = await client.get(f"/water/metering-points/{point_id}")
    assert 'id="nav-prev-link"' in response.text
    assert 'id="nav-next-link"' in response.text
