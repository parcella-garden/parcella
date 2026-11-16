"""
Processes (issue #331, ADR 0135, docs/module-processes.md): templates and
their snapshot, the "required fields before moving on" rule, going back
and aborting, permissions, private files (local and cloud), the subject
cards, the examples and the API.
"""
from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import select

from app.auth import hash_password
from app.database import AsyncSessionLocal
from app.models import (
    Applicant, ClubSetting, Group, GroupMembership, GroupModulePermission, Member, Parcel, ParcelStatus,
    Process, ProcessEvent, ProcessEventKind, ProcessFieldKind as K, ProcessFileStorage, ProcessStatus,
    ProcessSubjectKind, User, UserRole,
)
from app.services import processes as svc
from app.services.errors import ServiceError
from tests.conftest import auth_header, login
from tests.test_admin_integrations_incoming_folder import web_login

PDF = b"%PDF-1.4\n% test\n"
PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 16


@pytest.fixture(autouse=True)
def _private_dir(tmp_path, monkeypatch):
    """Never write into the real uploads directory (run_tests.sh shares
    app/static/uploads/ with the dev environment)."""
    monkeypatch.setattr(svc, "LOCAL_DIR", tmp_path / "processes")
    return tmp_path / "processes"


async def _admin(db) -> User:
    return (await db.execute(select(User).where(User.email == "admin@example.com"))).scalar_one()


async def _user(db, email: str, *, read=False, write=False, delete=False) -> User:
    user = User(email=email, name=email.split("@")[0], password_hash=hash_password("testpasswort123"),
                role=UserRole.READONLY)
    group = Group(name=f"g-{email}")
    db.add_all([user, group])
    await db.flush()
    db.add(GroupModulePermission(group_id=group.id, module="processes", can_read=read, can_write=write,
                                 can_delete=delete))
    db.add(GroupMembership(user_id=user.id, group_id=group.id))
    await db.commit()
    return user


async def _template(db, admin, *stages, subject_kind="NONE"):
    """stages: (name, [(label, kind, required, options), ...])"""
    template = await svc.create_template(db, admin, name="Test process", subject_kind=subject_kind)
    for name, fields in stages:
        template = await svc.get_template(db, template.id)
        stage = await svc.add_stage(db, template, admin, name=name)
        for label, kind, required, *options in fields:
            template = await svc.get_template(db, template.id)
            await svc.add_field(db, template, stage.id, admin, kind=kind, label=label, required=required,
                                options=options[0] if options else None)
    return await svc.get_template(db, template.id)


def _field(process, label):
    return next(f for s in process.stages for f in s.fields if f.label == label)


async def _fill(db, process, user):
    """Fills every required field of the current stage with something valid."""
    for field in svc.missing_fields(svc.current_stage(process)):
        if field.kind == K.FILE:
            await svc.store_file(db, process, field.id, user, content=PDF, filename="doc.pdf")
        else:
            value = {
                K.TEXT: "x", K.LONG_TEXT: "x", K.NUMBER: "1", K.MONEY: "1", K.DATE: "2026-11-16",
                K.CHECKBOX: True, K.CHOICE: (field.options or [""])[0],
            }.get(field.kind)
            if field.kind == K.MEMBER:
                value = (await db.scalar(select(Member.id)))
            elif field.kind == K.APPLICANT:
                value = (await db.scalar(select(Applicant.id)))
            elif field.kind == K.PARCEL:
                value = (await db.scalar(select(Parcel.id)))
            await svc.set_field(db, process, field.id, value, user)
        process = await svc.get_process(db, process.id, lock=True)
    return process


async def _run_to_end(db, process, user):
    while process.status == ProcessStatus.OPEN:
        process = await _fill(db, process, user)
        await svc.advance(db, process, user)
        process = await svc.get_process(db, process.id, lock=True)
    return process


async def _subjects(db):
    parcel = Parcel(plot_number="12", status=ParcelStatus.TERMINATED)
    member = Member(first_name="Otto", last_name="Gardener")
    applicant = Applicant(email="ann@example.org", first_name="Ann")
    db.add_all([parcel, member, applicant])
    await db.commit()
    return parcel, member, applicant


# ---------------------------------------------------------------------------
# Web happy path
# ---------------------------------------------------------------------------

