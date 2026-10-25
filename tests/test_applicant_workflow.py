"""
Applicant workflow fixes from issues #251-#255 (docs/module-applicants.md):

- #251: the facts card shows dates only, and "Consent given" is labelled
  as what it is -- the applicant's data-protection consent.
- #252: ACCEPTED is still open, so "Assign a parcel" stays available
  (the handover itself is covered in test_applicant_parcel_handover.py).
- #253: no WITHDRAWN status any more; CLOSED takes its enum label.
- #254: the "New" filter comes first, is the default while there are new
  applications, and is hidden while there are none.
- #255: applications are deleted after a configurable number of months
  without a status change, triggered by regular site use.
"""
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models import APPLICANT_OPEN_STATUSES, Applicant, ApplicantStatus, ChangeHistory, ClubSetting
from app.services import applicants as applicant_service
from app.services.applicants import (
    RETENTION_SETTING, _months_before, parse_retention_months, purge_expired_applicants,
)
from tests.test_admin_integrations_incoming_folder import web_login


async def _create_applicant(**fields) -> str:
    async with AsyncSessionLocal() as db:
        applicant = Applicant(email=fields.pop("email", "erika@example.org"), **fields)
        db.add(applicant)
        await db.commit()
        return applicant.id


async def _set_retention(value: str) -> None:
    async with AsyncSessionLocal() as db:
        db.add(ClubSetting(key=RETENTION_SETTING, value=value, description="test"))
        await db.commit()


async def _remaining_ids() -> set[str]:
    async with AsyncSessionLocal() as db:
        return set((await db.scalars(select(Applicant.id))).all())


# ---------------------------------------------------------------------------
# #251
# ---------------------------------------------------------------------------

async def test_facts_card_shows_dates_only_and_names_the_consent(client, admin_user):
    applicant_id = await _create_applicant(
        consent_at=datetime(2026, 3, 4, 17, 45, tzinfo=timezone.utc),
        applied_at=datetime(2026, 3, 4, 17, 45, tzinfo=timezone.utc),
    )
    await web_login(client)
    page = (await client.get(f"/applicants/{applicant_id}")).text
    assert "04.03.2026" in page
    assert "17:45" not in page
    assert "Privacy consent (applicant)" in page
    assert "Consent given" not in page

    listing = (await client.get("/applicants/?filter=all")).text
    assert "04.03.2026" in listing and "17:45" not in listing


# ---------------------------------------------------------------------------
# #252 / #253
# ---------------------------------------------------------------------------

async def test_accepted_applicant_can_still_get_a_parcel(client, admin_user):
    accepted = await _create_applicant(status=ApplicantStatus.ACCEPTED)
    closed = await _create_applicant(email="done@example.org", status=ApplicantStatus.CLOSED)
    await web_login(client)

    assert ApplicantStatus.ACCEPTED in APPLICANT_OPEN_STATUSES
    assert f"/applicants/{accepted}/assign-parcel" in (await client.get(f"/applicants/{accepted}")).text
    assert f"/applicants/{closed}/assign-parcel" not in (await client.get(f"/applicants/{closed}")).text

    # ACCEPTED shows under "open", CLOSED under "closed".
    open_page = (await client.get("/applicants/?filter=open")).text
    closed_page = (await client.get("/applicants/?filter=closed")).text
    assert "erika@example.org" in open_page and "done@example.org" not in open_page
    assert "done@example.org" in closed_page and "erika@example.org" not in closed_page


async def test_withdrawn_is_gone(client, admin_user):
    assert "WITHDRAWN" not in ApplicantStatus.__members__
    applicant_id = await _create_applicant()
    await web_login(client)
    page = (await client.get(f"/applicants/{applicant_id}")).text
    assert 'value="WITHDRAWN"' not in page
    assert 'value="CLOSED"' in page

    # A stale form posting the old value changes nothing.
    response = await client.post(f"/applicants/{applicant_id}/edit", data={
        "email": "erika@example.org", "status": "WITHDRAWN",
    })
    assert response.status_code == 303
    async with AsyncSessionLocal() as db:
        assert (await db.get(Applicant, applicant_id)).status == ApplicantStatus.NEW


# ---------------------------------------------------------------------------
# #254
# ---------------------------------------------------------------------------

