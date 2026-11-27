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


async def test_list_filter_by_custom_field(client, admin_user):
    from app.member_filters import MemberListFilter
    from tests.conftest import auth_header, login
    from tests.test_announcements import _enable_module
    await _enable_module(client, auth_header(await login(client, "admin@example.com")))
    await web_login(client, "admin@example.com")
    occupation = await _add(client, "MEMBER", "Occupation", "TEXT")
    pool = await _add(client, "PARCEL", "Pool", "GROUP")
    pool_kind = await _add(client, "PARCEL", "Pool type", "CHOICE", parent_id=pool.id, options="Frame\nInflatable")
    async with AsyncSessionLocal() as db:
        anna, bert = Member(first_name="Anna", last_name="Gärtner"), Member(first_name="Bert", last_name="Bäcker")
        with_pool, without = Parcel(plot_number="CF-P1"), Parcel(plot_number="CF-P2")
        db.add_all([anna, bert, with_pool, without])
        await db.commit()
        anna_id, with_pool_id = anna.id, with_pool.id
    await client.post(f"/members/{anna_id}/edit", data={
        "first_name": "Anna", "last_name": "Gärtner", "custom_fields_present": "1", f"cf_{occupation.id}": "Landscape gardener",
    })
    await client.post(f"/parcels/{with_pool_id}/edit", data={
        "plot_number": "CF-P1", "custom_fields_present": "1", f"cf_{pool.id}": "1", f"cf_{pool_kind.id}": "Frame",
    })

    page = (await client.get("/members/", params={"cf_field": occupation.id, "cf_value": "garden"})).text
    assert "Gärtner, Anna" in page and "Bäcker, Bert" not in page
    assert 'name="cf_field" value="' + occupation.id in page  # carried into the pick form for export / write to
    # Picking only the field shows its value control, without filtering yet.
    page = (await client.get("/members/", params={"cf_field": occupation.id})).text
    assert 'placeholder="contains …"' in page and "Bäcker, Bert" in page and "Gärtner, Anna" in page
    page = (await client.get("/members/", params={"cf_field": occupation.id, "cf_value": "__no__"})).text
    assert "Gärtner, Anna" not in page and "Bäcker, Bert" in page
    export = await client.get("/members/export/csv", params={"cf_field": occupation.id, "cf_value": "garden"})
    assert "Gärtner" in export.text and "Bäcker" not in export.text
    # A stored announcement filter keeps it (MemberListFilter is JSON in the DB).
    stored = MemberListFilter.from_dict(MemberListFilter.from_query(cf_field=occupation.id, cf_value="__yes__").to_dict())
    assert stored.cf_field == occupation.id and stored.cf_value == "__yes__"
    # A field picked without a value is no filter -- so not a "targeted" message to everybody.
    assert MemberListFilter.from_query(cf_field=occupation.id, cf_value="").is_empty()

    page = (await client.get("/parcels/", params={"cf_field": pool.id, "cf_value": "__yes__"})).text
    assert "CF-P1" in page and "CF-P2" not in page
    page = (await client.get("/parcels/", params={"cf_field": pool_kind.id, "cf_value": "=Inflatable"})).text
    assert "CF-P1" not in page
    page = (await client.get("/parcels/", params={"cf_field": pool.id, "cf_value": "__no__"})).text
    assert "CF-P1" not in page and "CF-P2" in page
    notice = await client.get("/announcements/new", params={
        "audience_kind": "parcels", "all_matching": "1", "cf_field": pool.id, "cf_value": "__yes__",
    })
    assert "Notice to the leaseholders of 1 parcel(s)" in notice.text


def _b64(text: str) -> str:
    import base64
    return base64.b64encode(text.encode("utf-8")).decode("ascii")


