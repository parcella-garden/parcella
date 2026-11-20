"""
Issue #397: tick parcels on /parcels/ and send a notice to their
leaseholders. Leasehold law, not association law (ADR 0142): one notice
per parcel -- a "double garden" couple gets two -- to its current
leaseholders. Email to each who consented; one letter per postal
address for the others, also when a housemate got the email. Every
email and letter names its parcel.
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
        def member(first, last, street, city, email=None, consent=True):
            m = Member(first_name=first, last_name=last, street=street, postal_code="04103", city=city,
                       email_notifications=consent)
            if email:
                m.email_addresses.append(MemberEmail(address=email, is_primary=True))
            db.add(m)
            return m

        anna = member("Anna", "Haus", "Lindenweg 1", "Leipzig", email="anna@example.org")
        bernd = member("Bernd", "Haus", "Lindenweg 1", "Leipzig", email="bernd@example.org", consent=False)
        berta = member("Berta", "Haus", " lindenweg 1 ", "LEIPZIG")
        clara = member("Clara", "Fern", "Am Hang 7", "Dresden")
        gone = member("Gerd", "Gegangen", "Altweg 3", "Leipzig")
        udo = member("Udo", "Unbeteiligt", "Weg 9", "Leipzig", email="udo@example.org")
        one, two, other = Parcel(plot_number="P-397-1"), Parcel(plot_number="P-397-2"), Parcel(plot_number="P-397-3")
        db.add_all([one, two, other])
        await db.flush()
        db.add_all([
            MemberParcel(member_id=anna.id, parcel_id=one.id), MemberParcel(member_id=bernd.id, parcel_id=one.id),
            MemberParcel(member_id=berta.id, parcel_id=one.id),
            MemberParcel(member_id=anna.id, parcel_id=two.id), MemberParcel(member_id=clara.id, parcel_id=two.id),
            MemberParcel(member_id=gone.id, parcel_id=one.id, assigned_until=date.today() - timedelta(days=30)),
            MemberParcel(member_id=udo.id, parcel_id=other.id),
        ])
        await db.commit()
        return one.id, two.id, other.id


def _pdf_pages(data: bytes) -> list:
    return [" ".join(p.extract_text().split()) for p in PdfReader(io.BytesIO(data)).pages]


async def test_notice_to_the_leaseholders_of_picked_parcels(client, admin_user, monkeypatch):
    one, two, other = await _setup(client)

    page = await client.get("/parcels/")
    assert 'name="audience_kind" value="parcels"' in page.text and f'value="{one}"' in page.text
    assert "Write to their leaseholders" in page.text

    export = await client.get("/parcels/export/csv", params=[("parcel_ids", one)])
    assert "P-397-1" in export.text and "P-397-2" not in export.text and "P-397-3" not in export.text

    picked = [("audience_kind", "parcels"), ("parcel_ids", one), ("parcel_ids", two)]
    preview = await client.get("/announcements/new", params=picked)
    assert preview.status_code == 200 and "Notice to the leaseholders of 2 parcel(s)" in preview.text
    assert "One notice per parcel" in preview.text and 'href="/parcels/"' in preview.text

    response = await client.post("/announcements/new", data={
        "title": "Wasser", "body_markdown": "Am Samstag wird das Wasser abgestellt.",
        "audience_kind": "parcels", "parcel_ids": [one, two],
    })
    assert response.status_code == 303, response.text
    stored = await _announcement(response.headers["location"].split("/")[2])
    assert stored.audience_parcel_ids == [one, two] and stored.audience_filter is None
    assert stored.is_parcel_message and stored.is_targeted

    sent = []

    async def fake_send_email(to, subject, html_body, text_body=None, db=None):
        sent.append((to, subject, html_body))
        return True

    monkeypatch.setattr("app.announcement_mailer.send_email", fake_send_email)
    assert (await client.post(f"/announcements/{stored.id}/send/email")).status_code == 303
    # Anna consented and holds both parcels: one email per parcel, each
    # naming it. Bernd has an address but no consent: no email.
    assert sorted((to, subject) for to, subject, _ in sent) == [
        ("anna@example.org", "Wasser – Parcel P-397-1"), ("anna@example.org", "Wasser – Parcel P-397-2"),
    ]
    assert all("Parcel P-397-" in html for _, _, html in sent)

    # Letters: parcel 1 -> Bernd and Berta share an address (one letter,
    # although Anna there got the email); parcel 2 -> Clara.
    letters = await client.post(f"/announcements/{stored.id}/letters")
    assert letters.headers["content-type"] == "application/pdf"
    pages = _pdf_pages(letters.content)
    assert len(pages) == 2
    first = next(p for p in pages if "Bernd Haus" in p)
    assert "Berta Haus" in first and "Parcel P-397-1" in first and "Anna Haus" not in first
    assert any("Clara Fern" in p and "Am Hang 7" in p and "Parcel P-397-2" in p for p in pages)
    assert not any("Gegangen" in p or "Unbeteiligt" in p for p in pages)


async def test_member_messages_are_unchanged(client, admin_user):
    """A message to members stays one letter per person (association law
    is a separate matter, its rules come in their own change)."""
    await _setup(client)
    async with AsyncSessionLocal() as db:
        ids = [row.id for row in (await db.execute(
            Member.__table__.select().where(Member.last_name == "Haus", Member.first_name.in_(["Bernd", "Berta"]))
        )).all()]
    response = await client.post("/announcements/new", data={
        "title": "Einzeln", "body_markdown": "Text.", "audience": "1",
        "audience_query": MemberListFilter(ids=tuple(ids)).query_string(),
    })
    stored = await _announcement(response.headers["location"].split("/")[2])
    assert stored.audience_parcel_ids is None
    letters = await client.post(f"/announcements/{stored.id}/letters")
    assert len(_pdf_pages(letters.content)) == 1  # Bernd has an email address, so only Berta gets a letter


async def test_picked_parcels_need_existing_parcels(client, admin_user):
    await _setup(client)
    response = await client.get("/announcements/new", params=[("audience_kind", "parcels"), ("parcel_ids", "nope")])
    assert response.status_code == 400
