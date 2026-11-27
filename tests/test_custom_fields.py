"""
Issue #443 (ADR 0147): custom fields on members and parcels, set up by a
system admin. A group is a yes/no whose sub-fields only count while it
is ticked; fields are archived, never deleted; a field's type is locked
once values exist.
"""
from decimal import Decimal

from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models import CustomField, CustomFieldValue, Member, Parcel
from tests.test_announcements import web_login


async def _field(target: str, label: str) -> CustomField:
    async with AsyncSessionLocal() as db:
        return (await db.scalars(select(CustomField).where(CustomField.target == target, CustomField.label == label))).one()


async def _add(client, target, label, kind, **extra):
    r = await client.post("/admin/custom-fields", data={"target": target, "label": label, "kind": kind, **extra})
    assert r.status_code == 303 and "error=" not in r.headers["location"], r.headers.get("location")
    return await _field(target, label)


async def _values(**owner):
    async with AsyncSessionLocal() as db:
        rows = (await db.scalars(select(CustomFieldValue).filter_by(**owner))).all()
        return {r.field_id: r for r in rows}


async def test_member_text_field_end_to_end(client, admin_user):
    await web_login(client, "admin@example.com")
    occupation = await _add(client, "MEMBER", "Occupation", "TEXT")
    assert occupation.key == "occupation"
    async with AsyncSessionLocal() as db:
        member = Member(first_name="Erika", last_name="Muster")
        db.add(member)
        await db.commit()
        member_id = member.id

    form = await client.get(f"/members/{member_id}/edit")
    assert f'name="cf_{occupation.id}"' in form.text and 'name="custom_fields_present"' in form.text

    r = await client.post(f"/members/{member_id}/edit", data={
        "first_name": "Erika", "last_name": "Muster", "custom_fields_present": "1", f"cf_{occupation.id}": "Gardener",
    })
    assert r.status_code == 302
    detail = await client.get(f"/members/{member_id}")
    assert "Further details" in detail.text and "Gardener" in detail.text

    # A post without the marker (an older form) leaves the value alone.
    await client.post(f"/members/{member_id}/edit", data={"first_name": "Erika", "last_name": "Muster"})
    assert (await _values(member_id=member_id))[occupation.id].value_text == "Gardener"


async def test_parcel_group_with_sub_fields(client, admin_user):
    await web_login(client, "admin@example.com")
    pool = await _add(client, "PARCEL", "Pool", "GROUP")
    diameter = await _add(client, "PARCEL", "Diameter", "NUMBER", parent_id=pool.id, unit="cm", required="true")
    winter = await _add(client, "PARCEL", "Removed in winter", "CHECKBOX", parent_id=pool.id)
    kind = await _add(client, "PARCEL", "Pool type", "CHOICE", parent_id=pool.id, options="Frame\nInflatable\n")
    assert kind.options == ["Frame", "Inflatable"]
    async with AsyncSessionLocal() as db:
        parcel = Parcel(plot_number="CF-1")
        db.add(parcel)
        await db.commit()
        parcel_id = parcel.id
    base = {"plot_number": "CF-1", "custom_fields_present": "1"}

    # Group ticked but its required sub-field empty: refused, nothing saved.
    r = await client.post(f"/parcels/{parcel_id}/edit", data={**base, f"cf_{pool.id}": "1"})
    assert r.status_code == 400 and "“Diameter” is required." in r.text
    assert await _values(parcel_id=parcel_id) == {}

    # Not a number: refused too.
    r = await client.post(f"/parcels/{parcel_id}/edit", data={**base, f"cf_{pool.id}": "1", f"cf_{diameter.id}": "wide"})
    assert r.status_code == 400 and "“Diameter” must be a number." in r.text

    r = await client.post(f"/parcels/{parcel_id}/edit", data={
        **base, f"cf_{pool.id}": "1", f"cf_{diameter.id}": "3,5", f"cf_{winter.id}": "1", f"cf_{kind.id}": "Frame",
    })
    assert r.status_code == 302
    values = await _values(parcel_id=parcel_id)
    assert values[pool.id].value_bool is True and values[diameter.id].value_number == Decimal("3.50")
    assert values[winter.id].value_bool is True and values[kind.id].value_text == "Frame"
    detail = (await client.get(f"/parcels/{parcel_id}")).text
    assert "Pool" in detail and "3.5 cm" in detail and "Frame" in detail

    # A choice that isn't offered is refused.
    r = await client.post(f"/parcels/{parcel_id}/edit", data={**base, f"cf_{pool.id}": "1", f"cf_{diameter.id}": "3", f"cf_{kind.id}": "Jacuzzi"})
    assert r.status_code == 400

    # Unticking the group clears its sub-fields: no pool, no pool data.
    r = await client.post(f"/parcels/{parcel_id}/edit", data={**base, f"cf_{diameter.id}": "9"})
    assert r.status_code == 302
    assert await _values(parcel_id=parcel_id) == {}