async def test_new_filter_comes_first_and_is_the_default_while_there_are_new_ones(client, admin_user):
    await _create_applicant(email="fresh@example.org")
    await _create_applicant(email="waiting@example.org", status=ApplicantStatus.CONTACTED)
    await web_login(client)

    page = (await client.get("/applicants/")).text
    assert "fresh@example.org" in page
    assert "waiting@example.org" not in page  # default is "new"
    assert page.index("?filter=new") < page.index("?filter=open")


async def test_new_filter_is_hidden_without_new_applications(client, admin_user):
    await _create_applicant(email="waiting@example.org", status=ApplicantStatus.CONTACTED)
    await web_login(client)

    page = (await client.get("/applicants/")).text
    assert "waiting@example.org" in page  # default falls back to "open"
    assert "?filter=new" not in page.split("<table")[0]


# ---------------------------------------------------------------------------
# #255
# ---------------------------------------------------------------------------

def test_retention_months_parsing_and_month_arithmetic():
    assert parse_retention_months("24") == 24
    assert parse_retention_months(" 6 ") == 6
    for off in (None, "", "0", "-3", "zwei"):
        assert parse_retention_months(off) is None
    assert _months_before(datetime(2026, 3, 31, tzinfo=timezone.utc), 1) == datetime(2026, 2, 28, tzinfo=timezone.utc)
    assert _months_before(datetime(2026, 1, 15, tzinfo=timezone.utc), 24) == datetime(2024, 1, 15, tzinfo=timezone.utc)
    assert _months_before(datetime(2026, 1, 15, tzinfo=timezone.utc), 1) == datetime(2025, 12, 15, tzinfo=timezone.utc)


async def test_purge_deletes_applications_untouched_longer_than_the_retention(client, admin_user):
    now = datetime.now(timezone.utc)
    long_ago = now - timedelta(days=800)
    # Old application, status never changed: goes.
    old_untouched = await _create_applicant(email="a@example.org", applied_at=long_ago)
    # Old application, but its status changed recently: stays.
    recently_changed = await _create_applicant(
        email="b@example.org", applied_at=long_ago, status=ApplicantStatus.CONTACTED,
        status_changed_at=now - timedelta(days=10),
    )
    # Any status counts -- an open one whose last change is old goes too.
    old_change = await _create_applicant(
        email="c@example.org", applied_at=long_ago, status=ApplicantStatus.OFFERED,
        status_changed_at=now - timedelta(days=760),
    )
    fresh = await _create_applicant(email="d@example.org")
    async with AsyncSessionLocal() as db:
        db.add(ChangeHistory(entity_type="Applicant", entity_id=old_change, field_name="status",
                             old_value="CONTACTED", new_value="OFFERED"))
        await db.commit()

    async with AsyncSessionLocal() as db:
        assert await purge_expired_applicants(db) == 0  # no retention set: nothing happens
    assert await _remaining_ids() == {old_untouched, recently_changed, old_change, fresh}

    await _set_retention("24")
    async with AsyncSessionLocal() as db:
        assert await purge_expired_applicants(db) == 2
        orphans = (await db.scalars(select(ChangeHistory).where(ChangeHistory.entity_id == old_change))).all()
    assert await _remaining_ids() == {recently_changed, fresh}
    assert orphans == []


async def test_purge_runs_on_regular_site_use(client, admin_user, monkeypatch):
    gone = await _create_applicant(applied_at=datetime.now(timezone.utc) - timedelta(days=400))
    await _set_retention("12")
    monkeypatch.setattr(applicant_service, "_last_purge", None)
    await web_login(client)
    await client.get("/")
    assert gone not in await _remaining_ids()


async def test_admin_saves_the_retention_setting(client, admin_user):
    await web_login(client)
    page = (await client.get("/admin/settings")).text
    assert 'name="applicant_retention_months"' in page

    async def saved() -> str:
        async with AsyncSessionLocal() as db:
            return await db.scalar(select(ClubSetting.value).where(ClubSetting.key == RETENTION_SETTING))

    response = await client.post("/admin/settings", data={"applicant_retention_months": "24"})
    assert response.status_code == 302
    assert await saved() == "24"

    await client.post("/admin/settings", data={"applicant_retention_months": "0"})
    assert await saved() == ""