async def test_csv_export_and_import(client, admin_user):
    from urllib.parse import unquote
    await web_login(client, "admin@example.com")
    occupation = await _add(client, "MEMBER", "Occupation", "TEXT")
    pool = await _add(client, "PARCEL", "Pool", "GROUP")
    diameter = await _add(client, "PARCEL", "Diameter", "NUMBER", parent_id=pool.id, unit="cm")
    async with AsyncSessionLocal() as db:
        existing = Parcel(plot_number="CF-E1")
        db.add(existing)
        await db.commit()
        existing_id = existing.id

    # Members: a mapped custom-field column is imported on create.
    r = await client.post("/members/import/finalize", data={
        "csv_content_b64": _b64("Vorname;Nachname;Occupation\nIda;Import;Beekeeper\n"), "delimiter": ";",
        "map_0": "first_name", "map_1": "last_name", "map_2": f"cf:{occupation.id}",
    }, follow_redirects=False)
    assert r.status_code == 302
    async with AsyncSessionLocal() as db:
        ida = (await db.scalars(select(Member).where(Member.last_name == "Import"))).one()
    assert (await _values(member_id=ida.id))[occupation.id].value_text == "Beekeeper"
    export = (await client.get("/members/export/csv")).text
    assert export.splitlines()[0].endswith(";Occupation") and "Beekeeper" in export

    # The preview offers the custom fields as targets and guesses them from the header.
    preview = await client.post("/parcels/import/preview", files={
        "file": ("p.csv", "Gartennummer;Pool: Diameter\nCF-E1;250\n".encode(), "text/csv"),
    })
    assert f'value="cf:{diameter.id}" selected' in " ".join(preview.text.split())

    # Parcels: an existing parcel keeps its own fields but gets the custom
    # values; a filled sub-field ticks its group; a bad number is reported.
    r = await client.post("/parcels/import/finalize", data={
        "csv_content_b64": _b64("Gartennummer;Diameter\nCF-E1;250\nCF-N1;3,5\nCF-N2;wide\n"), "delimiter": ";",
        "map_0": "plot_number", "map_1": f"cf:{diameter.id}",
    }, follow_redirects=False)
    message = unquote(r.headers["location"])
    assert "1 existing parcel(s) got custom field values" in message and "Row 4: “Diameter” must be a number." in message
    values = await _values(parcel_id=existing_id)
    assert values[pool.id].value_bool is True and values[diameter.id].value_number == Decimal("250.00")
    export = (await client.get("/parcels/export/csv")).text
    header = export.splitlines()[0]
    assert header.endswith(";Pool;Pool: Diameter")
    assert "CF-E1;" in export and export.split("CF-E1;")[1].splitlines()[0].endswith(";Ja;250")

    # A group set to "Nein" clears its sub-fields.
    await client.post("/parcels/import/finalize", data={
        "csv_content_b64": _b64("Gartennummer;Pool\nCF-E1;Nein\n"), "delimiter": ";",
        "map_0": "plot_number", "map_1": f"cf:{pool.id}",
    })
    assert await _values(parcel_id=existing_id) == {}


async def test_rest_api(client, admin_user):
    from tests.conftest import auth_header, login
    await web_login(client, "admin@example.com")
    occupation = await _add(client, "MEMBER", "Occupation", "TEXT")
    pool = await _add(client, "PARCEL", "Pool", "GROUP")
    await _add(client, "PARCEL", "Diameter", "NUMBER", parent_id=pool.id, unit="cm", required="true")
    await _add(client, "PARCEL", "Built", "DATE")
    headers = auth_header(await login(client, "admin@example.com"))
    async with AsyncSessionLocal() as db:
        member, parcel = Member(first_name="Api", last_name="Tester"), Parcel(plot_number="CF-API")
        db.add_all([member, parcel])
        await db.commit()
        member_id, parcel_id = member.id, parcel.id

    defs = (await client.get("/api/v1/custom-fields", params={"target": "PARCEL"}, headers=headers)).json()
    assert [d["key"] for d in defs] == ["pool", "diameter", "built"]
    assert defs[1]["group"] == "pool" and defs[1]["unit"] == "cm" and defs[1]["required"] is True

    r = await client.put(f"/api/v1/members/{member_id}/custom-fields", json={"occupation": "Carpenter"}, headers=headers)
    assert r.status_code == 200 and r.json() == {"occupation": "Carpenter"}
    assert (await _values(member_id=member_id))[occupation.id].value_text == "Carpenter"

    # A sub-field ticks its group; a JSON number is taken exactly.
    r = await client.put(f"/api/v1/parcels/{parcel_id}/custom-fields", json={"diameter": 1.25, "built": "2019-05-01"}, headers=headers)
    assert r.status_code == 200 and r.json() == {"pool": True, "diameter": "1.25", "built": "2019-05-01"}
    # The required sub-field can't be cleared while the group is on ...
    r = await client.put(f"/api/v1/parcels/{parcel_id}/custom-fields", json={"diameter": None}, headers=headers)
    assert r.status_code == 422 and "Diameter" in r.json()["detail"]
    # ... but switching the group off clears it.
    r = await client.put(f"/api/v1/parcels/{parcel_id}/custom-fields", json={"pool": False}, headers=headers)
    assert r.json() == {"pool": False, "diameter": None, "built": "2019-05-01"}

    for bad in ({"nope": 1}, {"pool": "yes"}, {"built": "soon"}):
        assert (await client.put(f"/api/v1/parcels/{parcel_id}/custom-fields", json=bad, headers=headers)).status_code == 422
    assert (await client.get("/api/v1/parcels/00000000-0000-0000-0000-000000000000/custom-fields", headers=headers)).status_code == 404
    assert (await client.get(f"/api/v1/parcels/{parcel_id}/custom-fields")).status_code == 401