async def test_plot_handover_example_via_web(client, admin_user):
    await web_login(client)
    async with AsyncSessionLocal() as db:
        parcel, _, _ = await _subjects(db)

    r = await client.post("/processes/templates/example", data={"key": "plot_handover"})
    assert r.status_code == 303
    template_id = r.headers["location"].rsplit("/", 1)[-1]
    assert (await client.get(f"/processes/templates/{template_id}")).status_code == 200
    assert (await client.get("/processes/templates/")).status_code == 200

    # Coming from the plot page: the template is preselected.
    page = await client.get(f"/processes/new?subject_kind=PARCEL&subject_id={parcel.id}")
    assert page.status_code == 200 and "Plot handover" in page.text

    # The subject is required for a plot template.
    r = await client.post("/processes/new", data={"template_id": template_id, "title": ""})
    assert r.status_code == 400
    r = await client.post("/processes/new", data={"template_id": template_id, "subject_id": parcel.id, "title": ""})
    assert r.status_code == 303
    url = r.headers["location"]
    process_id = url.rsplit("/", 1)[-1]

    page = await client.get(url)
    assert page.status_code == 200 and "Inspection" in page.text

    # Required fields block moving on.
    r = await client.post(f"{url}/advance")
    assert "error=processes.errors.missing_fields" in r.headers["location"]

    async with AsyncSessionLocal() as db:
        process = await svc.get_process(db, process_id)
        stage = svc.current_stage(process)
        date_field, ticked = _field(process, "Date of the inspection"), _field(process, "All defects resolved")
    r = await client.post(f"{url}/stages/{stage.id}", data={
        f"field-{date_field.id}": "2026-11-16", f"field-{ticked.id}": "1",
        f"field-{_field(process, 'Defects found').id}": "Conifer hedge too high",
    })
    assert r.status_code == 303 and "error" not in r.headers["location"]
    # Unticking: a checkbox missing from the form means "no".
    await client.post(f"{url}/stages/{stage.id}", data={f"field-{date_field.id}": "2026-11-16"})
    async with AsyncSessionLocal() as db:
        assert _field(await svc.get_process(db, process_id), "All defects resolved").value_bool is False
    await client.post(f"{url}/stages/{stage.id}", data={f"field-{date_field.id}": "2026-11-16", f"field-{ticked.id}": "1"})

    r = await client.post(f"{url}/advance")
    assert "error" not in r.headers["location"]
    async with AsyncSessionLocal() as db:
        process = await svc.get_process(db, process_id)
        assert process.current_position == 1 and process.stages[0].completed_at is not None

    # Back with a reason; values are kept.
    r = await client.post(f"{url}/back", data={"to_position": "0", "reason": ""})
    assert "error=processes.errors.reason_required" in r.headers["location"]
    r = await client.post(f"{url}/back", data={"to_position": "0", "reason": "Hedge measured wrong"})
    async with AsyncSessionLocal() as db:
        process = await svc.get_process(db, process_id)
        assert process.current_position == 0 and process.stages[0].completed_at is None
        assert _field(process, "Defects found").value_text == "Conifer hedge too high"

        admin = await _admin(db)
        process = await _run_to_end(db, await svc.get_process(db, process_id, lock=True), admin)
        assert process.status == ProcessStatus.COMPLETED and process.closed_at is not None
        kinds = [e.kind for e in process.events]
        assert ProcessEventKind.REVERTED in kinds and ProcessEventKind.COMPLETED in kinds

    page = await client.get(url)
    assert page.status_code == 200 and "Completed" in page.text
    # Shown on the plot page, and on the dashboard count.
    assert "Plot handover" in (await client.get(f"/parcels/{parcel.id}")).text
    assert (await client.get("/processes/?status=closed")).status_code == 200


async def test_both_examples_run_end_to_end(admin_user):
    async with AsyncSessionLocal() as db:
        parcel, member, _ = await _subjects(db)
        admin = await _admin(db)
        for key, subject in (("plot_handover", parcel.id), ("member_onboarding", member.id)):
            template = await svc.create_from_example(db, admin, key, "de")
            assert template.name and all(s.name for s in template.stages)
            assert not any(f.label.startswith("processes.") for s in template.stages for f in s.fields)
            process = await svc.start_process(db, admin, template_id=template.id, subject_id=subject)
            process = await _run_to_end(db, await svc.get_process(db, process.id, lock=True), admin)
            assert process.status == ProcessStatus.COMPLETED
            # The applicant picked as new tenant isn't named in the history
            # (it would outlive their purge, ADR 0091).
            assert not any("Ann" in (e.note or "") for e in process.events)


