"""
ADR 0101: handing a terminated parcel over to applicants -- old tenants
become former tenants (and leave the club unless they hold another
parcel), the applicants become members, tenants and invoice
recipients, the parcel is active again, the applications ACCEPTED.
"""
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from tests.conftest import login, auth_header
from app.database import AsyncSessionLocal, current_tenant_filter
from app.models import (
    Applicant, ApplicantStatus, ChangeHistory, Member, MemberEmail, MemberParcel, Parcel, ParcelStatus,
)


async def web_login(client, email: str, password: str = "testpasswort123") -> None:
    response = await client.post("/auth/login", data={"email": email, "password": password})
    assert response.status_code in (302, 303)


async def _setup() -> dict:
    """Parcel 7 (terminated) held by Anna (her only parcel) and Bernd
    (who also holds parcel 8); applicant Xaver (new to the club) and
    co-applicant Yvonne, whose email belongs to an existing member."""
    async with AsyncSessionLocal() as db:
        parcel = Parcel(plot_number="7", status=ParcelStatus.TERMINATED)
        other_parcel = Parcel(plot_number="8")
        anna = Member(first_name="Anna", last_name="Alt")
        bernd = Member(first_name="Bernd", last_name="Alt")
        yvonne_member = Member(first_name="Yvonne", last_name="Yilmaz")
        db.add_all([parcel, other_parcel, anna, bernd, yvonne_member])
        await db.flush()
        db.add_all([
            MemberParcel(member_id=anna.id, parcel_id=parcel.id, is_invoice_address=True,
                         assigned_from=date(2010, 1, 1), assigned_until=date.today() + timedelta(days=60)),
            MemberParcel(member_id=bernd.id, parcel_id=parcel.id, is_invoice_address=False,
                         assigned_from=date(2010, 1, 1)),
            MemberParcel(member_id=bernd.id, parcel_id=other_parcel.id, is_invoice_address=True),
            MemberEmail(member_id=yvonne_member.id, address="yvonne@example.com", is_primary=True),
        ])
        xaver = Applicant(email="xaver@example.com", first_name="Xaver", last_name="Neu", phone="0170 123")
        yvonne = Applicant(email="Yvonne@example.com", first_name="Yvonne", last_name="Yilmaz",
                           status=ApplicantStatus.CONTACTED)
        db.add_all([xaver, yvonne])
        await db.commit()
        return {
            "parcel": parcel.id, "other_parcel": other_parcel.id, "anna": anna.id, "bernd": bernd.id,
            "yvonne_member": yvonne_member.id, "xaver": xaver.id, "yvonne": yvonne.id,
        }


async def test_handover_via_web(client, admin_user):
    ids = await _setup()
    day = date.today()
    await web_login(client, "admin@example.com")

    detail = await client.get(f"/applicants/{ids['xaver']}")
    assert f"/applicants/{ids['xaver']}/assign-parcel" in detail.text

    preview = await client.get(
        f"/applicants/{ids['xaver']}/assign-parcel",
        params={"parcel_id": ids["parcel"], "handover_date": day.isoformat(), "co_applicant_ids": ids["yvonne"]},
    )
    assert preview.status_code == 200
    assert "Handover of parcel 7" in preview.text
    assert "keeps membership (still tenant of 8)" in preview.text
    assert f'/members/{ids["yvonne_member"]}' in preview.text

    response = await client.post(
        f"/applicants/{ids['xaver']}/assign-parcel",
        data={"parcel_id": ids["parcel"], "handover_date": day.isoformat(), "co_applicant_ids": ids["yvonne"]},
    )
    assert response.status_code == 303
    assert response.headers["location"] == f"/parcels/{ids['parcel']}"

    async with AsyncSessionLocal() as db:
        parcel = (await db.execute(
            select(Parcel).options(selectinload(Parcel.member_assignments)).where(Parcel.id == ids["parcel"])
        )).scalar_one()
        assert parcel.status == ParcelStatus.ACTIVE
        by_member = {a.member_id: a for a in parcel.member_assignments}

        # Old tenants: former from the handover date on, no invoice recipient any more.
        for old in (ids["anna"], ids["bernd"]):
            assert by_member[old].assigned_until == day
            assert by_member[old].is_invoice_address is False
            assert not by_member[old].is_current
        anna = await db.get(Member, ids["anna"])
        bernd = await db.get(Member, ids["bernd"])
        assert anna.member_until == day - timedelta(days=1)
        assert bernd.member_until is None  # still holds parcel 8

        # New tenants: Xaver as a brand-new member, Yvonne's existing member reused.
        xaver_member = (await db.execute(
            select(Member).options(selectinload(Member.email_addresses), selectinload(Member.phone_numbers))
            .where(Member.first_name == "Xaver")
        )).scalar_one()
        assert xaver_member.member_since == day
        assert [e.address for e in xaver_member.email_addresses] == ["xaver@example.com"]
        assert [p.number for p in xaver_member.phone_numbers] == ["0170 123"]
        assert len((await db.execute(select(Member).where(Member.first_name == "Yvonne"))).scalars().all()) == 1
        for new in (xaver_member.id, ids["yvonne_member"]):
            assert by_member[new].assigned_from == day
            assert by_member[new].assigned_until is None
            assert by_member[new].is_invoice_address is True

        for applicant_id in (ids["xaver"], ids["yvonne"]):
            applicant = await db.get(Applicant, applicant_id)
            assert applicant.status == ApplicantStatus.ACCEPTED
        history = (await db.execute(select(ChangeHistory).where(
            ChangeHistory.entity_type == "Applicant", ChangeHistory.entity_id == ids["xaver"],
        ))).scalars().all()
        assert [(h.field_name, h.new_value) for h in history] == [("status", "ACCEPTED")]

    # Closed now -- no handover button any more.
    detail = await client.get(f"/applicants/{ids['xaver']}")
    assert f"/applicants/{ids['xaver']}/assign-parcel" not in detail.text