async def test_archive_keeps_values_and_kind_locks(client, admin_user):
    await web_login(client, "admin@example.com")
    shed = await _add(client, "PARCEL", "Summer house", "GROUP")
    area = await _add(client, "PARCEL", "Area", "NUMBER", parent_id=shed.id, unit="m²")
    async with AsyncSessionLocal() as db:
        parcel = Parcel(plot_number="CF-2")
        db.add(parcel)
        await db.commit()
        parcel_id = parcel.id
    await client.post(f"/parcels/{parcel_id}/edit", data={
        "plot_number": "CF-2", "custom_fields_present": "1", f"cf_{shed.id}": "1", f"cf_{area.id}": "12",
    })

    # The type is locked once a value exists; the label can still change.
    r = await client.post(f"/admin/custom-fields/{area.id}/edit", data={"label": "Floor area", "kind": "TEXT", "unit": "m²"})
    assert "error=" in r.headers["location"]
    r = await client.post(f"/admin/custom-fields/{area.id}/edit", data={"label": "Floor area", "unit": "m²"})
    assert r.status_code == 303 and (await _field("PARCEL", "Floor area")).key == "area"

    # Archiving the group hides it with its sub-field; saving the parcel
    # meanwhile doesn't touch the hidden values; restoring brings them back.
    assert (await client.post(f"/admin/custom-fields/{shed.id}/archive")).status_code == 303
    form = (await client.get(f"/parcels/{parcel_id}/edit")).text
    assert f"cf_{shed.id}" not in form and f"cf_{area.id}" not in form
    await client.post(f"/parcels/{parcel_id}/edit", data={"plot_number": "CF-2", "custom_fields_present": "1"})
    assert len(await _values(parcel_id=parcel_id)) == 2
    assert "Floor area" not in (await client.get(f"/parcels/{parcel_id}")).text
    await client.post(f"/admin/custom-fields/{shed.id}/restore")
    assert "12 m²" in (await client.get(f"/parcels/{parcel_id}")).text


async def test_admin_rules(client, admin_user):
    await web_login(client, "admin@example.com")
    first = await _add(client, "MEMBER", "Hobby", "TEXT")
    await client.post("/admin/custom-fields", data={"target": "MEMBER", "label": "Hobby", "kind": "TEXT"})
    async with AsyncSessionLocal() as db:  # keys stay unique per area
        second = (await db.scalars(select(CustomField).where(CustomField.key == "hobby-2"))).one()
    group = await _add(client, "MEMBER", "Allotment history", "GROUP")
    r = await client.post("/admin/custom-fields", data={"target": "MEMBER", "label": "Inner", "kind": "GROUP", "parent_id": group.id})
    assert "error=" in r.headers["location"]  # no group in a group
    r = await client.post("/admin/custom-fields", data={"target": "MEMBER", "label": "Size", "kind": "CHOICE", "options": " \n"})
    assert "error=" in r.headers["location"]  # a choice needs choices

    await client.post(f"/admin/custom-fields/{second.id}/move", data={"direction": "up"})
    page = (await client.get("/admin/custom-fields?target=MEMBER")).text
    assert page.index(f"/admin/custom-fields/{second.id}/edit") < page.index(f"/admin/custom-fields/{first.id}/edit")
    assert (await client.get("/admin/custom-fields?target=SOMETHING")).status_code == 404


async def test_only_system_admins_define_fields(client, admin_user, board_user):
    await web_login(client, "vorstand@example.com")
    assert (await client.get("/admin/custom-fields")).status_code == 403
    r = await client.post("/admin/custom-fields", data={"target": "MEMBER", "label": "Sneaky", "kind": "TEXT"})
    assert r.status_code == 403
    async with AsyncSessionLocal() as db:
        assert (await db.scalars(select(CustomField))).first() is None