# ---------------------------------------------------------------------------
# Rules
# ---------------------------------------------------------------------------

async def test_running_process_is_a_snapshot(admin_user):
    async with AsyncSessionLocal() as db:
        admin = await _admin(db)
        template = await _template(db, admin, ("One", [("Name", "TEXT", True)]))
        process = await svc.start_process(db, admin, template_id=template.id)
        pid, tid = process.id, template.id

        template = await svc.get_template(db, tid)
        field = template.stages[0].fields[0]
        await svc.update_field(db, template, field.id, admin, kind="DATE", label="Renamed", help_text=None,
                               required=False, options=None)
        template = await svc.get_template(db, tid)
        await svc.add_stage(db, template, admin, name="Two")

        process = await svc.get_process(db, pid)
        assert [s.name for s in process.stages] == ["One"]
        assert process.stages[0].fields[0].label == "Name" and process.stages[0].fields[0].kind == K.TEXT

        # Used templates can't be deleted, only archived -- and archived
        # ones can't be started.
        with pytest.raises(ServiceError) as e:
            await svc.delete_template(db, await svc.get_template(db, tid), admin)
        assert e.value.key == "processes.errors.template_in_use"
        await db.rollback()
        admin = await _admin(db)
        await svc.set_template_active(db, await svc.get_template(db, tid), admin, False)
        with pytest.raises(ServiceError) as e:
            await svc.start_process(db, admin, template_id=tid)
        assert e.value.key == "processes.errors.template_archived"


async def test_every_required_kind_blocks_advancing(admin_user):
    async with AsyncSessionLocal() as db:
        await _subjects(db)
        admin = await _admin(db)
        kinds = [k for k in K]
        template = await _template(db, admin, ("All", [
            (k.value, k.value, True, ["Red", "Green"] if k == K.CHOICE else None) for k in kinds
        ]), ("Last", []))
        process = await svc.start_process(db, admin, template_id=template.id)
        pid, tid = process.id, template.id
        assert {f.kind for f in svc.missing_fields(svc.current_stage(process))} == set(kinds)

        with pytest.raises(ServiceError) as e:
            await svc.advance(db, await svc.get_process(db, pid, lock=True), admin)
        assert e.value.key == "processes.errors.missing_fields" and e.value.http_status == 409
        await db.rollback()
        admin = await _admin(db)

        # An unticked checkbox doesn't count as filled.
        process = await svc.get_process(db, pid, lock=True)
        await svc.set_field(db, process, _field(process, "CHECKBOX").id, False, admin)
        process = await svc.get_process(db, pid, lock=True)
        assert _field(process, "CHECKBOX") in svc.missing_fields(svc.current_stage(process))

        process = await _fill(db, process, admin)
        assert svc.missing_fields(svc.current_stage(process)) == []
        await svc.advance(db, process, admin)
        process = await svc.get_process(db, pid, lock=True)
        assert process.current_position == 1
        # A stage without fields is a plain step.
        await svc.advance(db, process, admin)
        assert (await svc.get_process(db, pid)).status == ProcessStatus.COMPLETED