async def test_handover_rejects_active_parcel(client, admin_user):
    ids = await _setup()
    await web_login(client, "admin@example.com")
    response = await client.post(
        f"/applicants/{ids['xaver']}/assign-parcel", data={"parcel_id": ids["other_parcel"]},
    )
    assert response.status_code == 400
    assert "Parcel 8 isn&#39;t terminated" in response.text
    async with AsyncSessionLocal() as db:
        assert (await db.get(Applicant, ids["xaver"])).status == ApplicantStatus.NEW


async def test_handover_via_api_with_future_date(client, admin_user):
    """ADR 0102: a handover recorded ahead of time. Until the date the
    old tenants stay current (and billed), the new ones are upcoming;
    nobody is current twice over."""
    ids = await _setup()
    token = await login(client, "admin@example.com")
    day = date.today() + timedelta(days=30)
    response = await client.post(
        f"/api/v1/applicants/{ids['xaver']}/assign-parcel",
        json={"parcel_id": ids["parcel"], "handover_date": day.isoformat()},
        headers=auth_header(token),
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert len(body["member_ids"]) == 1
    assert sorted(body["former_tenant_member_ids"]) == sorted([ids["anna"], ids["bernd"]])
    assert body["membership_ended_member_ids"] == [ids["anna"]]

    async with AsyncSessionLocal() as db:
        tenancies = {
            a.member_id: a for a in (await db.execute(
                select(MemberParcel).where(MemberParcel.parcel_id == ids["parcel"])
            )).scalars().all()
        }
        anna_tenancy = tenancies[ids["anna"]]
        assert anna_tenancy.assigned_until == day
        assert anna_tenancy.is_current and not anna_tenancy.is_former
        assert anna_tenancy.is_invoice_address is True  # still billed until she leaves (ADR 0058)
        anna = await db.get(Member, ids["anna"])
        assert anna.member_until == day - timedelta(days=1)
        assert anna.is_active

        new_tenancy = tenancies[body["member_ids"][0]]
        assert new_tenancy.is_upcoming and not new_tenancy.is_current
        assert new_tenancy.is_invoice_address is True
        assert not (await db.get(Member, body["member_ids"][0])).is_active  # member from `day` on

        current = (await db.execute(
            select(MemberParcel.member_id).where(MemberParcel.parcel_id == ids["parcel"], current_tenant_filter())
        )).scalars().all()
        assert sorted(current) == sorted([ids["anna"], ids["bernd"]])

    await web_login(client, "admin@example.com")
    page = await client.get(f"/parcels/{ids['parcel']}")
    assert f"from {day.strftime('%d.%m.%Y')}" in page.text
    assert f"until {day.strftime('%d.%m.%Y')}" in page.text
