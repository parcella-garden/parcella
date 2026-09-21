"""
Members search: matches email address and phone number, not just name
and parcel number -- widens the shared search condition in
app/routers/members.py's _filtered_members_query(), which the CSV
export reuses too. Matches any of a member's emails/phones (both
one-to-many), not just the primary one.
"""
from app.database import AsyncSessionLocal
from app.models import Member, MemberEmail, MemberPhone


async def test_search_matches_email_address(client, admin_user):
    await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})

    async with AsyncSessionLocal() as session:
        target = Member(first_name="Target", last_name="Person")
        other = Member(first_name="Other", last_name="Person")
        session.add_all([target, other])
        await session.flush()
        session.add(MemberEmail(member_id=target.id, address="target.person@example.com", is_primary=True))
        session.add(MemberEmail(member_id=other.id, address="other.person@example.com", is_primary=True))
        await session.commit()

    r = await client.get("/members/?search=target.person@example.com")
    assert r.status_code == 200
    assert "Person, Target" in r.text
    assert "Person, Other" not in r.text


async def test_search_matches_non_primary_email(client, admin_user):
    await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})

    async with AsyncSessionLocal() as session:
        target = Member(first_name="Secondary", last_name="Email")
        session.add(target)
        await session.flush()
        session.add(MemberEmail(member_id=target.id, address="primary@example.com", is_primary=True))
        session.add(MemberEmail(member_id=target.id, address="work-address@example.com", is_primary=False))
        await session.commit()

    r = await client.get("/members/?search=work-address")
    assert r.status_code == 200
    assert "Email, Secondary" in r.text


async def test_search_matches_phone_number(client, admin_user):
    await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})

    async with AsyncSessionLocal() as session:
        target = Member(first_name="Callable", last_name="Person")
        other = Member(first_name="Unrelated", last_name="Person")
        session.add_all([target, other])
        await session.flush()
        session.add(MemberPhone(member_id=target.id, number="030 1234567", is_primary=True))
        session.add(MemberPhone(member_id=other.id, number="040 7654321", is_primary=True))
        await session.commit()

    r = await client.get("/members/?search=1234567")
    assert r.status_code == 200
    assert "Person, Callable" in r.text
    assert "Person, Unrelated" not in r.text


async def test_csv_export_respects_search_by_email(client, admin_user):
    await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})

    async with AsyncSessionLocal() as session:
        target = Member(first_name="Exported", last_name="Member")
        other = Member(first_name="Excluded", last_name="Member")
        session.add_all([target, other])
        await session.flush()
        session.add(MemberEmail(member_id=target.id, address="exported@example.com", is_primary=True))
        session.add(MemberEmail(member_id=other.id, address="excluded@example.com", is_primary=True))
        await session.commit()

    r = await client.get("/members/export/csv?search=exported@example.com")
    assert r.status_code == 200
    assert "Exported" in r.text
    assert "Excluded" not in r.text