async def test_field_validation(admin_user):
    async with AsyncSessionLocal() as db:
        admin = await _admin(db)
        template = await _template(db, admin, ("One", [
            ("Amount", "MONEY", False), ("Count", "NUMBER", False), ("Colour", "CHOICE", False, "Red\nGreen\n\nRed"),
            ("When", "DATE", False), ("Who", "MEMBER", False), ("Later", "TEXT", False),
        ]), ("Two", [("Not yet", "TEXT", False)]))
        assert template.stages[0].fields[2].options == ["Red", "Green"]
        process = await svc.start_process(db, admin, template_id=template.id)
        pid, tid = process.id, template.id

        async def set_(label, value):
            p = await svc.get_process(db, pid, lock=True)
            await svc.set_field(db, p, _field(p, label).id, value, admin)
            return _field(await svc.get_process(db, pid), label)

        assert (await set_("Amount", "1.234,50")).value_number == Decimal("1234.50")
        assert (await set_("Amount", "1,234.50")).value_number == Decimal("1234.50")
        assert (await set_("Count", "7,5")).value_number == Decimal("7.50")
        assert (await set_("Amount", "")).value_number is None
        for label, value, key in (
            ("Amount", "lots", "invalid_number"), ("Amount", "1e15", "invalid_number"),
            ("Colour", "Blue", "invalid_choice"), ("When", "16.11.2026", "invalid_date"),
            ("Who", "no-such-id", "invalid_reference"), ("Not yet", "x", "stage_not_reached"),
        ):
            with pytest.raises(ServiceError) as e:
                await set_(label, value)
            assert e.value.key == "processes.errors." + key, label
            await db.rollback()
            admin = await _admin(db)

        assert (await set_("Colour", "Green")).value_text == "Green"
        events = (await svc.get_process(db, pid)).events
        assert any(e.kind == ProcessEventKind.FIELD_CHANGED and "Colour: – → Green" in (e.note or "") for e in events)

        # Choice fields need options; subjects must match the template.
        template = await svc.get_template(db, tid)
        with pytest.raises(ServiceError) as e:
            await svc.add_field(db, template, template.stages[0].id, admin, kind="CHOICE", label="Empty")
        assert e.value.key == "processes.errors.choice_needs_options"
        await db.rollback()
        admin = await _admin(db)
        plot_template = await _template(db, admin, ("One", []), subject_kind="PARCEL")
        with pytest.raises(ServiceError) as e:
            await svc.start_process(db, admin, template_id=plot_template.id, subject_id="nope")
        assert e.value.key == "processes.errors.subject_required"


async def test_abort_locks_the_process(admin_user):
    async with AsyncSessionLocal() as db:
        admin = await _admin(db)
        template = await _template(db, admin, ("One", [("Name", "TEXT", False)]))
        process = await svc.start_process(db, admin, template_id=template.id)
        pid, tid = process.id, template.id
        with pytest.raises(ServiceError) as e:
            await svc.abort(db, await svc.get_process(db, pid, lock=True), "  ", admin)
        assert e.value.key == "processes.errors.reason_required"
        await db.rollback()
        admin = await _admin(db)
        await svc.abort(db, await svc.get_process(db, pid, lock=True), "Tenant stays after all", admin)
        process = await svc.get_process(db, pid, lock=True)
        assert process.status == ProcessStatus.ABORTED and process.abort_reason == "Tenant stays after all"
        for action in (
            lambda p: svc.set_field(db, p, p.stages[0].fields[0].id, "x", admin),
            lambda p: svc.advance(db, p, admin),
            lambda p: svc.abort(db, p, "again", admin),
        ):
            with pytest.raises(ServiceError) as e:
                await action(await svc.get_process(db, pid, lock=True))
            assert e.value.key == "processes.errors.process_closed"
            await db.rollback()
            admin = await _admin(db)


# ---------------------------------------------------------------------------
# Permissions and the module flag
# ---------------------------------------------------------------------------

async def test_permissions(client, admin_user):
    async with AsyncSessionLocal() as db:
        admin = await _admin(db)
        template = await _template(db, admin, ("One", [("Name", "TEXT", False)]), ("Two", []))
        process = await svc.start_process(db, admin, template_id=template.id)
        await _user(db, "reader@example.org", read=True)
        await _user(db, "writer@example.org", read=True, write=True)
        await _user(db, "nobody@example.org")
    url = f"/processes/{process.id}"
    field_id = process.stages[0].fields[0].id
    stage_id = process.stages[0].id

    await web_login(client, "nobody@example.org")
    assert (await client.get("/processes/")).status_code == 403

    await web_login(client, "reader@example.org")
    assert (await client.get("/processes/")).status_code == 200
    page = await client.get(url)
    assert page.status_code == 200 and f'action="{url}/advance"' not in page.text
    assert (await client.post(f"{url}/advance")).status_code == 403
    assert (await client.post(f"{url}/stages/{stage_id}", data={f"field-{field_id}": "x"})).status_code == 403
    assert (await client.get("/processes/new")).status_code == 403

    await web_login(client, "writer@example.org")
    r = await client.post(f"{url}/stages/{stage_id}", data={f"field-{field_id}": "x"})
    assert r.status_code == 303
    assert (await client.post(f"{url}/abort", data={"reason": "no"})).status_code == 403
    assert (await client.post(f"{url}/delete")).status_code == 403
    assert (await client.get("/processes/templates/")).status_code == 403
    assert (await client.post("/processes/templates/new", data={"name": "Mine"})).status_code == 403
    assert (await client.post(f"/processes/templates/{template.id}/stages", data={"name": "X"})).status_code == 403

    await web_login(client)
    assert (await client.post(f"{url}/delete")).status_code == 303
    async with AsyncSessionLocal() as db:
        assert await db.get(Process, process.id) is None


