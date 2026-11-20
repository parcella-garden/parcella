"""
Issue #397: tick parcels on /parcels/ and write to the people on them.
Everyone currently on a ticked parcel is in the audience; a household
(same postal address, across all ticked parcels) gets one letter with
all its names, and an email address shared by several tenants gets the
message once.
"""
import io
from datetime import date, timedelta

from pypdf import PdfReader

from app.database import AsyncSessionLocal
from app.member_filters import MemberListFilter
from app.models import Member, MemberEmail, MemberParcel, Parcel
from tests.conftest import auth_header, login
from tests.test_announcement_audience import _announcement
from tests.test_announcements import _enable_module, web_login


async def _setup(client):
    await _enable_module(client, auth_header(await login(client, "admin@example.com")))
    await web_login(client, "admin@example.com")
    async with AsyncSessionLocal() as db:
        def member(first, last, street, city, email=None):
            m = Member(first_name=first, last_name=last, street=street, postal_code="04103", city=city)
            if email:
                m.email_addresses.append(MemberEmail(address=email, is_primary=True))
            db.add(m)
            return m

        anna = member("Anna", "Haus", "Lindenweg 1", "Leipzig", email="haus@example.org")
        emil = member("Emil", "Haus", "Lindenweg 1", "Leipzig", email="HAUS@example.org ")  # same inbox
        bernd = member("Bernd", "Haus", "Lindenweg 1", "Leipzig")
        berta = member("Berta", "Haus", " lindenweg 1 ", "LEIPZIG")
        clara = member("Clara", "Fern", "Am Hang 7", "Dresden")
        gone = member("Gerd", "Gegangen", "Altweg 3", "Leipzig")
        udo = member("Udo", "Unbeteiligt", "Weg 9", "Leipzig", email="udo@example.org")
        one, two, other = Parcel(plot_number="P-397-1"), Parcel(plot_number="P-397-2"), Parcel(plot_number="P-397-3")
        db.add_all([one, two, other])
        await db.flush()
        db.add_all([
            MemberParcel(member_id=anna.id, parcel_id=one.id), MemberParcel(member_id=bernd.id, parcel_id=one.id),
            MemberParcel(member_id=berta.id, parcel_id=two.id), MemberParcel(member_id=clara.id, parcel_id=two.id),
            MemberParcel(member_id=emil.id, parcel_id=two.id),
            MemberParcel(member_id=gone.id, parcel_id=one.id, assigned_until=date.today() - timedelta(days=30)),
            MemberParcel(member_id=udo.id, parcel_id=other.id),
        ])
        await db.commit()
        return one.id, two.id, other.id


def _pdf_pages(data: bytes) -> list:
    return [" ".join(p.extract_text().split()) for p in PdfReader(io.BytesIO(data)).pages]


async def test_write_to_the_tenants_of_picked_parcels(client, admin_user, monkeypatch):
    one, two, other = await _setup(client)

    page = await client.get("/parcels/")
    assert 'id="parcel-pick"' in page.text and f'value="{one}"' in page.text and "Write to their tenants" in page.text

    export = await client.get("/parcels/export/csv", params=[("parcels", one)])
    assert "P-397-1" in export.text and "P-397-2" not in export.text and "P-397-3" not in export.text

    # The pick form: audience=1, an empty member filter and the ticked parcels.
    picked = [("audience", "1"), ("audience_query", ""), ("parcels", one), ("parcels", two)]
    preview = await client.get("/announcements/new", params=picked)
    assert preview.status_code == 200 and "2 parcel(s) picked" in preview.text
    assert "Tenants who share a postal address get one letter" in preview.text

    response = await client.post("/announcements/new", data={
        "title": "Wasser", "body_markdown": "Am Samstag wird das Wasser abgestellt.",
        "audience": "1", "audience_query": "", "parcels": [one, two],
    })
    assert response.status_code == 303, response.text
    stored = await _announcement(response.headers["location"].split("/")[2])
    assert sorted(stored.audience_filter["parcels"]) == sorted([one, two])

    # "Show the list" from the message: the current tenants only.
    members_page = await client.get("/members/?" + MemberListFilter(parcels=(one, two)).query_string())
    assert "Showing the current tenants of 2 selected parcel(s)." in members_page.text
    assert "Gegangen" not in members_page.text and "Unbeteiligt" not in members_page.text and "Fern" in members_page.text

    sent_to = []

    async def fake_send_email(to, subject, html_body, text_body=None, db=None):
        sent_to.append(to)
        return True

    monkeypatch.setattr("app.announcement_mailer.send_email", fake_send_email)
    assert (await client.post(f"/announcements/{stored.id}/send/email")).status_code == 303
    assert len(sent_to) == 1 and sent_to[0].strip().lower() == "haus@example.org", "one email per inbox"

    # Letters: Bernd and Berta share an address across both parcels ->
    # one letter; Clara lives elsewhere -> her own.
    letters = await client.post(f"/announcements/{stored.id}/letters")
    assert letters.headers["content-type"] == "application/pdf"
    pages = _pdf_pages(letters.content)
    assert len(pages) == 2
    household = next(p for p in pages if "Bernd Haus" in p)
    assert "Berta Haus" in household and "Clara Fern" not in household
    assert any("Clara Fern" in p and "Am Hang 7" in p for p in pages)
    assert not any("Gegangen" in p or "Unbeteiligt" in p for p in pages)


async def test_member_messages_still_get_one_letter_per_person(client, admin_user):
    """Without picked parcels nothing is merged (issue #242 unchanged)."""
    one, two, _ = await _setup(client)
    async with AsyncSessionLocal() as db:
        ids = [m.id for m in (await db.execute(
            Member.__table__.select().where(Member.last_name == "Haus", Member.first_name.in_(["Bernd", "Berta"]))
        )).all()]
    response = await client.post("/announcements/new", data={
        "title": "Einzeln", "body_markdown": "Text.", "audience": "1",
        "audience_query": MemberListFilter(ids=tuple(ids)).query_string(),
    })
    stored = await _announcement(response.headers["location"].split("/")[2])
    letters = await client.post(f"/announcements/{stored.id}/letters")
    assert len(_pdf_pages(letters.content)) == 2


def test_member_filter_carries_picked_parcels():
    f = MemberListFilter(parcels=("p1", "p1", " ", "p2"))
    assert f.parcels == ("p1", "p2")
    assert MemberListFilter.from_dict(f.to_dict()) == f
    assert f.without_ids().parcels == ("p1", "p2") and not f.is_empty()
    assert "parcels=p1&parcels=p2" in f.query_string()
