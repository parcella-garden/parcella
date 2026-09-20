"""
Issue #229: filter /members/ down to members with Email info (the
email_notifications column) set to yes, to quickly find who to include
in an email-based announcement -- same shape as the active_only filter
(issue #200), via a fourth boolean AND'd onto _filtered_members_query()
(app/routers/members.py) and carried through the CSV export.
"""
from app.database import AsyncSessionLocal
from app.models import Member


async def test_email_info_only_excludes_opted_out_members(client, admin_user):
    await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})

    async with AsyncSessionLocal() as session:
        session.add(Member(first_name="Declined", last_name="Newsletter", email_notifications=False))
        session.add(Member(first_name="Subscribed", last_name="Reader", email_notifications=True))
        await session.commit()

    r = await client.get("/members/?email_info_only=true")
    assert r.status_code == 200
    assert "Newsletter, Declined" not in r.text
    assert "Reader, Subscribed" in r.text

    r_default = await client.get("/members/")
    assert "Newsletter, Declined" in r_default.text


async def test_csv_export_respects_email_info_only(client, admin_user):
    await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})

    async with AsyncSessionLocal() as session:
        session.add(Member(first_name="Declined", last_name="Newsletter", email_notifications=False))
        session.add(Member(first_name="Subscribed", last_name="Reader", email_notifications=True))
        await session.commit()

    r = await client.get("/members/export/csv?email_info_only=true")
    assert r.status_code == 200
    assert "Reader" in r.text
    assert "Newsletter" not in r.text