async def test_module_flag_off(client, admin_user):
    async with AsyncSessionLocal() as db:
        db.add(ClubSetting(key="modul_processes", value="false", description="test"))
        await db.commit()
    await web_login(client)
    assert (await client.get("/processes/")).status_code == 404
    token = await login(client, "admin@example.com")
    assert (await client.get("/api/v1/processes", headers=auth_header(token))).status_code == 404


# ---------------------------------------------------------------------------
# Files
# ---------------------------------------------------------------------------

async def test_files_are_private(client, raw_client, admin_user, _private_dir):
    async with AsyncSessionLocal() as db:
        admin = await _admin(db)
        template = await _template(db, admin, ("One", [("Photos", "FILE", True)]), ("Two", [("Later", "FILE", False)]))
        process = await svc.start_process(db, admin, template_id=template.id)
    await web_login(client)
    url = f"/processes/{process.id}"
    photos, later = process.stages[0].fields[0], process.stages[1].fields[0]

    r = await client.post(f"{url}/fields/{photos.id}/files", files={"file": ("x.png", b"not an image", "image/png")})
    assert "file_type_not_allowed" in r.headers["location"]
    r = await client.post(f"{url}/fields/{later.id}/files", files={"file": ("x.png", PNG, "image/png")})
    assert "stage_not_reached" in r.headers["location"]
    r = await client.post(f"{url}/fields/{photos.id}/files", files={"file": ('../"evil\r\nname Łódź.png', PNG, "image/png")})
    assert "error=" not in r.headers["location"]

    async with AsyncSessionLocal() as db:
        record = _field(await svc.get_process(db, process.id), "Photos").files[0]
    assert record.storage == ProcessFileStorage.LOCAL
    stored = _private_dir / process.id / record.stored_name
    assert stored.read_bytes() == PNG
    assert "/" not in record.original_name and '"' not in record.original_name and "\n" not in record.original_name

    download = await client.get(f"{url}/files/{record.id}")
    assert download.status_code == 200 and download.content == PNG
    assert download.headers["content-type"] == "image/png"
    assert download.headers["cache-control"] == "private, no-store"

    # Not without logging in, and never through /static, however the path is spelled.
    assert (await raw_client.get(f"{url}/files/{record.id}", follow_redirects=False)).status_code in (302, 303, 401, 403)
    for prefix in ("/static/uploads/private", "/static/uploads//private", "/static//uploads/private",
                   "/static/uploads/./private", "/static/x/../uploads/private"):
        blocked = await raw_client.get(f"{prefix}/processes/{process.id}/{record.stored_name}")
        assert blocked.status_code == 404, prefix

    await client.post(f"{url}/files/{record.id}/delete")
    assert not stored.exists()
    async with AsyncSessionLocal() as db:
        kinds = [e.kind for e in (await svc.get_process(db, process.id)).events]
    assert ProcessEventKind.FILE_ADDED in kinds and ProcessEventKind.FILE_REMOVED in kinds


async def test_files_go_to_cloud_when_configured(client, admin_user, monkeypatch):
    uploads = {}

    class FakeProvider:
        async def create_folder(self, path):
            uploads.setdefault("folders", []).append(path)

        async def upload_file(self, path, filename, content):
            uploads[(path, filename)] = content

        async def download_file(self, path, filename):
            return uploads[(path, filename)]

        async def aclose(self):
            pass

    async def fake_provider(db):
        return FakeProvider()

    monkeypatch.setattr(svc, "get_cloud_storage_provider", fake_provider)
    async with AsyncSessionLocal() as db:
        parcel, _, _ = await _subjects(db)
        db.add(ClubSetting(key="modul_cloud_storage", value="true", description="test"))
        db.add(ClubSetting(key=svc.CLOUD_FOLDER_SETTING, value="board/processes", description="test"))
        await db.commit()
        admin = await _admin(db)
        template = await _template(db, admin, ("One", [("Report", "FILE", False)]), subject_kind="PARCEL")
        process = await svc.start_process(db, admin, template_id=template.id, subject_id=parcel.id)
        process = await svc.get_process(db, process.id, lock=True)
        record = await svc.store_file(db, process, _field(process, "Report").id, admin, content=PDF,
                                      filename="Gutachten Łódź.pdf")
        assert record.storage == ProcessFileStorage.CLOUD
        assert record.cloud_path.startswith("board/processes/12_")
        assert (record.cloud_path, record.stored_name) in uploads

    await web_login(client)
    download = await client.get(f"/processes/{process.id}/files/{record.id}")
    assert download.status_code == 200 and download.content == PDF
    assert "attachment" in download.headers["content-disposition"]


# ---------------------------------------------------------------------------
# Subject cards and API
# ---------------------------------------------------------------------------

async def test_subject_cards(client, admin_user):
    async with AsyncSessionLocal() as db:
        parcel, member, applicant = await _subjects(db)
        admin = await _admin(db)
        for kind, subject in (("PARCEL", parcel.id), ("MEMBER", member.id), ("APPLICANT", applicant.id)):
            template = await _template(db, admin, ("One", []), subject_kind=kind)
            await svc.start_process(db, admin, template_id=template.id, subject_id=subject, title=f"About {kind}")
    await web_login(client)
    for path, kind in ((f"/parcels/{parcel.id}", "PARCEL"), (f"/members/{member.id}", "MEMBER"),
                       (f"/applicants/{applicant.id}", "APPLICANT")):
        page = await client.get(path)
        assert page.status_code == 200 and f"About {kind}" in page.text, path
        assert f"/processes/new?subject_kind={kind}" in page.text
    assert "About PARCEL" in (await client.get("/processes/")).text


async def test_api(client, admin_user):
    async with AsyncSessionLocal() as db:
        admin = await _admin(db)
        template = await _template(db, admin, ("One", [("Amount", "MONEY", True)]), ("Two", []))
    token = await login(client, "admin@example.com")
    h = auth_header(token)

    templates = await client.get("/api/v1/process-templates", headers=h)
    assert templates.status_code == 200 and templates.json()[0]["stages"][0]["fields"][0]["kind"] == "MONEY"

    r = await client.post("/api/v1/processes", json={"template_id": template.id, "title": "Via API"}, headers=h)
    assert r.status_code == 201, r.text
    process = r.json()
    url = f"/api/v1/processes/{process['id']}"
    field_id = process["stages"][0]["fields"][0]["id"]

    r = await client.post(f"{url}/advance", headers=h)
    assert r.status_code == 409 and "Amount" in r.json()["detail"]
    r = await client.put(f"{url}/fields/{field_id}", json={"value": "12,50"}, headers=h)
    assert r.status_code == 200
    field = r.json()["stages"][0]["fields"][0]
    assert field["filled"] and Decimal(str(field["value_number"])) == Decimal("12.50")
    r = await client.put(f"{url}/fields/{field_id}", json={"value": "abc"}, headers=h)
    assert r.status_code == 422

    r = await client.post(f"{url}/advance", headers=h)
    assert r.status_code == 200 and r.json()["current_position"] == 1
    r = await client.post(f"{url}/back", json={"to_position": 0, "reason": "Oops"}, headers=h)
    assert r.status_code == 200 and r.json()["current_position"] == 0
    r = await client.post(f"{url}/abort", json={"reason": "Not needed"}, headers=h)
    assert r.status_code == 200 and r.json()["status"] == "ABORTED"

    listing = await client.get("/api/v1/processes?status=all", headers=h)
    assert [p["id"] for p in listing.json()] == [process["id"]]
    assert (await client.get("/api/v1/processes", headers=h)).json() == []
